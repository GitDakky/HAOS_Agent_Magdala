"""Voice communication system for Agent Magdala Guardian."""
import asyncio
import logging
from datetime import datetime, time
from typing import Any, Dict, List, Optional
import re

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .models import VoiceAnnouncement, GuardianAlert
from .const import (
    LOGGER,
    AlertPriority,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
    DEFAULT_TTS_SERVICE,
)


class GuardianVoice:
    """Voice communication system for the Guardian Agent."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the voice system."""
        self.hass = hass
        self.tts_service = config.get("tts_service", DEFAULT_TTS_SERVICE)
        self.voice_announcements = config.get("voice_announcements", True)
        self.quiet_hours_start = config.get("quiet_hours_start")
        self.quiet_hours_end = config.get("quiet_hours_end")
        
        # Speaker mapping for different locations
        self.location_speakers: Dict[str, List[str]] = {}
        self.all_speakers: List[str] = []
        
        # Voice personality settings
        self.personality = {
            "greeting": "Hello",
            "emergency_prefix": "URGENT ALERT",
            "security_prefix": "Security Notice",
            "wellness_prefix": "Wellness Reminder",
            "energy_prefix": "Energy Update",
            "confirmation": "Understood",
            "error": "I apologize, but I encountered an issue"
        }
        
    async def initialize(self) -> bool:
        """Initialize the voice system and discover speakers."""
        try:
            await self._discover_speakers()
            await self._test_tts_service()
            LOGGER.info(f"Voice system initialized with {len(self.all_speakers)} speakers")
            return True
        except Exception as e:
            LOGGER.error(f"Error initializing voice system: {e}")
            return False

    async def _discover_speakers(self) -> None:
        """Discover available speakers and organize by location."""
        try:
            entity_registry = async_get_entity_registry(self.hass)
            
            # Find all media player entities that support TTS
            media_players = []
            for entity_id, entity in entity_registry.entities.items():
                if entity_id.startswith("media_player."):
                    state = self.hass.states.get(entity_id)
                    if state and hasattr(state, 'attributes'):
                        supported_features = state.attributes.get('supported_features', 0)
                        # Check if TTS is supported (feature flag 128)
                        if supported_features & 128:
                            media_players.append(entity_id)
            
            self.all_speakers = media_players
            
            # Organize speakers by room/area
            device_registry = async_get_device_registry(self.hass)
            for entity_id in media_players:
                entity = entity_registry.entities.get(entity_id)
                if entity and entity.device_id:
                    device = device_registry.devices.get(entity.device_id)
                    if device and device.area_id:
                        area_name = device.area_id.lower()
                        if area_name not in self.location_speakers:
                            self.location_speakers[area_name] = []
                        self.location_speakers[area_name].append(entity_id)
                        
            LOGGER.debug(f"Discovered speakers by location: {self.location_speakers}")
            
        except Exception as e:
            LOGGER.error(f"Error discovering speakers: {e}")

    async def _test_tts_service(self) -> bool:
        """Test if the configured TTS service is available."""
        try:
            # Check if TTS service exists
            if not self.hass.services.has_service("tts", self.tts_service.split(".")[-1]):
                LOGGER.warning(f"TTS service {self.tts_service} not found, using default")
                self.tts_service = "tts.speak"
                
            return True
        except Exception as e:
            LOGGER.error(f"Error testing TTS service: {e}")
            return False

    async def announce(
        self,
        message: str,
        priority: AlertPriority = PRIORITY_LOW,
        location: Optional[str] = None,
        repeat_count: int = 1,
        delay_seconds: Optional[int] = None
    ) -> bool:
        """Make a voice announcement."""
        if not self.voice_announcements:
            LOGGER.debug("Voice announcements disabled")
            return False
            
        if self._is_quiet_hours() and priority not in [PRIORITY_HIGH, PRIORITY_CRITICAL]:
            LOGGER.debug("Skipping announcement during quiet hours")
            return False
            
        try:
            announcement = VoiceAnnouncement(
                message=message,
                priority=priority,
                location=location,
                repeat_count=repeat_count,
                delay_seconds=delay_seconds
            )
            
            # Add delay if specified
            if delay_seconds:
                await asyncio.sleep(delay_seconds)
                
            # Format message based on priority
            formatted_message = self._format_message(message, priority)
            
            # Determine target speakers
            target_speakers = self._get_target_speakers(location, priority)
            
            if not target_speakers:
                LOGGER.warning("No target speakers found for announcement")
                return False
                
            # Make the announcement
            success = await self._speak_to_speakers(
                formatted_message,
                target_speakers,
                priority,
                repeat_count
            )
            
            if success:
                LOGGER.info(f"Voice announcement delivered: {message[:50]}...")
            else:
                LOGGER.error("Failed to deliver voice announcement")
                
            return success
            
        except Exception as e:
            LOGGER.error(f"Error making announcement: {e}")
            return False

    def _format_message(self, message: str, priority: AlertPriority) -> str:
        """Format message based on priority and personality."""
        prefix = ""
        
        if priority == PRIORITY_CRITICAL:
            prefix = f"{self.personality['emergency_prefix']}! "
        elif priority == PRIORITY_HIGH:
            prefix = f"{self.personality['security_prefix']}: "
        elif "security" in message.lower():
            prefix = f"{self.personality['security_prefix']}: "
        elif "medication" in message.lower() or "health" in message.lower():
            prefix = f"{self.personality['wellness_prefix']}: "
        elif "energy" in message.lower() or "power" in message.lower():
            prefix = f"{self.personality['energy_prefix']}: "
            
        return f"{prefix}{message}"

    def _get_target_speakers(self, location: Optional[str], priority: AlertPriority) -> List[str]:
        """Determine which speakers to use for the announcement."""
        if priority == PRIORITY_CRITICAL:
            # Use all speakers for critical alerts
            return self.all_speakers
            
        if location and location.lower() in self.location_speakers:
            # Use speakers in specified location
            return self.location_speakers[location.lower()]
            
        if location == "all" or priority == PRIORITY_HIGH:
            # Use all speakers for high priority or explicit "all"
            return self.all_speakers
            
        # Default to living room or first available speaker
        if "living_room" in self.location_speakers:
            return self.location_speakers["living_room"]
        elif "main" in self.location_speakers:
            return self.location_speakers["main"]
        elif self.all_speakers:
            return [self.all_speakers[0]]
            
        return []

    async def _speak_to_speakers(
        self,
        message: str,
        speakers: List[str],
        priority: AlertPriority,
        repeat_count: int = 1
    ) -> bool:
        """Send TTS message to specified speakers."""
        try:
            # Prepare TTS options based on priority
            tts_options = self._get_tts_options(priority)
            
            # Send to each speaker
            tasks = []
            for speaker in speakers:
                for _ in range(repeat_count):
                    task = self._send_tts_to_speaker(speaker, message, tts_options)
                    tasks.append(task)
                    
            # Execute all TTS calls
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if at least one succeeded
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            
            return success_count > 0
            
        except Exception as e:
            LOGGER.error(f"Error speaking to speakers: {e}")
            return False

    async def _send_tts_to_speaker(
        self,
        speaker: str,
        message: str,
        options: Dict[str, Any]
    ) -> bool:
        """Send TTS message to a single speaker."""
        try:
            service_data = {
                "entity_id": speaker,
                "message": message,
                **options
            }
            
            await self.hass.services.async_call(
                "tts",
                self.tts_service.split(".")[-1],
                service_data,
                blocking=False
            )
            
            return True
            
        except Exception as e:
            LOGGER.error(f"Error sending TTS to {speaker}: {e}")
            return False

    def _get_tts_options(self, priority: AlertPriority) -> Dict[str, Any]:
        """Get TTS options based on priority."""
        options = {}
        
        if priority == PRIORITY_CRITICAL:
            options.update({
                "options": {
                    "voice": "emergency",
                    "speed": 0.9,
                    "volume": 1.0
                }
            })
        elif priority == PRIORITY_HIGH:
            options.update({
                "options": {
                    "speed": 0.95,
                    "volume": 0.9
                }
            })
        else:
            options.update({
                "options": {
                    "speed": 1.0,
                    "volume": 0.7
                }
            })
            
        return options

    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
            
        try:
            now = datetime.now().time()
            start_time = time.fromisoformat(self.quiet_hours_start)
            end_time = time.fromisoformat(self.quiet_hours_end)
            
            if start_time <= end_time:
                # Same day quiet hours
                return start_time <= now <= end_time
            else:
                # Overnight quiet hours
                return now >= start_time or now <= end_time
                
        except Exception as e:
            LOGGER.error(f"Error checking quiet hours: {e}")
            return False

    async def announce_alert(self, alert: GuardianAlert) -> bool:
        """Announce a guardian alert via voice."""
        try:
            # Format alert message
            message = f"{alert.title}. {alert.message}"
            
            if alert.location:
                message += f" Location: {alert.location}."
                
            if alert.actions_available:
                message += f" Available actions: {', '.join(alert.actions_available)}."
                
            return await self.announce(
                message=message,
                priority=alert.priority,
                location=alert.location
            )
            
        except Exception as e:
            LOGGER.error(f"Error announcing alert: {e}")
            return False

    async def announce_morning_briefing(self, briefing_data: Dict[str, Any]) -> bool:
        """Announce morning briefing."""
        try:
            message_parts = [f"Good morning! Here's your briefing."]
            
            if "weather" in briefing_data:
                message_parts.append(f"Weather: {briefing_data['weather']}")
                
            if "security_status" in briefing_data:
                message_parts.append(f"Security: {briefing_data['security_status']}")
                
            if "energy_summary" in briefing_data:
                message_parts.append(f"Energy: {briefing_data['energy_summary']}")
                
            if "schedule" in briefing_data:
                message_parts.append(f"Schedule: {briefing_data['schedule']}")
                
            message = " ".join(message_parts)
            
            return await self.announce(
                message=message,
                priority=PRIORITY_MEDIUM,
                location="all"
            )
            
        except Exception as e:
            LOGGER.error(f"Error announcing morning briefing: {e}")
            return False

    async def confirm_action(self, action: str, success: bool) -> bool:
        """Confirm an action was completed."""
        try:
            if success:
                message = f"{self.personality['confirmation']}. {action} completed successfully."
            else:
                message = f"{self.personality['error']} while attempting to {action}."
                
            return await self.announce(
                message=message,
                priority=PRIORITY_LOW
            )
            
        except Exception as e:
            LOGGER.error(f"Error confirming action: {e}")
            return False

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update voice system configuration."""
        self.tts_service = config.get("tts_service", self.tts_service)
        self.voice_announcements = config.get("voice_announcements", self.voice_announcements)
        self.quiet_hours_start = config.get("quiet_hours_start", self.quiet_hours_start)
        self.quiet_hours_end = config.get("quiet_hours_end", self.quiet_hours_end)
        
        LOGGER.info("Voice system configuration updated")
