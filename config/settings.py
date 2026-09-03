"""
Singh Ji Voice AI — Configuration Manager
Pydantic Settings — Auto-load from .env file
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Singh Ji Voice AI Configuration
    Auto-loads from .env file or environment variables
    """

    # === Server ===
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # === TTS Defaults ===
    DEFAULT_TTS_ENGINE: str = "edge"
    DEFAULT_LANGUAGE: str = "hi"
    DEFAULT_VOICE_EDGE: str = "hi-IN-MadhurNeural"
    DEFAULT_VOICE_KOKORO: str = "hf_alpha"
    DEFAULT_VOICE_PIPER: str = "hi_IN-clone-medium"

    # === Audio ===
    AUDIO_SAMPLE_RATE: int = 24000
    AUDIO_FORMAT: str = "mp3"
    TELEPHONY_SAMPLE_RATE: int = 8000   # Mu-Law for calls

    # === LLM APIs (5-Layer Free Fallback) ===
    # Layer 1: Groq (fastest, 20 req/min free)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-70b-versatile"

    # Layer 2: Google Gemini (60 req/min free)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Layer 3: OpenRouter (100+ models, free tier)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-70b-instruct"

    # Layer 4: HuggingFace Inference API (free tier)
    HF_API_TOKEN: str = ""
    HF_LLM_MODEL: str = "microsoft/DialoGPT-medium"

    # Layer 5: Sarvam AI (Indian languages)
    SARVAM_API_KEY: str = ""

    # === STT (4-Layer Free Fallback) ===
    # Layer 1: Groq Whisper (20 req/min)
    GROQ_STT_MODEL: str = "whisper-large-v3"

    # Layer 2: Own HF Bucket — Hinglish STT
    HF_STT_BUCKET: str = "singhji-ai/zero-stt-hinglish-bucket"
    HF_STT_MODEL: str = "zero-stt-hinglish"  # Tumhara custom model

    # Layer 3: Google STT (60 min/mo)
    GOOGLE_STT_ENABLED: bool = False

    # Layer 4: Local Faster-Whisper (unlimited)
    LOCAL_WHISPER_MODEL: str = "base"  # tiny/base/small/medium
    LOCAL_WHISPER_ENABLED: bool = True

    # === HF Buckets (Tumhare Models) ===
    HF_BUCKETS: List[str] = [
        "singhji-ai/pingala-v1-universal-bucket",
        "singhji-ai/zero-stt-hinglish-bucket",
    ]

    # === Telegram Bot ===
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    # === WebSocket ===
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100

    # === Persona Matrix ===
    DEFAULT_PERSONA: str = "friendly_helper"
    DEFAULT_TONE: str = "warm"
    DEFAULT_AGE_GROUP: str = "adult"
    DEFAULT_ACCENT: str = "neutral_indian"

    # === Cloud ===
    RENDER: bool = False
    RAILWAY: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance — singleton pattern"""
    return Settings()


# Global settings instance
settings = get_settings()


if __name__ == "__main__":
    print("="*60)
    print("SINGH JI VOICE AI — SETTINGS LOADED")
    print("="*60)
    print(f"PORT: {settings.PORT}")
    print(f"HOST: {settings.HOST}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DEFAULT_TTS_ENGINE: {settings.DEFAULT_TTS_ENGINE}")
    print(f"DEFAULT_LANGUAGE: {settings.DEFAULT_LANGUAGE}")
    print(f"DEFAULT_VOICE_EDGE: {settings.DEFAULT_VOICE_EDGE}")
    print(f"GROQ_API_KEY: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
    print(f"HF_API_TOKEN: {'Set' if settings.HF_API_TOKEN else 'Not set'}")
    print(f"HF_STT_BUCKET: {settings.HF_STT_BUCKET}")
    print(f"HF_BUCKETS: {settings.HF_BUCKETS}")
    print(f"TELEGRAM_BOT_TOKEN: {'Set' if settings.TELEGRAM_BOT_TOKEN else 'Not set'}")
    print("="*60)
