from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send

from .const import (
    DOMAIN,
    NODE_ID_IDENTIFIER_PREFIX,
    SIGNAL_CREATE_BINARY_SENSOR,
    SIGNAL_REMOVE_BINARY_SENSOR,
    SIGNAL_UPDATE_BINARY_SENSOR,
    SIGNAL_CREATE_BATTERY_CHARGING_BINARY_SENSOR,
    SIGNAL_REMOVE_BATTERY_CHARGING_BINARY_SENSOR,
    SIGNAL_CREATE_WSC_BINARY_SENSORS,
    SIGNAL_REMOVE_WSC_BINARY_SENSORS,
    SIGNAL_CREATE_DEFENDER_RTP_BINARY_SENSOR,
    SIGNAL_REMOVE_DEFENDER_RTP_BINARY_SENSOR,
)
from .node_security_binary_sensor import (
    MeshCentralBatteryChargingSensor,
    MeshCentralWSCBinarySensor,
    MeshCentralDefenderRTPSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up MeshCentral binary sensors from config entry."""
    
    # Power binary sensor
    power_known_device_ids: set[str] = set()

    async def async_add_binary_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in power_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in power_known_device_ids]

        sensors = [MeshCentralBinarySensor(device) for device in new_devices]
        power_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_BINARY_SENSOR, async_add_binary_sensor)
    )

    async def async_remove_binary_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                power_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_BINARY_SENSOR, async_remove_binary_sensor)
    )

    # Battery Charging binary sensor
    battery_charging_known_device_ids: set[str] = set()

    async def async_add_battery_charging_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in battery_charging_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in battery_charging_known_device_ids]

        sensors = [MeshCentralBatteryChargingSensor(device) for device in new_devices]
        battery_charging_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_BATTERY_CHARGING_BINARY_SENSOR, async_add_battery_charging_sensor)
    )

    async def async_remove_battery_charging_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                battery_charging_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_BATTERY_CHARGING_BINARY_SENSOR, async_remove_battery_charging_sensor)
    )

    # WSC binary sensors
    wsc_known_device_ids: set[str] = set()

    async def async_add_wsc_sensors(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        
        new_devices = []
        for device in entry_devices:
            device_key = f"{device['id']}_{device.get('sensor_type')}"
            if device_key not in wsc_known_device_ids:
                new_devices.append(device)

        existing_devices = [d for d in entry_devices if f"{d['id']}_{d.get('sensor_type')}" in wsc_known_device_ids]

        sensors = [MeshCentralWSCBinarySensor(device) for device in new_devices]
        for device in new_devices:
            wsc_known_device_ids.add(f"{device['id']}_{device.get('sensor_type')}")

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_WSC_BINARY_SENSORS, async_add_wsc_sensors)
    )

    async def async_remove_wsc_sensors(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                device_key = f"{device['id']}_{device.get('sensor_type')}"
                wsc_known_device_ids.discard(device_key)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_WSC_BINARY_SENSORS, async_remove_wsc_sensors)
    )

    # Defender RTP binary sensor
    defender_rtp_known_device_ids: set[str] = set()

    async def async_add_defender_rtp_sensor(devices: list[dict[str, Any]]) -> None:
        entry_devices = [
            device for device in devices if device.get("entry_id") == config_entry.entry_id
        ]
        new_devices = [device for device in entry_devices if device["id"] not in defender_rtp_known_device_ids]
        existing_devices = [device for device in entry_devices if device["id"] in defender_rtp_known_device_ids]

        sensors = [MeshCentralDefenderRTPSensor(device) for device in new_devices]
        defender_rtp_known_device_ids.update(device["id"] for device in new_devices)

        if sensors:
            async_add_entities(sensors, True)

        if existing_devices:
            async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, existing_devices)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CREATE_DEFENDER_RTP_BINARY_SENSOR, async_add_defender_rtp_sensor)
    )

    async def async_remove_defender_rtp_sensor(devices: list[dict[str, Any]]) -> None:
        for device in devices:
            if device.get("entry_id") == config_entry.entry_id:
                defender_rtp_known_device_ids.discard(device["id"])

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_REMOVE_DEFENDER_RTP_BINARY_SENSOR, async_remove_defender_rtp_sensor)
    )

    _LOGGER.debug("MeshCentral binary sensor dispatcher connected")


class MeshCentralBinarySensor(BinarySensorEntity):
    """Represent a MeshCentral power state entity."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._node_id = device.get("node_id")
        self._state = bool(device.get("state"))
        self._entry_id = device.get("entry_id")
        self._osdesc = device.get("osdesc")
        self._rname = device.get("rname")
        self._icon = device.get("icon")
        self._ip = device.get("ip")

        self._attr_unique_id = f"{self._device_id}_power"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Power"

    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "osdesc": self._osdesc,
            "rname": self._rname,
            "icon": self._icon,
            "ip": self._ip,
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
                    self._state = bool(device.get("state"))
                    self._osdesc = device.get("osdesc")
                    self._rname = device.get("rname")
                    self._icon = device.get("icon")
                    self._ip = device.get("ip")
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_BINARY_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_REMOVE_BINARY_SENSOR, async_remove_sensor)
        )

