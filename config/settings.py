"""
Singh Ji Voice Agent — Configuration & Settings
Pydantic BaseSettings for env loading
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """All environment variables loaded here"""

    # AI Provider Keys
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")

    # Telegram
    telegram_voice_bot_token: str = Field(default="", alias="TELEGRAM_VOICE_BOT_TOKEN")

    # Server
    port: int = Field(default=8000, alias="PORT")
    app_url: str = Field(default="", alias="APP_URL")

    # Audio
    sample_rate: int = 16000
    chunk_duration_ms: int = 100

    # Gemini Live
    gemini_live_model: str = "gemini-2.5-flash-native-audio-preview-09-2025"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance
settings = Settings()

# Voice constants
VOICE_CONFIG = {
    "female": {
        "voice": "hi-IN-SwaraNeural",
        "rate": "+3%",
        "pitch": "+0Hz",
        "persona": "priya",
        "avatar": "👩‍💼 Priya:",
        "system_prompt": (
            "You are Priya, a polite, sweet, and intelligent AI personal assistant for Singh Ji / Singularity AI. "
            "Speak naturally in polite, friendly Hinglish (Hindi + English mix). "
            "Keep replies strictly under 2 short sentences. "
            "Never use asterisks or markdown formatting. Output only the spoken final response."
        )
    },
    "male": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "+2%",
        "pitch": "-1Hz",
        "persona": "singhji",
        "avatar": "🧔 Singh Ji:",
        "system_prompt": (
            "You are Singh Ji AI, a confident, sharp, and helpful Indian voice AI. "
            "Speak naturally in Hinglish (Hindi + English mix). "
            "Keep replies strictly under 2 short sentences. "
            "Never use asterisks or markdown formatting. Output only the spoken final response."
        )
    }
}

# LLM Fallback Order
FALLBACK_PROVIDERS = ["groq", "gemini", "openrouter", "huggingface"]

# Groq Models (priority order)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]
