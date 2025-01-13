from typing import Optional, Any
import redis.asyncio as redis
from loguru import logger

from src.services.cache.config import get_redis_settings

settings = get_redis_settings()


class RedisService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.ttl = settings.REDIS_TTL

    async def get(self, key: str) -> Optional[str]:
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return value
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        try:
            await self.redis.set(key, value, ex=ttl or self.ttl)
            logger.debug(f"Cached value for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            logger.debug(f"Deleted cache for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

    @staticmethod
    def generate_key(prefix: str, **kwargs) -> str:
        sorted_params = sorted(kwargs.items())
        params_str = '_'.join(f"{k}:{v}" for k, v in sorted_params)
        return f"{prefix}:{params_str}"


def get_redis_service() -> RedisService:
    return RedisService()
