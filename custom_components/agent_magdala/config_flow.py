"""Config flow for Agent Magdala Guardian integration."""
import voluptuous as vol
import aiohttp
import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_OPENROUTER_API_KEY,
    CONF_MEM0_API_KEY,
    CONF_OPENROUTER_MODEL,
    CONF_GUARDIAN_MODE,
    CONF_VOICE_ANNOUNCEMENTS,
    CONF_TTS_SERVICE,
    DEFAULT_OPENROUTER_MODEL,
    DEFAULT_GUARDIAN_MODE,
    DEFAULT_VOICE_ANNOUNCEMENTS,
    DEFAULT_TTS_SERVICE,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala Guardian."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate API keys
            validation_errors = await self._validate_api_keys(user_input)
            if validation_errors:
                errors.update(validation_errors)
            else:
                return self.async_create_entry(
                    title="HAOS Agent Magdala Guardian",
                    data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_OPENROUTER_API_KEY): str,
            vol.Required(CONF_MEM0_API_KEY): str,
            vol.Optional(CONF_OPENROUTER_MODEL, default=DEFAULT_OPENROUTER_MODEL): str,
            vol.Optional(CONF_GUARDIAN_MODE, default=DEFAULT_GUARDIAN_MODE): vol.In(["active", "passive", "sleep"]),
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

    async def _validate_api_keys(self, user_input: dict) -> dict:
        """Validate the provided API keys."""
        errors = {}
        session = async_get_clientsession(self.hass)

        # Validate OpenRouter API key
        try:
            headers = {
                "Authorization": f"Bearer {user_input[CONF_OPENROUTER_API_KEY]}",
                "Content-Type": "application/json"
            }

            async with session.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    errors[CONF_OPENROUTER_API_KEY] = "invalid_api_key"

        except Exception as e:
            _LOGGER.error(f"Error validating OpenRouter API key: {e}")
            errors[CONF_OPENROUTER_API_KEY] = "connection_error"

        # Validate Mem0 API key
        try:
            headers = {
                "Authorization": f"Bearer {user_input[CONF_MEM0_API_KEY]}",
                "Content-Type": "application/json"
            }

            async with session.get(
                "https://api.mem0.ai/v1/memories",
                headers=headers,
                params={"limit": 1},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status not in [200, 404]:  # 404 is OK if no memories exist
                    errors[CONF_MEM0_API_KEY] = "invalid_api_key"

        except Exception as e:
            _LOGGER.error(f"Error validating Mem0 API key: {e}")
            errors[CONF_MEM0_API_KEY] = "connection_error"

        return errors

    async def async_step_options(self, user_input=None):
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
            step_id="options",
            data_schema=options_schema
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ConfigFlow()