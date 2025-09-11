# SCORCHED - Nike Data Prosecution Engine

This repository contains a suite of automated intelligence modules designed to extract, index, and triangulate Nike's business data — including SEC filings, ESG claims, financial statements, facility metadata, and potential regulatory violations.

## 1. Core Module - SEC Filings Intelligence & Prosecution System

- Full-text and XLS extraction
- Keyword Sentinel scanning
- Triangulation engine
- JSON metadata with traceable hashes
- Timeline-ready and cross-year synthesis

## 2. Facility Mapping Module (Submodule)

The facility mapping module has been moved to `modules/facility_mapping/` and provides:
- Interactive geographical mapping solution for visualizing Nike's manufacturing facilities
- Components and Equipment facility visualization
- Geographic analysis and distance calculations

To use the facility mapping module:
```bash
python modules/facility_mapping/facility_map_generator.py
```

Open `modules/facility_mapping/facility_locations_map.html` in any web browser to view the interactive map.

## Requirements

```bash
pip install -r requirements.txt
```

## Quick Start

Run the main prosecution engine:
```bash
python main.py
```

Or run the triangulator directly:
```bash
python scripts/triangulator_auto_executor.py
```
