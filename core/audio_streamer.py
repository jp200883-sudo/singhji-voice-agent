"""
Audio Streaming Utilities
Mulaw 8k ↔ PCM 16k ↔ OGG/Opus conversions
"""

import io
import wave
import numpy as np
from typing import Optional
from pydub import AudioSegment


SAMPLE_RATE = 16000


def decode_mulaw(audio_data: bytes) -> np.ndarray:
    """Decode μ-law to float32 PCM"""
    mu = 255
    audio = np.frombuffer(audio_data, dtype=np.uint8).astype(np.float32)
    audio = (audio / mu) * 2 - 1
    audio = np.clip(audio, -1.0, 1.0)
    audio = np.sign(audio) * (np.exp(mu * np.abs(audio)) - 1) / (np.exp(mu) - 1)
    return audio


def encode_mulaw(audio: np.ndarray) -> bytes:
    """Encode float32 PCM to μ-law"""
    mu = 255
    audio = np.clip(audio, -1, 1)
    audio = np.sign(audio) * np.log(1 + mu * np.abs(audio)) / np.log(1 + mu)
    audio = ((audio + 1) / 2 * mu).astype(np.uint8)
    return audio.tobytes()


def pcm_float_to_wav_bytes(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Convert float32 PCM to WAV bytes"""
    audio_int16 = np.clip(audio, -1, 1)
    audio_int16 = (audio_int16 * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf.read()


def detect_gender_from_pitch(pcm_audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Detect caller gender from voice pitch"""
    try:
        audio = pcm_audio - np.mean(pcm_audio)
        corr = np.correlate(audio, audio, mode="full")
        corr = corr[len(corr) // 2:]

        min_lag = int(sample_rate / 300)
        max_lag = int(sample_rate / 75)

        if max_lag >= len(corr):
            return "unknown"

        segment = corr[min_lag:max_lag]
        if len(segment) == 0:
            return "unknown"

        peak_lag = np.argmax(segment) + min_lag
        if peak_lag == 0:
            return "unknown"

        pitch_hz = sample_rate / peak_lag
        return "male" if pitch_hz < 165 else "female"
    except Exception as e:
        print(f"⚠️ Gender detection error: {e}")
        return "unknown"


class AudioStreamer:
    """Handles audio format conversions for telephony"""

    @staticmethod
    def ogg_to_pcm(ogg_bytes: bytes) -> np.ndarray:
        """Convert OGG/Opus to float32 PCM"""
        audio = AudioSegment.from_file(io.BytesIO(ogg_bytes), format="ogg")
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        wav_buf = io.BytesIO()
        audio.export(wav_buf, format="wav")
        wav_buf.seek(0)

        with wave.open(wav_buf, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0

    @staticmethod
    def pcm_to_ogg(pcm_audio: np.ndarray, bitrate: str = "128k") -> bytes:
        """Convert float32 PCM to OGG/Opus"""
        wav_bytes = pcm_float_to_wav_bytes(pcm_audio)
        audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

        ogg_io = io.BytesIO()
        audio.export(ogg_io, format="ogg", codec="libopus", parameters=["-b:a", bitrate])
        ogg_io.seek(0)
        return ogg_io.read()
