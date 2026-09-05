import asyncio
import json
import logging
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from groq import AsyncGroq
import edge_tts

from core.persona_matrix import PersonaMatrix
from core.stt_service import stt_service  # ⬅️ ADD THIS
from config.settings import settings

logger = logging.getLogger("singhji-voice-ws")
router = APIRouter()

# 100% Free Inference Client (Groq Free Tier)
groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


@router.websocket("/stream/{agent_id}")
async def voice_stream_endpoint(websocket: WebSocket, agent_id: str):
    """
    फुल-डुप्लेक्स लाइव वॉयस पाइपलाइन:
    WebSocket Audio In -> STT -> Groq LLM -> Edge-TTS -> Audio Out
    """
    await websocket.accept()
    logger.info(f"Connected to voice agent session: {agent_id}")

    # एजेंट का पर्सोना और सिस्टम प्रॉम्प्ट लोड करें
    profile = PersonaMatrix.get_agent_profile(agent_id)
    system_prompt = PersonaMatrix.build_system_prompt(agent_id)

    conversation_history = [
        {"role": "system", "content": system_prompt}
    ]

    try:
        while True:
            # ⬇️ NEW: Receive audio OR text from client
            message = await websocket.receive()
            
            # Check if it's binary (audio) or text (JSON)
            if "bytes" in message:
                # === AUDIO INPUT (from ESP32/mobile app) ===
                audio_data = message["bytes"]
                logger.info(f"Received {len(audio_data)} bytes of audio")
                
                # STT: Convert audio to text (4-layer fallback)
                try:
                    user_text = await stt_service.transcribe(
                        audio_data=audio_data,
                        language="hi"  # Hindi/Hinglish
                    )
                    logger.info(f"STT Result: {user_text}")
                except Exception as e:
                    logger.error(f"STT failed: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Could not understand audio. Please try again."
                    })
                    continue
                
                if not user_text or len(user_text.strip()) < 2:
                    continue
                
                # Send transcript back to client (for debugging)
                await websocket.send_json({
                    "type": "transcript",
                    "text": user_text
                })
            
            elif "text" in message:
                # === TEXT INPUT (from web interface) ===
                event = json.loads(message["text"])
                user_text = event.get("text", "").strip()
                
                if not user_text:
                    continue
            
            # 2. तुरंत नेचुरल फिलर (Ahhs, रुको, Let me see)
            filler_text = PersonaMatrix.get_filler(agent_id, category="thinking")
            await websocket.send_json({
                "type": "filler",
                "text": filler_text
            })

            # 3. LLM प्रोसेसिंग (Groq Llama-3 8B)
            conversation_history.append({"role": "user", "content": user_text})
            
            chat_completion = await groq_client.chat.completions.create(
                messages=conversation_history,
                model="llama3-8b-8192",
                temperature=0.6,
                max_tokens=80
            )
            response_text = chat_completion.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": response_text})

            # 4. फ्री TTS जनरेशन (Microsoft Edge-TTS)
            voice_name = profile.get("voice", "hi-IN-MadhurNeural")
            tts = edge_tts.Communicate(response_text, voice_name)
            
            audio_buffer = bytearray()
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    audio_buffer.extend(chunk["data"])

            # 5. ऑडियो बाइट्स और टेक्स्ट वापस क्लाइंट को स्ट्रीम करना
            await websocket.send_json({
                "type": "response_text",
                "text": response_text
            })
            await websocket.send_bytes(bytes(audio_buffer))

    except WebSocketDisconnect:
        logger.info(f"Session closed for agent: {agent_id}")
    except Exception as e:
        logger.error(f"Error in voice stream pipeline: {str(e)}")
        await websocket.close()
