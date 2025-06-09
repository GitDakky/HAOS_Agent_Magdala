"""Test the HAOS Agent Magdala config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.agent_magdala.const import DOMAIN, CONF_OPENROUTER_API_KEY, CONF_PERPLEXITY_API_KEY

pytestmark = pytest.mark.usefixtures("hass_storage")


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    # The config flow doesn't validate keys with an API call, so we just patch the setup
    with patch(
        "custom_components.agent_magdala.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_OPENROUTER_API_KEY: "sk-or-v1-dummy-openrouter-key",
                CONF_PERPLEXITY_API_KEY: "pplx-dummy-perplexity-key",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "HAOS Agent Magdala"
    assert result2["data"] == {
        CONF_OPENROUTER_API_KEY: "sk-or-v1-dummy-openrouter-key",
        CONF_PERPLEXITY_API_KEY: "pplx-dummy-perplexity-key",
        "openrouter_model": "google/gemini-flash-1.5",
    }
    assert len(mock_setup_entry.mock_calls) == 1

async def test_form_input_errors(hass: HomeAssistant) -> None:
    """Test we handle input errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_OPENROUTER_API_KEY: "",
            CONF_PERPLEXITY_API_KEY: "",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {
        CONF_OPENROUTER_API_KEY: "openrouter_key_empty",
        CONF_PERPLEXITY_API_KEY: "perplexity_key_empty",
    }