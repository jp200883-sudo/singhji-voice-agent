"""
Singh Ji Voice AI — Helpers
Text cleaners, token counters, logging
"""

import re
import logging
from typing import Optional


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("singhji-voice-ai")


class TextCleaner:
    """Text preprocessing utilities"""

    @staticmethod
    def clean_for_tts(text: str) -> str:
        """Clean text for TTS synthesis"""
        # Remove URLs
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special chars that break TTS
        text = re.sub(r"[*#_~`\[\]\(\)]", "", text)
        # Trim
        text = text.strip()
        return text

    @staticmethod
    def clean_for_stt(text: str) -> str:
        """Clean STT transcript"""
        # Remove filler words
        fillers = ["um", "uh", "ah", "hmm", "like", "you know"]
        for filler in fillers:
            text = re.sub(rf"\b{filler}\b", "", text, flags=re.IGNORECASE)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect if text is Hindi, Hinglish, or English"""
        # Count Hindi characters (Devanagari range)
        hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
        total_chars = len(text.strip())

        if total_chars == 0:
            return "en"

        hindi_ratio = hindi_chars / total_chars

        if hindi_ratio > 0.5:
            return "hi"  # Pure Hindi
        elif hindi_ratio > 0.1:
            return "hi"  # Hinglish (has some Hindi)
        else:
            return "en"  # English

    @staticmethod
    def split_long_text(text: str, max_chars: int = 500) -> list:
        """Split long text into chunks for TTS"""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class TokenCounter:
    """Estimate token counts for rate limiting"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough estimate: ~4 chars per token for English, ~2 for Hindi"""
        hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
        other_chars = len(text) - hindi_chars

        # Hindi: ~2 chars/token, English: ~4 chars/token
        tokens = (hindi_chars // 2) + (other_chars // 4)
        return max(tokens, 1)

    @staticmethod
    def check_rate_limit(current_count: int, limit: int, window: str = "minute") -> bool:
        """Check if within rate limit"""
        return current_count < limit


class Logger:
    """Structured logging helper"""

    @staticmethod
    def info(msg: str, extra: Optional[dict] = None):
        if extra:
            logger.info(f"{msg} | {extra}")
        else:
            logger.info(msg)

    @staticmethod
    def error(msg: str, error: Optional[Exception] = None):
        if error:
            logger.error(f"{msg} | Error: {str(error)}")
        else:
            logger.error(msg)

    @staticmethod
    def warning(msg: str):
        logger.warning(msg)

    @staticmethod
    def debug(msg: str):
        logger.debug(msg)


# Export helpers
text_cleaner = TextCleaner()
token_counter = TokenCounter()
log = Logger()
