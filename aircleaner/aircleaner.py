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


# update time
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    location = config.get(CONF_AREA)


    for condition in config[CONF_MONITORED_CONDITIONS]:
        add_devices([WeatherSensor(weather, condition)])

    return True


class AircleanerSensor(Entity):
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


