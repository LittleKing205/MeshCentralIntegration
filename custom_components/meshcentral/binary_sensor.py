import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)
DOMAIN = "meshcentral"
SIGNAL_CREATE_BINARY_SENSOR = "meshcentral_create_binary_sensor"
SIGNAL_UPDATE_BINARY_SENSOR = "meshcentral_update_binary_sensor"

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info: DiscoveryInfoType = None):
    if discovery_info is None:
        return

    _LOGGER.info(f"Setting up MeshCentral binary sensor")

    async def async_add_binary_sensor(devices):
        sensors = []
        for device in devices:
            _LOGGER.info(f"Adding binary_sensor: {device['id']}")
            sensors.append(MeshCentralBinarySensor(device))
        async_add_entities(sensors, True)

    async_dispatcher_connect(hass, SIGNAL_CREATE_BINARY_SENSOR, async_add_binary_sensor)

class MeshCentralBinarySensor(BinarySensorEntity):
    def __init__(self, device):
        self._name = device.get("name", f"Unknown {device['id']}")
        self._device_id = device["id"]
        self._node_id = device.get("node_id", "unknown_node_id")
        self._state = device["state"]
    
    @property
    def name(self):
        return f"{self._name} Power"

    @property
    def is_on(self):
        return self._state

    @property
    def unique_id(self):
        return self._device_id

    @property
    def device_class(self):
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def extra_state_attributes(self):
        return {
            "node_id": self._node_id,
            "name": self._name
        }

    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._name,
            manufacturer="MeshCentral",
            model="MeshCentral",
            sw_version="MeshCentral"
        )

    def update_state(self, state):
        _LOGGER.info(f"Updating state for {self._device_id} to {state}")
        self._state = state
        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        async def async_update_sensor(devices):
            for device in devices:
                if device["id"] == self._device_id:
                    self.update_state(device["state"])
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_BINARY_SENSOR, async_update_sensor)
