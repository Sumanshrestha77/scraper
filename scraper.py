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
    
    try:
        # Add 10 second delay before fetching
        print("Waiting for 10 seconds before fetching data...")
        time.sleep(10)
        
        # Send GET request to the URL with verify=False
        print("Fetching data from the website...")
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First find the div with class table-responsive
        table_div = soup.find('div', class_='table-responsive')
        if not table_div:
            print("Table container div not found")
            return
            
        # Then find the table inside this div
        table = table_div.find('table')
        if not table:
            print("Table not found inside the container")
            return
        
        # Extract headers
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                # Get the text without the icon
                header = th.text.strip().replace(' \xa0', '')
                headers.append(header)
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    # Get the title attribute if it exists, otherwise get the text
                    value = td.get('title', td.text.strip())
                    row.append(value)
                if row:  # Only add non-empty rows
                    rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
        
        # Print first few rows for verification
        print("\nFirst few rows of data:")
        print(df.head())
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # Suppress SSL verification warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("Starting the scraper...")
    scrape_floor_sheet()