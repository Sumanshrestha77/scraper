import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_floor_sheet():
    # URL of the floor sheet
    url = "https://merolagani.com/Floorsheet.aspx"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print('Sleeping for 10 seconds...')
    time.sleep(10)
    print('Sleep completed, fetching data...')
    
    try:
        # Send GET request to the URL with verify=False
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Print response status and length
        print(f"Response Status: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        # Save the raw HTML for inspection
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved raw HTML to debug_response.html")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print all table classes found
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables on the page")
        for i, t in enumerate(tables):
            print(f"Table {i+1} classes: {t.get('class', 'No class')}")
        
        # Try to find the specific table
        table = soup.find('table', class_='table table-bordered table-striped table-hover sortable')
        
        if not table:
            print("\nTable not found with specific class. Trying alternative approaches...")
            
            # Try finding by partial class match
            table = soup.find('table', class_='table')
            
            if not table:
                print("Still no table found. The page might be using JavaScript to load data.")
                print("\nThis website might be using JavaScript to load the table dynamically.")
                print("You might need to use Selenium or Playwright instead of requests.")
                return
        
        print("\nTable found! Extracting data...")
        
        # Extract headers
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                header = th.text.strip().replace(' \xa0', '')
                headers.append(header)
        
        print(f"Extracted headers: {headers}")
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    row.append(td.text.strip())
                rows.append(row)
        
        print(f"Extracted {len(rows)} rows")
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        
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
    # Suppress SSL verification warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    scrape_floor_sheet()