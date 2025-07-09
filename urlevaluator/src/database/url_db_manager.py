import os
import duckdb
from .init_db import get_db_manager
from ..scraper.models import CrawledPageData
from datetime import datetime

class WebCrawlDatabaseManager:
    def __init__(self, db_name=None):
        self.database_connection = duckdb.connect(get_db_manager(db_name).get_db_path())
        self.current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def is_url_already_visited(self, url: str) -> bool:
        visited_url_count = self.database_connection.execute(
            'SELECT COUNT(*) FROM links WHERE url = ? AND visited_at IS NOT NULL', 
            [url]
        ).fetchone()[0]
        return visited_url_count > 0

    def mark_url_as_visited(self, url: str) -> None:
        self.database_connection.execute(
            'UPDATE links SET visited_at = ?, updated_at = ? WHERE url = ?',
            [self.current_timestamp, self.current_timestamp, url]
        )

    def get_all_visited_urls(self) -> set:
        query_results = self.database_connection.execute(
            'SELECT url FROM links WHERE visited_at IS NOT NULL'
        ).fetchall()
        return {row[0] for row in query_results}

    def store_crawled_page_data(self, crawled_page_data: CrawledPageData):
        try:
            self.database_connection.execute(
                'INSERT OR IGNORE INTO pages (url, source_url, depth, title, created_at) VALUES (?, ?, ?, ?, ?)',
                [crawled_page_data.url, crawled_page_data.source_url, crawled_page_data.crawl_depth, crawled_page_data.page_title, self.current_timestamp]
            )
            
            page_database_id = self.database_connection.execute(
                'SELECT id FROM pages WHERE url = ?', 
                [crawled_page_data.url]
            ).fetchone()[0]
            
            for extracted_link in crawled_page_data.extracted_links:
                self.database_connection.execute(
                    'INSERT OR IGNORE INTO links (page_id, url, link_text, content) VALUES (?, ?, ?, ?)',
                    [page_database_id, extracted_link.url, extracted_link.anchor_text, extracted_link.surrounding_content]
                )
            
        except Exception as database_error:
            raise database_error

    def close_database_connection(self):
        if self.database_connection:
            self.database_connection.close()
            self.database_connection = None 
    