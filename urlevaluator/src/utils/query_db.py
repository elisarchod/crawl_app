import duckdb
conn = duckdb.connect('data/scraping_results.db')

def delete_all_but_eight_rows():
    conn.execute("DELETE FROM links WHERE id NOT IN (SELECT id FROM links ORDER BY id LIMIT 8);")
    conn.commit()
    conn.close()


def clear_topic_columns():
    conn.execute("""
        UPDATE links 
        SET topic_scores = NULL
    """)
    conn.commit()
    conn.close()


def truncate_tables():
    conn.execute("TRUNCATE TABLE links")
    conn.execute("TRUNCATE TABLE pages")
    conn.commit()
    conn.close()


def get_table_info():
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
    conn.close()


if __name__ == "__main__":
    get_table_info()
    aggregate_topic_scores("http://example.com")
