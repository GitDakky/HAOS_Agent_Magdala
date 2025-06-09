"""Sensor platform for Agent Magdala Guardian."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="status",
        name="Guardian Status",
        icon="mdi:shield-check",
        device_class=None,
    ),
    SensorEntityDescription(
        key="mode",
        name="Guardian Mode",
        icon="mdi:shield-account",
        device_class=None,
    ),
    SensorEntityDescription(
        key="conversations",
        name="Conversation Count",
        icon="mdi:chat",
        device_class=None,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="last_interaction",
        name="Last Interaction",
        icon="mdi:clock",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="active_modules",
        name="Active Modules",
        icon="mdi:view-module",
        device_class=None,
    ),
    SensorEntityDescription(
        key="response_time",
        name="Average Response Time",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="ms",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Agent Magdala sensors."""
    agent_data = hass.data[DOMAIN][config_entry.entry_id]
    agent = agent_data.get("agent")
    
    if not agent:
        _LOGGER.warning("No agent instance found for sensor setup")
        return
    
    sensors = []
    for description in SENSOR_DESCRIPTIONS:
        sensors.append(AgentMagdalaSensor(agent, description, config_entry))
    
    async_add_entities(sensors, True)


class AgentMagdalaSensor(SensorEntity):
    """Agent Magdala sensor entity."""

    def __init__(
        self,
        agent,
        description: SensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._agent = agent
        self._config_entry = config_entry
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_name = f"Agent Magdala {description.name}"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="HAOS Agent Magdala",
            manufacturer="Augment Code",
            model="AI Guardian Agent",
            sw_version=VERSION,
            configuration_url="https://github.com/GitDakky/HAOS_Agent_Magdala",
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self._agent:
            return None
            
        key = self.entity_description.key
        
        if key == "status":
            return self._agent.status.health_status
        elif key == "mode":
            return self._agent.status.mode
        elif key == "conversations":
            return len(self._agent._conversation_contexts)
        elif key == "last_interaction":
            if self._agent.status.last_activity:
                # Ensure timezone-aware datetime
                if self._agent.status.last_activity.tzinfo is None:
                    return dt_util.as_local(self._agent.status.last_activity)
                return self._agent.status.last_activity
            return None
        elif key == "active_modules":
            return ", ".join(self._agent.status.active_modules)
        elif key == "response_time":
            # Calculate average response time (placeholder for now)
            return 1500  # ms
        
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self._agent:
            return {}
            
        key = self.entity_description.key
        
        if key == "status":
            return {
                "health_status": self._agent.status.health_status,
                "initialization_time": getattr(self._agent, '_init_time', None),
                "api_connected": bool(self._agent.session),
            }
        elif key == "mode":
            return {
                "available_modes": ["active", "passive", "sleep"],
                "mode_description": self._get_mode_description(self._agent.status.mode),
            }
        elif key == "conversations":
            active_conversations = len([
                ctx for ctx in self._agent._conversation_contexts.values()
                if ctx.last_activity and 
                (datetime.now() - ctx.last_activity).total_seconds() < 3600  # Active in last hour
            ])
            return {
                "active_conversations": active_conversations,
                "total_conversations": len(self._agent._conversation_contexts),
            }
        elif key == "active_modules":
            return {
                "modules": self._agent.status.active_modules,
                "available_modules": ["security", "wellness", "energy"],
            }
        
        return {}

    def _get_mode_description(self, mode: str) -> str:
        """Get description for guardian mode."""
        descriptions = {
            "active": "Full monitoring and proactive alerts",
            "passive": "Monitoring with reduced notifications",
            "sleep": "Emergency monitoring only"
        }
        return descriptions.get(mode, "Unknown mode")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._agent is not None and self._agent.status.health_status != "error"
