#!/usr/bin/env python3
"""
Nike PDF Text Extractor

This script extracts and processes text content from Nike SEC filing PDF documents.
It parses annual reports, quarterly reports, proxy statements, and other PDF-based
filing documents to extract structured text data for analysis.

Features:
- Extracts text from PDF files for specified year
- Processes SEC forms (10-K, 10-Q, 8-K, DEF 14A, etc.)
- Generates structured text output for downstream analysis
- Handles various PDF formats and structures
- Extracts metadata and document structure

Usage:
    python scripts/pdf_extractor.py --year YYYY
"""

import argparse
import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# PDF processing libraries (fallback gracefully if not available)
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pdfplumber import PDF
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

class NikePDFExtractor:
    """
    Nike PDF Text Extractor
    
    Extracts and processes text content from SEC filing PDF documents.
    """
    
    def __init__(self, year: str, base_dir: str = None):
        """Initialize the PDF extractor."""
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
                logging.FileHandler(os.path.join(self.output_dir, 'pdf_extraction.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize data containers
        self.extracted_data = {}
        self.file_metadata = {}
        
        # Check PDF library availability
        if not PDF_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            self.logger.warning("No PDF libraries available. Will extract basic metadata only.")
    
    def find_pdf_files(self) -> List[str]:
        """Find all PDF files in the filings directory."""
        self.logger.info(f"Searching for PDF files in: {self.filings_dir}")
        
        if not os.path.exists(self.filings_dir):
            self.logger.error(f"Filings directory not found: {self.filings_dir}")
            return []
            
        pdf_files = []
        for file in os.listdir(self.filings_dir):
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(self.filings_dir, file)
                pdf_files.append(file_path)
                self.logger.info(f"Found PDF file: {file}")
                
        self.logger.info(f"Total PDF files found: {len(pdf_files)}")
        return pdf_files
    
    def extract_file_metadata(self, file_path: str) -> Dict:
        """Extract metadata from PDF file."""
        file_name = os.path.basename(file_path)
        
        metadata = {
            'filename': file_name,
            'filepath': file_path,
            'filesize': os.path.getsize(file_path),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'year': self.year,
            'form_type': self.identify_form_type(file_name),
            'quarter': None,
            'document_type': self.identify_document_type(file_name)
        }
        
        # Extract quarter information from filename
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            if q in file_name:
                metadata['quarter'] = q
                break
                
        return metadata
    
    def identify_form_type(self, filename: str) -> str:
        """Identify SEC form type from filename."""
        filename_lower = filename.lower()
        
        if '10-k' in filename_lower:
            return '10-K'
        elif '10-q' in filename_lower:
            return '10-Q'
        elif '8-k' in filename_lower:
            return '8-K'
        elif 'def_14a' in filename_lower or 'proxy' in filename_lower:
            return 'DEF 14A'
        else:
            return 'Unknown'
    
    def identify_document_type(self, filename: str) -> str:
        """Identify document type from filename."""
        filename_lower = filename.lower()
        
        if 'annual' in filename_lower:
            return 'Annual Report'
        elif 'quarterly' in filename_lower or 'q1' in filename_lower or 'q2' in filename_lower or 'q3' in filename_lower or 'q4' in filename_lower:
            return 'Quarterly Report'
        elif 'proxy' in filename_lower:
            return 'Proxy Statement'
        elif 'current' in filename_lower or 'earning' in filename_lower:
            return 'Current Report'
        else:
            return 'SEC Filing'
    
    def extract_text_basic(self, file_path: str) -> str:
        """Basic text extraction using simple file reading (fallback method)."""
        try:
            # Try to read as text (will work for some PDFs)
            with open(file_path, 'rb') as f:
                content = f.read()
                # Simple text extraction - look for readable text
                text_content = ''
                for byte in content:
                    if 32 <= byte <= 126:  # Printable ASCII
                        text_content += chr(byte)
                    elif byte in [10, 13]:  # Line endings
                        text_content += '\n'
                
                # Clean up the text
                lines = text_content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if len(line) > 3:  # Only keep lines with meaningful content
                        cleaned_lines.append(line)
                
                return '\n'.join(cleaned_lines[:100])  # Return first 100 meaningful lines
        except Exception as e:
            self.logger.warning(f"Basic text extraction failed: {e}")
            return f"Text extraction failed: {e}"
    
    def extract_text_pypdf2(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using PyPDF2 library."""
        try:
            text_content = ""
            pdf_info = {}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get PDF metadata
                pdf_info = {
                    'page_count': len(pdf_reader.pages),
                    'pdf_version': getattr(pdf_reader, 'pdf_header', 'Unknown'),
                    'encrypted': pdf_reader.is_encrypted
                }
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text
                    except Exception as e:
                        self.logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue
            
            return text_content, pdf_info
            
        except Exception as e:
            self.logger.warning(f"PyPDF2 extraction failed: {e}")
            return f"PyPDF2 extraction failed: {e}", {}
    
    def analyze_text_content(self, text: str, metadata: Dict) -> Dict:
        """Analyze extracted text content for key information."""
        analysis = {
            'text_statistics': {
                'total_characters': len(text),
                'total_words': len(text.split()),
                'total_lines': len(text.split('\n')),
                'average_words_per_line': 0
            },
            'key_sections': [],
            'financial_terms': [],
            'business_terms': [],
            'risk_indicators': []
        }
        
        # Calculate average words per line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            total_words = sum(len(line.split()) for line in lines)
            analysis['text_statistics']['average_words_per_line'] = round(total_words / len(lines), 2)
        
        # Look for key sections (case insensitive)
        text_lower = text.lower()
        section_indicators = [
            'business overview', 'financial highlights', 'risk factors',
            'management discussion', 'financial statements', 'notes to',
            'consolidated statements', 'income statement', 'balance sheet',
            'cash flow', 'stockholders equity', 'executive compensation'
        ]
        
        for indicator in section_indicators:
            if indicator in text_lower:
                analysis['key_sections'].append(indicator)
        
        # Look for financial terms
        financial_terms = [
            'revenue', 'net income', 'gross profit', 'operating income',
            'earnings per share', 'dividend', 'cash flow', 'assets',
            'liabilities', 'equity', 'debt', 'interest expense'
        ]
        
        for term in financial_terms:
            if term in text_lower:
                # Count occurrences
                count = text_lower.count(term)
                analysis['financial_terms'].append({'term': term, 'occurrences': count})
        
        # Look for business terms
        business_terms = [
            'nike', 'jordan', 'converse', 'footwear', 'apparel',
            'wholesale', 'retail', 'direct-to-consumer', 'digital',
            'international', 'north america', 'innovation'
        ]
        
        for term in business_terms:
            if term in text_lower:
                count = text_lower.count(term)
                analysis['business_terms'].append({'term': term, 'occurrences': count})
        
        # Look for risk indicators
        risk_terms = [
            'risk', 'uncertainty', 'may adversely', 'could adversely',
            'litigation', 'regulatory', 'competition', 'economic conditions',
            'supply chain', 'currency', 'cybersecurity'
        ]
        
        for term in risk_terms:
            if term in text_lower:
                count = text_lower.count(term)
                analysis['risk_indicators'].append({'term': term, 'occurrences': count})
        
        return analysis
    
    def extract_pdf_data(self, file_path: str) -> Dict:
        """Extract data from a single PDF file."""
        self.logger.info(f"Extracting data from: {os.path.basename(file_path)}")
        
        try:
            # Get file metadata
            metadata = self.extract_file_metadata(file_path)
            
            # Extract text content
            text_content = ""
            pdf_info = {}
            extraction_method = "none"
            
            if PDF_AVAILABLE:
                try:
                    text_content, pdf_info = self.extract_text_pypdf2(file_path)
                    extraction_method = "PyPDF2"
                except Exception as e:
                    self.logger.warning(f"PyPDF2 failed, trying basic extraction: {e}")
                    text_content = self.extract_text_basic(file_path)
                    extraction_method = "basic"
            else:
                text_content = self.extract_text_basic(file_path)
                extraction_method = "basic"
            
            # Analyze text content
            text_analysis = self.analyze_text_content(text_content, metadata)
            
            # Create sample text (first 1000 characters)
            sample_text = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            
            return {
                'metadata': metadata,
                'pdf_info': pdf_info,
                'text_analysis': text_analysis,
                'sample_text': sample_text,
                'extraction_method': extraction_method,
                'extraction_timestamp': datetime.now().isoformat(),
                'full_text_available': len(text_content) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {file_path}: {e}")
            return {
                'metadata': self.extract_file_metadata(file_path),
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def process_all_pdf_files(self) -> bool:
        """Process all PDF files for the specified year."""
        self.logger.info(f"=== Starting PDF extraction for year {self.year} ===")
        
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            self.logger.warning("No PDF files found to process")
            return False
        
        # Process each file
        for file_path in pdf_files:
            file_name = os.path.basename(file_path)
            self.logger.info(f"Processing: {file_name}")
            
            extracted = self.extract_pdf_data(file_path)
            self.extracted_data[file_name] = extracted
            
            # Save individual file results
            output_file = os.path.join(self.output_dir, f"{file_name}_extracted.json")
            with open(output_file, 'w') as f:
                json.dump(extracted, f, indent=2, default=str)
            
            self.logger.info(f"Saved extraction results to: {output_file}")
        
        # Save combined results
        self.save_extraction_summary()
        
        self.logger.info(f"=== PDF extraction complete for year {self.year} ===")
        return True
    
    def save_extraction_summary(self) -> str:
        """Save extraction summary and metadata."""
        summary_file = os.path.join(self.output_dir, 'pdf_extraction_summary.json')
        
        summary = {
            'year': self.year,
            'extraction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_files_processed': len(self.extracted_data),
                'filings_directory': self.filings_dir,
                'output_directory': self.output_dir,
                'pdf_libraries_available': {
                    'PyPDF2': PDF_AVAILABLE,
                    'pdfplumber': PDFPLUMBER_AVAILABLE
                }
            },
            'file_summary': {},
            'aggregate_stats': {
                'total_characters': 0,
                'total_words': 0,
                'files_with_errors': 0,
                'form_types': {},
                'document_types': {}
            }
        }
        
        # Generate file summary and aggregate stats
        for file_name, data in self.extracted_data.items():
            file_summary = {
                'status': 'error' if 'error' in data else 'success',
                'metadata': data.get('metadata', {}),
                'extraction_method': data.get('extraction_method', 'unknown'),
                'text_available': data.get('full_text_available', False)
            }
            
            if 'text_analysis' in data:
                stats = data['text_analysis']['text_statistics']
                file_summary.update(stats)
                summary['aggregate_stats']['total_characters'] += stats.get('total_characters', 0)
                summary['aggregate_stats']['total_words'] += stats.get('total_words', 0)
            
            if 'error' in data:
                summary['aggregate_stats']['files_with_errors'] += 1
            
            # Count form types and document types
            form_type = data.get('metadata', {}).get('form_type', 'Unknown')
            doc_type = data.get('metadata', {}).get('document_type', 'Unknown')
            
            summary['aggregate_stats']['form_types'][form_type] = summary['aggregate_stats']['form_types'].get(form_type, 0) + 1
            summary['aggregate_stats']['document_types'][doc_type] = summary['aggregate_stats']['document_types'].get(doc_type, 0) + 1
            
            summary['file_summary'][file_name] = file_summary
        
        # Save summary
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Extraction summary saved to: {summary_file}")
        return summary_file


def main():
    """Main execution function for the PDF extractor."""
    parser = argparse.ArgumentParser(description='Nike PDF Text Extractor')
    parser.add_argument('--year', required=True, help='Year to process (e.g., 2019)')
    parser.add_argument('--base-dir', help='Base directory path (optional)')
    
    args = parser.parse_args()
    
    print(f"Nike PDF Text Extractor - Year {args.year}")
    print("=" * 50)
    
    # Initialize extractor
    extractor = NikePDFExtractor(args.year, args.base_dir)
    
    # Process all PDF files
    success = extractor.process_all_pdf_files()
    
    if success:
        print(f"\n✅ PDF extraction completed successfully for year {args.year}!")
        print(f"📁 Results saved to: {extractor.output_dir}")
        
        # Display summary
        if extractor.extracted_data:
            print(f"\n📊 Summary:")
            print(f"  • Files processed: {len(extractor.extracted_data)}")
            
            total_chars = sum(data.get('text_analysis', {}).get('text_statistics', {}).get('total_characters', 0) 
                            for data in extractor.extracted_data.values())
            total_words = sum(data.get('text_analysis', {}).get('text_statistics', {}).get('total_words', 0) 
                            for data in extractor.extracted_data.values())
            
            print(f"  • Total characters extracted: {total_chars:,}")
            print(f"  • Total words extracted: {total_words:,}")
            
            errors = sum(1 for data in extractor.extracted_data.values() if 'error' in data)
            if errors > 0:
                print(f"  • Files with errors: {errors}")
        
        return 0
    else:
        print(f"\n❌ PDF extraction failed for year {args.year}!")
        return 1


if __name__ == "__main__":
    sys.exit(main())