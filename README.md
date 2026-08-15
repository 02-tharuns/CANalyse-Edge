# CANalyse Edge

CANalyse Edge turns raw CAN/CAN-FD-style logs into decoded engineering signals,
data-quality evidence, rolling ML features, component condition predictions,
and an **SOVD-inspired** diagnostic API. The included example models an
industrial pump drive unit and is designed as an achievable student project.



## What makes it different

Many CAN projects stop at message decoding. This one records the provenance and
quality of the data, creates explainable signal-window features, separates
recording sessions during validation, and exposes results as component health,
fault, data, and operation resources suitable for a service-oriented diagnostic
demo.

```text
candump / CSV / simulator
          ↓
frame parser → DBC decoder → timing & DLC quality checks
          ↓
rolling signal features → Random Forest condition model
          ↓
health score + fault candidate → FastAPI → browser dashboard
```

## Quick start (Windows PowerShell)

Python 3.12 is used and recorded in `.python-version`.

```powershell
cd "path\to\CANalyse-Edge"
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
.\Automoble\Scripts\Activate.ps1
python -m canalyse.pipeline
python run.py
```

Open <http://127.0.0.1:8080>. Interactive API documentation is at
<http://127.0.0.1:8080/docs>.

Run the checks with:

```powershell
python -m pytest
python -m pip check
```

## Honest evaluation

`python -m canalyse.pipeline` creates nine noisy simulated recording sessions.
Six whole sessions train the classifier and three unseen sessions test it. This
is stricter than randomly mixing neighboring windows, but the resulting metric
is still only a **synthetic smoke test**, not a real-world accuracy claim.

Generated files:

- `outputs/demo_metrics.json` — held-out synthetic metrics and confusion matrix
- `outputs/demo_predictions.csv` — window-level predicted and actual condition
- `outputs/latest_health.json` — API/dashboard state
- `outputs/data_quality.json` — CAN timing, DLC, and signal-range evidence
- `outputs/public_dataset_status.json` — verified source/download status; never fake metrics
- `models/condition_model.joblib` — generated locally and ignored by Git

## Public datasets

Run `python scripts/datasets.py list` for the curated sources. The registry
includes ReCAN, ROAD, Scania Component X, and Q-Motion. These datasets have
different purposes: ROAD is useful for CAN anomaly research but is not a
mechanical-failure dataset; Scania is useful for predictive maintenance but is
not raw CAN. Third-party files are not redistributed by this repository.

See [datasets/README.md](datasets/README.md) for the validation protocol.

## API shape

- `GET /api/entities`
- `GET /api/entities/demo-pump-line/components`
- `GET /api/components/drive-unit-1/health`
- `GET /api/components/drive-unit-1/faults`
- `GET /api/components/drive-unit-1/data`
- `POST /api/components/drive-unit-1/operations/recompute-health`

The naming follows SOVD concepts for a portfolio demonstration; standards
conformance, OAuth, roles, discovery, TLS, and full resource semantics remain
future work.

## CAN libraries

- [`python-can`](https://python-can.readthedocs.io/en/stable/bus.html) provides
  the common `Bus` API used later for SocketCAN, Vector, PCAN, virtual CAN, and
  other supported interfaces. Start hardware experiments in listen-only mode.
- [`cantools`](https://cantools.readthedocs.io/en/stable/) loads the DBC and
  converts frame payloads into named engineering values with units and scaling.



## Repository layout

```text
CANalyse-Edge/
├── canalyse/       Python ingestion, decoding, features, ML, API
├── dashboard/      Dependency-free browser UI
├── datasets/       Public-source registry and validation notes
├── dbc/            Demonstration equipment DBC
├── scripts/        Demo and dataset helper commands
├── tests/          Fast unit/integration checks
├── outputs/        Generated reports that may be showcased
└── data/generated/ Reproducible local simulator output (Git ignored)
```

## Roadmap

1. Validate parsing and timing on ReCAN recordings.
2. Benchmark a traffic-anomaly branch on ROAD without relabeling attacks as failures.
3. Add a separate Scania Component X tabular maintenance pipeline.
4. Connect SocketCAN or a USB CAN adapter in read-only mode.
5. Add model explanations, signed model versions, authentication, and audit logs.

## License

Code in this repository is MIT licensed. External datasets retain their own
terms and must be attributed separately.
