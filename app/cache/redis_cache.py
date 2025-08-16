from redis import Redis
from fastapi import Depends
from app.core.config import config

class RedisCache:
    def __init__(self):
        self.client = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )

    def set(self, key: str, value: str, expire: int = 3600):
        self.client.set(key, value, ex=expire)

    def get(self, key: str) -> str:
        return self.client.get(key)

    def delete(self, key: str):
        self.client.delete(key)

redis_cache = RedisCache()