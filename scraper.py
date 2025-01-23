import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os
import signal
import sys

class NepseScraper:
    def __init__(self, output_dir='scrape_outputs'):
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Track previously scraped data to avoid duplicates
        self.previous_data = None
        
        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nScraping stopped by user. Exiting...")
        sys.exit(0)

    def scrape_floor_sheet(self):
        url = "https://nepalstock.com/live-market"
        
        try:
            # Send GET request to the URL with verify=False
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table with the updated header structure
            table = soup.find('table', class_='table table__border table__lg table-striped table__border--bottom table-head-fixed')
            
            if not table:
                print("Table not found. Skipping this iteration.")
                return None
            
            # Updated headers based on the new table structure
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
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching the data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            print(traceback.format_exc())

    def find_new_rows(self, current_df):
        # Compare current dataframe with previous dataframe
        if self.previous_data is None:
            return current_df
        
        # Remove any rows that exactly match previous data
        new_df = current_df[~current_df.apply(tuple, axis=1).isin(self.previous_data.apply(tuple, axis=1))]
        
        return new_df

    def continuous_scrape(self, interval=30):
        print(f"Starting continuous scraping. Interval: {interval} seconds. Press Ctrl+C to stop.")
        
        while True:
            print("\nScraping at:", datetime.now())
            self.scrape_floor_sheet()
            
            # Wait for specified interval before next scrape
            time.sleep(interval)

if __name__ == "__main__":
    # Suppress SSL verification warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Initialize scraper and start continuous scraping
    scraper = NepseScraper()
    scraper.continuous_scrape(interval=30)  # Scrape every 60 seconds