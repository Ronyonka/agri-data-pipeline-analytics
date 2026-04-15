"""Initialize database objects for the project."""

import logging

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
