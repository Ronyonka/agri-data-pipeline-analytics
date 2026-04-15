"""Reusable data quality checks for pipeline DataFrames."""

import pandas as pd

MIN_REASONABLE_TEMPERATURE_C = -50
MAX_REASONABLE_TEMPERATURE_C = 60
FACT_KEY_COLUMNS = ["region", "date", "crop_name"]


class DataQualityError(ValueError):
    """Raised when a data quality check fails."""


def require_columns(
    data: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    """Validate that a DataFrame includes required columns."""
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise DataQualityError(f"{dataset_name} is missing required columns: {missing}")


def validate_no_null_dates(data: pd.DataFrame, date_column: str = "date") -> None:
    """Validate that date values are present."""
    require_columns(data, {date_column}, "date check input")
    if data[date_column].isnull().any():
        raise DataQualityError(f"{date_column} contains null values")


def validate_no_null_regions(
    data: pd.DataFrame,
    region_column: str = "region",
) -> None:
    """Validate that region/location values are present."""
    require_columns(data, {region_column}, "region check input")
    normalized = data[region_column].astype("string").str.strip()
    if normalized.isnull().any() or (normalized == "").any():
        raise DataQualityError(f"{region_column} contains null or blank values")


def validate_non_negative_values(data: pd.DataFrame, columns: list[str]) -> None:
    """Validate that numeric columns do not contain negative values."""
    require_columns(data, set(columns), "non-negative check input")
    for column in columns:
        values = pd.to_numeric(data[column], errors="raise")
        if (values.dropna() < 0).any():
            raise DataQualityError(f"{column} contains negative values")


def validate_temperature_ranges(
    data: pd.DataFrame,
    min_column: str = "temperature_2m_min",
    max_column: str = "temperature_2m_max",
) -> None:
    """Validate temperatures are within a conservative Celsius range."""
    require_columns(data, {min_column, max_column}, "temperature check input")
    for column in [min_column, max_column]:
        values = pd.to_numeric(data[column], errors="raise").dropna()
        outside_range = (
            (values < MIN_REASONABLE_TEMPERATURE_C)
            | (values > MAX_REASONABLE_TEMPERATURE_C)
        )
        if outside_range.any():
            raise DataQualityError(
                f"{column} contains values outside "
                f"{MIN_REASONABLE_TEMPERATURE_C} to "
                f"{MAX_REASONABLE_TEMPERATURE_C} Celsius"
            )


def validate_no_duplicate_fact_keys(data: pd.DataFrame) -> None:
    """Validate fact rows are unique by region, date, and crop name."""
    require_columns(data, set(FACT_KEY_COLUMNS), "fact key check input")
    duplicate_rows = data.duplicated(subset=FACT_KEY_COLUMNS, keep=False)
    if duplicate_rows.any():
        raise DataQualityError("fact data contains duplicate region/date/crop_name rows")
