import logging

import voluptuous as vol

from homeassistant.components.sensor import ENTITY_ID_FORMAT, PLATFORM_SCHEMA
from homeassistant.const import TEMP_CELSIUS, CONF_ID
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['pylacrossapi==0.3']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the lacrosse alerts mobile platform."""
    import pylacrossapi
    device_id = config.get(CONF_ID)
    unit_measure = 1
    time_zone = 17
    lacrosse_device = pylacrossapi.lacrosse(device_id, unit_measure, time_zone)
    add_devices([LaCrosseAmbientSensor(lacrosse_device)])
    add_devices([LaCrosseProbeSensor(lacrosse_device)])
    add_devices([LaCrosseHumidSensor(lacrosse_device)])


class LaCrosseAmbientSensor(Entity):
    """Representation of a LaCrosse Alerts Mobile Sensor."""
    def __init__(self, lacrosse_device):
        """Initialize the sensor."""
        self._lacrosse_device = lacrosse_device
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Lacrosse.Ambient_Temp'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS
        
    def update(self):
        obs = self._lacrosse_device.getObservation(1)
        self._state = obs[0]['ambient_temp']
        
class LaCrosseProbeSensor(Entity):
    """Representation of a LaCrosse Alerts Mobile Sensor."""
    def __init__(self, lacrosse_device):
        """Initialize the sensor."""
        self._lacrosse_device = lacrosse_device
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Lacrosse.Probe_Temp'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS
        
    def update(self):
        obs = self._lacrosse_device.getObservation(1)
        self._state = obs[0]['probe_temp']


class LaCrosseHumidSensor(Entity):
    """Representation of a LaCrosse Alerts Mobile Sensor."""
    def __init__(self, lacrosse_device):
        """Initialize the sensor."""
        self._lacrosse_device = lacrosse_device
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Lacrosse.Ambient_Humidity'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return 'mdi:water-percent'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        obs = self._lacrosse_device.getObservation(1)
        self._state = obs[0]['humidity']
