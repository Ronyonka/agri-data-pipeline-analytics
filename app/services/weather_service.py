"""Open-Meteo weather ingestion service."""

from datetime import date
import logging
import re
from typing import Any

import pandas as pd
import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import RawWeather

logger = logging.getLogger(__name__)

KENYAN_LOCATIONS: dict[str, tuple[float, float]] = {
    "Nairobi": (-1.2864, 36.8172),
    "Nakuru": (-0.3031, 36.0800),
    "Eldoret": (0.5143, 35.2698),
    "Nyeri": (-0.4201, 36.9476),
    "Meru": (0.0463, 37.6559),
    "Kisumu": (-0.0917, 34.7680),
}

DAILY_WEATHER_FIELDS = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
)
REQUIRED_COLUMNS = {
    "location",
    "date",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rainfall_sum",
}
REQUEST_TIMEOUT_SECONDS = 30


def fetch_daily_weather(
    location: str,
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    """Fetch daily weather data for one location from Open-Meteo."""
    settings = get_settings()
    url = build_archive_url(settings.open_meteo_base_url)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_WEATHER_FIELDS),
        "timezone": "Africa/Nairobi",
    }

    logger.info("Fetching weather data for %s", location)
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def weather_response_to_dataframe(
    location: str,
    response_data: dict[str, Any],
) -> pd.DataFrame:
    """Transform an Open-Meteo daily response into normalized weather rows."""
    daily_data = response_data.get("daily")
    if not isinstance(daily_data, dict):
        raise ValueError(f"Weather response for {location} is missing daily data")

    expected_fields = {"time", *DAILY_WEATHER_FIELDS}
    missing_fields = expected_fields - set(daily_data)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Weather response for {location} is missing fields: {missing}")

    field_lengths = {field: len(daily_data[field]) for field in expected_fields}
    if len(set(field_lengths.values())) != 1:
        raise ValueError(f"Weather response for {location} has mismatched daily lengths")

    weather_data = pd.DataFrame(daily_data)
    weather_data.columns = [normalize_column_name(column) for column in weather_data.columns]
    weather_data = weather_data.rename(columns={"time": "date", "rain_sum": "rainfall_sum"})
    weather_data["location"] = location
    weather_data["date"] = pd.to_datetime(weather_data["date"], errors="raise").dt.date

    numeric_columns = [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "rainfall_sum",
    ]
    for column in numeric_columns:
        weather_data[column] = pd.to_numeric(weather_data[column], errors="raise")

    if weather_data[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError(f"Weather data for {location} contains null required values")

    return weather_data.loc[:, sorted(REQUIRED_COLUMNS)].copy()


def insert_raw_weather_data(db: Session, weather_data: pd.DataFrame) -> int:
    """Insert weather records into raw_weather, skipping duplicates."""
    if weather_data.empty:
        logger.info("No weather data rows to insert")
        return 0

    records = _dataframe_to_records(weather_data)
    statement = insert(RawWeather).values(records)
    statement = statement.on_conflict_do_nothing(
        constraint="uq_raw_weather_location_date"
    )

    result = db.execute(statement)
    db.commit()

    inserted_count = result.rowcount or 0
    skipped_count = len(records) - inserted_count
    logger.info(
        "Inserted %s weather rows; skipped %s duplicates",
        inserted_count,
        skipped_count,
    )
    return inserted_count


def ingest_weather_data(
    start_date: date,
    end_date: date,
    db: Session,
    locations: dict[str, tuple[float, float]] | None = None,
) -> int:
    """Fetch and insert weather data for configured Kenyan locations."""
    selected_locations = locations or KENYAN_LOCATIONS
    try:
        weather_frames = []
        for location, coordinates in selected_locations.items():
            latitude, longitude = coordinates
            response_data = fetch_daily_weather(
                location,
                latitude,
                longitude,
                start_date,
                end_date,
            )
            weather_frames.append(weather_response_to_dataframe(location, response_data))

        weather_data = pd.concat(weather_frames, ignore_index=True)
        return insert_raw_weather_data(db, weather_data)
    except Exception:
        db.rollback()
        logger.exception("Weather data ingestion failed")
        raise


def normalize_column_name(column_name: str) -> str:
    """Convert a column name to snake_case."""
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def build_archive_url(base_url: str) -> str:
    """Build the Open-Meteo archive URL from configured base URL."""
    normalized_url = base_url.rstrip("/")
    normalized_url = normalized_url.replace(
        "https://api.open-meteo.com",
        "https://archive-api.open-meteo.com",
    )
    if normalized_url.endswith("/archive"):
        return normalized_url
    return f"{normalized_url}/archive"


def _dataframe_to_records(weather_data: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert normalized weather data into RawWeather insert records."""
    return [
        {
            "location": row.location,
            "date": row.date,
            "temperature_2m_max": row.temperature_2m_max,
            "temperature_2m_min": row.temperature_2m_min,
            "precipitation_sum": row.precipitation_sum,
            "rainfall_sum": row.rainfall_sum,
        }
        for row in weather_data.itertuples(index=False)
    ]
