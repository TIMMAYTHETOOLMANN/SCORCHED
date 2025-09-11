#!/usr/bin/env python3
"""
Nike SEC Filings Downloader

This script downloads all PDF and XLS documents from Nike's SEC filings 
for the year 2020 from their investor relations page.

URL: https://investors.nike.com/investors/news-events-and-reports/default.aspx
"""

import os
import re
import sys
import time
import logging
import argparse
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class NikeSECFilingsDownloader:
    """Downloader for Nike SEC filings from their investor relations page."""
    
    def __init__(self, download_dir="nike_sec_filings_2020"):
        """
        Initialize the downloader.
        
        Args:
            download_dir (str): Directory to save downloaded files
        """
        self.base_url = "https://investors.nike.com"
        self.main_url = "https://investors.nike.com/investors/news-events-and-reports/default.aspx"
        self.download_dir = Path(download_dir)
        self.target_year = 2020
        
        # Create download directory
        self.download_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.download_dir / 'download.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup session for downloads
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def setup_driver(self):
        """Setup Chrome WebDriver for web scraping."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            self.logger.info("Trying with requests and BeautifulSoup fallback...")
            return None
    
    def extract_year_from_url_or_text(self, url, text=""):
        """Extract year from URL or associated text."""
        # Look for 4-digit year patterns
        year_pattern = r'\b(20\d{2})\b'
        
        # Check URL first
        url_match = re.search(year_pattern, url)
        if url_match:
            return int(url_match.group(1))
        
        # Check text content
        text_match = re.search(year_pattern, text)
        if text_match:
            return int(text_match.group(1))
        
        return None
    
    def is_target_file(self, url, text=""):
        """Check if file is a PDF or XLS document from 2020."""
        file_extensions = ['.pdf', '.xls', '.xlsx']
        
        # Check if it's the right file type
        has_extension = any(url.lower().endswith(ext) for ext in file_extensions)
        if not has_extension:
            return False
        
        # Check if it's from 2020
        year = self.extract_year_from_url_or_text(url, text)
        return year == self.target_year
    
    def download_file(self, url, filename=None):
        """Download a file from the given URL."""
        try:
            # Ensure we have a full URL
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            # Get filename from URL if not provided
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # Generate filename from URL components
                    filename = f"document_{int(time.time())}.pdf"
            
            filepath = self.download_dir / filename
            
            # Skip if file already exists
            if filepath.exists():
                self.logger.info(f"File already exists: {filename}")
                return True
            
            self.logger.info(f"Downloading: {url}")
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Write file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"Downloaded: {filename} ({os.path.getsize(filepath)} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def scrape_with_requests(self):
        """Fallback method using requests and BeautifulSoup."""
        self.logger.info("Using requests/BeautifulSoup method...")
        
        try:
            response = self.session.get(self.main_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links to documents
            links = soup.find_all('a', href=True)
            pdf_xls_links = []
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check if this is a target file
                if self.is_target_file(href, text):
                    full_url = urljoin(self.base_url, href)
                    pdf_xls_links.append({
                        'url': full_url,
                        'text': text,
                        'href': href
                    })
            
            return pdf_xls_links
            
        except Exception as e:
            self.logger.error(f"Failed to scrape with requests: {e}")
            return []
    
    def scrape_with_selenium(self, driver):
        """Scrape using Selenium for dynamic content."""
        self.logger.info("Using Selenium method...")
        
        try:
            driver.get(self.main_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for SEC filings section or similar
            sec_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'SEC') or contains(text(), 'filing') or contains(text(), '2020')]")
            
            if sec_elements:
                self.logger.info(f"Found {len(sec_elements)} elements mentioning SEC/filings/2020")
            
            # Get all links
            links = driver.find_elements(By.TAG_NAME, "a")
            pdf_xls_links = []
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and self.is_target_file(href, text):
                        pdf_xls_links.append({
                            'url': href,
                            'text': text,
                            'href': href
                        })
                except Exception:
                    continue
            
            return pdf_xls_links
            
        except Exception as e:
            self.logger.error(f"Failed to scrape with Selenium: {e}")
            return []
    
    def find_sec_filings_links(self):
        """Find all SEC filing links for 2020."""
        all_links = []
        
        # Try Selenium first
        driver = self.setup_driver()
        if driver:
            try:
                selenium_links = self.scrape_with_selenium(driver)
                all_links.extend(selenium_links)
            finally:
                driver.quit()
        
        # Try requests fallback
        if not all_links:
            requests_links = self.scrape_with_requests()
            all_links.extend(requests_links)
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in all_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def download_all_filings(self):
        """Main method to download all SEC filings."""
        self.logger.info(f"Starting Nike SEC filings download for {self.target_year}")
        self.logger.info(f"Download directory: {self.download_dir.absolute()}")
        
        # Find all filing links
        filing_links = self.find_sec_filings_links()
        
        if not filing_links:
            self.logger.warning("No SEC filing links found for 2020. This might be due to:")
            self.logger.warning("1. Website structure changes")
            self.logger.warning("2. Access restrictions")
            self.logger.warning("3. Documents not available on this page")
            
            # Try to create some example URLs based on common patterns
            common_sec_patterns = [
                f"{self.base_url}/investors/financial-reports/annual-reports/default.aspx",
                f"{self.base_url}/investors/financial-reports/quarterly-reports/default.aspx",
                f"{self.base_url}/investors/sec-filings/default.aspx",
            ]
            
            self.logger.info("Trying common SEC filing page patterns...")
            for pattern_url in common_sec_patterns:
                try:
                    response = self.session.get(pattern_url, timeout=15)
                    if response.status_code == 200:
                        self.logger.info(f"Found accessible page: {pattern_url}")
                        # You could extend this to scrape these pages too
                except:
                    continue
            
            return
        
        self.logger.info(f"Found {len(filing_links)} potential SEC filing documents")
        
        # Download each file
        successful_downloads = 0
        for i, link in enumerate(filing_links, 1):
            self.logger.info(f"Processing {i}/{len(filing_links)}: {link['text']}")
            
            # Generate a meaningful filename
            safe_text = re.sub(r'[^\w\s-]', '', link['text'])[:50]
            url_path = urlparse(link['url']).path
            original_filename = os.path.basename(url_path)
            
            if original_filename and '.' in original_filename:
                filename = original_filename
            else:
                # Create filename from text and URL
                extension = '.pdf'
                if any(ext in link['url'].lower() for ext in ['.xls', '.xlsx']):
                    extension = '.xlsx'
                filename = f"{safe_text.replace(' ', '_').lower()}{extension}"
            
            if self.download_file(link['url'], filename):
                successful_downloads += 1
            
            # Be nice to the server
            time.sleep(1)
        
        self.logger.info(f"Download complete! {successful_downloads}/{len(filing_links)} files downloaded")
        self.logger.info(f"Files saved to: {self.download_dir.absolute()}")
        
        # Create a summary report
        self.create_summary_report(filing_links, successful_downloads)
    
    def create_summary_report(self, filing_links, successful_downloads):
        """Create a summary report of the download operation."""
        report_path = self.download_dir / "download_summary.txt"
        
        with open(report_path, 'w') as f:
            f.write("Nike SEC Filings Download Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Target Year: {self.target_year}\n")
            f.write(f"Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files Found: {len(filing_links)}\n")
            f.write(f"Successfully Downloaded: {successful_downloads}\n")
            f.write(f"Download Directory: {self.download_dir.absolute()}\n\n")
            
            if filing_links:
                f.write("Files Found:\n")
                f.write("-" * 20 + "\n")
                for i, link in enumerate(filing_links, 1):
                    f.write(f"{i}. {link['text']}\n")
                    f.write(f"   URL: {link['url']}\n\n")
            else:
                f.write("No files found. Please check:\n")
                f.write("1. Website accessibility\n")
                f.write("2. Target year availability\n")
                f.write("3. Website structure changes\n")
        
        self.logger.info(f"Summary report created: {report_path}")


def main():
    """Main function to run the SEC filings downloader."""
    print("Nike SEC Filings Downloader")
    print("=" * 30)

    parser = argparse.ArgumentParser(description="Download Nike SEC filings for a range of years.")
    parser.add_argument('--start_year', type=int, default=2020, help='Start year (inclusive)')
    parser.add_argument('--end_year', type=int, default=2020, help='End year (inclusive)')
    args = parser.parse_args()

    for year in range(args.start_year, args.end_year + 1):
        print(f"\nProcessing year: {year}")
        download_dir = f"nike_sec_filings_{year}"
        downloader = NikeSECFilingsDownloader(download_dir=download_dir)
        downloader.target_year = year
        downloader.download_all_filings()


if __name__ == "__main__":
    main()