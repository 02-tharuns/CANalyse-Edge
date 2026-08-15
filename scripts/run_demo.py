from pathlib import Path
import json
from canalyse.pipeline import run_demo

ROOT = Path(__file__).resolve().parents[1]
print(json.dumps(run_demo(ROOT), indent=2))
