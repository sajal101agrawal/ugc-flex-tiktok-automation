import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import requests
import base64


load_dotenv()


# Function to handle CAPTCHA detection and solve it using the SadCaptcha API
def image_to_base64(driver, image_element):
    # Execute JavaScript to get the base64-encoded image from the blob URL
    base64_image = driver.execute_script("""
        var img = arguments[0];
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/png').split(',')[1];  // Get the Base64 data, remove the prefix
    """, image_element)
    return base64_image

# Function to handle CAPTCHA detection and solve it using the SadCaptcha API
def handle_captcha(driver):
    print("CAPTCHA detected, solving...")

    API_KEY = os.getenv("API_KEY")  # Fetch API key from environment variables

    try:
        # Locate the outer and inner CAPTCHA images
        outer_image_element = driver.find_element(By.XPATH, '//img[contains(@class, "cap-h-[170px]")]')  # Adjust with correct XPath
        inner_image_element = driver.find_element(By.XPATH, '//img[contains(@class, "cap-h-[105px]")]')  # Adjust with correct XPath

        # Convert images to Base64
        outer_image_b64 = image_to_base64(driver, outer_image_element)
        inner_image_b64 = image_to_base64(driver, inner_image_element)

        # Prepare the payload to send to the SadCaptcha API
        payload = {
            "outerImageB64": outer_image_b64,
            "innerImageB64": inner_image_b64
        }

        # Send the request to the API
        response = requests.post(
            f"https://www.sadcaptcha.com/api/v1/rotate?licenseKey={API_KEY}", json=payload
        )

        # Check the response from the API
        if response.status_code == 200:
            print("CAPTCHA solved successfully!")
            return response.json()  # Process the response data
        else:
            print(f"Error solving CAPTCHA: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error while handling CAPTCHA: {e}")
        return None

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

        try:
            captcha_frame = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[8]/div/div/div/div[1]'))  # Update with actual CAPTCHA iframe XPath
            )
            print("CAPTCHA iframe found.")
            handle_captcha(driver)
            return

        except Exception as e:
            print(f"No CAPTCHA detected or failed to locate CAPTCHA., {str(e)}")
            pass

    except Exception as e:
        if "incorrect" in str(e).lower():
            print("Login failed: Incorrect credentials.")
        else:
            print(f"Error during login: {e}")

# Main script to run the login procedure
def main():
    # Load Chrome options from environment variables if needed
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Retrieve credentials from environment variables
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    # Navigate directly to the login page
    driver.get("https://www.tiktok.com/login/")

    # Add a delay to ensure page has fully loaded
    sleep(5)

    # Perform login by calling the function
    perform_login(driver, email, password)

    # Wait for some time to ensure successful login before closing
    sleep(5)

    # Quit the browser
    driver.quit()

if __name__ == "__main__":
    main()
