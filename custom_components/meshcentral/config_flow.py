import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

class MeshCentralConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Example integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate and create the config entry
            return self.async_create_entry(title=user_input['url'], data=user_input)

        schema = vol.Schema({
            vol.Required('url', default='localhost:5222'): cv.string,
            vol.Required('username', default='admin'): cv.string,
            vol.Required('password'): cv.string,
            #vol.Optional('ssl', default=True): cv.boolean
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )


async def validate_input(data):
    """Validate the user input allows us to connect."""
    url = data['url']
    username = data['username']
    password = data['password']
    _LOGGER.debug(f"Validate User Input")

    # Beispielcode: Versuche, eine Verbindung herzustellen
    try:
        # Hier implementierst du den Verbindungscheck
        # Zum Beispiel könnte es ein HTTP-Request oder eine andere API-Anfrage sein
        raise CannotConnect
        if not response.success:
            raise ValueError("Invalid credentials")
    except Exception as e:
        raise CannotConnect

    return {"title": "Example Integration"}

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""