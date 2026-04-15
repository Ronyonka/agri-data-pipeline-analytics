"""Tests for reusable data quality checks."""

import pandas as pd
import pytest

from app.quality.checks import (
    DataQualityError,
    validate_no_duplicate_fact_keys,
    validate_no_null_dates,
    validate_no_null_regions,
    validate_non_negative_values,
    validate_temperature_ranges,
)


def valid_fact_data() -> pd.DataFrame:
    """Return a minimal valid fact-like DataFrame."""
    return pd.DataFrame(
        [
            {
                "region": "Nairobi",
                "date": "2025-01-15",
                "crop_name": "Maize",
                "yield_kg_per_hectare": 2000,
                "area_hectares": 3,
                "temperature_2m_min": 14,
                "temperature_2m_max": 28,
            }
        ]
    )


def test_valid_data_quality_checks_pass() -> None:
    data = valid_fact_data()

    validate_no_null_dates(data)
    validate_no_null_regions(data)
    validate_non_negative_values(data, ["yield_kg_per_hectare", "area_hectares"])
    validate_temperature_ranges(data)
    validate_no_duplicate_fact_keys(data)


def test_null_dates_fail() -> None:
    data = valid_fact_data()
    data.loc[0, "date"] = None

    with pytest.raises(DataQualityError, match="date contains null values"):
        validate_no_null_dates(data)


def test_null_regions_fail() -> None:
    data = valid_fact_data()
    data.loc[0, "region"] = " "

    with pytest.raises(DataQualityError, match="region contains null or blank values"):
        validate_no_null_regions(data)


def test_negative_yield_fails() -> None:
    data = valid_fact_data()
    data.loc[0, "yield_kg_per_hectare"] = -1

    with pytest.raises(DataQualityError, match="yield_kg_per_hectare"):
        validate_non_negative_values(data, ["yield_kg_per_hectare"])


def test_negative_area_fails() -> None:
    data = valid_fact_data()
    data.loc[0, "area_hectares"] = -1

    with pytest.raises(DataQualityError, match="area_hectares"):
        validate_non_negative_values(data, ["area_hectares"])


def test_unreasonable_temperature_fails() -> None:
    data = valid_fact_data()
    data.loc[0, "temperature_2m_max"] = 80

    with pytest.raises(DataQualityError, match="temperature_2m_max"):
        validate_temperature_ranges(data)


def test_duplicate_fact_keys_fail() -> None:
    data = pd.concat([valid_fact_data(), valid_fact_data()], ignore_index=True)

    with pytest.raises(DataQualityError, match="duplicate region/date/crop_name"):
        validate_no_duplicate_fact_keys(data)
