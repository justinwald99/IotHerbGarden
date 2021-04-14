"""Manager for the garden.

This module handles logging sensor values to the database as
well as the automation of watering events.

"""
import json
from datetime import datetime as dt
import logging

import paho.mqtt.client as mqtt
from sqlalchemy import MetaData, create_engine, select

from utils.common import get_broker_ip, parse_json_payload, connection_message
from utils.db_interaction import create_db, create_sensor, create_sample, create_plant, create_watering_event

# DB objects
engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
metadata = MetaData()

# IP for the MQTT broker
broker_ip = ""

# Create an MQTT client object
client = mqtt.Client("garden_manager")

# Logging setup
sample_logger = logging.getLogger("\u001b[32msample_log")
mqtt_logger = logging.getLogger("\u001b[35mmqtt_log")
config_logger = logging.getLogger("\u001b[34mconfig_log")

logging.basicConfig(
    level="INFO", format="\u001b[36m%(asctime)s \u001b[0m%(name)s \u001b[33m%(levelname)s \u001b[0m%(message)s")


def on_connect(client, userdata, flags, rc):
    """Print when the MQTT broker accepts the connection."""
    mqtt_logger.info(connection_message(broker_ip, rc))


def handle_pumps_control(client, userdata, msg):
    """Log a watering event in the database."""
    payload = parse_json_payload(msg)
    mqtt_logger.info(f"Received pump event for pump_id {msg.topic.split('/')[-1]}: {json.dumps(payload, indent=4)}")

    plant_table = metadata.tables["plant"]
    with engine.connect() as conn:
        result = conn.execute(
            select(plant_table.c.id).where(
                plant_table.c.id == int(msg.topic.split("/")[-1])
            )
        )
        plant_id = result.fetchone()[0]
    payload.update(
        {
            "timestamp": dt.now(),
            "plant_id": plant_id
        }
    )
    create_watering_event(engine, metadata, payload)


def handle_plants_config(client, userdata, msg):
    """Update the DB to save plant configs."""
    payload = parse_json_payload(msg)
    mqtt_logger.info(f"Received plant config: {json.dumps(payload, indent=4)}")
    create_plant(engine, metadata, payload)


def handle_sensors_config(client, userdata, msg):
    """Update the DB with a new sensor config, then broadcast a new 'sensors/info'."""
    payload = parse_json_payload(msg)
    mqtt_logger.info(
        f"Received sensor config: {json.dumps(payload, indent=4)}")
    payload.update(
        {
            "id": int(payload["id"]),
            "sample_gap": int(payload["sample_gap"])
        }
    )
    create_sensor(engine, metadata, payload)
    publish_sensor_info()


def handle_sensors_data(client, userdata, msg):
    """Log received data into the DB as a new data sample."""
    payload = parse_json_payload(msg)
    sample_logger.info(
        f"Received {payload['value']} from sensor_id {msg.topic.split('/')[-1]}")

    payload.update(
        {
            "sensor_id": msg.topic.split("/")[-1],
            "timestamp": dt.fromisoformat(payload["timestamp"])
        }
    )

    create_sample(engine, metadata, payload)


def publish_status():
    """Publish the status of garden_manager."""
    client.publish("status/garden_manager",
                   payload="online", qos=2, retain=True)
    mqtt_logger.info("Published status")


def publish_sensor_info():
    """Publish the current sensor info."""
    with engine.connect() as conn:
        result = conn.execute(select(metadata.tables["sensor"]))
        info = []
        for row in result:
            info.append({
                "id": row[0],
                "type": row[1],
                "name": row[2],
                "unit": row[3],
                "sample_gap": row[4]
            })
    client.publish("sensors/info", payload=json.dumps(info),
                   qos=2, retain=True)
    mqtt_logger.info(f"Published sensors/info: {json.dumps(info, indent=4)}")


if (__name__ == "__main__"):
    # Ensure that the client provided an IP for the MQTT broker
    broker_ip = get_broker_ip(__file__)

    # Create the tables needed if neccesary
    create_db(engine, metadata)

    # Add callbacks to the client
    client.message_callback_add("plants/config", handle_plants_config)
    client.message_callback_add("sensors/config", handle_sensors_config)
    client.message_callback_add("sensors/data/+", handle_sensors_data)
    client.message_callback_add("pumps/control/+", handle_pumps_control)
    client.on_connect = on_connect

    # Create the last will for garden_manager
    client.will_set("status/garden_manager",
                    payload="offline", qos=2, retain=True)

    # Create connection to MQTT broker
    client.connect(broker_ip, keepalive=5)

    # Subscribe to applicable topics
    client.subscribe([
        ("plants/config", 2),
        ("sensors/config", 2),
        ("sensors/data/+", 2),
        ("pumps/control/+", 2)
    ])

    publish_status()

    publish_sensor_info()

    client.loop_forever()
