"""The core of Agent Magdala's logic."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_perplexity import ChatPerplexity
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from .const import (
    DOMAIN,
    LOGGER,
    CONF_OPENROUTER_API_KEY,
    CONF_PERPLEXITY_API_KEY,
    CONF_OPENROUTER_MODEL,
)

# This is a placeholder for our conversation history.
# In a real implementation, this would need to be persisted.
conversation_history = {}

from .tools import HomeAssistantToolFactory


class MagdalaAgent:
    """The main class for Agent Magdala."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.agent_executor = self._create_agent_executor()

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        openrouter_api_key = self.entry.data.get(CONF_OPENROUTER_API_KEY)
        openrouter_model = self.entry.data.get(CONF_OPENROUTER_MODEL)

        # Set up the primary LLM via OpenRouter
        llm = ChatOpenAI(
            model=openrouter_model,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
        )

        # Define the tools the agent can use
        tool_factory = HomeAssistantToolFactory(self.hass)
        tools = tool_factory.get_tools()

        # Create the agent prompt
        # This is a very basic prompt and will need significant refinement.
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful Home Assistant agent named HAOS Agent Magdala. You have access to tools to interact with Home Assistant."),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        # Create the agent itself
        agent = create_tool_calling_agent(llm, tools, prompt)

        # Create the agent executor
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

    async def get_response(self, prompt: str, conversation_id: str | None = None) -> str:
        """Get a response from the agent for a given prompt."""
        LOGGER.debug(f"Agent received prompt: {prompt}")

        try:
            # Invoke the agent executor
            # Note: LangChain's invoke is blocking. For a real HA integration,
            # we must run this in an executor to avoid blocking the event loop.
            response = await self.hass.async_add_executor_job(
                self.agent_executor.invoke, {"input": prompt}
            )

            output = response.get("output", "Sorry, I encountered an error.")
            LOGGER.debug(f"Agent generated response: {output}")
            
            # Here, we would typically send the response back to the user,
            # e.g., via a persistent notification, a chat UI update, or a service response.
            # For now, we'll just log it.
            self.hass.components.persistent_notification.async_create(
                message=output, title="HAOS Agent Magdala Response"
            )

            return output

        except Exception as e:
            LOGGER.error(f"Error during agent execution: {e}", exc_info=True)
            return "Sorry, I encountered an error while processing your request."