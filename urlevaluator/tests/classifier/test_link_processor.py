"""Modern tests for topic classifier functionality.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from unittest.mock import patch
from urlevaluator.src.classifier.topic_classifier import TopicClassifier
from urlevaluator.src.classifier.link_processor import DEFAULT_TOPIC_CATEGORIES

@pytest.mark.parametrize("topics,text,expected_keys", [
    (DEFAULT_TOPIC_CATEGORIES, "AI and science", set(DEFAULT_TOPIC_CATEGORIES)),
    (["technology", "health"], "healthcare advances", {"technology", "health"}),
])
def test_topic_classifier_classify_text(topics, text, expected_keys):
    with patch('urlevaluator.src.classifier.topic_classifier.AutoTokenizer'), \
         patch('urlevaluator.src.classifier.topic_classifier.AutoModelForSequenceClassification'), \
         patch.object(TopicClassifier, '_calculate_topic_scores') as mock_calculate:
        mock_calculate.return_value = {topic: 0.5 for topic in topics}
        classifier = TopicClassifier(topics)
        result = classifier.classify_text(text)
        assert isinstance(result, dict)
        assert set(result.keys()) == expected_keys

def test_topic_classifier_topics_property():
    with patch('urlevaluator.src.classifier.topic_classifier.AutoTokenizer'), \
         patch('urlevaluator.src.classifier.topic_classifier.AutoModelForSequenceClassification'):
        topics = ["a", "b", "c"]
        classifier = TopicClassifier(topics)
        assert classifier.topics == topics

def test_default_topic_categories_validity():
    assert len(DEFAULT_TOPIC_CATEGORIES) > 0
    assert all(isinstance(category, str) for category in DEFAULT_TOPIC_CATEGORIES) 