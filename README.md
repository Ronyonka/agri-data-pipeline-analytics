# Agri Data Pipeline Analytics

A compact data engineering project that ingests Kenyan crop and weather data, validates and transforms it into an analytics-ready PostgreSQL fact table, exposes a FastAPI service, and presents the results in a Streamlit dashboard.

The project is intentionally small, but it follows production-conscious patterns: environment-based configuration, idempotent database loads, structured logging, data quality checks, focused tests, and clear operational entrypoints.

## Architecture Overview

```text
sample crop CSV ─┐
                 ├─ ingestion ─ raw tables ─ transformations + quality checks ─ fact table
Open-Meteo API ──┘                                                            │
                                                                               ├─ FastAPI summary endpoint
                                                                               └─ Streamlit dashboard
```

Pipeline stages:

1. Load sample crop data from `data/sample/crop_data.csv` into `raw_crop_data`.
2. Fetch historical daily weather from Open-Meteo into `raw_weather`.
3. Clean, normalize, validate, and join raw crop and weather rows.
4. Compute `total_yield_estimate`.
5. Load analytics-ready records into `fact_crop_performance`.
6. Serve summary metrics through FastAPI and dashboard views through Streamlit.

## Stack

- Python 3.11
- FastAPI
- Streamlit
- pandas
- SQLAlchemy
- PostgreSQL
- Pydantic
- requests
- pytest

## Project Structure

```text
agri-data-pipeline-analytics/
├── app/
│   ├── config.py
│   ├── db.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   ├── quality/
│   │   └── checks.py
│   ├── services/
│   │   ├── crop_service.py
│   │   ├── pipeline_service.py
│   │   └── weather_service.py
│   └── transformations/
│       ├── crop_transform.py
│       ├── fact_table_transform.py
│       ├── utils.py
│       └── weather_transform.py
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── sample/
│       └── crop_data.csv
├── queries/
│   └── analysis.sql
├── scripts/
│   ├── init_db.py
│   └── run_pipeline.py
└── tests/
```

## Setup

Create and activate a Python 3.11 virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment settings:

```bash
cp .env.example .env
```

Update `.env` for your local PostgreSQL database:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agri_data
OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com/v1
```

Create the database before initializing tables:

```bash
createdb agri_data
```

Initialize the schema:

```bash
python scripts/init_db.py
```

Run the pipeline before opening the dashboard:

```bash
python scripts/run_pipeline.py
```

The pipeline is idempotent. Re-running it skips records already present in the raw and fact tables.

## Run The API

```bash
uvicorn app.main:app --reload
```

Useful endpoints:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/pipeline/run
curl http://127.0.0.1:8000/analytics/summary
```

## Run The Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard reads from `fact_crop_performance` and includes:

- total records, average yield, and total estimated yield KPIs
- region and crop filters
- top-performing regions table
- yield trend over time

## Run Tests

```bash
pytest
```

## Sample Analytics Queries

Reusable SQL examples live in [queries/analysis.sql](queries/analysis.sql).

Examples include:

- total fact rows
- average yield by region
- top regions by total estimated yield
- yield trend over time
- crop performance by crop and region
- weather and yield comparison by region
