# Facility Geographical Bubble Map

This repository contains tools to generate geographical bubble maps from facility data in the Excel file `imap_export.xls`.

## Overview

The solution creates an interactive geographical bubble map that visualizes two types of facilities:
- **Finished Goods facilities** (482 facilities) - shown in blue
- **Finished Goods - Components facilities** (54 facilities) - shown in purple

## Features

- Interactive map with clickable facility markers
- Different colors for each facility type
- Facility information popups showing:
  - Factory name and type
  - Location (city, country)
  - Total workers
  - Percentage of female workers
  - Percentage of migrant workers
- Distance visualization showing the 30 shortest distances between different facility types
- Layer controls to toggle visibility of different elements
- Comprehensive statistical report

## Files

- `imap_export.xls` - Original Excel data file containing facility information
- `generate_facility_map_offline.py` - Main script to generate the map (offline version using predefined coordinates)
- `generate_facility_map.py` - Online version that uses geocoding APIs (requires internet)
- `facility_locations_map.html` - Generated interactive map (open in web browser)

## Results Summary

### Facility Distribution
- **Finished Goods facilities**: 455 successfully mapped (out of 482)
  - Top countries: Vietnam (120), China (103), Indonesia (42), USA (29), Thailand (24)
- **Components facilities**: 54 successfully mapped (out of 54)
  - Top countries: China (17), Vietnam (15), South Korea (5), Taiwan (5), India (4)

### Distance Analysis
- **Shortest distance**: 0.0 km (co-located facilities)
- **Longest distance**: 19,393.6 km
- **Average distance**: 4,639.3 km
- **Median distance**: 2,633.4 km

## Usage

1. Run the mapping script:
   ```bash
   python3 generate_facility_map_offline.py
   ```

2. Open the generated HTML file in a web browser:
   ```bash
   open facility_locations_map.html
   ```

## Map Features

The interactive map includes:
- **Blue markers**: Finished Goods facilities
- **Purple markers**: Components facilities  
- **Red lines**: 30 shortest distances between facility types
- **Layer control**: Toggle different elements on/off
- **Popup information**: Click markers for detailed facility info
- **Legend**: Explains marker colors and line meanings

## Technical Details

The offline version uses a comprehensive database of predefined coordinates for countries and major cities to avoid dependency on external geocoding APIs. This ensures the solution works in environments without internet access.

The distance calculations use geodesic distance (great circle distance) to accurately measure distances between facilities across the globe.