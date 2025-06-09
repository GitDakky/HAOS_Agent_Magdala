# HAOS Agent Magdala

[![GitHub Release](https://img.shields.io/github/release/GitDakky/HAOS_Agent_Magdala.svg?style=for-the-badge)](https://github.com/GitDakky/HAOS_Agent_Magdala/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

A Home Assistant custom integration that provides an AI-powered conversational agent for managing your smart home.

## ⚠️ Current Status (v0.3.0)

**Important**: The agent functionality is temporarily disabled while we resolve dependency conflicts. The integration can be installed and configured, but the AI features are not yet operational.

## Features (Planned)

- 🤖 AI-powered conversational interface using OpenRouter and Perplexity
- 🏠 Direct control of Home Assistant entities and services
- 🔍 Intelligent research capabilities for Home Assistant topics
- 💬 Natural language processing for intuitive interactions
- 🛠️ Extensible tool system for custom actions

## Prerequisites

- Home Assistant 2024.1.0 or newer
- OpenRouter API key (for LLM access)
- Perplexity API key (for research capabilities)

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/GitDakky/HAOS_Agent_Magdala` as a custom repository
5. Select "Integration" as the category
6. Click "Add"
7. Search for "HAOS Agent Magdala" and install it
8. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [releases page](https://github.com/GitDakky/HAOS_Agent_Magdala/releases)
2. Extract the `custom_components/agent_magdala` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "HAOS Agent Magdala"
4. Enter your configuration:
   - **OpenRouter API Key**: Your OpenRouter API key
   - **Perplexity API Key**: Your Perplexity API key
   - **OpenRouter Model**: (Optional) The model to use (default: `google/gemini-flash-1.5`)

## Usage

Once configured, the integration provides:

### Service: `agent_magdala.ask`

Send a prompt to the agent and receive a response via Home Assistant events.

```yaml
service: agent_magdala.ask
data:
  prompt: "Turn on the living room lights"
  conversation_id: "optional-conversation-id"
```

### Events

The integration fires `agent_magdala_response` events with the agent's responses:

```yaml
event_type: agent_magdala_response
data:
  response: "I've turned on the living room lights for you."
  conversation_id: "optional-conversation-id"
```

## Available Tools (When Fully Operational)

- **call_service**: Execute any Home Assistant service
- **get_entity_state**: Retrieve the current state of any entity
- **get_entities_by_domain**: List all entities in a specific domain
- **set_entity_state**: Directly modify entity states (use with caution)

## Known Issues

- **v0.3.0**: Agent functionality temporarily disabled due to dependency conflicts
- Config flow issues have been resolved in v0.3.0

## Development Roadmap

- [ ] Resolve langchain dependency conflicts
- [ ] Re-enable AI agent functionality
- [ ] Add conversation history persistence
- [ ] Implement web-based chat interface
- [ ] Add support for custom tools
- [ ] Improve error handling and logging

## Troubleshooting

### "Config flow could not be loaded" Error

This issue has been resolved in v0.3.0. If you're still experiencing this:
1. Ensure you're running the latest version
2. Clear your browser cache
3. Restart Home Assistant completely

### Agent Not Responding

The agent functionality is temporarily disabled in v0.3.0. Check back for updates or watch the repository for new releases.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- [Report Issues](https://github.com/GitDakky/HAOS_Agent_Magdala/issues)
- [Discussions](https://github.com/GitDakky/HAOS_Agent_Magdala/discussions)

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [OpenRouter](https://openrouter.ai/) and [Perplexity](https://www.perplexity.ai/)
- Inspired by the Home Assistant community