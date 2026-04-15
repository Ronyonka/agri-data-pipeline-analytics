"""Initialize database objects for the project."""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app.models  # noqa: F401
from app.db import Base, engine
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create database tables defined by SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization completed")


if __name__ == "__main__":
    setup_logging()
    init_db()
