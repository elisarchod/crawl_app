"""Modern tests for classifier modules.

Focus on public API and observable behavior with minimal mocking.
"""

import pytest
from unittest.mock import patch, Mock
from urlevaluator.src.classifier.link_processor import LinkTopicClassifier, DEFAULT_TOPIC_CATEGORIES
from urlevaluator.src.classifier.topic_classifier import TopicClassifier


class TestTopicClassifier:
    """Test the TopicClassifier public interface."""
    
    def test_init_with_topics(self):
        """Test classifier initialization with custom topics."""
        topics = ["technology", "sports"]
        with patch('urlevaluator.src.classifier.topic_classifier.AutoTokenizer'), \
             patch('urlevaluator.src.classifier.topic_classifier.AutoModelForSequenceClassification'):
            classifier = TopicClassifier(topics)
            assert classifier.topics == topics
    
    def test_init_requires_topics(self):
        """Test that TopicClassifier requires topics parameter."""
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            TopicClassifier()
    
    @patch.object(TopicClassifier, '_calculate_topic_scores')
    @patch.object(TopicClassifier, '_compute_model_predictions')
    @patch('urlevaluator.src.classifier.topic_classifier.AutoTokenizer')
    @patch('urlevaluator.src.classifier.topic_classifier.AutoModelForSequenceClassification')
    def test_classify_text_returns_dict(self, mock_model, mock_tokenizer, mock_compute, mock_calculate):
        """Test that classify_text returns a dictionary with topic scores."""
        # Setup mocks
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        # Mock the model predictions to return a tensor-like object
        mock_tensor = Mock()
        mock_compute.return_value = mock_tensor
        
        # Mock the topic scores calculation
        mock_calculate.return_value = {"technology": 0.8, "sports": 0.2}
        
        classifier = TopicClassifier(["technology", "sports"])
        result = classifier.classify_text("AI in sports")
        
        assert isinstance(result, dict)
        assert set(result.keys()) == {"technology", "sports"}
        assert all(isinstance(score, (int, float)) for score in result.values())


class TestLinkTopicClassifier:
    """Test the LinkTopicClassifier public interface."""
    
    @patch('urlevaluator.src.classifier.link_processor.QueueManager')
    @patch('urlevaluator.src.classifier.link_processor.TopicClassifier')
    def test_init_with_url_and_topics(self, mock_topic_classifier, mock_queue_manager):
        """Test initialization with URL and topics."""
        url = "https://example.com"
        topics = ["entertainment", "science"]
        
        classifier = LinkTopicClassifier(url, topics)
        
        assert "entertainment" in classifier.all_topic_categories
        assert "science" in classifier.all_topic_categories
        assert mock_queue_manager.called
        assert mock_topic_classifier.called
    
    @patch('urlevaluator.src.classifier.link_processor.QueueManager')
    @patch('urlevaluator.src.classifier.link_processor.TopicClassifier')
    def test_batch_classification(self, mock_topic_classifier, mock_queue_manager):
        """Test batch classification functionality."""
        classifier = LinkTopicClassifier("https://example.com", ["tech", "sports"])
        
        # Mock the single classification method
        classifier._classify_single_link_content = Mock(return_value=True)
        
        batch = [(1, "content1"), (2, "content2")]
        result = classifier._classify_link_batch(batch)
        
        assert result == 2
        assert classifier._classify_single_link_content.call_count == 2


class TestDefaultTopicCategories:
    """Test the default topic categories constant."""
    
    def test_default_categories_unique(self):
        """Test that default categories are unique."""
        assert len(DEFAULT_TOPIC_CATEGORIES) == len(set(DEFAULT_TOPIC_CATEGORIES))


class TestModelManager:
    """Test the ModelManager functionality."""
    
    @patch('urlevaluator.src.classifier.download_model.AutoTokenizer')
    @patch('urlevaluator.src.classifier.download_model.AutoModelForSequenceClassification')
    @patch('urlevaluator.src.classifier.download_model.os.makedirs')
    @patch('urlevaluator.src.classifier.download_model.os.path.exists')
    def test_download_model_creates_directory(self, mock_exists, mock_makedirs, mock_model, mock_tokenizer):
        """Test that model download creates necessary directories."""
        from urlevaluator.src.classifier.download_model import ModelManager
        
        # Setup mocks
        mock_exists.return_value = False
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        model_manager = ModelManager("test-model")
        model_manager.download_model()
        
        # Verify directory creation
        mock_makedirs.assert_called()
    
    @patch('urlevaluator.src.classifier.download_model.AutoTokenizer')
    @patch('urlevaluator.src.classifier.download_model.AutoModelForSequenceClassification')
    @patch('urlevaluator.src.classifier.download_model.os.path.exists')
    def test_download_model_skips_existing(self, mock_exists, mock_model, mock_tokenizer):
        """Test that model download skips if model already exists."""
        from urlevaluator.src.classifier.download_model import ModelManager
        
        # Setup mocks
        mock_exists.return_value = True
        
        model_manager = ModelManager("test-model")
        model_manager.download_model()
        
        # Should not download if model exists
        mock_tokenizer.from_pretrained.assert_not_called()
        mock_model.from_pretrained.assert_not_called() 