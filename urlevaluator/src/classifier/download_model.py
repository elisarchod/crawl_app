import os
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from urlevaluator.src.utils.singleton import singleton, RESOURCES_DIRECTORY
from urlevaluator.src.utils.log_handler import logger

load_dotenv()

@singleton
class ModelManager:
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        if not self.model_name:
            raise ValueError("Model name must be provided")
            
        self.model_path = os.path.join(RESOURCES_DIRECTORY, self.model_name)

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
            return
        self.save_model()

model_manager = ModelManager(os.environ.get('MODEL_NAME'))

if __name__ == "__main__":
    os.makedirs(RESOURCES_DIRECTORY, exist_ok=True)
    model_manager.download_model()