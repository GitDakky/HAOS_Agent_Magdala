"""MCP Client for Agent Magdala to communicate with Home Assistant MCP Server."""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with Home Assistant MCP Server."""
    
    def __init__(self, hass: HomeAssistant, mcp_server_url: str = "http://localhost:3001", ha_token: str = None):
        self.hass = hass
        self.mcp_server_url = mcp_server_url
        self.ha_token = ha_token or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhNTcyOWRkZGRhNjc0ZGFmYWEyZDdmNGNmOTkyM2E0YiIsImlhdCI6MTY5MzU5NzY2NywiZXhwIjoyMDA4OTU3NjY3fQ.n-W21HwVPLDbTjP0Rf0RiJdcdLjYyQVQvKX5EIr2TPA"
        self.session: Optional[aiohttp.ClientSession] = None
        self.sse_connection: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with authentication headers."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                "Authorization": f"Bearer {self.ha_token}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self.session
    
    async def close(self):
        """Close all connections."""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.sse_connection and not self.sse_connection.closed:
            await self.sse_connection.close()
    
    async def test_connection(self) -> bool:
        """Test connection to MCP server."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.mcp_server_url}/health") as response:
                if response.status == 200:
                    self.is_connected = True
                    _LOGGER.info("Successfully connected to Home Assistant MCP Server")
                    return True
                else:
                    _LOGGER.error(f"MCP Server health check failed: {response.status}")
                    return False
        except Exception as e:
            _LOGGER.error(f"Failed to connect to MCP Server: {e}")
            self.is_connected = False
            return False
    
    async def get_all_entities(self) -> List[Dict[str, Any]]:
        """Get all Home Assistant entities via MCP."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.mcp_server_url}/api/action",
                json={
                    "tool": "get_entities",
                    "action": "list_all"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("entities", [])
                else:
                    _LOGGER.error(f"Failed to get entities: {response.status}")
                    return []
        except Exception as e:
            _LOGGER.error(f"Error getting entities via MCP: {e}")
            return []
    
    async def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get entities by domain via MCP."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.mcp_server_url}/api/action",
                json={
                    "tool": "get_entities",
                    "action": "list_by_domain",
                    "domain": domain
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("entities", [])
                else:
                    _LOGGER.error(f"Failed to get {domain} entities: {response.status}")
                    return []
        except Exception as e:
            _LOGGER.error(f"Error getting {domain} entities via MCP: {e}")
            return []
    
    async def control_device(self, entity_id: str, command: str, **kwargs) -> bool:
        """Control a device via MCP."""
        try:
            session = await self._get_session()
            payload = {
                "command": command,
                "entity_id": entity_id,
                **kwargs
            }

            async with session.post(
                f"{self.mcp_server_url}/control",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        _LOGGER.info(f"Successfully controlled {entity_id}: {command}")
                        return True
                    else:
                        _LOGGER.error(f"MCP control failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    _LOGGER.error(f"Failed to control {entity_id}: {response.status}")
                    return False
        except Exception as e:
            _LOGGER.error(f"Error controlling device via MCP: {e}")
            return False
    
    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity state via MCP."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.mcp_server_url}/api/action",
                json={
                    "tool": "get_state",
                    "entity_id": entity_id
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("state")
                else:
                    _LOGGER.error(f"Failed to get state for {entity_id}: {response.status}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Error getting entity state via MCP: {e}")
            return None
    
    async def create_automation(self, automation_config: Dict[str, Any]) -> bool:
        """Create automation via MCP."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.mcp_server_url}/api/action",
                json={
                    "tool": "automation_config",
                    "action": "create",
                    "config": automation_config
                }
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Successfully created automation via MCP")
                    return True
                else:
                    _LOGGER.error(f"Failed to create automation: {response.status}")
                    return False
        except Exception as e:
            _LOGGER.error(f"Error creating automation via MCP: {e}")
            return False
    
    async def get_areas(self) -> List[Dict[str, Any]]:
        """Get all areas via MCP."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.mcp_server_url}/api/action",
                json={
                    "tool": "get_areas",
                    "action": "list_all"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("areas", [])
                else:
                    _LOGGER.error(f"Failed to get areas: {response.status}")
                    return []
        except Exception as e:
            _LOGGER.error(f"Error getting areas via MCP: {e}")
            return []
    
    async def subscribe_to_events(self, callback, domains: Optional[List[str]] = None):
        """Subscribe to real-time events via SSE."""
        try:
            url = f"{self.mcp_server_url}/subscribe_events"
            if domains:
                url += f"?domain={','.join(domains)}"
            
            self.sse_connection = aiohttp.ClientSession()
            
            async with self.sse_connection.get(url) as response:
                if response.status == 200:
                    _LOGGER.info("Connected to MCP Server SSE stream")
                    async for line in response.content:
                        if line:
                            try:
                                # Parse SSE data
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data = json.loads(line_str[6:])
                                    await callback(data)
                            except Exception as e:
                                _LOGGER.error(f"Error parsing SSE data: {e}")
                else:
                    _LOGGER.error(f"Failed to connect to SSE stream: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error in SSE subscription: {e}")
    
    async def interpret_natural_language(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interpret natural language commands via MCP."""
        try:
            session = await self._get_session()
            payload = {
                "input": input_text,
                "context": context or {},
                "model": "claude"
            }

            async with session.post(
                f"{self.mcp_server_url}/interpret",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.info(f"Successfully interpreted: {input_text}")
                    return data
                else:
                    _LOGGER.error(f"Failed to interpret command: {response.status}")
                    return {}
        except Exception as e:
            _LOGGER.error(f"Error interpreting natural language via MCP: {e}")
            return {}

    async def get_system_info(self) -> Dict[str, Any]:
        """Get Home Assistant system information via MCP."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.mcp_server_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    _LOGGER.error(f"Failed to get system info: {response.status}")
                    return {}
        except Exception as e:
            _LOGGER.error(f"Error getting system info via MCP: {e}")
            return {}


class MCPError(Exception):
    """Custom exception for MCP-related errors."""
    pass
