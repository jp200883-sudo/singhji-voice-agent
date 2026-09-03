i Voice AI — Ultimate Free Edition
300+ free TTS voices | Edge TTS + Kokoro + Piper | Cloud deploy ready
https://python.org
LICENSE
https://render.com
Features
300+ Voices across 3 free TTS engines
50+ Languages including Hindi, Hinglish, Tamil, Telugu, and more
Zero Cost — no API keys, no subscriptions
Cloud Ready — deploy to Render, Railway, AWS, Google Cloud, HF Spaces
Emotion Support — cheerful, sad, angry, whispering, and more
Streaming — real-time audio streaming via WebSocket
Auto-Select — automatically picks best engine for any language
Quick Start
bash
# 1. Clone
git clone https://github.com/jp200883-sudo/singhji-voice-agent.git
cd singhji-voice-agent

# 2. Install
pip install -r requirements.txt

# 3. Run API
uvicorn app:app --host 0.0.0.0 --port 8000

# 4. Test
python test_tts.py
Voice Engines
1. Edge TTS (200+ Voices)
Microsoft Edge TTS — no API key needed
Table
Language	Best Voice	Gender
Hindi	hi-IN-MadhurNeural	Male
Hinglish	en-IN-PrabhatNeural	Male
English (US)	en-US-AvaMultilingualNeural	Female
English (UK)	en-GB-SoniaNeural	Female
Tamil	ta-IN-PallaviNeural	Female
Telugu	te-IN-ShrutiNeural	Female
+ 40 more languages		
2. Kokoro TTS (50+ Voices)
82M parameters, MOS 4.2, Apache 2.0, CPU optimized
Table
Language	Best Voice	Gender
English (US)	af_bella	Female
English (UK)	bf_emma	Female
Hindi/Hinglish	hf_alpha	Female
Spanish	ef_dora	Female
+ 10 more languages		
3. Piper TTS (30+ Voices)
ONNX-based, edge-device optimized
Table
Language	Best Voice	Size
English (US)	en_US-lessac-medium	60 MB
Hindi	hi_IN-clone-medium	60 MB
Spanish	es_ES-claude-high	110 MB
+ 20 more languages		
API Endpoints
Table
Endpoint	Method	Description
/	GET	API info
/health	GET	Health check
/voices	GET	List all voices
/voices/best	GET	Best voice per language
/speak	GET	Synthesize to audio file
/speak/stream	GET	Stream audio in real-time
/engines	GET	List TTS engines
/languages	GET	List supported languages
Example API Call:
bash
curl "http://localhost:8000/speak?text=नमस्ते&language=hindi&format=json"
Response:
JSON
{
  "success": true,
  "audio_path": "/tmp/edge_tts_hi_IN_MadhurNeural.mp3",
  "engine": "edge",
  "voice": "hi-IN-MadhurNeural"
}
File Structure
plain
singhji-voice-agent/
├── app.py                          # FastAPI server
├── requirements.txt                # Dependencies
├── test_tts.py                     # Test suite
├── .env.example                    # Environment template
├── src/
│   ├── tts_engines/
│   │   ├── __init__.py
│   │   ├── edge_tts_manager.py   # 200+ Edge voices
│   │   ├── kokoro_tts_manager.py # 50+ Kokoro voices
│   │   ├── piper_tts_manager.py  # 30+ Piper voices
│   │   └── unified_tts_manager.py # Auto-select engine
│   ├── stt_engines/              # (Future: STT modules)
│   └── utils/                    # (Future: utilities)
├── tests/                        # Unit tests
├── docs/
│   └── CLOUD_DEPLOY.md           # Deploy guide
└── scripts/                      # Helper scripts
Deploy to Cloud
See docs/CLOUD_DEPLOY.md for detailed guides on:
Render — Free, always on
Railway — $5/mo credit
AWS EC2 — 750 hrs/mo free tier
Google Cloud Run — 2M requests/mo free
Hugging Face Spaces — Unlimited public
One-click deploy:
https://render.com/deploy
One-Liner Usage
Python
from src.tts_engines import speak

# Just speak!
audio_path = speak("नमस्ते दोस्तों!", language="hindi")
print(f"Audio saved: {audio_path}")
License
MIT License — 100% free forever
Made with by Singh Ji AI
