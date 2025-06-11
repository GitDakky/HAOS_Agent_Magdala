"""Secure Tools for the HAOS Agent Magdala to interact with Home Assistant."""
import logging
from typing import Optional, Dict, Any, List

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Safe domains for service calls
SAFE_DOMAINS = {
    'light', 'switch', 'fan', 'cover', 'climate', 'media_player',
    'vacuum', 'lock', 'alarm_control_panel', 'camera', 'notify'
}

# Safe services that don't modify critical system state
SAFE_SERVICES = {
    'turn_on', 'turn_off', 'toggle', 'set_temperature', 'set_hvac_mode',
    'open_cover', 'close_cover', 'stop_cover', 'play_media', 'media_play',
    'media_pause', 'media_stop', 'start', 'pause', 'stop', 'return_to_base',
    'lock', 'unlock', 'arm_home', 'arm_away', 'disarm'
}

# Dangerous services that should not be allowed
DANGEROUS_SERVICES = {
    'reload', 'restart', 'stop', 'reload_config_entry', 'reload_core_config',
    'check_config', 'restart_homeassistant', 'stop_homeassistant'
}

class SecureHomeAssistantTools:
    """Secure tools for Home Assistant interaction with permission checks."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the secure tools."""
        self.hass = hass

    def _is_safe_service_call(self, domain: str, service: str) -> bool:
        """Check if a service call is safe to execute."""
        # Block dangerous services
        if service in DANGEROUS_SERVICES:
            return False

        # Only allow safe domains
        if domain not in SAFE_DOMAINS:
            return False

        # Only allow safe services
        if service not in SAFE_SERVICES:
            return False

        return True

    async def call_service(self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Safely calls a Home Assistant service with security checks.

        Args:
            domain: The domain of the service to call (e.g., 'light', 'switch').
            service: The name of the service to call (e.g., 'turn_on', 'toggle').
            service_data: A dictionary of data to pass to the service call.

        Returns:
            A string indicating success or failure.
        """
        # Security check
        if not self._is_safe_service_call(domain, service):
            _LOGGER.warning(f"Blocked unsafe service call: {domain}.{service}")
            return f"Service call {domain}.{service} is not permitted for security reasons."

        _LOGGER.info(f"Agent calling service: {domain}.{service}")
        try:
            await self.hass.services.async_call(domain, service, service_data or {}, blocking=True)
            return f"Successfully called service {domain}.{service}."
        except Exception as e:
            _LOGGER.error(f"Error calling service {domain}.{service}: {type(e).__name__}")
            return f"Error calling service {domain}.{service}: {type(e).__name__}"

    def get_entity_state(self, entity_id: str) -> str:
        """
        Get the current state of a Home Assistant entity.

        Args:
            entity_id: The entity ID to get the state of (e.g., 'light.living_room').

        Returns:
            A string with the entity's state and key attributes.
        """
        _LOGGER.debug(f"Agent getting state for entity: {entity_id}")
        try:
            state = self.hass.states.get(entity_id)
            if state is None:
                return f"Entity {entity_id} not found."

            result = f"Entity: {entity_id}\nState: {state.state}"

            # Only include important attributes to avoid information overload
            important_attrs = ['friendly_name', 'unit_of_measurement', 'brightness',
                             'temperature', 'humidity', 'battery_level', 'device_class']

            if state.attributes:
                result += "\nKey Attributes:"
                for key in important_attrs:
                    if key in state.attributes:
                        result += f"\n  {key}: {state.attributes[key]}"

            return result
        except Exception as e:
            _LOGGER.error(f"Error getting state for entity {entity_id}: {type(e).__name__}")
            return f"Error getting state for entity {entity_id}: {type(e).__name__}"

    def get_entities_by_domain(self, domain: str, limit: int = 20) -> str:
        """
        Get entities for a specific domain with a reasonable limit.

        Args:
            domain: The domain to get entities for (e.g., 'light', 'switch', 'sensor').
            limit: Maximum number of entities to return (default: 20).

        Returns:
            A string listing entities in the domain with their states.
        """
        _LOGGER.debug(f"Agent getting entities for domain: {domain}")
        try:
            entities = []
            count = 0

            for state in self.hass.states.async_all():
                if state.entity_id.startswith(f"{domain}.") and count < limit:
                    friendly_name = state.attributes.get('friendly_name', state.entity_id)
                    entities.append(f"{friendly_name}: {state.state}")
                    count += 1

            if not entities:
                return f"No entities found for domain '{domain}'."

            result = f"Entities in domain '{domain}' (showing {len(entities)}):\n"
            result += "\n".join(entities)

            if count >= limit:
                result += f"\n... (limited to {limit} entities)"

            return result
        except Exception as e:
            _LOGGER.error(f"Error getting entities for domain {domain}: {type(e).__name__}")
            return f"Error getting entities for domain {domain}: {type(e).__name__}"

    def get_area_entities(self, area_name: str) -> str:
        """
        Get entities in a specific area.

        Args:
            area_name: The name of the area to get entities for.

        Returns:
            A string listing entities in the area.
        """
        _LOGGER.debug(f"Agent getting entities for area: {area_name}")
        try:
            entities = []

            for state in self.hass.states.async_all():
                area = state.attributes.get('area_id') or state.attributes.get('area')
                if area and area.lower() == area_name.lower():
                    friendly_name = state.attributes.get('friendly_name', state.entity_id)
                    entities.append(f"{friendly_name}: {state.state}")

            if not entities:
                return f"No entities found for area '{area_name}'."

            return f"Entities in area '{area_name}':\n" + "\n".join(entities)
        except Exception as e:
            _LOGGER.error(f"Error getting entities for area {area_name}: {type(e).__name__}")
            return f"Error getting entities for area {area_name}: {type(e).__name__}"