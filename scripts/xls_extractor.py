#!/usr/bin/env python3
"""
Nike XLS Extractor

This script extracts and processes Excel/XLS files from Nike SEC filings.
It parses financial data supplements and other Excel-based filing documents
to extract structured data for analysis.

Features:
- Extracts data from XLS/XLSX files for specified year
- Processes financial data supplements
- Generates structured output for downstream analysis
- Handles various Excel file formats and structures

Usage:
    python scripts/xls_extractor.py --year YYYY
"""

import argparse
import os
import sys
import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class NikeXLSExtractor:
    """
    Nike XLS/XLSX File Extractor
    
    Extracts and processes Excel files from SEC filings.
    """
    
    def __init__(self, year: str, base_dir: str = None):
        """Initialize the XLS extractor."""
        self.year = year
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filings_dir = os.path.join(self.base_dir, 'filings', str(year))
        self.output_dir = os.path.join(self.base_dir, 'extracted_data', str(year))
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.output_dir, 'xls_extraction.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize data containers
        self.extracted_data = {}
        self.file_metadata = {}
        
    def find_xls_files(self) -> List[str]:
        """Find all XLS/XLSX files in the filings directory."""
        self.logger.info(f"Searching for XLS/XLSX files in: {self.filings_dir}")
        
        if not os.path.exists(self.filings_dir):
            self.logger.error(f"Filings directory not found: {self.filings_dir}")
            return []
            
        xls_files = []
        for file in os.listdir(self.filings_dir):
            if file.lower().endswith(('.xls', '.xlsx')):
                file_path = os.path.join(self.filings_dir, file)
                xls_files.append(file_path)
                self.logger.info(f"Found XLS file: {file}")
                
        self.logger.info(f"Total XLS/XLSX files found: {len(xls_files)}")
        return xls_files
    
    def extract_file_metadata(self, file_path: str) -> Dict:
        """Extract metadata from XLS file."""
        file_name = os.path.basename(file_path)
        
        metadata = {
            'filename': file_name,
            'filepath': file_path,
            'filesize': os.path.getsize(file_path),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'year': self.year,
            'file_type': 'financial_supplement' if 'supplement' in file_name.lower() else 'unknown',
            'quarter': None
        }
        
        # Extract quarter information from filename
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            if q in file_name:
                metadata['quarter'] = q
                break
                
        return metadata
    
    def extract_xls_data(self, file_path: str) -> Dict:
        """Extract data from a single XLS/XLSX file."""
        self.logger.info(f"Extracting data from: {os.path.basename(file_path)}")
        
        try:
            # Get file metadata
            metadata = self.extract_file_metadata(file_path)
            
            # Read Excel file - try different sheet approaches
            excel_data = {}
            
            # First, get all sheet names
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            self.logger.info(f"Found {len(sheet_names)} sheets: {sheet_names}")
            
            # Extract data from each sheet
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Clean and process the data
                    excel_data[sheet_name] = {
                        'shape': df.shape,
                        'columns': df.columns.tolist(),
                        'data_summary': {
                            'row_count': len(df),
                            'column_count': len(df.columns),
                            'non_null_cells': df.count().sum(),
                            'null_cells': df.isnull().sum().sum()
                        }
                    }
                    
                    # For financial supplements, extract key metrics
                    if metadata['file_type'] == 'financial_supplement':
                        excel_data[sheet_name]['financial_metrics'] = self.extract_financial_metrics(df)
                    
                    # Store first few rows as sample
                    excel_data[sheet_name]['sample_data'] = df.head(5).fillna('').to_dict('records')
                    
                except Exception as e:
                    self.logger.warning(f"Error reading sheet '{sheet_name}': {e}")
                    excel_data[sheet_name] = {'error': str(e)}
            
            return {
                'metadata': metadata,
                'sheets': excel_data,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {file_path}: {e}")
            return {
                'metadata': self.extract_file_metadata(file_path),
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def extract_financial_metrics(self, df: pd.DataFrame) -> Dict:
        """Extract key financial metrics from financial supplement data."""
        metrics = {
            'revenue_indicators': [],
            'expense_indicators': [],
            'numeric_columns': [],
            'potential_kpis': []
        }
        
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        metrics['numeric_columns'] = numeric_cols
        
        # Look for revenue-related terms
        revenue_terms = ['revenue', 'sales', 'income', 'gross']
        for col in df.columns:
            for term in revenue_terms:
                if term.lower() in col.lower():
                    metrics['revenue_indicators'].append(col)
                    break
        
        # Look for expense-related terms
        expense_terms = ['expense', 'cost', 'expenditure', 'operating']
        for col in df.columns:
            for term in expense_terms:
                if term.lower() in col.lower():
                    metrics['expense_indicators'].append(col)
                    break
        
        # Calculate basic statistics for numeric columns
        if numeric_cols:
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                try:
                    stats = {
                        'column': col,
                        'sum': float(df[col].sum()) if not df[col].isnull().all() else None,
                        'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                        'min': float(df[col].min()) if not df[col].isnull().all() else None,
                        'max': float(df[col].max()) if not df[col].isnull().all() else None
                    }
                    metrics['potential_kpis'].append(stats)
                except:
                    continue
        
        return metrics
    
    def process_all_xls_files(self) -> bool:
        """Process all XLS files for the specified year."""
        self.logger.info(f"=== Starting XLS extraction for year {self.year} ===")
        
        xls_files = self.find_xls_files()
        
        if not xls_files:
            self.logger.warning("No XLS/XLSX files found to process")
            return False
        
        # Process each file
        for file_path in xls_files:
            file_name = os.path.basename(file_path)
            self.logger.info(f"Processing: {file_name}")
            
            extracted = self.extract_xls_data(file_path)
            self.extracted_data[file_name] = extracted
            
            # Save individual file results
            output_file = os.path.join(self.output_dir, f"{file_name}_extracted.json")
            with open(output_file, 'w') as f:
                json.dump(extracted, f, indent=2, default=str)
            
            self.logger.info(f"Saved extraction results to: {output_file}")
        
        # Save combined results
        self.save_extraction_summary()
        
        self.logger.info(f"=== XLS extraction complete for year {self.year} ===")
        return True
    
    def save_extraction_summary(self) -> str:
        """Save extraction summary and metadata."""
        summary_file = os.path.join(self.output_dir, 'xls_extraction_summary.json')
        
        summary = {
            'year': self.year,
            'extraction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_files_processed': len(self.extracted_data),
                'filings_directory': self.filings_dir,
                'output_directory': self.output_dir
            },
            'file_summary': {},
            'aggregate_stats': {
                'total_sheets': 0,
                'total_rows': 0,
                'total_columns': 0,
                'files_with_errors': 0
            }
        }
        
        # Generate file summary and aggregate stats
        for file_name, data in self.extracted_data.items():
            file_summary = {
                'status': 'error' if 'error' in data else 'success',
                'metadata': data.get('metadata', {}),
                'sheet_count': len(data.get('sheets', {})) if 'sheets' in data else 0
            }
            
            if 'sheets' in data:
                total_rows = sum(sheet.get('data_summary', {}).get('row_count', 0) 
                               for sheet in data['sheets'].values() 
                               if isinstance(sheet, dict) and 'data_summary' in sheet)
                file_summary['total_rows'] = total_rows
                summary['aggregate_stats']['total_rows'] += total_rows
                summary['aggregate_stats']['total_sheets'] += file_summary['sheet_count']
            
            if 'error' in data:
                summary['aggregate_stats']['files_with_errors'] += 1
            
            summary['file_summary'][file_name] = file_summary
        
        # Save summary
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Extraction summary saved to: {summary_file}")
        return summary_file


def main():
    """Main execution function for the XLS extractor."""
    parser = argparse.ArgumentParser(description='Nike XLS Extractor')
    parser.add_argument('--year', required=True, help='Year to process (e.g., 2019)')
    parser.add_argument('--base-dir', help='Base directory path (optional)')
    
    args = parser.parse_args()
    
    print(f"Nike XLS Extractor - Year {args.year}")
    print("=" * 50)
    
    # Initialize extractor
    extractor = NikeXLSExtractor(args.year, args.base_dir)
    
    # Process all XLS files
    success = extractor.process_all_xls_files()
    
    if success:
        print(f"\n✅ XLS extraction completed successfully for year {args.year}!")
        print(f"📁 Results saved to: {extractor.output_dir}")
        
        # Display summary
        if extractor.extracted_data:
            print(f"\n📊 Summary:")
            print(f"  • Files processed: {len(extractor.extracted_data)}")
            
            total_sheets = sum(len(data.get('sheets', {})) for data in extractor.extracted_data.values() if 'sheets' in data)
            print(f"  • Total sheets extracted: {total_sheets}")
            
            errors = sum(1 for data in extractor.extracted_data.values() if 'error' in data)
            if errors > 0:
                print(f"  • Files with errors: {errors}")
        
        return 0
    else:
        print(f"\n❌ XLS extraction failed for year {args.year}!")
        return 1


if __name__ == "__main__":
    sys.exit(main())