from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.api import routes           # Импортируем эндпоинты
from app.db import db                # Подключение к БД
from app.redis_client import redis_client
from app.rabbitmq import rabbitmq
from app.config import settings
from app.crawler.worker import start_worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Web Crawler API",
    description="Асинхронный краулер с обходом страниц",
    version="1.0.0",
    docs_url="/swagger",  # Swagger UI
    redoc_url="/redoc"     # ReDoc
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(routes.router)

@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    logger.info("Starting up...")
    
    # Подключаемся к БД
    await db.connect()
    # Подключаемся к Redis
    await redis_client.connect()
    # Подключаемся к RabbitMQ
    await rabbitmq.connect()
    # Запускаем воркер в фоне
    asyncio.create_task(start_worker())
    
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    """Очистка при остановке"""
    logger.info("Shutting down...")
    
    # Закрываем соединения
    await db.disconnect()
    await redis_client.disconnect()
    await rabbitmq.disconnect()
    
    logger.info("Shutdown complete")