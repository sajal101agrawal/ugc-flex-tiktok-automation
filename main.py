import os
from dotenv import load_dotenv

load_dotenv()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from fake_useragent import UserAgent

def perform_logout(driver):
    try:
        print("Attempting to log out...")

        button_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[1]/div[10]/button/div/div[1]/div'))
        )
        button_div.click()

        print("Button Clicked!")

        logout_button_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="creator-tools-selection-menu-header"]/li[8]/button/div'))
        )
        logout_button_div.click()
        print("Logout Button Clicked!")

        logout_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/div[3]/div/div/div/div[2]/button[2]'))
        )
        logout_div.click()
        print("You have been logged out")

    except Exception as e:
        print(f"Error during login: {e}")
        raise


def perform_login(driver, email, password):
    try:
        print("Attempting to log in...")

        login_with_email_part = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[3]/div[2]/div[2]'))
        )
        login_with_email_part.click()
        print("Switched to email/password login part.")

        login_with_email_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[1]/a'))
        )
        login_with_email_button.click()
        print("Switched to email/password login.")

        email_input = driver.find_element(By.XPATH, "//input[@name='username']")
        email_input.send_keys(email)

        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(password)

        print("Password entered and login attempt submitted.")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/button'))
        )
        login_button.click()
        print("Login button clicked!!")

        time.sleep(30)
        # handle_captcha(driver)
        print("Captcha handled or login complete.")

    except Exception as e:
        print(f"Error during login: {e}")
        raise


def reply_to_all_comment(driver, account_name, reply_text):
    try:
        print("ACCOUNTS DISABLED")
        # Step 1: Click on the button to open the account search form
        button_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "css-1khkwzw-DivIconWithRedDotContainer"))
        )
        button_div.click()
        print("Search button clicked.")

        # Step 2: Wait for the form to appear and fill in account details
        search_input = button_div.find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div/div[5]/div[1]/div[2]/form/input')
        search_input.send_keys(account_name)
        search_input.send_keys(Keys.RETURN)
        print(f"Searched for account: {account_name}")
        print("Please solve the CAPTCHA manually if prompted.")
        time.sleep(5)

        # Step 3: Wait for the account to appear in the search results and click it
        account_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='tabs-0-panel-search_top']/div/div/div[1]/div[2]/div/div"))
        )
        account_div.click()
        print(f"Navigated to {account_name}'s profile.")
        time.sleep(20)

        # Step 4: Find the first post in the account's profile
        # first_post_video = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[3]/div/div[1]/div/div/div/a/div[1]/div[1]/div[2]/div/video"))
        # )
        # first_post_video.click()

        # Step 5: Wait for the first comment to load
        # first_comment_on_video = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[1]"))
        # )
        # print("First Comment found.")

        post_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@id='main-content-others_homepage']/div/div[2]/div[3]/div/div"))
        )
        if not post_elements:
            print("No posts found for this account.")
            return
        print(f"Found {len(post_elements)} posts.")

        for index, post in enumerate(post_elements, start=1):
            print(f"Opening post {index}...")

            post.click()
            time.sleep(5)
            
            comments_loaded = False
            while not comments_loaded:
                try:
                    comments_section = driver.find_elements(By.XPATH, "//*[@id='app']/div[2]/div[4]/div/div[2]/div[1]/div/div[position() >= 3]")
                    if not comments_section:
                        print("No comments found starting from the third one.")
                        break
                    print(f"Found {len(comments_section)} comments (starting from the third one).")
                    for comment in comments_section:
                        try:
                            reply_button = WebDriverWait(comment, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, ".//span[@aria-label='Reply' and @role='button' and contains(@class, 'css-cpmlpt-SpanReplyButton')]")
                                )
                            )
                            reply_button.click()
                            time.sleep(1)
                            reply_input = comment.find_element(By.XPATH, '//*[@id="placeholder-fovu"]')
                            # reply_input.send_keys(reply_text)
                            # reply_input.send_keys(Keys.RETURN)
                            print("Replied to comment.")
                        except Exception as reply_error:
                            print(f"Error replying to comment: {str(reply_error)}")

                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(2)

                    comments_loaded = True
                except Exception as e:
                    print(f"Error while loading comments: {str(e)}")
                    break
            driver.back()
            time.sleep(3)
            print(f"Back to the feed after post {index}.")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

def main():
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        # chrome_options.add_argument("--user-agent=Your New User-Agent String Here")
        chrome_options.add_argument("--guest")
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f"user-agent={user_agent}")

        driver = webdriver.Chrome(options=chrome_options)

        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")

        driver.get("https://www.tiktok.com/")

        time.sleep(5)
        try:
            Profile_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[1]/div[9]/a/button/div/div[1]/div/img'))
            )
            print("User is already logged in.")
            # perform_logout(driver)

        except:
            # If profile div is not found, login is required
            print("User is not logged in. Attempting to log in.")
        perform_login(driver, email, password)

        reply_to_all_comment(driver, "asu.official", "Testing comment")

        time.sleep(5)

    except Exception as e:
        print(f"Error in main process: {str(e)}")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
