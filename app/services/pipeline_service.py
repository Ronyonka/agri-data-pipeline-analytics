"""Pipeline orchestration and analytics summary service."""

from datetime import date
import logging
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import FactCropPerformance
from app.services.crop_service import ingest_crop_csv
from app.services.weather_service import ingest_weather_data
from app.transformations.fact_table_transform import transform_fact_crop_performance

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CROP_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "crop_data.csv"
WEATHER_START_DATE = date(2025, 1, 15)
WEATHER_END_DATE = date(2025, 3, 15)


class PipelineResult(BaseModel):
    """Result returned after a pipeline run."""

    status: str
    crop_rows_inserted: int
    weather_rows_inserted: int
    fact_rows_inserted: int


class AverageYieldByRegion(BaseModel):
    """Average crop yield for a region."""

    region: str
    average_yield_kg_per_hectare: float | None


class TopRegionByYield(BaseModel):
    """Total estimated yield for a region."""

    region: str
    total_yield_estimate: float | None


class AnalyticsSummary(BaseModel):
    """Simple analytics summary for the fact table."""

    total_rows: int
    average_yield_by_region: list[AverageYieldByRegion]
    top_regions_by_total_estimated_yield: list[TopRegionByYield]


def run_pipeline(crop_data_path: Path | str = DEFAULT_CROP_DATA_PATH) -> PipelineResult:
    """Run crop ingestion, weather ingestion, validation, and fact loading."""
    logger.info("Starting pipeline")

    try:
        logger.info("Pipeline stage started: crop ingestion")
        with SessionLocal() as db:
            crop_rows_inserted = ingest_crop_csv(crop_data_path, db)
        logger.info(
            "Pipeline stage completed: crop ingestion inserted %s rows",
            crop_rows_inserted,
        )

        logger.info("Pipeline stage started: weather ingestion")
        with SessionLocal() as db:
            weather_rows_inserted = ingest_weather_data(
                WEATHER_START_DATE,
                WEATHER_END_DATE,
                db,
            )
        logger.info(
            "Pipeline stage completed: weather ingestion inserted %s rows",
            weather_rows_inserted,
        )

        logger.info("Pipeline stage started: transformations and quality validation")
        logger.info("Pipeline stage started: fact table loading")
        with SessionLocal() as db:
            fact_rows_inserted = transform_fact_crop_performance(db)
        logger.info(
            "Pipeline stage completed: fact table loading inserted %s rows",
            fact_rows_inserted,
        )

    except Exception:
        logger.exception("Pipeline failed")
        raise

    logger.info("Pipeline completed successfully")
    return PipelineResult(
        status="completed",
        crop_rows_inserted=crop_rows_inserted,
        weather_rows_inserted=weather_rows_inserted,
        fact_rows_inserted=fact_rows_inserted,
    )


def get_analytics_summary(db: Session) -> AnalyticsSummary:
    """Return simple aggregate metrics from crop performance facts."""
    total_rows = db.scalar(select(func.count(FactCropPerformance.id))) or 0

    average_yield_rows = db.execute(
        select(
            FactCropPerformance.region,
            func.avg(FactCropPerformance.yield_kg_per_hectare),
        )
        .group_by(FactCropPerformance.region)
        .order_by(FactCropPerformance.region)
    ).all()

    top_region_rows = db.execute(
        select(
            FactCropPerformance.region,
            func.sum(FactCropPerformance.total_yield_estimate).label("total_yield"),
        )
        .group_by(FactCropPerformance.region)
        .order_by(desc("total_yield"))
        .limit(5)
    ).all()

    return AnalyticsSummary(
        total_rows=total_rows,
        average_yield_by_region=[
            AverageYieldByRegion(
                region=region,
                average_yield_kg_per_hectare=_to_optional_float(average_yield),
            )
            for region, average_yield in average_yield_rows
        ],
        top_regions_by_total_estimated_yield=[
            TopRegionByYield(
                region=region,
                total_yield_estimate=_to_optional_float(total_yield),
            )
            for region, total_yield in top_region_rows
        ],
    )


def _to_optional_float(value: object) -> float | None:
    """Convert SQL aggregate values into JSON-friendly floats."""
    if value is None:
        return None
    return float(value)
