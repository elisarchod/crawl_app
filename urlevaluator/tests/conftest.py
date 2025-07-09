"""Pytest configuration and common fixtures.

This module provides common fixtures and configuration for the test suite,
following clean code principles and best practices.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, List
import tempfile
import os

from urlevaluator.src.scraper.models import WebScrapingConfig, ExtractedLink, CrawledPageData


@pytest.fixture
def sample_web_scraping_config() -> WebScrapingConfig:
    """Provide a sample web scraping configuration for tests."""
    return WebScrapingConfig(
        max_urls_to_crawl=10,
        http_request_timeout_seconds=5,
        request_delay_seconds=1.0,
        content_excerpt_size=200
    )


@pytest.fixture
def sample_extracted_links() -> List[ExtractedLink]:
    """Provide sample extracted links for testing."""
    return [
        ExtractedLink(
            url="https://example.com/tech-article",
            anchor_text="Technology Article",
            surrounding_content="This article discusses the latest advances in artificial intelligence and machine learning."
        ),
        ExtractedLink(
            url="https://example.com/sports-news",
            anchor_text="Sports News",
            surrounding_content="Coverage of the latest sports events and player performances."
        ),
        ExtractedLink(
            url="https://example.com/politics-update",
            anchor_text="Political Update",
            surrounding_content="Analysis of recent political developments and policy changes."
        )
    ]


@pytest.fixture
def sample_crawled_page_data(sample_extracted_links: List[ExtractedLink]) -> CrawledPageData:
    """Provide sample crawled page data for testing."""
    return CrawledPageData(
        url="https://example.com/homepage",
        source_url=None,
        crawl_depth=0,
        page_title="Example Homepage - News and Articles",
        extracted_links=sample_extracted_links
    )


@pytest.fixture
def mock_database_connection():
    """Provide a mock database connection for testing."""
    mock_conn = Mock()
    mock_conn.execute.return_value = Mock()
    mock_conn.execute.return_value.fetchone.return_value = [1]
    mock_conn.execute.return_value.fetchall.return_value = []
    mock_conn.close.return_value = None
    return mock_conn


@pytest.fixture
def mock_topic_scores() -> Dict[str, float]:
    """Provide mock topic classification scores for testing."""
    return {
        "technology": 0.45,
        "sports": 0.20,
        "politics": 0.15,
        "entertainment": 0.10,
        "science": 0.10
    }


@pytest.fixture
def temp_database_path():
    """Provide a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_path = temp_file.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def sample_html_content() -> str:
    """Provide sample HTML content for testing web scraping."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page Title</title>
    </head>
    <body>
        <h1>Welcome to Test Page</h1>
        <p>This is a test page with several links:</p>
        <div>
            <a href="/page1">First Page</a>
            <p>This is the first page link with some context.</p>
        </div>
        <div>
            <a href="/page2">Second Page</a>
            <p>This is the second page link with different context.</p>
        </div>
        <div>
            <a href="https://external.com">External Link</a>
            <p>This is an external link for testing.</p>
        </div>
        <div>
            <a>Link without href</a>
            <p>This link should be ignored.</p>
        </div>
    </body>
    </html>
    '''


@pytest.fixture
def sample_classification_batch() -> List[tuple]:
    """Provide sample classification batch data for testing."""
    return [
        (1, "This is content about artificial intelligence and machine learning technology."),
        (2, "Sports news about the latest football match results and player transfers."),
        (3, "Political analysis of recent election results and policy implications."),
        (4, "Entertainment news covering movie releases and celebrity updates."),
        (5, "Scientific research findings about climate change and environmental impact.")
    ]


@pytest.fixture
def mock_requests_response():
    """Provide a mock requests response for testing HTTP operations."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '<html><head><title>Mock Page</title></head><body><p>Mock content</p></body></html>'
    mock_response.raise_for_status.return_value = None
    return mock_response


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    # Add unit marker to all tests by default
    for item in items:
        if "integration" not in [marker.name for marker in item.iter_markers()]:
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that typically take longer
        if any(keyword in item.name.lower() for keyword in ["crawl", "download", "batch"]):
            item.add_marker(pytest.mark.slow) 