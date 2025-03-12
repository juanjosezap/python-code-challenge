import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import spacy

# Selenium Remote WebDriver URL (from Docker Compose)
SELENIUM_URL = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")

# Function to wait until Selenium is ready
def wait_for_selenium(timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check if Selenium is ready by getting its status
            response = requests.get("http://selenium:4444/wd/hub/status")
            if response.status_code == 200 and response.json().get("value", {}).get("ready", False):
                print("✅ Selenium is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass  # Selenium is not ready yet

        print("⏳ Waiting for Selenium to be ready...")
        time.sleep(2)  # Wait for 2 seconds before retrying

    raise RuntimeError("❌ Selenium did not become ready in time.")

# Function to count words that start with a capital letter
def count_words_starting_with_capital(text):
    if pd.isna(text):  # Handle NaN values
        return 0
    
    # Split the text into words and count those starting with capital letters
    words = text.split()
    capital_words = [word for word in words if word and word[0].isupper()]
    return len(capital_words)

# Function to keep the session active
def keep_alive(driver):
    try:
        # Executes a harmless script to keep the session alive
        driver.execute_script("return navigator.userAgent;")
        print("🔄 Keep-alive sent")
    except Exception as e:
        print(f"⚠️ Keep-alive failed: {e}")

def scrape_yogonet():
    # Wait for Selenium before proceeding
    wait_for_selenium()

    # Set Chrome options for headless mode (no UI)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Connect to Selenium Server using Remote WebDriver
    driver = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=chrome_options
    )

    scraped_data = []
    try:
        # Navigate to the Yogonet international website
        driver.get("https://www.yogonet.com/international/")

        # Send keep-alive every 5 seconds
        last_keep_alive = time.time()

        # Wait until the main articles are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contenedor_dato_modulo"))
        )
        # Get all news articles
        articles = driver.find_elements(By.CLASS_NAME, "contenedor_dato_modulo")

        print(f"Found {len(articles)} articles.")

        for index, article in enumerate(articles):
            # Send keep-alive if more than 5 seconds have passed
            if time.time() - last_keep_alive > 5:
                keep_alive(driver)
                last_keep_alive = time.time()

            print(f"Processing article {index+1} of {len(articles)}")
            # Extract elements from the article
            title_element = article.find_element(By.CLASS_NAME, "titulo")
            kicker_element = article.find_element(By.CLASS_NAME, "volanta")
            image_element = article.find_element(By.CLASS_NAME, "imagen")

            # Try to get the link from the article image
            try:
                link = image_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            except Exception as e:
                print(f"Error retrieving image source: {e}")
            # Try to get the image source URL
            try:
                image_src = image_element.find_element(By.TAG_NAME, "img").get_attribute("src")
            except Exception as e:
                print(f"Error retrieving image source: {e}")
            print("*************************************")
            # Append the extracted data to the list
            scraped_data.append(
                {
                    "title": title_element.text,
                    "kicker": kicker_element.text,
                    "link": link,
                    "image": image_src
                }
            )

    except Exception as e:
        print(f"⚠️ Error scraping article: {e}")
    finally:
        driver.quit()  # Ensure the driver is quit to free resources
        print("Driver exit.")

    return scraped_data

def extract_entities(text, entity_label):
    # Load spaCy's English model
    nlp = spacy.load("en_core_web_sm")
    # Process the text to extract entities
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == entity_label]

def post_process(scraped_data):
    # Convert scraped data to DataFrame for processing
    df = pd.DataFrame(scraped_data)
    # Add a column with the total word count of titles
    df['totalwords'] = [len(x.split()) for x in df['title'].tolist()]
    # Add a column with the total character count of titles
    df['totalcharacters'] = df['title'].str.len()
    # Count words starting with a capital letter in titles
    df['capital_word_count'] = df['title'].apply(count_words_starting_with_capital)
    # Apply extraction functions for named entities
    df["persons"] = df["title"].apply(lambda x: extract_entities(x, "PERSON"))
    df["organizations"] = df["title"].apply(lambda x: extract_entities(x, "ORG"))
    df["locations"] = df["title"].apply(lambda x: extract_entities(x, "GPE"))

    return df

if __name__ == "__main__":
    # Execute scraping and post-processing, then print results
    scraped_data = scrape_yogonet()
    post_process_data = post_process(scraped_data)
    print(post_process_data)

