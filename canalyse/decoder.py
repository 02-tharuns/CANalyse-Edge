"""DBC-backed conversion from CAN frames to engineering signals."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import cantools

from .canio import CANFrame


@dataclass(frozen=True)
class SignalValue:
    timestamp: float
    component: str
    message: str
    signal: str
    value: float | str
    unit: str | None
    arbitration_id: int
    frame_data: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "component": self.component,
            "message": self.message,
            "signal": self.signal,
            "value": self.value,
            "unit": self.unit,
            "arbitration_id": self.arbitration_id,
            "arbitration_id_hex": f"0x{self.arbitration_id:X}",
            "frame_data": self.frame_data,
        }


class DBCDecoder:
    def __init__(self, dbc_path: Path, component: str = "drive_unit"):
        self.database = cantools.database.load_file(dbc_path)
        self.component = component

    def decode(self, frame: CANFrame) -> list[SignalValue]:
        try:
            message = self.database.get_message_by_frame_id(frame.arbitration_id)
        except KeyError:
            return []
        decoded = message.decode(frame.data, decode_choices=False, allow_truncated=False)
        units = {signal.name: signal.unit for signal in message.signals}
        return [
            SignalValue(frame.timestamp, self.component, message.name, name, value,
                        units.get(name), frame.arbitration_id, frame.data.hex().upper())
            for name, value in decoded.items()
        ]

    def decode_many(self, frames):
        for frame in frames:
            yield from self.decode(frame)

