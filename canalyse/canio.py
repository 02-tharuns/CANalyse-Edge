"""Readers for candump and simple CSV CAN logs."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import re

CANDUMP = re.compile(
    r"^\s*\((?P<timestamp>\d+(?:\.\d+)?)\)\s+"
    r"(?P<channel>\S+)\s+(?P<can_id>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)\s*$"
)


@dataclass(frozen=True)
class CANFrame:
    timestamp: float
    channel: str
    arbitration_id: int
    data: bytes

    @property
    def dlc(self) -> int:
        return len(self.data)

    def to_dict(self) -> dict:
        result = asdict(self)
        result["data"] = self.data.hex().upper()
        result["arbitration_id_hex"] = f"0x{self.arbitration_id:X}"
        result["dlc"] = self.dlc
        return result


def parse_candump_line(line: str) -> CANFrame | None:
    match = CANDUMP.match(line)
    if not match:
        return None
    payload = match.group("data")
    if len(payload) % 2:
        raise ValueError(f"Odd-length CAN payload: {payload}")
    return CANFrame(
        timestamp=float(match.group("timestamp")),
        channel=match.group("channel"),
        arbitration_id=int(match.group("can_id"), 16),
        data=bytes.fromhex(payload),
    )


def read_candump(path: Path):
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            frame = parse_candump_line(line)
            if frame is None:
                raise ValueError(f"Invalid candump line {number}: {line.rstrip()}")
            yield frame


def read_can_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            identifier = str(row.get("arbitration_id", row.get("can_id", ""))).strip()
            yield CANFrame(
                timestamp=float(row["timestamp"]),
                channel=row.get("channel", "can0"),
                arbitration_id=int(identifier, 0) if identifier.lower().startswith("0x") else int(identifier, 16),
                data=bytes.fromhex(str(row["data"]).replace(" ", "")),
            )

