from pathlib import Path

from canalyse.canio import read_candump
from canalyse.decoder import DBCDecoder
from canalyse.features import signals_to_wide, window_features
from canalyse.simulator import simulate_session


def test_simulation_to_features(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    log = tmp_path / "trial.log"
    labels = tmp_path / "labels.csv"
    simulate_session(root / "dbc" / "demo_equipment.dbc", log, labels, duration_s=8)
    decoded = DBCDecoder(root / "dbc" / "demo_equipment.dbc").decode_many(read_candump(log))
    features = window_features(signals_to_wide(decoded), window_samples=20, step_samples=10)
    assert len(features) > 0
    assert "VibrationRms__rms" in features.columns
