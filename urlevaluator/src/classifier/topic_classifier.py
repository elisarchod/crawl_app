from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from urlevaluator.src.utils.log_handler import logger
from .download_model import model_manager


class TopicClassifier:
    def __init__(self, topics: List[str]):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        model_path = model_manager.get_model_path()
        logger.info(f"Loading model from: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.topics = topics
        logger.info("Model loaded successfully")

    def _prepare_model_inputs(self, text: str) -> Dict[str, torch.Tensor]:
        return self.tokenizer([text] * len(self.topics),
            [f"This text is about {topic}" for topic in self.topics],
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True).to(self.device)

    def _compute_model_predictions(self, inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
        with torch.no_grad():
            outputs = self.model(**inputs)
            return torch.softmax(outputs.logits, dim=1)

    def _calculate_topic_scores(self, scores: torch.Tensor) -> Dict[str, float]:
        confidences = scores[:, 1].tolist()
        return dict(zip(self.topics, confidences))

    def classify_text(self, text: str) -> Dict[str, float]:
        inputs = self._prepare_model_inputs(text)
        scores = self._compute_model_predictions(inputs)
        return self._calculate_topic_scores(scores)
