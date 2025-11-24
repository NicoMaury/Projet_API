"""Pydantic schemas shared across the API."""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class APIMessage(BaseModel):
    """Generic API response message."""

    detail: str


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    MAJOR = "major"
    CRITICAL = "critical"


class TransportMode(str, Enum):
    """Transport mode types."""
    TRAIN = "train"
    TGV = "tgv"
    TER = "ter"
    INTERCITES = "intercites"
    TRANSILIEN = "transilien"


# ===== Regions & Départements =====
class Region(BaseModel):
    id: str
    name: str
    code: Optional[str] = None


class RegionList(BaseModel):
    regions: List[Region]
    total: int


class Departement(BaseModel):
    id: str
    name: str
    code: str
    region_id: Optional[str] = None
    region_name: Optional[str] = None


class DepartementList(BaseModel):
    departements: List[Departement]
    total: int


# ===== Stations =====
class StationCoordinates(BaseModel):
    latitude: float
    longitude: float


class Station(BaseModel):
    id: str
    name: str
    uic_code: Optional[str] = None
    departement: Optional[str] = None
    commune: Optional[str] = None
    coordinates: Optional[StationCoordinates] = None
    is_active: bool = True


class StationDetail(Station):
    """Detailed station information."""
    address: Optional[str] = None
    accessibility: Optional[bool] = None
    services: List[str] = Field(default_factory=list)


class StationList(BaseModel):
    stations: List[Station]
    total: int


class DelayInfo(BaseModel):
    """Delay information for a train."""
    train_id: str
    train_number: Optional[str] = None
    scheduled_time: datetime
    actual_time: Optional[datetime] = None
    delay_minutes: int
    status: str  # on_time, delayed, cancelled


class StationDelayStats(BaseModel):
    """Delay statistics for a station."""
    station_id: str
    station_name: str
    period_start: datetime
    period_end: datetime
    total_trains: int
    delayed_trains: int
    average_delay_minutes: float
    max_delay_minutes: int
    on_time_rate: float
    recent_delays: List[DelayInfo] = Field(default_factory=list)


# ===== Lines =====
class Line(BaseModel):
    id: str
    name: str
    code: Optional[str] = None
    transport_mode: Optional[TransportMode] = None
    operator: Optional[str] = "SNCF"
    color: Optional[str] = None


class LineDetail(Line):
    """Detailed line information."""
    stations: List[str] = Field(default_factory=list)
    frequency: Optional[str] = None
    first_train: Optional[str] = None
    last_train: Optional[str] = None


class LineList(BaseModel):
    lines: List[Line]
    total: int


class LineStats(BaseModel):
    """Performance statistics for a line."""
    line_id: str
    line_name: str
    period_start: datetime
    period_end: datetime
    total_trains: int
    on_time_trains: int
    delayed_trains: int
    cancelled_trains: int
    punctuality_rate: float
    average_delay_minutes: float
    incidents_count: int


# ===== Trains =====
class TrainStop(BaseModel):
    """Train stop information."""
    station_id: str
    station_name: str
    scheduled_arrival: Optional[datetime] = None
    scheduled_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    delay_minutes: int = 0


class Train(BaseModel):
    id: str
    number: str
    line_id: Optional[str] = None
    transport_mode: Optional[TransportMode] = None
    departure_station: Optional[str] = None
    arrival_station: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    status: str = "scheduled"  # scheduled, in_progress, delayed, cancelled, completed


class TrainDetail(Train):
    """Detailed train information."""
    stops: List[TrainStop] = Field(default_factory=list)
    current_delay_minutes: int = 0
    platform: Optional[str] = None
    composition: Optional[str] = None


class TrainList(BaseModel):
    trains: List[Train]
    total: int


# ===== Alerts =====
class Alert(BaseModel):
    """Network alert information."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    affected_lines: List[str] = Field(default_factory=list)
    affected_stations: List[str] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class AlertList(BaseModel):
    alerts: List[Alert]
    total: int
