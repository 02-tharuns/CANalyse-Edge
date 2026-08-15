"""End-to-end demo and reusable processing pipeline."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from .canio import read_candump
from .decoder import DBCDecoder
from .features import signals_to_wide, window_features
from .model import train_and_evaluate
from .quality import assess_frames, signal_ranges
from .simulator import simulate_session


def _features_for_session(root: Path, session: int, fault: str) -> tuple[pd.DataFrame, dict]:
    log_path = root / "data" / "generated" / f"session_{session}_{fault}.log"
    labels_path = root / "data" / "generated" / f"session_{session}_{fault}_labels.csv"
    simulate_session(root / "dbc" / "demo_equipment.dbc", log_path, labels_path,
                     session=session, fault=fault)
    frames = list(read_candump(log_path))
    decoded = list(DBCDecoder(root / "dbc" / "demo_equipment.dbc").decode_many(frames))
    labels = pd.read_csv(labels_path).set_index("timestamp")["label"]
    features = window_features(signals_to_wide(decoded), labels=labels)
    features["session"] = session
    features["asset_id"] = f"demo-pump-{session:02d}"
    quality = {
        "session": session,
        "frames": [item.to_dict() for item in assess_frames(frames)],
        "signals": signal_ranges(decoded),
    }
    return features, quality


def run_demo(root: Path) -> dict:
    faults = ["bearing_degradation", "cooling_restriction", "undervoltage"]
    train_parts, test_parts, quality = [], [], []
    for session in range(1, 10):
        fault = faults[(session - 1) % len(faults)]
        features, report = _features_for_session(root, session, fault)
        # Hold out one complete recording for each fault class. Neighboring windows
        # from a recording never leak across train and test sets.
        (test_parts if session in {4, 5, 6} else train_parts).append(features)
        quality.append(report)

    train = pd.concat(train_parts, ignore_index=True)
    test = pd.concat(test_parts, ignore_index=True)
    model, metrics = train_and_evaluate(train, test)
    prediction = model.predict(test)
    prediction["actual"] = test["label"].to_numpy()
    prediction["session"] = test["session"].to_numpy()
    latest = prediction.iloc[-1]

    outputs = root / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    model.save(root / "models" / "condition_model.joblib")
    prediction.to_csv(outputs / "demo_predictions.csv", index=False)
    (outputs / "demo_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (outputs / "data_quality.json").write_text(json.dumps(quality[-1], indent=2), encoding="utf-8")
    health = {
        "component": "drive-unit-1",
        "health_score": float(latest["health_score"]),
        "condition": str(latest["condition"]),
        "confidence": float(latest["confidence"]),
        "anomaly_score": float(latest["anomaly_score"]),
        "source": "synthetic_demo",
        "disclaimer": "Demonstration output; not validated for safety decisions.",
    }
    (outputs / "latest_health.json").write_text(json.dumps(health, indent=2), encoding="utf-8")
    return {"metrics": metrics, "health": health}


if __name__ == "__main__":
    run_demo(Path(__file__).resolve().parents[1])
