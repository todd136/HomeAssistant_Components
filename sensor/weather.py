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
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_RESOURCE = 'http://api.weatherdt.com/common/?area={}&type=observe&key={}'
_LOGGER = logging.getLogger(__name__)

#
CONF_AREA = 'area'

# update time
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)

# Sensor types
SENSOR_TYPES = {
    'observationTime': ('Observation time', None, '000'),
    'weather': ('Weather', None, '001'),
    'temperature': ('Temperature', '°C', '002'),
    'windSpeed': ('Wind Speed level', 'level', '003'),
    'windDirection': ('Wind direction', None, '004'),
    'humidity': ('Humidity', '%', '005'),
    'rainTrace': ('Rain Today', 'mm', '006'),
    'pressure': ('Pressure', 'hPa', '007'),
}

# wind direction code text dict
WIND_DIRECTION = {
    '0': ('无持续风向', 'No wind'),
    '1': ('东北风', 'Northeast'),
    '2': ('东风', 'East'),
    '3': ('东南风', 'Southeast'),
    '4': ('南风', 'South'),
    '5': ('西南风', 'Southwest'),
    '6': ('西风', 'West'),
    '7': ('西北风', 'Northwest'),
    '8': ('北风', 'North'),
    '9': ('旋转风', 'Whirl wind'),
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
        condition_code = self._get_condition_code()
        if self.rest.data and condition_code in self.rest.data:
            state = self.rest.data[condition_code]
            if self._condition == 'windDirection':
                state = self._get_wind_by_code(state)
            return state

        return STATE_UNKNOWN

    def _get_condition_code(self):
        """Return the code of the condition, that used to get value from weather china"""
        return SENSOR_TYPES[self._condition][2]

    def _get_wind_by_code(self, state):
        """Return the wind direction by code dict"""
        return WIND_DIRECTION[state][0]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._condition][1]

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

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            result = requests.get(self._build_request_url(), timeout=10).json()
            result_value = result['observe'][self._location]['1001002']
            self.data = result_value
        except ValueError as err:
            _LOGGER.error('get weather data error, msg = s%', err.args)
            self.data = None
