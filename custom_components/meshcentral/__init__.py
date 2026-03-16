from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PASSWORD,
    CONF_SSL,
    CONF_URL,
    CONF_USERNAME,
    DATA_CLIENT,
    DATA_REGISTERED_BATTERY_DEVICES,
    DEFAULT_SSL,
    DOMAIN,
    PLATFORMS,
)
from .meshcentral_websocket import MeshCentralWebSocketClient
from .services import setup_services, unload_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the MeshCentral integration from yaml (not used)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MeshCentral from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    entry_runtime: dict = {
        DATA_REGISTERED_BATTERY_DEVICES: set(),
    }

    entry_config = {**entry.data, **entry.options}

    client = MeshCentralWebSocketClient(
        hass=hass,
        domain=entry_config[CONF_URL],
        username=entry_config[CONF_USERNAME],
        password=entry_config[CONF_PASSWORD],
        ssl_enabled=entry_config.get(CONF_SSL, DEFAULT_SSL),
        registered_battery_devices=entry_runtime[DATA_REGISTERED_BATTERY_DEVICES],
        entry_id=entry.entry_id,
    )
    await client.async_start()

    entry_runtime[DATA_CLIENT] = client
    hass.data[DOMAIN][entry.entry_id] = entry_runtime

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await setup_services(hass, entry.entry_id)

    _LOGGER.info("MeshCentral entry set up: %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    entry_runtime = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if entry_runtime and DATA_CLIENT in entry_runtime:
        await entry_runtime[DATA_CLIENT].async_stop()

    await unload_services(hass)

    _LOGGER.info("MeshCentral entry unloaded: %s", entry.entry_id)
    return True
