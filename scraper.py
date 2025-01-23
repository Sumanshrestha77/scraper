import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

def clean_table_class(class_str):
    """
    Clean and normalize Angular-generated class strings
    """
    if not class_str:
        return ''
    # Remove Angular-specific attributes and normalize
    class_str = re.sub(r'_ngcontent-[a-z0-9-]+', '', class_str)
    return class_str.strip()

def scrape_floor_sheet():
    # URL of the floor sheet
    url = "https://nepalstock.com/live-market"
    
    # Headers to mimic a browser request with additional Angular-specific headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'X-Requested-With': 'XMLHttpRequest',  # Sometimes helps with dynamic content
    }
    
    print('Waiting for page to load...')
    time.sleep(10)
    print('Sleep completed, fetching data...')
    
    try:
        # Send GET request to the URL
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
        
        # Find tables with multiple approaches
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables on the page")
        
        # Debugging: print all table classes
        for i, t in enumerate(tables):
            print(f"Table {i+1} classes: {t.get('class', 'No class')}")
        
        # Multiple strategies to find the correct table
        table_strategies = [
            # Exact class matching (removing Angular-specific attributes)
            lambda: soup.find('table', class_=lambda x: x and 'table__border' in clean_table_class(x)),
            
            # Partial class matching
            lambda: soup.find('table', class_=lambda x: x and all(cls in clean_table_class(x) for cls in ['table', 'table__border'])),
            
            # Find by table structure
            lambda: soup.find('table', lambda tag: 
                tag.name == 'table' and 
                tag.find('thead') and 
                len(tag.find('thead').find_all('th')) > 5
            )
        ]
        
        # Try each strategy to find the table
        table = None
        for strategy in table_strategies:
            table = strategy()
            if table:
                print("\nTable found using a detection strategy!")
                break
        
        if not table:
            print("\nNo table found. The page might be using complex JavaScript rendering.")
            return None
        
        # Extract headers
        headers = [
            "SN", "Symbol", "LTP", "LTV", "Point Change", 
            "% Change", "Open Price", "High Price", "Low Price", 
            "Avg Traded Price", "Volume", "Previous Closing"
        ]
        
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