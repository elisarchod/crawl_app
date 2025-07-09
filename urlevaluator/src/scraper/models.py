from typing import List, Optional
from dataclasses import dataclass


@dataclass
class WebScrapingConfig:
    request_delay_seconds: float = 1.0
    max_urls_to_crawl: int = 32
    content_excerpt_size: int = 200
    http_request_timeout_seconds: int = 10


@dataclass
class ExtractedLink:
    url: str
    anchor_text: str
    surrounding_content: str


@dataclass
class CrawledPageData:
    url: str
    source_url: Optional[str]
    crawl_depth: int
    page_title: str
    extracted_links: List[ExtractedLink] 