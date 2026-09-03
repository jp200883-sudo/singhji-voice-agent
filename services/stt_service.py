"""
Singh Ji Voice AI — STT Service
4-Layer Free Fallback: Groq Whisper → HF Bucket → Google STT → Local Whisper
"""

import os
import io
import base64
from typing import Optional
import httpx

from config import settings


class STTService:
    """
    4-Layer STT Fallback System
    All free tiers, auto-fallback on failure
    """

    def __init__(self):
        self.groq_client = None
        self._init_clients()

    def _init_clients(self):
        """Lazy init API clients"""
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                pass

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "hi",
        model: Optional[str] = None
    ) -> str:
        """
        Transcribe audio with auto-fallback

        Priority: Groq Whisper → HF Bucket → Google STT → Local Whisper
        """
        # Layer 1: Groq Whisper (fastest, <200ms)
        if self.groq_client:
            try:
                return await self._groq_transcribe(audio_data, language, model)
            except Exception as e:
                print(f"⚠️ Groq STT failed: {e}")

        # Layer 2: Own HF Bucket (Hinglish optimized)
        if settings.HF_API_TOKEN and settings.HF_STT_BUCKET:
            try:
                return await self._hf_bucket_transcribe(audio_data, language)
            except Exception as e:
                print(f"⚠️ HF Bucket STT failed: {e}")

        # Layer 3: Google STT (60 min/mo free)
        if settings.GOOGLE_STT_ENABLED:
            try:
                return await self._google_transcribe(audio_data, language)
            except Exception as e:
                print(f"⚠️ Google STT failed: {e}")

        # Layer 4: Local Faster-Whisper (unlimited, offline)
        if settings.LOCAL_WHISPER_ENABLED:
            try:
                return await self._local_whisper_transcribe(audio_data, language)
            except Exception as e:
                print(f"⚠️ Local Whisper failed: {e}")

        # All layers failed
        raise RuntimeError("All STT services failed. Please check audio and API keys.")

    async def _groq_transcribe(
        self, audio_data: bytes, language: str, model: Optional[str]
    ) -> str:
        """Groq Whisper API call — Ultra fast <200ms"""
        model_name = model or settings.GROQ_STT_MODEL

        # Save audio to temp file
        temp_file = "/tmp/stt_audio.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_data)

        with open(temp_file, "rb") as f:
            response = self.groq_client.audio.transcriptions.create(
                file=("audio.wav", f),
                model=model_name,
                language=language,
                response_format="text"
            )

        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return response.text if hasattr(response, 'text') else str(response)

    async def _hf_bucket_transcribe(self, audio_data: bytes, language: str) -> str:
        """HuggingFace Bucket STT — Tumhara custom Hinglish model"""
        # Convert audio to base64
        audio_b64 = base64.b64encode(audio_data).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{settings.HF_STT_BUCKET}",
                headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
                json={
                    "inputs": audio_b64,
                    "parameters": {"language": language}
                },
                timeout=30.0
            )

            result = response.json()
            if isinstance(result, dict):
                return result.get("text", "")
            elif isinstance(result, list) and len(result) > 0:
                return result[0].get("text", "")
            return str(result)

    async def _google_transcribe(self, audio_data: bytes, language: str) -> str:
        """Google Cloud STT API"""
        # Requires google-cloud-speech package
        try:
            from google.cloud import speech

            client = speech.SpeechClient()

            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                alternative_language_codes=["en-IN"] if language == "hi" else []
            )

            response = client.recognize(config=config, audio=audio)

            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript

            return transcript
        except ImportError:
            raise ImportError("google-cloud-speech not installed. Run: pip install google-cloud-speech")

    async def _local_whisper_transcribe(self, audio_data: bytes, language: str) -> str:
        """Local Faster-Whisper — No API, unlimited"""
        try:
            from faster_whisper import WhisperModel

            # Load model (cached after first use)
            model = WhisperModel(
                settings.LOCAL_WHISPER_MODEL,
                device="cpu",
                compute_type="int8"
            )

            # Save audio to temp file
            temp_file = "/tmp/whisper_audio.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)

            segments, _ = model.transcribe(temp_file, language=language)

            transcript = " ".join([segment.text for segment in segments])

            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return transcript.strip()

        except ImportError:
            raise ImportError("faster-whisper not installed. Run: pip install faster-whisper")

    async def transcribe_file(self, file_path: str, language: str = "hi") -> str:
        """Transcribe from file path"""
        with open(file_path, "rb") as f:
            audio_data = f.read()
        return await self.transcribe(audio_data, language)

    async def transcribe_telegram_voice(self, voice_file_url: str, language: str = "hi") -> str:
        """Download and transcribe Telegram voice message"""
        async with httpx.AsyncClient() as client:
            response = await client.get(voice_file_url, timeout=30.0)
            audio_data = response.content

        return await self.transcribe(audio_data, language)


# Global STT service instance
stt_service = STTService()
