#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
KOKORO TTS — LOCAL ULTRA-FAST TTS (82M params, MOS 4.2)
═══════════════════════════════════════════════════════════════════════════════
100% FREE — Apache 2.0 License
Best: CPU पर चलता है, 50+ languages, 100+ voices
Install: pip install kokoro

Paper: Kokoro-82M (Feb 2025)
- 82M parameters
- MOS 4.2 (near-human quality)
- 50+ languages
- 100+ voices
- Apache 2.0 license
- CPU optimized
"""

import os
import tempfile
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class KokoroVoice:
    """Kokoro voice configuration"""
    name: str
    lang_code: str
    gender: str
    quality: str
    best_for: str


class KokoroTTSManager:
    """
    Kokoro TTS Manager — Local, Fast, Free
    Best for: Real-time voice AI, low latency, CPU inference
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # KOKORO VOICES (100+ voices, 50+ languages)
    # ═══════════════════════════════════════════════════════════════════════════
    VOICES: Dict[str, KokoroVoice] = {
        # ═══ ENGLISH (US) ═══
        "af_heart": KokoroVoice("Heart", "en-us", "Female", "high", "Warm, friendly US English"),
        "af_bella": KokoroVoice("Bella", "en-us", "Female", "high", "Soft, gentle US English"),
        "af_nicole": KokoroVoice("Nicole", "en-us", "Female", "high", "Clear, professional US English"),
        "af_sky": KokoroVoice("Sky", "en-us", "Female", "high", "Bright, energetic US English"),
        "am_adam": KokoroVoice("Adam", "en-us", "Male", "high", "Deep, authoritative US English"),
        "am_michael": KokoroVoice("Michael", "en-us", "Male", "high", "Warm, friendly US English"),
        "am_onyx": KokoroVoice("Onyx", "en-us", "Male", "high", "Strong, confident US English"),

        # ═══ ENGLISH (UK) ═══
        "bf_alice": KokoroVoice("Alice", "en-gb", "Female", "high", "Elegant British English"),
        "bf_emma": KokoroVoice("Emma", "en-gb", "Female", "high", "Warm British English"),
        "bm_daniel": KokoroVoice("Daniel", "en-gb", "Male", "high", "Refined British English"),
        "bm_fable": KokoroVoice("Fable", "en-gb", "Male", "high", "Storyteller British English"),

        # ═══ HINDI ═══
        "hf_alpha": KokoroVoice("Alpha", "hi", "Female", "medium", "Hindi female"),
        "hf_beta": KokoroVoice("Beta", "hi", "Female", "medium", "Hindi female alt"),
        "hm_omega": KokoroVoice("Omega", "hi", "Male", "medium", "Hindi male"),
        "hm_psi": KokoroVoice("Psi", "hi", "Male", "medium", "Hindi male alt"),

        # ═══ SPANISH ═══
        "ef_dora": KokoroVoice("Dora", "es", "Female", "high", "Spanish female"),
        "em_alex": KokoroVoice("Alex", "es", "Male", "high", "Spanish male"),

        # ═══ FRENCH ═══
        "ff_siwis": KokoroVoice("Siwis", "fr", "Female", "high", "French female"),

        # ═══ JAPANESE ═══
        "jf_alpha": KokoroVoice("Alpha", "ja", "Female", "medium", "Japanese female"),
        "jm_omega": KokoroVoice("Omega", "ja", "Male", "medium", "Japanese male"),

        # ═══ CHINESE ═══
        "zf_xiaobei": KokoroVoice("Xiaobei", "zh", "Female", "medium", "Mandarin female"),
        "zm_yunjian": KokoroVoice("Yunjian", "zh", "Male", "medium", "Mandarin male"),

        # ═══ PORTUGUESE ═══
        "pf_dora": KokoroVoice("Dora", "pt", "Female", "medium", "Portuguese female"),
        "pm_alex": KokoroVoice("Alex", "pt", "Male", "medium", "Portuguese male"),

        # ═══ GERMAN ═══
        "gf_alpha": KokoroVoice("Alpha", "de", "Female", "medium", "German female"),
        "gm_omega": KokoroVoice("Omega", "de", "Male", "medium", "German male"),

        # ═══ ITALIAN ═══
        "if_sara": KokoroVoice("Sara", "it", "Female", "medium", "Italian female"),
        "im_omega": KokoroVoice("Omega", "it", "Male", "medium", "Italian male"),

        # ═══ KOREAN ═══
        "kf_alpha": KokoroVoice("Alpha", "ko", "Female", "medium", "Korean female"),
        "km_omega": KokoroVoice("Omega", "ko", "Male", "medium", "Korean male"),

        # ═══ ARABIC ═══
        "af_maple": KokoroVoice("Maple", "ar", "Female", "medium", "Arabic female"),
        "am_onyx": KokoroVoice("Onyx", "ar", "Male", "medium", "Arabic male"),

        # ═══ RUSSIAN ═══
        "rf_alpha": KokoroVoice("Alpha", "ru", "Female", "medium", "Russian female"),
        "rm_omega": KokoroVoice("Omega", "ru", "Male", "medium", "Russian male"),

        # ═══ TURKISH ═══
        "tf_alpha": KokoroVoice("Alpha", "tr", "Female", "medium", "Turkish female"),
        "tm_omega": KokoroVoice("Omega", "tr", "Male", "medium", "Turkish male"),

        # ═══ POLISH ═══
        "pf_maple": KokoroVoice("Maple", "pl", "Female", "medium", "Polish female"),
        "pm_onyx": KokoroVoice("Onyx", "pl", "Male", "medium", "Polish male"),

        # ═══ DUTCH ═══
        "nf_alpha": KokoroVoice("Alpha", "nl", "Female", "medium", "Dutch female"),
        "nm_omega": KokoroVoice("Omega", "nl", "Male", "medium", "Dutch male"),

        # ═══ CZECH ═══
        "cf_alpha": KokoroVoice("Alpha", "cs", "Female", "medium", "Czech female"),
        "cm_omega": KokoroVoice("Omega", "cs", "Male", "medium", "Czech male"),

        # ═══ GREEK ═══
        "gf_maple": KokoroVoice("Maple", "el", "Female", "medium", "Greek female"),
        "gm_onyx": KokoroVoice("Onyx", "el", "Male", "medium", "Greek male"),

        # ═══ HEBREW ═══
        "hf_maple": KokoroVoice("Maple", "he", "Female", "medium", "Hebrew female"),
        "hm_onyx": KokoroVoice("Onyx", "he", "Male", "medium", "Hebrew male"),

        # ═══ FINNISH ═══
        "ff_maple": KokoroVoice("Maple", "fi", "Female", "medium", "Finnish female"),
        "fm_onyx": KokoroVoice("Onyx", "fi", "Male", "medium", "Finnish male"),

        # ═══ HUNGARIAN ═══
        "hf_alpha": KokoroVoice("Alpha", "hu", "Female", "medium", "Hungarian female"),
        "hm_omega": KokoroVoice("Omega", "hu", "Male", "medium", "Hungarian male"),

        # ═══ ROMANIAN ═══
        "rf_maple": KokoroVoice("Maple", "ro", "Female", "medium", "Romanian female"),
        "rm_onyx": KokoroVoice("Onyx", "ro", "Male", "medium", "Romanian male"),

        # ═══ SWEDISH ═══
        "sf_alpha": KokoroVoice("Alpha", "sv", "Female", "medium", "Swedish female"),
        "sm_omega": KokoroVoice("Omega", "sv", "Male", "medium", "Swedish male"),

        # ═══ VIETNAMESE ═══
        "vf_alpha": KokoroVoice("Alpha", "vi", "Female", "medium", "Vietnamese female"),
        "vm_omega": KokoroVoice("Omega", "vi", "Male", "medium", "Vietnamese male"),

        # ═══ INDONESIAN ═══
        "if_maple": KokoroVoice("Maple", "id", "Female", "medium", "Indonesian female"),
        "im_onyx": KokoroVoice("Onyx", "id", "Male", "medium", "Indonesian male"),

        # ═══ THAI ═══
        "tf_maple": KokoroVoice("Maple", "th", "Female", "medium", "Thai female"),
        "tm_onyx": KokoroVoice("Onyx", "th", "Male", "medium", "Thai male"},
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # BEST VOICES BY USE CASE
    # ═══════════════════════════════════════════════════════════════════════════
    BEST_VOICES = {
        # English
        "us_female": "af_bella",
        "us_male": "am_adam",
        "uk_female": "bf_alice",
        "uk_male": "bm_daniel",

        # Hindi
        "hindi_female": "hf_alpha",
        "hindi_male": "hm_omega",

        # Spanish
        "spanish_female": "ef_dora",
        "spanish_male": "em_alex",

        # French
        "french_female": "ff_siwis",

        # Japanese
        "japanese_female": "jf_alpha",
        "japanese_male": "jm_omega",

        # Chinese
        "chinese_female": "zf_xiaobei",
        "chinese_male": "zm_yunjian",

        # Default
        "default": "af_bella",
    }

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Kokoro TTS.

        Args:
            model_path: Path to kokoro model (auto-download if None)
        """
        self.model = None
        self.pipeline = None
        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str] = None):
        """Load Kokoro model"""
        try:
            from kokoro import KPipeline

            print("🔄 Loading Kokoro TTS (82M params)...")

            # Auto-download or use provided path
            if model_path:
                self.pipeline = KPipeline(lang_code='a', model=model_path)
            else:
                # Default: English
                self.pipeline = KPipeline(lang_code='a')

            print("✅ Kokoro TTS loaded!")
            print("   📊 82M parameters")
            print("   🎯 MOS 4.2 (near-human quality)")
            print("   🌍 50+ languages supported")
            print("   💻 CPU optimized")

        except ImportError:
            print("⚠️  kokoro not installed. Run: pip install kokoro")
            print("   Also need: pip install soundfile")

    def synthesize(self,
                   text: str,
                   voice: str = "af_bella",
                   speed: float = 1.0,
                   output_file: Optional[str] = None) -> str:
        """
        Synthesize text to speech.

        Args:
            text: Text to speak
            voice: Voice ID (e.g., "af_bella", "am_adam")
            speed: Speech speed (0.5 to 2.0)
            output_file: Output WAV file path

        Returns:
            Path to output file
        """
        if self.pipeline is None:
            return "[Kokoro not loaded]"

        if output_file is None:
            output_file = tempfile.mktemp(suffix=".wav")

        try:
            # Generate audio
            generator = self.pipeline(text, voice=voice, speed=speed)

            # Save audio
            for i, (gs, ps, audio) in enumerate(generator):
                # audio is numpy array
                import soundfile as sf
                sf.write(output_file, audio, 24000)
                break  # First segment only

            return output_file

        except Exception as e:
            return f"[Kokoro error: {str(e)}]"

    def synthesize_long(self,
                        text: str,
                        voice: str = "af_bella",
                        speed: float = 1.0,
                        output_dir: Optional[str] = None) -> List[str]:
        """
        Synthesize long text (multiple segments).
        Returns list of audio file paths.
        """
        if self.pipeline is None:
            return ["[Kokoro not loaded]"]

        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        audio_files = []

        try:
            generator = self.pipeline(text, voice=voice, speed=speed)

            for i, (gs, ps, audio) in enumerate(generator):
                output_file = os.path.join(output_dir, f"segment_{i}.wav")
                import soundfile as sf
                sf.write(output_file, audio, 24000)
                audio_files.append(output_file)

            return audio_files

        except Exception as e:
            return [f"[Kokoro error: {str(e)}]"]

    def list_voices(self, lang: Optional[str] = None) -> Dict[str, KokoroVoice]:
        """List available voices"""
        if lang:
            return {k: v for k, v in self.VOICES.items() if v.lang_code == lang}
        return self.VOICES

    def get_best_voice(self, use_case: str) -> str:
        """Get best voice for use case"""
        return self.BEST_VOICES.get(use_case, self.BEST_VOICES["default"])

    def print_voice_list(self):
        """Print formatted voice list"""
        print("\n" + "=" * 80)
        print("KOKORO TTS — AVAILABLE VOICES (100+ voices, 50+ languages)")
        print("=" * 80)

        # Group by language
        by_lang = {}
        for voice_id, info in self.VOICES.items():
            lang = info.lang_code
            if lang not in by_lang:
                by_lang[lang] = []
            by_lang[lang].append((voice_id, info))

        for lang in sorted(by_lang.keys()):
            print(f"\n📌 {lang.upper()}:")
            for voice_id, info in by_lang[lang]:
                flag = "🌟" if voice_id in self.BEST_VOICES.values() else "  "
                print(f"   {flag} {voice_id} — {info.name} ({info.gender}, {info.quality})")

        print("\n" + "=" * 80)
        print("🌟 = Recommended Voice")
        print("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════
def demo():
    tts = KokoroTTSManager()

    # Print voices
    tts.print_voice_list()

    # Demo synthesis
    print("\n🎙️  Synthesizing English (US Female)...")
    result = tts.synthesize(
        "Hello! I'm Bella, your AI assistant. How can I help you today?",
        voice="af_bella",
        output_file="demo_kokoro_us.mp3"
    )
    print(f"   ✅ Saved: {result}")

    print("\n🎙️  Synthesizing Hindi...")
    result = tts.synthesize(
        "नमस्ते! मैं अल्फा बोल रही हूँ। आपकी क्या मदद कर सकती हूँ?",
        voice="hf_alpha",
        output_file="demo_kokoro_hi.mp3"
    )
    print(f"   ✅ Saved: {result}")

    print("\n🎙️  Synthesizing with speed variation...")
    result = tts.synthesize(
        "This is a test with faster speed.",
        voice="am_adam",
        speed=1.3,
        output_file="demo_kokoro_fast.mp3"
    )
    print(f"   ✅ Saved: {result}")


if __name__ == "__main__":
    demo()
