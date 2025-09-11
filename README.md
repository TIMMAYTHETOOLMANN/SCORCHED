# SCORCHED - Nike Analysis Tools

This repository contains tools for analyzing Nike's business operations, including facility mapping and SEC filings analysis.

## Tools Available

### 1. Facility Geographic Mapping - Components & Equipment

Interactive geographical mapping solution for visualizing Nike's manufacturing facilities.

The facility mapping solution creates an interactive geographical map showing:

1. **Components Facilities** (Purple markers) - FINISHED GOODS - COMPONENTS facilities (54 total)
2. **Equipment Facilities** (Green markers) - FINISHED GOODS facilities that handle Equipment (81 total)

#### Quick Start - Facility Mapping

### Generate the Map

```bash
python3 facility_map_generator.py
```

#### View the Map

Open `facility_locations_map.html` in any web browser to view the interactive map.

### 2. SEC Filings Downloader

Automated tool to download Nike's SEC filings (PDFs and Excel documents) from their investor relations website.

#### Quick Start - SEC Filings

```bash
# Download actual SEC filings (requires internet access)
python3 sec_filings_downloader.py

# Run demonstration with mock data
python3 sec_filings_demo.py
```

The SEC filings downloader will:
- Scrape Nike's investor relations page at https://investors.nike.com/investors/news-events-and-reports/default.aspx
- Filter for documents from 2020
- Download all PDF and XLS/XLSX files
- Organize files in a structured directory
- Create summary reports and indexes

## Features

### Facility Mapping Features

- **Interactive markers**: Click on any facility marker to see detailed information
- **Layer controls**: Toggle visibility of different facility types using the control panel
- **Distance visualization**: Red lines show the 25 shortest distances between Components and Equipment facilities
- **Responsive design**: Works on desktop and mobile browsers

### SEC Filings Features

- **Automated scraping**: Uses both Selenium and BeautifulSoup for robust website parsing
- **Smart filtering**: Identifies documents from 2020 based on URLs and content
- **File type detection**: Automatically downloads PDF and Excel (XLS/XLSX) documents
- **Organized storage**: Creates structured directory with clear file naming
- **Comprehensive reporting**: Generates summary reports and machine-readable indexes
- **Error handling**: Robust error handling with detailed logging
- **Demo mode**: Includes demonstration with realistic mock data

## Facility Types Mapped

### Components Facilities (Purple markers)
- **Type**: FINISHED GOODS - COMPONENTS
- **Count**: 54 facilities
- **Top Countries**: China (17), Vietnam (15), South Korea (5), Taiwan (5), India (4)

### Equipment Facilities (Green markers)  
- **Type**: FINISHED GOODS facilities with Equipment product type
- **Count**: 79 facilities (out of 81 total - 2 couldn't be geocoded)
- **Top Countries**: China (28), Vietnam (17), Indonesia (8), Taiwan (6), Cambodia (4)

## Facility Information

Each facility marker displays:
- Factory name and type
- Product type
- Location (city, country)
- Total workers
- Percentage of female workers
- Percentage of migrant workers

## Distance Analysis

The map shows relationships between facility types:
- **Shortest distance**: 0.0 km (co-located facilities)
- **Longest distance**: 19,181.9 km
- **Average distance**: 3,514.6 km
- **Median distance**: 2,437.4 km

## Technical Details

- Uses offline geocoding with a comprehensive coordinate database
- Built with Python, Pandas, and Folium
- Responsive HTML output that works in any modern browser
- No internet connection required to view the generated map

## Files

### Facility Mapping Files
- `facility_map_generator.py` - Main mapping script
- `facility_locations_map.html` - Generated interactive map
- `facility_viewer.html` - Alternative facility viewer
- `facility_data.json` - Facility data in JSON format
- `imap_export.xls` - Source facility data

### SEC Filings Files
- `sec_filings_downloader.py` - Production SEC filings downloader
- `sec_filings_demo.py` - Demonstration version with mock data
- `nike_sec_filings_2020/` - Download directory with organized filings

### Documentation
- `README.md` - This documentation

## Requirements

### Facility Mapping Requirements
```bash
pip install pandas xlrd folium geopy numpy
```

### SEC Filings Downloader Requirements
```bash
pip install requests beautifulsoup4 selenium lxml webdriver-manager
```

### Install All Requirements
```bash
pip install pandas xlrd folium geopy numpy requests beautifulsoup4 selenium lxml webdriver-manager
```

## SEC Filings Output

When you run the SEC filings downloader, it creates:

```
nike_sec_filings_2020/
├── Nike_Inc_Form_10-K_Annual_Report_2020.pdf
├── Nike_Inc_Form_10-Q_Q1_2020.pdf
├── Nike_Inc_Form_10-Q_Q2_2020.pdf
├── Nike_Inc_Form_10-Q_Q3_2020.pdf
├── Nike_Inc_Proxy_Statement_DEF_14A_2020.pdf
├── Nike_Inc_Form_8-K_Current_Report_-_Q4_2020_Earning.pdf
├── Nike_Inc_Financial_Data_Supplement_Q1_2020.xlsx
├── Nike_Inc_Financial_Data_Supplement_Q2_2020.xls
├── Nike_Inc_Financial_Data_Supplement_Q3_2020.xlsx
├── Nike_Inc_Financial_Data_Supplement_Q4_2020.xlsx
├── download_summary.txt
├── filing_index.json
├── README.txt
└── download.log
```

The downloader provides:
- **PDF Documents**: SEC forms (10-K annual reports, 10-Q quarterly reports, 8-K current reports, DEF 14A proxy statements)
- **Excel Documents**: Financial data supplements with detailed quarterly data
- **Summary Reports**: Human-readable summaries and machine-readable indexes
- **Documentation**: README explaining all downloaded files