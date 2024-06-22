import logging
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def setup_services(hass: HomeAssistant, websocket, send_command):
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
