# Pydantic models to serialize data into Python
from pydantic import (
    BaseModel,
    condecimal,
    conint,
    PositiveFloat,
    PositiveInt,
    FiniteFloat,
)
from datetime import datetime


class GeneralInfo(BaseModel):
    time: datetime
    speed_kmh: float
    trip_distance_m: float
    uptime_sec: PositiveInt
    total_distance_m: float
    est_distance_left_km: float
    frame_temp: float

    class Config:
        orm_mode = True


class BatteryInfo(BaseModel):
    time: datetime
    capacity: float
    percent: int
    voltage: float
    current: float
    power: float  # Generated column in DB
    temp1: int
    temp2: int

    class Config:
        orm_mode = True


class LocationInfo(BaseModel):
    time: datetime
    location: str  # TODO FIX
    altitude: float
    gps_speed: float

    class Config:
        orm_mode = True
