"""Constants for Agent Magdala."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "HAOS Agent Magdala"
DOMAIN = "agent_magdala"
VERSION = "0.2.0"
ATTRIBUTION = "AI Agent using OpenRouter and Perplexity"

# Platforms
# Initially, we might not have entities, but we'll set up a service.
# A custom panel will be the primary UI.
PLATFORMS = [] 

# Configuration and options
CONF_OPENROUTER_API_KEY = "openrouter_api_key"
CONF_PERPLEXITY_API_KEY = "perplexity_api_key"
CONF_OPENROUTER_MODEL = "openrouter_model"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_OPENROUTER_MODEL = "google/gemini-flash-1.5"

# Services
SERVICE_ASK_AGENT = "ask"

# Attributes
ATTR_PROMPT = "prompt"
ATTR_CONVERSATION_ID = "conversation_id"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration for an AI agent to help manage Home Assistant.
If you have any issues with this you need to open an issue here:
https://github.com/GitDakky/HAOS_Agent_Magdala/issues
-------------------------------------------------------------------
"""