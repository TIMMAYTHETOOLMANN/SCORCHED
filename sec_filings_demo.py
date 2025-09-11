#!/usr/bin/env python3
"""
Nike SEC Filings Downloader - Demo Version

This script demonstrates the SEC filings download functionality with mock data
when the actual Nike investor relations website is not accessible.

For production use, this would download all PDF and XLS documents from Nike's 
SEC filings for the year 2020 from their investor relations page.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# Mock data representing typical SEC filings that would be found
MOCK_NIKE_SEC_FILINGS_2020 = [
    {
        "title": "Nike Inc. Form 10-K Annual Report 2020",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-20-27281&CIK=320187",
        "type": "pdf",
        "date": "2020-07-24",
        "description": "Annual report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934"
    },
    {
        "title": "Nike Inc. Form 10-Q Q1 2020",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-20-44891&CIK=320187",
        "type": "pdf", 
        "date": "2020-09-22",
        "description": "Quarterly report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934"
    },
    {
        "title": "Nike Inc. Form 10-Q Q2 2020",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-20-57392&CIK=320187",
        "type": "pdf",
        "date": "2020-12-18",
        "description": "Quarterly report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934"
    },
    {
        "title": "Nike Inc. Form 10-Q Q3 2020",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-21-11581&CIK=320187",
        "type": "pdf",
        "date": "2020-03-25",
        "description": "Quarterly report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934"
    },
    {
        "title": "Nike Inc. Proxy Statement DEF 14A 2020",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-20-39847&CIK=320187",
        "type": "pdf",
        "date": "2020-08-13",
        "description": "Definitive proxy statement"
    },
    {
        "title": "Nike Inc. Form 8-K Current Report - Q4 2020 Earnings",
        "url": "https://investors.nike.com/secfiling.cfm?filingID=1564590-20-40129&CIK=320187",
        "type": "pdf",
        "date": "2020-06-25",
        "description": "Current report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934"
    },
    {
        "title": "Nike Inc. Financial Data Supplement Q4 2020",
        "url": "https://investors.nike.com/financial-data/q4-2020-supplement.xlsx",
        "type": "xlsx",
        "date": "2020-06-25",
        "description": "Quarterly financial data in Excel format"
    },
    {
        "title": "Nike Inc. Financial Data Supplement Q1 2020",
        "url": "https://investors.nike.com/financial-data/q1-2020-supplement.xlsx",
        "type": "xlsx",
        "date": "2020-09-22",
        "description": "Quarterly financial data in Excel format"
    },
    {
        "title": "Nike Inc. Financial Data Supplement Q2 2020",
        "url": "https://investors.nike.com/financial-data/q2-2020-supplement.xls",
        "type": "xls",
        "date": "2020-12-18",
        "description": "Quarterly financial data in Excel format"
    },
    {
        "title": "Nike Inc. Financial Data Supplement Q3 2020",
        "url": "https://investors.nike.com/financial-data/q3-2020-supplement.xlsx",
        "type": "xlsx",
        "date": "2020-03-25",
        "description": "Quarterly financial data in Excel format"
    }
]


class NikeSECFilingsDemo:
    """Demo version of Nike SEC filings downloader."""
    
    def __init__(self, download_dir="nike_sec_filings_2020"):
        """Initialize the demo downloader."""
        self.download_dir = Path(download_dir)
        self.target_year = 2020
        
        # Create download directory
        self.download_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.download_dir / 'download_demo.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_mock_document(self, filing_info):
        """Create a mock document file for demonstration."""
        # Create filename based on filing info
        safe_title = "".join(c for c in filing_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        extension = f".{filing_info['type']}"
        filename = f"{safe_title}{extension}"
        filepath = self.download_dir / filename
        
        # Create mock file content
        if filing_info['type'] == 'pdf':
            # Create a simple text file representing a PDF
            content = f"""MOCK PDF DOCUMENT - {filing_info['title']}
