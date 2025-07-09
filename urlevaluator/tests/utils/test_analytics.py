"""Modern tests for utility modules.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from unittest.mock import patch, Mock
from urlevaluator.src.utils.analytics import aggregate_topic_scores


class TestAnalytics:
    """Test analytics functionality."""
    
    @patch('urlevaluator.src.utils.analytics.duckdb.connect')
    def test_aggregate_topic_scores_success(self, mock_connect):
        """Test successful topic score aggregation."""
        # Setup mock database connection and results
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("technology", 0.85),
            ("sports", 0.12),
            ("politics", 0.03)
        ]
        mock_connection.execute.return_value = mock_result

        with patch('urlevaluator.src.utils.analytics.logger') as mock_logger:
            aggregate_topic_scores("https://example.com", "test.db")

        # Verify database operations
        mock_connect.assert_called_once_with("test.db")
        mock_connection.execute.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('urlevaluator.src.utils.analytics.duckdb.connect')
    def test_aggregate_topic_scores_no_results(self, mock_connect):
        """Test topic score aggregation with no results."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []  # No results
        mock_connection.execute.return_value = mock_result

        with patch('urlevaluator.src.utils.analytics.logger') as mock_logger:
            aggregate_topic_scores("https://example.com", "test.db")

        # Should still log headers even with no results
        mock_logger.info.assert_called()
        mock_connection.close.assert_called_once()
    
    @patch('urlevaluator.src.utils.analytics.duckdb.connect')
    def test_aggregate_topic_scores_database_error(self, mock_connect):
        """Test topic score aggregation with database error."""
        mock_connect.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            aggregate_topic_scores("https://example.com", "test.db")


class TestLogHandler:
    """Test log handler functionality."""
    
    def test_logger_import(self):
        """Test that logger can be imported and used."""
        from urlevaluator.src.utils.log_handler import logger
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_logger_basic_functionality(self):
        """Test basic logger functionality."""
        from urlevaluator.src.utils.log_handler import logger
        
        # Test that logger methods exist and are callable
        assert callable(logger.info)
        assert callable(logger.error)
        assert callable(logger.debug)


 