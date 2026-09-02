"""
Persona Injection Matrix
Tone, Age, Regional Accents for different user types
"""

from typing import Dict


class PersonaMatrix:
    """Dynamic persona selection based on caller profile"""

    # Base personas
    PERSONAS = {
        "priya": {
            "name": "Priya",
            "gender": "female",
            "tone": "polite, sweet, helpful",
            "age_hint": "25-30",
            "accent": "neutral Hindi",
            "voice": "hi-IN-SwaraNeural",
            "rate": "+3%",
            "pitch": "+0Hz",
            "avatar": "👩‍💼 Priya:",
            "system_prompt": (
                "You are Priya, a polite, sweet, and intelligent AI personal assistant for Singh Ji / Singularity AI. "
                "Speak naturally in polite, friendly Hinglish (Hindi + English mix). "
                "Keep replies strictly under 2 short sentences. "
                "Never use asterisks or markdown formatting. Output only the spoken final response."
            )
        },
        "singhji": {
            "name": "Singh Ji",
            "gender": "male",
            "tone": "confident, sharp, authoritative",
            "age_hint": "30-35",
            "accent": "neutral Hindi",
            "voice": "hi-IN-MadhurNeural",
            "rate": "+2%",
            "pitch": "-1Hz",
            "avatar": "🧔 Singh Ji:",
            "system_prompt": (
                "You are Singh Ji AI, a confident, sharp, and helpful Indian voice AI. "
                "Speak naturally in Hinglish (Hindi + English mix). "
                "Keep replies strictly under 2 short sentences. "
                "Never use asterisks or markdown formatting. Output only the spoken final response."
            )
        }
    }

    # Regional accent modifiers
    REGIONAL_MODIFIERS = {
        "punjabi": {"greeting": "Sat Sri Akal", "style": "warm, energetic"},
        "bhojpuri": {"greeting": "Ram Ram", "style": "friendly, earthy"},
        "haryanvi": {"greeting": "Ram Ram", "style": "bold, direct"},
        "rajasthani": {"greeting": "Khamma Ghani", "style": "respectful, traditional"},
    }

    @classmethod
    def get_persona(cls, gender: str = "male", region: str = None) -> Dict:
        """Get appropriate persona based on caller profile"""
        # Male caller → Female response (Priya)
        # Female caller → Male response (Singh Ji)
        persona_key = "priya" if gender == "male" else "singhji"

        persona = cls.PERSONAS[persona_key].copy()

        # Apply regional modifier if available
        if region and region in cls.REGIONAL_MODIFIERS:
            modifier = cls.REGIONAL_MODIFIERS[region]
            persona["greeting"] = modifier["greeting"]
            persona["tone"] += f", {modifier['style']}"

        return persona

    @classmethod
    def get_voice_config(cls, persona_key: str) -> Dict:
        """Get voice config for TTS"""
        p = cls.PERSONAS[persona_key]
        return {
            "voice": p["voice"],
            "rate": p["rate"],
            "pitch": p["pitch"]
        }


# Singleton
persona_matrix = PersonaMatrix()
