from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class HTMLParser:
    @staticmethod
    def extract_title(html: str) -> Optional[str]:
        """Извлечь title из HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            title_tag = soup.find('title')
            return title_tag.string.strip() if title_tag and title_tag.string else None
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return None
    
    @staticmethod
    def extract_links(html: str, base_url: str) -> Set[str]:
        """Извлечь все ссылки из HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            links = set()
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].strip()
                
                # Пропускаем пустые, якоря, javascript
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                # Пропускаем mailto, tel и т.д.
                if href.startswith(('mailto:', 'tel:', 'ftp:')):
                    continue
                
                try:
                    # Преобразуем относительные ссылки в абсолютные
                    full_url = urljoin(base_url, href)
                    
                    # Убираем якоря
                    full_url = urlparse(full_url)._replace(fragment='').geturl()
                    
                    # Проверяем, что это http/https
                    if full_url.startswith(('http://', 'https://')):
                        links.add(full_url)
                        
                except Exception as e:
                    logger.debug(f"Error parsing URL {href}: {e}")
                    continue
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return set()