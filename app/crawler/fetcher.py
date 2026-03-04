import aiohttp
from typing import Optional, Tuple
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class PageFetcher:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': settings.user_agent},
            timeout=aiohttp.ClientTimeout(total=settings.request_timeout)
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        Загрузить страницу.
        Возвращает: (html, status_code, error_message)
        """
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    return html, response.status, None
                else:
                    return None, response.status, f"HTTP {response.status}"
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching {url}: {e}")
            return None, None, str(e)
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None, None, str(e)