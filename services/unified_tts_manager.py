"""
Singh Ji Voice AI — Piper TTS Manager
Piper TTS: Lightweight, edge-device optimized, ONNX-based
Perfect for Raspberry Pi, mobile, low-resource environments
100% free, open source
"""

import os
import tempfile
import subprocess
import shutil
from typing import Optional, Dict, List
from pathlib import Path


class PiperTTSManager:
    """
    Piper TTS — Edge-optimized neural TTS
    ONNX Runtime based, runs on CPU/Raspberry Pi
    100+ voice models available

    Install: pip install piper-tts
    Download voices from: https://huggingface.co/rhasspy/piper-voices
    """

    # Popular pre-trained voice models
    # Format: model_name -> {language, quality, gender, url}
    VOICES = {
        # English (US)
        "en_US-lessac-medium": {"lang": "en", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "American female — balanced quality"},
        "en_US-lessac-high": {"lang": "en", "quality": "high", "gender": "Female", "size_mb": 110, "desc": "American female — high quality"},
        "en_US-ryan-medium": {"lang": "en", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "American male — balanced quality"},
        "en_US-ryan-high": {"lang": "en", "quality": "high", "gender": "Male", "size_mb": 110, "desc": "American male — high quality"},
        "en_US-libritts-high": {"lang": "en", "quality": "high", "gender": "Female", "size_mb": 120, "desc": "American female — LibriTTS"},
        "en_US-amy-medium": {"lang": "en", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "American female — Amy"},
        "en_US-danny-low": {"lang": "en", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "American male — fast, low quality"},

        # English (UK)
        "en_GB-alan-medium": {"lang": "en-gb", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "British male"},
        "en_GB-southern_english_female-medium": {"lang": "en-gb", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Southern British female"},
        "en_GB-northern_english_male-medium": {"lang": "en-gb", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "Northern British male"},

        # Hindi
        "hi_IN-clone-medium": {"lang": "hi", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Hindi female"},

        # Spanish
        "es_ES-carlfm-x_low": {"lang": "es", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "Spanish male — fast"},
        "es_ES-claude-high": {"lang": "es", "quality": "high", "gender": "Male", "size_mb": 110, "desc": "Spanish male — high quality"},
        "es_MX-claude-high": {"lang": "es", "quality": "high", "gender": "Male", "size_mb": 110, "desc": "Mexican Spanish male"},

        # French
        "fr_FR-siwis-medium": {"lang": "fr", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "French female"},
        "fr_FR-tom-medium": {"lang": "fr", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "French male"},

        # German
        "de_DE-thorsten-medium": {"lang": "de", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "German male"},
        "de_DE-eva_k-x_low": {"lang": "de", "quality": "low", "gender": "Female", "size_mb": 15, "desc": "German female — fast"},

        # Italian
        "it_IT-riccardo-x_low": {"lang": "it", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "Italian male — fast"},
        "it_IT-paola-medium": {"lang": "it", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Italian female"},

        # Portuguese
        "pt_BR-edresson-low": {"lang": "pt", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "Brazilian Portuguese male"},
        "pt_BR-faber-medium": {"lang": "pt", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "Brazilian Portuguese male"},

        # Polish
        "pl_PL-darkman-medium": {"lang": "pl", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "Polish male"},
        "pl_PL-gosia-medium": {"lang": "pl", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Polish female"},

        # Russian
        "ru_RU-irina-medium": {"lang": "ru", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Russian female"},
        "ru_RU-denis-medium": {"lang": "ru", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "Russian male"},

        # Ukrainian
        "uk_UK-lada-x_low": {"lang": "uk", "quality": "low", "gender": "Female", "size_mb": 15, "desc": "Ukrainian female"},

        # Czech
        "cs_CZ-jirka-low": {"lang": "cs", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "Czech male"},

        # Greek
        "el_GR-rapunzelina-low": {"lang": "el", "quality": "low", "gender": "Female", "size_mb": 15, "desc": "Greek female"},

        # Finnish
        "fi_FI-harri-low": {"lang": "fi", "quality": "low", "gender": "Male", "size_mb": 15, "desc": "Finnish male"},

        # Hungarian
        "hu_HU-anna-medium": {"lang": "hu", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Hungarian female"},

        # Norwegian
        "nb_NO-talesyntese-medium": {"lang": "nb", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Norwegian female"},

        # Swedish
        "sv_SE-nst-medium": {"lang": "sv", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Swedish female"},

        # Turkish
        "tr_TR-dfki-medium": {"lang": "tr", "quality": "medium", "gender": "Male", "size_mb": 60, "desc": "Turkish male"},

        # Vietnamese
        "vi_VN-25hours-single-low": {"lang": "vi", "quality": "low", "gender": "Female", "size_mb": 15, "desc": "Vietnamese female"},

        # Catalan
        "ca_ES-upc_ona-medium": {"lang": "ca", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Catalan female"},

        # Slovak
        "sk_SK-lili-medium": {"lang": "sk", "quality": "medium", "gender": "Female", "size_mb": 60, "desc": "Slovak female"},
    }

    BEST_VOICES = {
        "english": "en_US-lessac-medium",
        "english_us": "en_US-lessac-medium",
        "english_uk": "en_GB-alan-medium",
        "hindi": "hi_IN-clone-medium",
        "spanish": "es_ES-claude-high",
        "french": "fr_FR-siwis-medium",
        "german": "de_DE-thorsten-medium",
        "italian": "it_IT-paola-medium",
        "portuguese": "pt_BR-faber-medium",
        "polish": "pl_PL-gosia-medium",
        "russian": "ru_RU-irina-medium",
        "turkish": "tr_TR-dfki-medium",
        "catalan": "ca_ES-upc_ona-medium",
        "slovak": "sk_SK-lili-medium",
        "hungarian": "hu_HU-anna-medium",
        "norwegian": "nb_NO-talesyntese-medium",
        "swedish": "sv_SE-nst-medium",
        "vietnamese": "vi_VN-25hours-single-low",
        "ukrainian": "uk_UK-lada-x_low",
        "czech": "cs_CZ-jirka-low",
        "greek": "el_GR-rapunzelina-low",
        "finnish": "fi_FI-harri-low",
    }

    BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

    def __init__(self, models_dir: Optional[str] = None):
        self.temp_dir = tempfile.gettempdir()
        self.models_dir = models_dir or os.path.join(self.temp_dir, "piper_models")
        os.makedirs(self.models_dir, exist_ok=True)
        self._check_piper_install()

    def _check_piper_install(self):
        """Check if piper-tts is installed"""
        if not shutil.which("piper"):
            try:
                import piper
            except ImportError:
                raise ImportError(
                    "Piper TTS not installed. Run: pip install piper-tts\n"
                    "Or download binary from: https://github.com/rhasspy/piper/releases"
                )

    def _get_model_path(self, voice_id: str) -> tuple:
        """Get paths to model and config files"""
        model_file = f"{voice_id}.onnx"
        config_file = f"{voice_id}.onnx.json"

        model_path = os.path.join(self.models_dir, model_file)
        config_path = os.path.join(self.models_dir, config_file)

        return model_path, config_path

    def _download_voice(self, voice_id: str):
        """Download voice model and config from HuggingFace"""
        model_path, config_path = self._get_model_path(voice_id)

        if os.path.exists(model_path) and os.path.exists(config_path):
            return  # Already downloaded

        import urllib.request

        # Construct URLs
        model_url = f"{self.BASE_URL}/{voice_id}/{voice_id}.onnx"
        config_url = f"{self.BASE_URL}/{voice_id}/{voice_id}.onnx.json"

        print(f"📥 Downloading {voice_id}...")

        # Download model
        if not os.path.exists(model_path):
            urllib.request.urlretrieve(model_url, model_path)
            print(f"   ✅ Model: {model_path}")

        # Download config
        if not os.path.exists(config_path):
            urllib.request.urlretrieve(config_url, config_path)
            print(f"   ✅ Config: {config_path}")

    def get_all_voices(self) -> Dict[str, dict]:
        return self.VOICES

    def get_voices_by_language(self, lang_code: str) -> List[tuple]:
        lang_code = lang_code.lower()
        return [(k, v) for k, v in self.VOICES.items() if v["lang"].startswith(lang_code)]

    def get_best_voice(self, language: str) -> str:
        return self.BEST_VOICES.get(language.lower(), "en_US-lessac-medium")

    def list_languages(self) -> List[str]:
        langs = set()
        for v in self.VOICES.values():
            lang_map = {
                "en": "English (US)", "en-gb": "English (UK)", "hi": "Hindi",
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "pl": "Polish", "ru": "Russian", "uk": "Ukrainian",
                "cs": "Czech", "el": "Greek", "fi": "Finnish", "hu": "Hungarian",
                "nb": "Norwegian", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
                "ca": "Catalan", "sk": "Slovak"
            }
            langs.add(lang_map.get(v["lang"], v["lang"].upper()))
        return sorted(list(langs))

    def synthesize(
        self,
        text: str,
        voice: str = "en_US-lessac-medium",
        output_path: Optional[str] = None,
        length_scale: float = 1.0,
        noise_scale: float = 0.667,
        noise_w: float = 0.8
    ) -> str:
        """
        Synthesize text using Piper TTS

        Args:
            text: Text to speak
            voice: Voice model ID
            output_path: Output WAV path (auto if None)
            length_scale: Speed (1.0=normal, >1=slower, <1=faster)
            noise_scale: Noise scale (0-1)
            noise_w: Noise width (0-1)

        Returns:
            Path to generated WAV file
        """
        if voice not in self.VOICES:
            raise ValueError(f"Unknown voice: {voice}")

        # Download if needed
        self._download_voice(voice)

        model_path, config_path = self._get_model_path(voice)

        if output_path is None:
            output_path = os.path.join(self.temp_dir, f"piper_{voice}.wav")

        # Write text to temp file (Piper reads from stdin or file)
        text_file = os.path.join(self.temp_dir, "piper_input.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text)

        # Build command
        cmd = [
            "piper",
            "--model", model_path,
            "--config", config_path,
            "--output_file", output_path,
            "--length_scale", str(length_scale),
            "--noise_scale", str(noise_scale),
            "--noise_w", str(noise_w),
        ]

        # Run piper
        with open(text_file, "r", encoding="utf-8") as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Piper TTS failed: {result.stderr}")

        return output_path

    def get_voice_info(self, voice_id: str) -> Optional[dict]:
        if voice_id not in self.VOICES:
            return None
        info = self.VOICES[voice_id].copy()
        info["id"] = voice_id
        return info

    def print_voice_catalog(self):
        print("\n" + "="*60)
        print("SINGH JI VOICE AI — PIPER TTS VOICE CATALOG")
        print("="*60)

        from collections import defaultdict
        by_lang = defaultdict(list)
        for vid, v in self.VOICES.items():
            lang_display = {
                "en": "English (US)", "en-gb": "English (UK)", "hi": "Hindi",
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "pl": "Polish", "ru": "Russian", "uk": "Ukrainian",
                "cs": "Czech", "el": "Greek", "fi": "Finnish", "hu": "Hungarian",
                "nb": "Norwegian", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
                "ca": "Catalan", "sk": "Slovak"
            }.get(v["lang"], v["lang"].upper())
            by_lang[lang_display].append((vid, v))

        for lang in sorted(by_lang.keys()):
            voices = by_lang[lang]
            print(f"\n{lang} ({len(voices)} voices)")
            for vid, v in voices:
                flag = "*" if vid in self.BEST_VOICES.values() else "  "
                print(f"   {flag} {vid} — {v['gender']} — {v['quality']} — {v['size_mb']}MB")

        print(f"\nTOTAL: {len(self.VOICES)} voices across {len(by_lang)} languages")
        print("="*60)


if __name__ == "__main__":
    manager = PiperTTSManager()
    manager.print_voice_catalog()
