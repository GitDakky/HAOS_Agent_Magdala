"""The core Guardian Agent using Pydantic AI."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import json
import aiohttp

from homeassistant.core import HomeAssistant, Event, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

# Simplified imports to avoid dependency issues
try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIModel
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

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
    EVENT_AGENT_PATTERN,
    EVENT_GUARDIAN_STATUS,
    GUARDIAN_MODE_ACTIVE,
    GUARDIAN_MODE_PASSIVE,
    GUARDIAN_MODE_SLEEP,
    GUARDIAN_MODULES,
)

# Simplified imports to avoid dependency issues
# from .models import (
#     GuardianConfig,
#     GuardianStatus,
#     GuardianAlert,
#     GuardianResponse,
#     ConversationContext,
#     SecurityEvent,
#     WellnessEvent,
#     EnergyEvent,
#     DeviceState,
# )
# from .memory import GuardianMemory
# from .voice import GuardianVoice
# from .guardian import SecurityGuardian, WellnessGuardian, EnergyGuardian


# Simple data classes to replace complex models
class SimpleConfig:
    def __init__(self, data):
        self.openrouter_api_key = data.get(CONF_OPENROUTER_API_KEY)
        self.mem0_api_key = data.get(CONF_MEM0_API_KEY)
        self.openrouter_model = data.get(CONF_OPENROUTER_MODEL, "google/gemini-flash-1.5")
        self.guardian_mode = data.get(CONF_GUARDIAN_MODE, "active")
        self.voice_announcements = data.get(CONF_VOICE_ANNOUNCEMENTS, True)
        self.tts_service = data.get(CONF_TTS_SERVICE, "tts.piper")
        self.enabled_modules = ["security", "wellness", "energy"]

class SimpleStatus:
    def __init__(self):
        self.mode = "active"
        self.active_modules = ["security", "wellness", "energy"]
        self.last_activity = dt_util.utcnow()
        self.health_status = "initializing"

class SimpleContext:
    def __init__(self, conversation_id, user_id=None):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.messages = []
        self.started_at = dt_util.utcnow()
        self.last_activity = dt_util.utcnow()


class GuardianAgent:
    """The main Guardian Agent class using Pydantic AI."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the Guardian Agent."""
        self.hass = hass
        self.entry = entry
        self.config = self._create_config(entry.data)

        # Initialize subsystems
        self.memory = None
        self.voice = None

        # Guardian modules (simplified)
        self.security_guardian = None
        self.wellness_guardian = None
        self.energy_guardian = None

        # Agent state
        self.status = SimpleStatus()
        self.status.mode = self.config.guardian_mode

        # Pydantic AI agent
        self.agent = None
        self._conversation_contexts: Dict[str, SimpleContext] = {}
        self._state_listeners: List[Any] = []

        # HTTP session for API calls
        self.session = None

    def _create_config(self, data: Dict[str, Any]) -> SimpleConfig:
        """Create guardian configuration from entry data."""
        return SimpleConfig(data)

    async def initialize_basic(self) -> bool:
        """Initialize basic Guardian Agent functionality."""
        try:
            LOGGER.info("Initializing Guardian Agent (basic mode)...")

            # Set up basic HTTP session for API calls
            self.session = async_get_clientsession(self.hass)

            # Update status
            self.status.health_status = "healthy"
            self.status.last_activity = dt_util.utcnow()

            LOGGER.info("Guardian Agent initialized successfully (basic mode)")
            return True

        except Exception as e:
            LOGGER.error(f"Error initializing Guardian Agent: {e}", exc_info=True)
            self.status.health_status = "error"
            return False

    async def initialize(self) -> bool:
        """Initialize the full Guardian Agent and all subsystems."""
        try:
            LOGGER.info("Initializing Guardian Agent...")

            # Basic initialization first
            if not await self.initialize_basic():
                return False

            # Try to initialize advanced features
            try:
                # Skip complex initialization for now
                LOGGER.info("Advanced features skipped for stability")

            except Exception as e:
                LOGGER.warning(f"Advanced features failed to initialize: {e}")
                # Continue with basic functionality

            # Update status
            self.status.health_status = "healthy"
            self.status.last_activity = dt_util.utcnow()

            LOGGER.info("Guardian Agent initialized successfully")
            return True

        except Exception as e:
            LOGGER.error(f"Error initializing Guardian Agent: {e}", exc_info=True)
            self.status.health_status = "error"
            return False

    def _create_pydantic_agent(self):
        """Create the Pydantic AI agent (simplified)."""
        # Skip Pydantic AI for now to avoid dependency issues
        return None

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

