"""Config flow for Agent Magdala."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_OPENROUTER_API_KEY,
    CONF_PERPLEXITY_API_KEY,
    CONF_OPENROUTER_MODEL,
    DEFAULT_OPENROUTER_MODEL,
)

# Schema for user input
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_OPENROUTER_API_KEY): str,
        vol.Required(CONF_PERPLEXITY_API_KEY): str,
        vol.Optional(CONF_OPENROUTER_MODEL, default=DEFAULT_OPENROUTER_MODEL): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate the user input
            if not user_input.get(CONF_OPENROUTER_API_KEY):
                errors[CONF_OPENROUTER_API_KEY] = "openrouter_key_empty"
            if not user_input.get(CONF_PERPLEXITY_API_KEY):
                errors[CONF_PERPLEXITY_API_KEY] = "perplexity_key_empty"

            if not errors:
                # Create a unique ID based on the domain
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="HAOS Agent Magdala",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Agent Magdala."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Define the options schema
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OPENROUTER_API_KEY,
                    default=self.config_entry.data.get(CONF_OPENROUTER_API_KEY, ""),
                ): str,
                vol.Required(
                    CONF_PERPLEXITY_API_KEY,
                    default=self.config_entry.data.get(CONF_PERPLEXITY_API_KEY, ""),
                ): str,
                vol.Optional(
                    CONF_OPENROUTER_MODEL,
                    default=self.config_entry.data.get(
                        CONF_OPENROUTER_MODEL, DEFAULT_OPENROUTER_MODEL
                    ),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""