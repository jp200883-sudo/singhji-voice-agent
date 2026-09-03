"""
Singh Ji Voice AI — Main FastAPI Application
CORS, Lifespan, Router Mount, Health Check
"""

import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.connection_manager import manager
from routers import voice_ws, telegram_webhook
from models.schemas import HealthResponse


# Startup time for uptime calculation
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Startup: Init background tasks
    Shutdown: Cleanup connections
    """
    # === STARTUP ===
    print("=" * 60)
    print("SINGH JI VOICE AI v3.0 — STARTING")
    print("=" * 60)
    print(f"Host: {settings.HOST}:{settings.PORT}")
    print(f"Default TTS: {settings.DEFAULT_TTS_ENGINE}")
    print(f"Default LLM: {settings.GROQ_MODEL}")
    print(f"Default Language: {settings.DEFAULT_LANGUAGE}")
    print(f"Active Personas: 12 (India, US, UK, China)")
    print("=" * 60)

    # Start WebSocket cleanup task
    cleanup_task = None
    try:
        import asyncio
        cleanup_task = asyncio.create_task(manager.start_cleanup())
    except Exception as e:
        print(f"Cleanup task failed: {e}")

    yield  # App runs here

    # === SHUTDOWN ===
    print("=" * 60)
    print("SINGH JI VOICE AI — SHUTTING DOWN")
    print("=" * 60)

    if cleanup_task:
        cleanup_task.cancel()

    # Disconnect all WebSocket clients
    for client_id in list(manager.active_connections.keys()):
        manager.disconnect(client_id)

    print("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="Singh Ji Voice AI",
    description="""
    Real-time Voice AI Agent

    Features:
    - 300+ Free TTS Voices (Edge + Kokoro + Piper)
    - 4-Layer STT Fallback (Groq -> HF Bucket -> Google -> Local)
    - 5-Layer LLM Fallback (Groq -> Gemini -> OpenRouter -> HF -> Local)
    - 12 Voice Personas (India, US, UK, China)
    - Full-duplex WebSocket for telephony
    - Telegram Bot with voice support
    - Hinglish primary, 50+ languages supported

    All 100% FREE — No subscriptions!
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Mount Routers ===
app.include_router(voice_ws.router)           # /ws/voice/*
app.include_router(telegram_webhook.router)   # /telegram/*


# === Root Endpoint ===
@app.get("/")
def root():
    """API root — Project info"""
    return {
        "name": "Singh Ji Voice AI",
        "version": "3.0.0",
        "tagline": "300+ Free Voices, 5-Layer AI, Real-time Voice Agent",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "settings": "/settings",
            "ws_voice": "/ws/voice/{client_id}",
            "telegram_webhook": "/telegram/webhook",
            "telegram_stats": "/telegram/stats",
            "ws_stats": "/ws/voice/stats"
        },
        "personas": [
            "up_bhaiya", "naina_counselor", "senior_sharmaji",
            "corporate_aryan", "priya_sales", "south_murthy",
            "us_alex", "us_sarah", "uk_oliver", "uk_emma",
            "china_li_wei", "china_meiling"
        ],
        "engines": {
            "tts": ["edge", "kokoro", "piper"],
            "stt": ["groq_whisper", "hf_bucket", "google", "local_whisper"],
            "llm": ["groq", "gemini", "openrouter", "hf", "local"]
        }
    }


# === Health Check ===
@app.get("/health", response_model=HealthResponse)
def health():
    """Health check — All platforms use this"""
    uptime = int(time.time() - START_TIME)

    return {
        "status": "healthy",
        "version": "3.0.0",
        "uptime_seconds": uptime,
        "active_connections": len(manager.active_connections),
        "engines": ["edge", "kokoro", "piper"],
        "default_engine": settings.DEFAULT_TTS_ENGINE,
        "default_language": settings.DEFAULT_LANGUAGE
    }


# === Settings Endpoint ===
@app.get("/settings")
def get_settings():
    """Get current app configuration (sensitive keys hidden)"""
    return {
        "server": {
            "port": settings.PORT,
            "host": settings.HOST,
            "debug": settings.DEBUG
        },
        "tts": {
            "default_engine": settings.DEFAULT_TTS_ENGINE,
            "default_language": settings.DEFAULT_LANGUAGE,
            "default_voice_edge": settings.DEFAULT_VOICE_EDGE,
            "default_voice_kokoro": settings.DEFAULT_VOICE_KOKORO,
            "default_voice_piper": settings.DEFAULT_VOICE_PIPER
        },
        "llm": {
            "primary": "groq" if settings.GROQ_API_KEY else "not configured",
            "fallback_1": "gemini" if settings.GEMINI_API_KEY else "not configured",
            "fallback_2": "openrouter" if settings.OPENROUTER_API_KEY else "not configured",
            "fallback_3": "hf" if settings.HF_API_TOKEN else "not configured"
        },
        "stt": {
            "primary": "groq_whisper" if settings.GROQ_API_KEY else "not configured",
            "hf_bucket": settings.HF_STT_BUCKET,
            "local_whisper": settings.LOCAL_WHISPER_MODEL if settings.LOCAL_WHISPER_ENABLED else "disabled"
        },
        "hf_buckets": settings.HF_BUCKETS,
        "telegram": "configured" if settings.TELEGRAM_BOT_TOKEN else "not configured"
    }


# === Run Server ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 2
    )
