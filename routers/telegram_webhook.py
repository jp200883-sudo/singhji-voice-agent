"""
Singh Ji Voice AI — Telegram Bot Webhook Router
Async TG Bot with background voice tasks
"""

import os
import asyncio
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from services.llm_service import llm_service
from services.stt_service import stt_service
from services.tts_manager import tts_manager
from core.persona_matrix import persona_matrix
from config import settings


router = APIRouter(prefix="/telegram", tags=["telegram"])

# In-memory conversation store (replace with Redis/DB in production)
user_sessions = {}


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telegram Bot Webhook
    Handles: text messages, voice messages, commands
    """
    data = await request.json()

    # Verify webhook secret
    # (In production, verify X-Telegram-Bot-Api-Secret-Token header)

    if "message" not in data:
        return JSONResponse({"status": "ok"})

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    # Initialize user session
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "persona": "friendly_helper",
            "language": "hi",
            "history": []
        }

    session = user_sessions[user_id]

    try:
        # Handle different message types
        if "text" in message:
            text = message["text"]

            # Check for commands
            if text.startswith("/"):
                await handle_command(chat_id, text, session)
            else:
                # Regular text message
                background_tasks.add_task(
                    process_text_message,
                    chat_id, text, session
                )

        elif "voice" in message:
            # Voice message
            voice = message["voice"]
            background_tasks.add_task(
                process_voice_message,
                chat_id, voice, session
            )

        elif "audio" in message:
            # Audio file
            audio = message["audio"]
            background_tasks.add_task(
                process_voice_message,
                chat_id, audio, session
            )

        return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"❌ Telegram webhook error: {e}")
        return JSONResponse({"status": "error", "message": str(e)})


async def handle_command(chat_id: int, command: str, session: dict):
    """Handle Telegram bot commands"""
    from httpx import AsyncClient

    bot_token = settings.TELEGRAM_BOT_TOKEN
    api_url = f"https://api.telegram.org/bot{bot_token}"

    async with AsyncClient() as client:
        if command == "/start":
            persona = persona_matrix.get_persona(session["persona"])
            greeting = persona.greeting if persona else "Namaste! Main Singh Ji hoon."

            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"{greeting}\n\nCommands:\n/persona — Change persona\n/voices — List voices\n/help — Help"
            })

        elif command == "/help":
            help_text = """🎙️ Singh Ji Voice AI — Commands:

/persona — Change voice persona
/voices — List available voices
/language — Change language
/reset — Reset conversation
/help — Show this help

Just send voice or text to chat!"""

            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": help_text
            })

        elif command == "/persona":
            personas = persona_matrix.list_personas()
            text = "🎭 Choose persona:\n"
            for p in personas:
                text += f"\n• {p['id']} — {p['name']} ({p['language']})"

            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": text
            })

        elif command == "/voices":
            voices = tts_manager.get_voice_list()
            text = "🎙️ Available voices:\n"
            for vid, v in list(voices.items())[:10]:
                text += f"\n• {vid} — {v['name']} ({v['gender']})"
            text += "\n\n...and more!"

            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": text
            })

        elif command == "/reset":
            session["history"] = []
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": "🔄 Conversation reset!"
            })

        else:
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Unknown command. Use /help for list."
            })


async def process_text_message(chat_id: int, text: str, session: dict):
    """Process text message: LLM → TTS → Send voice"""
    from httpx import AsyncClient

    bot_token = settings.TELEGRAM_BOT_TOKEN
    api_url = f"https://api.telegram.org/bot{bot_token}"

    async with AsyncClient() as client:
        try:
            # Send "typing" action
            await client.post(f"{api_url}/sendChatAction", json={
                "chat_id": chat_id,
                "action": "typing"
            })

            # Build system prompt
            system_prompt = persona_matrix.build_system_prompt(session["persona"])

            # Generate response
            response_text = await llm_service.generate(
                prompt=text,
                system_prompt=system_prompt
            )

            # Send text response
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": response_text
            })

            # Generate voice response
            voice_id = persona_matrix.get_voice_for_persona(session["persona"])
            ogg_path = await tts_manager.synthesize_telegram(
                response_text,
                voice=voice_id,
                language=session["language"]
            )

            # Send voice
            with open(ogg_path, "rb") as voice_file:
                await client.post(
                    f"{api_url}/sendVoice",
                    data={"chat_id": chat_id},
                    files={"voice": ("voice.ogg", voice_file, "audio/ogg")}
                )

            # Clean up
            if os.path.exists(ogg_path):
                os.remove(ogg_path)

            # Store in history
            session["history"].append({"user": text, "ai": response_text})

        except Exception as e:
            print(f"❌ Text processing error: {e}")
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"Sorry, error occurred: {str(e)}"
            })


async def process_voice_message(chat_id: int, voice: dict, session: dict):
    """Process voice message: Download → STT → LLM → TTS → Send"""
    from httpx import AsyncClient

    bot_token = settings.TELEGRAM_BOT_TOKEN
    api_url = f"https://api.telegram.org/bot{bot_token}"

    async with AsyncClient() as client:
        try:
            # Send "typing" action
            await client.post(f"{api_url}/sendChatAction", json={
                "chat_id": chat_id,
                "action": "typing"
            })

            # Get voice file
            file_id = voice["file_id"]
            file_info = await client.get(f"{api_url}/getFile?file_id={file_id}")
            file_path = file_info.json()["result"]["file_path"]

            # Download voice
            file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            voice_response = await client.get(file_url)
            voice_data = voice_response.content

            # STT
            transcript = await stt_service.transcribe(voice_data, language=session["language"])

            # Send transcript
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"🎤 You said: {transcript}"
            })

            # Process with LLM
            system_prompt = persona_matrix.build_system_prompt(session["persona"])
            response_text = await llm_service.generate(
                prompt=transcript,
                system_prompt=system_prompt
            )

            # Send text
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": response_text
            })

            # Generate voice
            voice_id = persona_matrix.get_voice_for_persona(session["persona"])
            ogg_path = await tts_manager.synthesize_telegram(
                response_text,
                voice=voice_id,
                language=session["language"]
            )

            # Send voice
            with open(ogg_path, "rb") as voice_file:
                await client.post(
                    f"{api_url}/sendVoice",
                    data={"chat_id": chat_id},
                    files={"voice": ("voice.ogg", voice_file, "audio/ogg")}
                )

            # Clean up
            if os.path.exists(ogg_path):
                os.remove(ogg_path)

            # Store history
            session["history"].append({"user": transcript, "ai": response_text})

        except Exception as e:
            print(f"❌ Voice processing error: {e}")
            await client.post(f"{api_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"Sorry, could not process voice: {str(e)}"
            })


@router.get("/stats")
async def telegram_stats():
    """Get Telegram bot statistics"""
    return {
        "active_users": len(user_sessions),
        "users": list(user_sessions.keys()),
        "total_conversations": sum(len(s["history"]) for s in user_sessions.values())
    }
