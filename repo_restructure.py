"""
NIKE REPO RESTRUCTURE - REPRIORITIZATION SCRIPT
Reorganizes repo to centralize prosecution engine and isolate facility mapping.
Run once from the root of the repository.
"""

import os
import shutil

# === Constants ===
MAPPING_FILES = [
    "facility_map_generator.py",
    "facility_locations_map.html",
    "facility_viewer.html",
    "facility_data.json",
    "imap_export.xls"
]
MAPPING_MODULE_DIR = "modules/facility_mapping"
MAIN_README = "README.md"
LOG_FILE = "repo_restructure.log"

# === Utility Logging ===
def log(msg):
    with open(LOG_FILE, "a") as logf:
        logf.write(f"[RESTRUCTURE] {msg}\n")
    print(f"✅ {msg}")

# === Create module directory for facility mapping ===
os.makedirs(MAPPING_MODULE_DIR, exist_ok=True)
log(f"Created directory: {MAPPING_MODULE_DIR}")

# === Move mapping files ===
for filename in MAPPING_FILES:
    if os.path.exists(filename):
        dest_path = os.path.join(MAPPING_MODULE_DIR, filename)
        shutil.move(filename, dest_path)
        log(f"Moved {filename} → {dest_path}")
    else:
        log(f"Skipped (not found): {filename}")

# === Update README Priorities ===
# === Insert new mission banner at top ===
prosecution_focus = """# SCORCHED - Nike Data Prosecution Engine

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
"""

new_readme_lines = [prosecution_focus]

with open(MAIN_README, "w") as f:
    f.writelines(new_readme_lines)

log("README updated with mission reprioritization")

# === Set Triangulator as default entry point ===
default_entry = "main.py"
with open(default_entry, "w") as f:
    f.write("""from scripts.triangulator_auto_executor import main

if __name__ == "__main__":
    main()
""")
log(f"Set main.py with triangulator as default entry point")

log("Nike repo structure reprioritized. Facility map sandboxed. SEC prosecution engine now mission control.")