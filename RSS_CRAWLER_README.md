# RSS Document Crawler & Text Extractor

This system is a forensic data ingestion tool designed for comprehensive document collection and text extraction from RSS feeds.

## Overview

The system consists of two main components:
1. **RSS Harvester** (`rss_harvester.py`) - Downloads documents from RSS feeds
2. **Text Extractor** (`text_extractor.py`) - Extracts text content from various file formats

## Directory Structure

```
/
├── scripts/
│   ├── rss_harvester.py     # RSS feed parser and document downloader
│   └── text_extractor.py    # Text extraction from various formats
├── rss_feeds/               # Place RSS XML files here
├── raw_documents/           # Downloaded documents are stored here
├── extracted_text/          # Extracted text files (cleaned)
├── logs/
│   ├── rss_errors.log      # RSS harvesting errors
│   └── parse_errors.log    # Text extraction errors
└── requirements.txt         # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Prepare RSS Feeds
Place your RSS XML files in the `rss_feeds/` directory.

### Step 2: Harvest Documents
```bash
cd scripts
python rss_harvester.py
```

This will:
- Parse all .xml files in `rss_feeds/`
- Extract document URLs from RSS entries
- Download PDFs, Excel files, DOCX files, and HTML files
- Store downloads in `raw_documents/`
- Log any errors to `logs/rss_errors.log`

### Step 3: Extract Text
```bash
cd scripts
python text_extractor.py
```

This will:
- Process all files in `raw_documents/`
- Extract text from:
  - **PDFs**: Using PyMuPDF with page separation
  - **Excel files**: All sheets with tabular formatting
  - **DOCX files**: Text and tables
  - **HTML files**: Clean text extraction
- Save extracted text to `extracted_text/`
- Add metadata headers to each extracted file
- Log any errors to `logs/parse_errors.log`

## Supported File Types

- **PDF** (.pdf) - Full text extraction with page markers
- **Excel** (.xls, .xlsx) - All sheets with data formatting
- **Word Documents** (.docx) - Text and table extraction
- **HTML** (.html, .htm) - Clean text with structure preservation

## Features

- **No missed files**: Processes every entry in RSS feeds
- **Error logging**: Comprehensive error tracking
- **Metadata preservation**: Source file information included
- **Resume capability**: Skips already processed files
- **Local operation**: No cloud dependencies
- **Forensic ready**: Maintains chain of custody information

## Sample RSS Feed Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Document Feed</title>
        <description>RSS feed containing document links</description>
        <item>
            <title>Document Title</title>
            <description>Document description</description>
            <link>https://example.com/document.pdf</link>
        </item>
    </channel>
</rss>
```

## Output

Each extracted text file includes:
- **Metadata header**: Source file, extraction date, file size
- **Structured content**: Organized by sections (PDF pages, Excel sheets, etc.)
- **Original filename preservation**: Maintains document traceability

## Error Handling

- All download failures are logged to `logs/rss_errors.log`
- All text extraction failures are logged to `logs/parse_errors.log`
- System continues processing even if individual files fail
- Detailed error messages for troubleshooting

## Dependencies

- `feedparser` - RSS feed parsing
- `requests` - HTTP downloads with headers
- `PyMuPDF` - PDF text extraction
- `pandas` - Excel file processing
- `openpyxl` - Excel file support
- `python-docx` - Word document processing
- `beautifulsoup4` - HTML parsing and cleaning

## Security Notes

This tool is designed for forensic investigation purposes. It:
- Downloads files from untrusted sources
- Processes various file formats
- Maintains detailed logs for audit trails
- Operates entirely offline after initial download

Use appropriate security measures when processing unknown documents.