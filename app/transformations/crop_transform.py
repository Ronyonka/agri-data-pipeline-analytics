"""Crop data transformation helpers."""

import logging
import re

import pandas as pd

from app.quality.checks import (
    require_columns,
    validate_no_null_dates,
    validate_no_null_regions,
    validate_non_negative_values,
)

logger = logging.getLogger(__name__)

REQUIRED_CROP_COLUMNS = {
    "region",
    "date",
    "crop_name",
    "yield_kg_per_hectare",
    "area_hectares",
}
CROP_NUMERIC_COLUMNS = ["yield_kg_per_hectare", "area_hectares"]
CROP_OUTPUT_COLUMNS = [
    "region",
    "date",
    "crop_name",
    "yield_kg_per_hectare",
    "area_hectares",
]


def clean_crop_data(crop_data: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw crop data for fact table joins."""
    cleaned_data = crop_data.copy()
    cleaned_data.columns = [normalize_column_name(column) for column in cleaned_data.columns]
    require_columns(cleaned_data, REQUIRED_CROP_COLUMNS, "crop data")

    cleaned_data["region"] = cleaned_data["region"].astype("string").str.strip()
    cleaned_data["crop_name"] = cleaned_data["crop_name"].astype("string").str.strip()
    cleaned_data["date"] = pd.to_datetime(cleaned_data["date"], errors="raise").dt.date

    for column in CROP_NUMERIC_COLUMNS:
        cleaned_data[column] = pd.to_numeric(cleaned_data[column], errors="raise")

    before_count = len(cleaned_data)
    cleaned_data = cleaned_data.dropna(subset=["region", "date", "crop_name"])
    cleaned_data = cleaned_data[
        (cleaned_data["region"] != "") & (cleaned_data["crop_name"] != "")
    ]
    dropped_count = before_count - len(cleaned_data)
    if dropped_count:
        logger.info("Dropped %s crop rows with missing identity fields", dropped_count)

    validate_no_null_dates(cleaned_data)
    validate_no_null_regions(cleaned_data)
    validate_non_negative_values(cleaned_data, CROP_NUMERIC_COLUMNS)

    logger.info("Cleaned %s crop rows", len(cleaned_data))
    return cleaned_data.loc[:, CROP_OUTPUT_COLUMNS].copy()


def normalize_column_name(column_name: str) -> str:
    """Convert a column name to snake_case."""
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")
