"""Weather data transformation helpers."""

import logging

import pandas as pd

from app.quality.checks import (
    require_columns,
    validate_no_null_dates,
    validate_no_null_regions,
    validate_temperature_ranges,
)
from app.transformations.utils import normalize_column_name

logger = logging.getLogger(__name__)

REQUIRED_WEATHER_COLUMNS = {
    "location",
    "date",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rainfall_sum",
}
WEATHER_NUMERIC_COLUMNS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rainfall_sum",
]
WEATHER_OUTPUT_COLUMNS = [
    "location",
    "date",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rainfall_sum",
]


def clean_weather_data(weather_data: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw weather data for fact table joins."""
    cleaned_data = weather_data.copy()
    cleaned_data.columns = [normalize_column_name(column) for column in cleaned_data.columns]
    require_columns(cleaned_data, REQUIRED_WEATHER_COLUMNS, "weather data")

    cleaned_data["location"] = cleaned_data["location"].astype("string").str.strip()
    cleaned_data["date"] = pd.to_datetime(cleaned_data["date"], errors="raise").dt.date

    for column in WEATHER_NUMERIC_COLUMNS:
        cleaned_data[column] = pd.to_numeric(cleaned_data[column], errors="raise")

    before_count = len(cleaned_data)
    cleaned_data = cleaned_data.dropna(subset=["location", "date"])
    cleaned_data = cleaned_data[cleaned_data["location"] != ""]
    dropped_count = before_count - len(cleaned_data)
    if dropped_count:
        logger.info("Dropped %s weather rows with missing identity fields", dropped_count)

    validate_no_null_dates(cleaned_data)
    validate_no_null_regions(cleaned_data, region_column="location")
    validate_temperature_ranges(cleaned_data)

    logger.info("Cleaned %s weather rows", len(cleaned_data))
    return cleaned_data.loc[:, WEATHER_OUTPUT_COLUMNS].copy()
