import unittest

from intent_classifier import IntentClassifier


class TestIntentClassifierWithoutModel(unittest.TestCase):
    def setUp(self):
        self.classifier = IntentClassifier()

    def test_is_ready(self):
        self.assertEqual(self.classifier.is_ready(), False)

    def test_load_exception(self):
        with self.assertRaises(FileNotFoundError):
            self.classifier.load("invalid_path")

    def test_classify_without_model(self):
        with self.assertRaises(Exception):
            self.classifier.classify("test utterance")


class TestIntentClassifierWithModel(unittest.TestCase):
    def setUp(self):
        self.classifier = IntentClassifier()
        self.classifier.load("tests/depth-7.tree.model")

    def test_is_ready(self):
        self.assertEqual(self.classifier.is_ready(), True)

    def test_classify_with_model(self):
        self.assertEqual(
            self.classifier.classify(
                "what are the flights from san francisco to denver"
            ),
            ["flight"],
        )


if __name__ == "__main__":
    unittest.main()
