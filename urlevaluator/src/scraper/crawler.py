import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from requests import Response
from bs4 import BeautifulSoup

from urlevaluator.src.database.url_db_manager import CrawlerDataManager
from urlevaluator.src.utils.log_handler import logger
from urlevaluator.src.scraper.link_models import Link

REQUEST_DELAY = 1.0
MAX_URLS = 32
LIMIT_CONTENT = 1000

class WebScraper:
    def __init__(self, initial_url: str, max_depth: int):
        self.initial_url = initial_url
        self.max_depth = max_depth
        self.urls_scraped = 0
        self.db = CrawlerDataManager()

    def is_valid_url(self, url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response: Response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Link]:
        return [
            Link(
                url=urljoin(base_url, a['href']),
                text=a.get_text(strip=True) or 'No text',
                content=(a.parent.get_text(strip=True)[:LIMIT_CONTENT] if a.parent else 'No content')
            )
            for a in soup.find_all('a', href=True)
            if self.is_valid_url(urljoin(base_url, a['href']))
        ]

    def scrape(self, url: str, source_url: str = None, depth: int = 0) -> None:
        if depth > self.max_depth or self.db.is_url_visited(url) or self.urls_scraped >= MAX_URLS:
            return

        self.urls_scraped += 1
        self.db.mark_url_visited(url)
        logger.info(f"Scraping {url} (depth: {depth}, urls scraped: {self.urls_scraped}/{MAX_URLS})")
        time.sleep(REQUEST_DELAY)
        soup: BeautifulSoup = self.get_page_content(url)
        if not soup:
            return

        title: str = soup.title.string if soup.title else 'No title'
        links: List[Link] = self.extract_links(soup, url)
        
        self.db.save_page_data(url, source_url, depth, title, links)

        for link in links:
            self.scrape(link.url, url, depth + 1)

    def start_scraping(self) -> None:
        try:
            self.scrape(self.initial_url)
        finally:
            self.db.close()

