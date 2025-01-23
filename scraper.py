import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_live_market():
    # URL of the live market page
    url = "https://nepalstock.com/live-market"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print('Sleeping for 10 seconds...')
    time.sleep(10)
    print('Sleep completed, fetching data...')
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with the specified class
        table = soup.find('table', class_='table table__border table__lg table-striped table__border--bottom table-head-fixed')
        
        if not table:
            print("Table not found with the specified class.")
            return
        
        # Extract headers
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                headers.append(th.text.strip())
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = [td.text.strip() for td in tr.find_all('td')]
                rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_live_market_{timestamp}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
        
        return df
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_live_market()
