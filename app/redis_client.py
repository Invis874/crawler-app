import redis.asyncio as redis
from typing import Optional
from app.config import settings

class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        self.client = await redis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
            decode_responses=True
        )
        await self.client.ping()
        print("✅ Connected to Redis")
    
    async def disconnect(self):
        if self.client:
            await self.client.close()
            print("✅ Disconnected from Redis")
    
    async def get_page(self, url: str) -> Optional[str]:
        """Получить HTML страницы из кэша"""
        return await self.client.get(f"page:{url}")
    
    async def set_page(self, url: str, html: str):
        """Сохранить HTML страницы в кэш"""
        await self.client.setex(f"page:{url}", settings.cache_ttl, html)

redis_client = RedisClient()