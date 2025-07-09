"""
Tests for the query_db module and database connection configuration.
"""

import os
import pytest
from unittest.mock import patch, Mock
from urlevaluator.src.utils.query_db import get_db_connection


def test_query_db_default_path():
    with patch('urlevaluator.src.utils.query_db.duckdb.connect') as mock_connect:
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        result = get_db_connection()
        mock_connect.assert_called_once_with('resources/scraping_results.db')
        assert result == mock_conn

def test_query_db_env_override():
    custom_path = "/custom/path/database.db"
    with patch('urlevaluator.src.utils.query_db.duckdb.connect') as mock_connect, \
         patch('os.environ', {"DB_PATH": custom_path}):
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        result = get_db_connection()
        mock_connect.assert_called_once_with(custom_path)
        assert result == mock_conn 