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
from dotenv import load_dotenv


load_dotenv()

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
        like_btn = article.find_element(By.XPATH, ".//section[2]//button[1]")
        like_btn.click()
        random_sleep(1, 2)
        print("[+] Video liked.")
        return

    except Exception as e:
        print(f"[!] Like action failed: {e}")


def try_to_comment_video(driver):
    try:
        index = get_active_scroll_index(driver)
        print(f"[*] Active scroll index: {index}")
        article = driver.find_element(By.XPATH, f"//article[@data-scroll-index='{index}']")
        comment_btn = article.find_element(By.XPATH, ".//section[2]//button[2]")
        comment_btn.click()
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
        # Step 1: Get all buttons in the scroll area
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//*[@id='main-content-homepage_hot']//aside//button")
            )
        )
        print(f"[✓] Found {len(buttons)} button(s)")

        # Step 2: Log and filter only active buttons
        for idx, btn in enumerate(buttons):
            aria_disabled = btn.get_attribute("aria-disabled")
            print(f"Button {idx}: displayed={btn.is_displayed()}, aria-disabled={aria_disabled}")
        
        scroll_buttons = [
            btn for btn in buttons
            if btn.is_displayed() and btn.get_attribute("aria-disabled") in [None, "false"]
        ]

        if not scroll_buttons:
            print("[-] No active scroll buttons passed filtering.")
            return False, scroll_up_count

        # Step 3: Decide scroll direction
        scroll_direction = "up" if (scroll_up_count < max_up and random.random() < 0.3) else "down"
        selected_button = scroll_buttons[0] if scroll_direction == "up" else scroll_buttons[-1]

        # Step 4: Scroll into view and wait until clickable
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_button)
        time.sleep(1)

        # Wait until the button is clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(selected_button))

        # Step 5: Ensure the button is not intercepted by other elements
        # Retry clicking if interception occurs (up to 3 attempts)
        for attempt in range(3):
            try:
                selected_button.click()
                print(f"[+] Scrolled {scroll_direction} using button.")
                break  # Break the loop if the click was successful
            except Exception as e:
                print(f"[!] Click attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    print("[✖] All click attempts failed. Aborting.")
                    return False, scroll_up_count
                # If clicked failed due to interception, reattempt after short delay
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_button)

        # Step 6: Track scroll up count
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

def wait_for_captcha_to_clear(driver, sadcaptcha, timeout=90):
    """
    Waits until CAPTCHA is no longer present after solving.
    Includes retries and delays to handle async loading issues.
    """
    print("[*] Checking for CAPTCHA...")

    if "foryou" in driver.current_url:
        print("[✓] Already on /foryou. Skipping CAPTCHA clearance check.")
        return True

    if not is_captcha_present(driver):
        print("[✓] No CAPTCHA present.")
        return True

    print("[!] CAPTCHA detected. Attempting to solve...")
    solve_attempts = 0
    max_attempts = 3

    while solve_attempts < max_attempts:
        if is_captcha_present(driver):
            print(f"[~] Solving CAPTCHA (Attempt {solve_attempts + 1})...")
            time.sleep(2)  # Short delay before solving to allow loading
            try:
                sadcaptcha.solve_captcha_if_present()
            except Exception as e:
                print(f"[x] Error during CAPTCHA solve: {e}")

        print("[~] Waiting for CAPTCHA to clear...")

        cleared = False
        for i in range(timeout // max_attempts):
            if "foryou" in driver.current_url:
                print("[✓] Reached /foryou page. Skipping CAPTCHA check.")
                return True
            if not is_captcha_present(driver):
                cleared = True
                print("[+] CAPTCHA cleared.")
                break
            time.sleep(1)

        if cleared:
            return True

        solve_attempts += 1
        print(f"[!] CAPTCHA still present after attempt {solve_attempts}.")

    print("[✖] CAPTCHA still present after max attempts.")
    return False


def handle_after_login(driver, sadcaptcha):
    # Continue with video watching/interaction
    # if not wait_for_captcha_to_clear(driver, sadcaptcha):
    #     print("[✖] CAPTCHA was not cleared. Aborting.")
    #     return
    video_count = random.randint(6, 10)
    like_index = 1
    # like_index = random.randint(1, video_count - 2)
    # share_index = random.randint(like_index + 1, video_count)
    # comment_index = random.randint(like_index + 1, video_count)
    comment_index = 2
    share_index = 3
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
        api_key = "95f77cc41b3f8bccfd02dfb482bf9b75"   
        sadcaptcha = SeleniumSolver(
            driver,
            api_key,
            mouse_step_size=1, # Adjust to change mouse speed
            mouse_step_delay_ms=20 # Adjust to change mouse speed
        )

        # Selenium code that causes a TikTok or Douyin captcha...
        

        # email = "japdavev5@gmail.com"
        email = os.getenv("EMAIL")
        password = "Tech@123$$$"

        driver.get("https://www.tiktok.com/login")
        # driver.get("https://www.tiktok.com/foryou")
        random_sleep(2,5)
        sadcaptcha.solve_captcha_if_present()

        safe_action(driver, sadcaptcha, perform_login, email, password)

        if not wait_for_captcha_to_clear(driver, sadcaptcha, timeout=120):
            print("[✖] CAPTCHA was not cleared. Aborting.")
            return

        # Optionally: wait for home page or profile icon (adjust selector as needed)
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
