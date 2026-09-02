"""
Audio Converter Utilities
PyDub / AudioOps memory-safe converter
"""

import io
import wave
import numpy as np
from pydub import AudioSegment


class AudioConverter:
    """Memory-safe audio format conversions"""

    @staticmethod
    def ogg_to_wav(ogg_bytes: bytes) -> bytes:
        """Convert OGG to WAV bytes"""
        audio = AudioSegment.from_file(io.BytesIO(ogg_bytes), format="ogg")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        return wav_io.read()

    @staticmethod
    def wav_to_ogg(wav_bytes: bytes, bitrate: str = "128k") -> bytes:
        """Convert WAV to OGG/Opus"""
        audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
        ogg_io = io.BytesIO()
        audio.export(ogg_io, format="ogg", codec="libopus", parameters=["-b:a", bitrate])
        ogg_io.seek(0)
        return ogg_io.read()

    @staticmethod
    def resample(audio_bytes: bytes, target_rate: int = 16000, format_in: str = "wav") -> bytes:
        """Resample audio to target sample rate"""
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format_in)
        audio = audio.set_frame_rate(target_rate).set_channels(1)
        out_io = io.BytesIO()
        audio.export(out_io, format=format_in)
        out_io.seek(0)
        return out_io.read()

    @staticmethod
    def normalize(audio_bytes: bytes, format_in: str = "wav") -> bytes:
        """Normalize audio volume"""
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format_in)
        audio = audio.normalize()
        out_io = io.BytesIO()
        audio.export(out_io, format=format_in)
        out_io.seek(0)
        return out_io.read()


# Singleton
audio_converter = AudioConverter()
