"""Custom integration for Agent Magdala Guardian System."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
    SERVICE_ASK_AGENT,
    SERVICE_GUARDIAN_MODE,
    SERVICE_ANNOUNCE,
    SERVICE_LEARN_PATTERN,
    ATTR_PROMPT,
    ATTR_CONVERSATION_ID,
    ATTR_MODE,
    ATTR_MODULES,
    ATTR_MESSAGE,
    ATTR_PRIORITY,
    ATTR_LOCATION,
    ATTR_PATTERN_TYPE,
    ATTR_PATTERN_DATA,
    GUARDIAN_MODULES,
    PLATFORMS,
)

from .agent import GuardianAgent

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Service schemas
SERVICE_ASK_SCHEMA = vol.Schema({
    vol.Required(ATTR_PROMPT): cv.string,
    vol.Optional(ATTR_CONVERSATION_ID): cv.string,
})

SERVICE_GUARDIAN_MODE_SCHEMA = vol.Schema({
    vol.Required(ATTR_MODE): vol.In(["active", "passive", "sleep"]),
    vol.Optional(ATTR_MODULES): vol.All(cv.ensure_list, [vol.In(GUARDIAN_MODULES)]),
})

SERVICE_ANNOUNCE_SCHEMA = vol.Schema({
    vol.Required(ATTR_MESSAGE): cv.string,
    vol.Optional(ATTR_PRIORITY, default="low"): vol.In(["low", "medium", "high", "critical"]),
    vol.Optional(ATTR_LOCATION): cv.string,
})

SERVICE_LEARN_PATTERN_SCHEMA = vol.Schema({
    vol.Required(ATTR_PATTERN_TYPE): cv.string,
    vol.Required(ATTR_PATTERN_DATA): dict,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Agent Magdala integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Agent Magdala Guardian from a config entry."""
    _LOGGER.info(STARTUP_MESSAGE)

    # Initialize the Guardian Agent
    try:
        guardian_agent = GuardianAgent(hass, entry)

        # Store the agent instance
        hass.data[DOMAIN][entry.entry_id] = {
            "agent": guardian_agent,
            "config": entry.data
        }

        # Initialize the agent (this will be simplified for now)
        await guardian_agent.initialize_basic()

        # Register services with the actual agent
        await _register_services(hass, guardian_agent)

        # Set up platforms if any
        if PLATFORMS:
            await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        entry.async_on_unload(entry.add_update_listener(async_update_options))

        _LOGGER.info("Guardian Agent setup completed successfully")
        return True

    except Exception as e:
        _LOGGER.error(f"Failed to initialize Guardian Agent: {e}")
        # Fallback to basic services
        hass.data[DOMAIN][entry.entry_id] = {"config": entry.data}
        await _register_basic_services(hass)
        return True


async def _register_basic_services(hass: HomeAssistant) -> None:
    """Register basic Guardian Agent services."""

    async def handle_ask_service(call: ServiceCall):
        """Handle the service call to ask the agent a question."""
        prompt = call.data.get(ATTR_PROMPT)
        conversation_id = call.data.get(ATTR_CONVERSATION_ID)

        if not prompt:
            _LOGGER.error("Service call 'ask' is missing required attribute 'prompt'")
            return

        # Temporary response while agent is being developed
        _LOGGER.info(f"Agent received prompt: {prompt}")
        hass.bus.async_fire(
            f"{DOMAIN}_response",
            {
                "response": "Guardian Agent is initializing. Full functionality coming soon!",
                "conversation_id": conversation_id
            }
        )

    async def handle_guardian_mode_service(call: ServiceCall):
        """Handle guardian mode changes."""
        mode = call.data.get(ATTR_MODE)
        modules = call.data.get(ATTR_MODULES)

        _LOGGER.info(f"Guardian mode service called: {mode}, modules: {modules}")
        # Placeholder implementation

    async def handle_announce_service(call: ServiceCall):
        """Handle voice announcements."""
        message = call.data.get(ATTR_MESSAGE)
        priority = call.data.get(ATTR_PRIORITY, "low")
        location = call.data.get(ATTR_LOCATION)

        _LOGGER.info(f"Announce service called: {message}")
        # Placeholder implementation

    async def handle_learn_pattern_service(call: ServiceCall):
        """Handle pattern learning."""
        pattern_type = call.data.get(ATTR_PATTERN_TYPE)
        pattern_data = call.data.get(ATTR_PATTERN_DATA)

        _LOGGER.info(f"Learn pattern service called: {pattern_type}")
        # Placeholder implementation

    # Register all services
    hass.services.async_register(
        DOMAIN, SERVICE_ASK_AGENT, handle_ask_service, schema=SERVICE_ASK_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_GUARDIAN_MODE, handle_guardian_mode_service, schema=SERVICE_GUARDIAN_MODE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_ANNOUNCE, handle_announce_service, schema=SERVICE_ANNOUNCE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_LEARN_PATTERN, handle_learn_pattern_service, schema=SERVICE_LEARN_PATTERN_SCHEMA
    )

    # Enhanced services for device control and entity access
    async def handle_control_device_service(call: ServiceCall):
        """Handle device control service."""
        entity_id = call.data.get("entity_id")
        action = call.data.get("action")
        kwargs = {k: v for k, v in call.data.items() if k not in ["entity_id", "action"]}

        _LOGGER.info(f"Device control service called: {entity_id} -> {action}")

        # Fire event for now (placeholder)
        hass.bus.async_fire(
            f"{DOMAIN}_device_control",
            {
                "entity_id": entity_id,
                "action": action,
                "parameters": kwargs,
                "timestamp": datetime.now().isoformat()
            }
        )

    async def handle_get_entities_service(call: ServiceCall):
        """Handle get entities service."""
        area = call.data.get("area")
        domain = call.data.get("domain")

        _LOGGER.info(f"Get entities service called: area={area}, domain={domain}")

        # Fire event with entity information
        hass.bus.async_fire(
            f"{DOMAIN}_entities_info",
            {
                "area": area,
                "domain": domain,
                "timestamp": datetime.now().isoformat()
            }
        )

    # Register enhanced services
    hass.services.async_register(
        DOMAIN,
        "control_device",
        handle_control_device_service,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("action"): cv.string,
            vol.Optional("brightness"): vol.Range(min=0, max=255),
            vol.Optional("temperature"): vol.Range(min=0, max=50),
            vol.Optional("hvac_mode"): cv.string,
        })
    )

    hass.services.async_register(
        DOMAIN,
        "get_entities",
        handle_get_entities_service,
        schema=vol.Schema({
            vol.Optional("area"): cv.string,
            vol.Optional("domain"): cv.string,
        })
    )


