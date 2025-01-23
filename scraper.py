from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time

def scrape_floor_sheet():
    print("Starting Playwright scraping...")
    
    with sync_playwright() as p:
        try:
            print("Launching browser in headless mode...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Navigating to NEPSE live market page...")
            page.goto('https://nepalstock.com/live-market')
            
            print("Waiting for table to load...")
            page.wait_for_selector('table', timeout=30000)
            
            # Wait for page to stabilize and potentially reload
            print("Waiting 30 seconds for dynamic content to update...")
            time.sleep(30)
            
            # Refresh page to get latest data
            page.reload()
            print("Page reloaded. Waiting for table to stabilize...")
            page.wait_for_selector('table', timeout=30000)
            time.sleep(5)
            
            # Extract table data
            print("Extracting table rows...")
            table_rows = page.query_selector_all('table tr')
            
            headers = ["SN", "Symbol", "LTP", "LTV", "Point Change", 
                       "% Change", "Open Price", "High Price", "Low Price", 
                       "Avg Traded Price", "Volume", "Previous Closing"]
            
            rows = []
            print(f"Total rows found: {len(table_rows)}")
            
            for row in table_rows[1:]:  # Skip header
                cells = row.query_selector_all('td')
                row_data = [cell.inner_text().strip() for cell in cells]
                
                # Validate row data
                if len(row_data) == len(headers):
                    rows.append(row_data)
                else:
                    print(f"Skipping row with incorrect data length: {row_data}")
            
            print(f"Valid rows extracted: {len(rows)}")
            
            # Close browser
            browser.close()
            
            # Deduplication logic
            def load_previous_data():
                try:
                    return pd.read_csv('latest_nepse_data.csv')
                except FileNotFoundError:
                    return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Load previous data
            previous_df = load_previous_data()
            
            # Remove duplicate rows based on all columns
            if not previous_df.empty:
                df = df[~df.apply(tuple, axis=1).isin(previous_df.apply(tuple, axis=1))]
            
            # Only save if new data exists
            if not df.empty:
                # Append to existing data
                combined_df = pd.concat([previous_df, df], ignore_index=True)
                
                # Save latest complete dataset
                combined_df.to_csv('latest_nepse_data.csv', index=False)
                
                # Save just the new data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f'nepse_new_data_{timestamp}.csv'
                df.to_csv(new_filename, index=False)
                
                print(f"New data saved. Total new rows: {len(df)}")
                print(f"Complete dataset updated.")
                print(f"New data saved to: {new_filename}")
            else:
                print("No new data found.")
            
            return df
        
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    scrape_floor_sheet()