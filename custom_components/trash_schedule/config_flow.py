"""Configuration of the municipality and street for each calendar."""
import voluptuous as vol

from homeassistant import config_entries
from .const import DOMAIN

CONF_GMINA_ID = "gmina_id"
CONF_STREET = "street"


class TrashScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            gmina_id = user_input[CONF_GMINA_ID].strip()
            street = user_input[CONF_STREET].strip()
            if not gmina_id or not street:
                return self.async_show_form(
                    step_id="user", data_schema=self._schema(user_input),
                    errors={"base": "invalid_input"}
                )
            await self.async_set_unique_id(f"{gmina_id}:{street.casefold()}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Trash Schedule - {street}",
                data={CONF_GMINA_ID: gmina_id, CONF_STREET: street},
            )
        return self.async_show_form(step_id="user", data_schema=self._schema())

    @staticmethod
    def _schema(defaults=None):
        defaults = defaults or {}
        return vol.Schema({
            vol.Required(CONF_GMINA_ID, default=defaults.get(CONF_GMINA_ID, "")): str,
            vol.Required(CONF_STREET, default=defaults.get(CONF_STREET, "")): str,
        })
