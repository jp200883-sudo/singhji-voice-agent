"""
Singh Ji Voice AI — Audio Streamer
Audio format conversion: Mu-Law 8k ↔ PCM 16k ↔ OGG/Opus
Memory-safe streaming for telephony and Telegram
"""

import io
import struct
import audioop
from typing import AsyncGenerator, Optional
import numpy as np


class AudioStreamer:
    """
    Audio Format Converter & Streamer
    Supports: Mu-Law, PCM, OGG/Opus, MP3
    """

    # Audio format constants
    MULAW_RATE = 8000
    PCM_RATE = 16000
    OUTPUT_RATE = 24000

    @staticmethod
    def mulaw_to_pcm(mulaw_data: bytes) -> bytes:
        """Convert Mu-Law 8k to PCM 16k"""
        # Mu-Law decode
        pcm_data = audioop.ulaw2lin(mulaw_data, 2)
        # Resample 8k → 16k
        pcm_16k = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)[0]
        return pcm_16k

    @staticmethod
    def pcm_to_mulaw(pcm_data: bytes, input_rate: int = 16000) -> bytes:
        """Convert PCM to Mu-Law 8k for telephony"""
        # Resample to 8k if needed
        if input_rate != 8000:
            pcm_8k = audioop.ratecv(pcm_data, 2, 1, input_rate, 8000, None)[0]
        else:
            pcm_8k = pcm_data
        # Encode to Mu-Law
        mulaw_data = audioop.lin2ulaw(pcm_8k, 2)
        return mulaw_data

    @staticmethod
    def pcm_to_opus(pcm_data: bytes, sample_rate: int = 16000) -> bytes:
        """Convert PCM to OGG/Opus (for Telegram)"""
        try:
            from pydub import AudioSegment
            # Create audio segment from PCM
            audio = AudioSegment(
                data=pcm_data,
                sample_width=2,
                frame_rate=sample_rate,
                channels=1
            )
            # Export to OGG/Opus
            buffer = io.BytesIO()
            audio.export(buffer, format="ogg", codec="libopus", parameters=["-vbr", "on"])
            return buffer.getvalue()
        except Exception as e:
            print(f"Opus conversion failed: {e}")
            return pcm_data

    @staticmethod
    def opus_to_pcm(opus_data: bytes) -> bytes:
        """Convert OGG/Opus to PCM"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(io.BytesIO(opus_data), format="ogg")
            # Convert to mono 16k PCM
            audio = audio.set_channels(1).set_frame_rate(16000)
            return audio.raw_data
        except Exception as e:
            print(f"Opus decode failed: {e}")
            return b""

    @staticmethod
    def mp3_to_pcm(mp3_data: bytes) -> bytes:
        """Convert MP3 to PCM"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
            audio = audio.set_channels(1).set_frame_rate(16000)
            return audio.raw_data
        except Exception as e:
            print(f"MP3 decode failed: {e}")
            return b""

    @staticmethod
    def chunk_audio(audio_data: bytes, chunk_size: int = 320) -> AsyncGenerator[bytes, None]:
        """Stream audio in chunks for real-time playback"""
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i:i + chunk_size]

    @staticmethod
    def normalize_audio(pcm_data: bytes) -> bytes:
        """Normalize audio volume"""
        return audioop.normalize(pcm_data, 2, 1, 32767)

    @staticmethod
    def add_silence(pcm_data: bytes, duration_ms: int = 500, sample_rate: int = 16000) -> bytes:
        """Add silence padding"""
        silence_bytes = int(sample_rate * 2 * duration_ms / 1000)
        silence = b"\x00" * silence_bytes
        return silence + pcm_data + silence


# Global audio streamer instance
audio_streamer = AudioStreamer()
