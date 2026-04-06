"""Config flow for TP-Link Router 5G integration."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_VERIFY_SSL
from homeassistant.data_entry_flow import AbortFlow, FlowResultType

from .api import TPLinkRouter5GAPI
from .const import DEFAULT_NAME, DOMAIN, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

def _user_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Optional(CONF_USERNAME, default=defaults.get(CONF_USERNAME, "user")): str,
            vol.Required(CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, "")): str,
            vol.Required(CONF_SCAN_INTERVAL, default=defaults.get(CONF_SCAN_INTERVAL, 30)): int,
            vol.Required(CONF_VERIFY_SSL, default=defaults.get(CONF_VERIFY_SSL, False)): bool,
        }
    )

async def _validate_credentials(user_input: dict) -> None:
    api = TPLinkRouter5GAPI(
        user_input[CONF_HOST],
        user_input.get(CONF_USERNAME),
        user_input[CONF_PASSWORD],
        user_input.get(CONF_VERIFY_SSL, False)
    )
    await api.login()
    await api.logout()

class TPLinkRouter5GConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}
        if user_input is not None:
            try:
                await _validate_credentials(user_input)
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={},
                    options=user_input,
                )
            except AbortFlow:
                raise
            except Exception as e:
                _LOGGER.error("Setup failed: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(entry):
        return TPLinkRouter5GOptionsFlow(entry)

class TPLinkRouter5GOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await _validate_credentials(user_input)
                updated_options = dict(self._entry.options)
                updated_options.update(user_input)
                return self.async_create_entry(title="", data=updated_options)
            except Exception as e:
                _LOGGER.error("Update failed: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="init",
            data_schema=_user_schema(self._entry.options),
            errors=errors,
        )
