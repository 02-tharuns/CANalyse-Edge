from canalyse.canio import parse_candump_line


def test_parse_candump():
    frame = parse_candump_line("(1720000000.125000) can0 100#01020304")
    assert frame is not None
    assert frame.arbitration_id == 0x100
    assert frame.data == bytes.fromhex("01020304")


def test_ignore_non_candump_line():
    assert parse_candump_line("not a frame") is None
