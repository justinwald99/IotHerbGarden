import time
from datetime import datetime as dt
import paho.mqtt.client as mqtt
import json
import random

client = mqtt.Client("test")
client.connect("192.168.1.232")

client.loop_start()


while True:
    time.sleep(.5)
    payload = {
        "timestamp": str(dt.now()),
        "value": random.random() * 100
    }
    print(json.dumps(payload))
    client.publish("sensors/data/1", json.dumps(payload))