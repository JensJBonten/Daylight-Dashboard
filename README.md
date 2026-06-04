# Daylight Dashboard

A Python project for importing, cleaning, storing, and visualizing daylight measurements.

The project started as a learning exercise around pandas, file input, and basic reporting. It now uses a small data pipeline that reads daylight data from an Excel workbook, converts it into typed measurement objects, stores the history in SQLite, and presents the result in a Streamlit dashboard.

## Dashboard Preview

![Dashboard top page preview](/screenshots/Dashboard1.png)
![Dashboard bottom page preview](/screenshots/Dashboard2.png)


## Features

- Imports daylight measurements from an Excel file in `data/` which contains data ive tracked over a period of time.
- Normalizes Norwegian column names into consistent internal field names
- Converts Excel date and time values with pandas
- Maps cleaned rows into `DaylightMeasurement` objects
- Stores measurement history in SQLite
- Shows the latest measurement in a Streamlit dashboard
- Displays day length and daily increase charts
- Includes a history table and location filter
- Keeps JSON storage as legacy/bootstrap storage for simple object persistence
- Includes tests for formatting, mapping, JSON storage, and SQLite storage

## Tech Stack

- Python
- pandas
- SQLite
- Streamlit
- Matplotlib
- pytest

## Data Flow

```text
Excel file -> pandas DataFrame -> DaylightMeasurement objects -> SQLite database -> Streamlit dashboard
```

## Project Structure

```text
src/
  main.py                 CLI entry point for loading, previewing, saving, and plotting data
  data_loader.py          Reads Excel data and normalizes columns and time values
  measurement.py          DaylightMeasurement data model
  measurement_mapper.py   Converts DataFrame rows into measurement objects
  sqlite_storage.py       Main storage layer for dashboard data
  storage.py              Legacy/bootstrap JSON storage
  dashboard.py            Streamlit dashboard
  reporting.py            Terminal summary and preview formatting
  plotting.py             PNG chart export

tests/
  test_measurement_mapper.py
  test_measurement_service.py
  test_api_client.py
  test_formatting.py
  test_sqlite_storage.py
  test_storage.py

data/
  Dagens lengde (2).xlsx  Source Excel workbook
  daylight.db            SQLite database created by the app
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

Run the CLI summary and preview:

```bash
python -m src.main
```

Save imported measurements to SQLite for the dashboard:

```bash
python -m src.main --save-sqlite --location Grua
```

Start the Streamlit dashboard:

```bash
streamlit run src/dashboard.py
```

Export a PNG chart:

```bash
python -m src.main --plot output/daylight.png
```

Run the test suite:

```bash
python -m pytest
```

## Current Status

The project has a working Excel-to-SQLite pipeline, a Streamlit dashboard, chart export, location filtering, and a small test suite. SQLite is the main storage used by the dashboard.

JSON storage still exists in `src/storage.py`, but it is kept as legacy/bootstrap storage rather than the primary application storage.

A MET Sunrise API client has been added as the next step toward replacing manual Excel input with API-based daylight measurements.

This project is still ongoing while I implement new solutions and continue learning, so some parts are intentionally simple and easy to follow.


## Next Steps

- Add tests for Excel column normalization and time conversion edge cases
- Add clearer validation messages for unexpected workbook formats
- Keep refining naming, comments, and module boundaries as the project grows
