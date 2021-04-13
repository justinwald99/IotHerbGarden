import time

from ADC_Library import ADS7830
from utils.sensors import ambient_humidity, ambient_temperature, soil_humidity, light, dht_22
import board

adc = ADS7830()
dht_22 = dht_22(board.D17)
sensor_1 = soil_humidity(1, adc, 0)
sensor_2 = soil_humidity(2, adc, 1)
sensor_3 = soil_humidity(3, adc, 2)
sensor_4 = soil_humidity(4, adc, 3)
sensor_5 = ambient_temperature(5, dht_22)
sensor_6 = ambient_humidity(6, dht_22)
sensor_7 = light(7, adc, 4)

while (1):
    print(f"Humidity: {sensor_1.sample()}, {sensor_2.sample()}, {sensor_3.sample()}"
          f", {sensor_4.sample()}, Temperature: {sensor_5.sample()}, Humidity: {sensor_6.sample()}, Light: {sensor_7.sample()}")
    time.sleep(2.1)
