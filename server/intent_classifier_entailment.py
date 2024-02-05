import csv
import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MULTICLASS_PENALTY = 0.1
PROB_THRESHOLD = 0.2
TOP_N_CHOICES = 3


class IntentClassifierEntailmentModel:
    def __init__(self):
        self.model_name = "Entailment (NLI) Model"
        self.model_path = None

        self.device = torch.device("cuda" if torch.cuda.is_available() else "")

        self.model = None
        self.tokenizer = None
        self.base_labels = None
        self.labels = None
        self.multiclass_labels = None
        self.base_hypotheses = None
        self.entailment_id = None

    def is_ready(self):
        return self.model is not None

    def load(self, dir_path):
        self.model_path = dir_path
        base_labels_file = os.path.join(dir_path, "base_labels.tsv")
        labels_file = os.path.join(dir_path, "labels.txt")

        with open(base_labels_file, "rt", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            base_hypotheses_by_label = list(reader)
            self.base_labels = [row[0] for row in base_hypotheses_by_label]
            self.base_hypotheses = [row[1] for row in base_hypotheses_by_label]

        with open(labels_file, "rt", encoding="utf-8") as f:
            self.labels = [l for l in f.read().split("\n") if l]

        try:
            assert self.base_labels
            self.multiclass_labels = [
                tuple(self.base_labels.index(l) for l in label.split("+"))
                for label in self.labels
            ]
            assert self.multiclass_labels
        except AssertionError as e:
            raise ValueError("Unexpected model format") from e

        model = AutoModelForSequenceClassification.from_pretrained(dir_path)
        self.model = model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(dir_path)

        id2labels = self.model.config.id2label.items()
        self.entailment_id = next(ix for ix, v in id2labels if v == "entailment")

    def classify(self, utterance):
        if not self.is_ready():
            raise ValueError("Model not loaded")

        utterance = utterance.lower().replace("?", "")

        inputs = self.tokenizer.batch_encode_plus(
            [[utterance, t] for t in self.base_hypotheses],
            add_special_tokens=True,
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        logits = self.model(**inputs)["logits"][:, self.entailment_id]
        probs = logits.softmax(dim=0).tolist()
        assert len(probs) == len(self.base_hypotheses) == len(self.base_labels)

        all_probs = [
            sum(probs[ix] for ix in multi_labels)
            - (len(multi_labels) - 1) * MULTICLASS_PENALTY
            for multi_labels in self.multiclass_labels
        ]

        good = [
            (p, label)
            for p, label in zip(all_probs, self.labels)
            if p >= PROB_THRESHOLD
        ]
        topn = sorted(good, reverse=True)[:TOP_N_CHOICES]
        return [label for _, label in topn]
