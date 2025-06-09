"""Config flow for Agent Magdala."""
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY

from .const import (
    DOMAIN,
    LOGGER,
    CONF_OPENROUTER_API_KEY,
    CONF_PERPLEXITY_API_KEY,
    CONF_OPENROUTER_MODEL,
    DEFAULT_OPENROUTER_MODEL,
)

class AgentMagdalaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # For simplicity, we're not validating the keys against the APIs here,
            # but a real implementation should to provide better user feedback.
            # We'll just ensure they are not empty.
            if not user_input.get(CONF_OPENROUTER_API_KEY):
                errors[CONF_OPENROUTER_API_KEY] = "openrouter_key_empty"
            if not user_input.get(CONF_PERPLEXITY_API_KEY):
                errors[CONF_PERPLEXITY_API_KEY] = "perplexity_key_empty"

            if not errors:
                # Unique ID for the integration. Since we only want one instance,
                # we can use the domain itself.
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="HAOS Agent Magdala",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OPENROUTER_API_KEY): str,
                    vol.Required(CONF_PERPLEXITY_API_KEY): str,
                    vol.Optional(CONF_OPENROUTER_MODEL, default=DEFAULT_OPENROUTER_MODEL): str,
                }
            ),
            errors=errors,
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Agent Magdala."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the config entry with new options
            return self.async_create_entry(title="", data=user_input)

        # Define the options schema, allowing users to change settings after setup
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OPENROUTER_API_KEY,
                    default=self.config_entry.data.get(CONF_OPENROUTER_API_KEY),
                ): str,
                vol.Required(
                    CONF_PERPLEXITY_API_KEY,
                    default=self.config_entry.data.get(CONF_PERPLEXITY_API_KEY),
                ): str,
                vol.Optional(
                    CONF_OPENROUTER_MODEL,
                    default=self.config_entry.data.get(CONF_OPENROUTER_MODEL, DEFAULT_OPENROUTER_MODEL),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)