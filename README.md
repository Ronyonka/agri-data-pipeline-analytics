# Agri Data Pipeline Analytics

A Python 3.11 data engineering project that ingests crop and weather data, stores raw records in PostgreSQL, applies data quality checks and transformations, publishes a FastAPI service, and visualizes analytics in Streamlit.

## Architecture

The project follows a compact analytics pipeline:

1. Crop data ingestion loads sample Kenyan crop observations from CSV into `raw_crop_data`.
2. Weather ingestion fetches historical daily weather from the Open-Meteo Archive API into `raw_weather`.
3. Transformation logic cleans both datasets, joins crop rows to weather rows by region/location and date, and calculates `total_yield_estimate`.
4. Data quality checks validate required fields, non-negative crop metrics, reasonable weather temperatures, and duplicate fact keys.
5. The fact table loader writes analytics-ready rows to `fact_crop_performance`.
6. FastAPI exposes health, pipeline execution, and summary endpoints.
7. Streamlit reads the fact table directly from PostgreSQL and renders dashboard metrics.

## Stack

- FastAPI for API endpoints
- Streamlit for the dashboard
- pandas for ingestion and transformations
- SQLAlchemy for database access
- PostgreSQL for persistence
- Pydantic for settings and API response models
- requests for Open-Meteo API calls
- pytest for transformation and quality checks

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
│       └── weather_transform.py
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── sample/
│       └── crop_data.csv
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

Create the PostgreSQL database if needed:

```bash
createdb agri_data
```

Initialize tables:

```bash
python scripts/init_db.py
```

## Run The Pipeline

```bash
python scripts/run_pipeline.py
```

The pipeline is duplicate-safe. Re-running it skips records already present in the raw and fact tables.

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

- KPI cards for total records, average yield, and total estimated yield
- Region and crop filters
- Top-performing regions table
- Yield trend line chart

## Sample Analytics Queries

Total fact rows:

```sql
SELECT COUNT(*) AS total_rows
FROM fact_crop_performance;
```

Average yield by region:

```sql
SELECT
    region,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare
FROM fact_crop_performance
GROUP BY region
ORDER BY region;
```

Top regions by total estimated yield:

```sql
SELECT
    region,
    SUM(total_yield_estimate) AS total_estimated_yield
FROM fact_crop_performance
GROUP BY region
ORDER BY total_estimated_yield DESC
LIMIT 5;
```

Yield trend over time:

```sql
SELECT
    date,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare
FROM fact_crop_performance
GROUP BY date
ORDER BY date;
```

## Why This Demonstrates Data Engineering Skills

This project shows practical data engineering fundamentals in a small, readable codebase:

- API ingestion from Open-Meteo without hardcoded secrets
- CSV ingestion with pandas
- PostgreSQL raw and fact table modeling
- idempotent loads with unique constraints and conflict handling
- modular transformations into an analytics-ready fact table
- reusable data quality validation
- automated pytest coverage for transforms and checks
- operational entrypoints through a CLI pipeline and FastAPI
- a Streamlit dashboard for business-facing analytics
