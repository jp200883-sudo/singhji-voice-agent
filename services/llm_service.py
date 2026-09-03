"""
Singh Ji Voice AI — LLM Service
5-Layer Free Fallback: Groq → Gemini → OpenRouter → HF → Local
"""

import os
import asyncio
from typing import Optional, AsyncGenerator
import httpx

from config import settings


class LLMService:
    """
    5-Layer LLM Fallback System
    All free tiers, auto-fallback on failure
    """

    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.openrouter_client = None
        self._init_clients()

    def _init_clients(self):
        """Lazy init API clients"""
        # Groq
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                pass

        # Gemini
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai
            except ImportError:
                pass

        # OpenRouter (uses OpenAI-compatible client)
        if settings.OPENROUTER_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openrouter_client = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.OPENROUTER_API_KEY
                )
            except ImportError:
                pass

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        model: Optional[str] = None
    ) -> str:
        """
        Generate response with auto-fallback

        Priority: Groq → Gemini → OpenRouter → HF Inference → Error
        """
        # Layer 1: Groq (fastest, 20 req/min free)
        if self.groq_client:
            try:
                return await self._groq_generate(prompt, system_prompt, temperature, max_tokens, model)
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")

        # Layer 2: Gemini (60 req/min free)
        if self.gemini_client:
            try:
                return await self._gemini_generate(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}")

        # Layer 3: OpenRouter (free tier)
        if self.openrouter_client:
            try:
                return await self._openrouter_generate(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                print(f"⚠️ OpenRouter failed: {e}")

        # Layer 4: HuggingFace Inference API
        if settings.HF_API_TOKEN:
            try:
                return await self._hf_generate(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                print(f"⚠️ HF failed: {e}")

        # All layers failed
        raise RuntimeError("All LLM services failed. Please check API keys.")

    async def _groq_generate(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int, model: Optional[str]
    ) -> str:
        """Groq API call"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model_name = model or settings.GROQ_MODEL

        response = self.groq_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    async def _gemini_generate(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """Gemini API call"""
        model = self.gemini_client.GenerativeModel(settings.GEMINI_MODEL)

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )

        return response.text

    async def _openrouter_generate(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """OpenRouter API call"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.openrouter_client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "https://singhji-ai.com",
                "X-Title": "Singh Ji Voice AI"
            }
        )

        return response.choices[0].message.content

    async def _hf_generate(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """HuggingFace Inference API call"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{settings.HF_LLM_MODEL}",
                headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "temperature": temperature,
                        "max_new_tokens": max_tokens
                    }
                },
                timeout=30.0
            )

            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream response token by token (Groq only)"""
        if not self.groq_client:
            # Fallback to non-streaming
            response = await self.generate(prompt, system_prompt, temperature)
            yield response
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"⚠️ Streaming failed: {e}")
            response = await self.generate(prompt, system_prompt, temperature)
            yield response


# Global LLM service instance
llm_service = LLMService()
