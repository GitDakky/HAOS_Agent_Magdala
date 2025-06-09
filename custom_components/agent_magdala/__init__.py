"""Custom integration for Agent Magdala."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.components.http import HomeAssistantView

from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
    SERVICE_ASK_AGENT,
    ATTR_PROMPT,
    ATTR_CONVERSATION_ID,
    NAME,
)
from .agent import MagdalaAgent

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


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

    # Register the custom panel
    await hass.components.panel_custom.async_register_panel(
        frontend_url_path="agent_magdala",
        webcomponent_name="agent-magdala-panel",
        sidebar_title=NAME,
        sidebar_icon="mdi:brain",
        module_url=f"/api/hassio_ingress/{entry.entry_id}/index.html",
        embed_iframe=True,
        require_admin=True,
    )
    
    # Register a view to serve the panel's static files
    hass.http.register_static_path(
        f"/api/hassio_ingress/{entry.entry_id}",
        hass.config.path(f"custom_components/{DOMAIN}/www"),
        cache_headers=False,
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

    # Unregister the panel
    hass.components.panel_custom.async_remove_panel("agent_magdala")

    # Clean up the agent instance
    hass.data[DOMAIN].pop(entry.entry_id)

    return True