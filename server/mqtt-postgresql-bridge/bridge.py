from paho.mqtt import client as mqtt_client
import psycopg
import json
import logging
import sys
import tomllib


# Enable logging to stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load configuration
try:
    file = open("config.toml", "rb")
except Exception:
    logging.error("Can't open config file", exc_info=True)
    exit(1)
else:
    with file:
        config = tomllib.load(file)

logging.info("Configuration loaded!")

# Load variables
broker = config["mqtt"]["broker"]
mqtt_port = config["mqtt"]["port"]
client_id = config["mqtt"]["client"]
topic = config["mqtt"]["topic"]
template = "postgresql://{user}:{password}@{hostname}:{port}/{dbname}"
connection_str = template.format(
    user=config["database"]["user"],
    password=config["database"]["password"],
    hostname=config["database"]["db_hostname"],
    port=config["database"]["db_port"],
    dbname=config["database"]["db_name"],
)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logging.info("Connected to MQTT Broker!")
    else:
        logging.exception("Failed to connect, return code %d\n", reason_code)


def on_message(client, userdata, msg):

    logging.info("Message received!")

    message = msg.payload.decode()
    data = json.loads(message)

    print(json.dumps(data))

    # Insert data into PostgreSQL
    try:
        with conn.cursor() as cur:
            # Insert to general_info
            logging.info("Executing general_info query")
            try:
                cur.execute(
                    """
                    INSERT INTO general_info (time,speed_kmh,trip_distance_m,uptime_sec,total_distance_m,est_distance_left_km,frame_temp)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            """,
                    (
                        data["timestamp"],
                        data["speed_kmh"],
                        data["trip_distance_m"],
                        data["uptime_sec"],
                        data["total_distance_m"],
                        data["trip_distance_left_km"],
                        data["frame_temp"],
                    ),
                )
            except Exception as e:
                logging.error(f"Error executing general_info query: {e}")
                conn.rollback()  # For security reasons, postgresql locks the db when a query produces an error and you try to run another query without first rolling back the transaction
                raise

            # Insert to battery_info
            logging.info("Executing battery_info query")
            try:
                cur.execute(
                    """
                    INSERT INTO battery_info (time,capacity,percent,voltage,current,temp1,temp2)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            """,
                    (
                        data["timestamp"],
                        data["battery_info"]["capacity"],
                        data["battery_info"]["percent"],
                        data["battery_info"]["voltage"],
                        data["battery_info"]["current"],
                        data["battery_info"]["temperature_1"],
                        data["battery_info"]["temperature_2"],
                    ),
                )
            except Exception as e:
                logging.error(f"Error executing battery_info query: {e}")
                conn.rollback()
                raise

            # Insert to location_info
            logging.info("Executing location_info query")
            try:
                cur.execute(
                    """
                    INSERT INTO location_info (time,location,altitude,gps_speed)
                            VALUES (%s,%s,%s,%s)
                            """,
                    (
                        data["timestamp"],
                        f"SRID=4326;POINT({data['gpsinfo']['longitude']} {data['gpsinfo']['latitude']})",
                        data["gpsinfo"]["altitude"],
                        data["gpsinfo"]["gps_speed"],
                    ),
                )
            except Exception as e:
                logging.error(f"Error executing location_info query: {e}")
                conn.rollback()
                raise
            # Commit changes
            logging.info("Commiting changes")

            conn.commit()
    except psycopg.errors.UniqueViolation:
        logging.exception("Entry already exists")
    except Exception as e:
        return e


# Connect to the PostgreSQL database
try:
    conn = psycopg.connect(connection_str)
    logging.info("Database connection established.")
except Exception as e:
    logging.error(f"Error connecting to the database: {e}")
    exit(1)


# Connect to the MQTT broker
client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt_client.MQTTv5
)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, mqtt_port)

client.subscribe(topic, 0)

# Start the MQTT client loop
try:
    client.loop_forever()
except Exception as e:
    logging.exception(e)
finally:
    client.disconnect()
    if conn:
        conn.close()
        logging.info("Database connection closed.")
