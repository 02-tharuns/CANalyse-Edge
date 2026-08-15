"""Deterministic, imperfect industrial-pump CAN simulator for the demo."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import cantools


FAULTS = ("healthy", "bearing_degradation", "cooling_restriction", "undervoltage")


@dataclass(frozen=True)
class SimulationResult:
    log_path: Path
    labels_path: Path
    samples: int


def simulate_session(dbc_path: Path, log_path: Path, labels_path: Path, *, session: int = 1,
                     duration_s: float = 120.0, sample_hz: float = 10.0,
                     fault: str = "bearing_degradation") -> SimulationResult:
    if fault not in FAULTS:
        raise ValueError(f"Unknown fault: {fault}")
    database = cantools.database.load_file(dbc_path)
    drive = database.get_message_by_name("DriveUnitStatus")
    fluid = database.get_message_by_name("FluidStatus")
    rng = np.random.default_rng(4100 + session)
    asset_sensitivity = rng.uniform(0.55, 1.25)
    calibration = {
        "current": rng.uniform(-5.5, 5.5),
        "temperature": rng.uniform(-7.5, 7.5),
        "vibration_scale": rng.uniform(0.55, 1.60),
        "voltage": rng.uniform(-1.55, 1.55),
        "outlet": rng.uniform(-1.1, 1.1),
        "flow": rng.uniform(-6.5, 6.5),
    }
    total = int(duration_s * sample_hz)
    timestamps = np.arange(total) / sample_hz + 1_720_000_000 + session * 1000
    fault_start = int(total * 0.58)
    labels = []
    lines = []

    for index, timestamp in enumerate(timestamps):
        load = 0.55 + 0.22 * np.sin(index / 75) + rng.normal(0, 0.035)
        active_fault = fault if index >= fault_start else "healthy"
        severity = max(0.0, (index - fault_start) / max(total - fault_start, 1))
        command = 2800 + 850 * load + rng.normal(0, 22)
        speed = command + rng.normal(0, 32)
        current = 32 + 24 * load + calibration["current"] + rng.normal(0, 2.8)
        temperature = 66 + 13 * load + calibration["temperature"] + rng.normal(0, 1.4)
        vibration = (0.42 + 0.18 * load + abs(rng.normal(0, 0.10))) * calibration["vibration_scale"]
        voltage = 24.2 + calibration["voltage"] + rng.normal(0, 0.24)
        inlet = 2.1 + rng.normal(0, 0.07)
        outlet = 7.8 + 2.1 * load + calibration["outlet"] + rng.normal(0, 0.19)
        flow = 44 + 18 * load + calibration["flow"] + rng.normal(0, 1.8)

        # Harmless process transients make normal/fault classes overlap, as they
        # do in real operating data, and prevent a suspiciously perfect demo.
        if rng.random() < 0.035:
            vibration += rng.uniform(0.35, 1.2)
            current += rng.uniform(1.0, 7.0)
        if rng.random() < 0.025:
            voltage -= rng.uniform(0.25, 1.0)
            temperature += rng.uniform(0.5, 3.5)

        # Fault effects deliberately overlap normal load/noise, avoiding toy-perfect separation.
        if active_fault == "bearing_degradation":
            vibration += asset_sensitivity * (0.12 + 1.35 * severity) + rng.normal(0, 0.32)
            current += asset_sensitivity * 4.0 * severity + rng.normal(0, 3.0)
            speed -= asset_sensitivity * 55 * severity
        elif active_fault == "cooling_restriction":
            temperature += asset_sensitivity * (0.8 + 10 * severity) + rng.normal(0, 2.4)
            flow -= asset_sensitivity * (0.8 + 8 * severity)
            outlet += asset_sensitivity * (0.15 + 1.1 * severity)
        elif active_fault == "undervoltage":
            voltage -= asset_sensitivity * (0.25 + 2.2 * severity) + rng.normal(0, 0.48)
            current += asset_sensitivity * (0.4 + 3.0 * severity)
            speed -= asset_sensitivity * (12 + 75 * severity)

        drive_data = drive.encode({
            "MotorSpeed": np.clip(speed, 0, 16000),
            "MotorCurrent": np.clip(current, 0, 1000),
            "CoolantTemperature": np.clip(temperature, -40, 215),
            "VibrationRms": np.clip(vibration, 0, 12.75),
            "SupplyVoltage": np.clip(voltage, 0, 655.35),
        }, strict=False)
        fluid_data = fluid.encode({
            "InletPressure": np.clip(inlet, 0, 655.35),
            "OutletPressure": np.clip(outlet, 0, 655.35),
            "FlowRate": np.clip(flow, 0, 6553.5),
            "CommandedSpeed": np.clip(command, 0, 16000),
        }, strict=False)
        lines.append(f"({timestamp:.6f}) can0 100#{drive_data.hex().upper()}")
        lines.append(f"({timestamp + 0.004:.6f}) can0 101#{fluid_data.hex().upper()}")
        labels.append({"timestamp": timestamp, "label": active_fault, "session": session})

    log_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(labels).to_csv(labels_path, index=False)
    return SimulationResult(log_path, labels_path, total)
