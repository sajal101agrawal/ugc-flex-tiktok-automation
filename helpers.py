from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import imaplib
import email
import re
from html import unescape
import os
from datetime import datetime
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random
from selenium.webdriver.common.keys import Keys


load_dotenv()

def get_code_from_email(username=None, delay=10):
    try:
        print(f"[i] Waiting {delay} seconds to allow email delivery...")
        time.sleep(delay)

        with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
            print("Logging in to Mail...")
            CHALLENGE_EMAIL = os.getenv("EMAIL")
            CHALLENGE_PASSWORD = os.getenv("PASS")
            mail.login(CHALLENGE_EMAIL, CHALLENGE_PASSWORD)
            print("Logged in to Mail")

            mail.select("inbox")
            print("Selected Inbox")

            today = datetime.now().strftime('%d-%b-%Y')
            result, data = mail.search(None, f'(SINCE "{today}")')
            if result != "OK":
                raise Exception(f"Error searching for emails: {result}")

            email_ids = data[0].split()
            print(f"Found {len(email_ids)} messages from today.")

            tiktok_emails = []

            for num in email_ids:
                result, data = mail.fetch(num, "(RFC822)")
                if result != "OK":
                    continue

                msg = email.message_from_bytes(data[0][1])
                from_address = msg["From"]
                subject = msg["Subject"] or ""

                if "tiktok" not in from_address.lower() and "tiktok" not in subject.lower():
                    continue

                date_header = msg["Date"]
                try:
                    timestamp = parsedate_to_datetime(date_header)
                except:
                    timestamp = datetime.min

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                tiktok_emails.append((timestamp, body))

            tiktok_emails.sort(reverse=True, key=lambda x: x[0])

            for timestamp, body in tiktok_emails:
                code_match = re.search(r"\b\d{6}\b", body)
                if code_match:
                    print(f"Found TikTok verification code: {code_match.group(0)} at {timestamp}")
                    return code_match.group(0)

            print("No TikTok verification code found.")
            return False

    except imaplib.IMAP4.error as e:
        print(f"IMAP error occurred: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

    return False

def enter_verification_code(driver, username):
    code = get_code_from_email(username)
    if not code:
        print("[!] No verification code found in email.")
        return False

    try:
        print(f"[*] Entering verification code: {code}")
        code_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.code-input"))
        )
        code_input.clear()
        code_input.send_keys(code)

        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
        )
        next_btn.click()
        print("[✓] Code submitted.")
        return True

    except Exception as e:
        print(f"[!] Error while entering code: {e}")
        return False


def random_sleep(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))


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
        xpath = (
            "//*[@id='main-content-homepage_hot']//aside//button"
            " | "
            "//button[@aria-label='Go to next video']"
        )

        buttons = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

        scroll_buttons = [
            btn for btn in buttons
            if btn.is_displayed() and btn.get_attribute("aria-disabled") in [None, "false"]
        ]

        if not scroll_buttons:
            print("[-] No usable scroll buttons found.")
            return False, scroll_up_count

        print(f"[✓] Found {len(scroll_buttons)} usable scroll button(s).")

        scroll_direction = "up" if scroll_up_count < max_up and random.random() < 0.3 else "down"
        selected_button = scroll_buttons[0] if scroll_direction == "up" else scroll_buttons[-1]

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


def is_verification_prompt_present(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Suspicious activity detected')]"))
        )
        return True
    except TimeoutException:
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
            time.sleep(2)
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
