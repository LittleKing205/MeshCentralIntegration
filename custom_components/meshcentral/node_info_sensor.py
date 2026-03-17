"""MeshCentral node info sensors (Last Boot, Users, IP)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    NODE_ID_IDENTIFIER_PREFIX,
    SIGNAL_UPDATE_LAST_BOOT_SENSOR,
    SIGNAL_UPDATE_LOGGED_IN_USERS_SENSOR,
    SIGNAL_UPDATE_IP_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


class MeshCentralLastBootSensor(SensorEntity):
    """Represent a MeshCentral last boot time entity."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        self._attr_unique_id = f"{self._device_id}_last_boot"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Last Boot"

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {
            "name": self._name,
        }

    @property
    def device_info(self) -> DeviceInfo:
        identifiers = {(DOMAIN, self._device_id)}
        if self._node_id:
            identifiers.add((DOMAIN, f"{NODE_ID_IDENTIFIER_PREFIX}{self._node_id}"))

        return DeviceInfo(
            identifiers=identifiers,
            name=self._name,
        )

    async def async_added_to_hass(self) -> None:
        async def async_update_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    self._state = device.get("state")
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_LAST_BOOT_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_LAST_BOOT_SENSOR, async_remove_sensor)
        )


class MeshCentralLoggedInUsersSensor(SensorEntity):
    """Represent a MeshCentral logged-in users count entity."""

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._users = device.get("users", [])
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        self._attr_unique_id = f"{self._device_id}_logged_in_users"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Logged-in Users"

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "users": self._users,
        }

    @property
    def device_info(self) -> DeviceInfo:
        identifiers = {(DOMAIN, self._device_id)}
        if self._node_id:
            identifiers.add((DOMAIN, f"{NODE_ID_IDENTIFIER_PREFIX}{self._node_id}"))

        return DeviceInfo(
            identifiers=identifiers,
            name=self._name,
        )

    async def async_added_to_hass(self) -> None:
        async def async_update_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    self._state = device.get("state")
                    self._users = device.get("users", [])
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_LOGGED_IN_USERS_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_LOGGED_IN_USERS_SENSOR, async_remove_sensor)
        )


class MeshCentralIPSensor(SensorEntity):
    """Represent a MeshCentral IP address entity."""

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        self._attr_unique_id = f"{self._device_id}_ip"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "IP Address"

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {
            "name": self._name,
        }

    @property
    def device_info(self) -> DeviceInfo:
        identifiers = {(DOMAIN, self._device_id)}
        if self._node_id:
            identifiers.add((DOMAIN, f"{NODE_ID_IDENTIFIER_PREFIX}{self._node_id}"))

        return DeviceInfo(
            identifiers=identifiers,
            name=self._name,
        )

    async def async_added_to_hass(self) -> None:
        async def async_update_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    self._state = device.get("state")
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_IP_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_IP_SENSOR, async_remove_sensor)
        )
