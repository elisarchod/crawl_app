"""
Modern tests for models and main module.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from urlevaluator.src.scraper.models import WebScrapingConfig, ExtractedLink, CrawledPageData

def test_web_scraping_config_defaults_and_custom():
    # Defaults
    default = WebScrapingConfig()
    assert default.max_urls_to_crawl == 32
    assert default.http_request_timeout_seconds == 10
    assert default.request_delay_seconds == 1.0
    assert default.content_excerpt_size == 200

    # Custom
    custom = WebScrapingConfig(
        max_urls_to_crawl=5,
        http_request_timeout_seconds=2,
        request_delay_seconds=0.5,
        content_excerpt_size=50
    )
    assert custom.max_urls_to_crawl == 5
    assert custom.http_request_timeout_seconds == 2
    assert custom.request_delay_seconds == 0.5
    assert custom.content_excerpt_size == 50

def test_extracted_link_creation():
    link = ExtractedLink(
        url="https://example.com/page",
        anchor_text="Example Page",
        surrounding_content="This is an example page with useful content."
    )
    assert link.url == "https://example.com/page"
    assert link.anchor_text == "Example Page"
    assert link.surrounding_content == "This is an example page with useful content."

def test_crawled_page_data_creation():
    extracted_links = [
        ExtractedLink(url="https://example.com/link1", anchor_text="Link 1", surrounding_content="Content 1"),
        ExtractedLink(url="https://example.com/link2", anchor_text="Link 2", surrounding_content="Content 2")
    ]
    page_data = CrawledPageData(
        url="https://example.com",
        source_url="https://referring.com",
        crawl_depth=1,
        page_title="Test Page",
        extracted_links=extracted_links
    )
    assert page_data.url == "https://example.com"
    assert page_data.source_url == "https://referring.com"
    assert page_data.crawl_depth == 1
    assert page_data.page_title == "Test Page"
    assert page_data.extracted_links == extracted_links 