"""Guardian modules for Agent Magdala - Security, Wellness, and Energy monitoring."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from homeassistant.core import HomeAssistant, State
from homeassistant.const import (
    STATE_ON, STATE_OFF, STATE_OPEN, STATE_CLOSED,
    STATE_HOME, STATE_NOT_HOME, STATE_UNKNOWN
)

from .models import (
    SecurityEvent, WellnessEvent, EnergyEvent,
    GuardianConfig, GuardianAlert
)
from .memory import GuardianMemory
from .voice import GuardianVoice
from .const import LOGGER, PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL


class BaseGuardian(ABC):
    """Base class for all Guardian modules."""

    def __init__(
        self,
        hass: HomeAssistant,
        memory: GuardianMemory,
        voice: GuardianVoice,
        config: GuardianConfig
    ):
        """Initialize the base guardian."""
        self.hass = hass
        self.memory = memory
        self.voice = voice
        self.config = config
        self.mode = config.guardian_mode
        self.enabled = True
        self.last_check = datetime.now()

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the guardian module."""
        pass

    @abstractmethod
    async def handle_state_change(self, new_state: State, old_state: State) -> None:
        """Handle state changes for this guardian module."""
        pass

    @abstractmethod
    async def perform_periodic_check(self) -> None:
        """Perform periodic checks for this guardian module."""
        pass

    async def set_mode(self, mode: str) -> None:
        """Set the guardian mode."""
        self.mode = mode
        LOGGER.debug(f"{self.__class__.__name__} mode set to {mode}")

    async def shutdown(self) -> None:
        """Shutdown the guardian module."""
        self.enabled = False
        LOGGER.info(f"{self.__class__.__name__} shutdown")


