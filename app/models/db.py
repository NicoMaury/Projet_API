"""Relational database models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class RequestLog(Base):
    """Store each API call for auditing and analytics."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    user_id = Column(String(128), nullable=True)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class Region(Base):
    """French regions."""

    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    nom = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    departements = relationship("Departement", back_populates="region")


class Departement(Base):
    """French departments."""

    __tablename__ = "departements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    nom = Column(String(255), nullable=False, index=True)
    region_code = Column(String(10), ForeignKey("regions.code"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    region = relationship("Region", back_populates="departements")


class Station(Base):
    """Railway stations (gares SNCF)."""

    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    uic_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    commune = Column(String(255), nullable=True)
    departement_code = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    has_freight = Column(Boolean, default=False)
    has_passengers = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relations - No FK to departement since API returns names not codes
    delay_stats = relationship("StationDelayStat", back_populates="station")


class Line(Base):
    """Railway lines."""

    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, index=True)
    line_code = Column(String(200), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    network = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    text_color = Column(String(7), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    trains = relationship("Train", back_populates="line")
    line_stats = relationship("LineStat", back_populates="line")


class Train(Base):
    """Trains in circulation."""

    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(50), nullable=False, index=True)
    line_code = Column(String(200), ForeignKey("lines.line_code"), nullable=True)
    origin = Column(String(255), nullable=True)
    destination = Column(String(255), nullable=True)
    departure_time = Column(DateTime(timezone=True), nullable=True)
    arrival_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=True)  # on_time, delayed, cancelled
    delay_minutes = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    line = relationship("Line", back_populates="trains")


# NOTE: Incidents/Disruptions are fetched directly from Navitia API in real-time
# No database model needed for incidents


class StationDelayStat(Base):
    """Delay statistics by station."""

    __tablename__ = "station_delay_stats"

    id = Column(Integer, primary_key=True, index=True)
    station_uic_code = Column(String(20), ForeignKey("stations.uic_code"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_trains = Column(Integer, default=0)
    delayed_trains = Column(Integer, default=0)
    average_delay_minutes = Column(Float, default=0.0)
    max_delay_minutes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    station = relationship("Station", back_populates="delay_stats")


class LineStat(Base):
    """Performance statistics by line."""

    __tablename__ = "line_stats"

    id = Column(Integer, primary_key=True, index=True)
    line_code = Column(String(200), ForeignKey("lines.line_code"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_trains = Column(Integer, default=0)
    on_time_trains = Column(Integer, default=0)
    delayed_trains = Column(Integer, default=0)
    cancelled_trains = Column(Integer, default=0)
    punctuality_rate = Column(Float, default=0.0)  # Percentage
    average_delay_minutes = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    line = relationship("Line", back_populates="line_stats")
