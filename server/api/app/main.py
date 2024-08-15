from fastapi import FastAPI, Depends, HTTPException, Query
from enum import Enum
from typing import Optional, Union, Type
from datetime import datetime
from sqlalchemy.orm import Session
from models import GeneralInfo as GeneralInfoModel  # SQLAlchemy model
from models import BatteryInfo as BatteryInfoModel  # SQLAlchemy model
from models import LocationInfo as LocationInfoModel  # SQLAlchemy model

from pydantic import BaseModel

from schemas import (
    GeneralInfo,
    BatteryInfo,
    LocationInfoGeoJSON,
    UnifiedGlobalData,
)  # Pydantic model


from sqlalchemy import select

from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from fastapi_pagination import add_pagination

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Electric Scooter information and control",
    description="ChangeME",
    version="0.1.0",
)

# Add pagination to the FastAPI app
add_pagination(app)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db = get_db()


def validate_timeintervals(
    start: Optional[datetime] = None, end: Optional[datetime] = None
):
    """Validates that start_time is not ahead of end_time"""
    if (start != None and end != None) and start > end:
        raise HTTPException(
            status_code=400, detail="Start_date can't be posterior to end"
        )


class OrderSelector(str, Enum):
    asc = "asc"
    desc = "desc"


@app.get(
    "/api/v1/data",
    summary="Retrieve the latest data for all categories (battery,location,general)",
)
async def global_data(  # TODO TRY TO REFACTOR
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    order: OrderSelector = "asc",
) -> Page[UnifiedGlobalData]:

    # Base query with optional filters for all three models
    query = (
        select(
            GeneralInfoModel.time,
            GeneralInfoModel.speed_kmh,
            GeneralInfoModel.trip_distance_m,
            GeneralInfoModel.uptime_sec,
            GeneralInfoModel.total_distance_m,
            GeneralInfoModel.est_distance_left_km,
            GeneralInfoModel.frame_temp,
            BatteryInfoModel.capacity,
            BatteryInfoModel.percent,
            BatteryInfoModel.voltage,
            BatteryInfoModel.current,
            BatteryInfoModel.power,
            BatteryInfoModel.temp1,
            BatteryInfoModel.temp2,
            LocationInfoModel.geojson,
            LocationInfoModel.altitude,
            LocationInfoModel.gps_speed,
        )
        .join(BatteryInfoModel, GeneralInfoModel.time == BatteryInfoModel.time)
        .join(LocationInfoModel, GeneralInfoModel.time == LocationInfoModel.time)
    )

    if start_time:
        query = query.where(GeneralInfoModel.time >= start_time)
    if end_time:
        query = query.where(GeneralInfoModel.time <= end_time)

    # Order selector
    if order == OrderSelector.asc:
        query = query.order_by(GeneralInfoModel.time.asc())
    else:
        query = query.order_by(GeneralInfoModel.time.desc())

    return paginate(db, query)


# TODO: USE SCALAR FOR INPROVED EFICIENCY
# https://hatchjs.com/sqlalchemy-scalars-vs-all/


# Datatime accepts timestamp with hours minutes and second. If you don't specify hours and minutes it defaults to 00:00 of
# that date so if you type end_time 2024-08-01 it will show all results until 2024-08-01 00:00 so no result from that day will be shown
# If you want to include per example the whole day 2024-08-01 in the query you should add 2024-08-01T23:59:59 or 2024-08-02
# TODO: EXPLAIN THIS WITH EXAMPLE IN THE OPENAPI DOCS


# Base function to query data from the DB
def build_query(
    model: Union[
        Type[GeneralInfoModel], Type[BatteryInfoModel], Type[LocationInfoModel]
    ],
    order: OrderSelector,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    # Check date errors before anything
    validate_timeintervals(start_time, end_time)

    # Construct the base query with optional filters
    query = select(model)

    if start_time:  # If there is start_time filter by that
        query = query.where(model.time >= start_time)

    if end_time:  # If there is end_time filter by that
        query = query.where(model.time <= end_time)

    # Order selector
    if order == "asc":
        query = query.order_by(model.time.asc())
    else:
        query = query.order_by(model.time.desc())

    return query


@app.get("/api/v1/data/general")
async def general_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    order: OrderSelector = "asc",
) -> Page[GeneralInfo]:

    query = build_query(GeneralInfoModel, order, start_time, end_time)
    return paginate(db, query)


@app.get("/api/v1/data/battery")
async def battery_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    order: OrderSelector = "asc",
) -> Page[BatteryInfo]:

    query = build_query(BatteryInfoModel, order, start_time, end_time)
    return paginate(db, query)


@app.get("/api/v1/data/location")
async def location_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    order: OrderSelector = "asc",
) -> Page[LocationInfoGeoJSON]:

    query = build_query(LocationInfoModel, order, start_time, end_time)
    return paginate(db, query)


class RelayPowerModes(str, Enum):
    open = "open"  # If it is open then there is no power
    closed = "close"


class PowerCommand(BaseModel):
    state: RelayPowerModes


@app.post(
    "/api/v1/command/set_power", summary="Sets the power relay state to open or closed"
)
async def set_power(mode: RelayPowerModes):  # TODO
    return {"OPERATION X DONE. CURRENT STATE IS X"}
