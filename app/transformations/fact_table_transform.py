"""Build and persist crop performance fact table data."""

import logging
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import FactCropPerformance, RawCropData, RawWeather
from app.transformations.crop_transform import clean_crop_data
from app.transformations.weather_transform import clean_weather_data

logger = logging.getLogger(__name__)

FACT_COLUMNS = [
    "region",
    "date",
    "crop_name",
    "yield_kg_per_hectare",
    "area_hectares",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rainfall_sum",
    "total_yield_estimate",
]


def build_crop_performance_fact(
    crop_data: pd.DataFrame,
    weather_data: pd.DataFrame,
) -> pd.DataFrame:
    """Join crop and weather data into an analytics-ready fact DataFrame."""
    cleaned_crop_data = clean_crop_data(crop_data)
    cleaned_weather_data = clean_weather_data(weather_data)

    if cleaned_crop_data.empty:
        logger.info("No crop rows available for fact table transformation")
        return pd.DataFrame(columns=FACT_COLUMNS)

    fact_data = cleaned_crop_data.merge(
        cleaned_weather_data,
        how="left",
        left_on=["region", "date"],
        right_on=["location", "date"],
    )
    fact_data["total_yield_estimate"] = (
        fact_data["yield_kg_per_hectare"] * fact_data["area_hectares"]
    )

    logger.info("Built %s crop performance fact rows", len(fact_data))
    return fact_data.loc[:, FACT_COLUMNS].copy()


def load_raw_crop_data(db: Session) -> pd.DataFrame:
    """Load raw crop rows from the database."""
    rows = db.execute(select(RawCropData)).scalars().all()
    data = [
        {
            "region": row.region,
            "date": row.date,
            "crop_name": row.crop_name,
            "yield_kg_per_hectare": row.yield_kg_per_hectare,
            "area_hectares": row.area_hectares,
        }
        for row in rows
    ]
    logger.info("Loaded %s raw crop rows", len(data))
    return pd.DataFrame(data)


def load_raw_weather_data(db: Session) -> pd.DataFrame:
    """Load raw weather rows from the database."""
    rows = db.execute(select(RawWeather)).scalars().all()
    data = [
        {
            "location": row.location,
            "date": row.date,
            "temperature_2m_max": row.temperature_2m_max,
            "temperature_2m_min": row.temperature_2m_min,
            "precipitation_sum": row.precipitation_sum,
            "rainfall_sum": row.rainfall_sum,
        }
        for row in rows
    ]
    logger.info("Loaded %s raw weather rows", len(data))
    return pd.DataFrame(data)


def insert_fact_crop_performance(db: Session, fact_data: pd.DataFrame) -> int:
    """Insert crop performance facts, skipping duplicates."""
    if fact_data.empty:
        logger.info("No crop performance fact rows to insert")
        return 0

    records = _dataframe_to_records(fact_data)
    statement = insert(FactCropPerformance).values(records)
    statement = statement.on_conflict_do_nothing(
        constraint="uq_fact_crop_performance_region_date_crop_name"
    )

    try:
        result = db.execute(statement)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Crop performance fact insertion failed")
        raise

    inserted_count = result.rowcount or 0
    skipped_count = len(records) - inserted_count
    logger.info(
        "Inserted %s fact rows; skipped %s duplicates",
        inserted_count,
        skipped_count,
    )
    return inserted_count


def transform_fact_crop_performance(db: Session) -> int:
    """Build and insert crop performance fact rows from raw tables."""
    crop_data = load_raw_crop_data(db)
    if crop_data.empty:
        logger.info("No raw crop data found; skipping fact transformation")
        return 0

    weather_data = load_raw_weather_data(db)
    fact_data = build_crop_performance_fact(crop_data, weather_data)
    return insert_fact_crop_performance(db, fact_data)


def _dataframe_to_records(fact_data: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert fact data into FactCropPerformance insert records."""
    records = fact_data.where(pd.notnull(fact_data), None).to_dict("records")
    return [
        {
            "region": record["region"],
            "date": record["date"],
            "crop_name": record["crop_name"],
            "yield_kg_per_hectare": record["yield_kg_per_hectare"],
            "area_hectares": record["area_hectares"],
            "temperature_2m_max": record["temperature_2m_max"],
            "temperature_2m_min": record["temperature_2m_min"],
            "precipitation_sum": record["precipitation_sum"],
            "rainfall_sum": record["rainfall_sum"],
            "total_yield_estimate": record["total_yield_estimate"],
        }
        for record in records
    ]
