"""Switch platform for Agent Magdala Guardian."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS = [
    SwitchEntityDescription(
        key="guardian_active",
        name="Guardian Active Mode",
        icon="mdi:shield-check",
    ),
    SwitchEntityDescription(
        key="security_module",
        name="Security Module",
        icon="mdi:security",
    ),
    SwitchEntityDescription(
        key="wellness_module",
        name="Wellness Module",
        icon="mdi:heart-pulse",
    ),
    SwitchEntityDescription(
        key="energy_module",
        name="Energy Module",
        icon="mdi:lightning-bolt",
    ),
    SwitchEntityDescription(
        key="voice_announcements",
        name="Voice Announcements",
        icon="mdi:volume-high",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Agent Magdala switches."""
    agent_data = hass.data[DOMAIN][config_entry.entry_id]
    agent = agent_data.get("agent")
    
    if not agent:
        _LOGGER.warning("No agent instance found for switch setup")
        return
    
    switches = []
    for description in SWITCH_DESCRIPTIONS:
        switches.append(AgentMagdalaSwitch(agent, description, config_entry))
    
    async_add_entities(switches, True)


class AgentMagdalaSwitch(SwitchEntity):
    """Agent Magdala switch entity."""

    def __init__(
        self,
        agent,
        description: SwitchEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
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
        """Return true if switch is on."""
        if not self._agent:
            return False
            
        key = self.entity_description.key
        
        if key == "guardian_active":
            return self._agent.status.mode == "active"
        elif key == "security_module":
            return "security" in self._agent.status.active_modules
        elif key == "wellness_module":
            return "wellness" in self._agent.status.active_modules
        elif key == "energy_module":
            return "energy" in self._agent.status.active_modules
        elif key == "voice_announcements":
            return self._agent.config.voice_announcements
        
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if not self._agent:
            return
            
        key = self.entity_description.key
        
        try:
            if key == "guardian_active":
                await self._agent.set_guardian_mode("active")
            elif key == "security_module":
                modules = self._agent.status.active_modules.copy()
                if "security" not in modules:
                    modules.append("security")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "wellness_module":
                modules = self._agent.status.active_modules.copy()
                if "wellness" not in modules:
                    modules.append("wellness")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "energy_module":
                modules = self._agent.status.active_modules.copy()
                if "energy" not in modules:
                    modules.append("energy")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "voice_announcements":
                self._agent.config.voice_announcements = True
                
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning on {key}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if not self._agent:
            return
            
        key = self.entity_description.key
        
        try:
            if key == "guardian_active":
                await self._agent.set_guardian_mode("passive")
            elif key == "security_module":
                modules = self._agent.status.active_modules.copy()
                if "security" in modules:
                    modules.remove("security")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "wellness_module":
                modules = self._agent.status.active_modules.copy()
                if "wellness" in modules:
                    modules.remove("wellness")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "energy_module":
                modules = self._agent.status.active_modules.copy()
                if "energy" in modules:
                    modules.remove("energy")
                await self._agent.set_guardian_mode(self._agent.status.mode, modules)
            elif key == "voice_announcements":
                self._agent.config.voice_announcements = False
                
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning off {key}: {e}")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self._agent:
            return {}
            
        key = self.entity_description.key
        
        if key == "guardian_active":
            return {
                "current_mode": self._agent.status.mode,
                "available_modes": ["active", "passive", "sleep"],
            }
        elif key in ["security_module", "wellness_module", "energy_module"]:
            module_name = key.replace("_module", "")
            return {
                "module_status": "enabled" if module_name in self._agent.status.active_modules else "disabled",
                "all_modules": self._agent.status.active_modules,
            }
        
        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._agent is not None and self._agent.status.health_status != "error"
