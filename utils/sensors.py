"""Utility class that standarizes interaction with different sensors."""
import time
from datetime import datetime as dt

import adafruit_dht


class generic_sensor():
    """Abstrac class that describes expected behavior of a sensor."""

    def __init__(self, id, unit, sample_gap):
        """Create a new generic sensor."""
        self.id = id
        self.unit = unit
        self.sample_gap = sample_gap
        self.last_sample = dt.now()

    def sample(self):
        """Return a sample of data."""
        raise NotImplementedError


class soil_humidity(generic_sensor):
    """A single capacitive soil humidity sensor hooked to an ADC."""

    def __init__(self, id, adc, adc_index, unit="", sample_gap=60, wet_value=0, dry_value=255):
        """Concrete soil humidity sensor.

        Capacitive soil humidity sensor that emits an anologue reading.
        This sensor must be connected to an ADC to be read by the pi which
        is why the ADC object must be passed into the constructor.

        Parameters
        ----------
        id : int
            Sensor_id of the sensor, unique to each sensor.

        unit : string
            The unit to be appended to a reading for display.

        sample_gap : int
            The number of seconds between each sensor reading.

        adc : ADC_Library.ADS7830()
            The ADC object that the soil humidity sensor is hooked up to.

        adc_index : int
            Index of the channel to read for this sensor.

        dry_value : int
            This should be the value from the adc that represents
                completely dry soil.
        wet_value : int
            This should be the value from the adc that represents
                completely saturated soil.
        """
        super().__init__(id, unit, sample_gap)
        self.adc = adc
        self.adc_index = adc_index
        self.dry_value = dry_value
        self.wet_value = wet_value

    def sample(self):
        """Collect a sample from this sensor.

        Moist readings are lower than dry readings.

        Returns
        -------
        Percent from 0-1 indicating the percentage humidity measured in the soil.
        """
        raw_reading = self.adc.analogRead(self.adc_index)
        self.last_sample = dt.now()
        result = (1 - (raw_reading - self.wet_value) /
                  (self.dry_value - self.wet_value)) * 100
        result = min(result, 100)
        result = max(result, 0)
        result = round(result, 2)
        return result


class light(generic_sensor):
    """A photoresistor light sensor."""

    def __init__(self, id, adc, adc_index, unit="", sample_gap=60, dark_value=0, light_value=255):
        """Create a new photoresistor light sensor.

        The photoresistor emits an anolog signal that's read by the adc.

        Parameters
        ----------
        id : int
            Sensor_id of the sensor, unique to each sensor.

        unit : string
            The unit to be appended to a reading for display.

        sample_gap : int
            The number of seconds between each sensor reading.

        adc : ADC_Library.ADS7830()
            The ADC object that the soil humidity sensor is hooked up to.

        adc_index : int
            Index of the channel to read for this sensor.

        dark_value : int
            This should be the value in a very dark setting

        light_value : int
            This should be the value in a very bright setting
        """
        super().__init__(id, unit, sample_gap)
        self.adc = adc
        self.adc_index = adc_index
        self.dark_value = dark_value
        self.light_value = light_value

    def sample(self):
        """Collect a sample from this sensor.

        light readings are higher than dark readings.

        Returns
        -------
        Percent from 0-1 indicating the percentage of light.
        """
        raw_reading = self.adc.analogRead(self.adc_index)
        self.last_sample = dt.now()
        result = (raw_reading - self.dark_value) / \
            (self.light_value - self.dark_value) * 100
        result = min(result, 100)
        result = max(result, 0)
        result = round(result, 2)
        return result


class dht_22():
    """Wrapper for the DHT-22 to prevent over-querying."""

    def __init__(self, pin):
        """Create one instance of this class per DHT-22.

        Parameters
        ----------
        pin : board.pin
            The GPIO pin that the DHT-22's data wire is connected to.
        """
        self.dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)
        self.temperature_f = 0
        self.humidity = 0
        self._update_values()

    def get_humidity(self):
        """Return the current relative humidity.

        Returns the most recent humidity value or querries the sensor again if more than 2 seconds have passed
        """
        if ((dt.now() - self.last_sample).total_seconds() > 2.5):
            self._update_values()

        return round(self.humidity, 1)

    def get_temperature_f(self):
        """Return the current temperature in fahrenheit.

        Returns the most recent temperature value or querries the sensor again if more than 2 seconds have passed
        """
        if (not self.last_sample or (dt.now() - self.last_sample).total_seconds() > 2.5):
            self._update_values()
        return round(self.temperature_f, 1)

    def _update_values(self):
        """Private method to retrieve values then put them in cache to rate-limit querries."""
        try:
            self.last_sample = dt.now()
            temperature_c = self.dhtDevice.temperature
            self.temperature_f = temperature_c * (9 / 5) + 32
            self.humidity = self.dhtDevice.humidity

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)

        except Exception as error:
            self.dhtDevice.exit()
            raise error


class ambient_temperature(generic_sensor):
    """The temperature side of the DHT-22."""

    def __init__(self, id, dht_22, unit="°f", sample_gap=60):
        """Create a new instance of the temperature sensors.

        The DHT-22 houses a humidity sensor as well as temperature sensors. This
        class records samples for the temperature sensor.

        Parameters
        ----------
        id : int
            Sensor_id of the sensor, unique to each sensor.

        unit : string
            The unit to be appended to a reading for display.

        sample_gap : int
            The number of seconds between each sensor reading.

        dht_22 : sensors.dht_22
            The dht_22 sensor to query values from.
        """
        super().__init__(id, unit, sample_gap)
        self.dht_22 = dht_22

    def sample(self):
        """Collect a sample from this sensor.

        Returns
        -------
        Temperature in fahrenheit
        """
        self.last_sample = dt.now()
        return self.dht_22.get_temperature_f()


class ambient_humidity(generic_sensor):
    """The humidity side of the DHT-22."""

    def __init__(self, id, dht_22, unit="%", sample_gap=60):
        """Create a new instance of the humidity sensors.

        The DHT-22 houses a humidity sensor as well as temperature sensors. This
        class records samples for the humidity sensor.

        Parameters
        ----------
        id : int
            Sensor_id of the sensor, unique to each sensor.

        unit : string
            The unit to be appended to a reading for display.

        sample_gap : int
            The number of seconds between each sensor reading.

        dht_22 : sensors.dht_22
            The dht_22 sensor to query values from.
        """
        super().__init__(id, unit, sample_gap)
        self.dht_22 = dht_22

    def sample(self):
        """Collect a sample from this sensor.

        Returns
        -------
        Relative humidity percentage.
        """
        self.last_sample = dt.now()
        return self.dht_22.get_humidity()
