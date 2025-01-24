import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_floor_sheet():
    """
    Scrape the floor sheet data from Nepal Stock Exchange website
    
    Returns:
    pandas.DataFrame: Scraped floor sheet data
    """
    try:
        # Step 1: Initial request
        logger.info("Starting scraping process...")
        
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Send GET request
        logger.info("Sending request to the website...")
        response = requests.get('https://nepalstock.com/floor-sheet', headers=headers, timeout=10)
        
        # Check if request was successful
        response.raise_for_status()
        
        logger.info(f"Request status code: {response.status_code}")
        logger.info(f"Response content length: {len(response.text)} characters")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table (this might need adjustment based on the actual HTML structure)
        table = soup.find('table')
        
        if not table:
            logger.error("No table found on the page. Check the website structure.")
            return None
        
        # Extract headers
        headers = [header.get_text(strip=True) for header in table.find_all('th')]
        logger.info(f"Found {len(headers)} headers: {headers}")
        
        # Extract rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if cells:
                row_data = [cell.get_text(strip=True) for cell in cells]
                rows.append(row_data)
        
        logger.info(f"Extracted {len(rows)} data rows")
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        return df
    
    except requests.RequestException as e:
        logger.error(f"Request error occurred: {e}")
        return None
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def main():
    # Scrape the floor sheet
    logger.info("Starting main scraping process...")
    
    floor_sheet_df = scrape_floor_sheet()
    
    if floor_sheet_df is not None and not floor_sheet_df.empty:
        # Save to CSV
        output_file = 'nepal_stock_floor_sheet.csv'
        floor_sheet_df.to_csv(output_file, index=False)
        logger.info(f"Floor sheet data saved to {output_file}")
        
        # Display the first few rows
        logger.info("\nFirst few rows of the data:")
        print(floor_sheet_df.head())
    else:
        logger.warning("No data could be scraped.")

if __name__ == '__main__':
    main()