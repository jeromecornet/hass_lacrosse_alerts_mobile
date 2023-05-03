import logging

import voluptuous as vol

from homeassistant.components.sensor import ENTITY_ID_FORMAT, PLATFORM_SCHEMA
from homeassistant.const import TEMP_CELSIUS, CONF_ID, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, DeviceInfo
from . import DOMAIN



REQUIREMENTS = ['pylacrossapi==0.3']

_LOGGER = logging.getLogger(__name__)

UNIT = 1 # 1 = ˚C , 0 = ˚F
TIME_ZONE = 17 # America/Toronto
CONF_TZ = "timezone"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_TZ): cv.positive_int
})



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the lacrosse alerts mobile platform."""
    device_id = config.get(CONF_ID)
    device_name = config.get(CONF_NAME)
    timezone = config.get(CONF_TZ)   
    add_devices([LaCrosseAmbientSensor(device_name,device_id, timezone)])
    add_devices([LaCrosseProbeSensor(device_name,device_id, timezone)])
    add_devices([LaCrosseHumidSensor(device_name,device_id, timezone)])


class LaCrosseSensor(Entity):
    import pylacrossapi

    """Representation of a LaCrosse Alerts Mobile Sensor."""
    def __init__(self, device_name, device_id, timezone):
        """Initialize the sensor."""
        self._lacrosse_device =   pylacrossapi.lacrosse(device_id, UNIT, timezone or TIME_ZONE)
        self._state = None
        self._attr_name = device_name or "LaCrosse-"+device_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
        )

class LaCrosseAmbientSensor(LaCrosseSensor):

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + '.Ambient_Temp'

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
        
class LaCrosseProbeSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + '.Probe_Temp'

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


class LaCrosseHumidSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + '.Ambient_Humidity'

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
