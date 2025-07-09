"""
Modern tests for the crawler module.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError
from urlevaluator.src.scraper.crawler import (
    UrlValidator,
    WebpageDownloader,
    HtmlContentExtractor,
)
from urlevaluator.src.scraper.models import WebScrapingConfig

class TestUrlValidator:
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com", True),
        ("http://test.org", True),
        ("ftp://example.com", True),  # FTP URLs are actually valid in the implementation
        ("not-a-url", False),
        ("", False),
        (None, False),
        (123, False),
    ])
    def test_url_validation(self, url, expected):
        assert UrlValidator.is_valid_url(url) == expected

class TestWebpageDownloader:
    def setup_method(self):
        self.config = WebScrapingConfig()
        self.downloader = WebpageDownloader(self.config)

    @patch('urlevaluator.src.scraper.crawler.requests.get')
    def test_successful_download(self, mock_get):
        html_content = "<html><head><title>Test</title></head><body>Content</body></html>"
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = self.downloader.download_and_parse_webpage("https://example.com")
        assert result is not None
        assert isinstance(result, BeautifulSoup)
        assert result.title.string == "Test"

    @patch('urlevaluator.src.scraper.crawler.requests.get')
    def test_http_error_handling(self, mock_get):
        mock_get.side_effect = HTTPError("404 Not Found")
        result = self.downloader.download_and_parse_webpage("https://example.com")
        assert result is None

    @patch('urlevaluator.src.scraper.crawler.requests.get')
    def test_timeout_handling(self, mock_get):
        mock_get.side_effect = Timeout("Request timed out")
        result = self.downloader.download_and_parse_webpage("https://example.com")
        assert result is None

    @patch('urlevaluator.src.scraper.crawler.requests.get')
    def test_general_request_exception(self, mock_get):
        mock_get.side_effect = RequestException("Connection error")
        result = self.downloader.download_and_parse_webpage("https://example.com")
        assert result is None

class TestHtmlContentExtractor:
    def setup_method(self):
        self.config = WebScrapingConfig()
        self.extractor = HtmlContentExtractor(self.config)

    def test_extract_page_title_with_title_tag(self):
        html = "<html><head><title>Test Page Title</title></head></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = self.extractor.extract_page_title(soup)
        assert title == "Test Page Title"

    def test_extract_page_title_no_title_tag(self):
        html = "<html><head></head><body>Content</body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = self.extractor.extract_page_title(soup)
        assert title == "No title"

    def test_extract_link_from_anchor_tag_valid(self):
        html = '<a href="/path/to/page">Link Text</a>'
        soup = BeautifulSoup(html, 'html.parser')
        anchor_tag = soup.find('a')
        base_url = "https://example.com"
        link = self.extractor.extract_link_from_anchor_tag(anchor_tag, base_url)
        assert link is not None
        assert link.url == "https://example.com/path/to/page"
        assert link.anchor_text == "Link Text"

    def test_extract_link_from_anchor_tag_no_href(self):
        html = '<a>Link Text</a>'
        soup = BeautifulSoup(html, 'html.parser')
        anchor_tag = soup.find('a')
        link = self.extractor.extract_link_from_anchor_tag(anchor_tag, "https://example.com")
        assert link is None 