"""Logging configuration for the application."""

import logging
import logging.config
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "%(asctime)s %(levelname)s "
                    "%(name)s %(module)s:%(lineno)d %(message)s"
                )
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }
    logging.config.dictConfig(logging_config)
