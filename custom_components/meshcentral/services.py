from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import DATA_CLIENT, DOMAIN, NODE_ID_IDENTIFIER_PREFIX
from .meshcentral_websocket import MeshCentralWebSocketClient

_LOGGER = logging.getLogger(__name__)

SERVICE_POWER = "power"
SERVICE_NOTIFY = "notify"

_SERVICE_OWNER_ENTRY_ID: str | None = None


def _get_client(hass: HomeAssistant, entry_id: str | None) -> MeshCentralWebSocketClient | None:
    if entry_id is None:
        return None

    entry_runtime = hass.data.get(DOMAIN, {}).get(entry_id)
    if not entry_runtime:
        return None

    return entry_runtime.get(DATA_CLIENT)


def _resolve_node_id(hass: HomeAssistant, device_id: str) -> str | None:
    device_registry = async_get_device_registry(hass)

    device_entry = device_registry.async_get(device_id)
    if not device_entry:
        _LOGGER.error("Device with ID %s not found", device_id)
        return None

    for identifier_domain, identifier_value in device_entry.identifiers:
        if identifier_domain != DOMAIN:
            continue
        if identifier_value.startswith(NODE_ID_IDENTIFIER_PREFIX):
            return identifier_value.removeprefix(NODE_ID_IDENTIFIER_PREFIX)

    _LOGGER.error("No node_id identifier found for device %s", device_id)
    return None


async def setup_services(hass: HomeAssistant, entry_id: str) -> None:
    """Register MeshCentral services."""
    global _SERVICE_OWNER_ENTRY_ID

    if _SERVICE_OWNER_ENTRY_ID is not None:
        return

    async def handle_power(call: ServiceCall) -> None:
        client = _get_client(hass, _SERVICE_OWNER_ENTRY_ID)
        if not client:
            _LOGGER.error("MeshCentral client is unavailable")
            return

        node_id = _resolve_node_id(hass, call.data["device"])
        if not node_id:
            return

        mode = call.data["mode"]
        if mode == "wake":
            await client.async_send_command("wakedevices", {"nodeids": [node_id]})
            return

        action_map = {
            "off": 2,
            "reset": 3,
            "sleep": 4,
        }
        action_type = action_map.get(mode)
        if action_type is None:
            _LOGGER.error("Unsupported power mode: %s", mode)
            return

        await client.async_send_command(
            "poweraction",
            {
                "nodeids": [node_id],
                "actiontype": action_type,
            },
        )

    async def handle_notify(call: ServiceCall) -> None:
        client = _get_client(hass, _SERVICE_OWNER_ENTRY_ID)
        if not client:
            _LOGGER.error("MeshCentral client is unavailable")
            return

        node_id = _resolve_node_id(hass, call.data["device"])
        if not node_id:
            return

        await client.async_send_command(
            "msg",
            {
                "msg": call.data["message"],
                "title": call.data.get("title", "HomeAssistant"),
                "type": "messagebox",
                "nodeid": node_id,
            },
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_POWER,
        handle_power,
        schema=vol.Schema(
            {
                vol.Required("device"): cv.string,
                vol.Required("mode"): vol.In(["wake", "off", "sleep", "reset"]),
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NOTIFY,
        handle_notify,
        schema=vol.Schema(
            {
                vol.Required("device"): cv.string,
                vol.Required("message"): cv.string,
                vol.Optional("title", default="HomeAssistant"): cv.string,
            }
        ),
    )

    _SERVICE_OWNER_ENTRY_ID = entry_id
    _LOGGER.debug("MeshCentral services registered")


async def unload_services(hass: HomeAssistant) -> None:
    """Unregister MeshCentral services."""
    global _SERVICE_OWNER_ENTRY_ID

    if _SERVICE_OWNER_ENTRY_ID is None:
        return

    hass.services.async_remove(DOMAIN, SERVICE_POWER)
    hass.services.async_remove(DOMAIN, SERVICE_NOTIFY)
    _SERVICE_OWNER_ENTRY_ID = None
    _LOGGER.debug("MeshCentral services unregistered")
