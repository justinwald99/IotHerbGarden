import sys
import time
import json
import datetime

import paho.mqtt.client as mqtt
from ADC_Library import ADS7830
from gpiozero import GPIODevice
import dht11
import asyncio

adc = ADS7830()
# soil sensors channel: 0, 1, 2, 3
# light sensor channel: 4
ambientSensor = dht11.DHT11(pin = 11)
# result = ambientSensor.read
# temp = result.temperature
# humidity = result.humidity
pump1 = GPIODevice("GPIO26")
pump2 = GPIODevice("GPIO19")
pump3 = GPIODevice("GPIO13")
pump4 = GPIODevice("GPIO5")

pump_mapping = {
    "pump1":pump1,
    "pump2":pump2,
    "pump3":pump3,
    "pump4":pump4
}

sensors = {} ## TODO: Hard code default values
# ids 0, 1, 2, 3 will be soil sensors. id=4 will be light,
# id=5 will be temperature from DHT, id=6 will be ambient humidity from DHT

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos[0]))

def on_control_message(client, userdata, msg):
    # will be subscribed to pumps/control, which will have an {id} at the end.
    chunk = msg.topic.split("/") # chunk[2] is id, chunk[3] is time
    curr = pump_mapping[chunk[2]]
    curr.value = 1
    time.sleep(int(chunk[3]))
    curr.value = 0
        

def on_sensor_info(client, userdata, msg):
    global sensors
    sensor_info = json.loads(msg)
    #For sensors that are passed, we change our local config
    knownids = []
    for sensor in sensor_info:
        if sensor["id"] in dict.keys(sensors):
            sensors[sensor["id"]] = {
                "type":sensor["type"],
                "name":sensor["name"],
                "unit":sensor["unit"], 
                "sample_rate_hz":sensor["sample_rate_hz"]
            }
            knownids.append("id")
    #For sensors that sensor info didn't know about, we pass them through sensors/config/id
    # monitor - knownids = unknown to manager
    for index, sensor in dict.items(sensors):
        if index not in knownids:
            mqttc.publish(f"sensors/config/{index}",
                 payload=json.dumps({"id":index,
                    "type":sensor["type"],
                    "name":sensor["name"],
                    "unit":sensor["unit"],
                    "sample_rate_hz":sensor["sample_rate_hz"]}), qos=2, retain=False)


def sample(sensor):
    print("wip")
    if sensor.key in range(0,5):
        adc.analogRead(sensor.key)
        # TODO: send MQTT message with results
    elif sensor.key == 5: #read temperature
        pass # TODO: Figure out what library and methods we need to use to read from DHT
        # TODO: send MQTT message with results
    elif sensor.key == 6: #read humidity
        pass # TODO: Figure out what library and methods we need to use to read from DHT
        # TODO: send MQTT message with results


def sample_routine(): ## TODO: code the sample routine
    # guaranteed to have received the retained sensors info if it exists, don't have to 
    # poll again until the end of the loop.
    last_sampled = { sensor_id:datetime.datetime.now() for sensor_id in sensors.keys() }
    while(1):
        for id, sample_timestamp in last_sampled.items:
            if (datetime.datetime.now() - sample_timestamp).total_seconds() > (sensors[id]["samples"]):
                sample(sensors[id])
                last_sampled[id] = datetime.datetime.now()
    

# on startup, sensor info is empty
# garden monitor will call sensor config for each of the sensors not in sensor info
# garden monitor gets current state from sensors info. If garden monitor has the sensors,
# it will change the values it has if they are different. However, if garden monitor has
# sensors unknown to sensors info, it will post a sensors/config for each one that is not
# included.
if __name__ == '__main__':
    # Check for correct execution of program
    if len(sys.argv) < 2:
        raise ValueError("Please execute the program: python3 index.py <MQTT_IP>")
    # connect to MQTT, set last will to offline
    mqttc = mqtt.Client("garden_monitor")
    mqttc.will_set("status/garden_monitor", payload="offline", qos=2, retain=True)
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe
    mqttc.message_callback_add("pumps/control/#", on_control_message)
    mqttc.message_callback_add("sensors/info", on_sensor_info)
    # will be subscribed to sensors/info, which is a list of all sensor dictionaries
    mqttc.connect(sys.argv[1], 1883)

    asyncio.run(sample_routine())
    # store retained messages from config - check
    # use that config to sample
    # after sampling, send to sensors/data/{id}
    # look for new config on sensors/info and manual pumps on pumps/control
