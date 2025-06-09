"""Config flow for Agent Magdala integration."""
import voluptuous as vol

from homeassistant import config_entries

DOMAIN = "agent_magdala"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                title="HAOS Agent Magdala", 
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required("openrouter_api_key"): str,
            vol.Required("perplexity_api_key"): str,
            vol.Optional("openrouter_model", default="google/gemini-flash-1.5"): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema,
            errors=errors
        )