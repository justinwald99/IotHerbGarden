"""Manager for the garden.

This module handles logging sensor values to the database as
well as the automation of watering events.

"""
import json
from datetime import datetime as dt

import paho.mqtt.client as mqtt
from sqlalchemy import select

from utils.common import connection_message, get_broker_ip, parse_json_payload
from utils.db_interaction import (create_plant, create_sample, create_sensor,
                                  create_watering_event, engine, initialize_db,
                                  plant_table, sensor_table, watering_table)
from utils.logging import mqtt_logger, sample_logger

# Create all of the schema objects in the database and create the engine.
initialize_db()

# IP for the MQTT broker
broker_ip = ""

# Create an MQTT client object
client = mqtt.Client("garden_manager")


def check_plants():
    """Check that every soil_humidity sensor has a plant associated with it.

    If there exists a soil_humidity sensor that does not have a plant associated,
    create a new plant with default values in the DB.
    """
    with engine.connect() as conn:
        plant_ids = conn.execute(
            select(plant_table.c.id)
        ).fetchall()
        # Convert list of tuples into list of ids.
        plant_ids = [id for id, in plant_ids]

        associated_sensor_ids = conn.execute(
            select(plant_table.c.humidity_sensor_id)
        ).fetchall()
        associated_sensor_ids = [id for id, in associated_sensor_ids]

        humidity_sensors = conn.execute(
            select(sensor_table.c.id).where(
                sensor_table.c.type == 'soil_humidity')
        ).fetchall()
        humidity_sensors = [id for id, in humidity_sensors]

        # now we have all plants and soil humidity sensors
        for humidity_sensor_id in humidity_sensors:
            # Create plants for every humidity sensor
            if humidity_sensor_id not in associated_sensor_ids:
                # Plant with default values
                create_plant({
                    # plant_ids is combined with single-element list to prevent max([])
                    "name": f"plant_{max(plant_ids + [0]) + 1}",
                    "humidity_sensor_id": humidity_sensor_id,
                    "pump_id": max(plant_ids + [0]) + 1,
                    "target": 50,
                    "watering_cooldown": 300,
                    "watering_duration": 1,
                    "humidity_tolerance": 5
                })
                # Recursive call so we don't have to keep track of generated ids
                check_plants()
                return


def check_watering(msg):
    """Check whether a plant needs to be watered by a pump

    Parameters
    ----------
    msg : dict
        Message from a soil_humidity sensor that may a prompt a watering event.
            Format:
                {
                    sensor_id: <id>,
                    timestamp: <ISO>,
                    value: <value>
                }
    """
    # Ensure that all humidity_sensors have an associated plant object.
    check_plants()

    # Select data on the plant for the given soil_humidity sensor_id
    with engine.connect() as conn:
        plant_info = conn.execute(
            select(plant_table).
            where(plant_table.c.humidity_sensor_id == msg["sensor_id"])
        ).first()

    id, name, hum_sensor_id, pump_id, target, cooldown, duration, tolerance = plant_info

    with engine.connect() as conn:
        last_watering_event = conn.execute(
            select(watering_table)
            .where(watering_table.c.plant_id == id)
            .order_by(watering_table.c.timestamp.desc())
        ).fetchone()

    # Check if plant has never been watered or if last time watered is longer than cooldown
    if (not last_watering_event or (msg["timestamp"] - last_watering_event["timestamp"]).total_seconds() > cooldown):
        # Check if the soil humidity is less than target - tolerance
        if (msg["value"] < target - tolerance):
            payload = {
                "duration": duration
            }
            mqtt_logger.info(
                f"Published to pumps/control/{pump_id}: {json.dumps(payload, indent=4)}")
            client.publish(
                f"pumps/control/{pump_id}", payload=json.dumps(payload), qos=2)


def on_connect(client, userdata, flags, rc):
    """Print when the MQTT broker accepts the connection."""
    mqtt_logger.info(connection_message(broker_ip, rc))


def handle_pumps_control(client, userdata, msg):
    """Log a watering event in the database."""
    payload = parse_json_payload(msg)
    mqtt_logger.info(
        f"Received pump event for pump_id {msg.topic.split('/')[-1]}: {json.dumps(payload, indent=4)}")

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
    create_watering_event(payload)


def handle_plants_config(client, userdata, msg):
    """Update the DB to save plant configs."""
    payload = parse_json_payload(msg)
    mqtt_logger.info(f"Received plant config: {json.dumps(payload, indent=4)}")
    create_plant(payload)


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
    create_sensor(payload)
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

    create_sample(payload)

    with engine.connect() as conn:
        result = conn.execute(
            select(sensor_table.c.type)
            .where(sensor_table.c.id == payload["sensor_id"])
        ).fetchone()

    if result[0] == "soil_humidity":
        # Check if the plant needs to be watered
        check_watering(payload)


def publish_status():
    """Publish the status of garden_manager."""
    client.publish("status/garden_manager",
                   payload="online", qos=2, retain=True)
    mqtt_logger.info("Published status")


def publish_sensor_info():
    """Publish the current sensor info."""
    with engine.connect() as conn:
        result = conn.execute(select(sensor_table))
        info = []
        for row in result:
            id, type, name, unit, sample_gap = row
            info.append({
                "id": id,
                "type": type,
                "name": name,
                "unit": unit,
                "sample_gap": sample_gap
            })
    client.publish("sensors/info", payload=json.dumps(info),
                   qos=2, retain=True)
    mqtt_logger.info(
        f"Published to sensors/info: {json.dumps(info, indent=4)}")


if (__name__ == "__main__"):
    # Ensure that the client provided an IP for the MQTT broker
    broker_ip = get_broker_ip(__file__)

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
