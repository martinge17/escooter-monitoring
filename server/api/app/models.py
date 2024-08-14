from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    DECIMAL,
    SmallInteger,
)
from database import Base
from geoalchemy2 import Geography, functions
from sqlalchemy.orm import column_property


# Since this API is intended to be read-only, constraints are not defined here.


# Model the database tables for the ORM to access the DB.
class GeneralInfo(Base):
    __tablename__ = "general_info"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    speed_kmh = Column(DECIMAL(4, 2), nullable=False)
    trip_distance_m = Column(Integer, nullable=False)
    uptime_sec = Column(Integer, nullable=False)
    total_distance_m = Column(Integer, nullable=False)
    est_distance_left_km = Column(DECIMAL(5, 2), nullable=False)
    frame_temp = Column(DECIMAL(4, 2), nullable=False)


class BatteryInfo(Base):
    __tablename__ = "battery_info"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    capacity = Column(SmallInteger, nullable=False)
    percent = Column(SmallInteger, nullable=False)
    voltage = Column(DECIMAL(4, 2), nullable=False)
    current = Column(DECIMAL(5, 3), nullable=False)
    power = Column(DECIMAL(5, 2), nullable=False)  # Generated column in DB
    temp1 = Column(SmallInteger, nullable=False)
    temp2 = Column(SmallInteger, nullable=False)


class LocationInfo(Base):
    __tablename__ = "location_info"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    location = Column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )  # GeoAlchemy2 https://geoalchemy-2.readthedocs.io/en/latest/index.html
    altitude = Column(DECIMAL(6, 2), nullable=False)
    gps_speed = Column(DECIMAL(4, 2), nullable=False)

    # Test try to convert to geojson https://geojson.org/
    geojson = column_property(functions.ST_AsGeoJSON(location))  # Map an SQL response


# Model data classes
