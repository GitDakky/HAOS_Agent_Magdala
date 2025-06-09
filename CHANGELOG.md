# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-06-09

### Changed
- Major refactor to resolve config flow loading issues
- Temporarily disabled LangChain and agent functionality to fix dependency conflicts
- Simplified config_flow.py to minimal implementation
- Removed all external dependencies from manifest.json

### Fixed
- Fixed "500 Internal Server Error" when loading config flow
- Resolved import issues preventing integration discovery

### Known Issues
- Agent functionality is temporarily disabled
- Service returns placeholder response only

## [0.2.1] - 2024-06-09

### Changed
- Simplified config_flow.py to avoid import conflicts
- Added specific version constraints for langchain dependencies
- Hardcoded DOMAIN constant in config_flow to prevent circular imports

### Fixed
- Attempted fix for "Invalid handler specified" error
- Populated empty translations/en.json file

## [0.2.0] - 2024-06-09

### Changed
- Refactored config_flow.py to fix "Invalid handler specified" error
- Changed class name from AgentMagdalaConfigFlow to ConfigFlow
- Updated imports to use modern Home Assistant patterns
- Added proper type hints and FlowResult return types

### Fixed
- Config flow handler discovery issues

## [0.1.1] - 2024-06-09

### Added
- New Home Assistant tools:
  - get_entity_state: Retrieve entity states and attributes
  - get_entities_by_domain: List entities by domain
  - set_entity_state: Directly modify entity states

### Fixed
- Fixed missing @tool import in agent.py
- Improved async/sync handling in tools.py
- Enhanced error handling and logging

### Changed
- Updated tool imports from langchain.tools to langchain_core.tools

## [0.1.0] - 2024-06-09

### Added
- Initial release of HAOS Agent Magdala
- Basic custom component structure
- Config flow for API key management
- Service registration (agent_magdala.ask)
- Event-based response system
- LangChain integration with OpenRouter and Perplexity
- Basic Home Assistant tool (call_service)
- Localization support (strings.json)

### Known Issues
- Config flow may not load properly in some environments
- Limited tool functionality