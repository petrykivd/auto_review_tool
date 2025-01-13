from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class AIServiceSettings(BaseSettings):
    API_KEY: str
    MODEL: str = "gpt-4-turbo"

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_ai_service_settings() -> AIServiceSettings:
    return AIServiceSettings()
