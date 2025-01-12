from pydantic_settings import BaseSettings
from functools import lru_cache


class AIServiceSettings(BaseSettings):
    API_KEY: str
    MODEL: str = "gpt-4-turbo"

    class Config:
        env_prefix = "OPENAI_"
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_ai_service_settings() -> AIServiceSettings:
    return AIServiceSettings()
