import logging
import asyncio
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from .meshcentral_websocket import connect_websocket
from homeassistant.const import CONF_URL
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .services import setup_services


_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["binary_sensor", "sensor"]

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('url', default='localhost:5222'): cv.string,
        vol.Required('username', default='admin'): cv.string,
        vol.Required('password'): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Connecting to WebSocket")
    hass.loop.create_task(connect_websocket(hass, entry.data.get('url', 'localhost:5222'), entry.data.get('username', 'admin'), entry.data.get('password'), entry.data.get('ssl', True)))

    _LOGGER.info("Setting up Platforms")
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor", "sensor"])
    
    while hass.data.get(DOMAIN) is None:
        await asyncio.sleep(1)

    websocket = hass.data[DOMAIN]['websocket']
    send_command = hass.data[DOMAIN]['websocket_send_command']
    await send_command(websocket, "nodes")

    await setup_services(hass, websocket, send_command)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Unload the integration
    hass.data.pop(DOMAIN, None)
    return True