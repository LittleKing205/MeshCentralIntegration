import logging
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN
from homeassistant.helpers.device_registry import async_get as async_get_device
from homeassistant.helpers.entity_registry import async_get as async_get_entity
from homeassistant.helpers.entity_registry import async_entries_for_device

_LOGGER = logging.getLogger(__name__)

async def setup_services(hass: HomeAssistant, websocket, send_command):
    _LOGGER.info("Setting up Services")

    async def handle_power(call: ServiceCall):
        device = call.data.get("device")
        mode = call.data.get("mode")

        device_registry = async_get_device(hass)
        entity_registry = async_get_entity(hass)

        # Lade Device
        device_entry = device_registry.async_get(device)

        if device_entry:
            entities = async_entries_for_device(entity_registry, device_entry.id)
            
            if entities:
                entity = hass.states.get(entities[0].entity_id)
            else:
                _LOGGER.error(f"No entities found for device {device}")
        else:
            _LOGGER.error(f"Device with ID {device} not found")

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

    async def handle_notify(call: ServiceCall):
        device = call.data.get("device")
        message = call.data.get("message")
        title = call.data.get("title", "HomeAssistant")

        device_registry = async_get_device(hass)
        entity_registry = async_get_entity(hass)

        # Lade Device
        device_entry = device_registry.async_get(device)

        if device_entry:
            entities = async_entries_for_device(entity_registry, device_entry.id)
            
            if entities:
                entity = hass.states.get(entities[0].entity_id)
            else:
                _LOGGER.error(f"No entities found for device {device}")
        else:
            _LOGGER.error(f"Device with ID {device} not found")


        if entity:
            node_id = entity.attributes.get("node_id")
            if node_id is not None:
                name = entity.attributes.get("name")
                await send_command(websocket, "msg", {
                    'msg': message,
                    'title': title,
                    'type': 'messagebox',
                    'nodeid': node_id
                })

    hass.services.async_register(DOMAIN, "power", handle_power, schema=vol.Schema({
        vol.Required("device"): cv.string,
        vol.Required("mode"): cv.string
    }))

    hass.services.async_register(DOMAIN, "notify", handle_notify, schema=vol.Schema({
        vol.Required("device"): cv.string,
        vol.Required("message"): cv.string,
        vol.Required('title', default='HomeAssistant'): cv.string
    }))
