import asyncio
import json
import logging
from typing import Optional
from app.rabbitmq import rabbitmq
from app.repositories.page_repo import PageRepository
from app.crawler.fetcher import PageFetcher
from app.crawler.parser import HTMLParser
from app.models.page import CrawlTask
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlerWorker:
    def __init__(self):
        self.parser = HTMLParser()
        self.semaphores = {}
    
    async def process_task(self, task_data: dict):
        """Обработать одну задачу на обход"""
        task = CrawlTask(**task_data)

        # Создаем семафор с нужным ограничением
        if task.max_concurrent not in self.semaphores:
            self.semaphores[task.max_concurrent] = asyncio.Semaphore(task.max_concurrent)

        semaphore = self.semaphores[task.max_concurrent]
        
        async with semaphore:
            logger.info(f"Обработка {task.url} (глубина {task.current_depth}/{task.max_depth}) "
                       f"с ограничением {task.max_concurrent}")
        
            # Загружаем страницу
            async with PageFetcher() as fetcher:
                html, status_code, error = await fetcher.fetch(task.url)
            
            if error or not html:
                logger.error(f"Не удалось получить {task.url}: {error}")
                return
            
            # Парсим заголовок
            title = self.parser.extract_title(html)
            
            # Сохраняем в БД
            page_data = {
                'url': task.url,
                'title': title,
                'html_content': html,
                'crawl_depth': task.current_depth,
                'http_status_code': status_code,
                'parent_task_id': task.parent_task_id
            }
            
            try:
                page_id = await PageRepository.create(page_data)
                logger.info(f"Saved {task.url} as {page_id}")
            except Exception as e:
                logger.error(f"Не удалось сохранить {task.url}: {e}")
                return
            
            # Если нужно обходить дальше
            if task.current_depth < task.max_depth:
                links = self.parser.extract_links(html, task.url)
                logger.info(f"Found {len(links)} links on {task.url}")
                
                # Создаем новые задачи для каждой ссылки
                for link in links:
                    # Проверяем, не обходили ли уже
                    exists = await PageRepository.exists(link)
                    if exists:
                        logger.debug(f"Skip {link} - уже есть")
                        continue
                    
                    new_task = CrawlTask(
                        url=link,
                        current_depth=task.current_depth + 1,
                        max_depth=task.max_depth,
                        max_concurrent=task.max_concurrent,
                        parent_task_id=page_id
                    )
                    
                    # Отправляем в очередь
                    await rabbitmq.publish_task(new_task.dict())
                    logger.debug(f"Поставленый в очередь {link}")
    
    async def run(self):
        """Запуск воркера"""
        logger.info("Starting crawler worker")
        
        # Слушаем очередь
        async with rabbitmq.queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    task_data = json.loads(message.body.decode())
                    await self.process_task(task_data)
                    await message.ack()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    await message.reject(requeue=False)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    # Не делаем ack, чтобы сообщение вернулось в очередь
                    await message.reject(requeue=True)

async def start_worker():
    """Функция для запуска воркера из main.py"""
    worker = CrawlerWorker()
    await worker.run()