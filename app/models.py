"""SQLAlchemy ORM models for raw and analytics tables."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RawWeather(Base):
    """Raw daily weather observations by location."""

    __tablename__ = "raw_weather"
    __table_args__ = (
        UniqueConstraint("location", "date", name="uq_raw_weather_location_date"),
        Index("ix_raw_weather_location_date", "location", "date"),
        Index("ix_raw_weather_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature_2m_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_2m_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_sum: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_sum: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class RawCropData(Base):
    """Raw crop yield and area observations by region."""

    __tablename__ = "raw_crop_data"
    __table_args__ = (
        UniqueConstraint(
            "region",
            "date",
            "crop_name",
            name="uq_raw_crop_data_region_date_crop_name",
        ),
        Index("ix_raw_crop_data_region_date_crop_name", "region", "date", "crop_name"),
        Index("ix_raw_crop_data_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    region: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    crop_name: Mapped[str] = mapped_column(String(120), nullable=False)
    yield_kg_per_hectare: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class FactCropPerformance(Base):
    """Analytics fact table joining crop performance and weather metrics."""

    __tablename__ = "fact_crop_performance"
    __table_args__ = (
        UniqueConstraint(
            "region",
            "date",
            "crop_name",
            name="uq_fact_crop_performance_region_date_crop_name",
        ),
        Index(
            "ix_fact_crop_performance_region_date_crop_name",
            "region",
            "date",
            "crop_name",
        ),
        Index("ix_fact_crop_performance_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    region: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    crop_name: Mapped[str] = mapped_column(String(120), nullable=False)
    yield_kg_per_hectare: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_2m_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_2m_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_sum: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_sum: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_yield_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
