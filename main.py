"""
Singh Ji Voice AI Agent v2.4
FastAPI App, CORS, Lifespan, Routers Mount
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from core.connection_manager import manager
from routers import voice_ws, telegram_webhook

# ═══════════════════════════════════════════════════════════════════
# LIFESPAN
# ═══════════════════════════════════════════════════════════════════

_start_time: datetime = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _start_time
    _start_time = datetime.now()

    print("🚀 Singh Ji Voice Agent v2.4 initialized...")
    print("   📞 Phone Calls: Gemini Live (True Voice-to-Voice)")
    print("   🤖 LLM Fallback: Groq -> Gemini -> OpenRouter -> Hugging Face")
    print("   🎤 STT: Groq Whisper-Large-V3")
    print("   🔊 TTS: Smart Tuned Edge-TTS (Priya/Singh Ji Persona)")
    print("   🤖 Telegram Bot: Webhook Ready")

    # Start connection cleanup
    manager.start_cleanup()

    yield

    print("🛑 Server shutdown completed.")

# ═══════════════════════════════════════════════════════════════════
# APP INIT
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Singh Ji Voice AI Agent",
    version="2.4.0",
    description="Real-time Voice AI with Telegram & WebSocket support",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# ROUTERS
# ═══════════════════════════════════════════════════════════════════

app.include_router(voice_ws.router)
app.include_router(telegram_webhook.router)

# ═══════════════════════════════════════════════════════════════════
# ROOT & HEALTH
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "service": "Singh Ji Voice AI Agent",
        "version": "2.4.0",
        "status": "online",
        "endpoints": {
            "health": "/api/health",
            "websocket_call": "/ws/call/{call_id}",
            "telegram_webhook": "/webhook/telegram"
        }
    }

@app.get("/api/health")
async def health_check():
    from config.settings import settings

    uptime = None
    if _start_time:
        uptime = (datetime.now() - _start_time).total_seconds()

    return {
        "status": "healthy",
        "version": "2.4.0",
        "groq_whisper": bool(settings.groq_api_key),
        "gemini_live": bool(settings.gemini_api_key),
        "openrouter": bool(settings.openrouter_api_key),
        "huggingface": bool(settings.huggingface_api_key),
        "telegram_bot": bool(settings.telegram_voice_bot_token),
        "active_calls_count": len(manager.active_connections),
        "memory_history_sessions": 0,  # TODO: track from conversation_history
        "uptime_seconds": uptime
    }

# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.port))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
