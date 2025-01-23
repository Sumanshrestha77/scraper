from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

def scrape_floor_sheet():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto('https://nepalstock.com/live-market')
        page.wait_for_selector('table', timeout=30000)
        
        # Extract table data
        table_rows = page.query_selector_all('table tr')
        
        headers = ["SN", "Symbol", "LTP", "LTV", "Point Change", 
                   "% Change", "Open Price", "High Price", "Low Price", 
                   "Avg Traded Price", "Volume", "Previous Closing"]
        
        rows = []
        for row in table_rows[1:]:  # Skip header
            cells = row.query_selector_all('td')
            row_data = [cell.inner_text() for cell in cells]
            rows.append(row_data)
        
        browser.close()
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Save CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        return df

# Prerequisites:
# pip install playwright pandas
# playwright install

if __name__ == "__main__":
    scrape_floor_sheet()