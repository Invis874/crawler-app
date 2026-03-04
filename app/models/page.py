from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class PageBase(BaseModel):
    url: str
    title: Optional[str] = None
    http_status_code: Optional[int] = None

class PageCreate(PageBase):
    html_content: str
    crawl_depth: int = 0
    parent_task_id: Optional[str] = None

class PageResponse(PageBase):
    id: str
    html_content: Optional[str]  # Может быть null при запросе списка
    crawl_depth: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class PageListItem(BaseModel):
    id: str
    url: str
    title: Optional[str]
    created_at: datetime

class CrawlRequest(BaseModel):
    url: HttpUrl
    max_depth: int = Field(default=1, ge=0, le=5)
    max_concurrent: int = Field(default=3, ge=1, le=10)

class CrawlTask(BaseModel):
    url: str
    current_depth: int
    max_depth: int
    max_concurrent: int = 3
    parent_task_id: Optional[str] = None