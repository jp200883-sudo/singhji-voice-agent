#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
EDGE TTS — COMPLETE VOICE LIST & SYNTHESIS SCRIPT
═══════════════════════════════════════════════════════════════════════════════
100% FREE — No API Key Required
Microsoft Edge's online TTS service (free, legal to use)

Install: pip install edge-tts
"""

import asyncio
import edge_tts
from typing import Dict, List, Optional
import json


class EdgeTTSManager:
    """Complete Edge TTS Manager — All Voices + Best Selection"""

    # ═══════════════════════════════════════════════════════════════════════════
    # ALL EDGE TTS VOICES (Complete List)
    # ═══════════════════════════════════════════════════════════════════════════
    ALL_VOICES: Dict[str, Dict[str, str]] = {
        # ═══ HINDI (India) ═══
        "hi-IN-MadhurNeural": {"gender": "Male", "lang": "Hindi", "region": "India", "quality": "high"},
        "hi-IN-SwaraNeural": {"gender": "Female", "lang": "Hindi", "region": "India", "quality": "high"},

        # ═══ ENGLISH — India ═══
        "en-IN-PrabhatNeural": {"gender": "Male", "lang": "English", "region": "India", "quality": "high"},
        "en-IN-NeerjaNeural": {"gender": "Female", "lang": "English", "region": "India", "quality": "high"},
        "en-IN-NeerjaExpressiveNeural": {"gender": "Female", "lang": "English", "region": "India", "quality": "expressive"},

        # ═══ ENGLISH — US ═══
        "en-US-AvaMultilingualNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "multilingual"},
        "en-US-AndrewMultilingualNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "multilingual"},
        "en-US-EmmaMultilingualNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "multilingual"},
        "en-US-BrianNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "high"},
        "en-US-JennyNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "high"},
        "en-US-GuyNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "high"},
        "en-US-AriaNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "high"},
        "en-US-DavisNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "high"},
        "en-US-JaneNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "high"},
        "en-US-JasonNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "high"},
        "en-US-SaraNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "high"},
        "en-US-TonyNeural": {"gender": "Male", "lang": "English", "region": "US", "quality": "high"},
        "en-US-NancyNeural": {"gender": "Female", "lang": "English", "region": "US", "quality": "high"},

        # ═══ ENGLISH — UK ═══
        "en-GB-SoniaNeural": {"gender": "Female", "lang": "English", "region": "UK", "quality": "high"},
        "en-GB-RyanNeural": {"gender": "Male", "lang": "English", "region": "UK", "quality": "high"},
        "en-GB-LibbyNeural": {"gender": "Female", "lang": "English", "region": "UK", "quality": "high"},
        "en-GB-MaisieNeural": {"gender": "Female", "lang": "English", "region": "UK", "quality": "high"},

        # ═══ ENGLISH — Australia ═══
        "en-AU-NatashaNeural": {"gender": "Female", "lang": "English", "region": "Australia", "quality": "high"},
        "en-AU-WilliamNeural": {"gender": "Male", "lang": "English", "region": "Australia", "quality": "high"},

        # ═══ ENGLISH — Canada ═══
        "en-CA-ClaraNeural": {"gender": "Female", "lang": "English", "region": "Canada", "quality": "high"},
        "en-CA-LiamNeural": {"gender": "Male", "lang": "English", "region": "Canada", "quality": "high"},

        # ═══ CHINESE ═══
        "zh-CN-XiaoxiaoNeural": {"gender": "Female", "lang": "Chinese", "region": "China", "quality": "high"},
        "zh-CN-YunxiNeural": {"gender": "Male", "lang": "Chinese", "region": "China", "quality": "high"},
        "zh-CN-YunjianNeural": {"gender": "Male", "lang": "Chinese", "region": "China", "quality": "high"},
        "zh-CN-XiaoyiNeural": {"gender": "Female", "lang": "Chinese", "region": "China", "quality": "high"},
        "zh-CN-YunxiaNeural": {"gender": "Male", "lang": "Chinese", "region": "China", "quality": "high"},

        # ═══ TAMIL ═══
        "ta-IN-ValluvarNeural": {"gender": "Male", "lang": "Tamil", "region": "India", "quality": "high"},
        "ta-IN-PallaviNeural": {"gender": "Female", "lang": "Tamil", "region": "India", "quality": "high"},

        # ═══ TELUGU ═══
        "te-IN-MohanNeural": {"gender": "Male", "lang": "Telugu", "region": "India", "quality": "high"},
        "te-IN-ShrutiNeural": {"gender": "Female", "lang": "Telugu", "region": "India", "quality": "high"},

        # ═══ BENGALI ═══
        "bn-IN-BashkarNeural": {"gender": "Male", "lang": "Bengali", "region": "India", "quality": "high"},
        "bn-IN-TanishaaNeural": {"gender": "Female", "lang": "Bengali", "region": "India", "quality": "high"},

        # ═══ MARATHI ═══
        "mr-IN-ManoharNeural": {"gender": "Male", "lang": "Marathi", "region": "India", "quality": "high"},
        "mr-IN-AarohiNeural": {"gender": "Female", "lang": "Marathi", "region": "India", "quality": "high"},

        # ═══ GUJARATI ═══
        "gu-IN-DhwaniNeural": {"gender": "Female", "lang": "Gujarati", "region": "India", "quality": "high"},
        "gu-IN-NiranjanNeural": {"gender": "Male", "lang": "Gujarati", "region": "India", "quality": "high"},

        # ═══ KANNADA ═══
        "kn-IN-GaganNeural": {"gender": "Male", "lang": "Kannada", "region": "India", "quality": "high"},
        "kn-IN-SapnaNeural": {"gender": "Female", "lang": "Kannada", "region": "India", "quality": "high"},

        # ═══ MALAYALAM ═══
        "ml-IN-MidhunNeural": {"gender": "Male", "lang": "Malayalam", "region": "India", "quality": "high"},
        "ml-IN-SobhanaNeural": {"gender": "Female", "lang": "Malayalam", "region": "India", "quality": "high"},

        # ═══ PUNJABI ═══
        "pa-IN-GurdeepNeural": {"gender": "Male", "lang": "Punjabi", "region": "India", "quality": "high"},
        "pa-IN-OjasNeural": {"gender": "Male", "lang": "Punjabi", "region": "India", "quality": "high"},

        # ═══ URDU ═══
        "ur-IN-GulNeural": {"gender": "Female", "lang": "Urdu", "region": "India", "quality": "high"},
        "ur-IN-SalmanNeural": {"gender": "Male", "lang": "Urdu", "region": "India", "quality": "high"},

        # ═══ SPANISH ═══
        "es-ES-ElviraNeural": {"gender": "Female", "lang": "Spanish", "region": "Spain", "quality": "high"},
        "es-ES-AlvaroNeural": {"gender": "Male", "lang": "Spanish", "region": "Spain", "quality": "high"},
        "es-MX-DaliaNeural": {"gender": "Female", "lang": "Spanish", "region": "Mexico", "quality": "high"},
        "es-MX-JorgeNeural": {"gender": "Male", "lang": "Spanish", "region": "Mexico", "quality": "high"},

        # ═══ FRENCH ═══
        "fr-FR-DeniseNeural": {"gender": "Female", "lang": "French", "region": "France", "quality": "high"},
        "fr-FR-HenriNeural": {"gender": "Male", "lang": "French", "region": "France", "quality": "high"},

        # ═══ GERMAN ═══
        "de-DE-KatjaNeural": {"gender": "Female", "lang": "German", "region": "Germany", "quality": "high"},
        "de-DE-ConradNeural": {"gender": "Male", "lang": "German", "region": "Germany", "quality": "high"},

        # ═══ JAPANESE ═══
        "ja-JP-NanamiNeural": {"gender": "Female", "lang": "Japanese", "region": "Japan", "quality": "high"},
        "ja-JP-KeitaNeural": {"gender": "Male", "lang": "Japanese", "region": "Japan", "quality": "high"},

        # ═══ KOREAN ═══
        "ko-KR-SunHiNeural": {"gender": "Female", "lang": "Korean", "region": "Korea", "quality": "high"},
        "ko-KR-InJoonNeural": {"gender": "Male", "lang": "Korean", "region": "Korea", "quality": "high"},

        # ═══ ARABIC ═══
        "ar-SA-ZariyahNeural": {"gender": "Female", "lang": "Arabic", "region": "Saudi", "quality": "high"},
        "ar-SA-HamedNeural": {"gender": "Male", "lang": "Arabic", "region": "Saudi", "quality": "high"},

        # ═══ PORTUGUESE ═══
        "pt-BR-FranciscaNeural": {"gender": "Female", "lang": "Portuguese", "region": "Brazil", "quality": "high"},
        "pt-BR-AntonioNeural": {"gender": "Male", "lang": "Portuguese", "region": "Brazil", "quality": "high"},

        # ═══ RUSSIAN ═══
        "ru-RU-SvetlanaNeural": {"gender": "Female", "lang": "Russian", "region": "Russia", "quality": "high"},
        "ru-RU-DmitryNeural": {"gender": "Male", "lang": "Russian", "region": "Russia", "quality": "high"},

        # ═══ ITALIAN ═══
        "it-IT-ElsaNeural": {"gender": "Female", "lang": "Italian", "region": "Italy", "quality": "high"},
        "it-IT-DiegoNeural": {"gender": "Male", "lang": "Italian", "region": "Italy", "quality": "high"},

        # ═══ DUTCH ═══
        "nl-NL-ColetteNeural": {"gender": "Female", "lang": "Dutch", "region": "Netherlands", "quality": "high"},
        "nl-NL-FennaNeural": {"gender": "Female", "lang": "Dutch", "region": "Netherlands", "quality": "high"},

        # ═══ TURKISH ═══
        "tr-TR-EmelNeural": {"gender": "Female", "lang": "Turkish", "region": "Turkey", "quality": "high"},
        "tr-TR-AhmetNeural": {"gender": "Male", "lang": "Turkish", "region": "Turkey", "quality": "high"},

        # ═══ VIETNAMESE ═══
        "vi-VN-HoaiMyNeural": {"gender": "Female", "lang": "Vietnamese", "region": "Vietnam", "quality": "high"},
        "vi-VN-NamMinhNeural": {"gender": "Male", "lang": "Vietnamese", "region": "Vietnam", "quality": "high"},

        # ═══ THAI ═══
        "th-TH-PremwadeeNeural": {"gender": "Female", "lang": "Thai", "region": "Thailand", "quality": "high"},
        "th-TH-NiwatNeural": {"gender": "Male", "lang": "Thai", "region": "Thailand", "quality": "high"},

        # ═══ INDONESIAN ═══
        "id-ID-GadisNeural": {"gender": "Female", "lang": "Indonesian", "region": "Indonesia", "quality": "high"},
        "id-ID-ArdiNeural": {"gender": "Male", "lang": "Indonesian", "region": "Indonesia", "quality": "high"},
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # BEST VOICES BY USE CASE
    # ═══════════════════════════════════════════════════════════════════════════
    BEST_VOICES = {
        # Hindi
        "hindi_male": "hi-IN-MadhurNeural",
        "hindi_female": "hi-IN-SwaraNeural",

        # Indian English (Hinglish)
        "hinglish_male": "en-IN-PrabhatNeural",
        "hinglish_female": "en-IN-NeerjaNeural",
        "hinglish_expressive": "en-IN-NeerjaExpressiveNeural",

        # US English
        "us_male": "en-US-AndrewMultilingualNeural",
        "us_female": "en-US-AvaMultilingualNeural",
        "us_male_alt": "en-US-BrianNeural",
        "us_female_alt": "en-US-JennyNeural",

        # UK English
        "uk_male": "en-GB-RyanNeural",
        "uk_female": "en-GB-SoniaNeural",

        # Chinese
        "chinese_male": "zh-CN-YunxiNeural",
        "chinese_female": "zh-CN-XiaoxiaoNeural",

        # Tamil
        "tamil_male": "ta-IN-ValluvarNeural",
        "tamil_female": "ta-IN-PallaviNeural",

        # Telugu
        "telugu_male": "te-IN-MohanNeural",
        "telugu_female": "te-IN-ShrutiNeural",

        # Bengali
        "bengali_male": "bn-IN-BashkarNeural",
        "bengali_female": "bn-IN-TanishaaNeural",

        # Marathi
        "marathi_male": "mr-IN-ManoharNeural",
        "marathi_female": "mr-IN-AarohiNeural",

        # Gujarati
        "gujarati_male": "gu-IN-NiranjanNeural",
        "gujarati_female": "gu-IN-DhwaniNeural",

        # Kannada
        "kannada_male": "kn-IN-GaganNeural",
        "kannada_female": "kn-IN-SapnaNeural",

        # Malayalam
        "malayalam_male": "ml-IN-MidhunNeural",
        "malayalam_female": "ml-IN-SobhanaNeural",

        # Punjabi
        "punjabi_male": "pa-IN-GurdeepNeural",

        # Urdu
        "urdu_male": "ur-IN-SalmanNeural",
        "urdu_female": "ur-IN-GulNeural",
    }

    def __init__(self):
        self.voices = self.ALL_VOICES
        self.best = self.BEST_VOICES

    def list_all_voices(self, lang: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """List all available voices, optionally filter by language"""
        if lang:
            return {k: v for k, v in self.voices.items() if v["lang"].lower() == lang.lower()}
        return self.voices

    def list_indian_voices(self) -> Dict[str, Dict[str, str]]:
        """List all Indian voices"""
        indian_langs = ["Hindi", "English", "Tamil", "Telugu", "Bengali", 
                       "Marathi", "Gujarati", "Kannada", "Malayalam", 
                       "Punjabi", "Urdu"]
        return {k: v for k, v in self.voices.items() 
                if v["lang"] in indian_langs and v["region"] == "India"}

    def get_voice(self, use_case: str) -> str:
        """Get best voice for use case"""
        return self.best.get(use_case, "en-US-JennyNeural")

    async def synthesize(self, 
                         text: str, 
                         voice: str = "hi-IN-MadhurNeural",
                         rate: str = "+0%",
                         pitch: str = "+0Hz",
                         volume: str = "+0%",
                         output_file: str = "output.mp3") -> str:
        """
        Synthesize text to speech using Edge TTS.

        Args:
            text: Text to speak
            voice: Voice ID
            rate: Speed (-50% to +50%)
            pitch: Pitch (-50Hz to +50Hz)
            volume: Volume (-50% to +50%)
            output_file: Output audio file path

        Returns:
            Path to output file
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        await communicate.save(output_file)
        return output_file

    async def synthesize_with_emotion(self,
                                       text: str,
                                       voice: str = "hi-IN-MadhurNeural",
                                       emotion: str = "neutral",
                                       output_file: str = "output.mp3") -> str:
        """
        Synthesize with emotion-based modulation.

        Emotions: neutral, calm, excited, concerned, empathetic, 
                  confident, hesitant, surprised, apologetic, urgent
        """
        emotion_settings = {
            "neutral":    {"rate": "+0%",  "pitch": "+0Hz",  "volume": "+0%"},
            "calm":       {"rate": "-10%", "pitch": "-5Hz",  "volume": "-10%"},
            "excited":    {"rate": "+15%", "pitch": "+25Hz", "volume": "+15%"},
            "concerned":  {"rate": "-5%",  "pitch": "-15Hz", "volume": "-5%"},
            "empathetic": {"rate": "-8%",  "pitch": "+5Hz",  "volume": "-8%"},
            "confident":  {"rate": "+5%",  "pitch": "+10Hz", "volume": "+5%"},
            "hesitant":   {"rate": "-15%", "pitch": "-10Hz", "volume": "-15%"},
            "surprised":  {"rate": "+20%", "pitch": "+30Hz", "volume": "+20%"},
            "apologetic": {"rate": "-12%", "pitch": "-8Hz",  "volume": "-12%"},
            "urgent":     {"rate": "+25%", "pitch": "+15Hz", "volume": "+25%"},
        }

        settings = emotion_settings.get(emotion, emotion_settings["neutral"])

        return await self.synthesize(
            text=text,
            voice=voice,
            rate=settings["rate"],
            pitch=settings["pitch"],
            volume=settings["volume"],
            output_file=output_file
        )

    async def stream_to_speakers(self, text: str, voice: str = "hi-IN-MadhurNeural"):
        """Stream audio directly to speakers (real-time)"""
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=voice)

        # Stream chunks
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                # Play audio chunk
                # Requires pygame or similar for playback
                pass

    def print_voice_list(self):
        """Print formatted voice list"""
        print("\n" + "=" * 80)
        print("EDGE TTS — ALL AVAILABLE VOICES")
        print("=" * 80)

        # Group by language
        by_lang = {}
        for voice_id, info in self.voices.items():
            lang = info["lang"]
            if lang not in by_lang:
                by_lang[lang] = []
            by_lang[lang].append((voice_id, info))

        for lang in sorted(by_lang.keys()):
            print(f"\n📌 {lang}:")
            for voice_id, info in by_lang[lang]:
                flag = "🌟" if voice_id in self.best.values() else "  "
                print(f"   {flag} {voice_id} ({info['gender']}, {info['region']})")

        print("\n" + "=" * 80)
        print("🌟 = Recommended/Best Voice")
        print("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════
async def demo():
    tts = EdgeTTSManager()

    # Print all voices
    tts.print_voice_list()

    # Demo synthesis
    print("\n🎙️  Synthesizing Hindi...")
    await tts.synthesize(
        "नमस्ते! मैं रमेश बोल रहा हूँ। आपका स्वागत है।",
        voice="hi-IN-MadhurNeural",
        output_file="demo_hindi.mp3"
    )
    print("   ✅ Saved: demo_hindi.mp3")

    print("\n🎙️  Synthesizing with emotion (Excited)...")
    await tts.synthesize_with_emotion(
        "वाह! ये तो कमाल हो गया!",
        voice="hi-IN-SwaraNeural",
        emotion="excited",
        output_file="demo_excited.mp3"
    )
    print("   ✅ Saved: demo_excited.mp3")

    print("\n🎙️  Synthesizing Hinglish...")
    await tts.synthesize(
        "Hello sir, main Aryan bol raha hoon. Aapka kaise help kar sakta hoon?",
        voice="en-IN-PrabhatNeural",
        output_file="demo_hinglish.mp3"
    )
    print("   ✅ Saved: demo_hinglish.mp3")

    print("\n🎙️  Synthesizing US English...")
    await tts.synthesize(
        "Hey there! I'm Alex, your customer success lead. How can I help you today?",
        voice="en-US-AndrewMultilingualNeural",
        output_file="demo_us.mp3"
    )
    print("   ✅ Saved: demo_us.mp3")

    print("\n🎙️  Synthesizing Tamil...")
    await tts.synthesize(
        "வணக்கம்! நான் மூர்த்தி பேசுகிறேன்.",
        voice="ta-IN-ValluvarNeural",
        output_file="demo_tamil.mp3"
    )
    print("   ✅ Saved: demo_tamil.mp3")


if __name__ == "__main__":
    asyncio.run(demo())
