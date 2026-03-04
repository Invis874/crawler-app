from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "Crawler App"
    debug: bool = False
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "crawler"
    db_password: str = "secret"
    db_name: str = "crawler"
    
    # Redis
    redis_host: str = "rabbitmq"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600  # 1 час
    
    # RabbitMQ
    rabbit_host: str = "localhost"
    rabbit_port: int = 5672
    rabbit_user: str = "crawler"
    rabbit_password: str = "secret"
    crawl_queue: str = "crawl_tasks"
    
    # Crawler
    default_max_depth: int = 2
    default_max_concurrent: int = 5
    request_timeout: int = 10
    user_agent: str = "Mozilla/5.0 (compatible; CrawlerBot/1.0)"
    
    class Config:
        env_file = ".env"

settings = Settings()