"""Shared transformation utilities."""

import re


def normalize_column_name(column_name: str) -> str:
    """Convert a column name to snake_case."""
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")
