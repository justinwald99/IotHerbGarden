import sys
import time
import json
import datetime
from utils.common import get_broker_ip, print_connection

import paho.mqtt.client as mqtt
from ADC_Library import ADS7830
from gpiozero import GPIODevice

# Create the MQTT client
client = mqtt.Client("garden_monitor")

# Config to hold sensor config data
config = []

adc = ADS7830()
# soil sensors channel: 0, 1, 2, 3
# light sensor channel: 4
# result = ambientSensor.read
# temp = result.temperature
# humidity = result.humidity
pump1 = GPIODevice("GPIO26")
pump2 = GPIODevice("GPIO19")
pump3 = GPIODevice("GPIO13")
pump4 = GPIODevice("GPIO5")

pump_mapping = {
    "pump1": pump1,
    "pump2": pump2,
    "pump3": pump3,
    "pump4": pump4
}

sensors = {}  # TODO: Hard code default values
# ids 0, 1, 2, 3 will be soil sensors. id=4 will be light,
# id=5 will be temperature from DHT, id=6 will be ambient humidity from DHT


def read_config():
    """Read the config JSON that contains known info about the sensors connected."""
    with open("sensor_config.json", "r") as config_file:
        config = json.loads(config_file.read())
    return config


def on_connect(client, obj, flags, rc):
    """Print a message when connected to the MQTT broker."""
    print_connection()


def handle_pumps_control(client, userdata, msg):
    # will be subscribed to pumps/control, which will have an {id} at the end.
    chunk = msg.topic.split("/")  # chunk[2] is id, chunk[3] is time
    curr = pump_mapping[chunk[2]]
    curr.value = 1
    time.sleep(int(chunk[3]))
    curr.value = 0


def handle_sensor_info(client, userdata, msg):
    global sensors
    sensor_info = json.loads(msg)
    # For sensors that are passed, we change our local config
    knownids = []
    for sensor in sensor_info:
        if sensor["id"] in dict.keys(sensors):
            sensors[sensor["id"]] = {
                "type": sensor["type"],
                "name": sensor["name"],
                "unit": sensor["unit"],
                "sample_rate_hz": sensor["sample_rate_hz"]
            }
            knownids.append("id")
    # For sensors that sensor info didn't know about, we pass them through sensors/config/id
    # monitor - knownids = unknown to manager
    for index, sensor in dict.items(sensors):
        if index not in knownids:
            client.publish(f"sensors/config/{index}",
                           payload=json.dumps({"id": index,
                                              "type": sensor["type"],
                                               "name": sensor["name"],
                                               "unit": sensor["unit"],
                                               "sample_rate_hz": sensor["sample_rate_hz"]}), qos=2, retain=False)


def sample(sensor):
    print("wip")
    for sensor in sensors:
        print(f"{sensor.id}: {sensor.sample()} {sensor.unit}")


def sample_routine():  # TODO: code the sample routine
    # guaranteed to have received the retained sensors info if it exists, don't have to
    # poll again until the end of the loop.
    last_sampled = {sensor_id: datetime.datetime.now()
                    for sensor_id in sensors.keys()}
    while(1):
        for id, sample_timestamp in last_sampled.items:
            if (datetime.datetime.now() - sample_timestamp).total_seconds() > (sensors[id]["samples"]):
                sample(sensors[id])
                last_sampled[id] = datetime.datetime.now()


def publish_status():
    """Publish the status of garden_monitor."""
    client.publish("status/garden_monitor",
                   payload="online", qos=2, retain=True)


"""
On startup, sensor info is empty
garden monitor will call sensor config for each of the sensors not in sensor info
garden monitor gets current state from sensors info. If garden monitor has the sensors,
it will change the values it has if they are different. However, if garden monitor has
sensors unknown to sensors info, it will post a sensors/config for each one that is not
included.
"""
if __name__ == '__main__':
    # Check for correct execution of program
    get_broker_ip(__file__)

    # Load known values in.
    config = read_config()

    print(config)

    # Set garden_monitor's last will message for when it is offline.
    client.will_set("status/garden_monitor",
                    payload="offline", qos=2, retain=True)

    # Set callback methods
    client.on_connect = on_connect
    client.message_callback_add("pumps/control/#", handle_pumps_control)
    client.message_callback_add("sensors/info", handle_sensor_info)

    # Subscribe to applicable topics
    client.subscribe([
        ("sensors/info", 2),
        ("pumps/control/+", 2)
    ])

    # Connect to the MQTT broker
    client.connect(sys.argv[1], 1883)

    # store retained messages from config - check
    # use that config to sample
    # after sampling, send to sensors/data/{id}
    # look for new config on sensors/info and manual pumps on pumps/control
