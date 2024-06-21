import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "meshcentral"
SIGNAL_CREATE_BATTERY_SENSOR = "meshcentral_create_battery_sensor"
SIGNAL_UPDATE_BATTERY_SENSOR = "meshcentral_update_battery_sensor"

async def async_setup_platform(hass: HomeAssistantType, config: ConfigType, async_add_entities, discovery_info: DiscoveryInfoType = None):
    if discovery_info is None:
        return

    _LOGGER.info(f"Setting up MeshCentral battery sensor")
    send_command = hass.data[DOMAIN]['websocket_send_command']

    async def async_add_battery_sensor(devices):
        sensors = []
        for device in devices:
            _LOGGER.info(f"Adding sensor: {device['id']}")
            sensors.append(MeshCentralBatterySensor(device))
        async_add_entities(sensors, True)

    async_dispatcher_connect(hass, SIGNAL_CREATE_BATTERY_SENSOR, async_add_battery_sensor)

class MeshCentralBatterySensor(SensorEntity):
    def __init__(self, device):
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {device['id']}")
        self._state = device["state"]
        self._node_id = device.get("node_id", "unknown_node_id")
    
    @property
    def name(self):
        return f"{self._name} Battery"

    @property
    def native_value(self):
        return self._state

    @property
    def unique_id(self):
        return self._device_id

    @property
    def device_class(self):
        return SensorDeviceClass.BATTERY

    @property
    def native_unit_of_measurement(self):
        return "%"

    @property
    def extra_state_attributes(self):
        return {
            "node_id": self._node_id,
            "name": self._name
        }

    def update_state(self, state):
        _LOGGER.info(f"Updating state for {self._device_id} to {state}")
        self._state = state
        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        async def async_update_sensor(devices):
            for device in devices:
                if device["id"] == self._device_id:
                    self.update_state(device["state"])
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_BATTERY_SENSOR, async_update_sensor)
