from pathlib import Path
import cantools

from canalyse.canio import CANFrame
from canalyse.decoder import DBCDecoder

ROOT = Path(__file__).resolve().parents[1]


def test_demo_dbc_round_trip():
    database = cantools.database.load_file(ROOT / "dbc" / "demo_equipment.dbc")
    message = database.get_message_by_name("DriveUnitStatus")
    payload = message.encode({"MotorSpeed": 3000, "MotorCurrent": 42, "CoolantTemperature": 72,
                              "VibrationRms": 0.8, "SupplyVoltage": 24.1})
    values = DBCDecoder(ROOT / "dbc" / "demo_equipment.dbc").decode(CANFrame(1.0, "can0", 0x100, payload))
    decoded = {item.signal: item.value for item in values}
    assert decoded["MotorSpeed"] == 3000
    assert abs(decoded["SupplyVoltage"] - 24.1) < 0.01
