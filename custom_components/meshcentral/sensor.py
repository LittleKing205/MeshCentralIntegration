from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send

from .const import (
    DOMAIN,
    NODE_ID_IDENTIFIER_PREFIX,
    SIGNAL_CREATE_BATTERY_SENSOR,
    SIGNAL_REMOVE_BATTERY_SENSOR,
    SIGNAL_UPDATE_BATTERY_SENSOR,
    SIGNAL_CREATE_LAST_BOOT_SENSOR,
    SIGNAL_REMOVE_LAST_BOOT_SENSOR,
    SIGNAL_CREATE_LOGGED_IN_USERS_SENSOR,
    SIGNAL_REMOVE_LOGGED_IN_USERS_SENSOR,
    SIGNAL_CREATE_IP_SENSOR,
    SIGNAL_REMOVE_IP_SENSOR,
)
from .node_info_sensor import (
    MeshCentralLastBootSensor,
    MeshCentralLoggedInUsersSensor,
    MeshCentralIPSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up MeshCentral sensors from config entry."""
    
    # Battery Sensor
    battery_known_device_ids: set[str] = set()

    async def async_add_battery_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in battery_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in battery_known_device_ids]

        sensors = [MeshCentralBatterySensor(device) for device in new_devices]
        battery_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_BATTERY_SENSOR, async_add_battery_sensor)
    )

    async def async_remove_battery_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                battery_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_BATTERY_SENSOR, async_remove_battery_sensor)
    )

    # Last Boot Sensor
    last_boot_known_device_ids: set[str] = set()

    async def async_add_last_boot_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in last_boot_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in last_boot_known_device_ids]

        sensors = [MeshCentralLastBootSensor(device) for device in new_devices]
        last_boot_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_LAST_BOOT_SENSOR, async_add_last_boot_sensor)
    )

    async def async_remove_last_boot_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                last_boot_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_LAST_BOOT_SENSOR, async_remove_last_boot_sensor)
    )

    # Logged-in Users Sensor
    logged_in_users_known_device_ids: set[str] = set()

    async def async_add_logged_in_users_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in logged_in_users_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in logged_in_users_known_device_ids]

        sensors = [MeshCentralLoggedInUsersSensor(device) for device in new_devices]
        logged_in_users_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_LOGGED_IN_USERS_SENSOR, async_add_logged_in_users_sensor)
    )

    async def async_remove_logged_in_users_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                logged_in_users_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_LOGGED_IN_USERS_SENSOR, async_remove_logged_in_users_sensor)
    )

    # IP Sensor
    ip_known_device_ids: set[str] = set()

    async def async_add_ip_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in ip_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in ip_known_device_ids]

        sensors = [MeshCentralIPSensor(device) for device in new_devices]
        ip_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_IP_SENSOR, async_add_ip_sensor)
    )

    async def async_remove_ip_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                ip_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_IP_SENSOR, async_remove_ip_sensor)
    )

    _LOGGER.debug("MeshCentral sensor dispatcher connected")


class MeshCentralBatterySensor(SensorEntity):
    """Represent a MeshCentral battery entity."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

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
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_BATTERY_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_REMOVE_BATTERY_SENSOR, async_remove_sensor)
        )
