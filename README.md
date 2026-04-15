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

Update `DATABASE_URL` in `.env` for your local PostgreSQL database.

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

## Initialize The Database

```bash
python scripts/init_db.py
```

The current scaffold intentionally avoids business logic. Pipeline services, transformations, data quality checks, models, and schemas will be added in later iterations.
