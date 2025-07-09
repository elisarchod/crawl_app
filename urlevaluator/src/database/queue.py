from typing import List, Optional, Tuple

import duckdb

from .init_db import get_db_manager


class QueueManager:
    def __init__(self, initial_url: str, db_name=None):
        self.connection = duckdb.connect(get_db_manager(db_name).get_db_path())
        self.initial_url = initial_url

    def fetch_pending_batch(self, batch_size: int, last_id: Optional[int]) -> List[Tuple[int, str]]:
        query = """
            SELECT l.id, l.link_text 
            FROM links l
            JOIN pages p ON l.page_id = p.id
            WHERE l.topic_scores IS NULL
            AND p.source_url = ?
            AND l.id > ?
            ORDER BY l.id
            LIMIT ?
        """
        params = [self.initial_url,
                  last_id if last_id is not None else 0,
                  batch_size]
        return self.connection.execute(query, params).fetchall()

    def update_classification(self, link_id: int, topic_scores: dict) -> None:
        query = """
            UPDATE links 
            SET topic_scores = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.connection.execute(query, [topic_scores, link_id])

    def get_total_pending(self) -> int:
        query = """
            SELECT COUNT(*) 
            FROM links l
            JOIN pages p ON l.page_id = p.id
            WHERE l.topic_scores IS NULL
            AND p.source_url = ?
        """
        return self.connection.execute(query, [self.initial_url]).fetchone()[0]

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
