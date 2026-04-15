"""Pipeline runner placeholder."""

import logging

from app.logging_config import setup_logging

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run the data pipeline when business logic is added."""
    logger.info("Pipeline scaffold is ready")


if __name__ == "__main__":
    setup_logging()
    run_pipeline()
