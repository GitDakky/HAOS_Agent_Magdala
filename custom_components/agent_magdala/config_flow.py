"""Config flow for Agent Magdala Guardian integration."""
import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import callback

# Use string constants directly to avoid import issues
DOMAIN = "agent_magdala"
CONF_OPENROUTER_API_KEY = "openrouter_api_key"
CONF_MEM0_API_KEY = "mem0_api_key"
CONF_OPENROUTER_MODEL = "openrouter_model"
CONF_GUARDIAN_MODE = "guardian_mode"
CONF_VOICE_ANNOUNCEMENTS = "voice_announcements"
CONF_TTS_SERVICE = "tts_service"

DEFAULT_OPENROUTER_MODEL = "google/gemini-flash-1.5"
DEFAULT_GUARDIAN_MODE = True
DEFAULT_VOICE_ANNOUNCEMENTS = True
DEFAULT_TTS_SERVICE = "tts.piper"

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala Guardian."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Basic validation - just check if OpenRouter API key is provided
            if not user_input.get(CONF_OPENROUTER_API_KEY):
                errors[CONF_OPENROUTER_API_KEY] = "required"
            else:
                # Skip API validation for now to avoid setup issues
                return self.async_create_entry(
                    title="HAOS Agent Magdala Guardian",
                    data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_OPENROUTER_API_KEY): str,
            vol.Optional(CONF_MEM0_API_KEY, default=""): str,
            vol.Optional(CONF_OPENROUTER_MODEL, default=DEFAULT_OPENROUTER_MODEL): str,
            vol.Optional(CONF_GUARDIAN_MODE, default="active"): vol.In(["active", "passive", "sleep"]),
            vol.Optional(CONF_VOICE_ANNOUNCEMENTS, default=DEFAULT_VOICE_ANNOUNCEMENTS): bool,
            vol.Optional(CONF_TTS_SERVICE, default=DEFAULT_TTS_SERVICE): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "openrouter_info": "Get your API key from https://openrouter.ai/",
                "mem0_info": "Get your API key from https://mem0.ai/",
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Agent Magdala Guardian."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_GUARDIAN_MODE,
                default=self.config_entry.options.get(CONF_GUARDIAN_MODE, DEFAULT_GUARDIAN_MODE)
            ): vol.In(["active", "passive", "sleep"]),
            vol.Optional(
                CONF_VOICE_ANNOUNCEMENTS,
                default=self.config_entry.options.get(CONF_VOICE_ANNOUNCEMENTS, DEFAULT_VOICE_ANNOUNCEMENTS)
            ): bool,
            vol.Optional(
                CONF_TTS_SERVICE,
                default=self.config_entry.options.get(CONF_TTS_SERVICE, DEFAULT_TTS_SERVICE)
            ): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )