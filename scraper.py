import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_floor_sheet():
    # URL of the floor sheet
    url = "https://nepalstock.com/floor-sheet"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(10)
    print('sleeping for 10 sec')
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with the specified class
        table = soup.find('table', class_='table table__lg table-striped table__border table__border--bottom')
        
        if not table:
            print("Table not found. The website structure might have changed.")
            return
        
        # Extract headers
        headers = []
        for th in table.find('thead').find_all('th'):
            # Clean header text by removing the icon reference
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
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Add a small delay to be respectful to the server
    time.sleep(1)
    scrape_floor_sheet()