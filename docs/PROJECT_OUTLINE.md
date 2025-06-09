# HAOS Agent Magdala - Project Outline

## Current Status (v0.3.0)

**Implementation Progress:**
- ✅ Basic custom component structure
- ✅ Config flow for API key management
- ✅ Service registration (`agent_magdala.ask`)
- ✅ Event-based response system
- ⚠️ LangChain integration (temporarily disabled)
- ❌ Chat UI interface
- ❌ Advanced Home Assistant interactions

## 1. Concept Overview

*   **Goal:** Create a conversational AI agent within Home Assistant to assist users with managing and configuring their Home Assistant instance.
*   **User Interface:** A chat window (custom panel or Lovelace card) within Home Assistant.
*   **Core LLM:** Utilize OpenRouter API for primary natural language understanding, reasoning, and task execution logic.
*   **Research LLM:** Utilize Perplexity Sonar API for researching Home Assistant specific procedures, configurations, and integration methods.
*   **Capabilities:**
    *   Understand natural language requests related to Home Assistant management (e.g., creating dashboards, adding integrations, modifying configurations, optimizing automations).
    *   Use Perplexity to research "how-to" information for specific Home Assistant tasks.
    *   Use OpenRouter to formulate plans and specific actions (API calls, file modifications, service calls).
    *   Execute these actions to modify Home Assistant settings.
    *   Provide feedback and results to the user via the chat interface.

## 2. Core Components

### 2.1. Frontend - Chat User Interface
*   **Type:** Custom Panel (iframe) or Custom Lovelace Card.
*   **Technology:** HTML, CSS, JavaScript.
*   **Functionality:**
    *   Display chat history.
    *   Accept user input.
    *   Communicate with the agent's backend (Python custom component) likely via Home Assistant's WebSocket API or a dedicated WebSocket/HTTP endpoint provided by the agent.
    *   Render responses from the agent.
*   **Status:** Not yet implemented. Basic HTML structure exists in `www/index.html`.

### 2.2. Backend - AI Agent Custom Integration
*   **Location:** `custom_components/agent_magdala/`
*   **Core Files:**
    *   ✅ `manifest.json`: Defines the integration.
    *   ✅ `__init__.py`: Main setup, initializes service, sets up event system.
    *   ✅ `config_flow.py`: For user to input API keys (OpenRouter, Perplexity) and other settings.
    *   ⚠️ `agent.py`: Contains the agent logic (currently disabled).
    *   ⚠️ `tools.py`: Home Assistant interaction tools (currently disabled).
    *   ✅ `const.py`: Constants and configuration values.
    *   ✅ `strings.json` & `translations/`: Localization support.
*   **Communication:**
    *   Listen for service calls (`agent_magdala.ask`).
    *   Fire events with responses (`agent_magdala_response`).
    *   Make outbound HTTP requests to LLM APIs (disabled).
    *   Interact with Home Assistant Core (disabled).

### 2.3. LLM Integration
*   **OpenRouter Client:** Handles authentication and requests to various models available via OpenRouter for core reasoning and planning.
*   **Perplexity Client:** Handles authentication and requests to Perplexity Sonar API for research tasks.
*   **Status:** Temporarily disabled due to dependency conflicts with LangChain.

## 3. Key Agent Capabilities & Home Assistant Interactions

### 3.1. Implemented Tools (Currently Disabled)
*   **call_service:** Execute any Home Assistant service
*   **get_entity_state:** Retrieve entity states and attributes
*   **get_entities_by_domain:** List entities by domain
*   **set_entity_state:** Directly modify entity states

### 3.2. Planned Capabilities
*   **Modifying Configuration Files (YAML)**
*   **Managing Lovelace Dashboards**
*   **Creating Helper Entities**
*   **Triggering Setup of Other Integrations**

## 4. Development Phases (Updated)

1.  **Phase 1: Core Backend & LLM Comms** ✅ (Partially Complete)
    *   ✅ Set up custom component structure.
    *   ⚠️ Implement API clients for OpenRouter and Perplexity (disabled).
    *   ✅ Basic `config_flow.py` for API keys.
    *   ⚠️ Simple mechanism to receive a text query and get responses from both LLMs (disabled).

2.  **Phase 2: Basic Home Assistant Interaction** ⚠️ (Partially Complete)
    *   ⚠️ Implement ability to call HA services based on LLM output (disabled).
    *   ⚠️ Implement ability to read HA entity states (disabled).

3.  **Phase 3: Chat UI** ❌ (Not Started)
    *   Develop the custom panel/card for chat.
    *   Establish communication between Chat UI and Agent Backend.

4.  **Phase 4: Advanced HA Interactions** ❌ (Not Started)
    *   YAML configuration modification (with safety checks).
    *   Lovelace dashboard management (start with reading, then cautious modification via WebSocket API).

5.  **Phase 5: Refinement & Safety** ❌ (Not Started)
    *   Robust error handling.
    *   User confirmations for destructive actions.
    *   Context management for conversations.
    *   Testing and documentation.

## 5. Current Technical Challenges

1.  **Dependency Conflicts:** LangChain and its dependencies conflict with Home Assistant's environment, causing import errors.
2.  **Config Flow Loading:** Initial issues with config flow discovery have been resolved.
3.  **Async/Sync Bridge:** Proper handling of async Home Assistant calls from synchronous LangChain tools.

## 6. Immediate Next Steps

1.  **Resolve Dependency Issues:**
    *   Investigate compatible versions of LangChain with Home Assistant
    *   Consider alternative LLM integration approaches
    *   Implement lazy loading or optional imports

2.  **Re-enable Core Functionality:**
    *   Restore agent.py functionality
    *   Re-implement tools.py with proper async handling
    *   Test basic service calls and entity queries

3.  **Implement Basic UI:**
    *   Create simple chat interface
    *   Implement WebSocket or REST communication
    *   Add conversation history display

## 7. Security & Stability Considerations

*   **API Key Management:** Secure storage and handling of OpenRouter/Perplexity API keys.
*   **Permissions:** The agent will have significant power. Consider if a permission model within the agent is needed.
*   **Input Sanitization/Validation:** Before acting on LLM-generated plans or code.
*   **Confirmation Prompts:** For any action that modifies configuration or state.
*   **Backup/Restore:** Advise users to have HA backups. Consider if the agent can trigger a HA backup before major operations.
*   **Rate Limiting:** For external API calls.
*   **Preventing Loops:** Ensure agent doesn't get into destructive feedback loops.

## 8. Open Questions / Research Areas

*   Best approach to resolve LangChain dependency conflicts with Home Assistant
*   Alternative LLM integration libraries that might be more compatible
*   Exact WebSocket commands and JSON payloads for all desired Lovelace dashboard manipulations
*   Best practices for a custom component to safely modify `.storage` files
*   Mechanisms for the agent to learn or be fine-tuned for Home Assistant specific tasks over time