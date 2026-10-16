"""Aer device and sampler timings for small noisy dynamic circuits on one Kaggle machine.

Each configuration samples the same compiled circuits under one retained
calibration snapshot's noise (calibration_snapshot.noise_simulator):

  cpu_statevector       statevector trajectories on every host CPU
  cpu_density_matrix    the exact channel per shot on every host CPU
  gpu_statevector       statevector trajectories, one GPU kernel per shot
  gpu_statevector_batch the same with Aer's batched_shots_gpu
  gpu_density_matrix_batch the exact channel with batched_shots_gpu

The circuits are the N=21 order-finding workloads of
scripts/n21_conjugation_noise.py under the work-register encoding of
coset 281 (columns 1, 2, 5, 13, 25): the two-round diagnostic with
feed-forward (7 qubits, one mid-circuit measurement and if_else) and the
ten-round circuit (7 qubits, nine). Every configuration reports wall seconds
per shot, and its two-round labeled distribution's total variation from
cpu_statevector, against the binomial sampling scale of the two shot counts.
A configuration that would exceed its time budget at full shots runs a
reduced shot count, which the record states. GPU configurations are skipped
on a machine without a GPU.

Usage:
    "$PYTHON" scripts/aer_gpu_probe.py --snapshot SNAP.json --out PATH
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from n21_conjugation_noise import _backend, circuits  # noqa: E402
from qiskit.transpiler import generate_preset_pass_manager  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

COLUMNS = (1, 2, 5, 13, 25)
SEED = 20261016
FULL_SHOTS = {"two_round_encoded_ff": 32768, "ten_round_encoded": 8192}
PILOT_SHOTS = 32
# Wall-time budget per configuration and circuit; a slower configuration
# runs the shot count the pilot predicts fits it.
BUDGET_SECONDS = 240.0
CONFIGURATIONS = {
    "cpu_statevector": ("CPU", "statevector", False),
    "cpu_density_matrix": ("CPU", "density_matrix", False),
    "gpu_statevector": ("GPU", "statevector", False),
    "gpu_statevector_batch": ("GPU", "statevector", True),
    "gpu_density_matrix_batch": ("GPU", "density_matrix", True),
}


def gpu_count() -> int:
    try:
        listing = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, check=False).stdout
    except FileNotFoundError:
        return 0
    return sum(line.startswith("GPU ") for line in listing.splitlines())


def labeled(counts: dict[str, int]) -> list[float]:
    shots = sum(counts.values())
    distribution = [0.0] * 4
    for key, count in counts.items():
        distribution[int(key.replace(" ", ""), 2)] += count / shots
    return distribution


def sample(simulator: Any, isa: Any, shots: int) -> tuple[dict[str, int], float, dict[str, Any]]:
    started = time.perf_counter()
    result = simulator.run(isa, shots=shots, seed_simulator=SEED).result()
    seconds = time.perf_counter() - started
    metadata = result.results[0].metadata
    keys = ("method", "device", "batched_shots_optimization", "num_bind_params", "parallel_shots")
    return result.get_counts(), seconds, {key: metadata[key] for key in keys if key in metadata}


def planned_shots(simulator: Any, isa: Any, full: int) -> int:
    """Escalating pilots until the per-shot time is measured on enough shots to fit the budget."""
    trial = PILOT_SHOTS
    while True:
        _, seconds, _ = sample(simulator, isa, trial)
        per_shot = seconds / trial
        if per_shot * full <= BUDGET_SECONDS:
            return full
        larger = min(full, int(BUDGET_SECONDS / 4 / per_shot))
        if larger <= 2 * trial:
            return max(trial, int(BUDGET_SECONDS / per_shot))
        trial = larger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    backend = _backend(snapshot)
    built = circuits(COLUMNS, COLUMNS)
    gpus = gpu_count()
    rows = []
    reference: dict[str, list[float]] = {}
    for name, full in FULL_SHOTS.items():
        compiled = generate_preset_pass_manager(optimization_level=3, target=backend.target, seed_transpiler=0).run(
            built[name]
        )
        isa, qubits = snapshot_laws.restrict_circuit(compiled)
        reduced = snapshot_laws.restrict(snapshot, qubits)
        for label, (device, method, batched) in CONFIGURATIONS.items():
            if device == "GPU" and gpus == 0:
                rows.append({"circuit": name, "configuration": label, "skipped": "no GPU on this machine"})
                continue
            simulator = calibration_snapshot.noise_simulator(reduced, device, method=method, batched_shots=batched)
            simulator.set_options(max_parallel_threads=parallel.workers())
            shots = planned_shots(simulator, isa, full)
            counts, seconds, metadata = sample(simulator, isa, shots)
            row: dict[str, Any] = {
                "circuit": name,
                "configuration": label,
                "device": device,
                "method": method,
                "batched_shots_gpu": batched,
                "shots": shots,
                "reduced": shots < full,
                "seconds": round(seconds, 3),
                "microseconds_per_shot": round(1e6 * seconds / shots, 2),
                "routed_cz": int(isa.count_ops().get("cz", 0)),
                "metadata": metadata,
            }
            if name.startswith("two_round"):
                distribution = labeled(counts)
                if label == "cpu_statevector":
                    reference = {"distribution": distribution, "shots": [shots]}
                row["distribution"] = distribution
                if reference:
                    row["tvd_to_cpu_statevector"] = 0.5 * sum(
                        abs(a - b) for a, b in zip(distribution, reference["distribution"], strict=True)
                    )
                    # Four outcomes: the expected total variation of two
                    # independent samples is of order sqrt(2 / shots).
                    row["sampling_scale"] = math.sqrt(1 / shots + 1 / reference["shots"][0])
            rows.append(row)
            print(json.dumps({key: row[key] for key in ("circuit", "configuration", "shots", "microseconds_per_shot")}))
    record = {
        "schema": "aer-gpu-probe-v1",
        "snapshot": str(args.snapshot),
        "calibration": snapshot["calibration"],
        "gpus": gpus,
        "workers": parallel.workers(),
        "columns": list(COLUMNS),
        "budget_seconds": BUDGET_SECONDS,
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
