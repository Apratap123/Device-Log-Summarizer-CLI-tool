# Device Log Summarizer & Telemetry Analytics CLI

A robust, production-grade Python toolset developed for the **Software Engineering Intern Technical Assessment**. This repository implements data sanitization algorithms, a telemetric log summarizer with threshold filtering, JSON exports, terminal reporting, and automated visualization modules.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Architecture](#repository-architecture)
3. [Section Breakdown](#section-breakdown)
   - [Section 1: Coding Logic & Sanitization](#section-1-coding-logic--sanitization)
   - [Section 2: Core Data Processing CLI](#section-2-core-data-processing-cli)
   - [Section 3: AI Prompting & Visualization](#section-3-ai-prompting--visualization)
4. [Installation & Requirements](#installation--requirements)
5. [Usage Instructions](#usage-instructions)
   - [1. Running Sensor Sanitizer](#1-running-sensor-sanitizer)
   - [2. Running Device Log Summarizer](#2-running-device-log-summarizer)
   - [3. Generating Visualizations](#3-generating-visualizations)
   - [4. Running the Test Suite](#4-running-the-test-suite)
6. [Sample Outputs](#sample-outputs)
7. [Error Handling & Robustness](#error-handling--robustness)

---

## Project Overview

The objective of this assessment is to evaluate clean code structure, defensive programming, edge-case sanitization, data aggregation, and structured AI collaboration. The project comprises three primary modules:
- **`sensor_sanitizer.py`**: A defensive sanitization pipeline that cleans, converts, filters, and clips sensor readings.
- **`log_summarizer.py`**: A CLI application that ingests CSV telemetric logs, aggregates metrics per device, filters out devices with average temperatures exceeding 80.0°C, and outputs clean JSON and terminal summary tables.
- **`chart_generator.py`**: An automated plotting module using `matplotlib` to render publication-ready comparisons with visual error indicators and threshold lines.

---

## Repository Architecture

```text
.
├── device_telemetry.csv         # Sample input CSV containing multi-device telemetry
├── device_summary.json          # Sample output JSON generated from log_summarizer.py
├── device_temperature_chart.png # High-resolution bar chart generated from chart_generator.py
├── sensor_sanitizer.py          # Section 1: Sanitization and normalization module
├── log_summarizer.py            # Section 2: Core CSV ingestion, aggregation, CLI tool
├── chart_generator.py           # Section 3: Data visualization script using matplotlib
├── test_suite.py                # Comprehensive unit tests for all components
├── PROMPT_LOG.md                # Section 3: AI prompting log, bug analysis, and refinement
└── README.md                    # Project documentation and user guide
```

---

## Section Breakdown

### Section 1: Coding Logic & Sanitization
Implemented in `sensor_sanitizer.py`.
- **Type Conversion & Filtering**: Safely attempts float conversion. Rejects non-convertible types, strings, `None`, boolean flags, `NaN`, infinity, and negative numbers (`< 0.0`). Zero (`0.0`) is retained as a valid reading.
- **Clipping**: Any valid reading exceeding `500.0` is capped at `500.0`.
- **Edge-Case Resilience**: Non-list or non-iterable inputs, empty lists, and lists containing exclusively invalid entries return an empty list without throwing unhandled exceptions.

### Section 2: Core Data Processing CLI
Implemented in `log_summarizer.py`.
- **Data Ingestion**: Reads CSV files with BOM handling (`utf-8-sig`) and case-insensitive column header mapping (`device_id`, `status`, `temperature`).
- **Aggregation**:
  - Total records per device.
  - Mean average temperature per device (rounded to 2 decimal places).
  - Count of occurrences where status equals `ERROR`.
- **Filtering**: Automatically excludes devices whose average temperature is strictly greater than `80.0°C`.
- **Export & CLI**:
  - Saves filtered, aggregated results into a formatted JSON file.
  - Renders a formatted ASCII summary table in the terminal.
  - Supports CLI arguments for customizable file paths and temperature thresholds.

### Section 3: AI Prompting & Visualization
Implemented in `chart_generator.py` and documented in `PROMPT_LOG.md`.
- Generates an analytical bar chart comparing average temperatures across active devices.
- Visual enhancements:
  - Error-aware color coding: healthy devices in dark slate blue (`#2b5c8f`), devices with recorded errors in coral red (`#d9534f`).
  - Red dashed threshold reference line at `80.0°C`.
  - Direct value annotations above each bar with temperature and error counts.
  - Gridlines, customized margins, and legend.

---

## Installation & Requirements

### Prerequisites
- Python 3.9+ (Tested on Python 3.12)
- Dependencies: `matplotlib` (standard library handles CSV, JSON, Math, and CLI parsing)

### Setup
```bash
# Clone the repository
git clone <repository_url>
cd <repository_directory>

# Install visualization dependency
pip install matplotlib
```

---

## Usage Instructions

### 1. Running Sensor Sanitizer
To run the sanitization function with built-in test assertions:
```bash
python sensor_sanitizer.py
```

Programmatic usage:
```python
from sensor_sanitizer import clean_sensor_readings

raw_data = ["12.5", None, -5, "sensor_error", 620.4, 0, 499.9, "350.25"]
cleaned_data = clean_sensor_readings(raw_data)
# Output: [12.5, 500.0, 0.0, 499.9, 350.25]
```

### 2. Running Device Log Summarizer
Run with default input (`device_telemetry.csv`) and output (`device_summary.json`):
```bash
python log_summarizer.py
```

Run with custom arguments:
```bash
python log_summarizer.py --input custom_telemetry.csv --output custom_summary.json --threshold 75.0
```

CLI Options:
- `--input`, `-i`: Path to the input CSV file (default: `device_telemetry.csv`).
- `--output`, `-o`: Path to the target output JSON file (default: `device_summary.json`).
- `--threshold`, `-t`: Maximum allowable average temperature in Celsius (default: `80.0`).

### 3. Generating Visualizations
Generate the bar chart comparing average temperatures per device:
```bash
python chart_generator.py --input device_summary.json --output device_temperature_chart.png
```

### 4. Running the Test Suite
Execute the comprehensive unit test suite:
```bash
python test_suite.py
```
Or via Python's unittest runner:
```bash
python -m unittest test_suite.py
```

---

## Sample Outputs

### Terminal Summary Table
```text
==================================================================
                 DEVICE TELEMETRY SUMMARY REPORT                  
                (Devices with Avg Temp <= 80.0 C)                 
==================================================================
+-------------+-----------------+----------------+---------------+
| Device ID   | Total Records   | Avg Temp (C)   | Error Count   |
+-------------+-----------------+----------------+---------------+
| DEV_A       |               5 |          45.12 |             0 |
| DEV_B       |               5 |          71.20 |             2 |
| DEV_D       |               4 |          33.00 |             0 |
| DEV_E       |               4 |          62.00 |             2 |
+-------------+-----------------+----------------+---------------+
```
*(Notice: `DEV_C` with avg 85.5°C and `DEV_F` with avg 93.2°C were correctly filtered out).*

### Sample Output JSON (`device_summary.json`)
```json
[
    {
        "device_id": "DEV_A",
        "total_records": 5,
        "average_temperature": 45.12,
        "error_count": 0
    },
    {
        "device_id": "DEV_B",
        "total_records": 5,
        "average_temperature": 71.2,
        "error_count": 2
    },
    {
        "device_id": "DEV_D",
        "total_records": 4,
        "average_temperature": 33.0,
        "error_count": 0
    },
    {
        "device_id": "DEV_E",
        "total_records": 4,
        "average_temperature": 62.0,
        "error_count": 2
    }
]
```

### Generated Visualization
The chart is saved as high-resolution (300 DPI) at `device_temperature_chart.png`.

---

## Error Handling & Robustness

- **Missing Input Files**: Controlled `FileNotFoundError` handling with user-friendly error messages and clean non-zero exit codes.
- **Malformed Rows**: Rows containing corrupted temperature strings, missing fields, or empty device IDs are skipped without halting pipeline execution.
- **Corrupted / Invalid Headers**: The parser validates the presence of required column headers (`device_id`, `status`, `temperature`) regardless of case or order, raising descriptive validation errors.
- **Boundary Conditions**: Tested against empty CSVs, single-row files, devices with 100% error rates, and floating point boundaries at exactly `80.0°C` and `500.0°C`.
- **Code Standards**: Written strictly following clean code conventions, full type hints, zero extraneous dependencies, and no code comments as per project specifications.
