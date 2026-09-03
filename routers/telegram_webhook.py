"""
Singh Ji Voice AI — Voice WebSocket Router
Full-duplex WebSocket for telephony and live voice
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.connection_manager import manager
from core.audio_streamer import audio_streamer
from core.persona_matrix import persona_matrix
from services.llm_service import llm_service
from services.stt_service import stt_service
from services.tts_manager import tts_manager
from config import settings


router = APIRouter(prefix="/ws/voice", tags=["voice-websocket"])


@router.websocket("/{client_id}")
async def voice_websocket(websocket: WebSocket, client_id: str):
    """
    Full-duplex WebSocket for real-time voice

    Flow:
    1. Client connects
    2. Client sends audio chunks (Mu-Law/OGG)
    3. Server transcribes → LLM → TTS → streams back audio
    """
    connected = await manager.connect(websocket, client_id)
    if not connected:
        return

    # Default persona
    current_persona = "friendly_helper"

    try:
        # Send welcome message
        persona = persona_matrix.get_persona(current_persona)
        welcome_msg = {
            "type": "greeting",
            "text": persona.greeting if persona else "Hello! I am Singh Ji Voice AI.",
            "persona": current_persona,
            "voice": persona_matrix.get_voice_for_persona(current_persona)
        }
        await manager.send_text(client_id, json.dumps(welcome_msg))

        while True:
            # Receive message from client
            message = await websocket.receive()

            if "text" in message:
                # Text command
                data = json.loads(message["text"])
                await handle_text_command(client_id, data, current_persona)

            elif "bytes" in message:
                # Audio data
                audio_data = message["bytes"]
                await handle_audio_input(client_id, audio_data, current_persona)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WS Error for {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_text_command(client_id: str, data: dict, persona_name: str):
    """Handle text commands from client"""
    command = data.get("command")

    if command == "set_persona":
        new_persona = data.get("persona", "friendly_helper")
        persona = persona_matrix.get_persona(new_persona)
        if persona:
            response = {
                "type": "persona_changed",
                "persona": new_persona,
                "greeting": persona.greeting
            }
            await manager.send_text(client_id, json.dumps(response))

    elif command == "chat":
        text = data.get("text", "")
        await process_conversation(client_id, text, persona_name)

    elif command == "ping":
        await manager.send_text(client_id, json.dumps({"type": "pong"}))

    elif command == "get_voices":
        voices = tts_manager.get_voice_list()
        response = {"type": "voices", "voices": voices}
        await manager.send_text(client_id, json.dumps(response))


async def handle_audio_input(client_id: str, audio_data: bytes, persona_name: str):
    """Handle audio input: STT → LLM → TTS → Stream back"""
    try:
        # Step 1: Convert audio format if needed
        # Mu-Law 8k → PCM 16k
        pcm_data = audio_streamer.mulaw_to_pcm(audio_data)

        # Step 2: STT (Speech-to-Text)
        transcript = await stt_service.transcribe(pcm_data, language="hi")

        # Send transcript to client
        await manager.send_text(client_id, json.dumps({
            "type": "transcript",
            "text": transcript
        }))

        # Step 3: Process with LLM
        await process_conversation(client_id, transcript, persona_name)

    except Exception as e:
        await manager.send_text(client_id, json.dumps({
            "type": "error",
            "message": f"Audio processing failed: {str(e)}"
        }))


async def process_conversation(client_id: str, text: str, persona_name: str):
    """Full pipeline: LLM → TTS → Stream audio"""
    try:
        # Build system prompt with persona
        system_prompt = persona_matrix.build_system_prompt(persona_name)

        # Get LLM response
        response_text = await llm_service.generate(
            prompt=text,
            system_prompt=system_prompt
        )

        # Send text response
        await manager.send_text(client_id, json.dumps({
            "type": "response",
            "text": response_text
        }))

        # Get voice for persona
        voice_id = persona_matrix.get_voice_for_persona(persona_name)

        # Stream TTS audio back
        await manager.send_text(client_id, json.dumps({
            "type": "audio_start",
            "voice": voice_id
        }))

        async for chunk in tts_manager.synthesize_stream(response_text, voice=voice_id):
            await manager.send_bytes(client_id, chunk)

        await manager.send_text(client_id, json.dumps({
            "type": "audio_end"
        }))

    except Exception as e:
        await manager.send_text(client_id, json.dumps({
            "type": "error",
            "message": f"Conversation failed: {str(e)}"
        }))


@router.get("/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_stats()
