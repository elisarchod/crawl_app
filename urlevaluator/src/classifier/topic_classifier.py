from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .download_model import get_model_manager
from ..utils import logger


class TopicClassifier:
    def __init__(self, topics, model_name=None):
        self.topics = topics
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        model_path = get_model_manager(model_name).get_model_path()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path).to(self.device)
        logger.info("Model loaded successfully")

    def _prepare_model_inputs(self, text: str) -> Dict[str, torch.Tensor]:
        return self.tokenizer([text] * len(self.topics),
                             [f"This text is about {topic}" for topic in self.topics],
                             truncation=True,
                             max_length=512,
                             return_tensors="pt",
                             padding=True).to(self.device)

    def _compute_model_predictions(self, inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
        with torch.no_grad():
            outputs = self.model(**inputs)
            return outputs.logits

    def _calculate_topic_scores(self, scores: torch.Tensor) -> Dict[str, float]:
        probabilities = torch.softmax(scores, dim=-1)
        confidences = probabilities[:, 1].tolist()
        return dict(zip(self.topics, confidences))

    def classify_text(self, text: str) -> Dict[str, float]:
        inputs = self._prepare_model_inputs(text)
        scores = self._compute_model_predictions(inputs)
        return self._calculate_topic_scores(scores)
