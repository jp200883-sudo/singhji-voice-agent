"""
Pydantic Schemas
Telemetry, WS In/Out Packets, Agent State
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# TELEMETRY SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class CallTelemetry(BaseModel):
    """Voice call telemetry data"""
    call_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    language: str = "hi"
    stt_provider: str = "groq"
    llm_provider: str = "groq"
    tts_provider: str = "edge-tts"
    user_gender: Optional[str] = None
    persona_used: str = "priya"
    message_count: int = 0
    error_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DailyStats(BaseModel):
    """Daily usage statistics"""
    date: str
    total_calls: int = 0
    total_messages: int = 0
    avg_duration: float = 0.0
    unique_users: int = 0
    errors: int = 0


# ═══════════════════════════════════════════════════════════════════
# WEBSOCKET PACKET SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class WSIncomingPacket(BaseModel):
    """Incoming WebSocket packet from client"""
    event: str  # "media", "start", "stop", "mark"
    media: Optional[Dict[str, Any]] = None
    start: Optional[Dict[str, Any]] = None
    mark: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class WSOutgoingPacket(BaseModel):
    """Outgoing WebSocket packet to client"""
    event: str  # "media", "mark", "clear"
    media: Optional[Dict[str, Any]] = None
    mark: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class MediaPayload(BaseModel):
    """Audio media payload"""
    payload: str  # Base64 encoded audio
    track: Optional[str] = "inbound"
    chunk: Optional[str] = None
    timestamp: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# AGENT STATE SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class AgentState(BaseModel):
    """Current agent state"""
    call_id: str
    status: str  # "idle", "listening", "thinking", "speaking", "ended"
    current_persona: str = "priya"
    language: str = "hi"
    last_activity: datetime = datetime.now()
    conversation_history: List[Dict[str, str]] = []

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthStatus(BaseModel):
    """Service health status"""
    status: str = "healthy"
    version: str = "2.4.0"
    groq_whisper: bool = False
    gemini_live: bool = False
    openrouter: bool = False
    huggingface: bool = False
    telegram_bot: bool = False
    active_calls_count: int = 0
    memory_history_sessions: int = 0
    uptime_seconds: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════
# TELEGRAM SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class TelegramUpdate(BaseModel):
    """Telegram webhook update"""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class TelegramMessage(BaseModel):
    """Telegram message object"""
    message_id: int
    chat: Dict[str, Any]
    from_user: Optional[Dict[str, Any]] = None
    date: int
    text: Optional[str] = None
    voice: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"
