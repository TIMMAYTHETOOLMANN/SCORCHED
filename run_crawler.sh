#!/bin/bash

# RSS Document Crawler - Full Pipeline Execution
# This script runs the complete RSS harvesting and text extraction process

echo "=================================================="
echo "RSS DOCUMENT CRAWLER - FORENSIC DATA PIPELINE"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -d "scripts" ] || [ ! -d "rss_feeds" ]; then
    echo "Error: Please run this script from the main project directory"
    echo "Expected directory structure: scripts/, rss_feeds/, etc."
    exit 1
fi

# Check for RSS files
RSS_COUNT=$(find rss_feeds -name "*.xml" | wc -l)
if [ $RSS_COUNT -eq 0 ]; then
    echo "Warning: No .xml RSS files found in rss_feeds/ directory"
    echo "Please add RSS feed XML files to rss_feeds/ before running"
    echo ""
    echo "Sample RSS feed structure:"
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    echo "<rss version=\"2.0\">"
    echo "    <channel>"
    echo "        <title>Document Feed</title>"
    echo "        <item>"
    echo "            <title>Document Title</title>"
    echo "            <link>https://example.com/document.pdf</link>"
    echo "        </item>"
    echo "    </channel>"
    echo "</rss>"
    exit 1
fi

echo "Found $RSS_COUNT RSS feed(s) to process"
echo ""

# Step 1: Run RSS Harvester
echo "STEP 1: RSS DOCUMENT HARVESTING"
echo "================================"
cd scripts
python3 rss_harvester.py

if [ $? -ne 0 ]; then
    echo "Error: RSS harvesting failed"
    exit 1
fi

echo ""
echo "STEP 2: TEXT EXTRACTION"
echo "======================="
python3 text_extractor.py

if [ $? -ne 0 ]; then
    echo "Error: Text extraction failed"
    exit 1
fi

cd ..

echo ""
echo "=================================================="
echo "PIPELINE COMPLETE - SUMMARY"
echo "=================================================="

# Count downloaded files
DOWNLOAD_COUNT=$(find raw_documents -type f | wc -l)
echo "Downloaded documents: $DOWNLOAD_COUNT"

# Count extracted text files  
EXTRACT_COUNT=$(find extracted_text -name "*.txt" | wc -l)
echo "Extracted text files: $EXTRACT_COUNT"

# Check for errors
if [ -f "logs/rss_errors.log" ]; then
    ERROR_COUNT=$(wc -l < logs/rss_errors.log)
    echo "RSS errors logged: $ERROR_COUNT"
fi

if [ -f "logs/parse_errors.log" ]; then
    PARSE_ERROR_COUNT=$(wc -l < logs/parse_errors.log)
    echo "Parse errors logged: $PARSE_ERROR_COUNT"
fi

echo ""
echo "Results:"
echo "  Raw documents: ./raw_documents/"
echo "  Extracted text: ./extracted_text/"
echo "  Error logs: ./logs/"
echo ""
echo "✅ Forensic data pipeline execution complete!"