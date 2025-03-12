import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# Selenium Remote WebDriver URL (from Docker Compose)
SELENIUM_URL = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")

# Function to check if Selenium is ready
def wait_for_selenium(timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://selenium:4444/wd/hub/status")
            if response.status_code == 200 and response.json().get("value", {}).get("ready", False):
                print("✅ Selenium is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass  # Selenium is not ready yet
        
        print("⏳ Waiting for Selenium to be ready...")
        time.sleep(2)

    raise RuntimeError("❌ Selenium did not become ready in time.")

# Wait for Selenium before proceeding
wait_for_selenium()

# Set Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Connect to Selenium Server
driver = webdriver.Remote(
    command_executor=SELENIUM_URL,
    options=chrome_options
)

try:
    driver.get("https://www.yogonet.com/international/")
    time.sleep(2)  # Give time for the page to load

    print("Page Title:", driver.title)

finally:
    driver.quit()
