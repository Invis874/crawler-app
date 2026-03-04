from typing import Optional, List, Dict, Any
from app.db import db

class PageRepository:
    """Все запросы к БД в одном месте"""
    
    @staticmethod
    async def create(page_data: Dict[str, Any]) -> str:
        """Создать новую страницу"""
        query = """
            INSERT INTO pages (
                url, title, html_content, crawl_depth, 
                http_status_code, parent_task_id
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (url) DO UPDATE SET
                title = EXCLUDED.title,
                html_content = EXCLUDED.html_content,
                crawl_depth = LEAST(pages.crawl_depth, EXCLUDED.crawl_depth),
                http_status_code = EXCLUDED.http_status_code,
                updated_at = NOW()
            RETURNING id
        """
        
        async with db.connection.acquire() as conn:
            page_id = await conn.fetchval(
                query,
                page_data['url'],
                page_data.get('title'),
                page_data['html_content'],
                page_data['crawl_depth'],
                page_data.get('http_status_code'),
                page_data.get('parent_task_id')
            )
            return str(page_id)
    
    @staticmethod
    async def get_by_url(url: str) -> Optional[Dict[str, Any]]:
        """Получить страницу по URL"""
        query = """
            SELECT
                id::text,           -- <-- явно преобразуем в текст
                url, 
                title, 
                html_content, 
                crawl_depth,
                http_status_code, 
                created_at, 
                updated_at
            FROM pages
            WHERE url = $1
        """
        
        async with db.connection.acquire() as conn:
            row = await conn.fetchrow(query, url)
            return dict(row) if row else None
    
    @staticmethod
    async def search(term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Поиск по URL и заголовку"""
        query = """
            SELECT id::text, url, title, created_at
            FROM pages
            WHERE url ILIKE $1 OR title ILIKE $1
            ORDER BY 
                CASE 
                    WHEN url ILIKE $2 THEN 1
                    WHEN title ILIKE $2 THEN 2
                    ELSE 3
                END,
                created_at DESC
            LIMIT $3
        """
        search_pattern = f"%{term}%"
        exact_start = f"{term}%"
        
        async with db.connection.acquire() as conn:
            rows = await conn.fetch(query, search_pattern, exact_start, limit)
            return [dict(row) for row in rows]
    
    @staticmethod
    async def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Список всех страниц"""
        query = """
            SELECT id::text, url, title, created_at
            FROM pages
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        
        async with db.connection.acquire() as conn:
            rows = await conn.fetch(query, limit, offset)
            return [dict(row) for row in rows]
    
    @staticmethod
    async def exists(url: str) -> bool:
        """Проверить существование URL"""
        query = "SELECT EXISTS(SELECT 1 FROM pages WHERE url = $1)"
        async with db.connection.acquire() as conn:
            return await conn.fetchval(query, url)