Always prioritize safety and security. When in doubt, err on the side of caution and ask for clarification.
Communicate important alerts immediately through voice announcements.

Remember: You are a guardian, not just a chatbot. Be proactive in protecting and optimizing the home."""

    def _register_agent_tools(self, agent) -> None:
        """Register tools with the Pydantic AI agent."""
        # Skip for now
        pass

    async def _initialize_guardian_modules(self) -> None:
        """Initialize the guardian modules."""
        try:
            # Skip complex guardian modules for now
            LOGGER.info("Guardian modules initialization skipped for stability")

        except Exception as e:
            LOGGER.error(f"Error initializing guardian modules: {e}")

    async def _setup_state_monitoring(self) -> None:
        """Set up state change monitoring for guardian functions."""
        try:
            # For now, skip state monitoring to avoid import issues
            # This will be implemented in a future update
            LOGGER.debug("State monitoring setup skipped (will be implemented later)")

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
            self.status.last_activity = dt_util.utcnow()

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
        """Process a user query and return a response using OpenRouter API."""
        try:
            # Get or create conversation context
            if not conversation_id:
                conversation_id = f"conv_{dt_util.utcnow().timestamp()}"

            context = self._get_conversation_context(conversation_id, user_id)

            # Get Home Assistant context
            ha_context = await self._get_home_assistant_context()

            # Build the system prompt
            system_prompt = f"""You are HAOS Agent Magdala, an intelligent AI guardian for a Home Assistant smart home.

Your primary responsibilities:
1. SECURITY: Monitor and protect the home from unauthorized access and security threats
2. WELLNESS: Ensure the health and safety of family members
3. ENERGY: Optimize energy usage and reduce waste

Current Home Assistant Status:
{ha_context}

Your personality:
- Protective but not intrusive
- Helpful and proactive
- Clear and concise in communication
- Respectful of privacy and family routines

