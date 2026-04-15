"""Pipeline runner for local data ingestion."""

from datetime import date
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import SessionLocal
from app.logging_config import setup_logging
from app.services.crop_service import ingest_crop_csv
from app.services.weather_service import ingest_weather_data

logger = logging.getLogger(__name__)
CROP_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "crop_data.csv"
WEATHER_START_DATE = date(2025, 1, 15)
WEATHER_END_DATE = date(2025, 3, 15)


def run_pipeline() -> None:
    """Run the local data ingestion pipeline."""
    with SessionLocal() as db:
        crop_inserted_count = ingest_crop_csv(CROP_DATA_PATH, db)
    logger.info("Crop data ingestion completed with %s new rows", crop_inserted_count)

    with SessionLocal() as db:
        weather_inserted_count = ingest_weather_data(
            WEATHER_START_DATE,
            WEATHER_END_DATE,
            db,
        )
    logger.info(
        "Weather data ingestion completed with %s new rows",
        weather_inserted_count,
    )


if __name__ == "__main__":
    setup_logging()
    run_pipeline()
