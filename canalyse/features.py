"""Window CAN engineering signals into compact ML-ready features."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable
import numpy as np
import pandas as pd

from .decoder import SignalValue


def signals_to_wide(values: Iterable[SignalValue]) -> pd.DataFrame:
    rows = [value.to_dict() for value in values if isinstance(value.value, (int, float))]
    if not rows:
        return pd.DataFrame()
    long = pd.DataFrame(rows)
    return (long.pivot_table(index="timestamp", columns="signal", values="value", aggfunc="last")
            .sort_index().interpolate(limit_direction="both"))


def _slope(values: np.ndarray) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.polyfit(np.arange(len(values)), values, 1)[0])


def window_features(wide: pd.DataFrame, window_samples: int = 50, step_samples: int = 25,
                    labels: pd.Series | None = None) -> pd.DataFrame:
    if wide.empty or len(wide) < window_samples:
        return pd.DataFrame()
    records: list[dict] = []
    for start in range(0, len(wide) - window_samples + 1, step_samples):
        chunk = wide.iloc[start:start + window_samples]
        row: dict[str, float | str] = {
            "window_start": float(chunk.index[0]),
            "window_end": float(chunk.index[-1]),
        }
        for signal in sorted(chunk.columns):
            values = chunk[signal].astype(float).to_numpy()
            row.update({
                f"{signal}__mean": float(np.mean(values)),
                f"{signal}__std": float(np.std(values)),
                f"{signal}__min": float(np.min(values)),
                f"{signal}__max": float(np.max(values)),
                f"{signal}__range": float(np.ptp(values)),
                f"{signal}__rms": float(np.sqrt(np.mean(values ** 2))),
                f"{signal}__slope": _slope(values),
            })
        if labels is not None:
            selected = labels.reindex(chunk.index, method="nearest")
            row["label"] = str(selected.mode().iloc[0])
        records.append(row)
    return pd.DataFrame(records)


def feature_columns(frame: pd.DataFrame) -> list[str]:
    excluded = {"window_start", "window_end", "label", "session", "asset_id"}
    return [column for column in frame.columns if column not in excluded]
