"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI, HTTPException

from app.db import SessionLocal
from app.logging_config import setup_logging
from app.services.pipeline_service import (
    AnalyticsSummary,
    PipelineResult,
    get_analytics_summary,
    run_pipeline,
)

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


@app.post("/pipeline/run", response_model=PipelineResult)
def run_pipeline_endpoint() -> PipelineResult:
    """Run the data pipeline synchronously."""
    try:
        return run_pipeline()
    except Exception as exc:
        logger.exception("Pipeline endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary() -> AnalyticsSummary:
    """Return summary metrics from the fact table."""
    try:
        with SessionLocal() as db:
            return get_analytics_summary(db)
    except Exception as exc:
        logger.exception("Analytics summary endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
