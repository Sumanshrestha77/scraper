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
        # Send GET request to the URL with verify=False
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Print the response status and content length for debugging
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different methods to find the table
        table = None
        
        # Method 1: Try finding any table
        table = soup.find('table')
        
        if not table:
            print("No table found in the page.")
            # Print the entire HTML for debugging
            print("Page HTML:")
            print(response.text[:1000])  # Print first 1000 characters
            return
        
        # Print table HTML for debugging
        print("\nFound table HTML:")
        print(table.prettify()[:500])  # Print first 500 characters of table
        
        # Extract headers
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                header = th.text.strip().replace(' \xa0', '')
                headers.append(header)
        
        # If no headers found, try getting from first row
        if not headers:
            first_row = table.find('tr')
            if first_row:
                headers = [td.text.strip() for td in first_row.find_all(['th', 'td'])]
        
        print("\nExtracted headers:", headers)
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = [td.text.strip() for td in tr.find_all('td')]
                if row:  # Only add non-empty rows
                    rows.append(row)
        else:
            # If no tbody, get all rows except first (headers)
            all_rows = table.find_all('tr')[1:]  # Skip header row
            for tr in all_rows:
                row = [td.text.strip() for td in tr.find_all('td')]
                if row:  # Only add non-empty rows
                    rows.append(row)
        
        print(f"\nExtracted {len(rows)} rows")
        
        if not rows:
            print("No data rows found in the table")
            return
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers if headers else None)
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'nepse_floor_sheet_{timestamp}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"\nData successfully saved to {filename}")
        
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
    
    # Add a small delay to be respectful to the server
    time.sleep(1)
    scrape_floor_sheet()