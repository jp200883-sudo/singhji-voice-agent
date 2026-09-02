"""
Full-duplex WebSocket Router for Telephony / Live Voice Calls
Gemini Live API integration
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import websockets

from config.settings import settings
from core.connection_manager import manager


router = APIRouter(prefix="/ws", tags=["voice"])

GEMINI_LIVE_URL = (
    f"wss://generativelanguage.googleapis.com/ws/"
    f"google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
    f"?key={settings.gemini_api_key}"
)


async def gemini_live_session(client_ws: WebSocket, call_id: str):
    """Bridge between client WebSocket and Gemini Live API"""
    try:
        async with websockets.connect(GEMINI_LIVE_URL) as gemini_ws:
            # Setup Gemini session
            setup_msg = {
                "setup": {
                    "model": f"models/{settings.gemini_live_model}",
                    "generation_config": {
                        "response_modalities": ["AUDIO"],
                        "speech_config": {
                            "voice_config": {
                                "prebuilt_voice_config": {"voice_name": "Puck"}
                            }
                        }
                    },
                    "system_instruction": {
                        "parts": [{
                            "text": "You are Priya, a polite, smart Indian AI voice assistant. Speak concisely in natural Hindi/Hinglish."
                        }]
                    }
                }
            }
            await gemini_ws.send(json.dumps(setup_msg))

            # Client → Gemini
            async def phone_to_gemini():
                while True:
                    message = await client_ws.receive_text()
                    data = json.loads(message)
                    if data.get("event") == "media":
                        payload = data["media"]["payload"]
                        audio_msg = {
                            "realtime_input": {
                                "media_chunks": [{
                                    "mime_type": "audio/pcm;rate=16000",
                                    "data": payload
                                }]
                            }
                        }
                        await gemini_ws.send(json.dumps(audio_msg))
                    elif data.get("event") == "stop":
                        break

            # Gemini → Client
            async def gemini_to_phone():
                async for message in gemini_ws:
                    response = json.loads(message)
                    server_content = response.get("serverContent", {})
                    parts = server_content.get("modelTurn", {}).get("parts", [])
                    for part in parts:
                        inline_data = part.get("inlineData")
                        if inline_data:
                            audio_b64 = inline_data.get("data")
                            await client_ws.send_json({
                                "event": "media",
                                "media": {"payload": audio_b64}
                            })

            await asyncio.gather(phone_to_gemini(), gemini_to_phone())

    except WebSocketDisconnect:
        print(f"🔌 Call disconnected: {call_id}")
    except Exception as e:
        print(f"❌ Gemini Live Error ({call_id}): {e}")


@router.websocket("/call/{call_id}")
async def websocket_call(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for live voice calls"""
    await manager.connect(call_id, websocket)
    manager.start_cleanup()

    try:
        await gemini_live_session(websocket, call_id)
    except WebSocketDisconnect:
        print(f"📴 Call disconnected: {call_id}")
    except Exception as e:
        print(f"❌ Call runtime error: {e}")
    finally:
        manager.disconnect(call_id)
