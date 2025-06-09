"""Config flow for Agent Magdala."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

# Use string for DOMAIN to avoid import issues during config flow discovery
DOMAIN = "agent_magdala"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Agent Magdala."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate inputs
            if not user_input.get("openrouter_api_key"):
                errors["openrouter_api_key"] = "openrouter_key_empty"
            if not user_input.get("perplexity_api_key"):
                errors["perplexity_api_key"] = "perplexity_key_empty"
                
            if not errors:
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
                    vol.Required("openrouter_api_key"): str,
                    vol.Required("perplexity_api_key"): str,
                    vol.Optional("openrouter_model", default="google/gemini-flash-1.5"): str,
                }
            ),
            errors=errors,
        )