"""Tools for the HAOS Agent Magdala to interact with Home Assistant."""
import logging
from typing import Optional, Dict, Any

from homeassistant.core import HomeAssistant
from langchain.tools import tool

_LOGGER = logging.getLogger(__name__)

class HomeAssistantToolFactory:
    """Factory to create Home Assistant tools with access to the hass object."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the tool factory."""
        self.hass = hass

    def get_tools(self) -> list:
        """Return a list of all available tools."""
        return [
            self.call_service,
        ]

    @tool
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
            # Home Assistant services are asynchronous, but LangChain tools are often called synchronously.
            # We need to call the async function from this sync context.
            # The agent executor runs in a separate thread, so we can use hass.add_job.
            self.hass.add_job(self.hass.services.async_call, domain, service, service_data, blocking=False)
            return f"Successfully called service {domain}.{service}."
        except Exception as e:
            _LOGGER.error(f"Error calling service {domain}.{service}: {e}")
            return f"Error calling service {domain}.{service}: {e}"