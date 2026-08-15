"""Display public dataset sources without silently downloading large archives."""
from __future__ import annotations

import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["list"])
    args = parser.parse_args()
    registry = yaml.safe_load((ROOT / "datasets" / "registry.yaml").read_text(encoding="utf-8"))
    if args.command == "list":
        for dataset in registry["datasets"]:
            size = f" (~{dataset['approximate_size_mb']} MB)" if "approximate_size_mb" in dataset else ""
            print(f"{dataset['id']}: {dataset['name']}{size}\n  {dataset['url']}\n  Use: {dataset['use']}\n")


if __name__ == "__main__":
    main()