Always prioritize safety and security. When in doubt, err on the side of caution.
Provide helpful, actionable responses based on the current home status."""

            # Prepare the conversation history
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history (last 5 messages to keep context manageable)
            for msg in context.messages[-10:]:  # Last 5 exchanges (user + assistant)
                messages.append(msg)

            # Add current user message
            messages.append({"role": "user", "content": prompt})

            # Call OpenRouter API
            response_text = await self._call_openrouter_api(messages)

            # Update conversation context
            context.messages.append({"role": "user", "content": prompt})
            context.messages.append({"role": "assistant", "content": response_text})
            context.last_activity = dt_util.utcnow()

            # Store conversation in memory if available
            if self.memory:
                try:
                    await self.memory.add_memory(
                        content=f"User query: {prompt}\nResponse: {response_text}",
                        category="conversation",
                        user_id=user_id,
                        importance=0.6,
                        metadata={"conversation_id": conversation_id}
                    )
                except Exception as e:
                    LOGGER.warning(f"Failed to store conversation in memory: {e}")

            # Fire response event
            self.hass.bus.async_fire(
                EVENT_AGENT_RESPONSE,
                {
                    "response": response_text,
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "timestamp": dt_util.utcnow().isoformat()
                }
            )

            return response_text

        except Exception as e:
            LOGGER.error(f"Error processing query: {e}", exc_info=True)
            error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"

            # Fire error response event
            self.hass.bus.async_fire(
                EVENT_AGENT_RESPONSE,
                {
                    "response": error_response,
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "timestamp": dt_util.utcnow().isoformat(),
                    "error": True
                }
            )

            return error_response

    async def control_device(self, entity_id: str, action: str, **kwargs) -> bool:
        """Control a Home Assistant device."""
        try:
            domain = entity_id.split('.')[0]

            # Map common actions to service calls
            service_map = {
                'light': {
                    'turn_on': 'light.turn_on',
                    'turn_off': 'light.turn_off',
                    'toggle': 'light.toggle'
                },
                'switch': {
                    'turn_on': 'switch.turn_on',
                    'turn_off': 'switch.turn_off',
                    'toggle': 'switch.toggle'
                },
                'climate': {
                    'set_temperature': 'climate.set_temperature',
                    'set_hvac_mode': 'climate.set_hvac_mode',
                    'turn_on': 'climate.turn_on',
                    'turn_off': 'climate.turn_off'
                },
                'cover': {
                    'open': 'cover.open_cover',
                    'close': 'cover.close_cover',
                    'stop': 'cover.stop_cover',
                    'toggle': 'cover.toggle'
                },
                'media_player': {
                    'play': 'media_player.media_play',
                    'pause': 'media_player.media_pause',
                    'stop': 'media_player.media_stop',
                    'turn_on': 'media_player.turn_on',
                    'turn_off': 'media_player.turn_off'
                }
            }

            if domain in service_map and action in service_map[domain]:
                service = service_map[domain][action]
                service_domain, service_name = service.split('.')

                service_data = {'entity_id': entity_id}
                service_data.update(kwargs)

                await self.hass.services.async_call(
                    service_domain,
                    service_name,
                    service_data
                )

                LOGGER.info(f"Successfully controlled {entity_id}: {action}")
                return True
            else:
                LOGGER.warning(f"Unsupported action {action} for domain {domain}")
                return False

        except Exception as e:
            LOGGER.error(f"Error controlling device {entity_id}: {e}")
            return False

    async def get_entity_details(self, entity_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific entity."""
        try:
            state = self.hass.states.get(entity_id)
            if not state:
                return {"error": f"Entity {entity_id} not found"}

            # Get device and area information
            device_registry = self.hass.helpers.device_registry.async_get(self.hass)
            entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
            area_registry = self.hass.helpers.area_registry.async_get(self.hass)

            entity_entry = entity_registry.async_get(entity_id)
            device_info = None
            area_info = None

            if entity_entry:
                if entity_entry.device_id:
                    device_entry = device_registry.async_get(entity_entry.device_id)
                    if device_entry:
                        device_info = {
                            'name': device_entry.name,
                            'manufacturer': device_entry.manufacturer,
                            'model': device_entry.model,
                            'sw_version': device_entry.sw_version
                        }

                if entity_entry.area_id:
                    area_entry = area_registry.async_get_area(entity_entry.area_id)
                    if area_entry:
                        area_info = {
                            'name': area_entry.name,
                            'id': area_entry.id
                        }

            return {
                'entity_id': entity_id,
                'state': state.state,
                'attributes': dict(state.attributes),
                'last_changed': state.last_changed.isoformat() if state.last_changed else None,
                'last_updated': state.last_updated.isoformat() if state.last_updated else None,
                'domain': state.domain,
                'device_info': device_info,
                'area_info': area_info
            }

        except Exception as e:
            LOGGER.error(f"Error getting entity details for {entity_id}: {e}")
            return {"error": str(e)}

    async def get_entities_by_area(self, area_name: str) -> List[Dict[str, Any]]:
        """Get all entities in a specific area."""
        try:
            area_registry = self.hass.helpers.area_registry.async_get(self.hass)
            entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)

            # Find area by name
            area_entry = None
            for area in area_registry.areas.values():
                if area.name.lower() == area_name.lower():
                    area_entry = area
                    break

            if not area_entry:
                return []

            # Get entities in this area
            entities = []
            for entity_entry in entity_registry.entities.values():
                if entity_entry.area_id == area_entry.id:
                    entity_details = await self.get_entity_details(entity_entry.entity_id)
                    entities.append(entity_details)

            return entities

        except Exception as e:
            LOGGER.error(f"Error getting entities for area {area_name}: {e}")
            return []

    async def _call_openrouter_api(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenRouter API to get AI response."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/GitDakky/HAOS_Agent_Magdala",
                "X-Title": "HAOS Agent Magdala"
            }

            payload = {
                "model": self.config.openrouter_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }

            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    LOGGER.error(f"OpenRouter API error {response.status}: {error_text}")
                    return f"API Error: Unable to get response from AI model (status {response.status})"

        except Exception as e:
            LOGGER.error(f"Error calling OpenRouter API: {e}")
            return f"Connection Error: Unable to reach AI model ({str(e)})"

    async def _get_home_assistant_context(self) -> str:
        """Get comprehensive Home Assistant context for the AI."""
        try:
            context_parts = []

            # Get basic system info
            context_parts.append(f"Current time: {dt_util.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Get all entities with full context
            states = self.hass.states.async_all()

            # Organize entities by domain and area
            entities_by_domain = {}
            entities_by_area = {}

            for state in states:
                domain = state.domain
                if domain not in entities_by_domain:
                    entities_by_domain[domain] = []

                # Get entity details
                entity_info = {
                    'entity_id': state.entity_id,
                    'state': state.state,
                    'attributes': dict(state.attributes),
                    'last_changed': state.last_changed.isoformat() if state.last_changed else None,
                    'last_updated': state.last_updated.isoformat() if state.last_updated else None
                }

                entities_by_domain[domain].append(entity_info)

                # Group by area if available
                area = state.attributes.get('area_id') or state.attributes.get('area')
                if area:
                    if area not in entities_by_area:
                        entities_by_area[area] = []
                    entities_by_area[area].append(entity_info)

            # Security entities (detailed)
            security_domains = ['binary_sensor', 'alarm_control_panel', 'camera', 'lock', 'cover']
            security_entities = []
            for domain in security_domains:
                if domain in entities_by_domain:
                    for entity in entities_by_domain[domain]:
                        if any(keyword in entity['entity_id'].lower() for keyword in
                               ['door', 'window', 'lock', 'alarm', 'motion', 'security', 'camera', 'garage']):
                            security_entities.append(entity)

            if security_entities:
                context_parts.append("🔒 Security Status:")
                for entity in security_entities[:15]:  # Limit to 15 most important
                    friendly_name = entity['attributes'].get('friendly_name', entity['entity_id'])
                    context_parts.append(f"  - {friendly_name}: {entity['state']}")

            # Climate and environment
            climate_entities = []
            for domain in ['climate', 'weather', 'sensor']:
                if domain in entities_by_domain:
                    for entity in entities_by_domain[domain]:
                        if any(keyword in entity['entity_id'].lower() for keyword in
                               ['temperature', 'humidity', 'weather', 'climate', 'thermostat']):
                            climate_entities.append(entity)

            if climate_entities:
                context_parts.append("🌡️ Climate & Environment:")
                for entity in climate_entities[:10]:
                    friendly_name = entity['attributes'].get('friendly_name', entity['entity_id'])
                    unit = entity['attributes'].get('unit_of_measurement', '')
                    context_parts.append(f"  - {friendly_name}: {entity['state']} {unit}".strip())

            # Lighting status
            if 'light' in entities_by_domain:
                lights_on = [e for e in entities_by_domain['light'] if e['state'] == 'on']
                lights_total = len(entities_by_domain['light'])
                context_parts.append(f"💡 Lighting: {len(lights_on)}/{lights_total} lights on")
                if lights_on:
                    context_parts.append("  Currently on:")
                    for light in lights_on[:8]:  # Show first 8 lights that are on
                        friendly_name = light['attributes'].get('friendly_name', light['entity_id'])
                        brightness = light['attributes'].get('brightness', '')
                        if brightness:
                            brightness_pct = round((int(brightness) / 255) * 100)
                            context_parts.append(f"    - {friendly_name} ({brightness_pct}%)")
                        else:
                            context_parts.append(f"    - {friendly_name}")

            # Energy and power
            energy_entities = []
            for domain in ['sensor', 'switch']:
                if domain in entities_by_domain:
                    for entity in entities_by_domain[domain]:
                        if any(keyword in entity['entity_id'].lower() for keyword in
                               ['power', 'energy', 'consumption', 'watt', 'kwh']):
                            energy_entities.append(entity)

            if energy_entities:
                context_parts.append("⚡ Energy & Power:")
                for entity in energy_entities[:8]:
                    friendly_name = entity['attributes'].get('friendly_name', entity['entity_id'])
                    unit = entity['attributes'].get('unit_of_measurement', '')
                    context_parts.append(f"  - {friendly_name}: {entity['state']} {unit}".strip())

            # Device counts by domain
            domain_counts = {domain: len(entities) for domain, entities in entities_by_domain.items()}
            important_domains = ['light', 'switch', 'sensor', 'binary_sensor', 'camera', 'media_player']
            context_parts.append("📊 Device Summary:")
            for domain in important_domains:
                if domain in domain_counts:
                    context_parts.append(f"  - {domain.replace('_', ' ').title()}: {domain_counts[domain]}")

            # Areas/Rooms if available
            if entities_by_area:
                context_parts.append("🏠 Areas/Rooms:")
                for area, entities in list(entities_by_area.items())[:8]:  # Show first 8 areas
                    context_parts.append(f"  - {area}: {len(entities)} entities")

            return "\n".join(context_parts)

        except Exception as e:
            LOGGER.error(f"Error getting HA context: {e}")
            return "Home Assistant context unavailable"

    def _get_conversation_context(self, conversation_id: str, user_id: Optional[str] = None) -> SimpleContext:
        """Get or create conversation context."""
        if conversation_id not in self._conversation_contexts:
            self._conversation_contexts[conversation_id] = SimpleContext(conversation_id, user_id)
        return self._conversation_contexts[conversation_id]

    async def set_guardian_mode(self, mode: str, modules: Optional[List[str]] = None) -> bool:
        """Set the guardian mode and optionally enable/disable modules."""
        try:
            if mode not in ["active", "passive", "sleep"]:
                LOGGER.error(f"Invalid guardian mode: {mode}")
                return False

            old_mode = self.status.mode
            self.status.mode = mode

            if modules:
                self.status.active_modules = [m for m in modules if m in GUARDIAN_MODULES]

            # Fire status event
            self.hass.bus.async_fire(
                EVENT_GUARDIAN_STATUS,
                {
                    "mode": mode,
                    "active_modules": self.status.active_modules,
                    "previous_mode": old_mode,
                    "timestamp": dt_util.utcnow().isoformat()
                }
            )

            LOGGER.info(f"Guardian mode changed from {old_mode} to {mode}")
            return True

        except Exception as e:
            LOGGER.error(f"Error setting guardian mode: {e}")
            return False

    async def announce(self, message: str, priority: str = "low", location: Optional[str] = None) -> bool:
        """Make a voice announcement."""
        try:
            if self.voice:
                return await self.voice.announce(message, priority, location)
            else:
                # Fallback: log the announcement
                LOGGER.info(f"Voice announcement ({priority}): {message}")

                # Fire an event for the announcement
                self.hass.bus.async_fire(
                    f"{DOMAIN}_announcement",
                    {
                        "message": message,
                        "priority": priority,
                        "location": location,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                return True

        except Exception as e:
            LOGGER.error(f"Error making announcement: {e}")
            return False

    async def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Learn a new pattern from user behavior."""
        try:
            if self.memory:
                from .models import UserPattern

                pattern = UserPattern(
                    user_id=user_id or "household",
                    pattern_type=pattern_type,
                    pattern_data=pattern_data,
                    confidence=0.7,  # Initial confidence
                    last_updated=dt_util.utcnow(),
                    occurrences=1
                )

                success = await self.memory.learn_pattern(pattern)

                if success:
                    LOGGER.info(f"Learned new pattern: {pattern_type}")
                    return True
            else:
                # Fallback: just log the pattern
                LOGGER.info(f"Pattern learning (no memory system): {pattern_type} - {pattern_data}")

                # Fire an event for the learned pattern
                self.hass.bus.async_fire(
                    EVENT_AGENT_PATTERN,
                    {
                        "pattern_type": pattern_type,
                        "pattern_data": pattern_data,
                        "user_id": user_id,
                        "timestamp": dt_util.utcnow().isoformat()
                    }
                )
                return True

        except Exception as e:
            LOGGER.error(f"Error learning pattern: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Get current guardian status."""
        try:
            # Update status with current metrics
            self.status.uptime_hours = (dt_util.utcnow() - self.status.last_activity).total_seconds() / 3600

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
                    "timestamp": dt_util.utcnow().isoformat(),
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