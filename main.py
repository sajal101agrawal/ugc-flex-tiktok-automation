import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from helpers import handle_captcha

load_dotenv()


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
        print("Login button clicked!")

        sleep(30)
        # handle_captcha(driver)
        print("Captcha handle successfully")

    except Exception as e:
        print(f"Error during login: {e}")


def reply_to_first_comment(driver, account_name, reply_text):
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
        search_input.send_keys(Keys.RETURN)  # Simulate hitting Enter
        print(f"Searched for account: {account_name}")
        print("Please solve the CAPTCHA manually if prompted.")
        sleep(30)

        # Step 3: Wait for the account to appear in the search results and click it
        account_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='tabs-0-panel-search_top']/div/div/div[1]/div[2]/div/div"))
        )
        account_div.click()
        print(f"Navigated to {account_name}'s profile.")
        sleep(20)

        # Step 4: Find the first post in the account's profile

        first_post_video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[3]/div/div[1]/div/div/div/a/div[1]/div[1]/div[2]/div/video"))
        )
        first_post_video.click()

        first_comment_on_video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[1]"))
        )
        # first_comment_on_video.click()

        print("First post found.")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")


def main():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-unsafe-swiftshader")

    driver = webdriver.Chrome(options=chrome_options)

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    driver.get("https://www.tiktok.com/login/")

    sleep(5)

    perform_login(driver, email, password)
    reply_to_first_comment(driver, "romaniiautalent", "Testing comment")

    sleep(5)

if __name__ == "__main__":
    main()