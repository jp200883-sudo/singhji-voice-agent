"""
Speech-to-Text Service
Groq Whisper — Ultra-fast <200ms transcription
"""

import io
import wave
import numpy as np
from typing import Optional
from groq import Groq

from config.settings import settings
from core.audio_streamer import pcm_float_to_wav_bytes


# Groq client
groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


class STTService:
    """Ultra-fast speech transcription"""

    @classmethod
    async def transcribe(
        cls,
        pcm_audio: np.ndarray,
        language: str = "hi",
        model: str = "whisper-large-v3"
    ) -> str:
        """
        Transcribe audio to text

        Args:
            pcm_audio: float32 PCM array (-1 to 1)
            language: Language code (default: hi for Hindi)
            model: Whisper model name

        Returns:
            Transcribed text
        """
        try:
            # Convert to WAV for API
            wav_bytes = pcm_float_to_wav_bytes(pcm_audio)

            if groq_client is None:
                raise Exception("Groq client not configured")

            def _call():
                return groq_client.audio.transcriptions.create(
                    file=("audio.wav", wav_bytes),
                    model=model,
                    language=language,
                    response_format="text",
                )

            transcription = await __import__('asyncio').to_thread(_call)
            return str(transcription).strip()

        except Exception as e:
            print(f"❌ STT Error: {e}")
            return ""

    @classmethod
    async def transcribe_ogg(cls, ogg_bytes: bytes, language: str = "hi") -> str:
        """Transcribe OGG audio directly"""
        from core.audio_streamer import AudioStreamer
        pcm = AudioStreamer.ogg_to_pcm(ogg_bytes)
        return await cls.transcribe(pcm, language)


# Singleton
stt_service = STTService()
