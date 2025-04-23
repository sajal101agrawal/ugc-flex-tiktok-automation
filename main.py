import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tiktok_captcha_solver import SeleniumSolver
import undetected_chromedriver as uc
from helpers import pause_video_with_spacebar, enter_verification_code, is_comment_section_open, send_reply, \
                    open_comment_section, open_other_login_options, reopen_comment_section, send_comment, try_click_login, \
                    try_to_like_video, click_random_scroll_button, random_sleep, with_retries, wait_for_captcha_to_clear, \
                    try_to_comment_video, try_to_share_video, safe_action, is_verification_prompt_present, dismiss_cookie_banner
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging


load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def perform_login(driver, email, password):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//div[contains(text(), 'Phone') or contains(text(), 'phone')]"
            ))
        ).click()


        login_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, "//a[contains(text(), 'Log in with email or username')]"
            ))
        )
        login_link.click()


        logger.info("[*] Waiting for login fields...")

        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
        )
        username_input.clear()
        username_input.send_keys(email)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        password_input.clear()
        password_input.send_keys(password)

        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="login-button"]'))
        )
        login_btn.click()

        logger.info("[+] Login attempted. Waiting for response...")
        random_sleep(3, 5)
    except TimeoutException:
        logger.info("[!] Login timeout. Please check credentials or complete login manually.")
        raise
    except Exception as e:
        logger.info(f"[!] Login error: {e}")
        raise


def handle_after_login(driver, sadcaptcha):
    dismiss_cookie_banner(driver)
    video_count = random.randint(6, 10)
    like_index = random.randint(1, video_count - 2)
    share_index = random.randint(like_index + 1, video_count)
    comment_index = random.randint(like_index + 1, video_count)
    # like_index = 1
    # comment_index = 2
    # share_index = 1
    scroll_up_count = 0

    for i in range(video_count):
        logger.info(f"\n[*] Watching video {i + 1}/{video_count}")
        
        random_sleep(10, 15)
        logger.info(i)
        if i == like_index:
            safe_action(driver, sadcaptcha, try_to_like_video)

        if i == comment_index:
            safe_action(driver, sadcaptcha, try_to_comment_video)

        if i == share_index:
            safe_action(driver, sadcaptcha, try_to_share_video)

        success, scroll_up_count = click_random_scroll_button(driver, scroll_up_count)
        if not success:
            logger.info("[!] Fallback to JS scroll.")
            direction = -1 if scroll_up_count < 2 and random.random() < 0.3 else 1
            pixels = random.randint(500, 1000) * direction
            driver.execute_script(f"window.scrollBy(0, {pixels});")
            if direction < 0:
                scroll_up_count += 1
            logger.info(f"[~] JS scrolled {'up' if direction < 0 else 'down'}.")

        random_sleep(3, 5)


def comment_on_video(driver, comment, sadcaptcha, email, password, video_url):
    try:
        pause_video_with_spacebar(driver)
        dismiss_cookie_banner(driver)
        open_comment_section(driver)

        if is_comment_section_open(driver):
            logger.info("[✖] Comment section failed to open.")
            try_click_login(driver)

        open_other_login_options(driver)
        with_retries(lambda: safe_action(driver, sadcaptcha, perform_login, email, password))
        if is_verification_prompt_present(driver):
                logger.info("[!] Verification required. Fetching code from email...")
                random_sleep(2, 5)
                if not enter_verification_code(driver, email):
                    logger.info("[✖] Failed to enter verification code.")
                    return
                logger.info("[✓] Verification successful, no need to check CAPTCHA.")
        logger.info("[✓] Login completed.")
        if not wait_for_captcha_to_clear(driver, sadcaptcha, timeout=120):
            logger.info("[✖] CAPTCHA not cleared.")
            return
        logger.info("[*] Waiting for page refresh and comment section to open...")
        random_sleep(5, 7)
        
        # if not is_comment_section_open(driver):
        #     logger.info("[✖] Comment section failed to open after login.")
        #     return
        if video_url not in driver.current_url:
            logger.info(f"[!] Redirected to {driver.current_url}. Navigating back to video via JS...")
            driver.execute_script(f"window.location.href = '{video_url}';")
            random_sleep(5, 7)

        reopen_comment_section(driver)
        send_comment(driver, comment)

    except Exception as e:
        logger.info(f"[!] pause_video failed: {e}")


