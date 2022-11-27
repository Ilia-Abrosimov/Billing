from redis import Redis

from src.core.config import redis_settings


class RedisCacheService:
    """Сервис кэширования"""

    def __init__(self, redis_conn: Redis):
        self.redis = redis_conn

    def get(self, key: str) -> str:
        return self.redis.get(key)

    def set(self, name: str, value: str, time: int) -> None:
        """Добавляет данные в Рэдис"""
        self.redis.setex(name, time, value)
        return None

    def delete(self, key: str) -> None:
        self.redis.delete(key)


redis_conn = Redis(
    host=redis_settings.redis_host,
    port=redis_settings.redis_port,
)

redis_service = RedisCacheService(redis_conn)
