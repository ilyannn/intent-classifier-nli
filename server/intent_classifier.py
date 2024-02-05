import os

from intent_classifier_entailment import IntentClassifierEntailmentModel
from intent_classifier_tree import IntentClassifierTreeModel


def load_intent_classifier(path):
    if os.path.isdir(path):
        model = IntentClassifierEntailmentModel()
    else:
        model = IntentClassifierTreeModel()

    model.load(path)
    return model
