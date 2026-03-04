# Async Web Crawler

Асинхронный веб-краулер с API на FastAPI, очередями RabbitMQ, кэшированием Redis и PostgreSQL.

## 🚀 Технологии

- Python 3.11 + asyncio
- FastAPI + Swagger UI
- PostgreSQL + asyncpg (чистый SQL)
- Redis (кэширование HTML)
- RabbitMQ (очереди задач)
- Docker + docker-compose
- aiohttp (асинхронный HTTP клиент)

## 📋 Функциональность

- Обход страниц с заданной глубиной (0 - только указанная страница, N - рекурсивно)
- Контроль параллельности (max_concurrent)
- Сохранение HTML, заголовка, URL
- Поиск по заголовкам и URL
- Кэширование HTML в Redis
- Асинхронная обработка через RabbitMQ

## 🛠️ Запуск

- Создать файл `.env` пример `cp .env.example .env`
- Запустить через docker-compose: `docker-compose up --build`
- Открыть Swagger UI: http://localhost:8000/swagger
