"""Custom integration for Agent Magdala."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
    SERVICE_ASK_AGENT,
    ATTR_PROMPT,
    ATTR_CONVERSATION_ID,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Agent Magdala integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Agent Magdala from a config entry."""
    _LOGGER.info(STARTUP_MESSAGE)

    # Store config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register the service
    async def handle_ask_service(call: ServiceCall):
        """Handle the service call to ask the agent a question."""
        prompt = call.data.get(ATTR_PROMPT)
        conversation_id = call.data.get(ATTR_CONVERSATION_ID)

        if not prompt:
            _LOGGER.error("Service call 'ask' is missing required attribute 'prompt'")
            return

        # Temporary response while we fix dependencies
        _LOGGER.info(f"Agent received prompt: {prompt}")
        hass.bus.async_fire(
            f"{DOMAIN}_response",
            {"response": "Agent is temporarily offline while dependencies are being fixed.", "conversation_id": conversation_id},
        )

    hass.services.async_register(
        DOMAIN, SERVICE_ASK_AGENT, handle_ask_service
    )

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister the service
    hass.services.async_remove(DOMAIN, SERVICE_ASK_AGENT)

    # Clean up stored data
    hass.data[DOMAIN].pop(entry.entry_id)

    return True