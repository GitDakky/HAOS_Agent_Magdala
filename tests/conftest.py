"""Common fixtures for the HAOS Agent Magdala tests."""
import pytest
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.config_entries import ConfigEntry

from custom_components.agent_magdala.const import DOMAIN

MOCK_CONFIG = {
    "openrouter_api_key": "sk-or-v1-dummy-openrouter-key",
    "perplexity_api_key": "pplx-dummy-perplexity-key",
    "openrouter_model": "google/gemini-flash-1.5",
}

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield

@pytest.fixture
async def mock_config_entry() -> ConfigEntry:
    """Return a mock config entry."""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="HAOS Agent Magdala",
        data=MOCK_CONFIG,
        source="user",
    )

@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry: ConfigEntry):
    """Set up the integration for testing."""
    mock_config_entry.add_to_hass(hass)
    
    with patch("custom_components.agent_magdala.agent.ChatOpenAI", autospec=True), \
         patch("custom_components.agent_magdala.agent.ChatPerplexity", autospec=True):
        
        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()

    return mock_config_entry