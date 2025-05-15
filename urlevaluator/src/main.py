from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()
from .scraper.crawler import WebScraper
from .classifier.link_processor import LinkProcessor
from .utils.log_handler import logger
from .utils.analytics import aggregate_topic_scores



def scrape_and_process_links(initial_url: str,
                             max_depth: int,
                             additional_topics: Optional[List[str]] = None):

    WebScraper(initial_url, max_depth=max_depth).start_scraping()
    LinkProcessor(initial_url, additional_topics).process_links()
    logger.info("Link processing completed")
    aggregate_topic_scores(initial_url)

if __name__ == "__main__":
    scrape_and_process_links("http://example.com", 2)
    # scrape_and_process_links("https://nohello.net/en/", 2)