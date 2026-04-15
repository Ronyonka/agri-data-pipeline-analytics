"""Streamlit dashboard for crop performance analytics."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

shadowed_app = sys.modules.get("app")
if shadowed_app and getattr(shadowed_app, "__file__", None) == __file__:
    del sys.modules["app"]

from app.db import SessionLocal
from app.models import FactCropPerformance


@st.cache_data(ttl=300)
def load_fact_data() -> pd.DataFrame:
    """Load crop performance facts from PostgreSQL."""
    with SessionLocal() as db:
        rows = db.execute(select(FactCropPerformance)).scalars().all()

    records = [
        {
            "region": row.region,
            "date": row.date,
            "crop_name": row.crop_name,
            "yield_kg_per_hectare": row.yield_kg_per_hectare,
            "area_hectares": row.area_hectares,
            "temperature_2m_max": row.temperature_2m_max,
            "temperature_2m_min": row.temperature_2m_min,
            "precipitation_sum": row.precipitation_sum,
            "rainfall_sum": row.rainfall_sum,
            "total_yield_estimate": row.total_yield_estimate,
        }
        for row in rows
    ]
    data = pd.DataFrame(records)
    if not data.empty:
        data["date"] = pd.to_datetime(data["date"])
    return data


def apply_filters(
    data: pd.DataFrame,
    selected_regions: list[str],
    selected_crops: list[str],
) -> pd.DataFrame:
    """Apply region and crop filters to dashboard data."""
    filtered_data = data.copy()
    if selected_regions:
        filtered_data = filtered_data[filtered_data["region"].isin(selected_regions)]
    if selected_crops:
        filtered_data = filtered_data[filtered_data["crop_name"].isin(selected_crops)]
    return filtered_data


def render_header() -> None:
    """Render the dashboard header."""
    st.title("Agri Data Pipeline Analytics")
    st.caption(
        "Crop yield, weather, and regional performance insights from the analytics "
        "fact table."
    )


def render_filters(data: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Render dashboard filters and return selected values."""
    st.subheader("Filters")
    regions = sorted(data["region"].dropna().unique().tolist())
    crops = sorted(data["crop_name"].dropna().unique().tolist())

    region_column, crop_column = st.columns(2)
    with region_column:
        selected_regions = st.multiselect("Region", regions)
    with crop_column:
        selected_crops = st.multiselect("Crop", crops)

    return selected_regions, selected_crops


def render_kpis(data: pd.DataFrame) -> None:
    """Render dashboard KPI metrics."""
    st.subheader("Overview")
    total_records = len(data)
    average_yield = data["yield_kg_per_hectare"].mean()
    total_estimated_yield = data["total_yield_estimate"].sum()

    total_column, average_column, yield_column = st.columns(3)
    total_column.metric("Total records", f"{total_records:,}")
    average_column.metric("Average yield", f"{average_yield:,.0f} kg/ha")
    yield_column.metric("Total estimated yield", f"{total_estimated_yield:,.0f} kg")


def render_top_regions(data: pd.DataFrame) -> None:
    """Render top-performing regions by total estimated yield."""
    st.subheader("Top-performing regions")
    top_regions = (
        data.groupby("region", as_index=False)
        .agg(
            total_yield_estimate=("total_yield_estimate", "sum"),
            average_yield_kg_per_hectare=("yield_kg_per_hectare", "mean"),
            records=("region", "size"),
        )
        .sort_values("total_yield_estimate", ascending=False)
        .head(10)
    )
    st.dataframe(
        top_regions,
        use_container_width=True,
        hide_index=True,
        column_config={
            "region": "Region",
            "total_yield_estimate": st.column_config.NumberColumn(
                "Total estimated yield",
                format="%.0f kg",
            ),
            "average_yield_kg_per_hectare": st.column_config.NumberColumn(
                "Average yield",
                format="%.0f kg/ha",
            ),
            "records": "Records",
        },
    )


def render_yield_trend(data: pd.DataFrame) -> None:
    """Render average yield trend over time."""
    st.subheader("Yield trend over time")
    trend = (
        data.groupby("date", as_index=False)["yield_kg_per_hectare"]
        .mean()
        .sort_values("date")
    )
    trend = trend.rename(columns={"yield_kg_per_hectare": "Average yield"})
    st.line_chart(trend, x="date", y="Average yield")


def render_empty_state(message: str) -> None:
    """Render an empty-state information message."""
    st.info(message)


def main() -> None:
    """Render the Streamlit dashboard."""
    st.set_page_config(page_title="Agri Data Pipeline Analytics", layout="wide")
    render_header()

    try:
        with st.spinner("Loading analytics data..."):
            fact_data = load_fact_data()
    except Exception as exc:
        st.error(f"Unable to load analytics data: {exc}")
        return

    if fact_data.empty:
        render_empty_state("No fact table records found. Run the pipeline first.")
        return

    selected_regions, selected_crops = render_filters(fact_data)
    filtered_data = apply_filters(fact_data, selected_regions, selected_crops)

    if filtered_data.empty:
        render_empty_state("No records match the selected filters.")
        return

    st.divider()
    render_kpis(filtered_data)
    st.divider()
    render_top_regions(filtered_data)
    st.divider()
    render_yield_trend(filtered_data)


if __name__ == "__main__":
    main()
