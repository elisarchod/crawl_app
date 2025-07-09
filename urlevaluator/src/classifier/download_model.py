from typing import Optional
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from ..utils import logger

class ModelManager:
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        if not self.model_name:
            self.model_name = os.environ.get('MODEL_NAME', 'facebook/bart-large-mnli')
        os.makedirs('resources', exist_ok=True)
        self.model_path = os.path.join('resources', self.model_name)

    def get_model_path(self) -> str:
        return self.model_path

    def save_model(self) -> None:
        logger.info(f"Downloading model and tokenizer: {self.model_name}")
        os.makedirs(self.model_path, exist_ok=True)
        AutoTokenizer.from_pretrained(self.model_name).save_pretrained(self.model_path)
        AutoModelForSequenceClassification.from_pretrained(self.model_name).save_pretrained(self.model_path)
        logger.info("Model and tokenizer successfully downloaded and cached")

    def download_model(self) -> None:
        logger.info(f"Starting model download: {self.model_name}")
        if os.path.exists(self.model_path):
            logger.info(f"Model already exists at {self.model_path}. Skipping download.")
        else:
            self.save_model()

def get_model_manager(model_name: str = None):
    """Get a new model manager instance."""
    return ModelManager(model_name)

if __name__ == "__main__":
    get_model_manager().download_model()