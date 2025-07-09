"""
Modern tests for database modules.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from unittest.mock import Mock, patch
from urlevaluator.src.database.url_db_manager import WebCrawlDatabaseManager
from urlevaluator.src.database.queue import QueueManager
from urlevaluator.src.scraper.models import ExtractedLink, CrawledPageData

class TestWebCrawlDatabaseManager:
    def setup_method(self):
        with patch('urlevaluator.src.database.url_db_manager.duckdb.connect') as mock_connect:
            self.mock_connection = Mock()
            mock_connect.return_value = self.mock_connection
            self.db_manager = WebCrawlDatabaseManager()

    def test_is_url_already_visited(self):
        mock_result = Mock()
        mock_result.fetchone.return_value = [1]
        self.mock_connection.execute.return_value = mock_result
        assert self.db_manager.is_url_already_visited("https://example.com") is True

    def test_mark_url_as_visited(self):
        self.db_manager.mark_url_as_visited("https://example.com")
        self.mock_connection.execute.assert_called()

    def test_get_all_visited_urls(self):
        mock_result = Mock()
        mock_result.fetchall.return_value = [("https://example.com",), ("https://test.org",)]
        self.mock_connection.execute.return_value = mock_result
        result = self.db_manager.get_all_visited_urls()
        assert result == {"https://example.com", "https://test.org"}

    def test_store_crawled_page_data(self):
        mock_page_result = Mock()
        mock_page_result.fetchone.return_value = [123]
        self.mock_connection.execute.return_value = mock_page_result
        extracted_links = [ExtractedLink(url="https://example.com/link1", anchor_text="Link 1", surrounding_content="Context 1")]
        crawled_data = CrawledPageData(url="https://example.com", source_url="https://ref.com", crawl_depth=1, page_title="Test", extracted_links=extracted_links)
        self.db_manager.store_crawled_page_data(crawled_data)
        self.mock_connection.execute.assert_called()

    def test_close_database_connection(self):
        self.db_manager.close_database_connection()
        self.mock_connection.close.assert_called_once()

class TestQueueManager:
    def setup_method(self):
        with patch('urlevaluator.src.database.queue.get_db_manager') as mock_get_db_manager:
            mock_db_manager = Mock()
            mock_db_manager.get_db_path.return_value = "test.db"
            mock_get_db_manager.return_value = mock_db_manager
            with patch('urlevaluator.src.database.queue.duckdb.connect') as mock_connect:
                self.mock_connection = Mock()
                mock_connect.return_value = self.mock_connection
                self.queue_manager = QueueManager("https://example.com")

    def test_get_total_pending(self):
        mock_result = Mock()
        mock_result.fetchone.return_value = [42]
        self.mock_connection.execute.return_value = mock_result
        assert self.queue_manager.get_total_pending() == 42

    def test_fetch_pending_batch_with_data(self):
        mock_result = Mock()
        mock_result.fetchall.return_value = [(1, "content1"), (2, "content2")]
        self.mock_connection.execute.return_value = mock_result
        result = self.queue_manager.fetch_pending_batch(2, None)
        assert result == [(1, "content1"), (2, "content2")]

    def test_update_classification(self):
        self.queue_manager.update_classification(1, {"topic": 0.9})
        self.mock_connection.execute.assert_called()

    def test_close_connection(self):
        self.queue_manager.close()
        self.mock_connection.close.assert_called_once() 