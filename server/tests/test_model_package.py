from unittest import TestCase
from unittest.mock import Mock

from model_package import ModelPackage


class TestModel(TestCase):
    def setUp(self):
        self.model_package = ModelPackage()

    def test_model_initial_state(self):
        self.assertEqual(len(self.model_package.models), 0)

    def test_model_ready_state(self):
        self.assertFalse(self.model_package.ready)

    def test_model_add(self):
        test_model = Mock()
        test_model.is_ready.return_value = False
        test_model.model_name = "Test Model"
        test_model.model_path = "/path/to/model"
        self.model_package.add(test_model)

        self.assertEqual(len(self.model_package.models), 1)

        self.assertFalse(self.model_package.ready)
        test_model.is_ready.return_value = True
        self.assertTrue(self.model_package.ready)

    def test_model_info(self):
        test_model = Mock()
        test_model.is_ready.return_value = True
        test_model.model_name = "Test Model"
        test_model.model_path = "/path/to/model"
        self.model_package.add(test_model)

        expected_info = [{"key": "0", "name": "Test Model", "path": "/path/to/model"}]
        self.assertEqual(self.model_package.info(), expected_info)

    def test_model_index_by_key(self):
        self.assertEqual(self.model_package.model_index(None), None)
        self.assertEqual(self.model_package.model_index(0), None)
        self.assertEqual(self.model_package.model_index("Test Model"), None)
        self.assertEqual(self.model_package.model_index("/path/to/model"), None)

        test_model = Mock()
        test_model.is_ready.return_value = True
        test_model.model_name = "Test Model"
        test_model.model_path = "/path/to/model"
        self.model_package.add(test_model)

        test_model2 = Mock()
        test_model2.is_ready.return_value = True
        test_model2.model_name = "Another Model"
        test_model2.model_path = "/path/to/model2"
        self.model_package.add(test_model2)

        self.assertEqual(self.model_package.model_index(None), 0)
        self.assertEqual(self.model_package.model_index(0), 0)
        self.assertEqual(self.model_package.model_index(7), 1)
        self.assertEqual(self.model_package.model_index(10), 0)
        self.assertEqual(self.model_package.model_index("Test Model"), 0)
        self.assertEqual(self.model_package.model_index("Another Model"), 1)
        self.assertEqual(self.model_package.model_index("Unknown Model"), None)
        self.assertEqual(self.model_package.model_index("/path/to/model2"), 1)
        self.assertEqual(self.model_package.model_index("/does/not/exist"), None)

    def test_model_classify(self):
        test_model = Mock()
        test_model.is_ready.return_value = True
        test_model.predict.return_value = "answer"
        test_model.model_name = "Test Model"
        test_model.model_path = "/path/to/model"
        self.model_package.add(test_model)

        self.assertEqual(self.model_package.classify([1, 2, 3], "0"), "answer")

        self.assertRaises(
            ValueError,
            self.model_package.classify,
            data=[1, 2, 3],
            model_key="Unknown Model",
        )


if __name__ == "__main__":
    unittest.main()
