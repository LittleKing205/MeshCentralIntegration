from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_PASSWORD,
    CONF_SSL,
    CONF_URL,
    CONF_USERNAME,
    DEFAULT_SSL,
    DEFAULT_URL,
    DEFAULT_USERNAME,
    DOMAIN,
)


class MeshCentralConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeshCentral."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_URL])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_URL], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=DEFAULT_URL): str,
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_SSL, default=DEFAULT_SSL): bool,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return options flow handler."""
        return MeshCentralOptionsFlow(config_entry)


class MeshCentralOptionsFlow(config_entries.OptionsFlow):
    """Handle options for MeshCentral."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=current.get(CONF_URL, DEFAULT_URL)): str,
                    vol.Required(CONF_USERNAME, default=current.get(CONF_USERNAME, DEFAULT_USERNAME)): str,
                    vol.Required(CONF_PASSWORD, default=current.get(CONF_PASSWORD, "")): str,
                    vol.Optional(CONF_SSL, default=current.get(CONF_SSL, DEFAULT_SSL)): bool,
                }
            ),
        )
