from canalyse.canio import CANFrame
from canalyse.quality import assess_frames


def test_quality_detects_gap_and_dlc_change():
    frames = [
        CANFrame(0.0, "can0", 0x100, b"12345678"),
        CANFrame(0.1, "can0", 0x100, b"12345678"),
        CANFrame(0.2, "can0", 0x100, b"short"),
        CANFrame(1.0, "can0", 0x100, b"12345678"),
    ]
    report = assess_frames(frames)[0]
    assert report.dlc_mismatches == 1
    assert report.large_gaps == 1
