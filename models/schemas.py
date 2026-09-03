"""
Singh Ji Voice AI — Pydantic Schemas
Telemetry, WS In/Out Packets, Agent State
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# === Enums ===
class MessageType(str, Enum):
    GREETING = "greeting"
    TRANSCRIPT = "transcript"
    RESPONSE = "response"
    AUDIO_START = "audio_start"
    AUDIO_CHUNK = "audio_chunk"
    AUDIO_END = "audio_end"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    PERSONA_CHANGED = "persona_changed"
    VOICES = "voices"


class EngineType(str, Enum):
    EDGE = "edge"
    KOKORO = "kokoro"
    PIPER = "piper"


class PersonaId(str, Enum):
    FRIENDLY_HELPER = "friendly_helper"
    PROFESSIONAL_CA = "professional_ca"
    BIKE_DEALER = "bike_dealer"
    HOSPITAL_RECEPTION = "hospital_reception"
    REAL_ESTATE = "real_estate"
    ENGLISH_SUPPORT = "english_support"
    TAMIL_HELPER = "tamil_helper"


# === WebSocket Packets ===
class WSIncoming(BaseModel):
    """Incoming WebSocket message"""
    command: str = Field(..., description="Command type: chat, set_persona, ping, get_voices")
    text: Optional[str] = Field(None, description="Text content for chat command")
    persona: Optional[str] = Field(None, description="Persona ID for set_persona")
    language: Optional[str] = Field("hi", description="Language code")


class WSOutgoing(BaseModel):
    """Outgoing WebSocket message"""
    type: MessageType
    text: Optional[str] = None
    persona: Optional[str] = None
    voice: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# === Agent State ===
class AgentState(BaseModel):
    """Current agent state"""
    client_id: str
    persona: str = "friendly_helper"
    language: str = "hi"
    voice: str = "hi-IN-MadhurNeural"
    is_speaking: bool = False
    is_listening: bool = False
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# === Telemetry ===
class TelemetryEvent(BaseModel):
    """Telemetry event for analytics"""
    event_type: str
    client_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[int] = None
    engine_used: Optional[str] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionTelemetry(BaseModel):
    """Session-level telemetry"""
    session_id: str
    client_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_messages: int = 0
    total_audio_seconds: float = 0.0
    stt_events: List[TelemetryEvent] = Field(default_factory=list)
    llm_events: List[TelemetryEvent] = Field(default_factory=list)
    tts_events: List[TelemetryEvent] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


# === API Request/Response ===
class SpeakRequest(BaseModel):
    """TTS request"""
    text: str = Field(..., min_length=1, max_length=5000)
    language: str = "hi"
    voice: Optional[str] = None
    engine: Optional[EngineType] = None
    emotion: Optional[str] = None
    speed: float = Field(1.0, ge=0.5, le=2.0)


class SpeakResponse(BaseModel):
    """TTS response"""
    success: bool
    audio_url: Optional[str] = None
    engine: str
    voice: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class TranscribeRequest(BaseModel):
    """STT request"""
    audio_url: Optional[str] = None
    language: str = "hi"
    model: Optional[str] = None


class TranscribeResponse(BaseModel):
    """STT response"""
    success: bool
    transcript: str
    confidence: Optional[float] = None
    engine: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat/LLM request"""
    message: str = Field(..., min_length=1, max_length=2000)
    persona: Optional[PersonaId] = PersonaId.FRIENDLY_HELPER
    language: str = "hi"
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat/LLM response"""
    success: bool
    response: str
    persona: str
    engine: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None


# === Health & Stats ===
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "3.0.0"
    uptime_seconds: int
    active_connections: int
    engines: List[str]
    default_engine: str
    default_language: str


class StatsResponse(BaseModel):
    """System statistics"""
    total_sessions: int
    active_sessions: int
    total_messages: int
    total_audio_processed_seconds: float
    avg_response_time_ms: float
    engine_usage: Dict[str, int]
    top_languages: List[Dict[str, Any]]
    errors_last_hour: int
