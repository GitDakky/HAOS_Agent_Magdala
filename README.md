# HAOS Agent Magdala

This is a custom component for Home Assistant that integrates "Agent Magdala," an AI-powered conversational agent.

## Installation

1.  **Copy the component:** Copy the `custom_components/agent_magdala` directory into your Home Assistant `custom_components` folder.
2.  **Restart Home Assistant:** Restart your Home Assistant instance to load the new component.

## Configuration

1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration** and search for "HAOS Agent Magdala".
3.  Enter your API keys for OpenRouter and Perplexity.
4.  The agent will be set up and a custom panel will be added to your sidebar.

## Usage

1.  Open the "Agent Magdala" panel from the sidebar.
2.  Type your questions or commands into the chat interface.
3.  The agent will respond and can execute Home Assistant services.

### Available Tools

-   `call_service`: Allows the agent to call any Home Assistant service (e.g., `light.turn_on`).
-   `research_home_assistant_topic`: Allows the agent to research Home Assistant-related topics using Perplexity.