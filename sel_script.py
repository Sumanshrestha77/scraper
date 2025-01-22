from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_floor_sheet():
    logging.info("Starting Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)  # Ensure chromedriver is in PATH or specify its location
    
    try:
        logging.info("Loading page...")
        driver.get("https://nepalstock.com/floor-sheet")
        
        logging.info("Waiting for table to load...")
        # Wait up to 20 seconds for the table to appear
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
        
        logging.info("Table found! Extracting data...")
        # Get the page source after JavaScript has loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the table
        table = soup.find('table', class_='table table__lg table-striped table__border table__border--bottom')
        if not table:
            logging.error("Table not found. Exiting.")
            return
        
        # Extract headers
        headers = [th.text.strip().replace('\xa0', '') for th in table.find('thead').find_all('th')]
        
        # Extract rows
        rows = [
            [td.text.strip() for td in tr.find_all('td')]
            for tr in table.find('tbody').find_all('tr')
        ]
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        df.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")
        
        return df
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        
    finally:
        driver.quit()
        logging.info("Driver closed.")

if __name__ == "__main__":
    scrape_floor_sheet()
