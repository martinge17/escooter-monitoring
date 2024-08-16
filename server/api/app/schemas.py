# Pydantic models to serialize data into Python
from pydantic import BaseModel, field_validator, PositiveInt, ConfigDict
from datetime import datetime
import json
from enum import Enum
from typing import Union, Literal
from models import RelayPowerModes


class RelayPowerModes(str, Enum):
    open = "open"  # If it is open then there is no power
    close = "close"


class PowerCommand(BaseModel):
    status: RelayPowerModes


class MQTTResponse(BaseModel):
    result: bool
    status: Union[
        RelayPowerModes, Literal["unknown"]
    ]  # Since it is possible that the scooter return status "unknown"
    reason: str


class PowerResponse(BaseModel):
    response: MQTTResponse


class GeneralInfo(BaseModel):
    time: datetime
    speed_kmh: float
    trip_distance_m: float
    uptime_sec: PositiveInt
    total_distance_m: float
    est_distance_left_km: float
    frame_temp: float

    model_config = ConfigDict(from_attributes=True)


class BatteryInfo(BaseModel):
    time: datetime
    capacity: float
    percent: int
    voltage: float
    current: float
    power: float  # Generated column in DB
    temp1: int
    temp2: int

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class UnifiedGlobalData(BaseModel):
    # time: datetime
    # general: GeneralInfo
    # battery: BatteryInfo
    # location: LocationInfoGeoJSON
    time: datetime
    speed_kmh: float
    trip_distance_m: float
    uptime_sec: PositiveInt
    total_distance_m: float
    est_distance_left_km: float
    frame_temp: float
    capacity: float
    percent: int
    voltage: float
    current: float
    power: float  # Generated column in DB
    temp1: int
    temp2: int
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

    model_config = ConfigDict(from_attributes=True)
