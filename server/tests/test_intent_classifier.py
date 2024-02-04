import os
import unittest

from intent_classifier import IntentClassifier

MODELS_DIR = "models/"


class TestIntentClassifierWithoutModel(unittest.TestCase):
    def setUp(self):
        self.classifier = IntentClassifier()

    def test_is_ready(self):
        self.assertEqual(self.classifier.is_ready(), False)

    def test_load_exception(self):
        with self.assertRaises(FileNotFoundError):
            self.classifier.load("invalid_path")

    def test_classify_without_model(self):
        with self.assertRaises(TypeError):
            self.classifier.classify("test utterance")


class TestIntentClassifierWithModel(unittest.TestCase):
    def setUp(self):
        models = os.listdir(MODELS_DIR)
        self.classifiers = [IntentClassifier() for _ in models]
        for classifier, model in zip(self.classifiers, models):
            classifier.load(os.path.join(MODELS_DIR, model))

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
                ),
                ["flight"],
            )


if __name__ == "__main__":
    unittest.main()
