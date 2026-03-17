"""MeshCentral node security binary sensors (Battery Charging, WSC, Defender)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    NODE_ID_IDENTIFIER_PREFIX,
    SIGNAL_UPDATE_BATTERY_CHARGING_BINARY_SENSOR,
    SIGNAL_UPDATE_WSC_BINARY_SENSORS,
    SIGNAL_UPDATE_DEFENDER_RTP_BINARY_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


class MeshCentralBatteryChargingSensor(BinarySensorEntity):
    """Represent a MeshCentral battery charging status entity."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._battery_state = device.get("battery_state")
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        self._attr_unique_id = f"{self._device_id}_battery_charging"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Battery Charging"

    @property
    def is_on(self) -> bool:
        return bool(self._state)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "battery_state": self._battery_state,
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
                    self._battery_state = device.get("battery_state")
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE_BATTERY_CHARGING_BINARY_SENSOR, async_update_sensor
            )
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE_BATTERY_CHARGING_BINARY_SENSOR, async_remove_sensor
            )
        )


class MeshCentralWSCBinarySensor(BinarySensorEntity):
    """Represent a MeshCentral Windows Security Center entity."""

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._sensor_type = device.get("sensor_type")  # "firewall", "antivirus", "autoupdate"
        self._state = device.get("state")
        self._wsc_value = device.get("wsc_value")
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        # Set the suffix based on sensor type
        self._attr_unique_id = f"{self._device_id}_wsc_{self._sensor_type}"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        if self._sensor_type == "firewall":
            return "WSC Firewall"
        elif self._sensor_type == "antivirus":
            return "WSC AntiVirus"
        elif self._sensor_type == "autoupdate":
            return "WSC Auto Update"
        return "WSC"

    @property
    def is_on(self) -> bool:
        return bool(self._state)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "wsc_value": self._wsc_value,
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
                if device["id"] == self._device_id and device.get("sensor_type") == self._sensor_type:
                    self._state = device.get("state")
                    self._wsc_value = device.get("wsc_value")
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_WSC_BINARY_SENSORS, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id and device.get("sensor_type") == self._sensor_type:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_WSC_BINARY_SENSORS, async_remove_sensor)
        )


class MeshCentralDefenderRTPSensor(BinarySensorEntity):
    """Represent a MeshCentral Defender Real-Time Protection entity."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, device: dict[str, Any]) -> None:
        self._device_id = device["id"]
        self._name = device.get("name", f"Unknown {self._device_id}")
        self._state = device.get("state")
        self._tamper_protected = device.get("tamper_protected")
        self._antivirus_signature_version = device.get("antivirus_signature_version")
        self._antivirus_signature_last_updated = device.get("antivirus_signature_last_updated")
        self._av_products = device.get("av_products", [])
        self._node_id = device.get("node_id")
        self._entry_id = device.get("entry_id")

        self._attr_unique_id = f"{self._device_id}_defender_rtp"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        return "Defender RTP"

    @property
    def is_on(self) -> bool:
        # For `safety` class, ON means "unsafe" in Home Assistant.
        # MeshCentral reports RealTimeProtection=True when system is protected,
        # so invert it to avoid showing a protected host as unsafe.
        return not bool(self._state)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        av_product_list = []
        for av in self._av_products:
            av_product_list.append(
                {
                    "product": av.get("product"),
                    "enabled": av.get("enabled"),
                    "updated": av.get("updated"),
                }
            )

        return {
            "name": self._name,
            "realtime_protection_enabled": bool(self._state),
            "tamper_protected": self._tamper_protected,
            "antivirus_signature_version": self._antivirus_signature_version,
            "antivirus_signature_last_updated": self._antivirus_signature_last_updated,
            "av_products": av_product_list,
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
                    self._tamper_protected = device.get("tamper_protected")
                    self._antivirus_signature_version = device.get("antivirus_signature_version")
                    self._antivirus_signature_last_updated = device.get("antivirus_signature_last_updated")
                    self._av_products = device.get("av_products", [])
                    if device.get("node_id"):
                        self._node_id = device["node_id"]
                    self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_DEFENDER_RTP_BINARY_SENSOR, async_update_sensor)
        )

        async def async_remove_sensor(devices: list[dict[str, Any]]) -> None:
            for device in devices:
                if device.get("entry_id") not in (None, self._entry_id):
                    continue
                if device["id"] == self._device_id:
                    await self.async_remove(force_remove=True)
                    return

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE_DEFENDER_RTP_BINARY_SENSOR, async_remove_sensor)
        )
