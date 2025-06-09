"""Tools for the HAOS Agent Magdala to interact with Home Assistant."""
import logging
from typing import Optional, Dict, Any
import asyncio

from homeassistant.core import HomeAssistant
from langchain_core.tools import tool

_LOGGER = logging.getLogger(__name__)

class HomeAssistantToolFactory:
    """Factory to create Home Assistant tools with access to the hass object."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the tool factory."""
        self.hass = hass

    def get_tools(self) -> list:
        """Return a list of all available tools."""
        # We need to bind self to the tools
        call_service_tool = tool(self.call_service)
        get_entity_state_tool = tool(self.get_entity_state)
        get_entities_by_domain_tool = tool(self.get_entities_by_domain)
        set_entity_state_tool = tool(self.set_entity_state)
        
        return [
            call_service_tool,
            get_entity_state_tool,
            get_entities_by_domain_tool,
            set_entity_state_tool,
        ]

    def call_service(self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Calls a Home Assistant service.

        Args:
            domain: The domain of the service to call (e.g., 'light', 'switch', 'homeassistant').
            service: The name of the service to call (e.g., 'turn_on', 'toggle', 'reload_config_entry').
            service_data: A dictionary of data to pass to the service call. For example, to turn on a light, this would be {'entity_id': 'light.my_light'}.
        
        Returns:
            A string indicating success or failure.
        """
        _LOGGER.debug(f"Agent is calling service: {domain}.{service} with data: {service_data}")
        try:
            # Since we're running in an executor thread, we need to properly handle the async call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def _call_service():
                await self.hass.services.async_call(domain, service, service_data or {}, blocking=True)
            
            loop.run_until_complete(_call_service())
            loop.close()
            
            return f"Successfully called service {domain}.{service}."
        except Exception as e:
            _LOGGER.error(f"Error calling service {domain}.{service}: {e}")
            return f"Error calling service {domain}.{service}: {e}"

    def get_entity_state(self, entity_id: str) -> str:
        """
        Get the current state of a Home Assistant entity.

        Args:
            entity_id: The entity ID to get the state of (e.g., 'light.living_room').
        
        Returns:
            A string with the entity's state and attributes.
        """
        _LOGGER.debug(f"Agent is getting state for entity: {entity_id}")
        try:
            state = self.hass.states.get(entity_id)
            if state is None:
                return f"Entity {entity_id} not found."
            
            result = f"Entity: {entity_id}\nState: {state.state}"
            if state.attributes:
                result += "\nAttributes:\n"
                for key, value in state.attributes.items():
                    result += f"  {key}: {value}\n"
            
            return result
        except Exception as e:
            _LOGGER.error(f"Error getting state for entity {entity_id}: {e}")
            return f"Error getting state for entity {entity_id}: {e}"

    def get_entities_by_domain(self, domain: str) -> str:
        """
        Get all entities for a specific domain.

        Args:
            domain: The domain to get entities for (e.g., 'light', 'switch', 'sensor').
        
        Returns:
            A string listing all entities in the domain with their states.
        """
        _LOGGER.debug(f"Agent is getting entities for domain: {domain}")
        try:
            entities = []
            for state in self.hass.states.async_all():
                if state.entity_id.startswith(f"{domain}."):
                    entities.append(f"{state.entity_id}: {state.state}")
            
            if not entities:
                return f"No entities found for domain '{domain}'."
            
            return f"Entities in domain '{domain}':\n" + "\n".join(entities)
        except Exception as e:
            _LOGGER.error(f"Error getting entities for domain {domain}: {e}")
            return f"Error getting entities for domain {domain}: {e}"

    def set_entity_state(self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Set the state of a Home Assistant entity (use with caution).

        Args:
            entity_id: The entity ID to set the state of.
            state: The new state value.
            attributes: Optional dictionary of attributes to set.
        
        Returns:
            A string indicating success or failure.
        """
        _LOGGER.debug(f"Agent is setting state for entity: {entity_id} to {state}")
        try:
            # Setting state directly should be done carefully
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def _set_state():
                self.hass.states.async_set(entity_id, state, attributes or {})
            
            loop.run_until_complete(_set_state())
            loop.close()
            
            return f"Successfully set state of {entity_id} to {state}."
        except Exception as e:
            _LOGGER.error(f"Error setting state for entity {entity_id}: {e}")
            return f"Error setting state for entity {entity_id}: {e}"