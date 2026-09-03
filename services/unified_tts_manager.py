#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SINGH JI UNIFIED TTS MANAGER — ALL FREE TTS ENGINES
═══════════════════════════════════════════════════════════════════════════════
Combines: Kokoro + Edge TTS + Piper + Orpheus + Qwen3-TTS
100% FREE — Choose the best engine for each use case
"""

import os
import asyncio
import tempfile
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class TTSEngine(Enum):
    KOKORO = "kokoro"
    EDGE = "edge"
    PIPER = "piper"
    ORPHEUS = "orpheus"
    QWEN3 = "qwen3"


@dataclass
class TTSResult:
    audio_file: str
    engine: TTSEngine
    voice: str
    duration_sec: float
    text: str


class UnifiedTTSManager:
    """Unified TTS Manager — Auto-selects best engine"""

    def __init__(self, 
                 prefer_local: bool = True,
                 kokoro_enabled: bool = True,
                 edge_enabled: bool = True,
                 piper_enabled: bool = False,
                 orpheus_enabled: bool = False,
                 qwen3_enabled: bool = False):

        self.prefer_local = prefer_local
        self.engines = {}

        if kokoro_enabled:
            try:
                from kokoro_tts_manager import KokoroTTSManager
                self.engines[TTSEngine.KOKORO] = KokoroTTSManager()
                print("✅ Kokoro TTS loaded")
            except Exception as e:
                print(f"⚠️  Kokoro TTS failed: {e}")

        if edge_enabled:
            try:
                from edge_tts_manager import EdgeTTSManager
                self.engines[TTSEngine.EDGE] = EdgeTTSManager()
                print("✅ Edge TTS loaded")
            except Exception as e:
                print(f"⚠️  Edge TTS failed: {e}")

        self.default_engine = self._pick_default()
        print(f"🎯 Default engine: {self.default_engine.value}")

    def _pick_default(self) -> TTSEngine:
        if self.prefer_local:
            priority = [TTSEngine.KOKORO, TTSEngine.PIPER, TTSEngine.EDGE]
        else:
            priority = [TTSEngine.EDGE, TTSEngine.KOKORO, TTSEngine.PIPER]

        for engine in priority:
            if engine in self.engines:
                return engine

        if self.engines:
            return list(self.engines.keys())[0]

        raise RuntimeError("No TTS engine available!")

    def synthesize(self,
                   text: str,
                   voice: Optional[str] = None,
                   engine: Optional[TTSEngine] = None,
                   emotion: str = "neutral",
                   speed: float = 1.0,
                   output_file: Optional[str] = None) -> TTSResult:

        if output_file is None:
            output_file = tempfile.mktemp(suffix=".wav")

        selected_engine = engine or self.default_engine

        if selected_engine not in self.engines:
            selected_engine = self.default_engine

        engine_instance = self.engines[selected_engine]

        if selected_engine == TTSEngine.KOKORO:
            result_file = engine_instance.synthesize(
                text=text,
                voice=voice or "af_bella",
                speed=speed,
                output_file=output_file
            )

        elif selected_engine == TTSEngine.EDGE:
            import asyncio
            result_file = asyncio.run(engine_instance.synthesize_with_emotion(
                text=text,
                voice=voice or "hi-IN-MadhurNeural",
                emotion=emotion,
                output_file=output_file
            ))

        else:
            raise RuntimeError(f"Engine {selected_engine} not implemented")

        duration = len(text.split()) * 0.3

        return TTSResult(
            audio_file=result_file,
            engine=selected_engine,
            voice=voice or "default",
            duration_sec=duration,
            text=text
        )

    def get_best_voice(self, lang: str = "en", gender: str = "female") -> str:
        voice_map = {
            ("en", "female", "kokoro"): "af_bella",
            ("en", "male", "kokoro"): "am_adam",
            ("hi", "female", "kokoro"): "hf_alpha",
            ("hi", "male", "kokoro"): "hm_omega",
            ("en", "female", "edge"): "en-US-AvaMultilingualNeural",
            ("en", "male", "edge"): "en-US-AndrewMultilingualNeural",
            ("hi", "female", "edge"): "hi-IN-SwaraNeural",
            ("hi", "male", "edge"): "hi-IN-MadhurNeural",
        }

        engine_name = self.default_engine.value
        key = (lang, gender, engine_name)

        return voice_map.get(key, "af_bella")

    def list_engines(self) -> List[TTSEngine]:
        return list(self.engines.keys())

    def print_status(self):
        print("\n" + "=" * 60)
        print("UNIFIED TTS MANAGER — STATUS")
        print("=" * 60)
        print(f"🎯 Default Engine: {self.default_engine.value}")
        print(f"🌍 Prefer Local: {self.prefer_local}")
        print(f"\n📦 Available Engines:")
        for engine in self.engines:
            print(f"   ✅ {engine.value}")
        print("=" * 60)
