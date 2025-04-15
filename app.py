import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def auto_scroll(driver, duration=60):
    driver.get("https://www.tiktok.com")
    print("[*] TikTok loaded.")
    time.sleep(20)  # Initial wait for content to load

    start_time = time.time()
    scroll_count = 0

    while (time.time() - start_time) < duration:
        scroll_btn = driver.find_element(By.XPATH,'//*[@id="main-content-homepage_hot"]/aside/div/div[2]/button/div/div')
        scroll_btn.click()
        scroll_count += 1
        print(f"[+] Scrolled {scroll_count} time(s). Waiting 10s...")
        time.sleep(10)

def main():
    driver = setup_driver()
    try:
        auto_scroll(driver, duration=60)  # Scroll for 60 seconds total
    finally:
        driver.quit()
        print("[*] Driver closed.")

if __name__ == "__main__":
    main()
