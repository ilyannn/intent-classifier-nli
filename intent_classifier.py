# -*- coding: utf-8 -*-

import pickle
import unittest

from sklearn.tree import DecisionTreeClassifier


class IntentClassifier:
    def __init__(self):
        self.model = None

    def is_ready(self):
        return self.model is not None

    def load(self, file_path):
        with open(file_path, "rb") as f:
            self.model = pickle.load(f)
        try:
            assert isinstance(self.model, dict)
            assert "tree" in self.model and "words" in self.model
            assert isinstance(self.model["tree"], DecisionTreeClassifier)
        except AssertionError:
            raise ValueError("Unexpected model format")

    def classify(self, utterance):
        utterance = utterance.lower().replace("?", "")
        predict = self.model["tree"].predict
        words = set(utterance.split(" "))
        features = [int(word in words) for word in self.model["words"]]
        return [predict([features])[0]]
