import sys
import time

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