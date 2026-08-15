"""Data-quality checks for CAN frames and decoded engineering signals."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from statistics import median
from typing import Iterable

from .canio import CANFrame
from .decoder import SignalValue


@dataclass(frozen=True)
class FrameQuality:
    arbitration_id: int
    frame_count: int
    expected_dlc: int
    dlc_mismatches: int
    median_period_ms: float | None
    large_gaps: int
    out_of_order: int

    def to_dict(self) -> dict:
        value = asdict(self)
        value["arbitration_id_hex"] = f"0x{self.arbitration_id:X}"
        return value


def assess_frames(frames: Iterable[CANFrame], gap_multiplier: float = 3.0) -> list[FrameQuality]:
    grouped: dict[int, list[CANFrame]] = defaultdict(list)
    for frame in frames:
        grouped[frame.arbitration_id].append(frame)

    reports = []
    for can_id, group in sorted(grouped.items()):
        dlcs = [frame.dlc for frame in group]
        expected_dlc = max(set(dlcs), key=dlcs.count)
        deltas = [b.timestamp - a.timestamp for a, b in zip(group, group[1:])]
        positive = [delta for delta in deltas if delta > 0]
        typical = median(positive) if positive else None
        reports.append(FrameQuality(
            arbitration_id=can_id,
            frame_count=len(group),
            expected_dlc=expected_dlc,
            dlc_mismatches=sum(dlc != expected_dlc for dlc in dlcs),
            median_period_ms=round(typical * 1000, 3) if typical is not None else None,
            large_gaps=sum(delta > typical * gap_multiplier for delta in positive) if typical else 0,
            out_of_order=sum(delta <= 0 for delta in deltas),
        ))
    return reports


def signal_ranges(values: Iterable[SignalValue]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for value in values:
        if isinstance(value.value, (int, float)):
            grouped[value.signal].append(float(value.value))
    return {
        signal: {
            "samples": len(samples),
            "minimum": round(min(samples), 4),
            "maximum": round(max(samples), 4),
            "stuck": int(len(samples) > 5 and max(samples) == min(samples)),
        }
        for signal, samples in sorted(grouped.items()) if samples
    }
