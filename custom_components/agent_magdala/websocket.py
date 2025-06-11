"""WebSocket API for Agent Magdala chat interface."""
import logging
from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback
from homeassistant.components import websocket_api
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@callback
def async_register_websocket_handlers(hass: HomeAssistant) -> None:
    """Register WebSocket handlers for Agent Magdala."""
    try:
        websocket_api.async_register_command(hass, websocket_chat_message)
        websocket_api.async_register_command(hass, websocket_get_conversations)
        websocket_api.async_register_command(hass, websocket_get_agent_status)
        _LOGGER.info("Agent Magdala WebSocket handlers registered")
    except Exception as e:
        _LOGGER.error(f"Failed to register WebSocket handlers: {e}")


@websocket_api.websocket_command({
    vol.Required("type"): "agent_magdala/chat",
    vol.Required("message"): str,
    vol.Optional("conversation_id"): str,
})
@websocket_api.async_response
async def websocket_chat_message(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: Dict[str, Any]
) -> None:
    """Handle chat message via WebSocket."""
    try:
        # Get the agent instance
        agent = hass.data.get(DOMAIN, {}).get("agent")
        if not agent:
            connection.send_error(msg["id"], "agent_not_found", "Agent not initialized")
            return

        message = msg["message"]
        conversation_id = msg.get("conversation_id")

        _LOGGER.debug(f"WebSocket chat message: {message}")

        # Send typing indicator
        connection.send_message({
            "id": msg["id"],
            "type": "result",
            "success": True,
            "result": {
                "type": "typing",
                "conversation_id": conversation_id,
                "timestamp": agent.status.last_activity.isoformat() if agent.status.last_activity else None
            }
        })

        # Process the message through the agent
        response = await agent.ask(message, conversation_id)

        # Send the response
        connection.send_message({
            "id": msg["id"],
            "type": "result",
            "success": True,
            "result": {
                "type": "message",
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": agent.status.last_activity.isoformat() if agent.status.last_activity else None,
                "agent_status": agent.status.health_status
            }
        })

    except Exception as e:
        _LOGGER.error(f"WebSocket chat error: {e}")
        connection.send_error(
            msg["id"], 
            "chat_error", 
            f"Failed to process message: {type(e).__name__}"
        )


@websocket_api.websocket_command({
    vol.Required("type"): "agent_magdala/conversations",
    vol.Optional("limit", default=10): int,
})
@websocket_api.async_response
async def websocket_get_conversations(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: Dict[str, Any]
) -> None:
    """Get conversation history via WebSocket."""
    try:
        # Get the agent instance
        agent = hass.data.get(DOMAIN, {}).get("agent")
        if not agent:
            connection.send_error(msg["id"], "agent_not_found", "Agent not initialized")
            return

        limit = msg.get("limit", 10)
        conversations = []

        # Get recent conversations
        for conv_id, context in list(agent._conversation_contexts.items())[-limit:]:
            conversations.append({
                "id": conv_id,
                "started_at": context.started_at.isoformat() if context.started_at else None,
                "last_activity": context.last_activity.isoformat() if context.last_activity else None,
                "message_count": len(context.messages),
                "preview": context.messages[-1]["content"][:100] + "..." if context.messages else ""
            })

        connection.send_message({
            "id": msg["id"],
            "type": "result",
            "success": True,
            "result": {
                "conversations": conversations,
                "total": len(agent._conversation_contexts)
            }
        })

    except Exception as e:
        _LOGGER.error(f"WebSocket conversations error: {e}")
        connection.send_error(
            msg["id"], 
            "conversations_error", 
            f"Failed to get conversations: {type(e).__name__}"
        )


@websocket_api.websocket_command({
    vol.Required("type"): "agent_magdala/status",
})
@websocket_api.async_response
async def websocket_get_agent_status(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: Dict[str, Any]
) -> None:
    """Get agent status via WebSocket."""
    try:
        # Get the agent instance
        agent = hass.data.get(DOMAIN, {}).get("agent")
        if not agent:
            connection.send_error(msg["id"], "agent_not_found", "Agent not initialized")
            return

        status = {
            "health_status": agent.status.health_status,
            "mode": agent.status.mode,
            "active_modules": agent.status.active_modules,
            "last_activity": agent.status.last_activity.isoformat() if agent.status.last_activity else None,
            "conversation_count": len(agent._conversation_contexts),
            "llm_available": agent.llm_client is not None,
            "api_connected": agent.llm_client is not None and agent.config.openrouter_api_key is not None
        }

        connection.send_message({
            "id": msg["id"],
            "type": "result",
            "success": True,
            "result": status
        })

    except Exception as e:
        _LOGGER.error(f"WebSocket status error: {e}")
        connection.send_error(
            msg["id"], 
            "status_error", 
            f"Failed to get status: {type(e).__name__}"
        )
