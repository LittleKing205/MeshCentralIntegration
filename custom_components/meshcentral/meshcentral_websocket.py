import asyncio
import base64
import json
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    RECONNECT_DELAY_SECONDS,
    SIGNAL_CREATE_BATTERY_SENSOR,
    SIGNAL_CREATE_BINARY_SENSOR,
    SIGNAL_UPDATE_BATTERY_SENSOR,
    SIGNAL_UPDATE_BINARY_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

IGNORED_EVENTS = {
    "wakedevices",
    "changenode",
    "wssessioncount",
    "servertimelinestats",
    "ifchange",
    "sysinfohash",
    "accountchange",
    "loginTokenAdded",
    "login",
    "logout",
    "agentlog",
    "recording",
    "relaylog",
}
IGNORED_ACTIONS = {"serverinfo", "userinfo", "plugin"}


class MeshCentralWebSocketClient:
    """Manage a persistent websocket connection to MeshCentral."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        username: str,
        password: str,
        ssl_enabled: bool,
        registered_battery_devices: set[str],
        entry_id: str | None = None,
    ) -> None:
        self.hass = hass
        self._domain = domain
        self._username = username
        self._password = password
        self._ssl_enabled = ssl_enabled
        self._registered_battery_devices = registered_battery_devices
        self._entry_id = entry_id

        self._session: aiohttp.ClientSession | None = None
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._worker_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._connected_event = asyncio.Event()
        self._connect_lock = asyncio.Lock()
        self._cached_devices: dict[str, dict[str, Any]] = {}

    async def async_start(self) -> None:
        """Start websocket background worker."""
        if self._worker_task and not self._worker_task.done():
            return

        self._stop_event.clear()
        self._session = aiohttp.ClientSession()
        self._worker_task = self.hass.async_create_task(self._run())

    async def async_stop(self) -> None:
        """Stop websocket background worker and close resources."""
        self._stop_event.set()
        self._connected_event.clear()

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        if self._session and not self._session.closed:
            await self._session.close()

        self._websocket = None
        self._worker_task = None
        self._session = None

    async def async_reconnect(self) -> None:
        """Force the current websocket to reconnect."""
        _LOGGER.warning("Websocket reconnect requested")
        self._connected_event.clear()
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

    async def async_send_command(self, action: str, extra_data: dict[str, Any] | None = None) -> None:
        """Send a command to MeshCentral over websocket."""
        if not self._websocket or self._websocket.closed:
            raise RuntimeError("MeshCentral websocket is not connected")

        command_data: dict[str, Any] = {"action": action, "type": "json"}
        if extra_data:
            command_data.update(extra_data)

        await self._websocket.send_str(json.dumps(command_data))
        _LOGGER.debug("Sent command '%s'", action)

    def get_cached_devices(self) -> list[dict[str, Any]]:
        """Return list of cached devices."""
        return list(self._cached_devices.values())

    async def _run(self) -> None:
        """Keep websocket connected until stopped."""
        while not self._stop_event.is_set():
            try:
                await self._connect_and_consume()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Unexpected websocket loop error: %s", err)

            if self._stop_event.is_set():
                break

            _LOGGER.warning("Websocket disconnected. Reconnecting in %s seconds", RECONNECT_DELAY_SECONDS)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)

    async def _connect_and_consume(self) -> None:
        """Connect once and consume messages until disconnect."""
        if not self._session:
            return

        url, headers = generate_url_header(
            domain=self._domain,
            ssl_enabled=self._ssl_enabled,
            username=self._username,
            password=self._password,
        )

        async with self._connect_lock:
            async with self._session.ws_connect(url, headers=headers) as websocket:
                self._websocket = websocket
                self._connected_event.set()
                _LOGGER.info("Connected to %s", url)

                await self.async_send_command("nodes")

                async for msg in websocket:
                    if self._stop_event.is_set():
                        break
                    await self._handle_message(msg)

        self._connected_event.clear()
        self._websocket = None

    async def _handle_message(self, msg: aiohttp.WSMessage) -> None:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await self._handle_text_message(msg.data)
            return

        if msg.type == aiohttp.WSMsgType.ERROR:
            _LOGGER.error("WebSocket connection error")
            await self.async_reconnect()
            return

        if msg.type == aiohttp.WSMsgType.CLOSED:
            _LOGGER.warning("WebSocket connection closed")
            await self.async_reconnect()

    async def _handle_text_message(self, payload: str) -> None:
        try:
            message_data = json.loads(payload)
        except json.JSONDecodeError:
            _LOGGER.error("Received invalid JSON: %s", payload)
            return

        action = message_data.get("action")
        if action in {"traceinfo", "wakedevices", "poweraction", "msg"}:
            return

        if action == "event":
            event_data = message_data.get("event")
            if event_data:
                await process_event(self.hass, event_data, self._registered_battery_devices, self._entry_id)
            return

        if action and message_data.get("type") == "json":
            action_data = json.loads(message_data.get("data", "{}"))
            await process_action(self.hass, action, action_data, self._entry_id)
            return

        if action and action in message_data:
            await process_action(self.hass, action, message_data[action], self._entry_id)


def generate_url_header(
    domain: str,
    ssl_enabled: bool,
    username: str,
    password: str,
    token: str | None = None,
) -> tuple[str, dict[str, str]]:
    scheme = "wss" if ssl_enabled else "ws"
    url = f"{scheme}://{domain}/control.ashx"

    username_b64 = base64.b64encode(username.encode()).decode()
    password_b64 = base64.b64encode(password.encode()).decode()

    if token:
        token_b64 = base64.b64encode(token.encode()).decode()
        header_token = f"{username_b64},{password_b64},{token_b64}"
    else:
        header_token = f"{username_b64},{password_b64}"

    return url, {"x-meshauth": header_token}


def parse_nodeid(nodeid: str) -> str:
    nodeid = nodeid.replace("@", "")
    nodeid = nodeid.replace("$", "")
    if nodeid.startswith("node//"):
        nodeid = nodeid[len("node//") :]
    return nodeid


async def process_event(hass: HomeAssistant, event_data: dict[str, Any], registered_battery_devices: set[str], entry_id: str | None = None) -> None:
    action = event_data.get("action")
    if not action or action in IGNORED_EVENTS:
        return

    if action == "nodeconnect":
        handle_event_nodeconnect(hass, event_data, entry_id)
        return

    if action == "devicesessions":
        await handle_event_devicesessions(hass, event_data, registered_battery_devices, entry_id)
        return

    _LOGGER.debug("Unknown event type: %s", action)


async def process_action(hass: HomeAssistant, action: str, action_data: Any, entry_id: str | None = None) -> None:
    if action in IGNORED_ACTIONS:
        return

    if action == "nodes":
        handle_action_nodes(hass, action_data, entry_id)
        return

    _LOGGER.debug("Unknown action type: %s", action)


def handle_action_nodes(hass: HomeAssistant, groups: dict[str, list[dict[str, Any]]], entry_id: str | None = None) -> None:
    devices: list[dict[str, Any]] = []

    for group in groups.values():
        for node in group:
            device_id = parse_nodeid(node["_id"])
            power = bool(node.get("pwr") == 1)
            name = node.get("name", f"Unknown {device_id}")
            devices.append(
                {
                    "id": device_id,
                    "name": name,
                    "state": power,
                    "node_id": node["_id"],
                    "entry_id": entry_id,
                }
            )

    async_dispatcher_send(hass, SIGNAL_CREATE_BINARY_SENSOR, devices)


def handle_event_nodeconnect(
    hass: HomeAssistant,
    event_data: dict[str, Any],
    entry_id: str | None = None,
) -> None:
    device_id = parse_nodeid(event_data["nodeid"])
    power = bool(event_data.get("pwr") == 1)
    device = {
        "id": device_id,
        "state": power,
        "node_id": event_data["nodeid"],
        "entry_id": entry_id,
    }
    async_dispatcher_send(hass, SIGNAL_UPDATE_BINARY_SENSOR, [device])


async def handle_event_devicesessions(
    hass: HomeAssistant,
    event_data: dict[str, Any],
    registered_battery_devices: set[str],
    entry_id: str | None = None,
) -> None:
    device_id = parse_nodeid(event_data["nodeid"])

    battery = event_data.get("sessions", {}).get("battery", {}).get("level")
    if battery is None:
        return

    entity_registry = er.async_get(hass)
    entity_id_power = entity_registry.async_get_entity_id("binary_sensor", DOMAIN, f"{device_id}_power")

    if not entity_id_power:
        return

    power_entity_state = hass.states.get(entity_id_power)
    if power_entity_state is None:
        return

    device_name = power_entity_state.attributes.get("name", f"Unknown {device_id}")

    device = {
        "id": device_id,
        "name": device_name,
        "state": battery,
        "node_id": event_data["nodeid"],
        "entry_id": entry_id,
    }

    if device_id in registered_battery_devices:
        async_dispatcher_send(hass, SIGNAL_UPDATE_BATTERY_SENSOR, [device])
        return

    registered_battery_devices.add(device_id)
    async_dispatcher_send(hass, SIGNAL_CREATE_BATTERY_SENSOR, [device])
