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
from dotenv import load_dotenv


load_dotenv()

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
        like_btn = article.find_element(By.XPATH, ".//button[.//span[@data-e2e='like-icon']]")
        try:
            like_btn.click()
        except Exception as e:
            print(f"[!] Default click failed, trying JS click: {e}")
            driver.execute_script("arguments[0].click();", like_btn)
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

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[@aria-label='Reply' and @role='button' and contains(@data-e2e, 'comment-reply')]"
            ))
        )

        reply_buttons = driver.find_elements(
            By.XPATH,
            "//span[@aria-label='Reply' and @role='button' and contains(@data-e2e, 'comment-reply')]"
        )

        print(f"[✓] Found {len(reply_buttons)} reply buttons.")
        if not reply_buttons:
            print("[-] No reply buttons found.")
            return

        reply_button = random.choice(reply_buttons)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
        random_sleep(1, 2)
        reply_button.click()
        print("[*] Clicked on random reply button.")

        try:
            placeholder = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'public-DraftEditorPlaceholder-inner')]"))
            )
            placeholder.click()
            print("[*] Clicked placeholder to focus input.")
        except:
            print("[~] Placeholder not found or already gone.")

        # Now send text to the input
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
        )

        reply_text = random.choice(["Nice!", "Haha true", "So relatable!", "Agreed"])
        input_box.send_keys(reply_text)
        random_sleep(1, 2)
        input_box.send_keys(Keys.ENTER)
        print(f"[+] Replied with: {reply_text}")

        try:
            xpath = ("//button[@role='button' and @aria-label='Close' and @data-e2e='browse-close']"
                     " | "
                     "//button[@aria-label='exit']")
            close_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            close_btn.click()
            print("[✓] Closed the comment panel.")
        except Exception as close_error:
            print(f"[!] Failed to close comment panel: {close_error}")

    except Exception as e:
        print(f"[!] Comment reply failed: {e}")


def try_to_share_video(driver):
    index = get_active_scroll_index(driver)
    print(f"[*] Active scroll index: {index}")
    article = driver.find_element(By.XPATH, f"//article[@data-scroll-index='{index}']")
    share_btn = article.find_element(By.XPATH, ".//section[2]//button[3]")
    share_btn.click()
    print("[*] Share button clicked.")
    random_sleep(2, 3)

    try:
        copy_btn = driver.find_element(By.XPATH,
            "//div[@data-e2e='share-copy']//div[@tabindex='0'] | //button[contains(., 'Copy link')]"
        )
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
        # Combined XPath for both UI layouts using union (|)
        xpath = (
            "//*[@id='main-content-homepage_hot']//aside//button"
            " | "
            "//button[@aria-label='Go to next video']"
        )

        # Wait for any scroll button from either layout
        buttons = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

        # Filter usable buttons
        scroll_buttons = [
            btn for btn in buttons
            if btn.is_displayed() and btn.get_attribute("aria-disabled") in [None, "false"]
        ]

        if not scroll_buttons:
            print("[-] No usable scroll buttons found.")
            return False, scroll_up_count

        print(f"[✓] Found {len(scroll_buttons)} usable scroll button(s).")

        # Decide scroll direction
        scroll_direction = "up" if scroll_up_count < max_up and random.random() < 0.3 else "down"
        selected_button = scroll_buttons[0] if scroll_direction == "up" else scroll_buttons[-1]

        # Scroll into view and try clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_button)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(selected_button))
        time.sleep(1)

        for attempt in range(3):
            try:
                selected_button.click()
                print(f"[+] Scrolled {scroll_direction} using button.")
                break
            except Exception as e:
                print(f"[!] Click attempt {attempt + 1} failed: {e}")
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_button)
                if attempt == 2:
                    print("[✖] All attempts failed. Skipping scroll.")
                    return False, scroll_up_count

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

        email = "japdavev5@gmail.com"
        password = "Tech@123$$$"

        driver.get("https://www.tiktok.com/login")
        random_sleep(2, 5)
        sadcaptcha.solve_captcha_if_present()

        with_retries(lambda: safe_action(driver, sadcaptcha, perform_login, email, password))

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
