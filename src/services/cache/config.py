from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class RedisCacheServiceSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_TTL: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache()
def get_redis_settings() -> RedisCacheServiceSettings:
    return RedisCacheServiceSettings()
