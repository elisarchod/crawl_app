import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from requests import Response
from bs4 import BeautifulSoup, Tag

from ..database.url_db_manager import WebCrawlDatabaseManager
from ..utils.log_handler import logger
from .models import WebScrapingConfig, ExtractedLink, CrawledPageData


class UrlValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
            
        parsed_url_components = urlparse(url)
        return all([parsed_url_components.scheme, parsed_url_components.netloc])


class WebpageDownloader:
    def __init__(self, config: WebScrapingConfig):
        self._config = config
    
    def download_and_parse_webpage(self, url: str) -> Optional[BeautifulSoup]:
        try:
            http_response: Response = requests.get(
                url, 
                timeout=self._config.http_request_timeout_seconds
            )
            http_response.raise_for_status()
            return BeautifulSoup(http_response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Failed to download webpage from {url}: {str(e)}")
            return None


class HtmlContentExtractor:
    def __init__(self, config: WebScrapingConfig):
        self._config = config
        self._url_validator = UrlValidator()
    
    def extract_page_title(self, parsed_html_document: BeautifulSoup) -> str:
        if parsed_html_document.title and parsed_html_document.title.string:
            return parsed_html_document.title.string.strip()
        return 'No title'
    
    def extract_link_from_anchor_tag(self, anchor_tag: Tag, base_url: str) -> Optional[ExtractedLink]:
        anchor_href_attribute = anchor_tag.get('href')
        if not anchor_href_attribute:
            return None
            
        absolute_link_url = urljoin(base_url, anchor_href_attribute)
        if not self._url_validator.is_valid_url(absolute_link_url):
            return None
            
        visible_anchor_text = anchor_tag.get_text(strip=True) or 'No text'
        parent_element_context = self._extract_surrounding_content(anchor_tag)
        
        return ExtractedLink(
            url=absolute_link_url,
            anchor_text=visible_anchor_text,
            surrounding_content=parent_element_context
        )
    
    def _extract_surrounding_content(self, anchor_tag: Tag) -> str:
        if anchor_tag.parent:
            parent_text_content = anchor_tag.parent.get_text(strip=True)
            return parent_text_content[:self._config.content_excerpt_size]
        return 'No content'
    
    def extract_all_links_from_page(self, parsed_html_document: BeautifulSoup, base_url: str) -> List[ExtractedLink]:
        extracted_links = []
        for anchor_tag in parsed_html_document.find_all('a', href=True):
            extracted_link = self.extract_link_from_anchor_tag(anchor_tag, base_url)
            if extracted_link:
                extracted_links.append(extracted_link)
        return extracted_links
    
    def parse_complete_webpage(self, parsed_html_document: BeautifulSoup, current_url: str, referring_url: Optional[str], crawl_depth: int) -> CrawledPageData:
        page_title = self.extract_page_title(parsed_html_document)
        extracted_links = self.extract_all_links_from_page(parsed_html_document, current_url)
        
        return CrawledPageData(
            url=current_url,
            source_url=referring_url,
            crawl_depth=crawl_depth,
            page_title=page_title,
            extracted_links=extracted_links
        )


class RecursiveWebCrawler:
    def __init__(self, config: WebScrapingConfig, database_manager: WebCrawlDatabaseManager):
        self._config = config
        self._database_manager = database_manager
        self._webpage_downloader = WebpageDownloader(config)
        self._html_content_extractor = HtmlContentExtractor(config)
        self._total_pages_crawled = 0
    
    def should_continue_crawling_url(self, url: str, current_depth: int, maximum_crawl_depth: int) -> bool:
        return (
            current_depth <= maximum_crawl_depth
            and not self._database_manager.is_url_already_visited(url)
            and self._total_pages_crawled < self._config.max_urls_to_crawl
        )
    
    def crawl_and_store_single_page(self, url: str, referring_url: Optional[str], crawl_depth: int) -> Optional[CrawledPageData]:
        parsed_html_document = self._webpage_downloader.download_and_parse_webpage(url)
        if not parsed_html_document:
            return None
        
        crawled_page_data = self._html_content_extractor.parse_complete_webpage(parsed_html_document, url, referring_url, crawl_depth)
        
        self._database_manager.store_crawled_page_data(crawled_page_data)
        
        return crawled_page_data
    
    def crawl_website_recursively(self, url: str, referring_url: Optional[str], current_depth: int, maximum_crawl_depth: int) -> None:
        if not self.should_continue_crawling_url(url, current_depth, maximum_crawl_depth):
            return
         
        self._database_manager.mark_url_as_visited(url)
        self._total_pages_crawled += 1
        
        logger.info(
            f"Crawling webpage: {url} (depth: {current_depth}, "
            f"pages crawled: {self._total_pages_crawled}/{self._config.max_urls_to_crawl})"
        )
        
        time.sleep(self._config.request_delay_seconds)
        
        crawled_page_data = self.crawl_and_store_single_page(url, referring_url, current_depth)
        if not crawled_page_data:
            return
        
        for extracted_link in crawled_page_data.extracted_links:
            self.crawl_website_recursively(extracted_link.url, url, current_depth + 1, maximum_crawl_depth)
    
    @property
    def total_pages_crawled_count(self) -> int:
        return self._total_pages_crawled


class WebSiteCrawler:
    def __init__(self, starting_url: str, maximum_crawl_depth: int, config: Optional[WebScrapingConfig] = None):
        if not UrlValidator.is_valid_url(starting_url):
            raise ValueError(f"Invalid starting URL provided: {starting_url}")
        
        logger.info(f"Initializing website crawler for: {starting_url}")
        
        self._starting_url = starting_url
        self._maximum_crawl_depth = maximum_crawl_depth
        self._crawling_config = config or WebScrapingConfig()
        self._database_manager = WebCrawlDatabaseManager()
        self._recursive_crawler = RecursiveWebCrawler(self._crawling_config, self._database_manager)
    
    def start_website_crawling(self) -> None:
        try:
            logger.info(f"Starting website crawl from {self._starting_url} with maximum depth {self._maximum_crawl_depth}")
            self._recursive_crawler.crawl_website_recursively(
                self._starting_url, 
                None, 
                0, 
                self._maximum_crawl_depth
            )
            logger.info(f"Website crawling completed. Total pages crawled: {self._recursive_crawler.total_pages_crawled_count}")
        except Exception as e:
            logger.error(f"Website crawling failed with error: {str(e)}")
            raise
        finally:
            self._cleanup_database_resources()
    
    def _cleanup_database_resources(self) -> None:
        try:
            self._database_manager.close_database_connection()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error during database cleanup: {str(e)}")
    
    @property
    def total_pages_crawled_count(self) -> int:
        return self._recursive_crawler.total_pages_crawled_count

