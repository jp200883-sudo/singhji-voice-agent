"""
Telegram Bot Webhook Router
Async voice processing with background tasks
"""

import io
import wave
import numpy as np
from fastapi import APIRouter, BackgroundTasks

from config.settings import settings, VOICE_CONFIG
from core.audio_streamer import AudioStreamer
from core.persona_matrix import persona_matrix
from services.llm_service import llm_service
from services.stt_service import stt_service
from services.tts_manager import tts_manager


router = APIRouter(prefix="/webhook", tags=["telegram"])

# Conversation history
conversation_history: dict = {}

# HTTP client for Telegram
_tg_http_client = None

async def _get_tg_client():
    global _tg_http_client
    if _tg_http_client is None or _tg_http_client.is_closed:
        import httpx
        _tg_http_client = httpx.AsyncClient(timeout=30.0)
    return _tg_http_client


async def tg_send_text(chat_id: str, text: str):
    """Send text message to Telegram"""
    try:
        client = await _get_tg_client()
        url = f"https://api.telegram.org/bot{settings.telegram_voice_bot_token}/sendMessage"
        await client.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"❌ tg_send_text error: {e}")


async def tg_send_voice(chat_id: str, audio_bytes: bytes):
    """Send voice message to Telegram"""
    try:
        client = await _get_tg_client()
        url = f"https://api.telegram.org/bot{settings.telegram_voice_bot_token}/sendVoice"
        files = {"voice": ("voice.ogg", audio_bytes, "audio/ogg")}
        data = {"chat_id": chat_id}
        resp = await client.post(url, data=data, files=files)
        if resp.status_code != 200:
            print(f"❌ Voice send failed: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ tg_send_voice error: {e}")


async def process_voice_message(chat_id: str, voice_data: dict):
    """Process voice message in background"""
    try:
        file_id = voice_data["file_id"]

        # Download voice file
        client = await _get_tg_client()
        get_file_url = f"https://api.telegram.org/bot{settings.telegram_voice_bot_token}/getFile"
        resp = await client.post(get_file_url, json={"file_id": file_id})
        file_data = resp.json()

        if not file_data.get("ok"):
            await tg_send_text(chat_id, "⚠️ ऑडियो प्राप्त करने में त्रुटि हुई।")
            return

        file_path = file_data["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{settings.telegram_voice_bot_token}/{file_path}"
        file_resp = await client.get(download_url)
        voice_bytes = file_resp.content

        # Convert OGG to PCM
        pcm_audio = AudioStreamer.ogg_to_pcm(voice_bytes)

        # Gender detection
        from core.audio_streamer import detect_gender_from_pitch
        caller_gender = detect_gender_from_pitch(pcm_audio, sample_rate=16000)

        # Dynamic persona selection
        if caller_gender == "male":
            persona_key = "priya"
            reply_voice = "female"
            avatar = "👩‍💼 Priya:"
        else:
            persona_key = "singhji"
            reply_voice = "male"
            avatar = "🧔 Singh Ji:"

        # STT
        transcribed_text = await stt_service.transcribe(pcm_audio, language="hi")
        if not transcribed_text:
            await tg_send_text(chat_id, "😅 आवाज़ स्पष्ट नहीं सुनाई दी, कृपया पुनः प्रयास करें।")
            return

        await tg_send_text(chat_id, f"🎤 आपने कहा: {transcribed_text}")

        # LLM Response
        persona = persona_matrix.get_persona(gender=caller_gender)
        history = conversation_history.get(chat_id, [])

        ai_response = await llm_service.get_response(
            user_text=transcribed_text,
            system_prompt=persona["system_prompt"],
            history=history
        )

        await tg_send_text(chat_id, f"{avatar} {ai_response}")

        # TTS
        ogg_audio = await tts_manager.synthesize(ai_response, voice_type=reply_voice)
        if ogg_audio:
            await tg_send_voice(chat_id, ogg_audio)

        # Update history
        history.append({"user": transcribed_text, "ai": ai_response})
        conversation_history[chat_id] = history[-6:]

    except Exception as e:
        print(f"❌ Voice processing error: {e}")
        await tg_send_text(chat_id, "❌ ऑडियो प्रोसेस करने में तकनीकी समस्या आई।")


async def process_text_message(chat_id: str, user_text: str):
    """Process text message in background"""
    try:
        # Default: Priya persona for text
        persona = persona_matrix.get_persona(gender="male")  # Male caller → Female response
        history = conversation_history.get(chat_id, [])

        ai_response = await llm_service.get_response(
            user_text=user_text,
            system_prompt=persona["system_prompt"],
            history=history
        )

        await tg_send_text(chat_id, f"👩‍💼 {ai_response}")

        # TTS
        ogg_audio = await tts_manager.synthesize(ai_response, voice_type="female")
        if ogg_audio:
            await tg_send_voice(chat_id, ogg_audio)

        # Update history
        history.append({"user": user_text, "ai": ai_response})
        conversation_history[chat_id] = history[-6:]

    except Exception as e:
        print(f"❌ Text processing error: {e}")
        await tg_send_text(chat_id, "❌ संदेश प्रोसेस करने में त्रुटि आई।")


@router.post("/telegram")
async def telegram_webhook(data: dict, background_tasks: BackgroundTasks):
    """Handle Telegram webhook updates"""
    try:
        message = data.get("message")
        if not message:
            return {"status": "ignored"}

        chat_id = str(message["chat"]["id"])
        user_text = message.get("text", "")
        voice = message.get("voice")

        # /start command
        if user_text and user_text.startswith("/start"):
            await tg_send_text(
                chat_id,
                "👋 नमस्ते! मैं प्रिया हूँ, Singh Ji AI की वॉइस असिस्टेंट।\n\n"
                "🎤 Voice message भेजें → Voice reply मिलेगा\n"
                "📝 Text भेजें → Text + Voice reply मिलेगा"
            )
            return {"status": "ok"}

        # Text message
        if user_text and not user_text.startswith("/"):
            background_tasks.add_task(process_text_message, chat_id, user_text)
            return {"status": "processing"}

        # Voice message
        if voice:
            background_tasks.add_task(process_voice_message, chat_id, voice)
            return {"status": "processing"}

        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Telegram webhook error: {e}")
        return {"status": "error", "message": str(e)}
