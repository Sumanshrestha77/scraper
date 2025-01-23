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
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Print response status
        print(f"Response Status: {response.status_code}")
        
        # Save the raw HTML for inspection (optional for debugging)
        with open('debug_live_market.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved raw HTML to debug_live_market.html")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with the class provided
        table = soup.find('table', class_='table table__border table__lg table-striped table__border--bottom table-head-fixed')
        
        if not table:
            print("\nTable not found. The page might use JavaScript to load data.")
            print("Consider using Selenium or checking for an API endpoint.")
            return
        
        print("\nTable found! Extracting data...")
        
        # Extract headers
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                header = th.text.strip()
                headers.append(header)
        
        print(f"Extracted headers: {headers}")
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = [td.text.strip() for td in tr.find_all('td')]
                rows.append(row)
        
        print(f"Extracted {len(rows)} rows")
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_live_market_{timestamp}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"\nData successfully saved to {filename}")
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    scrape_live_market()
