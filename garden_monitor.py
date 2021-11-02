"""Monitor that runs on the pi to collect sensor data and run pumps."""
import json
import os
import threading
import time
from datetime import datetime as dt

import board
import paho.mqtt.client as mqtt
import yaml
from gpiozero.output_devices import OutputDevice

from utils.adc_library import ADS7830
from utils.common import connection_message, parse_json_payload
from utils.logging import (config_logger, mqtt_logger, pump_logger,
                           sample_logger)
from utils.sensors import (ambient_humidity, ambient_temperature, dht_22,
                           light, soil_humidity)

# Create the MQTT client
client = mqtt.Client("garden_monitor")

# IP for the MQTT broker
broker_host = ""

# Config to hold sensor config data
sensor_config = {}

# Sensor dictionary with sensor values that can be sampled
sensors = {}

# Make an object to interact with the analog-to-digital converter
adc = ADS7830()

# Object used to control access to the dht-22 sensor
dht_22 = dht_22(board.D17)

# Register pumps on GPIO pins
pump1 = OutputDevice("GPIO26", active_high=False)
pump2 = OutputDevice("GPIO19", active_high=False)
pump3 = OutputDevice("GPIO13", active_high=False)
pump4 = OutputDevice("GPIO6", active_high=False)

# Threading lock to prevent concurrent pump activation
pump_lock = threading.Lock()

# Map pump ids to their pump objects
pump_mapping = {
    "1": pump1,
    "2": pump2,
    "3": pump3,
    "4": pump4
}


