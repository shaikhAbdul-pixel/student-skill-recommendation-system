"""Fixed holdout evaluation of synthetic labels; never a claim about real students."""
import hashlib
import json
from collections import Counter
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.dummy import DummyClassifier
from src.engine import Recommender
from src.profiles import features


def signature(record):
    return json.dumps(features(record), sort_keys=True)


def evaluate(records):
    # Remove exact feature duplicates BEFORE splitting, not after looking at scores.
    unique = {signature(r): r for r in records}
    clean = list(unique.values())
    train, test = train_test_split(clean, test_size=0.25, stratify=[r["track"] for r in clean], random_state=42)
    engine = Recommender(train)  # vocabulary, trees, neighbours and centroids fit on TRAIN ONLY
    truth = [r["track"] for r in test]
    scores = engine.score(test)
    metrics = {}
    predictions = {}
    for name, values in scores.items():
        predicted = engine.classes[np.argmax(values, axis=1)]
        predictions[name] = predicted
        metrics[name] = {"accuracy": float(accuracy_score(truth, predicted)),
                         "macro_f1": float(f1_score(truth, predicted, average="macro", zero_division=0))}
    dummy = DummyClassifier(strategy="most_frequent").fit(np.zeros((len(train), 1)), [r["track"] for r in train])
    baseline = dummy.predict(np.zeros((len(test), 1)))
    metrics["Most-frequent baseline"] = {"accuracy": float(accuracy_score(truth, baseline)),
                                         "macro_f1": float(f1_score(truth, baseline, average="macro", zero_division=0))}
    overlap = {signature(r) for r in train} & {signature(r) for r in test}
    return {
        "dataset": "synthetic_demo_v1", "dataset_sha256": hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest(),
        "seed": 42, "input_rows": len(records), "unique_rows": len(clean),
        "train_rows": len(train), "test_rows": len(test), "feature_overlap_count": len(overlap),
        "test_class_counts": dict(Counter(truth)), "metrics": metrics,
        "class_order": engine.classes.tolist(),
        "hybrid_confusion_matrix": confusion_matrix(truth, predictions["Hybrid"], labels=engine.classes).tolist(),
        "hybrid_classification_report": classification_report(truth, predictions["Hybrid"], output_dict=True, zero_division=0),
        "limitations": [
            "All student profiles and labels were generated for demonstration, not collected from real students.",
            "A random holdout measures recovery of synthetic design patterns, not real-world recommendation quality.",
            "Hybrid weights and model settings are design choices, not tuned or validated on real students.",
            "Course relevance and skill-gap rules are not measured by classification accuracy.",
            "One fixed split gives no estimate of uncertainty; future work needs independent expert labels and user studies.",
        ],
    }