def reply_on_comment(driver, comment, sadcaptcha, email, password, reply, video_url):
    try:
        pause_video_with_spacebar(driver)
        dismiss_cookie_banner(driver)
        open_comment_section(driver)

        if is_comment_section_open(driver):
            logger.info("[✖] Comment section failed to open.")
            try_click_login(driver)

        open_other_login_options(driver)
        with_retries(lambda: safe_action(driver, sadcaptcha, perform_login, email, password))
        if is_verification_prompt_present(driver):
                logger.info("[!] Verification required. Fetching code from email...")
                random_sleep(2, 5)
                if not enter_verification_code(driver, email):
                    logger.info("[✖] Failed to enter verification code.")
                    return
                logger.info("[✓] Verification successful, no need to check CAPTCHA.")
        logger.info("[✓] Login completed.")
        if not wait_for_captcha_to_clear(driver, sadcaptcha, timeout=120):
            logger.info("[✖] CAPTCHA not cleared.")
            return
        logger.info("[*] Waiting for page refresh and comment section to open...")
        random_sleep(5, 7)
        # if not is_comment_section_open(driver):
        #     logger.info("[✖] Comment section failed to open after login.")
        #     return

        if video_url not in driver.current_url:
            logger.info(f"[!] Redirected to {driver.current_url}. Navigating back to video via JS...")
            driver.execute_script(f"window.location.href = '{video_url}';")
            random_sleep(5, 7)
        reopen_comment_section(driver)
        send_reply(driver, comment, reply)

    except Exception as e:
        logger.info(f"[!] pause_video failed: {e}")


def main(video_url=None, comment=None, reply=None):
    driver = None
    try:
        driver = uc.Chrome(headless=True)
        driver.maximize_window()

        api_key = "ca73e4fdf55a63b83ecfff3194754775"
        sadcaptcha = SeleniumSolver(driver, api_key, mouse_step_size=1, mouse_step_delay_ms=20)

        # email = "japdavev5@gmail.com"
        email = os.getenv("UNAME")
        password = "Tech@123$$$"
        driver.get("https://www.tiktok.com/login")
        random_sleep(2, 5)
        sadcaptcha.solve_captcha_if_present()

        with_retries(lambda: safe_action(driver, sadcaptcha, perform_login, email, password))

        if is_verification_prompt_present(driver):
            logger.info("[!] Verification required. Fetching code from email...")
            random_sleep(2, 5)
            if not enter_verification_code(driver, email):
                logger.info("[✖] Failed to enter verification code.")
                return
            logger.info("[✓] Verification successful, no need to check CAPTCHA.")

        # else:
        #     if not wait_for_captcha_to_clear(driver, sadcaptcha, timeout=120):
        #         logger.info("[✖] CAPTCHA was not cleared. Aborting.")
        #         return

        try:
            WebDriverWait(driver, 90).until(lambda d: "foryou" in d.current_url)
            logger.info(f"[✓] Redirected to {driver.current_url}. Login successful.")
            # handle_after_login(driver, sadcaptcha)
            if video_url and comment:
                driver.execute_script(f"window.location.href = '{video_url}';")
                reopen_comment_section(driver)

                random_sleep(5, 7)
                if reply is None:
                    # reopen_comment_section(driver)
                    send_comment(driver, comment)
                else:
                    send_reply(driver, comment, reply)
            else:
                handle_after_login(driver, sadcaptcha)
            random_sleep(5, 7)
        except TimeoutException:
            logger.info(f"[✖] Still not redirected to /foryou after login. Current URL: {driver.current_url}")

    except Exception as e:
        logger.info(f"[!] Main error: {e}")
    finally:
        if driver:

            driver.quit()

if __name__ == "__main__":
    main(video_url=None, comment=None, reply=None)
    # main(video_url="https://www.tiktok.com/@pet.babylover88/video/7480131003374259502?is_from_webapp=1&sender_device=pc", 
    #      comment="This isnt funny 💔", reply= "True That!!")
