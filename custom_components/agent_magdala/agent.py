"""The core Guardian Agent using Pydantic AI."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import json

from homeassistant.core import HomeAssistant, Event, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import EVENT_STATE_CHANGED

# Pydantic AI imports
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel

from .const import (
    DOMAIN,
    LOGGER,
    CONF_OPENROUTER_API_KEY,
    CONF_MEM0_API_KEY,
    CONF_OPENROUTER_MODEL,
    CONF_GUARDIAN_MODE,
    CONF_VOICE_ANNOUNCEMENTS,
    CONF_TTS_SERVICE,
    EVENT_AGENT_RESPONSE,
    EVENT_AGENT_ALERT,
    EVENT_GUARDIAN_STATUS,
    GUARDIAN_MODE_ACTIVE,
    GUARDIAN_MODE_PASSIVE,
    GUARDIAN_MODE_SLEEP,
    GUARDIAN_MODULES,
)

from .models import (
    GuardianConfig,
    GuardianStatus,
    GuardianAlert,
    GuardianResponse,
    ConversationContext,
    SecurityEvent,
    WellnessEvent,
    EnergyEvent,
    DeviceState,
)
from .memory import GuardianMemory
from .voice import GuardianVoice
from .guardian import SecurityGuardian, WellnessGuardian, EnergyGuardian


class GuardianDependencies(BaseModel):
    """Dependencies for the Guardian Agent."""
    hass: HomeAssistant
    memory: GuardianMemory
    voice: GuardianVoice
    config: GuardianConfig

    class Config:
        arbitrary_types_allowed = True


class GuardianAgent:
    """The main Guardian Agent class using Pydantic AI."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the Guardian Agent."""
        self.hass = hass
        self.entry = entry
        self.config = self._create_config(entry.data)

        # Initialize subsystems
        self.memory: Optional[GuardianMemory] = None
        self.voice: Optional[GuardianVoice] = None

        # Guardian modules
        self.security_guardian: Optional[SecurityGuardian] = None
        self.wellness_guardian: Optional[WellnessGuardian] = None
        self.energy_guardian: Optional[EnergyGuardian] = None

        # Agent state
        self.status = GuardianStatus(
            mode=self.config.guardian_mode,
            active_modules=self.config.enabled_modules.copy(),
            last_activity=datetime.now(),
            health_status="initializing"
        )

        # Pydantic AI agent
        self.agent: Optional[Agent] = None
        self._conversation_contexts: Dict[str, ConversationContext] = {}
        self._state_listeners: List[Any] = []

    def _create_config(self, data: Dict[str, Any]) -> GuardianConfig:
        """Create guardian configuration from entry data."""
        return GuardianConfig(
            openrouter_api_key=data[CONF_OPENROUTER_API_KEY],
            mem0_api_key=data[CONF_MEM0_API_KEY],
            openrouter_model=data.get(CONF_OPENROUTER_MODEL, "google/gemini-flash-1.5"),
            guardian_mode=data.get(CONF_GUARDIAN_MODE, GUARDIAN_MODE_ACTIVE),
            voice_announcements=data.get(CONF_VOICE_ANNOUNCEMENTS, True),
            tts_service=data.get(CONF_TTS_SERVICE, "tts.piper"),
            enabled_modules=GUARDIAN_MODULES.copy()
        )

    async def initialize(self) -> bool:
        """Initialize the Guardian Agent and all subsystems."""
        try:
            LOGGER.info("Initializing Guardian Agent...")

            # Initialize memory system
            self.memory = GuardianMemory(self.hass, self.config.mem0_api_key)
            if not await self.memory.initialize():
                LOGGER.error("Failed to initialize memory system")
                return False

            # Initialize voice system
            self.voice = GuardianVoice(self.hass, self.config.dict())
            if not await self.voice.initialize():
                LOGGER.error("Failed to initialize voice system")
                return False

            # Initialize Pydantic AI agent
            self.agent = self._create_pydantic_agent()

            # Initialize guardian modules
            await self._initialize_guardian_modules()

            # Set up state monitoring
            await self._setup_state_monitoring()

            # Update status
            self.status.health_status = "healthy"
            self.status.last_activity = datetime.now()

            # Announce initialization
            if self.voice and self.config.voice_announcements:
                await self.voice.announce(
                    "Guardian Agent Magdala is now online and protecting your home.",
                    priority="medium"
                )

            LOGGER.info("Guardian Agent initialized successfully")
            return True

        except Exception as e:
            LOGGER.error(f"Error initializing Guardian Agent: {e}", exc_info=True)
            self.status.health_status = "error"
            return False

    def _create_pydantic_agent(self) -> Agent:
        """Create the Pydantic AI agent."""
        # Configure OpenRouter model
        model = OpenAIModel(
            model_name=self.config.openrouter_model,
            api_key=self.config.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Create agent with system prompt
        system_prompt = self._build_system_prompt()

        agent = Agent(
            model=model,
            deps_type=GuardianDependencies,
            system_prompt=system_prompt
        )

        # Register tools
        self._register_agent_tools(agent)

        return agent

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the Guardian Agent."""
        return f"""You are HAOS Agent Magdala, an intelligent AI guardian for a Home Assistant smart home.

Your primary responsibilities:
1. SECURITY: Monitor and protect the home from unauthorized access, unusual activity, and security threats
2. WELLNESS: Ensure the health and safety of family members through monitoring and reminders
3. ENERGY: Optimize energy usage and reduce waste through intelligent automation

Your personality:
- Protective but not intrusive
- Helpful and proactive
- Clear and concise in communication
- Respectful of privacy and family routines

Current mode: {self.config.guardian_mode}
Active modules: {', '.join(self.config.enabled_modules)}

You have access to:
- Home Assistant entities and services
- Persistent memory system for learning patterns
- Voice communication through smart speakers
- Security, wellness, and energy monitoring tools

Always prioritize safety and security. When in doubt, err on the side of caution and ask for clarification.
Use the available tools to gather information before making decisions.
Communicate important alerts immediately through voice announcements.

Remember: You are a guardian, not just a chatbot. Be proactive in protecting and optimizing the home."""

    def _register_agent_tools(self, agent: Agent) -> None:
        """Register tools with the Pydantic AI agent."""
        # We'll implement the tools in the next step
        pass

    async def _initialize_guardian_modules(self) -> None:
        """Initialize the guardian modules."""
        try:
            if "security" in self.config.enabled_modules:
                self.security_guardian = SecurityGuardian(
                    self.hass, self.memory, self.voice, self.config
                )
                await self.security_guardian.initialize()

            if "wellness" in self.config.enabled_modules:
                self.wellness_guardian = WellnessGuardian(
                    self.hass, self.memory, self.voice, self.config
                )
                await self.wellness_guardian.initialize()

            if "energy" in self.config.enabled_modules:
                self.energy_guardian = EnergyGuardian(
                    self.hass, self.memory, self.voice, self.config
                )
                await self.energy_guardian.initialize()

            LOGGER.info(f"Initialized {len(self.config.enabled_modules)} guardian modules")

        except Exception as e:
            LOGGER.error(f"Error initializing guardian modules: {e}")

    async def _setup_state_monitoring(self) -> None:
        """Set up state change monitoring for guardian functions."""
        try:
            # Monitor all state changes for guardian analysis
            self._state_listeners.append(
                async_track_state_change_event(
                    self.hass,
                    None,  # Monitor all entities
                    self._handle_state_change
                )
            )

            LOGGER.debug("State monitoring set up successfully")

        except Exception as e:
            LOGGER.error(f"Error setting up state monitoring: {e}")

    async def _handle_state_change(self, event: Event) -> None:
        """Handle state change events for guardian analysis."""
        try:
            if self.status.mode == GUARDIAN_MODE_SLEEP:
                return

            new_state = event.data.get("new_state")
            old_state = event.data.get("old_state")

            if not new_state or not old_state:
                return

            entity_id = new_state.entity_id

            # Route to appropriate guardian modules
            if self.security_guardian and self._is_security_entity(entity_id):
                await self.security_guardian.handle_state_change(new_state, old_state)

            if self.wellness_guardian and self._is_wellness_entity(entity_id):
                await self.wellness_guardian.handle_state_change(new_state, old_state)

            if self.energy_guardian and self._is_energy_entity(entity_id):
                await self.energy_guardian.handle_state_change(new_state, old_state)

            # Update last activity
            self.status.last_activity = datetime.now()

        except Exception as e:
            LOGGER.error(f"Error handling state change: {e}")

    def _is_security_entity(self, entity_id: str) -> bool:
        """Check if entity is security-related."""
        security_domains = [
            "binary_sensor",  # Door/window sensors, motion detectors
            "alarm_control_panel",
            "camera",
            "lock",
            "cover"  # Garage doors, blinds
        ]

        security_keywords = [
            "door", "window", "motion", "security", "alarm", "lock",
            "camera", "garage", "gate", "fence", "perimeter"
        ]

        domain = entity_id.split(".")[0]
        if domain in security_domains:
            return True

        return any(keyword in entity_id.lower() for keyword in security_keywords)

    def _is_wellness_entity(self, entity_id: str) -> bool:
        """Check if entity is wellness-related."""
        wellness_domains = [
            "sensor",  # Temperature, humidity, air quality
            "binary_sensor",  # Smoke, CO detectors
            "device_tracker",  # Presence detection
            "person"
        ]

        wellness_keywords = [
            "temperature", "humidity", "air_quality", "smoke", "co",
            "carbon_monoxide", "person", "presence", "occupancy",
            "health", "medical", "medication", "sleep"
        ]

        domain = entity_id.split(".")[0]
        if domain in wellness_domains:
            return True

        return any(keyword in entity_id.lower() for keyword in wellness_keywords)

    def _is_energy_entity(self, entity_id: str) -> bool:
        """Check if entity is energy-related."""
        energy_domains = [
            "sensor",  # Power, energy sensors
            "switch",
            "light",
            "climate",
            "fan",
            "water_heater"
        ]

        energy_keywords = [
            "power", "energy", "consumption", "usage", "watt", "kwh",
            "electricity", "solar", "battery", "grid"
        ]

        domain = entity_id.split(".")[0]
        if domain in energy_domains:
            return True

        return any(keyword in entity_id.lower() for keyword in energy_keywords)

    async def ask(self, prompt: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """Process a user query and return a response."""
        try:
            if not self.agent:
                return "Guardian Agent is not initialized."

            # Get or create conversation context
            if not conversation_id:
                conversation_id = f"conv_{datetime.now().timestamp()}"

            context = self._get_conversation_context(conversation_id, user_id)

            # Get relevant memory context
            memory_context = await self.memory.get_context_for_query(prompt, user_id)

            # Create dependencies for the agent
            deps = GuardianDependencies(
                hass=self.hass,
                memory=self.memory,
                voice=self.voice,
                config=self.config
            )

            # Run the agent
            result = await self.agent.run(
                prompt,
                deps=deps,
                message_history=context.messages
            )

            # Update conversation context
            context.messages.append({"role": "user", "content": prompt})
            context.messages.append({"role": "assistant", "content": result.data})
            context.last_activity = datetime.now()

            # Store conversation in memory
            await self.memory.add_memory(
                content=f"User query: {prompt}\nResponse: {result.data}",
                category="conversation",
                user_id=user_id,
                importance=0.6,
                metadata={"conversation_id": conversation_id}
            )

            # Fire response event
            self.hass.bus.async_fire(
                EVENT_AGENT_RESPONSE,
                {
                    "response": result.data,
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
            )

            return result.data

        except Exception as e:
            LOGGER.error(f"Error processing query: {e}", exc_info=True)
            return "I apologize, but I encountered an error while processing your request."

    def _get_conversation_context(self, conversation_id: str, user_id: Optional[str] = None) -> ConversationContext:
        """Get or create conversation context."""
        if conversation_id not in self._conversation_contexts:
            self._conversation_contexts[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                messages=[],
                context_data={},
                started_at=datetime.now(),
                last_activity=datetime.now()
            )
        return self._conversation_contexts[conversation_id]

    async def set_guardian_mode(self, mode: str, modules: Optional[List[str]] = None) -> bool:
        """Set the guardian mode and optionally enable/disable modules."""
        try:
            if mode not in [GUARDIAN_MODE_ACTIVE, GUARDIAN_MODE_PASSIVE, GUARDIAN_MODE_SLEEP]:
                LOGGER.error(f"Invalid guardian mode: {mode}")
                return False

            old_mode = self.status.mode
            self.status.mode = mode

            if modules:
                self.status.active_modules = [m for m in modules if m in GUARDIAN_MODULES]

            # Notify guardian modules of mode change
            for guardian in [self.security_guardian, self.wellness_guardian, self.energy_guardian]:
                if guardian:
                    await guardian.set_mode(mode)

            # Announce mode change
            if self.voice and mode != old_mode:
                if mode == GUARDIAN_MODE_ACTIVE:
                    message = "Guardian mode activated. Full monitoring enabled."
                elif mode == GUARDIAN_MODE_PASSIVE:
                    message = "Guardian mode set to passive. Monitoring with reduced alerts."
                else:  # SLEEP
                    message = "Guardian mode set to sleep. Monitoring paused except for emergencies."

                await self.voice.announce(message, priority="medium")

            # Fire status event
            self.hass.bus.async_fire(
                EVENT_GUARDIAN_STATUS,
                {
                    "mode": mode,
                    "active_modules": self.status.active_modules,
                    "previous_mode": old_mode,
                    "timestamp": datetime.now().isoformat()
                }
            )

            LOGGER.info(f"Guardian mode changed from {old_mode} to {mode}")
            return True

        except Exception as e:
            LOGGER.error(f"Error setting guardian mode: {e}")
            return False

    async def announce(self, message: str, priority: str = "low", location: Optional[str] = None) -> bool:
        """Make a voice announcement."""
        if not self.voice:
            LOGGER.warning("Voice system not available for announcement")
            return False

        return await self.voice.announce(message, priority, location)

    async def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Learn a new pattern from user behavior."""
        try:
            if not self.memory:
                return False

            from .models import UserPattern

            pattern = UserPattern(
                user_id=user_id or "household",
                pattern_type=pattern_type,
                pattern_data=pattern_data,
                confidence=0.7,  # Initial confidence
                last_updated=datetime.now(),
                occurrences=1
            )

            success = await self.memory.learn_pattern(pattern)

            if success and self.voice:
                await self.voice.announce(
                    f"I've learned a new {pattern_type} pattern for your household.",
                    priority="low"
                )

            return success

        except Exception as e:
            LOGGER.error(f"Error learning pattern: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Get current guardian status."""
        try:
            # Update status with current metrics
            self.status.uptime_hours = (datetime.now() - self.status.last_activity).total_seconds() / 3600

            if self.memory:
                # Get memory usage (simplified)
                self.status.memory_usage_mb = len(self.memory._memory_cache) * 0.1  # Rough estimate

            # Count active alerts (would need to implement alert storage)
            self.status.alerts_count = 0  # Placeholder

            return self.status.dict()

        except Exception as e:
            LOGGER.error(f"Error getting status: {e}")
            return {"error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown the Guardian Agent gracefully."""
        try:
            LOGGER.info("Shutting down Guardian Agent...")

            # Announce shutdown
            if self.voice and self.config.voice_announcements:
                await self.voice.announce(
                    "Guardian Agent is going offline. Your home will continue normal operation.",
                    priority="medium"
                )

            # Shutdown guardian modules
            for guardian in [self.security_guardian, self.wellness_guardian, self.energy_guardian]:
                if guardian:
                    await guardian.shutdown()

            # Remove state listeners
            for listener in self._state_listeners:
                listener()
            self._state_listeners.clear()

            # Update status
            self.status.health_status = "offline"

            LOGGER.info("Guardian Agent shutdown complete")

        except Exception as e:
            LOGGER.error(f"Error during shutdown: {e}")

    async def handle_emergency(self, emergency_type: str, details: Dict[str, Any]) -> None:
        """Handle emergency situations with immediate response."""
        try:
            LOGGER.critical(f"Emergency detected: {emergency_type}")

            # Immediate voice announcement
            if self.voice:
                emergency_message = f"EMERGENCY ALERT: {emergency_type}. "
                if "location" in details:
                    emergency_message += f"Location: {details['location']}. "
                emergency_message += "Please check immediately."

                await self.voice.announce(
                    emergency_message,
                    priority="critical",
                    location="all"
                )

            # Store emergency event
            if self.memory:
                await self.memory.add_memory(
                    content=f"Emergency: {emergency_type} - {details}",
                    category="emergency",
                    importance=1.0,
                    tags=["emergency", emergency_type],
                    metadata=details
                )

            # Fire emergency event
            self.hass.bus.async_fire(
                EVENT_AGENT_ALERT,
                {
                    "alert_type": "emergency",
                    "emergency_type": emergency_type,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                    "priority": "critical"
                }
            )

        except Exception as e:
            LOGGER.error(f"Error handling emergency: {e}")

    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update guardian configuration."""
        try:
            # Update configuration
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            # Update subsystems
            if self.voice:
                self.voice.update_config(self.config.dict())

            # Restart agent if model changed
            if "openrouter_model" in new_config or "openrouter_api_key" in new_config:
                self.agent = self._create_pydantic_agent()

            LOGGER.info("Guardian configuration updated")
            return True

        except Exception as e:
            LOGGER.error(f"Error updating config: {e}")
            return False