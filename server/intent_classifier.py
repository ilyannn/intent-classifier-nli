# -*- coding: utf-8 -*-

import pickle

from sklearn.tree import DecisionTreeClassifier


class IntentClassifier:
    def __init__(self):
        self.model = None
        self.model_name = "Decision Tree Classifier"
        self.model_path = None

    def is_ready(self):
        return self.model is not None

    def load(self, file_path):
        self.model_path = file_path

        with open(file_path, "rb") as f:
            model = pickle.load(f)
        try:
            assert isinstance(model, dict)
            assert "tree" in model and "words" in model
            assert isinstance(model["tree"], DecisionTreeClassifier)
        except AssertionError as e:
            raise ValueError("Unexpected model format") from e

        self.model = model

    def classify(self, utterance):
        utterance = utterance.lower().replace("?", "")
        predict = self.model["tree"].predict
        words = set(utterance.split(" "))
        features = [int(word in words) for word in self.model["words"]]
        return [predict([features])[0]]
