from sel_script import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_floor_sheet():
    print("Starting Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Loading page...")
        driver.get("https://nepalstock.com/floor-sheet")
        
        print("Waiting for table to load...")
        # Wait up to 20 seconds for the table to appear
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
        
        print("Table found! Extracting data...")
        # Get the page source after JavaScript has loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the table
        table = soup.find('table', class_='table table__lg table-striped table__border table__border--bottom')
        
        # Extract headers
        headers = []
        for th in table.find('thead').find_all('th'):
            header = th.text.strip().replace(' \xa0', '')
            headers.append(header)
        
        # Extract rows
        rows = []
        for tr in table.find('tbody').find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
        return df
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_floor_sheet()