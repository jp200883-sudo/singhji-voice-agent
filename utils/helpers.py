"""
Utility Helpers
Text cleaners, Token counters, Logging
"""

import re
import logging
from typing import Optional


# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("SinghJi.Voice")


class TextHelpers:
    """Text processing utilities"""

    @staticmethod
    def clean_thinking(text: str) -> str:
        """Remove AI thinking artifacts"""
        text = re.sub(r'\s*thinking\s*.*?\s*end_thinking\s*', '', text, flags=re.DOTALL)
        text = re.sub(r"Here\'s a thinking process:.*?\n", '', text, flags=re.DOTALL)
        text = re.sub(r'Thinking:.*?\n', '', text, flags=re.DOTALL)
        return text

    @staticmethod
    def clean_markdown(text: str) -> str:
        """Remove markdown formatting"""
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'[\*\_#`]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token count estimate"""
        # Approximate: 1 token ≈ 4 characters for English, 1-2 for Hindi
        return len(text) // 3

    @staticmethod
    def truncate(text: str, max_tokens: int = 120) -> str:
        """Truncate text to approximate token limit"""
        if TextHelpers.estimate_tokens(text) <= max_tokens:
            return text
        # Rough truncation
        max_chars = max_tokens * 3
        return text[:max_chars] + "..."


class VoiceHelpers:
    """Voice-specific utilities"""

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    @staticmethod
    def detect_language_hint(text: str) -> str:
        """Detect if text is Hindi, English, or Hinglish"""
        hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097f')
        total_chars = len(text.replace(" ", ""))

        if hindi_chars / total_chars > 0.5:
            return "hi"
        elif hindi_chars / total_chars > 0.1:
            return "hi-en"  # Hinglish
        return "en"


# Singletons
text_helpers = TextHelpers()
voice_helpers = VoiceHelpers()
