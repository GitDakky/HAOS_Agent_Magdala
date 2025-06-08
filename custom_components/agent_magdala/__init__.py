"""Custom integration for Agent Magdala."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
    SERVICE_ASK_AGENT,
    ATTR_PROMPT,
    ATTR_CONVERSATION_ID,
)
from .agent import MagdalaAgent

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Agent Magdala integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Agent Magdala from a config entry."""
    _LOGGER.info(STARTUP_MESSAGE)

    # Create and store the agent instance
    agent = MagdalaAgent(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = agent

    # Register the service that the frontend/user will call
    async def handle_ask_service(call: ServiceCall):
        """Handle the service call to ask the agent a question."""
        prompt = call.data.get(ATTR_PROMPT)
        conversation_id = call.data.get(ATTR_CONVERSATION_ID)

        if not prompt:
            _LOGGER.error("Service call 'ask' is missing required attribute 'prompt'")
            return

        # We can run the agent's response logic in a background task
        # so it doesn't block the Home Assistant event loop.
        hass.async_create_task(agent.get_response(prompt, conversation_id))

    hass.services.async_register(
        DOMAIN, SERVICE_ASK_AGENT, handle_ask_service
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister the service
    hass.services.async_remove(DOMAIN, SERVICE_ASK_AGENT)

    # Clean up the agent instance
    hass.data[DOMAIN].pop(entry.entry_id)

    return True