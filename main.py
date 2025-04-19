import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tiktok_captcha_solver import SeleniumSolver
import undetected_chromedriver as uc
from helpers import enter_verification_code, try_to_like_video, click_random_scroll_button, random_sleep, \
                    try_to_comment_video, try_to_share_video, safe_action, is_verification_prompt_present, with_retries
from dotenv import load_dotenv


load_dotenv()


def perform_login(driver, email, password):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone / email / username')]"))
        ).click()

        fields_option = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/div[1]/a')
        fields_option.click()

        print("[*] Waiting for login fields...")

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

        login_btn = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/button')
        login_btn.click()

        print("[+] Login attempted. Waiting for response...")
        random_sleep(3, 5)
    except TimeoutException:
        print("[!] Login timeout. Please check credentials or complete login manually.")
        raise
    except Exception as e:
        print(f"[!] Login error: {e}")
        raise


def handle_after_login(driver, sadcaptcha):

    video_count = random.randint(6, 10)
    like_index = random.randint(1, video_count - 2)
    share_index = random.randint(like_index + 1, video_count)
    comment_index = random.randint(like_index + 1, video_count)
    # like_index = 1
    # comment_index = 2
    # share_index = 1
    scroll_up_count = 0

    for i in range(video_count):
        print(f"\n[*] Watching video {i + 1}/{video_count}")
        
        random_sleep(10, 15)
        print(i)
        if i == like_index:
            safe_action(driver, sadcaptcha, try_to_like_video)

        if i == comment_index:
            safe_action(driver, sadcaptcha, try_to_comment_video)

        if i == share_index:
            safe_action(driver, sadcaptcha, try_to_share_video)

        success, scroll_up_count = click_random_scroll_button(driver, scroll_up_count)
        if not success:
            print("[!] Fallback to JS scroll.")
            direction = -1 if scroll_up_count < 2 and random.random() < 0.3 else 1
            pixels = random.randint(500, 1000) * direction
            driver.execute_script(f"window.scrollBy(0, {pixels});")
            if direction < 0:
                scroll_up_count += 1
            print(f"[~] JS scrolled {'up' if direction < 0 else 'down'}.")

        random_sleep(3, 5)

def main():
    driver = None
    try:
        driver = uc.Chrome(headless=False)
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
            print("[!] Verification required. Fetching code from email...")
            random_sleep(2, 5)
            if not enter_verification_code(driver, email):
                print("[✖] Failed to enter verification code.")
                return
            print("[✓] Verification successful, no need to check CAPTCHA.")

        # else:
        #     if not wait_for_captcha_to_clear(driver, sadcaptcha, timeout=120):
        #         print("[✖] CAPTCHA was not cleared. Aborting.")
        #         return

        try:
            WebDriverWait(driver, 90).until(lambda d: "foryou" in d.current_url)
            print(f"[✓] Redirected to {driver.current_url}. Login successful.")
            handle_after_login(driver, sadcaptcha)
        except TimeoutException:
            print(f"[✖] Still not redirected to /foryou after login. Current URL: {driver.current_url}")

    except Exception as e:
        print(f"[!] Main error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
