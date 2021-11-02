class RealSensorABC():
    """Abstract class to define the expected and common behavior of a hardware sensor.
    """

    def ___init__(self):
        """Create the sensor and configure anything that is needed for function.
        """
        return NotImplementedError()

    def get_value(self):
        """Return the current value of the sensor.

        Returns
        -------
            The current value of the sensor.
        """
        return NotImplementedError()

    def get_unit(self):
        """Return the unit of the value returned by the sensor.
        """

    def get_config(self):
        """Return the configuration used by the sensor.
        """


class Photoresistor(RealSensorABC):
    """Photoresistor for measuring light

    Parameters
    ----------
    RealSensorABC : [type]
        [description]
    """
    def __init__(adc_pin, min_value, max_value):
        """[summary]

        Parameters
        ----------
        adc_pin : [type]
            [description]
        min_value : [type]
            [description]
        max_value : [type]
            [description]
        """
