# Facility Geographic Mapping - Components & Equipment

This repository contains a mapping solution for visualizing two specific types of finished goods facilities from Nike's manufacturing network.

## Overview

The solution creates an interactive geographical map showing:

1. **Components Facilities** (Purple markers) - FINISHED GOODS - COMPONENTS facilities (54 total)
2. **Equipment Facilities** (Green markers) - FINISHED GOODS facilities that handle Equipment (81 total)

## Quick Start

### Generate the Map

```bash
python3 facility_map_generator.py
```

### View the Map

Open `facility_locations_map.html` in any web browser to view the interactive map.

## Map Features

- **Interactive markers**: Click on any facility marker to see detailed information
- **Layer controls**: Toggle visibility of different facility types using the control panel
- **Distance visualization**: Red lines show the 25 shortest distances between Components and Equipment facilities
- **Responsive design**: Works on desktop and mobile browsers

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

- `facility_map_generator.py` - Main mapping script
- `facility_locations_map.html` - Generated interactive map
- `imap_export.xls` - Source facility data
- `README.md` - This documentation

## Requirements

```bash
pip install pandas xlrd folium geopy numpy
```