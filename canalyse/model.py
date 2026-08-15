"""Training and inference for component condition classification."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix

from .features import feature_columns


@dataclass
class ConditionModel:
    classifier: RandomForestClassifier
    columns: list[str]

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        probabilities = self.classifier.predict_proba(frame[self.columns])
        prediction = self.classifier.classes_[np.argmax(probabilities, axis=1)]
        confidence = np.max(probabilities, axis=1)
        result = frame[["window_start", "window_end"]].copy()
        result["condition"] = prediction
        result["confidence"] = confidence.round(4)
        result["anomaly_score"] = (1.0 - probabilities[:, list(self.classifier.classes_).index("healthy")]).round(4)
        result["health_score"] = (100 * (1 - result["anomaly_score"])).clip(0, 100).round(1)
        return result

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"classifier": self.classifier, "columns": self.columns}, path)

    @classmethod
    def load(cls, path: Path) -> "ConditionModel":
        value = joblib.load(path)
        return cls(value["classifier"], value["columns"])


def train_and_evaluate(train: pd.DataFrame, test: pd.DataFrame, random_state: int = 42):
    columns = feature_columns(train)
    classifier = RandomForestClassifier(
        n_estimators=120, max_depth=6, min_samples_leaf=5,
        class_weight="balanced", random_state=random_state, n_jobs=-1,
    )
    classifier.fit(train[columns], train["label"])
    prediction = classifier.predict(test[columns])
    labels = sorted(set(train["label"]) | set(test["label"]))
    metrics = {
        "evaluation_scope": "synthetic held-out sessions; not a real-world performance claim",
        "accuracy": round(float(accuracy_score(test["label"], prediction)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(test["label"], prediction)), 4),
        "classification_report": classification_report(test["label"], prediction, labels=labels,
                                                       output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(test["label"], prediction, labels=labels).tolist(),
        "labels": labels,
        "train_windows": int(len(train)),
        "test_windows": int(len(test)),
    }
    return ConditionModel(classifier, columns), metrics
