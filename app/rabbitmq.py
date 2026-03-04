import json
import aio_pika
from typing import Optional
from app.config import settings

class RabbitMQ:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        self.connection = await aio_pika.connect_robust(
            host=settings.rabbit_host,
            port=settings.rabbit_port,
            login=settings.rabbit_user,
            password=settings.rabbit_password,
        )
        self.channel = await self.connection.channel()
        
        # Декларируем очередь (создаст если нет)
        self.queue = await self.channel.declare_queue(
            settings.crawl_queue,
            durable=True,  # Очередь сохранится после рестарта
            arguments={
                'x-max-length': 10000,  # Правильный способ
                'x-overflow': 'drop-head'  # или 'reject-publish'
            }
        )
        print("✅ Подключен к RabbitMQ")
    
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            print("✅ Отключен от RabbitMQ")
    
    async def publish_task(self, task_data: dict):
        """Отправить задачу в очередь"""
        message = aio_pika.Message(
            body=json.dumps(task_data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(
            message,
            routing_key=settings.crawl_queue
        )

rabbitmq = RabbitMQ()