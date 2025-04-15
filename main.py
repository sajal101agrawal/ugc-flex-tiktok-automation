import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def random_sleep(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def perform_login(driver, email, password):
    try:
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

        print("[*] Credentials filled. Please manually click the 'Log in' button.")
        print("[*] Waiting for login success (up to 2 mins)...")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@aria-label, 'Profile') or contains(@href, '/user')]"))
        )
        print("[+] Login successful.")
    except TimeoutException:
        print("[!] Login timeout. Please check credentials or complete login manually.")
        raise
    except Exception as e:
        print(f"[!] Login error: {e}")
        raise

def try_to_like_video(driver):
    try:
        like_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Like video')]")
        for btn in like_buttons:
            if btn.get_attribute("aria-pressed") == "false":
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                random_sleep(1, 2)
                btn.click()
                print("[+] Video liked.")
                return
        print("[~] No likeable video found or already liked.")
    except Exception as e:
        print(f"[!] Like action failed: {e}")

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

def main():
    driver = None
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")

        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f"user-agent={user_agent}")

        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        email = "sajal101agrawal@gmail.com"
        password = "@Tdnfi7nupy8"

        driver.get("https://www.tiktok.com/login")
        random_sleep(5, 10)

        perform_login(driver, email, password)

        video_count = random.randint(6, 10)
        like_index = random.randint(1, video_count - 2)
        share_index = random.randint(like_index + 1, video_count)
        scroll_up_count = 0

        for i in range(video_count):
            print(f"\n[*] Watching video {i + 1}/{video_count}")
            
            random_sleep(30, 50)

            if i == like_index:
                try_to_like_video(driver)

            if i == share_index:
                try:
                    share_button = driver.find_element(By.XPATH, '//*[@id="column-list-container"]/article[1]/div/section[2]/button[3]')
                    share_button.click()
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
                except Exception as e:
                    print("[!] Share flow failed:", e)

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

    except Exception as e:
        print(f"[!] Main error: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
