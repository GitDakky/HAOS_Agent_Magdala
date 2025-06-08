# Home Assistant AI Agent - Project Outline

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

### 2.2. Backend - AI Agent Custom Integration
*   **Location:** `custom_components/ai_agent/`
*   **Core Files:**
    *   `manifest.json`: Defines the integration.
    *   `__init__.py`: Main setup, initializes API clients (OpenRouter, Perplexity), sets up communication listeners.
    *   `config_flow.py`: For user to input API keys (OpenRouter, Perplexity) and other settings.
    *   `api_clients.py` (or similar): Wrapper classes for OpenRouter and Perplexity APIs.
    *   `agent_logic.py` (or similar): Contains the core orchestration logic:
        *   Receives user query from frontend.
        *   Decides if research is needed.
        *   Calls Perplexity for research.
        *   Calls OpenRouter for planning and action formulation.
        *   Interacts with Home Assistant core.
    *   `ha_actions.py` (or similar): Module for specific Home Assistant interactions (calling services, modifying configs, dashboard management via WebSocket).
*   **Communication:**
    *   Listen for messages from the Chat UI.
    *   Make outbound HTTP requests to LLM APIs.
    *   Interact with Home Assistant Core (see below).

### 2.3. LLM Integration
*   **OpenRouter Client:** Handles authentication and requests to various models available via OpenRouter for core reasoning and planning.
*   **Perplexity Client:** Handles authentication and requests to Perplexity Sonar API for research tasks.

## 3. Key Agent Capabilities & Home Assistant Interactions

### 3.1. Calling Home Assistant Services
*   **Method:** `self.hass.services.async_call()`
*   **Use Cases:** Controlling entities, triggering automations/scripts, reloading configurations, etc.

### 3.2. Modifying Configuration Files (YAML)
*   **Method:** Python file I/O operations.
*   **Target Files:** `configuration.yaml`, `automations.yaml`, `scripts.yaml`, user-defined YAML includes.
*   **Process:**
    1.  Read file.
    2.  Parse YAML.
    3.  Modify data structure.
    4.  Serialize back to YAML.
    5.  Write file.
    6.  Call relevant `homeassistant.reload_config_entry` or core config reload service.
*   **Caution:** High risk; requires robust parsing, validation, and backup strategy.

### 3.3. Managing Lovelace Dashboards (Storage Mode)
*   **Method:** Utilize Home Assistant's WebSocket API.
*   **Key WebSocket Commands:**
    *   `lovelace/dashboards`: List dashboards.
    *   `lovelace/config`: Get current configuration of a specific dashboard (returns JSON).
    *   `lovelace/config/save`: Save a new or modified dashboard configuration (takes JSON).
*   **Process:**
    1.  Agent backend connects to HA WebSocket API (or uses `hass` object wrappers).
    2.  Fetch dashboard list/config.
    3.  LLM helps formulate desired JSON changes (e.g., new card, view, layout modification).
    4.  Agent sends updated JSON via `lovelace/config/save`.
*   **Challenge:** Discovering and correctly using the exact JSON structure and WebSocket message formats used by the HA frontend. Requires inspection of frontend code or live WebSocket traffic.

### 3.4. Managing Lovelace Dashboards (YAML Mode)
*   **Method:** Python file I/O (similar to other YAML configurations).
*   **Target Files:** `ui-lovelace.yaml` or files in a user-configured `dashboards/` directory.

### 3.5. Triggering Setup of Other Integrations
*   **Challenge:** No direct, generic API to trigger arbitrary `config_flow` for other integrations.
*   **Potential Approaches:**
    *   Guide user through UI steps via chat.
    *   If target integration offers a setup service, call it.
    *   For YAML-configured integrations, modify `configuration.yaml`.

### 3.6. Creating Helper Entities
*   **Method:** Modify `configuration.yaml` (e.g., to add `input_boolean:`, `sensor: - platform: template`, etc.) and then call the relevant reload service for that domain.

## 4. Development Phases (Suggested)

1.  **Phase 1: Core Backend & LLM Comms**
    *   Set up custom component structure.
    *   Implement API clients for OpenRouter and Perplexity.
    *   Basic `config_flow.py` for API keys.
    *   Simple mechanism to receive a text query (e.g., a service call) and get responses from both LLMs.
2.  **Phase 2: Basic Home Assistant Interaction**
    *   Implement ability to call HA services based on LLM output.
    *   Implement ability to read HA entity states.
3.  **Phase 3: Chat UI**
    *   Develop the custom panel/card for chat.
    *   Establish communication between Chat UI and Agent Backend.
4.  **Phase 4: Advanced HA Interactions**
    *   YAML configuration modification (with safety checks).
    *   Lovelace dashboard management (start with reading, then cautious modification via WebSocket API).
5.  **Phase 5: Refinement & Safety**
    *   Robust error handling.
    *   User confirmations for destructive actions.
    *   Context management for conversations.
    *   Testing and documentation.

## 5. Security & Stability Considerations

*   **API Key Management:** Secure storage and handling of OpenRouter/Perplexity API keys.
*   **Permissions:** The agent will have significant power. Consider if a permission model within the agent is needed.
*   **Input Sanitization/Validation:** Before acting on LLM-generated plans or code.
*   **Confirmation Prompts:** For any action that modifies configuration or state.
*   **Backup/Restore:** Advise users to have HA backups. Consider if the agent can trigger a HA backup before major operations.
*   **Rate Limiting:** For external API calls.
*   **Preventing Loops:** Ensure agent doesn't get into destructive feedback loops.

## 6. Open Questions / Research Areas

*   Exact WebSocket commands and JSON payloads for all desired Lovelace dashboard manipulations.
*   Best practices for a custom component to safely modify `.storage` files (if absolutely necessary and other methods fail).
*   Robust methods for an agent to understand the current HA configuration state to inform its actions.
*   Mechanisms for the agent to learn or be fine-tuned for Home Assistant specific tasks over time.