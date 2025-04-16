import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
from tiktok_captcha_solver import SeleniumSolver
import undetected_chromedriver as uc

def random_sleep(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def with_retries(fn, retries=3, delay=2, backoff=2, **kwargs):
    for attempt in range(retries):
        try:
            return fn(**kwargs)
        except Exception as e:
            print(f"[!] Attempt {attempt + 1} failed for {fn.__name__}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= backoff
            else:
                print(f"[X] Failed after {retries} attempts.")
                raise

def perform_login(driver, email, password):
    try:
        email_option = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div/div/div/div[3]/div[2]/div[2]/div')
        email_option.click()

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

def get_active_scroll_index(driver):
    script = """
    const articles = document.querySelectorAll('article[data-scroll-index]');
    for (let article of articles) {
        const rect = article.getBoundingClientRect();
        if (rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)) {
            return article.getAttribute('data-scroll-index');
        }
    }
    return null;
    """
    return driver.execute_script(script)

def try_to_like_video(driver):
    index = get_active_scroll_index(driver)
    print(f"[*] Active scroll index: {index}")
    article = driver.find_element(By.XPATH, f"//article[@data-scroll-index='{index}']")
    like_btn = article.find_element(By.XPATH, ".//section[2]//button[2]")
    like_btn.click()
    random_sleep(1, 2)
    print("[+] Video liked.")

def try_to_share_video(driver):
    index = get_active_scroll_index(driver)
    print(f"[*] Active scroll index: {index}")
    article = driver.find_element(By.XPATH, f"//article[@data-scroll-index='{index}']")
    share_btn = article.find_element(By.XPATH, ".//section[2]//button[4]")
    share_btn.click()
    print("[*] Share button clicked.")
    random_sleep(2, 3)

    try:
        copy_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Copy link')]")
        copy_btn.click()
        print("[+] Link copied.")
    except NoSuchElementException:
        print("[!] Copy link not found.")

    random_sleep(1, 2)

    try:
        close_popup = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
        close_popup.click()
        print("[*] Share popup closed.")
    except NoSuchElementException:
        print("[-] Close button for share popup not found.")

def click_random_scroll_button(driver, scroll_up_count, max_up=2):
    try:
        buttons = driver.find_elements(By.XPATH, "//aside[contains(@class,'AsideOneColumnSidebar')]//button")
        scroll_buttons = [btn for btn in buttons if btn.get_attribute("aria-disabled") == "false"]

        if not scroll_buttons:
            print("[-] No active scroll buttons found.")
            return False, scroll_up_count

        scroll_direction = "up" if (scroll_up_count < max_up and random.random() < 0.3) else "down"
        selected_button = scroll_buttons[0] if scroll_direction == "up" else scroll_buttons[-1]

        driver.execute_script("arguments[0].scrollIntoView(true);", selected_button)
        random_sleep(1, 2)
        selected_button.click()
        print(f"[+] Scrolled {scroll_direction} using button.")

        if scroll_direction == "up":
            scroll_up_count += 1
        return True, scroll_up_count
    except Exception as e:
        print(f"[!] Scroll error: {e}")
        return False, scroll_up_count

def is_captcha_present(driver):
    try:
        driver.find_element(By.XPATH, "//iframe[contains(@src, 'captcha')]")
        print("[*] CAPTCHA iframe detected.")
        return True
    except NoSuchElementException:
        pass

    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Verify') or contains(text(), 'Slide to verify')]")
        print("[*] CAPTCHA verify text detected.")
        return True
    except NoSuchElementException:
        return False

def safe_action(driver, sadcaptcha, action_fn, *args, retries=3, **kwargs):
    for attempt in range(retries):
        try:
            if is_captcha_present(driver):
                print("[!] CAPTCHA detected before action.")
                sadcaptcha.solve_captcha_if_present()
                print("[+] CAPTCHA solved.")

            result = action_fn(driver, *args, **kwargs)

            if is_captcha_present(driver):
                print("[!] CAPTCHA detected after action.")
                sadcaptcha.solve_captcha_if_present()
                print("[+] CAPTCHA solved.")

            return result
        except Exception as e:
            print(f"[!] safe_action attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2)

def main():
    driver = None
    try:
        driver = uc.Chrome(headless=False)
        driver.maximize_window()

        api_key = "ca73e4fdf55a63b83ecfff3194754775"
        sadcaptcha = SeleniumSolver(driver, api_key, mouse_step_size=1, mouse_step_delay_ms=20)

        email = "sajal101agrawal@gmail.com"
        password = "@Tdnfi7nupy8"

        driver.get("https://www.tiktok.com/login")
        random_sleep(2, 5)
        sadcaptcha.solve_captcha_if_present()

        with_retries(lambda: safe_action(driver, sadcaptcha, perform_login, email, password))

        video_count = random.randint(6, 10)
        like_index = random.randint(1, video_count - 2)
        share_index = random.randint(like_index + 1, video_count)
        scroll_up_count = 0

        for i in range(video_count):
            print(f"\n[*] Watching video {i + 1}/{video_count}")
            random_sleep(10, 15)

            if i == like_index:
                with_retries(lambda: safe_action(driver, sadcaptcha, try_to_like_video))

            if i == share_index:
                with_retries(lambda: safe_action(driver, sadcaptcha, try_to_share_video))

            def scroll_fn():
                return click_random_scroll_button(driver, scroll_up_count)
            try:
                success, scroll_up_count = with_retries(scroll_fn)
            except:
                print("[X] All scroll attempts failed.")
                success = False

            if not success:
                print("[!] Fallback to JS scroll.")
                direction = -1 if scroll_up_count < 2 and random.random() < 0.3 else 1
                pixels = random.randint(500, 1000) * direction
                driver.execute_script(f"window.scrollBy(0, {pixels});")
                if direction < 0:
                    scroll_up_count += 1
                print(f"[~] JS scrolled {'up' if direction < 0 else 'down'}.")

            random_sleep(3, 5)

    except Exception as e:
        print(f"[!] Main error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
