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
from tiktok_captcha_solver import SeleniumSolver
import undetected_chromedriver as uc

def random_sleep(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

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

        print("[*] Credentials filled. Please manually click the 'Log in' button.")
        print("[*] Waiting for login success (up to 2 mins)...")

        login_btn = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/button')
        login_btn.click()
        print("[+] Login successful.")
    
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
    try:
        index = get_active_scroll_index(driver)
        print(f"[*] Active scroll index: {index}")
        article = driver.find_element(By.XPATH, f"//article[@data-scroll-index='{index}']")
        like_btn = article.find_element(By.XPATH, ".//section[2]//button[2]")
        like_btn.click()
        random_sleep(1, 2)
        print("[+] Video liked.")
        return

    except Exception as e:
        print(f"[!] Like action failed: {e}")

def try_to_share_video(driver):
    try:
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
        return
    except Exception as e:
        print("[!] Share flow failed:", e)

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
        # Method 1: Check for iframe that contains CAPTCHA
        iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'captcha')]")
        print("[*] CAPTCHA iframe detected.")
        return True
    except NoSuchElementException:
        pass

    try:
        # Method 2: Check for common verification text
        verify_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Verify') or contains(text(), 'Slide to verify')]")
        print("[*] CAPTCHA verify text detected.")
        return True
    except NoSuchElementException:
        return False

def safe_action(driver, sadcaptcha, action_fn, *args, **kwargs):
    """
    Wraps an action function and checks for CAPTCHA before or after it runs.
    """
    if is_captcha_present(driver):
        print("[!] CAPTCHA detected before action.")
        sadcaptcha.solve_captcha_if_present()
        print("[+] CAPTCHA solved. Retrying action.")

    result = action_fn(driver, *args, **kwargs)

    if is_captcha_present(driver):
        print("[!] CAPTCHA detected after action.")
        sadcaptcha.solve_captcha_if_present()
        print("[+] CAPTCHA solved.")

    return result

def main():
    driver = None
    try:
        # options = Options()
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--start-maximized")

        # ua = UserAgent()
        # user_agent = ua.random
        # options.add_argument(f"user-agent={user_agent}")

        driver = uc.Chrome(headless=False)
        driver.maximize_window()
        api_key = "5a42012209289ee170f48a66f4155b3b"   
        sadcaptcha = SeleniumSolver(
            driver,
            api_key,
            mouse_step_size=1, # Adjust to change mouse speed
            mouse_step_delay_ms=20 # Adjust to change mouse speed
        )

        # Selenium code that causes a TikTok or Douyin captcha...
        

        email = "japdavev5@gmail.com"
        password = "Tech@123$$$"

        driver.get("https://www.tiktok.com/login")
        random_sleep(2,5)
        sadcaptcha.solve_captcha_if_present()

        safe_action(driver, sadcaptcha, perform_login, email, password)
        # perform_login(driver, email, password)

        video_count = random.randint(6, 10)
        like_index = random.randint(1, video_count - 2)
        share_index = random.randint(like_index + 1, video_count)
        scroll_up_count = 0

        for i in range(video_count):
            print(f"\n[*] Watching video {i + 1}/{video_count}")
            
            random_sleep(10, 15)
            if i == like_index:
                # try_to_like_video(driver)
                safe_action(driver, sadcaptcha, try_to_like_video)

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

    except Exception as e:
        print(f"[!] Main error: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
