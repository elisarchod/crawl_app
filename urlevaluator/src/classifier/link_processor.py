from tqdm.auto import tqdm
from typing import Optional, List, Tuple, Dict, Any

from urlevaluator.src.database.queue import QueueManager
from urlevaluator.src.utils.log_handler import logger
from .topic_classifier import TopicClassifier

DEFAULT_TOPICS = ["technology", "sports", "politics", "entertainment", "science"]

class LinkProcessor:
    def __init__(self, initial_url: str, additional_topics: Optional[List[str]]):
        topics = DEFAULT_TOPICS + additional_topics if additional_topics else DEFAULT_TOPICS
        self.db_manager = QueueManager(initial_url)
        self.classifier = TopicClassifier(topics)

    def _process_single_link(self, link_id: int, target_text: str) -> bool:
        topic_scores: Dict[str, float] = self.classifier.classify_text(target_text)

        if topic_scores:
            self.db_manager.update_classification(link_id, topic_scores)
            return True
        return False

    def _process_batch(self, batch: List[Tuple[int, str]]) -> int:
        processed_count = 0
        for link_id, target_text in tqdm(batch, desc="Processing links"):
            try:
                if self._process_single_link(link_id, target_text):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing link {link_id}: {str(e)}")
        return processed_count

    def process_links(self, batch_size: int = 100):
        total_processed = 0
        last_id: Optional[int] = None
        total_pending = self.db_manager.get_total_pending()
        logger.info(f"Starting to process {total_pending} pending links")
        
        try:
            while True:
                batch = self.db_manager.fetch_pending_batch(batch_size, last_id)
                if not batch:
                    break
                    
                processed_in_batch = self._process_batch(batch)
                total_processed += processed_in_batch
                last_id = batch[-1][0]
                
                self.db_manager.connection.commit()
                logger.info(f"Processed {total_processed}/{total_pending} links")
                
        except Exception as e:
            logger.error(f"Error in process_links: {str(e)}")
            raise
        finally:
            self.db_manager.close()
            logger.info(f"Completed processing {total_processed} links")
            