def read_config():
    """Read the config JSON that contains known info about the sensors connected.

    This data needs to be reconciled with known data from sensors/info before building.
    """
    with open("sensor_config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file.read())
    config_logger.info(f"Loaded config: {json.dumps(config, indent=4)}")
    return config


def build_sensors():
    """Build sensor objects from the configuration stored in sensors."""
    config_logger.info(
        f"Reconciled config: {json.dumps(sensor_config, indent=4)}")
    for id, sensor in sensor_config.items():
        if (sensor["type"] == "soil_humidity"):
            new_sensor = soil_humidity(
                id, adc, sensor["adc_index"], unit=sensor["unit"],
                sample_gap=sensor["sample_gap"], dry_value=sensor["dry_value"],
                wet_value=sensor["wet_value"]
            )
            sensors.update({new_sensor.id: new_sensor})

        if (sensor["type"] == "ambient_humidity"):
            new_sensor = ambient_humidity(
                id, dht_22, unit=sensor["unit"], sample_gap=sensor["sample_gap"]
            )
            sensors.update({new_sensor.id: new_sensor})

        if (sensor["type"] == "ambient_temperature"):
            new_sensor = ambient_temperature(
                id, dht_22, unit=sensor["unit"], sample_gap=sensor["sample_gap"]
            )
            sensors.update({new_sensor.id: new_sensor})

        if (sensor["type"] == "light"):
            new_sensor = light(
                id, adc, sensor["adc_index"], unit=sensor["unit"],
                sample_gap=sensor["sample_gap"], dark_value=sensor["dark_value"],
                light_value=sensor["light_value"]
            )
            sensors.update({new_sensor.id: new_sensor})
        config_logger.info(
            f"Created {sensor['type']} sensor with id: {sensor['id']}")


def activate_pump(pump_id, duration, lock):
    """Activate pump for a specified amount of time, ensuring that only one pump runs at a time.

    Parameters
    ----------
    pump : int
        ID of the pump to activate.

    duration : int
        Number of seconds to run the pump.

    lock : threading.Lock()
        Lock primitive to prevent pumps running concurrently which may draw too much current.
    """
    pump = pump_mapping[pump_id]
    with lock:
        pump_logger.info(f"Pump {pump_id} activated")
        pump.on()
        time.sleep(duration)
        pump.off()
        pump_logger.info(f"Pump {pump_id} deactivated")


def sample_routine():
    """Run the main routines of the program.

    Collects data from the sensors if their sample_gap has elapsed since the last collection
    event. Then checks for MQTT messages.
    """
    for id, sensor in sensors.items():
        if (dt.now() - sensor.last_sample).total_seconds() > (sensor.sample_gap):
            value = sensor.sample()
            timestamp = dt.now()
            payload = {
                "value": value,
                "timestamp": timestamp.isoformat()
            }
            client.publish(f'sensors/data/{id}',
                           payload=json.dumps(payload), qos=2)
            sample_logger.info(
                f"Published {value}{sensor.unit} for sensor_id {id}")


def handle_pumps_control(client, userdata, msg):
    """Activate a specified pump when a message is received on pumps/control/{id}."""
    data = parse_json_payload(msg)
    mqtt_logger.info(
        f"Pump instruction received: {json.dumps(data, indent=4)}")

    pump_id = msg.topic.split("/")[-1]

    new_thread = threading.Thread(target=activate_pump, args=(
        pump_id, data["duration"], pump_lock))
    new_thread.start()


def handle_sensor_info(client, userdata, msg):
    """Reconcile known sensor info from garden_manager with local config."""
    global sensors
    known_sensors = parse_json_payload(msg)
    mqtt_logger.info(
        f"Received config from sensors/info: {json.dumps(known_sensors, indent=2)}")

    # For sensors that are passed, we change our local config
    for known_sensor in known_sensors:
        # Check for sensor_id matches in the known config vs local
        if str(known_sensor["id"]) in sensor_config.keys():
            sensor_config[str(known_sensor["id"])].update(
                {
                    "type": known_sensor["type"],
                    "name": known_sensor["name"],
                    "unit": known_sensor["unit"],
                    "sample_gap": known_sensor["sample_gap"]
                }
            )
    # For sensors that sensors/info didn't know about, we send a default config to sensors/config
    known_ids = [str(sensor["id"]) for sensor in known_sensors]
    for id, sensor in sensor_config.items():
        if id not in known_ids:
            payload = {
                "id": id,
                "type": sensor["type"],
                "name": sensor["name"],
                "unit": sensor["unit"],
                "sample_gap": sensor["sample_gap"]
            }
            mqtt_logger.info(
                f"Publishing new sensor config for sensor_id {id}")
            client.publish("sensors/config",
                           payload=json.dumps(payload), qos=2, retain=False)

    # Once config has been reconciled, build sensors.
    build_sensors()


def publish_status(client, userdata=None, flags=None, rc=None):
    """Publish the status of garden_monitor."""
    mqtt_logger.info(connection_message(broker_host, rc))
    client.publish("status/garden_monitor",
                   payload="online", qos=2, retain=True)
    mqtt_logger.info("Status published")


"""
On startup, sensor info is empty
garden monitor will call sensor config for each of the sensors not in sensor info
garden monitor gets current state from sensors info. If garden monitor has the sensors,
it will change the values it has if they are different. However, if garden monitor has
sensors unknown to sensors info, it will post a sensors/config for each one that is not
included.
"""
if __name__ == '__main__':
    # Set garden_monitor's last will message for when it is offline.
    client.will_set("status/garden_monitor",
                    payload="offline", qos=2, retain=True)

    # Set callback methods
    client.on_connect = publish_status
    client.message_callback_add("pumps/control/#", handle_pumps_control)
    client.message_callback_add("sensors/info", handle_sensor_info)

    # Connect to the MQTT broker
    client.connect(os.environ.get("MQTT_BROKER_HOST"), 1883)

    # Subscribe to applicable topics
    client.subscribe([
        ("sensors/info", 2),
        ("pumps/control/+", 2)
    ])

    # Send online message
    publish_status(client)

    # Load basic values in.
    sensor_config = read_config()

    build_sensors()

    # Start the main routine
    while(True):
        sample_routine()
        client.loop()
