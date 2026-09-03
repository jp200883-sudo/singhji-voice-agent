"""
Singh Ji Voice AI — Audio Converter
PyDub / AudioOps memory-safe converter
"""

import io
import audioop
from typing import Optional


class AudioConverter:
    """
    Memory-safe audio format converter
    Supports: MP3, WAV, OGG, Mu-Law, PCM
    """

    @staticmethod
    def convert(
        input_data: bytes,
        input_format: str,
        output_format: str,
        sample_rate: Optional[int] = None
    ) -> bytes:
        """
        Convert audio between formats

        Args:
            input_data: Raw audio bytes
            input_format: Source format (mp3, wav, ogg, mulaw, pcm)
            output_format: Target format (mp3, wav, ogg, mulaw, pcm)
            sample_rate: Target sample rate (optional)

        Returns:
            Converted audio bytes
        """
        try:
            from pydub import AudioSegment

            # Load input
            if input_format == "mp3":
                audio = AudioSegment.from_mp3(io.BytesIO(input_data))
            elif input_format == "wav":
                audio = AudioSegment.from_wav(io.BytesIO(input_data))
            elif input_format == "ogg":
                audio = AudioSegment.from_file(io.BytesIO(input_data), format="ogg")
            elif input_format == "mulaw":
                # Mu-Law 8k → PCM
                pcm = audioop.ulaw2lin(input_data, 2)
                audio = AudioSegment(
                    data=pcm,
                    sample_width=2,
                    frame_rate=8000,
                    channels=1
                )
            elif input_format == "pcm":
                audio = AudioSegment(
                    data=input_data,
                    sample_width=2,
                    frame_rate=sample_rate or 16000,
                    channels=1
                )
            else:
                raise ValueError(f"Unsupported input format: {input_format}")

            # Apply sample rate if specified
            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)

            # Export to output format
            buffer = io.BytesIO()

            if output_format == "mp3":
                audio.export(buffer, format="mp3")
            elif output_format == "wav":
                audio.export(buffer, format="wav")
            elif output_format == "ogg":
                audio.export(buffer, format="ogg", codec="libopus")
            elif output_format == "mulaw":
                # PCM → Mu-Law 8k
                audio = audio.set_frame_rate(8000).set_channels(1)
                pcm_data = audio.raw_data
                mulaw = audioop.lin2ulaw(pcm_data, 2)
                return mulaw
            elif output_format == "pcm":
                audio = audio.set_channels(1)
                return audio.raw_data
            else:
                raise ValueError(f"Unsupported output format: {output_format}")

            return buffer.getvalue()

        except ImportError:
            raise ImportError("pydub not installed. Run: pip install pydub")

    @staticmethod
    def get_duration(audio_data: bytes, format: str) -> float:
        """Get audio duration in seconds"""
        try:
            from pydub import AudioSegment

            if format == "mp3":
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            elif format == "wav":
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            elif format == "ogg":
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format="ogg")
            else:
                return 0.0

            return len(audio) / 1000.0  # pydub gives ms

        except:
            return 0.0

    @staticmethod
    def normalize_volume(audio_data: bytes, format: str, target_db: float = -20.0) -> bytes:
        """Normalize audio volume to target dB"""
        try:
            from pydub import AudioSegment

            if format == "mp3":
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            elif format == "wav":
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            else:
                return audio_data

            # Normalize
            change_in_db = target_db - audio.dBFS
            normalized = audio.apply_gain(change_in_db)

            buffer = io.BytesIO()
            normalized.export(buffer, format=format)
            return buffer.getvalue()

        except:
            return audio_data


# Global converter instance
audio_converter = AudioConverter()
