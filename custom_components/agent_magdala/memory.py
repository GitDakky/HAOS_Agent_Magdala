"""Memory management system using Mem0 for Agent Magdala Guardian."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import aiohttp
import json

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .models import (
    MemoryEntry,
    UserPattern,
    SecurityEvent,
    WellnessEvent,
    EnergyEvent,
    ConversationContext,
    AlertEvent,
)
from .const import LOGGER

class GuardianMemory:
    """Memory management system for the Guardian Agent using Mem0."""

    def __init__(self, hass: HomeAssistant, api_key: str):
        """Initialize the memory system."""
        self.hass = hass
        self.api_key = api_key
        self.base_url = "https://api.mem0.ai/v1"
        self.session = async_get_clientsession(hass)
        self._memory_cache: Dict[str, MemoryEntry] = {}
        self._pattern_cache: Dict[str, UserPattern] = {}
        
    async def initialize(self) -> bool:
        """Initialize the memory system and verify connectivity."""
        try:
            # Test connection to Mem0
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.base_url}/memories",
                headers=headers,
                params={"limit": 1}
            ) as response:
                if response.status == 200:
                    LOGGER.info("Mem0 connection established successfully")
                    await self._load_cached_memories()
                    return True
                else:
                    LOGGER.error(f"Failed to connect to Mem0: {response.status}")
                    return False
                    
        except Exception as e:
            LOGGER.error(f"Error initializing Mem0 connection: {e}")
            return False

    async def _load_cached_memories(self) -> None:
        """Load frequently accessed memories into cache."""
        try:
            # Load recent patterns and important memories
            recent_memories = await self.search_memories(
                query="pattern OR preference OR routine",
                limit=50,
                filters={"category": ["pattern", "preference", "routine"]}
            )
            
            for memory in recent_memories:
                self._memory_cache[memory.memory_id] = memory
                
            LOGGER.debug(f"Loaded {len(recent_memories)} memories into cache")
            
        except Exception as e:
            LOGGER.error(f"Error loading cached memories: {e}")

    async def add_memory(
        self,
        content: str,
        category: str,
        user_id: Optional[str] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Optional[MemoryEntry]:
        """Add a new memory to the system."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            memory_data = {
                "content": content,
                "metadata": {
                    "category": category,
                    "user_id": user_id,
                    "importance": importance,
                    "tags": tags or [],
                    "custom_metadata": metadata or {},
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "created_by": "guardian_agent"
                }
            }
            
            if user_id:
                memory_data["user_id"] = user_id
                
            async with self.session.post(
                f"{self.base_url}/memories",
                headers=headers,
                json=memory_data
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    memory_entry = MemoryEntry(
                        memory_id=result["id"],
                        content=content,
                        category=category,
                        user_id=user_id,
                        importance=importance,
                        tags=tags or [],
                        metadata=metadata or {},
                        expires_at=expires_at
                    )
                    
                    # Cache important memories
                    if importance > 0.7:
                        self._memory_cache[memory_entry.memory_id] = memory_entry
                        
                    LOGGER.debug(f"Added memory: {memory_entry.memory_id}")
                    return memory_entry
                else:
                    LOGGER.error(f"Failed to add memory: {response.status}")
                    return None
                    
        except Exception as e:
            LOGGER.error(f"Error adding memory: {e}")
            return None

    async def search_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Search for memories based on query and filters."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            search_data = {
                "query": query,
                "limit": limit
            }
            
            if user_id:
                search_data["user_id"] = user_id
                
            if filters:
                search_data["filters"] = filters
                
            async with self.session.post(
                f"{self.base_url}/memories/search",
                headers=headers,
                json=search_data
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    memories = []
                    
                    for result in results.get("memories", []):
                        memory = MemoryEntry(
                            memory_id=result["id"],
                            content=result["content"],
                            category=result.get("metadata", {}).get("category", "general"),
                            user_id=result.get("user_id"),
                            importance=result.get("metadata", {}).get("importance", 0.5),
                            tags=result.get("metadata", {}).get("tags", []),
                            metadata=result.get("metadata", {}).get("custom_metadata", {}),
                            timestamp=datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
                        )
                        memories.append(memory)
                        
                    return memories
                else:
                    LOGGER.error(f"Failed to search memories: {response.status}")
                    return []
                    
        except Exception as e:
            LOGGER.error(f"Error searching memories: {e}")
            return []

    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        # Check cache first
        if memory_id in self._memory_cache:
            return self._memory_cache[memory_id]
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.base_url}/memories/{memory_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    memory = MemoryEntry(
                        memory_id=result["id"],
                        content=result["content"],
                        category=result.get("metadata", {}).get("category", "general"),
                        user_id=result.get("user_id"),
                        importance=result.get("metadata", {}).get("importance", 0.5),
                        tags=result.get("metadata", {}).get("tags", []),
                        metadata=result.get("metadata", {}).get("custom_metadata", {}),
                        timestamp=datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
                    )
                    
                    # Cache the memory
                    self._memory_cache[memory_id] = memory
                    return memory
                else:
                    LOGGER.error(f"Failed to get memory {memory_id}: {response.status}")
                    return None
                    
        except Exception as e:
            LOGGER.error(f"Error getting memory {memory_id}: {e}")
            return None

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.delete(
                f"{self.base_url}/memories/{memory_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    # Remove from cache
                    self._memory_cache.pop(memory_id, None)
                    LOGGER.debug(f"Deleted memory: {memory_id}")
                    return True
                else:
                    LOGGER.error(f"Failed to delete memory {memory_id}: {response.status}")
                    return False
                    
        except Exception as e:
            LOGGER.error(f"Error deleting memory {memory_id}: {e}")
            return False

    async def learn_pattern(self, pattern: UserPattern) -> bool:
        """Learn a new user pattern."""
        try:
            content = f"User {pattern.user_id} {pattern.pattern_type}: {json.dumps(pattern.pattern_data)}"
            
            memory = await self.add_memory(
                content=content,
                category="pattern",
                user_id=pattern.user_id,
                importance=pattern.confidence,
                tags=[pattern.pattern_type, "pattern", "learned"],
                metadata={
                    "pattern_type": pattern.pattern_type,
                    "confidence": pattern.confidence,
                    "occurrences": pattern.occurrences,
                    "pattern_data": pattern.pattern_data
                }
            )
            
            if memory:
                self._pattern_cache[f"{pattern.user_id}_{pattern.pattern_type}"] = pattern
                LOGGER.info(f"Learned pattern: {pattern.pattern_type} for user {pattern.user_id}")
                return True
            return False
            
        except Exception as e:
            LOGGER.error(f"Error learning pattern: {e}")
            return False

    async def get_user_patterns(self, user_id: str, pattern_type: Optional[str] = None) -> List[UserPattern]:
        """Get learned patterns for a user."""
        try:
            query = f"user {user_id} pattern"
            if pattern_type:
                query += f" {pattern_type}"
                
            memories = await self.search_memories(
                query=query,
                user_id=user_id,
                filters={"category": ["pattern"]}
            )
            
            patterns = []
            for memory in memories:
                if "pattern_type" in memory.metadata:
                    pattern = UserPattern(
                        user_id=user_id,
                        pattern_type=memory.metadata["pattern_type"],
                        pattern_data=memory.metadata.get("pattern_data", {}),
                        confidence=memory.metadata.get("confidence", 0.5),
                        last_updated=memory.timestamp,
                        occurrences=memory.metadata.get("occurrences", 1)
                    )
                    patterns.append(pattern)
                    
            return patterns
            
        except Exception as e:
            LOGGER.error(f"Error getting user patterns: {e}")
            return []

    async def store_event(self, event: AlertEvent) -> bool:
        """Store a security, wellness, or energy event."""
        try:
            event_data = event.dict()
            content = f"{event.__class__.__name__}: {event.description}"
            
            memory = await self.add_memory(
                content=content,
                category="event",
                importance=self._get_event_importance(event),
                tags=[event.__class__.__name__.lower(), "event"],
                metadata=event_data
            )
            
            return memory is not None
            
        except Exception as e:
            LOGGER.error(f"Error storing event: {e}")
            return False

    def _get_event_importance(self, event: AlertEvent) -> float:
        """Calculate importance score for an event."""
        if hasattr(event, 'severity'):
            severity_map = {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "critical": 1.0
            }
            return severity_map.get(event.severity, 0.5)
        return 0.5

    async def get_context_for_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get relevant context for a query."""
        try:
            # Search for relevant memories
            memories = await self.search_memories(
                query=query,
                user_id=user_id,
                limit=5
            )
            
            # Get recent patterns if user specified
            patterns = []
            if user_id:
                patterns = await self.get_user_patterns(user_id)
                
            context = {
                "relevant_memories": [m.dict() for m in memories],
                "user_patterns": [p.dict() for p in patterns[:3]],  # Top 3 patterns
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            
            return context
            
        except Exception as e:
            LOGGER.error(f"Error getting context for query: {e}")
            return {"query": query, "timestamp": datetime.now().isoformat()}

    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memories and return count of deleted memories."""
        try:
            # This would need to be implemented based on Mem0's API capabilities
            # For now, we'll clean up local cache
            expired_count = 0
            current_time = datetime.now()
            
            expired_keys = []
            for key, memory in self._memory_cache.items():
                if memory.expires_at and memory.expires_at < current_time:
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self._memory_cache[key]
                expired_count += 1
                
            if expired_count > 0:
                LOGGER.info(f"Cleaned up {expired_count} expired memories from cache")
                
            return expired_count
            
        except Exception as e:
            LOGGER.error(f"Error cleaning up expired memories: {e}")
            return 0
