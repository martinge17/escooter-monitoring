import asyncio
from pydoc import cli
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional, Union, Type
from datetime import datetime
from pydantic import Json, JsonValue
from sqlalchemy.orm import Session
from models import GeneralInfo as GeneralInfoModel  # SQLAlchemy model
from models import BatteryInfo as BatteryInfoModel  # SQLAlchemy model
from models import LocationInfo as LocationInfoModel  # SQLAlchemy model

from schemas import (
    GeneralInfo,
    BatteryInfo,
    LocationInfoGeoJSON,
    PowerResponse,
    UnifiedGlobalData,
    PowerCommand,
    RelayPowerModes,
    MQTTResponse,
)  # Pydantic model


from sqlalchemy import select

from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from fastapi_pagination import add_pagination

from database import SessionLocal, engine
import models

#########################################################
# TODO FOR TEST PASAR A ARHCIVO MQTT
import paho.mqtt.client as mqtt_client
import json

client_id = "test-fastapi"
broker = "localhost"
mqtt_port = 1883
topic = "vehicle/1/control"

mqtt_response = None  # TODO: PROPERLY HANDLE CONCURRENCY FOR MQTT_RESPONSE


def on_message_ctrl(client, userdata, msg):

    global mqtt_response
    try:
        payload = json.loads(msg.payload.decode())
        mqtt_response = payload  ##TODO: TO PYDANTIC MODEL

        # Avoid infinite loops by checking if the message received == client response
        if next(iter(mqtt_response)) != "response":
            return

        print(f"Received Ctrl MQTT message: {mqtt_response}")
    except Exception as e:
        print(f"Can't process message: {e}")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic, 1)
    else:
        print("Failed to connect, return code %d\n", reason_code)


client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt_client.MQTTv5
)


client.message_callback_add(
    topic, on_message_ctrl
)  # Defines how to handle control messages only

client.on_connect = on_connect


# https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python
# https://fastapi.tiangolo.com/advanced/events/#async-context-manager
# TODO MQTT
@asynccontextmanager
async def lifespan(app: FastAPI):
    client.connect(broker, 1883, 60)
    client.loop_start()
    yield  # From here the code is executed on exit
    client.disconnect()
    client.loop_stop()


##########################################################

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    lifespan=lifespan,
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


########################################################################################################


########################################################################################################


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


# TODO: USE SCALAR FOR IMPROVED EFFICIENCY
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


async def command_to_scooter(command: Union[PowerCommand, dict]):

    try:
        global mqtt_response
        mqtt_response = None

        if type(command) is PowerCommand:
            payload = command.model_dump_json()
        else:
            payload = json.dumps(command)

        print(f"Publishing: {payload}")
        s = client.publish(topic, payload)

        # Wait for publish and response 5 secs
        await asyncio.sleep(3)

        if s.is_published() == False:
            print("Cant publish message")
            raise ConnectionError

        if mqtt_response is None:
            return PowerResponse(
                MQTTResponse(
                    result=False,
                    status="unknown",
                    reason="Didn't get response from scooter. Please check status using get_relay_status",
                )
            )

        return mqtt_response

    except ConnectionError:
        return PowerResponse(
            MQTTResponse(result=False, reason="Can't send message to MQTT broker")
        )


@app.get("/api/v1/command/get_relay_status", summary="Gets the power relay status")
async def get_relay_status() -> PowerResponse:

    return await command_to_scooter({"status": "query"})


# https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-commands#door-unlock
@app.post(
    "/api/v1/command/set_power", summary="Sets the power relay state to open or closed"
)
async def set_power(
    command: PowerCommand,
) -> PowerResponse:

    return await command_to_scooter(command)
