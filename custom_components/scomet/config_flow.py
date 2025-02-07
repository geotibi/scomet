import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class ScometConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Scomet."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Scomet: Administrăm confortul", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                }
            )
        )

    @callback
    def async_get_options_flow(self, config_entry):
        """Get the options flow for this handler."""
        return ScometOptionsFlow(config_entry)


class ScometOptionsFlow(config_entries.OptionsFlow):
    """Handle Scomet options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional("update_interval", default=10): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
