"""Test the HAOS Agent Magdala agent."""
from unittest.mock import patch, AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.agent_magdala.const import DOMAIN, SERVICE_ASK_AGENT, ATTR_PROMPT



async def test_agent_setup(hass: HomeAssistant):
    """Test that the agent is set up correctly."""
    # The setup_integration fixture already sets up the component.
    # We just need to check if the agent instance is in hass.data.
    assert DOMAIN in hass.data

@pytest.mark.usefixtures("hass_config_entry_only")
async def test_ask_service_call(hass: HomeAssistant):
    """Test the agent_magdala.ask service call."""
    # The agent executor's invoke method is what we want to mock
    # to avoid real LLM calls.
    with patch(
        "custom_components.agent_magdala.agent.AgentExecutor.invoke",
        return_value={"output": "This is a mocked response."},
    ) as mock_invoke, patch(
        "homeassistant.core.EventBus.async_fire"
    ) as mock_async_fire:
        
        # Mock the async_add_executor_job to run the mocked invoke
        async def mock_run_in_executor(*args):
            # The first arg is the function to run, the rest are its arguments
            func = args[0]
            func_args = args[1:]
            return func(*func_args)

        hass.async_add_executor_job = AsyncMock(side_effect=mock_run_in_executor)

        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ASK_AGENT,
            {ATTR_PROMPT: "What version are you?"},
            blocking=True,
        )

        # Check that the agent's invoke method was called
        mock_invoke.assert_called_once_with({"input": "What version are you?"})

        # Check that the response event was fired
        mock_async_fire.assert_called_once()
        event_call = mock_async_fire.call_args
        assert event_call.args[0] == f"{DOMAIN}_response"
        assert "This is a mocked response." in event_call.args[1].get("response", "")