async def _register_services(hass: HomeAssistant, agent: GuardianAgent) -> None:
    """Register Guardian Agent services with actual AI functionality."""

    async def handle_ask_service(call: ServiceCall):
        """Handle the service call to ask the agent a question."""
        prompt = call.data.get(ATTR_PROMPT)
        conversation_id = call.data.get(ATTR_CONVERSATION_ID)

        if not prompt:
            _LOGGER.error("Service call 'ask' is missing required attribute 'prompt'")
            return

        try:
            response = await agent.ask(prompt, conversation_id)
            _LOGGER.debug(f"Agent response: {response[:100]}...")
        except Exception as e:
            _LOGGER.error(f"Error processing ask service: {e}")
            # Fire error response
            hass.bus.async_fire(
                f"{DOMAIN}_response",
                {
                    "response": f"Error: {str(e)}",
                    "conversation_id": conversation_id,
                    "error": True
                }
            )

    async def handle_guardian_mode_service(call: ServiceCall):
        """Handle guardian mode changes."""
        mode = call.data.get(ATTR_MODE)
        modules = call.data.get(ATTR_MODULES)

        try:
            success = await agent.set_guardian_mode(mode, modules)
            if success:
                _LOGGER.info(f"Guardian mode set to {mode}")
            else:
                _LOGGER.error(f"Failed to set guardian mode to {mode}")
        except Exception as e:
            _LOGGER.error(f"Error setting guardian mode: {e}")

    async def handle_announce_service(call: ServiceCall):
        """Handle voice announcements."""
        message = call.data.get(ATTR_MESSAGE)
        priority = call.data.get(ATTR_PRIORITY, "low")
        location = call.data.get(ATTR_LOCATION)

        try:
            success = await agent.announce(message, priority, location)
            if success:
                _LOGGER.debug(f"Announcement made: {message[:50]}...")
            else:
                _LOGGER.warning("Failed to make announcement")
        except Exception as e:
            _LOGGER.error(f"Error making announcement: {e}")

    async def handle_learn_pattern_service(call: ServiceCall):
        """Handle pattern learning."""
        pattern_type = call.data.get(ATTR_PATTERN_TYPE)
        pattern_data = call.data.get(ATTR_PATTERN_DATA)

        try:
            success = await agent.learn_pattern(pattern_type, pattern_data)
            if success:
                _LOGGER.info(f"Learned new pattern: {pattern_type}")
            else:
                _LOGGER.warning(f"Failed to learn pattern: {pattern_type}")
        except Exception as e:
            _LOGGER.error(f"Error learning pattern: {e}")

    # Register all services
    hass.services.async_register(
        DOMAIN, SERVICE_ASK_AGENT, handle_ask_service, schema=SERVICE_ASK_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_GUARDIAN_MODE, handle_guardian_mode_service, schema=SERVICE_GUARDIAN_MODE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_ANNOUNCE, handle_announce_service, schema=SERVICE_ANNOUNCE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_LEARN_PATTERN, handle_learn_pattern_service, schema=SERVICE_LEARN_PATTERN_SCHEMA
    )


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    # Get the agent instance
    agent_data = hass.data[DOMAIN].get(entry.entry_id)
    if agent_data and "agent" in agent_data:
        agent = agent_data["agent"]
        # Update agent configuration
        await agent.update_config(entry.data)

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        # Get the agent instance
        agent_data = hass.data[DOMAIN].get(entry.entry_id)
        if agent_data and "agent" in agent_data:
            agent = agent_data["agent"]
            # Gracefully shutdown the agent
            await agent.shutdown()

        # Unload platforms
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

        # Unregister services
        hass.services.async_remove(DOMAIN, SERVICE_ASK_AGENT)
        hass.services.async_remove(DOMAIN, SERVICE_GUARDIAN_MODE)
        hass.services.async_remove(DOMAIN, SERVICE_ANNOUNCE)
        hass.services.async_remove(DOMAIN, SERVICE_LEARN_PATTERN)

        # Clean up stored data
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

        _LOGGER.info("Guardian Agent unloaded successfully")
        return unload_ok

    except Exception as e:
        _LOGGER.error(f"Error unloading Guardian Agent: {e}")
        return False