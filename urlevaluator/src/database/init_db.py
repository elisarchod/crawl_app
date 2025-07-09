import os
from dotenv import load_dotenv
import duckdb

from ..utils.log_handler import logger

load_dotenv()

class DatabaseManager:
    def __init__(self, db_name: str = None):
        if db_name is None:
            db_name = os.environ.get('DB_NAME', 'scraping_results.db')
        os.makedirs('resources', exist_ok=True)
        self.db_path: str = os.path.join('resources', db_name)

    def get_db_path(self) -> str:
        return self.db_path

    def create_database(self) -> None:
        if os.path.exists(self.db_path):
            logger.info(f"Database already exists in {self.db_path}. Skipping initialization.")
            return

        logger.info(f"Starting database initialization at {self.db_path}")
        conn: duckdb.DuckDBPyConnection = duckdb.connect(self.db_path)
        
        conn.execute('CREATE SEQUENCE pages_id_seq')
        conn.execute('CREATE SEQUENCE links_id_seq')
        
        conn.execute('''
            CREATE TABLE pages (
                id BIGINT PRIMARY KEY DEFAULT nextval('pages_id_seq'),
                url VARCHAR(2048) UNIQUE,
                source_url VARCHAR(2048),
                depth INTEGER,
                title VARCHAR(255),
                created_at TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE links (
                id BIGINT PRIMARY KEY DEFAULT nextval('links_id_seq'),
                page_id BIGINT,
                url VARCHAR(2048),
                link_text VARCHAR(255),
                content VARCHAR(2048),
                topic_scores JSON,
                visited_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        conn.close()
        logger.info("Database initialization completed successfully")

def get_db_manager(db_name: str = None):
    """Get a new database manager instance."""
    return DatabaseManager(db_name)

if __name__ == "__main__":
    get_db_manager().create_database()

