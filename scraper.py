import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
import io
import pandas as pd
import time
from datetime import datetime
import os

class NepseTmsScraper:
    def __init__(self, username, password, output_dir='scrape_outputs'):
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Login credentials
        self.username = username
        self.password = password
        
        # Session to maintain cookies
        self.session = requests.Session()
        
        # Headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def solve_captcha(self, captcha_url):
        """
        Solve captcha using pytesseract OCR
        Note: This might require additional preprocessing 
        depending on the captcha complexity
        """
        try:
            # Download captcha image
            response = self.session.get(captcha_url, headers=self.headers)
            
            # Open image with PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Preprocess image (you might need to adjust these steps)
            # image = image.convert('L')  # Convert to grayscale
            # image = image.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize
            
            # Use Tesseract to read the text
            captcha_text = pytesseract.image_to_string(
                image, 
                config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            ).strip()
            
            return captcha_text
        except Exception as e:
            print(f"Captcha solving error: {e}")
            return None

    def login(self):
        """
        Perform login to NEPSE TMS
        """
        login_url = "https://tms55.nepsetms.com.np/"
        
        try:
            # First, get the login page to fetch any necessary tokens or cookies
            response = self.session.get(login_url, headers=self.headers, verify=False)
            
            # Parse the page to find captcha image
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find captcha image URL (this might need adjustment)
            captcha_img = soup.find('img', class_='captcha-image-dimension')
            if not captcha_img:
                print("Captcha image not found")
                return False
            
            # Solve captcha
            captcha_text = self.solve_captcha(captcha_img['src'])
            if not captcha_text:
                print("Failed to solve captcha")
                return False
            
            # Prepare login payload
            login_payload = {
                'username': self.username,
                'password': self.password,
                'captcha': captcha_text
            }
            
            # Perform login
            login_response = self.session.post(
                login_url, 
                data=login_payload, 
                headers=self.headers,
                verify=False
            )
            
            # Check if login was successful
            if "Dashboard" in login_response.text:
                print("Login successful")
                return True
            else:
                print("Login failed")
                return False
        
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def scrape_market_data(self):
        """
        Scrape market data after login
        """
        try:
            # Navigate to dashboard
            dashboard_url = "https://tms55.nepsetms.com.np/tms/mwDashboard"
            response = self.session.get(dashboard_url, headers=self.headers, verify=False)
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the live data table
            table = soup.find('table', class_='live-data-table')
            if not table:
                print("Market data table not found")
                return None
            
            # Extract headers
            headers = [
                "Symbol", "LTP", "LTV", "Point Change", 
                "% Change", "Open", "High", "Low", 
                "Volume", "Previous Closing"
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
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Save to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f'nepse_tms_market_data_{timestamp}.csv')
            df.to_csv(filename, index=False)
            
            print(f"Market data saved to {filename}")
            return df
        
        except Exception as e:
            print(f"Scraping error: {e}")
            return None

    def run(self):
        """
        Main method to perform login and scrape market data
        """
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Attempt login
        if self.login():
            # Scrape market data
            return self.scrape_market_data()
        else:
            print("Failed to log in")
            return None

# Usage
if __name__ == "__main__":
    scraper = NepseTmsScraper(
        username='2020082983', 
        password='Tulsi@123'
    )
    scraper.run()