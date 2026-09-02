import os
import logging
from fastapi import APIRouter, Request
import httpx
from groq import AsyncGroq
import edge_tts

from core.persona_matrix import PersonaMatrix
from config.settings import settings

logger = logging.getLogger("singhji-telegram")
router = APIRouter()

groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    टेलीग्राम बॉट वेबहुक: टेक्स्ट/वॉइस मैसेज हैंडलर (फ्री ग्रॉक + एज टीटीएस)
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"status": "token_not_configured"}

    payload = await request.json()
    message = payload.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return {"status": "ignored"}

    # डिफ़ॉल्ट देसी/यूपी पर्सोना
    agent_id = "up_bhaiya"
    profile = PersonaMatrix.get_agent_profile(agent_id)
    system_prompt = PersonaMatrix.build_system_prompt(agent_id)

    # 1. फ्री LLM कॉल (Groq)
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text or "नमस्ते"}
            ],
            model="llama3-8b-8192",
            max_tokens=100
        )
        reply_text = chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API Error: {str(e)}")
        reply_text = "अरे भैया, थोड़ा सा नेटवर्क इशू आ गया, दोबारा बोलना जरा!"

    # 2. फ्री वॉइस जनरेशन (Edge-TTS)
    audio_file = f"/tmp/reply_{chat_id}.mp3"
    voice_name = profile.get("voice", "hi-IN-MadhurNeural")
    tts = edge_tts.Communicate(reply_text, voice_name)
    await tts.save(audio_file)

    # 3. टेलीग्राम पर टेक्स्ट और वॉइस दोनों भेजना
    async with httpx.AsyncClient() as client:
        # टेक्स्ट मैसेज
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reply_text}
        )
        # वॉइस नोट
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                await client.post(
                    f"{TELEGRAM_API_URL}/sendVoice",
                    data={"chat_id": chat_id},
                    files={"voice": f}
                )
            os.remove(audio_file)

    return {"status": "success"}
