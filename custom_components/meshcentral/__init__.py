import logging
import asyncio
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from .meshcentral_websocket import connect_websocket
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
DOMAIN = "meshcentral"
PLATFORMS = ["binary_sensor", "sensor"]

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('url', default='localhost:5222'): cv.string,
        vol.Required('username', default='admin'): cv.string,
        vol.Required('password'): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType):

    _LOGGER.info("Connecting to WebSocket")
    hass.loop.create_task(connect_websocket(hass, config[DOMAIN].get('url', 'localhost:5222'), config[DOMAIN].get('username', 'admin'), config[DOMAIN].get('password'), config[DOMAIN].get('ssl', True)))

    _LOGGER.info("Setting up Platforms")
    for platform in PLATFORMS:
        await hass.helpers.discovery.async_load_platform(platform, DOMAIN, {}, config)
        
    while hass.data.get(DOMAIN) is None:
        await asyncio.sleep(1)

    websocket = hass.data[DOMAIN]['websocket']
    send_command = hass.data[DOMAIN]['websocket_send_command']
    await send_command(websocket, "nodes")

    _LOGGER.info("Setting up Services")
    async def handle_power(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        mode = call.data.get("mode")

        entity = hass.states.get(entity_id)
        if entity:
            node_id = entity.attributes.get("node_id")
            if node_id is not None:
                name = entity.attributes.get("name")
                match mode:
                    case "wake":
                        await send_command(websocket, 'wakedevices', {'nodeids': [node_id]})
                    case "off":
                        await send_command(websocket, 'poweraction', {'nodeids': [node_id], 'actiontype': 2})
                    case "reset":
                        await send_command(websocket, 'poweraction', {'nodeids': [node_id], 'actiontype': 3})
                    case "sleep":
                        await send_command(websocket, 'poweraction', {'nodeids': [node_id], 'actiontype': 4})
                _LOGGER.debug(f"Turning device ({name}) into mode '{mode}' with node_id: {node_id}")

    async def handle_notify(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        message = call.data.get("message")
        title = call.data.get("title", "HomeAssistant")

        entity = hass.states.get(entity_id)
        if entity:
            node_id = entity.attributes.get("node_id")
            if node_id is not None:
                name = entity.attributes.get("name")
                _LOGGER.debug(f"Sending Notification to ({name}) with node_id: {node_id}")
                await send_command(websocket, "msg", {
                    'msg': message,
                    'title': title,
                    'type': 'messagebox',
                    'nodeid': node_id
                })

    hass.services.async_register(DOMAIN, "power", handle_power, schema=vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("mode"): cv.string
    }))

    hass.services.async_register(DOMAIN, "notify", handle_notify, schema=vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("message"): cv.string,
        vol.Required('title', default='HomeAssistant'): cv.string
    }))

    return True
