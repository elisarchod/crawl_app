from urlevaluator.src.database.init_db import db_manager
from urlevaluator.src.utils.log_handler import logger
import duckdb

def aggregate_topic_scores(initial_url: str):
    conn = duckdb.connect(db_manager.get_db_path())
    query = """
        WITH numbered_scores AS (
            SELECT
                l.topic_scores::JSON AS json_blob
            FROM links l
            JOIN pages p ON l.page_id = p.id
            WHERE l.topic_scores IS NOT NULL
            AND p.source_url = ?
        ),
        unpacked_keys AS (
            SELECT
                json_blob,
                UNNEST(json_keys(json_blob)) AS topic_name
            FROM numbered_scores
        ),
        topic_scores AS (
            SELECT
                topic_name AS topic,
                CAST(json_extract_string(json_blob, '$."' || topic_name || '"') AS DOUBLE) AS score
            FROM unpacked_keys
        )
        SELECT
            topic,
            AVG(score) AS average_score
        FROM topic_scores
        GROUP BY topic
        ORDER BY topic;
    """
    
    results = conn.execute(query, [initial_url]).fetchall()
    
    logger.info("\nTopic Score Aggregation Results:")
    logger.info("=" * 40)
    logger.info(f"{'Topic':<15} {'Average Score':<15} ")
    logger.info("-" * 40)
    for topic, average_score in results:
        logger.info(f"{topic:<15} {average_score:.4f}")
    conn.close()