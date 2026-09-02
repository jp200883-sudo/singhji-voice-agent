"""
Text-to-Speech Manager
Edge-TTS — Streamed OGG/Opus for telephony & Telegram
"""

import io
import asyncio
from typing import Optional
from pydub import AudioSegment

from config.settings import settings, VOICE_CONFIG


class TTSManager:
    """High-quality TTS with multiple voice options"""

    @classmethod
    async def synthesize(
        cls,
        text: str,
        voice_type: str = "female",
        bitrate: str = "128k"
    ) -> bytes:
        """
        Generate OGG/Opus audio from text

        Args:
            text: Text to speak
            voice_type: "female" (Priya) or "male" (Singh Ji)
            bitrate: Audio quality (default: 128k)

        Returns:
            OGG/Opus audio bytes
        """
        try:
            import edge_tts

            config = VOICE_CONFIG.get(voice_type, VOICE_CONFIG["female"])

            communicate = edge_tts.Communicate(
                text=text,
                voice=config["voice"],
                rate=config["rate"],
                pitch=config["pitch"]
            )

            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])

            buf.seek(0)
            mp3_bytes = buf.read()

            if len(mp3_bytes) > 0:
                # Convert MP3 to OGG/Opus
                audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3").normalize()
                ogg_io = io.BytesIO()
                audio.export(ogg_io, format="ogg", codec="libopus", parameters=["-b:a", bitrate])
                ogg_io.seek(0)
                return ogg_io.read()

        except Exception as e:
            print(f"⚠️ Edge TTS Error: {e}")

        # Fallback: gTTS
        try:
            from gtts import gTTS

            def _gtts():
                tts = gTTS(text=text, lang="hi", slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                audio = AudioSegment.from_file(buf, format="mp3").normalize()
                ogg_io = io.BytesIO()
                audio.export(ogg_io, format="ogg", codec="libopus", parameters=["-b:a", "96k"])
                ogg_io.seek(0)
                return ogg_io.read()

            return await asyncio.to_thread(_gtts)

        except Exception as e:
            print(f"⚠️ gTTS Fallback Error: {e}")
            return b""

    @classmethod
    async def synthesize_for_persona(cls, text: str, persona_key: str = "priya") -> bytes:
        """Synthesize using persona config"""
        voice_type = "female" if persona_key == "priya" else "male"
        return await cls.synthesize(text, voice_type)


# Singleton
tts_manager = TTSManager()
