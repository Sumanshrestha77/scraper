import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os
import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class NepseScraper:
    def __init__(self, output_dir='scrape_outputs'):
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Track previously scraped data to avoid duplicates
        self.previous_data = None
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        
        # Signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nScraping stopped by user. Closing browser...")
        self.driver.quit()
        sys.exit(0)

    def scrape_floor_sheet(self):
        url = "https://nepalstock.com/live-market"
        
        try:
            # Navigate to the page
            self.driver.get(url)
            
            # Wait for the table to be present (up to 10 seconds)
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table__border"))
            )
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find the table
            table = soup.find('table', class_=lambda x: x and 'table' in x and 'table__border' in x)
            
            if not table:
                print("Table not found. Skipping this iteration.")
                return None
            
            # Updated headers based on the table structure
            headers = [
                "SN", "Symbol", "LTP", "LTV", "Point Change", 
                "% Change", "Open Price", "High Price", "Low Price", 
                "Avg Traded Price", "Volume", "Previous Closing"
            ]
            
            # Extract rows
            rows = []
            tbody = table.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    row = []
                    for td in tr.find_all('td'):
                        row.append(td.text.strip())
                    rows.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Check for new data
            if self.previous_data is not None:
                # Find new rows by comparing with previous scrape
                df = self.find_new_rows(df)
            
            # Update previous data
            self.previous_data = df
            
            if not df.empty:
                # Generate filename with current timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join(self.output_dir, f'nepse_floor_sheet_{timestamp}.csv')
                
                # Save to CSV
                df.to_csv(filename, index=False)
                print(f"New data saved to {filename}")
                
                return df
            else:
                print("No new data found in this iteration.")
                return None
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            print(traceback.format_exc())

    def find_new_rows(self, current_df):
        # Compare current dataframe with previous dataframe
        if self.previous_data is None:
            return current_df
        
        # Remove any rows that exactly match previous data
        new_df = current_df[~current_df.apply(tuple, axis=1).isin(self.previous_data.apply(tuple, axis=1))]
        
        return new_df

    def continuous_scrape(self, interval=60):
        print(f"Starting continuous scraping. Interval: {interval} seconds. Press Ctrl+C to stop.")
        
        try:
            while True:
                print("\nScraping at:", datetime.now())
                self.scrape_floor_sheet()
                
                # Wait for specified interval before next scrape
                time.sleep(interval)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Ensure browser is closed
            self.driver.quit()

if __name__ == "__main__":
    # Initialize scraper and start continuous scraping
    scraper = NepseScraper()
    scraper.continuous_scrape(interval=60)  # Scrape every 60 seconds