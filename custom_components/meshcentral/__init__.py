import logging
import asyncio
from homeassistant.core import HomeAssistant
from .meshcentral_websocket import connect_websocket
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL

_LOGGER = logging.getLogger(__name__)
DOMAIN = "meshcentral"
PLATFORMS = ["binary_sensor", "sensor"]

async def async_setup(hass: HomeAssistant, config):

    _LOGGER.info("Connecting to WebSocket")
    hass.loop.create_task(connect_websocket(hass, config[DOMAIN].get('url', 'localhost:5222'), config[DOMAIN].get('username', 'admin'), config[DOMAIN].get('password'), config[DOMAIN].get('ssl', True)))

    await asyncio.sleep(5)

    _LOGGER.info("Setting up Platforms")
    for platform in PLATFORMS:
        hass.helpers.discovery.load_platform(platform, DOMAIN, {}, config)

    return True
