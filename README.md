# Daylight Dashboard

[![Tests](https://github.com/JensJBonten/Daylight-Dashboard/actions/workflows/tests.yml/badge.svg)](https://github.com/JensJBonten/Daylight-Dashboard/actions/workflows/tests.yml)

A Python and Streamlit application for tracking sunrise, sunset and daylight length across selected locations in Norway.

The project started as a small pandas exercise using manually recorded Excel data. Over time I expanded it with live data from the MET Norway API, SQLite storage, historical data, automated tests and a deployed Streamlit dashboard.

## Live demo

- [Streamlit Community Cloud](https://daylight-dashboard-jb.streamlit.app/)
- [Databricks Apps](https://daylight-dashboard-jb-7474660523267861.aws.databricksapps.com/)

## Screenshot

![Daylight Dashboard](docs/dashboard-preview.png)

## Features

- Sunrise, sunset and daylight length from the MET Norway Sunrise API
- Support for Oslo, Bergen, Grua and Tromsø
- Historical daylight measurements
- Weekly MET reference curve
- Shared daily check-ins
- Change since the previous check-in
- Change since the previous solstice
- Summer and winter solstice information
- Seasonal themes
- Measurement history
- Responsive layout for desktop, tablet and mobile
- SQLite storage
- Automated tests with pytest and GitHub Actions

## Tech stack

- Python
- Streamlit
- pandas
- Altair
- SQLite
- requests
- pytest
- GitHub Actions
- MET Norway Sunrise API
- Databricks Apps

## Project structure

```text
src/
├── components/
│   ├── sidebar.py
│   ├── season_overview.py
│   ├── metrics.py
│   ├── charts.py
│   └── history.py
│
├── styles/
│   └── dashboard.css
│
├── api_client.py
├── dashboard.py
├── dashboard_styles.py
├── formatting.py
├── historical_seed.py
├── measurement.py
├── measurement_mapper.py
├── measurement_service.py
├── plotting.py
├── reference_data.py
├── seasonal.py
├── sqlite_storage.py
└── time_utils.py
```

The dashboard is split into smaller UI components, while API access, calculations, storage, formatting and plotting are kept in separate modules.

## Data flow

```text
MET Norway API
      ↓
API client
      ↓
Measurement service
      ↓
SQLite
      ↓
Streamlit dashboard
```

Historical measurements and reference data are also loaded into the application so the dashboard can show more than just the latest API result.

## Running locally

Clone the repository:

```bash
git clone https://github.com/JensJBonten/Daylight-Dashboard.git
cd Daylight-Dashboard
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run src/dashboard.py
```

## Testing

Run the tests with:

```bash
python -m pytest
```

The test suite covers API handling, daylight calculations, timezone handling, SQLite storage, historical data, reference data, formatting and seasonal logic.

GitHub Actions runs the tests automatically on pushes and pull requests.

## Deployment

The application is deployed to both Streamlit Community Cloud and Databricks Apps.

## Future improvements

- Persistent production database
- Individual or anonymous check-ins
- More locations
- Further accessibility and mobile improvements