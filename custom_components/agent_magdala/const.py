"""Constants for Agent Magdala Guardian System."""
from logging import Logger, getLogger
from typing import Literal

LOGGER: Logger = getLogger(__package__)

NAME = "HAOS Agent Magdala"
DOMAIN = "agent_magdala"
VERSION = "0.4.0-dev"
ATTRIBUTION = "AI Guardian Agent using Pydantic AI and Mem0"

# Platforms
PLATFORMS = ["sensor", "switch", "binary_sensor"]

# Configuration and options
CONF_OPENROUTER_API_KEY = "openrouter_api_key"
CONF_MEM0_API_KEY = "mem0_api_key"
CONF_OPENROUTER_MODEL = "openrouter_model"
CONF_GUARDIAN_MODE = "guardian_mode"
CONF_VOICE_ANNOUNCEMENTS = "voice_announcements"
CONF_TTS_SERVICE = "tts_service"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_OPENROUTER_MODEL = "google/gemini-flash-1.5"
DEFAULT_GUARDIAN_MODE = True
DEFAULT_VOICE_ANNOUNCEMENTS = True
DEFAULT_TTS_SERVICE = "tts.piper"

# Services
SERVICE_ASK_AGENT = "ask"
SERVICE_GUARDIAN_MODE = "guardian_mode"
SERVICE_ANNOUNCE = "announce"
SERVICE_LEARN_PATTERN = "learn_pattern"

# Guardian Modules
GUARDIAN_SECURITY = "security"
GUARDIAN_WELLNESS = "wellness"
GUARDIAN_ENERGY = "energy"

GUARDIAN_MODULES = [GUARDIAN_SECURITY, GUARDIAN_WELLNESS, GUARDIAN_ENERGY]

# Guardian Modes
GuardianMode = Literal["active", "passive", "sleep"]
GUARDIAN_MODE_ACTIVE = "active"
GUARDIAN_MODE_PASSIVE = "passive"
GUARDIAN_MODE_SLEEP = "sleep"

# Alert Priorities
AlertPriority = Literal["low", "medium", "high", "critical"]
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

# Attributes
ATTR_PROMPT = "prompt"
ATTR_CONVERSATION_ID = "conversation_id"
ATTR_MODE = "mode"
ATTR_MODULES = "modules"
ATTR_MESSAGE = "message"
ATTR_PRIORITY = "priority"
ATTR_LOCATION = "location"
ATTR_PATTERN_TYPE = "pattern_type"
ATTR_PATTERN_DATA = "pattern_data"

# Events
EVENT_AGENT_RESPONSE = f"{DOMAIN}_response"
EVENT_AGENT_ALERT = f"{DOMAIN}_alert"
EVENT_AGENT_PATTERN = f"{DOMAIN}_pattern"
EVENT_GUARDIAN_STATUS = f"{DOMAIN}_guardian_status"

# Entity IDs
ENTITY_GUARDIAN_MODE = f"switch.{DOMAIN}_guardian_mode"
ENTITY_SECURITY_STATUS = f"binary_sensor.{DOMAIN}_security_status"
ENTITY_WELLNESS_STATUS = f"binary_sensor.{DOMAIN}_wellness_status"
ENTITY_ENERGY_STATUS = f"binary_sensor.{DOMAIN}_energy_status"
ENTITY_MEMORY_USAGE = f"sensor.{DOMAIN}_memory_usage"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME} - AI Guardian System
Version: {VERSION}
{ATTRIBUTION}

Guardian Modules: Security, Wellness, Energy
Memory System: Mem0 Integration
Voice Communication: Home Assistant TTS

If you have any issues, please open an issue here:
https://github.com/GitDakky/HAOS_Agent_Magdala/issues
-------------------------------------------------------------------
"""