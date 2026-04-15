# Agri Data Pipeline Analytics

Initial scaffold for a Python 3.11 project that will ingest, transform, validate, store, and visualize agricultural and weather data.

## Stack

- FastAPI for the API layer
- pandas for data processing
- SQLAlchemy with PostgreSQL for persistence
- Pydantic for validation and configuration
- requests for external API access
- Streamlit for the dashboard

## Project Structure

```text
agri-data-pipeline-analytics/
├── app/
│   ├── config.py
│   ├── db.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services/
│   ├── transformations/
│   └── quality/
├── dashboard/
├── data/
│   ├── raw/
│   └── sample/
├── scripts/
└── tests/
```

## Setup

From the project root, create and activate a Python 3.11 virtual environment:

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

Update `DATABASE_URL` in `.env` for your local PostgreSQL database:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agri_data
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
```

Create the PostgreSQL database if it does not already exist:

```bash
createdb agri_data
```

Initialize the database tables:

```bash
python scripts/init_db.py
```

The initialization script creates the current SQLAlchemy tables:

- `raw_weather`
- `raw_crop_data`
- `fact_crop_performance`

## Run The API

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run The Dashboard

```bash
streamlit run dashboard/app.py
```

The current scaffold intentionally avoids business logic. Pipeline services, transformations, data quality checks, models, and schemas will be added in later iterations.
