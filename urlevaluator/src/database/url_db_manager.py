from datetime import datetime
from typing import List

import duckdb

from urlevaluator.src.database.init_db import db_manager
from urlevaluator.src.scraper.link_models import Link


class CrawlerDataManager:
    def __init__(self):
        self.connection = duckdb.connect(db_manager.get_db_path())
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def is_url_visited(self, url: str) -> bool:
        count = self.connection.execute('SELECT COUNT(*) FROM links WHERE url = ? AND visited_at IS NOT NULL', [url]).fetchone()[0]
        return count > 0

    def mark_url_visited(self, url: str) -> None:
        self.connection.execute(
            'UPDATE links SET visited_at = ?, updated_at = ? WHERE url = ?',
            [self.timestamp, self.timestamp, url]
        )

    def get_visited_urls(self) -> set:
        result = self.connection.execute('SELECT url FROM links WHERE visited_at IS NOT NULL').fetchall()
        return {row[0] for row in result}

    def save_page_data(self, url: str, source_url: str, depth: int, title: str, links: List[Link]):
        try:
            self.connection.execute(
                'INSERT OR IGNORE INTO pages (url, source_url, depth, title, created_at) VALUES (?, ?, ?, ?, ?)',
                [url, source_url, depth, title, self.timestamp]
            )
            
            page_id = self.connection.execute(
                'SELECT id FROM pages WHERE url = ?', 
                [url]
            ).fetchone()[0]
            
            for link in links:
                self.connection.execute(
                    'INSERT OR IGNORE INTO links (page_id, url, link_text, content) VALUES (?, ?, ?, ?)',
                    [page_id, link.url, link.text, link.content]
                )
            
        except Exception as e:
            raise e

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None 
    