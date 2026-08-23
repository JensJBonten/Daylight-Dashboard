# Daylight Dashboard

[![Tests](https://github.com/JensJBonten/Daylight-Dashboard/actions/workflows/tests.yml/badge.svg)](https://github.com/JensJBonten/Daylight-Dashboard/actions/workflows/tests.yml)

A Python and Streamlit application for tracking and visualizing how sunrise, sunset, and day length change throughout the year in Norway.

The project started as a simple way to make the transition from the dark winter months toward longer and brighter days easier to follow. It has since grown into an application with live API data, historical measurements, reference curves, shared check-ins, automated updates, testing, and public deployment.

## Live Demo

- [Streamlit Community Cloud](https://daylight-dashboard-jb.streamlit.app/)
- [Databricks Apps](https://daylight-dashboard-jb-7474660523267861.aws.databricksapps.com/)

## Features

### Daylight tracking

- Bergen, Grua, Oslo, and Tromsø, with Oslo selected by default
- Sunrise, sunset, and day length from the MET Norway Sunrise API
- Historical daylight measurements
- Weekly MET reference curve
- Shared daily check-ins
- Change since the previous actual check-in
- Total daylight change since the first stored measurement
- Summer and winter solstice information
- Days until the next solstice
- Daylight change since the previous solstice

### Dashboard

- Seasonal themes throughout the year
- Seasonal theme preview
- Responsive desktop and mobile layout
- Graceful handling of unavailable reference data
- Historical state restored automatically on fresh deployments

Check-ins are currently shared application state. The application does not have individual user accounts or per-user histories.

## Architecture

The application separates API access, application logic, storage, historical data handling, and presentation into individual modules.

```text
Streamlit Dashboard
        |
        +--> Measurement Service
        |       |
        |       +--> MET Norway API
        |       |
        |       +--> SQLite
        |
        +--> Historical Seed Data
        |       |
        |       +--> Excel history
        |       +--> Historical API measurements
        |       +--> Historical check-ins
        |
        +--> Weekly MET Reference Data
                |
                +--> Comparison chart
```

New measurements are fetched from MET and stored in SQLite. Historical measurements and check-ins are bundled as seed data so important project history can be restored when a deployment starts with a fresh database.

The application also handles Norwegian summer and winter UTC offsets automatically using `Europe/Oslo`. Service-level errors are converted into readable dashboard messages instead of exposing technical tracebacks.

## Tech Stack

- **Python 3.11+**
- **Streamlit**
- **pandas**
- **Altair**
- **SQLite**
- **requests**
- **pytest**
- **GitHub Actions**
- **MET Norway Sunrise API**
- **Databricks Apps**

Matplotlib is also used by the optional command-line chart export.

## Project Structure

```text
Daylight-Dashboard/
│
├── .github/
│   └── workflows/                 GitHub Actions
│
├── data/                          Historical and reference data
│
├── scripts/
│   ├── export_historical_api_data.py
│   └── generate_reference_data.py
│
├── src/
│   ├── dashboard.py               Streamlit entry point
│   ├── dashboard_components.py    Dashboard components
│   ├── dashboard_styles.py        Dashboard styling
│   ├── measurement_service.py     Measurement workflow
│   ├── sqlite_storage.py          SQLite persistence
│   ├── historical_seed.py         Historical data restoration
│   ├── reference_data.py          Weekly reference data
│   └── seasonal.py                Seasonal and solstice logic
│
├── tests/                          Pytest test suite
├── app.yaml                        Databricks Apps configuration
└── requirements.txt
```

The repository also contains the original command-line workflow and legacy storage functionality used during the earlier stages of the project.

## Running Locally

Clone the repository:

```bash
git clone https://github.com/JensJBonten/Daylight-Dashboard.git
cd Daylight-Dashboard
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run src/dashboard.py
```

## Testing and Automation

Run the test suite with:

```bash
python -m pytest
```

The project currently has **65 passing pytest tests**, covering areas such as:

- MET API handling
- daylight calculations
- SQLite storage and check-ins
- historical data seeding and reconciliation
- reference and solstice logic
- seasonal behavior and formatting

GitHub Actions automatically runs the test suite on pushes and pull requests.

A separate scheduled workflow updates the weekly MET reference dataset and can also be triggered manually.

## Data and Persistence

SQLite is used for runtime storage.

Historical data comes from several sources:

- the original Grua Excel dataset
- historical MET API measurements
- historical shared check-ins
- weekly MET reference data

A local SQLite database inside a hosted application is not treated as permanent production storage. Important historical state is therefore stored as tracked seed data and restored automatically when a fresh database is created.

Existing runtime measurements are preserved during the seeding process.

## Deployment

The application is deployed from the GitHub repository to both Streamlit Community Cloud and Databricks Apps.

`src/dashboard.py` is the Streamlit entry point, while Databricks Apps uses the start command defined in `app.yaml`.

## Future Improvements

- Move runtime state to a persistent production database
- Explore optional individual or anonymous browser-based check-ins
- Add more locations and reference datasets
- Continue improving accessibility and mobile usability