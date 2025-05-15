import unittest

from src.classifier.link_processor import DEFAULT_TOPICS
from urlevaluator.src.classifier.topic_classifier import TopicClassifier

class TestTopicClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = TopicClassifier(DEFAULT_TOPICS)
        self.test_text = "Test text for classification"

    def test_classifier_initialization(self):
        self.assertIsNotNone(self.classifier.model)
        self.assertIsNotNone(self.classifier.tokenizer)

    def test_get_best_topic(self):
        topic_scores = self.classifier.classify_text(self.test_text)
        self.assertIsInstance(topic_scores, dict)
        self.assertListEqual(list(topic_scores.keys()), self.classifier.topics)

        for topic, score in topic_scores.items():
            self.assertIsInstance(topic, str)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

if __name__ == '__main__':
    unittest.main() 