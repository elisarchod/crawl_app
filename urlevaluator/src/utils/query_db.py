import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_path = os.getenv('DB_PATH', 'resources/scraping_results.db')
    return duckdb.connect(db_path)

def delete_all_but_eight_rows():
    with get_db_connection() as conn:
        conn.execute("DELETE FROM links WHERE id NOT IN (SELECT id FROM links ORDER BY id LIMIT 8);")
        conn.commit()

def clear_topic_columns():
    with get_db_connection() as conn:
        conn.execute("""
            UPDATE links 
            SET topic_scores = NULL
        """)
        conn.commit()

def truncate_tables():
    with get_db_connection() as conn:
        conn.execute("TRUNCATE TABLE links")
        conn.execute("TRUNCATE TABLE pages")
        conn.commit()

def get_table_info():
    with get_db_connection() as conn:
        tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main';").fetchall()
        print(f"Found {len(tables)} tables in the database")
        
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
            print(f"\nTable: {table_name}")
            print(f"Total rows: {count}")
            print("Sample rows:")
            rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 5;").fetchall()
            for row in rows:
                print(row)

if __name__ == "__main__":
    get_table_info()
    truncate_tables()
