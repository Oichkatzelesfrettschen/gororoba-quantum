"""Substrate crossover: Aer density-matrix wall time on CPU and GPU by active width, under calibrated noise.

The workload is the shape retained IBM jobs have: ISA circuits on a
connected chain of physical qubits of a full-width backend, layers of rz
and sx on every chain qubit followed by CZ on alternating chain pairs, then
a measurement of every chain qubit. The dynamic variant adds one mid-circuit
measurement of the first chain qubit and an X conditioned on it, which makes
Aer simulate shot by shot. Noise is gororoba_quantum/calibration_snapshot's
rebuild of live_run's model from the retained export
docs/evidence/calibration/ibm_kingston.json.

For every available device (CPU always, GPU when nvidia-smi lists one) and
workload it records the noise-model build once, then the run of BATCH
circuits at SHOTS shots per width, best of REPEATS. Once a width exceeds
BUDGET_SECONDS on a device and workload, the wider widths there are not run
and record why. The output names the machine (CPU model, cores, GPU) so a
row is read against the substrate that produced it.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister  # noqa: E402

import calibration_snapshot  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
WIDTHS = (2, 4, 6, 8, 10, 12, 14)
LAYERS = 8
BATCH = 8
SHOTS = 2048
REPEATS = 2
BUDGET_SECONDS = 180.0
SEED = 20261016


def chain(snapshot: dict[str, Any], width: int) -> list[int]:
    """A path of width physical qubits along CZ couplers with a reported error below 1, by depth-first search."""
    edges: dict[int, set[int]] = {}
    for entry in snapshot["instructions"]["cz"]:
        if entry["error"] is not None and entry["error"] < 1.0:
            a, b = entry["qargs"]
            edges.setdefault(a, set()).add(b)
            edges.setdefault(b, set()).add(a)

    def extend(path: list[int]) -> list[int] | None:
        if len(path) == width:
            return path
        for nxt in sorted(edges.get(path[-1], ())):
            if nxt not in path and (found := extend([*path, nxt])) is not None:
                return found
        return None

    for start in sorted(edges):
        if (found := extend([start])) is not None:
            return found
    raise SystemExit(f"no {width}-qubit chain of working couplers")


def circuits(snapshot: dict[str, Any], width: int, dynamic: bool) -> list[QuantumCircuit]:
    """BATCH seeded circuits on the chain, as full-width ISA circuits like the retained replicas."""
    qubits = chain(snapshot, width)
    rng = np.random.default_rng(SEED + width)
    out = []
    for k in range(BATCH):
        register = QuantumRegister(snapshot["num_qubits"], "q")
        bits = ClassicalRegister(width, "c")
        circuit = QuantumCircuit(register, bits, name=f"w{width}-{k}")
        if dynamic:
            flag = ClassicalRegister(1, "flag")
            circuit.add_register(flag)
        for layer in range(LAYERS):
            for q in qubits:
                circuit.rz(float(rng.uniform(0, 2 * np.pi)), register[q])
                circuit.sx(register[q])
            for a, b in zip(qubits[layer % 2 :: 2], qubits[layer % 2 + 1 :: 2], strict=False):
                circuit.cz(register[a], register[b])
            if dynamic and layer == LAYERS // 2:
                circuit.measure(register[qubits[0]], flag[0])
                with circuit.if_test((flag, 1)):
                    circuit.x(register[qubits[0]])
        for position, q in enumerate(qubits):
            circuit.measure(register[q], bits[position])
        out.append(circuit)
    return out


def gpu_names() -> list[str]:
    if shutil.which("nvidia-smi") is None:
        return []
    listing = subprocess.run(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True, check=False
    )
    return [line.strip() for line in listing.stdout.splitlines() if line.strip()]


def cpu_model() -> str | None:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def measure(snapshot: dict[str, Any], device: str, dynamic: bool) -> dict[str, Any]:
    start = time.perf_counter()
    simulator = calibration_snapshot.noise_simulator(snapshot, device)
    build = time.perf_counter() - start
    rows: list[dict[str, Any]] = []
    skipped_after: float | None = None
    for width in WIDTHS:
        if skipped_after is not None:
            rows.append({"width": width, "not_run": f"the previous width took {skipped_after:.1f} s"})
            continue
        batch = circuits(snapshot, width, dynamic)
        times = []
        for repeat in range(REPEATS):
            start = time.perf_counter()
            simulator.run(batch, shots=SHOTS, seed_simulator=SEED + repeat).result()
            times.append(time.perf_counter() - start)
        best = min(times)
        rows.append({"width": width, "seconds": round(best, 3), "seconds_per_circuit": round(best / BATCH, 4)})
        print(json.dumps({"device": device, "dynamic": dynamic, **rows[-1]}), flush=True)
        if best > BUDGET_SECONDS:
            skipped_after = best
    return {"noise_model_build_seconds": round(build, 3), "widths": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    devices = ["CPU"] + (["GPU"] if gpu_names() else [])
    out: dict[str, Any] = {
        "schema": "substrate-crossover-v1",
        "machine": {
            "cpu": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "gpus": gpu_names(),
            "python": platform.python_version(),
        },
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "snapshot": SNAPSHOT.relative_to(ROOT).as_posix(),
        "workload": {"layers": LAYERS, "batch": BATCH, "shots": SHOTS, "repeats": REPEATS, "budget": BUDGET_SECONDS},
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for dynamic in (False, True):
        for device in devices:
            out["runs"].append({"device": device, "dynamic": dynamic, **measure(snapshot, device, dynamic)})
            args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
