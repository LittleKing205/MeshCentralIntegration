import asyncio
import json
import logging
import base64
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SIGNAL_CREATE_BINARY_SENSOR = "meshcentral_create_binary_sensor"
SIGNAL_UPDATE_BINARY_SENSOR = "meshcentral_update_binary_sensor"
SIGNAL_CREATE_BATTERY_SENSOR = "meshcentral_create_battery_sensor"
SIGNAL_UPDATE_BATTERY_SENSOR = "meshcentral_update_battery_sensor"

IGNORED_EVENTS  = ['wakedevices', 'changenode', 'wssessioncount', 'servertimelinestats', 'ifchange', 'sysinfohash', 'accountchange', 'loginTokenAdded', 'login', 'logout', 'agentlog', "recording", "relaylog"]
IGNORED_ACTIONS = ['serverinfo', 'userinfo', 'plugin']

registered_battery_devices = set()

async def connect_websocket(hass: HomeAssistant, domain, username, password, ssl=True):
    url, headers = generate_url_header(domain, ssl, username, password)
    session = aiohttp.ClientSession()
    
    while True:
        try:
            async with session.ws_connect(url, headers=headers) as websocket:
                _LOGGER.info(f"Connected to {url}")
                hass.data[DOMAIN] = {
                    "websocket": websocket,
                    "websocket_send_command": send_command
                }

                async for msg in websocket:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            message_data = json.loads(msg.data)
                            if 'action' in message_data and message_data['action'] in ['traceinfo', 'wakedevices', 'poweraction', 'msg']:
                                continue
                            elif 'action' in message_data and message_data['action'] == 'event':
                                event_data = message_data.get('event')
                                if event_data:
                                    await process_event(hass, event_data)
                            elif 'action' in message_data and 'type' in message_data and message_data['type'] == 'json':
                                action_data = json.loads(message_data['data'])
                                await process_action(hass, message_data['action'], action_data)
                            elif 'action' in message_data:
                                await process_action(hass, message_data['action'], message_data[message_data['action']])
                        except json.JSONDecodeError:
                            _LOGGER.error(f"Received invalid JSON: {msg.data}")
                        except Exception as e:
                            _LOGGER.error(f"Error processing message: {e}")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        _LOGGER.error("WebSocket connection error")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        _LOGGER.warning("WebSocket connection closed")
                        break
        except aiohttp.ClientConnectionError as e:
            _LOGGER.warning(f"Connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            _LOGGER.error(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def generate_url_header(domain, ssl, username, password, token=None):
    if ssl:
        url = f"wss://{domain}/control.ashx"
    else:
        url = f"ws://{domain}/control.ashx"
    username_b64 = base64.b64encode(username.encode()).decode()
    password_b64 = base64.b64encode(password.encode()).decode()

    if token:
        token_b64 = base64.b64encode(token.encode()).decode()
        header_token = f"{username_b64},{password_b64},{token_b64}"
    else:
        header_token = f"{username_b64},{password_b64}"

    return url, {'x-meshauth': header_token}

async def send_command(websocket, action, extra_data=None):
    command_data = {'action': action, 'type': 'json'}
    if extra_data:
        command_data.update(extra_data)
    
    await websocket.send_str(json.dumps(command_data))
    _LOGGER.info(f"Sent command '{action}'")


###########
#  Helper Functions
###########
def parse_nodeid(nodeid):
    nodeid = nodeid.replace('@', '')
    nodeid = nodeid.replace('$', '')
    if nodeid.startswith('node//'):
        nodeid = nodeid[len('node//'):]
    return nodeid


###########
#  Event Filter
###########
async def process_event(hass: HomeAssistant, event_data):
    action = event_data['action']
    match action:
        case action if action in IGNORED_EVENTS:
            pass
        case 'nodeconnect':
            handle_event_nodeconnect(hass, event_data)
        case 'devicesessions':
            await handle_event_devicesessions(hass, event_data)
        case _:
            _LOGGER.debug(f"Unknown event type: {action}")


###########
#  Actions Filter
###########
async def process_action(hass: HomeAssistant, action, action_data):
    match action:
        case action if action in IGNORED_ACTIONS:
            pass
        case 'nodes':
            handle_action_nodes(hass, action_data)
        case _:
            _LOGGER.debug(f"Unknown action type: {action}")


###########
#  Action functions
###########
def handle_action_nodes(hass: HomeAssistant, groups):
    devices = []
    for group in groups.values():
        for node in group:
            deviceId = parse_nodeid(node['_id'])
            power = 'pwr' in node and node['pwr'] == 1
            name = node['name']
            devices.append({
                "id": deviceId,
                "name": name,
                "state": power,
                "node_id": node['_id']
            })
    async_dispatcher_send(hass, SIGNAL_CREATE_BINARY_SENSOR, devices)


###########
#  Event Functions
###########
def handle_event_nodeconnect(hass: HomeAssistant, event_data):
    deviceId = parse_nodeid(event_data['nodeid'])
    power = 'pwr' in event_data and event_data['pwr'] == 1
    device = {
        "id": deviceId,
        "state": power,
        "node_id": event_data['nodeid']
    }
    async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, [device])

async def handle_event_devicesessions(hass: HomeAssistant, event_data):
    deviceId = parse_nodeid(event_data['nodeid'])
    try:
        battery = event_data['sessions']['battery']['level']
        state = event_data['sessions']['battery']['state']
    except KeyError:
        battery = None
        state = None
        return

    entity_registry = er.async_get(hass)

    entity_id_power = entity_registry.async_get_entity_id("binary_sensor", DOMAIN, deviceId)
    entity_id_battery = entity_registry.async_get_entity_id("sensor", DOMAIN, deviceId)
    deviceName = hass.states.get(entity_id_power).attributes["name"]
    device = {
        "id": deviceId,
        "name": deviceName,
        "state": battery,
        "node_id": event_data['nodeid']
    }
    if deviceId in registered_battery_devices:
        async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, [device])
    else:
        registered_battery_devices.add(deviceId)
        async_dispatcher_send(hass, SIGNAL_CREATE_BATTERY_SENSOR, [device])