"""Crop data ingestion service."""

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import RawCropData

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "region",
    "date",
    "crop_name",
    "yield_kg_per_hectare",
    "area_hectares",
}


def normalize_column_name(column_name: str) -> str:
    """Convert a column name to snake_case."""
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def load_crop_csv(file_path: Path | str) -> pd.DataFrame:
    """Load, normalize, and validate crop CSV data."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Crop data file not found: {path}")

    logger.info("Loading crop data from %s", path)
    crop_data = pd.read_csv(path)
    crop_data.columns = [normalize_column_name(column) for column in crop_data.columns]

    missing_columns = REQUIRED_COLUMNS - set(crop_data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Crop data is missing required columns: {missing}")

    crop_data = crop_data.loc[:, sorted(REQUIRED_COLUMNS)].copy()
    crop_data["date"] = pd.to_datetime(crop_data["date"], errors="raise").dt.date

    numeric_columns = ["yield_kg_per_hectare", "area_hectares"]
    for column in numeric_columns:
        crop_data[column] = pd.to_numeric(crop_data[column], errors="raise")

    if crop_data[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError("Crop data contains null values in required columns")

    logger.info("Loaded %s crop data rows", len(crop_data))
    return crop_data


def insert_raw_crop_data(db: Session, crop_data: pd.DataFrame) -> int:
    """Insert crop records into raw_crop_data, skipping duplicates."""
    if crop_data.empty:
        logger.info("No crop data rows to insert")
        return 0

    records = _dataframe_to_records(crop_data)
    statement = insert(RawCropData).values(records)
    statement = statement.on_conflict_do_nothing(
        constraint="uq_raw_crop_data_region_date_crop_name"
    )

    result = db.execute(statement)
    db.commit()

    inserted_count = result.rowcount or 0
    skipped_count = len(records) - inserted_count
    logger.info(
        "Inserted %s crop rows; skipped %s duplicates",
        inserted_count,
        skipped_count,
    )
    return inserted_count


def ingest_crop_csv(file_path: Path | str, db: Session) -> int:
    """Load a crop CSV file and insert its rows into raw_crop_data."""
    try:
        crop_data = load_crop_csv(file_path)
        return insert_raw_crop_data(db, crop_data)
    except Exception:
        db.rollback()
        logger.exception("Crop data ingestion failed")
        raise


def _dataframe_to_records(crop_data: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert normalized crop data into RawCropData insert records."""
    return [
        {
            "region": row.region,
            "date": row.date,
            "crop_name": row.crop_name,
            "yield_kg_per_hectare": row.yield_kg_per_hectare,
            "area_hectares": row.area_hectares,
        }
        for row in crop_data.itertuples(index=False)
    ]
