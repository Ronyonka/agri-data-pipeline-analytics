"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI

from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agri Data Pipeline Analytics",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the service health status."""
    logger.info("Health check requested")
    return {"status": "ok"}
