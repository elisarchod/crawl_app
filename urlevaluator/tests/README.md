# Tests Directory

This directory contains all tests for the urlevaluator project, organized to mirror the `src` directory structure.

## Directory Structure

```
tests/
├── conftest.py              # Shared pytest configuration and fixtures
├── __init__.py              # Makes tests a Python package
├── README.md                # This documentation file
├── classifier/              # Tests for classifier module
│   ├── test_topic_classifier.py
│   └── test_link_processor.py
├── database/                # Tests for database module
│   └── test_url_db_manager.py
├── scraper/                 # Tests for scraper module
│   ├── test_crawler.py
│   └── test_models.py
└── utils/                   # Tests for utils module
    └── test_analytics.py
```

## Running Tests

### Run all tests:
```bash
poetry run pytest urlevaluator/tests/
```

### Run tests for a specific module:
```bash
# Classifier tests only
poetry run pytest urlevaluator/tests/classifier/

# Database tests only
poetry run pytest urlevaluator/tests/database/

# Scraper tests only
poetry run pytest urlevaluator/tests/scraper/

# Utils tests only
poetry run pytest urlevaluator/tests/utils/
```

### Run tests with verbose output:
```bash
poetry run pytest urlevaluator/tests/ -v
```

### Run tests with coverage:
```bash
poetry run pytest urlevaluator/tests/ --cov=urlevaluator
```

## Test Organization

- **classifier/**: Tests for topic classification functionality
  - `test_topic_classifier.py`: Tests for the main TopicClassifier class
  - `test_link_processor.py`: Tests for link processing and batch classification

- **database/**: Tests for database operations
  - `test_url_db_manager.py`: Tests for URL database management and queue operations

- **scraper/**: Tests for web scraping functionality
  - `test_crawler.py`: Tests for URL validation, webpage downloading, and content extraction
  - `test_models.py`: Tests for data models used in scraping

- **utils/**: Tests for utility functions
  - `test_analytics.py`: Tests for analytics and logging functionality

## Test Philosophy

Tests focus on:
- **Public API behavior** rather than implementation details
- **Observable outcomes** rather than internal state
- **Minimal mocking** to test real behavior
- **Clear, descriptive test names** that explain what is being tested 