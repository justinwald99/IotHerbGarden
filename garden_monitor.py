import sys
import time
import json

import paho.mqtt.client as mqtt
from ADC_Library import ADS7830
from gpiozero import GPIODevice
import dht11

adc = ADS7830()
# soil sensors channel: 0, 1, 2, 3
# light sensor channel: 4
ambientySensor = dht11.DHT11(pin = 11)
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

sensors = []

#       (id: <int>):
        #(type: <string>,
        #name: <string>,
        #unit: <string>,
        #sample_rate_hz: <int>)


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
    sensor_info = json.loads(msg)
    # collect all known sensor ids
    known_ids = []
    for sensor in sensors:
        known_ids.append(sensor["id"])
    for sensor in sensor_info:
        if sensor["id"] in known_ids:
            for known_sensor in sensors:
                if sensor["id"] == known_sensor["id"]:
                    sensors[sensors.index(known_sensor)] = sensor
                    known_sensor = sensor
                    break
            



def sample_routine():
    

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

    sample_routine()
    # store retained messages from config - check
    # use that config to sample
    # after sampling, send to sensors/data/{id}
    # look for new config on sensors/info and manual pumps on pumps/control
