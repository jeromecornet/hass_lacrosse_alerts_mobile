import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity

from homeassistant.const import TEMP_CELSIUS, CONF_ID, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN
from datetime import datetime


REQUIREMENTS = ["pylacrossapi==0.3"]

_LOGGER = logging.getLogger(__name__)

UNIT = 1  # 1 = ˚C , 0 = ˚F
TIME_ZONE = 17  # America/Toronto
CONF_TZ = "timezone"
STALE_TIMEOUT_MINUTES = 15

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TZ): cv.positive_int,
    }
)


def measureOrNone(obs, key):
    if datetime.timestamp(datetime.now()) - obs["utctime"] < STALE_TIMEOUT_MINUTES * 60:
        return obs[key]
    else:
        return None


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    from pylacrossapi import lacrosse

    """Setup the lacrosse alerts mobile platform."""
    device_id = config.get(CONF_ID)
    device_name = config.get(CONF_NAME)
    timezone = config.get(CONF_TZ)
    ld = lacrosse(device_id, UNIT, timezone or TIME_ZONE)
    _LOGGER.info("Setting up lacrosse alerts for device %s", device_name)
    sensors = await hass.async_add_executor_job(lambda: all_sensors(hass, device_name, device_id, ld))
    add_devices(sensors)


class LaCrosseSensor(SensorEntity):
    """Representation of a LaCrosse Alerts Mobile Sensor."""

    def __init__(self, hass, device_name, device_id, ld):
        """Initialize the sensor."""
        self._hass = hass
        self._lacrosse_device = ld
        self._device_id = device_id
        self._state = None
        name = device_name or "LaCrosse-" + device_id
        self._attr_name = name
        try:
            obs = ld.getObservation(1)[0]
            self._device_info = DeviceInfo(
                identifiers={(DOMAIN, self._device_id)},
                name_by_user=self._attr_name,
                model=obs["device_type"],
                manufacturer="La Crosse",
            )
        except Exception as e:
            _LOGGER.exception("Cannot setup sensor %s", name, exc_info=e)    

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device_info

    def get_latest_observation(self):
        if self._lacrosse_device is None:
            return None        
        return self._lacrosse_device.getObservation(1)


class LaCrosseAmbientSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Ambient_Temp"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "AmbientTemp"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        self._state = measureOrNone(obs[0], "ambient_temp")


class LaCrosseProbeSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Probe_Temp"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "ProbeTemp"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        self._state = measureOrNone(obs[0], "probe_temp")


class LaCrosseHumidSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Ambient_Humidity"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "AmbientHumidity"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:water-percent"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        self._state = measureOrNone(obs[0], "humidity")


class LaCrosseBatterySensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Low_Battery"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "LowBattery"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        meas = measureOrNone(obs[0], "lowbattery")
        if meas is None:
            self._state = None
        else:
            self._state = meas == 1


class LaCrosseSignalSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Signal_Strength"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "SignalStrength"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "dB"

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        self._state = measureOrNone(obs[0], "linkquality")


class LaCrosseUpdateSensor(LaCrosseSensor):
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name + ".Last_Seen_At"

    @property
    def unique_id(self):
        return DOMAIN + self._device_id + "LastSeenAt"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        obs = await self._hass.async_add_executor_job(self.get_latest_observation)
        self._state = datetime.fromtimestamp(obs[0]["utctime"])


def all_sensors(hass, device_name, device_id, ld):
    return [
        LaCrosseAmbientSensor(hass, device_name, device_id, ld),
        LaCrosseProbeSensor(hass, device_name, device_id, ld),
        LaCrosseHumidSensor(hass, device_name, device_id, ld),
        LaCrosseBatterySensor(hass, device_name, device_id, ld),
        LaCrosseSignalSensor(hass, device_name, device_id, ld),
        LaCrosseUpdateSensor(hass, device_name, device_id, ld),
    ]
