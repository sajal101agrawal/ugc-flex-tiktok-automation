import requests
from selenium.webdriver.common.by import By
import base64
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://www.sadcaptcha.com/api/v1'


def get_image_base64(driver, image_url):
    """Converts an image URL to Base64 format using JavaScript."""
    try:
        base64_image = driver.execute_script("""
            var img = document.createElement('img');
            img.src = arguments[0];
            return new Promise(function(resolve, reject) {
                img.onload = function() {
                    var canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    var ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    var base64 = canvas.toDataURL('image/png');
                    resolve(base64.split(',')[1]);  // Strip out the 'data:image/png;base64,' part
                };
                img.onerror = function() {
                    reject('Error loading image');
                };
            });
        """, image_url)

        return base64_image
    except Exception as e:
        print(f"Error while converting image to Base64: {e}")
        return None


def solve_captcha(api_url, data, captcha_type):
    """Generic function to solve a CAPTCHA using the given API endpoint."""
    try:
        API_KEY = os.getenv("API_KEY")
        response = requests.post(f"{BASE_URL}/{api_url}?licenseKey={API_KEY}", json=data)
        if response.status_code == 200:
            print(f"{captcha_type} CAPTCHA solved successfully!")
            return response.status_code
        else:
            print(f"Error solving {captcha_type} CAPTCHA: {response.status_code}")
            return response.status_code
    except Exception as e:
        print(f"Error while solving {captcha_type} CAPTCHA: {e}")
        return None


def handle_shapes_captcha(driver):
    """Handle the 'shapes' CAPTCHA."""
    try:
        image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="cap-flex cap-flex-col cap-relative"]//img'))
        )
        print("Shapes CAPTCHA image detected. Solving using API...")

        shapes_image_url = image_element.get_attribute("src")
        shapes_image_b64 = get_image_base64(driver, shapes_image_url)

        if shapes_image_b64:
            return solve_captcha('shapes', {'imageB64': shapes_image_b64}, 'Shapes')
        else:
            print("Error: Shapes CAPTCHA image could not be converted to Base64.")
            return None
    except Exception as e:
        print(f"Error while handling shapes CAPTCHA: {e}")
        return None


def handle_image_crawl_captcha(driver):
    """Handle the 'image crawl' CAPTCHA."""
    try:
        print("IMAGE CRAWL CAPTCHA detected. Solving...")

        puzzle_image_element = driver.find_element(By.XPATH, '//div[@class="captcha-container"]//img[1]')
        piece_image_element = driver.find_element(By.XPATH, '//div[@class="captcha-container"]//img[2]') 

        puzzle_image_url = puzzle_image_element.get_attribute('src')
        piece_image_url = piece_image_element.get_attribute('src')

        puzzle_image = requests.get(puzzle_image_url).content
        piece_image = requests.get(piece_image_url).content

        data = {
            'puzzleImageB64': base64.b64encode(puzzle_image).decode(),
            'pieceImageB64': base64.b64encode(piece_image).decode(),
            'slidePieceTrajectory': []
        }

        return solve_captcha('shopee-image-crawl', data, 'Image Crawl')
    except Exception as e:
        print(f"Error handling image crawl CAPTCHA: {e}")
        return None


def handle_rotate_captcha(driver):
    """Handle the 'rotate' CAPTCHA."""
    try:
        outer_image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="captcha-verify-container-main-page"]/div[2]/div[1]/img[1]'))
        )
        inner_image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="captcha-verify-container-main-page"]/div[2]/div[1]/img[2]'))
        )

        outer_image_b64 = extract_base64_from_image(driver, outer_image_element)
        inner_image_b64 = extract_base64_from_image(driver, inner_image_element)

        data = {
            "outerImageB64": outer_image_b64,
            "innerImageB64": inner_image_b64
        }
        return solve_captcha('rotate', data, 'Rotate')
    except Exception as e:
        print(f"Error while handling rotate CAPTCHA: {e}")
        return None


def extract_base64_from_image(driver, image_element):
    """Extract Base64 from an image element."""
    image_url = image_element.get_attribute("src")
    if image_url.startswith("blob:"):
        return driver.execute_script("""
            var img = arguments[0];
            return img.src.split(',')[1];  // Extract base64 part from data URL
        """, image_element)
    else:
        return image_url.split(',')[1]


def is_element_present_and_visible(driver, xpath, timeout=5):
    """Check if an element is present and visible within a specified timeout."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        print(f"Element with XPath {xpath} not visible or not found: {e}")
        return None


def handle_captcha(driver):
    """Check for all possible CAPTCHA types and solve the detected one."""
    captcha_types = {
        'rotate': "/html/body/div[8]/div/div/div/div[1]",
        'shapes': "/html/body/div[8]/div/div/div/div[2]/div",
        'image_crawl': "/html/body/div[8]/div/div/div/div[2]/div[1]"
    }

    for captcha_type, xpath in captcha_types.items():
        print(f"Checking for {captcha_type} CAPTCHA...")
        if is_element_present_and_visible(driver, xpath):
            print(f"Element detected for {captcha_type} CAPTCHA.")
            handler_function = globals()[f'handle_{captcha_type}_captcha']
            status_code = handler_function(driver)
            if status_code is not None:
                break
    else:
        print("No CAPTCHA detected!")
