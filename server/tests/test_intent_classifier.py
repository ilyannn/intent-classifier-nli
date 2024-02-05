import os
import unittest

from intent_classifier import *

MODELS_DIR = "models/"


class TestIntentClassifierWithoutModel(unittest.TestCase):
    def setUp(self):
        self.classifiers = [
            IntentClassifierTreeModel(),
            IntentClassifierEntailmentModel(),
        ]

    def test_is_ready(self):
        for classifier in self.classifiers:
            self.assertEqual(classifier.is_ready(), False)

    def test_load_exception(self):
        for classifier in self.classifiers:
            with self.assertRaises(FileNotFoundError):
                classifier.load("invalid_path")

    def test_classify_without_model(self):
        for classifier in self.classifiers:
            with self.assertRaises(ValueError):
                classifier.classify("test utterance")


class TestIntentClassifierWithModel(unittest.TestCase):
    def setUp(self):
        models = os.listdir(MODELS_DIR)
        self.classifiers = [
            load_intent_classifier(os.path.join(MODELS_DIR, model)) for model in models
        ]

    def test_has_models(self):
        self.assertTrue(self.classifiers)

    def test_is_ready(self):
        for classifier in self.classifiers:
            self.assertEqual(classifier.is_ready(), True)

    def test_classify_with_model(self):
        for classifier in self.classifiers:
            self.assertEqual(
                classifier.classify(
                    "what are the flights from san francisco to denver"
                )[0],
                "flight",
            )


if __name__ == "__main__":
    unittest.main()
