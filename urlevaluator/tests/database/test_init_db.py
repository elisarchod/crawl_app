"""
Tests for the DatabaseManager class and database initialization.
"""

import os
from unittest.mock import patch, Mock
from urlevaluator.src.database.init_db import DatabaseManager, get_db_manager

def test_database_manager_default_path():
    with patch.dict(os.environ, {}, clear=True):
        manager = DatabaseManager()
        assert manager.db_path == os.path.join('resources', 'scraping_results.db')

def test_database_manager_env_override():
    env_db = "env_database.db"
    with patch.dict(os.environ, {'DB_NAME': env_db}, clear=True):
        manager = get_db_manager()
        expected_path = os.path.join('resources', env_db)
        assert manager.db_path == expected_path 