"""Pydantic models for Agent Magdala Guardian System."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from .const import (
    AlertPriority,
    GuardianMode,
    GUARDIAN_MODULES,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
)


class DeviceState(BaseModel):
    """Model for device state information."""
    entity_id: str = Field(..., description="Home Assistant entity ID")
    state: str = Field(..., description="Current state of the device")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Device attributes")
    last_changed: datetime = Field(default_factory=datetime.now, description="Last state change time")
    friendly_name: Optional[str] = Field(None, description="Human-readable device name")


class SecurityEvent(BaseModel):
    """Model for security-related events."""
    event_type: str = Field(..., description="Type of security event")
    location: str = Field(..., description="Location where event occurred")
    severity: AlertPriority = Field(PRIORITY_LOW, description="Event severity level")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    entity_id: Optional[str] = Field(None, description="Related entity ID")
    description: str = Field(..., description="Human-readable event description")
    action_taken: Optional[str] = Field(None, description="Action taken in response")
    resolved: bool = Field(False, description="Whether the event has been resolved")


class WellnessEvent(BaseModel):
    """Model for wellness and health-related events."""
    event_type: str = Field(..., description="Type of wellness event")
    user_id: Optional[str] = Field(None, description="Associated user/family member")
    severity: AlertPriority = Field(PRIORITY_LOW, description="Event severity level")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    description: str = Field(..., description="Human-readable event description")
    medication_related: bool = Field(False, description="Whether event is medication-related")
    emergency: bool = Field(False, description="Whether this is an emergency situation")
    action_taken: Optional[str] = Field(None, description="Action taken in response")


class EnergyEvent(BaseModel):
    """Model for energy-related events and optimizations."""
    event_type: str = Field(..., description="Type of energy event")
    device_entity_id: str = Field(..., description="Related device entity ID")
    energy_impact: float = Field(..., description="Energy impact in kWh or percentage")
    cost_impact: Optional[float] = Field(None, description="Cost impact in local currency")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    description: str = Field(..., description="Human-readable event description")
    optimization_suggestion: Optional[str] = Field(None, description="Suggested optimization")
    action_taken: Optional[str] = Field(None, description="Action taken in response")


class UserPattern(BaseModel):
    """Model for learned user behavior patterns."""
    user_id: str = Field(..., description="User identifier")
    pattern_type: str = Field(..., description="Type of pattern (routine, preference, etc.)")
    pattern_data: Dict[str, Any] = Field(..., description="Pattern-specific data")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last pattern update")
    occurrences: int = Field(1, description="Number of times pattern observed")
    active: bool = Field(True, description="Whether pattern is currently active")


class GuardianCommand(BaseModel):
    """Model for commands to be executed by the guardian system."""
    command_type: str = Field(..., description="Type of command to execute")
    target_entity: Optional[str] = Field(None, description="Target entity for command")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    priority: AlertPriority = Field(PRIORITY_LOW, description="Command priority")
    timestamp: datetime = Field(default_factory=datetime.now, description="Command timestamp")
    user_confirmation_required: bool = Field(False, description="Whether user confirmation is needed")
    timeout_seconds: Optional[int] = Field(None, description="Command timeout in seconds")


class GuardianAlert(BaseModel):
    """Model for guardian system alerts."""
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    module: str = Field(..., description="Guardian module that generated the alert")
    priority: AlertPriority = Field(..., description="Alert priority level")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    location: Optional[str] = Field(None, description="Location related to alert")
    timestamp: datetime = Field(default_factory=datetime.now, description="Alert timestamp")
    acknowledged: bool = Field(False, description="Whether alert has been acknowledged")
    resolved: bool = Field(False, description="Whether alert has been resolved")
    actions_available: List[str] = Field(default_factory=list, description="Available user actions")
    related_entities: List[str] = Field(default_factory=list, description="Related entity IDs")

    @validator('module')
    def validate_module(cls, v):
        if v not in GUARDIAN_MODULES:
            raise ValueError(f"Module must be one of {GUARDIAN_MODULES}")
        return v


class GuardianStatus(BaseModel):
    """Model for overall guardian system status."""
    mode: GuardianMode = Field(..., description="Current guardian mode")
    active_modules: List[str] = Field(..., description="Currently active guardian modules")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last guardian activity")
    alerts_count: int = Field(0, description="Number of active alerts")
    patterns_learned: int = Field(0, description="Number of patterns learned")
    memory_usage_mb: float = Field(0.0, description="Memory usage in MB")
    uptime_hours: float = Field(0.0, description="System uptime in hours")
    health_status: str = Field("healthy", description="Overall system health")


class VoiceAnnouncement(BaseModel):
    """Model for voice announcements."""
    message: str = Field(..., description="Message to announce")
    priority: AlertPriority = Field(PRIORITY_LOW, description="Announcement priority")
    location: Optional[str] = Field(None, description="Target location/speaker")
    timestamp: datetime = Field(default_factory=datetime.now, description="Announcement timestamp")
    tts_service: Optional[str] = Field(None, description="TTS service to use")
    voice_options: Dict[str, Any] = Field(default_factory=dict, description="Voice-specific options")
    repeat_count: int = Field(1, description="Number of times to repeat")
    delay_seconds: Optional[int] = Field(None, description="Delay before announcement")


class MemoryEntry(BaseModel):
    """Model for memory system entries."""
    memory_id: str = Field(..., description="Unique memory identifier")
    content: str = Field(..., description="Memory content")
    category: str = Field(..., description="Memory category")
    user_id: Optional[str] = Field(None, description="Associated user")
    timestamp: datetime = Field(default_factory=datetime.now, description="Memory creation time")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Memory importance (0-1)")
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    expires_at: Optional[datetime] = Field(None, description="Memory expiration time")


class GuardianConfig(BaseModel):
    """Model for guardian system configuration."""
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    mem0_api_key: str = Field(..., description="Mem0 API key")
    openrouter_model: str = Field("google/gemini-flash-1.5", description="OpenRouter model to use")
    guardian_mode: GuardianMode = Field("active", description="Guardian operation mode")
    voice_announcements: bool = Field(True, description="Enable voice announcements")
    tts_service: str = Field("tts.piper", description="TTS service to use")
    enabled_modules: List[str] = Field(default_factory=lambda: GUARDIAN_MODULES.copy(), description="Enabled guardian modules")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Alert threshold configurations")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end time (HH:MM)")
    emergency_contacts: List[str] = Field(default_factory=list, description="Emergency contact numbers")


class ConversationContext(BaseModel):
    """Model for conversation context and history."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Conversation messages")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    started_at: datetime = Field(default_factory=datetime.now, description="Conversation start time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last conversation activity")
    active: bool = Field(True, description="Whether conversation is active")
    summary: Optional[str] = Field(None, description="Conversation summary")


class GuardianResponse(BaseModel):
    """Model for guardian system responses."""
    response_type: str = Field(..., description="Type of response")
    content: str = Field(..., description="Response content")
    conversation_id: Optional[str] = Field(None, description="Related conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Response confidence")
    actions_taken: List[str] = Field(default_factory=list, description="Actions taken")
    follow_up_required: bool = Field(False, description="Whether follow-up is needed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")


# Type aliases for common model unions
AlertEvent = Union[SecurityEvent, WellnessEvent, EnergyEvent]
GuardianEvent = Union[SecurityEvent, WellnessEvent, EnergyEvent, GuardianAlert]
