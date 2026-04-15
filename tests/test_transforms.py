"""Tests for crop, weather, and fact transformations."""

from datetime import date

import pandas as pd
import pytest

from app.quality.checks import DataQualityError
from app.transformations.crop_transform import clean_crop_data
from app.transformations.fact_table_transform import build_crop_performance_fact
from app.transformations.weather_transform import clean_weather_data


def crop_data() -> pd.DataFrame:
    """Return minimal crop transform input."""
    return pd.DataFrame(
        [
            {
                "Region": " Nairobi ",
                "Date": "2025-01-15",
                "Crop Name": " Maize ",
                "Yield Kg Per Hectare": "2000",
                "Area Hectares": "3",
            }
        ]
    )


def weather_data() -> pd.DataFrame:
    """Return minimal weather transform input."""
    return pd.DataFrame(
        [
            {
                "Location": " Nairobi ",
                "Date": "2025-01-15",
                "Temperature 2m Max": "28",
                "Temperature 2m Min": "14",
                "Precipitation Sum": "2.5",
                "Rainfall Sum": "2.0",
            }
        ]
    )


def test_clean_crop_data_normalizes_dates_and_numeric_values() -> None:
    cleaned = clean_crop_data(crop_data())

    assert cleaned.loc[0, "region"] == "Nairobi"
    assert cleaned.loc[0, "crop_name"] == "Maize"
    assert cleaned.loc[0, "date"] == date(2025, 1, 15)
    assert cleaned.loc[0, "yield_kg_per_hectare"] == 2000
    assert cleaned.loc[0, "area_hectares"] == 3


def test_clean_weather_data_normalizes_dates_and_numeric_values() -> None:
    cleaned = clean_weather_data(weather_data())

    assert cleaned.loc[0, "location"] == "Nairobi"
    assert cleaned.loc[0, "date"] == date(2025, 1, 15)
    assert cleaned.loc[0, "temperature_2m_max"] == 28
    assert cleaned.loc[0, "temperature_2m_min"] == 14


def test_build_crop_performance_fact_joins_and_computes_total_yield() -> None:
    fact_data = build_crop_performance_fact(crop_data(), weather_data())

    assert len(fact_data) == 1
    assert fact_data.loc[0, "region"] == "Nairobi"
    assert fact_data.loc[0, "temperature_2m_max"] == 28
    assert fact_data.loc[0, "total_yield_estimate"] == 6000


def test_weather_transform_rejects_unreasonable_temperatures() -> None:
    data = weather_data()
    data.loc[0, "Temperature 2m Max"] = "80"

    with pytest.raises(DataQualityError, match="temperature_2m_max"):
        clean_weather_data(data)


def test_fact_transform_rejects_duplicate_fact_keys() -> None:
    duplicated_crop_data = pd.concat([crop_data(), crop_data()], ignore_index=True)

    with pytest.raises(DataQualityError, match="duplicate region/date/crop_name"):
        build_crop_performance_fact(duplicated_crop_data, weather_data())
