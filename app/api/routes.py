from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
import uuid
import json

from app.models.page import (
    CrawlRequest, PageResponse, PageListItem, 
    CrawlTask
)
from app.repositories.page_repo import PageRepository
from app.rabbitmq import rabbitmq
from app.redis_client import redis_client
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["crawler"])

@router.post("/crawl", status_code=202)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks
):
    """
    Запустить обход страницы
    - **url**: начальная страница
    - **max_depth**: максимальная глубина (0 - только эта страница)
    - **max_concurrent**: максимум одновременных загрузок
    """
    # Создаем начальную задачу
    task = CrawlTask(
        url=str(request.url),
        current_depth=0,
        max_depth=request.max_depth,
        max_concurrent=request.max_concurrent
    )
    
    # Отправляем в очередь
    await rabbitmq.publish_task(task.dict())
    
    return {
        "status": "accepted",
        "message": "Crawl task queued",
        "task": task.dict()
    }

@router.get("/pages/search", response_model=List[PageListItem])
async def search_pages(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Поиск страниц по URL и заголовку"""
    results = await PageRepository.search(q, limit)
    return results

@router.get("/pages", response_model=List[PageListItem])
async def list_pages(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Список всех страниц"""
    return await PageRepository.list_all(limit, offset)

@router.get("/pages/{url:path}", response_model=PageResponse)
async def get_page(url: str):
    """Получить страницу по URL (с телом HTML)"""
    # Сначала проверяем кэш
    cached = await redis_client.get_page(url)
    if cached:
        # В кэше только HTML, нужно получить остальное из БД
        page = await PageRepository.get_by_url(url)
        if page:
            page['html_content'] = cached
            return page
    
    # Если нет в кэше - идем в БД
    page = await PageRepository.get_by_url(url)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Сохраняем HTML в кэш для следующих запросов
    if page.get('html_content'):
        await redis_client.set_page(url, page['html_content'])
    
    return page

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "ok",
        "services": {
            "postgres": "connected" if rabbitmq.connection else "disconnected",  # TODO: добавить реальную проверку PG
            "redis": "connected" if redis_client.client else "disconnected",
            "rabbitmq": "connected" if rabbitmq.connection else "disconnected"
        }
    }