class SecurityGuardian(BaseGuardian):
    """Security monitoring guardian module."""

    def __init__(self, hass: HomeAssistant, memory: GuardianMemory, voice: GuardianVoice, config: GuardianConfig):
        """Initialize the Security Guardian."""
        super().__init__(hass, memory, voice, config)
        self.monitored_entities: List[str] = []
        self.security_events: List[SecurityEvent] = []
        self.armed_state = False

    async def initialize(self) -> bool:
        """Initialize the Security Guardian."""
        try:
            # Discover security-related entities
            await self._discover_security_entities()
            
            # Load security patterns from memory
            await self._load_security_patterns()
            
            LOGGER.info(f"Security Guardian initialized with {len(self.monitored_entities)} entities")
            return True
            
        except Exception as e:
            LOGGER.error(f"Error initializing Security Guardian: {e}")
            return False

    async def _discover_security_entities(self) -> None:
        """Discover security-related entities."""
        security_domains = ["binary_sensor", "alarm_control_panel", "camera", "lock", "cover"]
        security_keywords = ["door", "window", "motion", "security", "alarm", "lock", "camera"]
        
        for state in self.hass.states.async_all():
            entity_id = state.entity_id
            domain = entity_id.split(".")[0]
            
            if domain in security_domains or any(keyword in entity_id.lower() for keyword in security_keywords):
                self.monitored_entities.append(entity_id)

    async def _load_security_patterns(self) -> None:
        """Load security patterns from memory."""
        try:
            patterns = await self.memory.search_memories(
                query="security pattern normal activity",
                filters={"category": ["pattern", "security"]}
            )
            LOGGER.debug(f"Loaded {len(patterns)} security patterns")
        except Exception as e:
            LOGGER.error(f"Error loading security patterns: {e}")

    async def handle_state_change(self, new_state: State, old_state: State) -> None:
        """Handle security-related state changes."""
        if not self.enabled or self.mode == "sleep":
            return
            
        try:
            entity_id = new_state.entity_id
            
            # Check for door/window sensors
            if "door" in entity_id or "window" in entity_id:
                await self._handle_door_window_change(new_state, old_state)
                
            # Check for motion sensors
            elif "motion" in entity_id:
                await self._handle_motion_change(new_state, old_state)
                
            # Check for lock status
            elif "lock" in entity_id:
                await self._handle_lock_change(new_state, old_state)
                
        except Exception as e:
            LOGGER.error(f"Error handling security state change: {e}")

    async def _handle_door_window_change(self, new_state: State, old_state: State) -> None:
        """Handle door/window sensor changes."""
        if new_state.state == STATE_OPEN and old_state.state == STATE_CLOSED:
            # Door/window opened
            location = self._get_location_from_entity(new_state.entity_id)
            
            # Check if this is during normal hours
            is_normal_hours = await self._is_normal_hours()
            
            if not is_normal_hours or self.mode == "active":
                event = SecurityEvent(
                    event_type="door_window_opened",
                    location=location,
                    severity=PRIORITY_MEDIUM if is_normal_hours else PRIORITY_HIGH,
                    entity_id=new_state.entity_id,
                    description=f"{location} opened"
                )
                
                await self._process_security_event(event)

    async def _handle_motion_change(self, new_state: State, old_state: State) -> None:
        """Handle motion sensor changes."""
        if new_state.state == STATE_ON and old_state.state == STATE_OFF:
            location = self._get_location_from_entity(new_state.entity_id)
            
            # Check if motion is expected
            is_expected = await self._is_motion_expected(location)
            
            if not is_expected and not await self._is_normal_hours():
                event = SecurityEvent(
                    event_type="unexpected_motion",
                    location=location,
                    severity=PRIORITY_HIGH,
                    entity_id=new_state.entity_id,
                    description=f"Unexpected motion detected in {location}"
                )
                
                await self._process_security_event(event)

    async def _handle_lock_change(self, new_state: State, old_state: State) -> None:
        """Handle lock state changes."""
        if new_state.state != old_state.state:
            location = self._get_location_from_entity(new_state.entity_id)
            action = "locked" if new_state.state == "locked" else "unlocked"
            
            event = SecurityEvent(
                event_type="lock_changed",
                location=location,
                severity=PRIORITY_LOW,
                entity_id=new_state.entity_id,
                description=f"{location} {action}"
            )
            
            await self._process_security_event(event)

    async def _process_security_event(self, event: SecurityEvent) -> None:
        """Process a security event."""
        try:
            # Store event in memory
            await self.memory.store_event(event)
            
            # Add to local events list
            self.security_events.append(event)
            
            # Voice announcement for important events
            if event.severity in [PRIORITY_HIGH, PRIORITY_CRITICAL] and self.voice:
                message = f"Security alert: {event.description}"
                if event.location:
                    message += f" in {event.location}"
                    
                await self.voice.announce(message, event.severity, event.location)
                
            LOGGER.info(f"Security event processed: {event.description}")
            
        except Exception as e:
            LOGGER.error(f"Error processing security event: {e}")

    def _get_location_from_entity(self, entity_id: str) -> str:
        """Extract location from entity ID."""
        # Simple extraction - could be enhanced with area registry
        parts = entity_id.split(".")[-1].split("_")
        return " ".join(parts[:-1]) if len(parts) > 1 else "unknown"

    async def _is_normal_hours(self) -> bool:
        """Check if current time is during normal hours (6 AM - 10 PM)."""
        current_hour = datetime.now().hour
        return 6 <= current_hour <= 22

    async def _is_motion_expected(self, location: str) -> bool:
        """Check if motion is expected in this location at this time."""
        # This would use learned patterns from memory
        # For now, return False for simplicity
        return False

    async def perform_periodic_check(self) -> None:
        """Perform periodic security checks."""
        try:
            # Check for doors/windows left open
            await self._check_open_doors_windows()
            
            # Check for unusual patterns
            await self._check_unusual_patterns()
            
            self.last_check = datetime.now()
            
        except Exception as e:
            LOGGER.error(f"Error in security periodic check: {e}")

    async def _check_open_doors_windows(self) -> None:
        """Check for doors/windows that have been open too long."""
        for entity_id in self.monitored_entities:
            if "door" in entity_id or "window" in entity_id:
                state = self.hass.states.get(entity_id)
                if state and state.state == STATE_OPEN:
                    # Check how long it's been open
                    # This is simplified - would need to track open times
                    pass

    async def _check_unusual_patterns(self) -> None:
        """Check for unusual activity patterns."""
        # This would analyze recent events against learned patterns
        pass


class WellnessGuardian(BaseGuardian):
    """Wellness and health monitoring guardian module."""

    async def initialize(self) -> bool:
        """Initialize the Wellness Guardian."""
        LOGGER.info("Wellness Guardian initialized")
        return True

    async def handle_state_change(self, new_state: State, old_state: State) -> None:
        """Handle wellness-related state changes."""
        # Placeholder implementation
        pass

    async def perform_periodic_check(self) -> None:
        """Perform periodic wellness checks."""
        # Placeholder implementation
        pass


class EnergyGuardian(BaseGuardian):
    """Energy monitoring and optimization guardian module."""

    async def initialize(self) -> bool:
        """Initialize the Energy Guardian."""
        LOGGER.info("Energy Guardian initialized")
        return True

    async def handle_state_change(self, new_state: State, old_state: State) -> None:
        """Handle energy-related state changes."""
        # Placeholder implementation
        pass

    async def perform_periodic_check(self) -> None:
        """Perform periodic energy checks."""
        # Placeholder implementation
        pass
