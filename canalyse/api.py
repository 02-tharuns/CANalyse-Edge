"""SOVD-inspired HTTP interface for the demo component."""
from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ROOT
from .pipeline import run_demo

app = FastAPI(
    title="CANalyse Edge API",
    version="0.1.0",
    description="Educational, SOVD-inspired diagnostic API. It is not ASAM SOVD compliant.",
)
dashboard = ROOT / "dashboard"
app.mount("/static", StaticFiles(directory=dashboard), name="static")


def _read_output(name: str):
    path = ROOT / "outputs" / name
    if not path.exists():
        run_demo(ROOT)
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(dashboard / "index.html")


@app.get("/api/health")
def service_health():
    return {"status": "ok", "service": "canalyse-edge", "version": app.version}


@app.get("/api/entities")
def entities():
    return [{"id": "demo-pump-line", "name": "Demo Pump Line", "type": "industrial_asset"}]


@app.get("/api/entities/{entity_id}/components")
def components(entity_id: str):
    if entity_id != "demo-pump-line":
        raise HTTPException(404, "Entity not found")
    return [{"id": "drive-unit-1", "name": "Pump drive unit", "capabilities": ["health", "faults", "data", "operations"]}]


@app.get("/api/components/{component_id}/health")
def component_health(component_id: str):
    if component_id != "drive-unit-1":
        raise HTTPException(404, "Component not found")
    return _read_output("latest_health.json")


@app.get("/api/components/{component_id}/faults")
def component_faults(component_id: str):
    health = component_health(component_id)
    if health["condition"] == "healthy":
        return []
    return [{
        "code": f"DEMO-{health['condition'].upper()}",
        "status": "active",
        "confidence": health["confidence"],
        "description": health["condition"].replace("_", " ").title(),
    }]


@app.get("/api/components/{component_id}/data")
def component_data(component_id: str):
    health = component_health(component_id)
    quality = _read_output("data_quality.json")
    return {"health": health, "quality": quality}


@app.post("/api/components/{component_id}/operations/recompute-health")
def recompute(component_id: str):
    if component_id != "drive-unit-1":
        raise HTTPException(404, "Component not found")
    return run_demo(ROOT)["health"]
