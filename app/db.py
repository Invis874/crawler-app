import asyncpg
from typing import Optional
from app.config import settings
import asyncio

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Инициализация пула соединений"""
        self.pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            min_size=5,
            max_size=20,
        )
        print("✅ Connected to PostgreSQL")
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("✅ Disconnected from PostgreSQL")
    
    @property
    def connection(self) -> asyncpg.Pool:
        if not self.pool:
            raise RuntimeError("Database not initialized")
        return self.pool

db = Database()