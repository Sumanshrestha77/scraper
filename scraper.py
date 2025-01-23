from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time
import re

def scrape_floor_sheet():
    url = "https://nepalstock.com/live-market"
    print("Starting scraper with Playwright...")
    
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            print("Creating new browser context...")
            context = browser.new_context(
                # Add headers to mimic a real browser
              extra_http_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

            )
            
            page = context.new_page()
            
            # Configure page to handle potential network issues
            page.set_default_timeout(30000)
            
            print("Navigating to the page...")
            try:
                response = page.goto(url, wait_until='networkidle')
                
                # Check response status
                if response and response.status != 200:
                    print(f"Warning: Received status code {response.status}")
                
                # Wait for potential overlays or popups
                page.wait_for_timeout(5000)
                
                # Check if table is present
                print("Checking for table...")
                table_selector = 'table.table.table__border.table__lg.table-striped.table__border--bottom.table-head-fixed'
                
                # Multiple attempts to find the table
                for attempt in range(3):
                    try:
                        page.wait_for_selector(table_selector, timeout=10000)
                        break
                    except Exception as wait_err:
                        print(f"Attempt {attempt + 1} failed to find table: {wait_err}")
                        page.reload()
                        page.wait_for_timeout(3000)
                
                # Extract headers
                headers_elements = page.query_selector_all('thead tr th')
                headers = [header.inner_text().strip() for header in headers_elements]
                print(f"Extracted headers: {headers}")
                
                # Extract table rows
                rows = page.query_selector_all('table.table.table__border.table__lg.table-striped.table__border--bottom.table-head-fixed tbody tr')
                
                data = []
                for row in rows:
                    cells = row.query_selector_all('td')
                    row_data = [cell.inner_text().strip() for cell in cells]
                    
                    # Validate row data matches headers
                    if len(row_data) == len(headers):
                        data.append(row_data)
                    else:
                        print(f"Skipping row with mismatched length: {row_data}")
                
                # Close browser
                browser.close()
                
                # Save data to DataFrame
                df = pd.DataFrame(data, columns=headers)
                
                # Save to CSV
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'nepse_floor_sheet_{timestamp}.csv'
                df.to_csv(filename, index=False)
                
                print(f"Data successfully saved to {filename}")
                return df
            
            except Exception as nav_err:
                print(f"Navigation error: {nav_err}")
                return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    scrape_floor_sheet()