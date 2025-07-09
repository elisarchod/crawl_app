"""
Tests for the ModelManager class and model download functionality.
"""

import os
from urlevaluator.src.classifier.download_model import ModelManager

def test_model_manager_uses_env(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "my/model")
    manager = ModelManager()
    assert manager.model_name == "my/model"

def test_model_manager_singleton():
    m1 = ModelManager("first/model")
    m2 = ModelManager("second/model")
    assert m1.model_name == "first/model"
    assert m2.model_name == "second/model"
    assert m1 is not m2 