"""Pipeline runner for local data ingestion."""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.logging_config import setup_logging
from app.services.pipeline_service import run_pipeline as run_pipeline_service

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run the local data ingestion pipeline."""
    result = run_pipeline_service()
    logger.info("Pipeline result: %s", result.model_dump())


if __name__ == "__main__":
    setup_logging()
    run_pipeline()
