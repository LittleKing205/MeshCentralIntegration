from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_CREATE_BATTERY_SENSOR, SIGNAL_UPDATE_BATTERY_SENSOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up MeshCentral battery sensors from config entry."""

    async def async_add_battery_sensor(devices: list[dict[str, Any]]) -> None:
        sensors = [MeshCentralBatterySensor(device) for device in devices]
        if sensors:
            async_add_entities(sensors, True)

    async_dispatcher_connect(hass, SIGNAL_CREATE_BATTERY_SENSOR, async_add_battery_sensor)
    _LOGGER.debug("MeshCentral battery sensor dispatcher connected")


class MeshCentralBatterySensor(SensorEntity):
    """Represent a MeshCentral battery entity."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._node_id = device.get("node_id", "unknown_node_id")

        self._attr_unique_id = f"{self._device_id}_battery"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Battery"

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {
            "node_id": self._node_id,
            "name": self._name,
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._name,
        )

    async def async_added_to_hass(self) -> None:
        async def async_update_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device["id"] == self._device_id:
                    self._state = device.get("state")
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_BATTERY_SENSOR, async_update_sensor)
        )
