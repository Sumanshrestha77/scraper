import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_floor_sheet():
    """
    Scrape the floor sheet data from Nepal Stock Exchange website
    
    Returns:
    pandas.DataFrame: Scraped floor sheet data
    """
    # Setup Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Navigate to the website
        driver.get('https://nepalstock.com/floor-sheet')
        
        # Wait for the table to load (up to 10 seconds)
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        
        # Additional wait to ensure full content is loaded
        time.sleep(5)
        
        # Find the table
        table = driver.find_element(By.TAG_NAME, 'table')
        
        # Extract headers
        headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
        
        # Extract rows
        rows = []
        for row in table.find_elements(By.TAG_NAME, 'tr')[1:]:  # Skip header row
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:  # Ensure the row has data
                row_data = [cell.text for cell in cells]
                rows.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        return df
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        # Close the browser
        driver.quit()

def main():
    # Scrape the floor sheet
    floor_sheet_df = scrape_floor_sheet()
    
    if floor_sheet_df is not None:
        # Save to CSV
        floor_sheet_df.to_csv('nepal_stock_floor_sheet.csv', index=False)
        print("Floor sheet data scraped and saved to nepal_stock_floor_sheet.csv")
        
        # Optional: Display the first few rows
        print("\nFirst few rows of the data:")
        print(floor_sheet_df.head())

if __name__ == '__main__':
    main()