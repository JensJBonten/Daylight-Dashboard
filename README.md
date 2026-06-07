# Daylight Dashboard

A Python dashboard for tracking and visualizing daylight development over time.

The project started as a learning exercise around pandas, file input, and basic reporting. It has since grown into a small data pipeline that imports historical daylight measurements from Excel, converts them into typed measurement objects, stores the history in SQLite, and presents the result in a Streamlit dashboard.

The dashboard can fetch today's sunrise and sunset for a selected location using the MET Sunrise API, calculate day length and daylight increase, store the measurement in SQLite, and refresh the visual history.

## Dashboard Preview

![Dashboard top page preview](/screenshots/Dashboard1.png)
![Dashboard bottom page preview](/screenshots/Dashboard2.png)

## Features

* Imports historical daylight measurements from an Excel file in `data/`
* Normalizes Norwegian column names into consistent internal field names
* Converts Excel date and time values with pandas
* Maps cleaned rows into `DaylightMeasurement` objects
* Stores measurement history in SQLite
* Fetches sunrise and sunset data from MET Sunrise API
* Calculates day length from API data
* Calculates daily and total daylight increase from saved history
* Shows latest measurement in a Streamlit dashboard
* Displays day length and daily increase charts
* Includes a history table and location filter
* Supports API updates for selected locations such as Grua, Oslo, Tromsø and Bergen
* Keeps JSON storage as an optional legacy storage path
* Includes tests for formatting, mapping, API parsing, service logic, duration calculations, JSON storage, and SQLite storage

## Tech Stack

* Python
* pandas
* SQLite
* Streamlit
* Matplotlib
* pytest
* MET Sunrise API

## Data Flow

Historical import:

```text
Excel file -> pandas DataFrame -> DaylightMeasurement objects -> SQLite database -> Streamlit dashboard
```

API update:

```text
MET Sunrise API -> JSON response -> DaylightMeasurement object -> SQLite database -> Streamlit dashboard
```

## Project Structure

```text
src/
  main.py                 CLI entry point for loading, previewing, saving, and plotting data
  data_loader.py          Reads Excel data and normalizes columns and time values
  measurement.py          DaylightMeasurement data model
  measurement_mapper.py   Converts DataFrame rows into measurement objects
  api_client.py           Fetches and parses MET Sunrise API data
  measurement_service.py  Connects API fetching, measurement creation, history calculation, and storage
  sqlite_storage.py       Main SQLite storage layer
  storage.py              Optional legacy JSON storage
  formatting.py           Display formatting helpers
  time_utils.py           Time calculation helpers
  dashboard.py            Streamlit dashboard
  reporting.py            Terminal summary and preview output
  plotting.py             PNG chart export

tests/
  test_api_client.py
  test_formatting.py
  test_measurement_mapper.py
  test_measurement_service.py
  test_sqlite_storage.py
  test_storage.py
  test_time_utils.py

data/
  Dagens lengde (2).xlsx  Historical source Excel workbook
```

## Setup

Python 3.10 or newer is recommended.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI summary and preview:

```bash
python -m src.main
```

Save imported Excel measurements to SQLite:

```bash
python -m src.main --save-sqlite --location Grua
```

Start the Streamlit dashboard:

```bash
streamlit run src/dashboard.py
```

The dashboard reads from SQLite. Import the historical Excel data with `--save-sqlite` before starting it for the first time.

Export a PNG chart:

```bash
python -m src.main --plot output/daylight.png
```

Run the test suite:

```bash
python -m pytest
```

## Current Status

The project currently has a working Excel-to-SQLite pipeline, a Streamlit dashboard, location filtering, MET Sunrise API updates, chart visualization, and automated tests for the core data flow.

SQLite is the main storage used by the dashboard. JSON storage still exists in `src/storage.py` as an optional legacy path, but it is not used to initialize SQLite automatically.

This is a working v1.0 candidate and an ongoing portfolio project. I am continuing to improve API error handling, dashboard structure, tests, and overall code quality.

## Next Steps

* Improve error handling for failed API requests
* Add clearer validation messages for unexpected workbook formats
* Add tests for Excel column normalization and time conversion edge cases
* Improve dashboard layout and visual structure
* Keep refining naming, comments, and module boundaries as the project grows
