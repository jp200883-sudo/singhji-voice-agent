from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    GROQ_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
