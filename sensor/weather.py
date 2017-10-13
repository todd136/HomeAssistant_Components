"""
Support for weather china observe weather service.

For more details about this platform, please refer to the documentation at
https://github.com/todd136/HomeAssistant_Components
"""
import logging
import requests
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_MONITORED_CONDITIONS, TEMP_CELSIUS,
                                 CONF_API_KEY, ATTR_FRIENDLY_NAME, STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_RESOURCE = 'http://api.weatherdt.com/common/?area={}&type=observe&key={}'
_LOGGER = logging.getLogger(__name__)

#
CONF_AREA = 'area'

# Sensor types
SENSOR_TYPES = {
    'weather': ('Weather', None),
    'temperature': ('Temperature', '°C'),
    'windDirection': ('Wind direction', '°'),
    'windSpeed': ('Wind Speed level', 'level'),
    'humidity': ('Humidity', '%'),
    'rainTrace': ('Rain Today', 'mm'),
    'pressure': ('Pressure', 'hPa'),
    'observationTime': ('Observation time', None)
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_AREA): cv.string,
    vol.Required(CONF_MONITORED_CONDITIONS, default=[]):
    vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    location = config.get(CONF_AREA)

    weather = WeatherData(hass, config.get(CONF_API_KEY), location)

    for condition in config[CONF_MONITORED_CONDITIONS]:
        add_devices([WeatherSensor(weather, condition)])

    return True


class WeatherSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, rest, condition):
        """Initialize the sensor."""
        self.rest = rest
        self._condition = condition

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._condition

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.rest.data and self._get_code_by_condition() in self.rest.data:
            state = self.rest.data[self._get_code_by_condition()]
            return state

        return STATE_UNKNOWN

    def _get_code_by_condition(self):
        if self._condition == 'observationTime':
            return '000'
        elif self._condition == 'weather':
            return '001'
        elif self._condition == 'temperature':
            return '002'
        elif self._condition == 'windSpeed':
            return '003'
        elif self._condition == 'windDirection':
            return '004'
        elif self._condition == 'humidity':
            return '005'
        elif self._condition == 'rainTrace':
            return '006'
        elif self._condition == 'pressure':
            return '007'
        else:
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._condition][1]

    # def _get_state(self):
    #     return STATE_UNKNOWN

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.rest.update()


class WeatherData(object):
    def __init__(self, hass, api_key, location):
        self._hass = hass
        self._api_key = api_key
        self._location = location
        self.data = None

    def _build_request_url(self, baseurl=_RESOURCE):
        url = baseurl.format(self._location, self._api_key)
        return url

    def update(self):
        try:
            result = requests.get(self._build_request_url(), timeout=10).json()
            result_value = result['observe'][self._location]['1001002']
            self.data = result_value
        except ValueError as err:
            _LOGGER.error('get weather data error, msg = s%', err.args)
            self.data = None
