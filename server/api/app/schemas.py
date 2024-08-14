# Pydantic models to serialize data into Python
from pydantic import (
    BaseModel,
    field_validator,
    PositiveInt,
)
from datetime import datetime
import json


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


class LocationInfoGeoJSON(BaseModel):
    time: datetime
    geojson: dict  # Here return a GeoJSON for simplicity
    altitude: float
    gps_speed: float

    # Since by default ST_AsGeoJSON returns the json as a string.
    # Create a field_validator to parse that string into a real object before returning it
    @field_validator("geojson", mode="before")
    def parse_geojson(cls, value):
        if isinstance(value, str):
            return json.loads(value)  # Convert the JSON string to a dictionary
        return value

    class Config:
        orm_mode = True
