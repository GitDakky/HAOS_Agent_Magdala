"""Binary sensor platform for Agent Magdala Guardian."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="agent_online",
        name="Agent Online",
        icon="mdi:robot",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="api_connected",
        name="API Connected",
        icon="mdi:api",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="guardian_monitoring",
        name="Guardian Monitoring",
        icon="mdi:shield-check",
        device_class=None,
    ),
    BinarySensorEntityDescription(
        key="conversation_active",
        name="Conversation Active",
        icon="mdi:chat",
        device_class=None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Agent Magdala binary sensors."""
    agent_data = hass.data[DOMAIN][config_entry.entry_id]
    agent = agent_data.get("agent")
    
    if not agent:
        _LOGGER.warning("No agent instance found for binary sensor setup")
        return
    
    binary_sensors = []
    for description in BINARY_SENSOR_DESCRIPTIONS:
        binary_sensors.append(AgentMagdalaBinarySensor(agent, description, config_entry))
    
    async_add_entities(binary_sensors, True)


class AgentMagdalaBinarySensor(BinarySensorEntity):
    """Agent Magdala binary sensor entity."""

    def __init__(
        self,
        agent,
        description: BinarySensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self._agent:
            return False
            
        key = self.entity_description.key
        
        if key == "agent_online":
            return self._agent.status.health_status in ["healthy", "initializing"]
        elif key == "api_connected":
            return bool(self._agent.session and self._agent.config.openrouter_api_key)
        elif key == "guardian_monitoring":
            return self._agent.status.mode in ["active", "passive"]
        elif key == "conversation_active":
            # Check if there's been a conversation in the last 5 minutes
            if not self._agent._conversation_contexts:
                return False
            recent_activity = any(
                ctx.last_activity and
                (dt_util.utcnow() - ctx.last_activity).total_seconds() < 300  # 5 minutes
                for ctx in self._agent._conversation_contexts.values()
            )
            return recent_activity
        
        return False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self._agent:
            return {}
            
        key = self.entity_description.key
        
        if key == "agent_online":
            return {
                "health_status": self._agent.status.health_status,
                "last_activity": self._agent.status.last_activity.isoformat() if self._agent.status.last_activity else None,
                "uptime_seconds": (dt_util.utcnow() - getattr(self._agent, '_init_time', dt_util.utcnow())).total_seconds(),
            }
        elif key == "api_connected":
            return {
                "api_key_configured": bool(self._agent.config.openrouter_api_key),
                "model": self._agent.config.openrouter_model,
                "session_active": bool(self._agent.session),
            }
        elif key == "guardian_monitoring":
            return {
                "mode": self._agent.status.mode,
                "active_modules": self._agent.status.active_modules,
                "monitoring_since": self._agent.status.last_activity.isoformat() if self._agent.status.last_activity else None,
            }
        elif key == "conversation_active":
            active_conversations = [
                ctx.conversation_id for ctx in self._agent._conversation_contexts.values()
                if ctx.last_activity and 
                (dt_util.utcnow() - ctx.last_activity).total_seconds() < 300
            ]
            return {
                "active_conversation_ids": active_conversations,
                "total_conversations": len(self._agent._conversation_contexts),
                "last_conversation": max(
                    (ctx.last_activity for ctx in self._agent._conversation_contexts.values() if ctx.last_activity),
                    default=None
                ),
            }
        
        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._agent is not None
