"""
5-Layer LLM Fallback Service
Groq → Sarvam → Gemini → OpenRouter → Hugging Face
"""

import asyncio
import re
from typing import List, Dict, Optional
import httpx
from groq import Groq

from config.settings import settings, GROQ_MODELS


# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=15.0)
    return _http_client


# Groq client
groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


class LLMService:
    """Multi-provider LLM with automatic fallback"""

    @staticmethod
    def clean_response(text: str) -> str:
        """Clean AI thinking artifacts"""
        text = re.sub(r'\s*thinking\s*.*?\s*end_thinking\s*', '', text, flags=re.DOTALL)
        text = re.sub(r"Here\'s a thinking process:.*?\n", '', text, flags=re.DOTALL)
        text = re.sub(r'Thinking:.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'[\*\_#`]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _build_messages(user_text: str, system_prompt: str, history: List[Dict] = None) -> List[Dict]:
        """Build message array with history"""
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history[-4:]:
                messages.append({"role": "user", "content": h.get("user", "")})
                messages.append({"role": "assistant", "content": h.get("ai", "")})
        messages.append({"role": "user", "content": user_text})
        return messages

    @classmethod
    async def _try_groq(cls, messages: List[Dict]) -> str:
        """Groq API with multiple model fallback"""
        if not settings.groq_api_key or groq_client is None:
            raise Exception("Groq not configured")

        for model in GROQ_MODELS:
            try:
                def _call():
                    return groq_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=120,
                        temperature=0.6
                    )
                resp = await asyncio.to_thread(_call)
                return resp.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Groq {model} failed: {e}")
                continue
        raise Exception("All Groq models failed")

    @classmethod
    async def _try_gemini(cls, messages: List[Dict]) -> str:
        """Gemini API fallback"""
        if not settings.gemini_api_key:
            raise Exception("Gemini not configured")

        client = _get_http_client()
        prompt_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        resp = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "Content-Type": "application/json"
            },
            json={"contents": [{"parts": [{"text": prompt_text}]}]}
        )
        data = resp.json()

        if "error" in data:
            raise Exception(f"Gemini error: {data['error']}")

        return data["candidates"][0]["content"]["parts"][0]["text"]

    @classmethod
    async def _try_openrouter(cls, messages: List[Dict]) -> str:
        """OpenRouter API fallback"""
        if not settings.openrouter_api_key:
            raise Exception("OpenRouter not configured")

        client = _get_http_client()
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://singh-ji-voice-agent.onrender.com",
                "X-Title": "Singh Ji AI"
            },
            json={
                "model": "openrouter/free",
                "messages": messages,
                "max_tokens": 120,
                "temperature": 0.6
            }
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    @classmethod
    async def _try_huggingface(cls, messages: List[Dict]) -> str:
        """Hugging Face API fallback"""
        if not settings.huggingface_api_key:
            raise Exception("HuggingFace not configured")

        client = _get_http_client()
        system_prompt = messages[0]["content"]
        user_text = messages[-1]["content"]

        hf_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        prompt_full = f"<s>[INST] {system_prompt}\n\nUser: {user_text} [/INST]"

        resp = await client.post(
            hf_url,
            headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
            json={"inputs": prompt_full, "parameters": {"max_new_tokens": 120, "temperature": 0.6}}
        )
        data = resp.json()

        if isinstance(data, list) and len(data) > 0:
            generated = data[0].get("generated_text", "")
            return generated.split("[/INST]")[-1].strip()
        raise Exception("Invalid HF response format")

    @classmethod
    async def get_response(
        cls,
        user_text: str,
        system_prompt: str,
        history: List[Dict] = None
    ) -> str:
        """Get AI response with automatic fallback"""
        messages = cls._build_messages(user_text, system_prompt, history)

        providers = [
            ("Groq", cls._try_groq, bool(settings.groq_api_key)),
            ("Gemini", cls._try_gemini, bool(settings.gemini_api_key)),
            ("OpenRouter", cls._try_openrouter, bool(settings.openrouter_api_key)),
            ("HuggingFace", cls._try_huggingface, bool(settings.huggingface_api_key)),
        ]

        for name, fn, has_key in providers:
            if not has_key:
                continue
            try:
                raw = await fn(messages)
                clean = cls.clean_response(raw)
                if clean:
                    return clean
            except Exception as e:
                print(f"⚠️ {name} failed: {e}")
                continue

        return "जी, मैं आपकी बात समझ नहीं पाई। क्या आप दोबारा कह सकते हैं?"


# Singleton
llm_service = LLMService()
