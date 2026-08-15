# Public-data validation

The project does not commit third-party datasets. Their size, licensing, and
attribution requirements differ, so downloads live under `data/downloads/`,
which Git ignores.

Use `python scripts/datasets.py list` to see the curated registry. Download a
dataset from its publisher, read its license, then place it below
`data/downloads/<dataset-id>/`.

Each dataset has a distinct role:

- **ReCAN** checks raw parsing, timing, DBC decoding, and data-quality behavior.
- **ROAD** benchmarks anomalous CAN traffic. Its attacks must not be described
  as mechanical equipment failures.
- **Scania Component X** supports real predictive-maintenance research, but its
  operational tables are not raw CAN frames.
- **Q-Motion** provides CAN and motion telemetry for additional experiments.

Report results per dataset and keep vehicle/session groups separated between
training and testing. Never mix windows from the same recording across both.