Date: {filing_info['date']}
Type: {filing_info['description']}

This is a mock representation of the actual SEC filing document.
In a real scenario, this would be the actual PDF file downloaded from:
{filing_info['url']}

--- MOCK CONTENT ---
UNITED STATES
SECURITIES AND EXCHANGE COMMISSION
Washington, D.C. 20549

FORM {filing_info['title'].split(' ')[-2] if 'Form' in filing_info['title'] else '10-K'}

ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the fiscal year ended May 31, 2020

Commission File Number: 001-10635

NIKE, Inc.
(Exact name of registrant as specified in its charter)

[This would contain the full SEC filing content...]
"""
        else:  # Excel files
            content = f"""MOCK EXCEL DOCUMENT - {filing_info['title']}
Date: {filing_info['date']}
Type: {filing_info['description']}

This represents financial data that would typically be in Excel format.
Actual URL: {filing_info['url']}

--- MOCK FINANCIAL DATA ---
Quarter,Revenue,Net Income,Gross Margin
Q4 2020,6313.0,1506.0,44.7%
Q3 2020,6672.3,1232.5,45.2%
Q2 2020,10336.0,1543.0,43.8%
Q1 2020,9366.0,862.0,44.7%

[This would contain detailed financial spreadsheet data...]
"""
        
        # Write the mock file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath, len(content)
    
    def download_all_filings(self):
        """Demo method to create mock SEC filings."""
        self.logger.info("=" * 50)
        self.logger.info("Nike SEC Filings Downloader - DEMO MODE")
        self.logger.info("=" * 50)
        self.logger.info(f"Target Year: {self.target_year}")
        self.logger.info(f"Download Directory: {self.download_dir.absolute()}")
        self.logger.info("")
        self.logger.info("NOTE: This is a demonstration using mock data.")
        self.logger.info("In production, this would download actual SEC filings from:")
        self.logger.info("https://investors.nike.com/investors/news-events-and-reports/default.aspx")
        self.logger.info("")
        
        # Process each mock filing
        successful_downloads = 0
        total_size = 0
        
        for i, filing in enumerate(MOCK_NIKE_SEC_FILINGS_2020, 1):
            self.logger.info(f"Processing {i}/{len(MOCK_NIKE_SEC_FILINGS_2020)}: {filing['title']}")
            
            try:
                filepath, file_size = self.create_mock_document(filing)
                total_size += file_size
                successful_downloads += 1
                
                self.logger.info(f"  Created: {filepath.name} ({file_size} bytes)")
                self.logger.info(f"  Date: {filing['date']}")
                self.logger.info(f"  Type: {filing['type'].upper()}")
                self.logger.info("")
                
                # Simulate download time
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"  Failed to create {filing['title']}: {e}")
        
        # Create summary
        self.logger.info("=" * 50)
        self.logger.info("DOWNLOAD SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total Documents Found: {len(MOCK_NIKE_SEC_FILINGS_2020)}")
        self.logger.info(f"Successfully Downloaded: {successful_downloads}")
        self.logger.info(f"Total Size: {total_size:,} bytes")
        self.logger.info(f"Files saved to: {self.download_dir.absolute()}")
        
        # Create detailed summary files
        self.create_detailed_summary()
        self.create_filing_index()
        
        self.logger.info("")
        self.logger.info("Additional files created:")
        self.logger.info("  - download_summary.txt (detailed summary)")
        self.logger.info("  - filing_index.json (machine-readable index)")
        self.logger.info("  - README.txt (information about files)")
    
    def create_detailed_summary(self):
        """Create a detailed text summary of all filings."""
        summary_path = self.download_dir / "download_summary.txt"
        
        with open(summary_path, 'w') as f:
            f.write("Nike SEC Filings Download Summary - 2020\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target Year: {self.target_year}\n")
            f.write(f"Total Documents: {len(MOCK_NIKE_SEC_FILINGS_2020)}\n")
            f.write(f"Download Directory: {self.download_dir.absolute()}\n\n")
            
            # Group by document type
            pdf_docs = [f for f in MOCK_NIKE_SEC_FILINGS_2020 if f['type'] == 'pdf']
            excel_docs = [f for f in MOCK_NIKE_SEC_FILINGS_2020 if f['type'] in ['xls', 'xlsx']]
            
            f.write(f"PDF Documents ({len(pdf_docs)}):\n")
            f.write("-" * 30 + "\n")
            for doc in pdf_docs:
                f.write(f"• {doc['title']}\n")
                f.write(f"  Date: {doc['date']}\n")
                f.write(f"  Description: {doc['description']}\n\n")
            
            f.write(f"Excel Documents ({len(excel_docs)}):\n")
            f.write("-" * 30 + "\n")
            for doc in excel_docs:
                f.write(f"• {doc['title']}\n")
                f.write(f"  Date: {doc['date']}\n")
                f.write(f"  Description: {doc['description']}\n\n")
            
            f.write("\nNote: These are demonstration files created to show the\n")
            f.write("functionality of the SEC filings downloader. In production,\n")
            f.write("these would be actual SEC filing documents downloaded from\n")
            f.write("Nike's investor relations website.\n")
    
    def create_filing_index(self):
        """Create a JSON index of all filings."""
        index_path = self.download_dir / "filing_index.json"
        
        index_data = {
            "company": "Nike Inc.",
            "year": self.target_year,
            "download_date": datetime.now().isoformat(),
            "total_documents": len(MOCK_NIKE_SEC_FILINGS_2020),
            "source_url": "https://investors.nike.com/investors/news-events-and-reports/default.aspx",
            "filings": MOCK_NIKE_SEC_FILINGS_2020
        }
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2, sort_keys=True)
    
    def create_readme(self):
        """Create a README file explaining the downloaded files."""
        readme_path = self.download_dir / "README.txt"
        
        with open(readme_path, 'w') as f:
            f.write("Nike SEC Filings 2020 - Downloaded Files\n")
            f.write("=" * 45 + "\n\n")
            f.write("This directory contains SEC filing documents for Nike Inc. for the year 2020.\n\n")
            f.write("FILE TYPES:\n")
            f.write("-----------\n")
            f.write("• PDF files: SEC forms (10-K, 10-Q, 8-K, DEF 14A, etc.)\n")
            f.write("• XLS/XLSX files: Financial data supplements\n\n")
            f.write("IMPORTANT DOCUMENTS:\n")
            f.write("-------------------\n")
            f.write("• Form 10-K: Annual report with comprehensive business overview\n")
            f.write("• Form 10-Q: Quarterly reports with financial statements\n")
            f.write("• Form 8-K: Current reports for material events\n")
            f.write("• DEF 14A: Proxy statements for shareholder meetings\n")
            f.write("• Financial Supplements: Detailed quarterly financial data\n\n")
            f.write("INDEX FILES:\n")
            f.write("------------\n")
            f.write("• download_summary.txt: Human-readable summary of all documents\n")
            f.write("• filing_index.json: Machine-readable index with metadata\n")
            f.write("• download_demo.log: Download process log\n\n")
            f.write("For questions about these filings, visit:\n")
            f.write("https://investors.nike.com/\n")


def main():
    """Main function to run the demo."""
    print("\n" + "=" * 60)
    print("Nike SEC Filings Downloader - DEMONSTRATION")
    print("=" * 60)
    print("This demo shows what the SEC filings downloader would do")
    print("when accessing Nike's actual investor relations website.")
    print("=" * 60 + "\n")
    
    demo = NikeSECFilingsDemo()
    demo.download_all_filings()
    demo.create_readme()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("Check the 'nike_sec_filings_2020' directory for:")
    print("• Mock SEC filing documents (PDF and Excel)")
    print("• Summary reports and indexes")
    print("• README with file descriptions")
    print("=" * 60)


if __name__ == "__main__":
    main()