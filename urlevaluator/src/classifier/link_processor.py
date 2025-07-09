from tqdm.auto import tqdm
from typing import Optional, List, Tuple, Dict

from ..database import QueueManager
from ..utils import logger
from .topic_classifier import TopicClassifier

DEFAULT_TOPIC_CATEGORIES = ["technology", "sports", "politics", "entertainment", "science"]
LINK_CLASSIFICATION_BATCH_SIZE = 12

class LinkTopicClassifier:
    def __init__(self, crawl_starting_url: str, additional_topic_categories: Optional[List[str]]):
        logger.info("Starting to initialize LinkTopicClassifier")
        self.all_topic_categories = [*DEFAULT_TOPIC_CATEGORIES, *(additional_topic_categories or [])]
        self.classification_queue_manager = QueueManager(crawl_starting_url)
        self.topic_classifier = TopicClassifier(self.all_topic_categories)

    def _classify_single_link_content(self, link_database_id: int, text_content_to_classify: str) -> bool:
        topic_classification_scores: Dict[str, float] = self.topic_classifier.classify_text(text_content_to_classify)

        if topic_classification_scores:
            self.classification_queue_manager.update_classification(link_database_id, topic_classification_scores)
            return True
        return False

    def _classify_link_batch(self, link_classification_batch: List[Tuple[int, str]]) -> int:
        successfully_classified_count = 0
        for link_database_id, text_content_to_classify in tqdm(link_classification_batch, desc="Classifying link content"):
            try:
                if self._classify_single_link_content(link_database_id, text_content_to_classify):
                    successfully_classified_count += 1
            except Exception as classification_error:
                logger.error(f"Error classifying link {link_database_id}: {str(classification_error)}")
        return successfully_classified_count

    def classify_all_pending_links(self):
        total_links_classified = 0
        last_processed_link_id: Optional[int] = None
        total_pending_links = self.classification_queue_manager.get_total_pending()
        logger.info(f"Starting to classify {total_pending_links} pending links")
        
        try:
            while True:
                link_classification_batch = self.classification_queue_manager.fetch_pending_batch(LINK_CLASSIFICATION_BATCH_SIZE, last_processed_link_id)
                if not link_classification_batch:
                    break
                    
                successfully_classified_in_batch = self._classify_link_batch(link_classification_batch)
                total_links_classified += successfully_classified_in_batch
                last_processed_link_id = link_classification_batch[-1][0]
                
                self.classification_queue_manager.connection.commit()
                logger.info(f"Classified {total_links_classified}/{total_pending_links} links")
                
        except Exception as processing_error:
            logger.error(f"Error in classify_all_pending_links: {str(processing_error)}")
            raise
        finally:
            self.classification_queue_manager.close()
            logger.info(f"Completed classifying {total_links_classified} links")
            
