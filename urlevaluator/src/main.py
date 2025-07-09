#!/usr/bin/env python3
"""
Main entry point for the URL Evaluator application.

This module provides the primary interface for crawling websites and classifying links.
"""

from typing import List, Optional

from .scraper import WebSiteCrawler
from .classifier import LinkTopicClassifier
from .utils import logger, aggregate_topic_scores
from .database import get_db_manager


def crawl_website_and_classify_links(
    starting_url: str,
    maximum_crawl_depth: int,
    additional_topic_categories: Optional[List[str]] = None
) -> None:
    """
    Crawl a website and classify the content of discovered links.
    
    This function orchestrates the entire process of crawling a website
    and classifying the discovered links by topic.
    
    Args:
        starting_url: The URL to start crawling from
        maximum_crawl_depth: Maximum depth to crawl (0 = only starting page)
        additional_topic_categories: Additional topic categories beyond defaults
        
    Raises:
        ValueError: If starting_url is invalid
        Exception: If crawling or classification fails
    """
    try:
        logger.info(f"Starting website crawl from: {starting_url}")
        WebSiteCrawler(
            starting_url, 
            maximum_crawl_depth=maximum_crawl_depth
        ).start_website_crawling()
        
        logger.info("Starting link classification")
        LinkTopicClassifier(
            starting_url, 
            additional_topic_categories
        ).classify_all_pending_links()
        
        logger.info("Aggregating topic scores")
        aggregate_topic_scores(starting_url, get_db_manager().get_db_path())
        
        logger.info("Link classification processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during website crawling and classification: {e}")
        raise


if __name__ == "__main__":
    # Load environment variables only when running as main
    from dotenv import load_dotenv
    load_dotenv()
    
    # Simple fallback for direct execution
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        topics = sys.argv[3:] if len(sys.argv) > 3 else None
        crawl_website_and_classify_links(url, depth, topics)
    else:
        print("Usage: python main.py <url> [depth] [topics...]")
        print("Or use: poetry run poe scrape-url <url> [depth]")
        print("Or use: poetry run poe scrape-with-topics <url> [depth] [topics...]")