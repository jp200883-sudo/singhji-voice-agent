import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from routers import voice_ws, telegram_webhook

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("singhji-voice-agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup और Shutdown Lifecycle Events
    """
    logger.info("🚀 Starting singhji-voice-agent core engine...")
    # Cloud/API connections warm-up logic
    yield
    logger.info("🛑 Shutting down singhji-voice-agent gracefully...")


app = FastAPI(
    title="SinghJi Voice Agent Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Mount
app.include_router(voice_ws.router, prefix="/voice", tags=["Live Voice Stream"])
app.include_router(telegram_webhook.router, prefix="/telegram", tags=["Telegram Webhook"])


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "singhji-voice-agent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main.py:app",
        host="0.0.0.0",
        port=settings.PORT if hasattr(settings, "PORT") else 8000,
        reload=True
    )
