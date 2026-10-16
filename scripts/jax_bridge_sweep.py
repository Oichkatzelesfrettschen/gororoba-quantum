"""JAX bridge sweep: exact model probabilities of retained replicas across the error-scale grid, on a chosen JAX device.

For every retained run and member, under the snapshot in force when its PUB
began (ghost_run.prepare), each replica whose measurements are all terminal
is exported once per CZ factor of scripts/ghost_error_scale.py
(gororoba_quantum/jax_bridge.export on ghost_error_scale.scaled), and the
ten programs replay as one batched JAX call on the requested device. The
readout factors act on the resulting register diagonal classically, with the
same cap as ghost_error_scale.flip, so each replica yields the exact model
distribution at all fifty grid points and its TV distance to the hardware
distribution retained in collect.json. These distances carry hardware shot
noise only; the ghost sweep's sampled distances also carry the model draw,
so the two estimators are reported side by side and never merged.

Before its distances count, every replica's factor-1 program is compared
with Aer's own density matrix (calibration_snapshot.noise_simulator with
save_density_matrix in place of the terminal measurements) on the CPU, and
the largest probability difference is recorded per run. Replicas with
reset, mid-circuit measurement or classical control are listed as skipped
with the reason. ``--device`` names the JAX platform the replay must use
(cpu, gpu or tpu); a missing platform raises instead of falling back, and
the output records the platform of every result array.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale  # noqa: E402
import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402

import calibration_snapshot  # noqa: E402
import jax_bridge  # noqa: E402

SCHEMA = "jax-bridge-sweep-v1"


def aer_probabilities(circuit: QuantumCircuit, program: jax_bridge.Program, snapshot: dict[str, Any]) -> np.ndarray:
    """Aer's density matrix on the program's qubits, with the terminal measurements replaced by save_density_matrix."""
    body = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    for instruction in circuit.data:
        if instruction.operation.name != "measure":
            body.append(instruction.operation, instruction.qubits, instruction.clbits)
    body.save_density_matrix(qubits=[body.qubits[q] for q in program.physical])
    simulator = calibration_snapshot.noise_simulator(snapshot, "CPU")
    rho = np.asarray(simulator.run(body, shots=1).result().data(0)["density_matrix"])
    return jax_bridge.probabilities(program, np.diag(rho))


def sweep_run(run_name: str, device: Any, index: dict[str, Any], evolvers: dict[Any, Any]) -> dict[str, Any]:
    import jax

    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    noise: dict[tuple[str, float], Any] = {}
    snapshots: dict[str, dict[str, Any]] = {}
    tvd: dict[str, list[list[list[float]]]] = {}
    skipped: dict[str, str] = {}
    parity = 0.0
    platforms: set[str] = set()
    seconds = {"export": 0.0, "parity": 0.0, "replay": 0.0}
    for m in members:
        relative = execution[m]
        snapshot = snapshots.setdefault(relative, json.loads((ROOT / relative).read_text(encoding="utf-8")))
        rows = []
        for k, replica in enumerate(prepared["replicas"][m][1]):
            start = time.perf_counter()
            programs = []
            try:
                for c in ghost_error_scale.CZ_FACTORS:
                    if (relative, c) not in noise:
                        noise[(relative, c)] = calibration_snapshot.noise_model(
                            ghost_error_scale.scaled(snapshot, c, 1.0)
                        )[1]
                    programs.append(jax_bridge.export(replica, noise[(relative, c)]))
            except jax_bridge.UnsupportedCircuit as reason:
                skipped[f"{m}#{k}"] = str(reason)
                continue
            seconds["export"] += time.perf_counter() - start
            stacked = jax_bridge.stack_programs(programs)
            if stacked:
                key = (tuple(programs[0].structure()), programs[0].n)
                if key not in evolvers:
                    evolvers[key] = jax_bridge.make_jax_evolver(programs[0].structure(), programs[0].n)
                start = time.perf_counter()
                arrays = [jax.device_put(kraus.astype(np.complex64), device) for _, kraus in stacked]
                replayed = evolvers[key](arrays).block_until_ready()
                seconds["replay"] += time.perf_counter() - start
                platforms.update(d.platform for d in replayed.devices())
                diagonals = np.asarray(replayed, dtype=np.float64)
            else:
                # A replica that only measures leaves |0...0> unchanged; readout alone acts.
                diagonals = np.zeros((len(programs), 2 ** programs[0].n))
                diagonals[:, 0] = 1.0
            base = ghost_error_scale.CZ_FACTORS.index(1.0)
            start = time.perf_counter()
            reference = aer_probabilities(replica, programs[base], snapshot)
            parity = max(
                parity, float(np.max(np.abs(jax_bridge.probabilities(programs[base], diagonals[base]) - reference)))
            )
            seconds["parity"] += time.perf_counter() - start
            measured = prepared["measured"][m][k]
            rows.append(
                [
                    [
                        round(ghost_run.tv(measured, jax_bridge.probabilities(program, diagonal, readout_scale=r)), 6)
                        for r in ghost_error_scale.READOUT_FACTORS
                    ]
                    for program, diagonal in zip(programs, diagonals, strict=True)
                ]
            )
        if rows:
            tvd[m] = rows
    grid = np.array([cell for rows in tvd.values() for cell in rows]) if tvd else np.zeros((0,))
    means = grid.mean(axis=0).round(6).tolist() if grid.size else None
    print(
        json.dumps({"run": run_name, "replicas": int(grid.shape[0]) if grid.size else 0, "parity": parity}), flush=True
    )
    return {
        "run": run_name,
        "backend": prepared["backend"],
        "execution_snapshot": {m: execution[m] for m in tvd},
        "member_shots": {m: prepared["shots"][m] for m in tvd},
        "skipped_replicas": skipped,
        "max_abs_probability_minus_aer": parity,
        "result_platforms": sorted(platforms),
        "seconds": {k: round(v, 2) for k, v in seconds.items()},
        "mean_tvd": means,
        "tvd": tvd,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--device", required=True, choices=("cpu", "gpu", "tpu"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    import jax

    device = jax.devices(args.device)[0]
    versions: dict[str, str | None] = {}
    for name in ("jax", "jaxlib", "libtpu", "qiskit", "qiskit-aer", "qiskit-aer-gpu-cu11"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": {"requested": args.device, "selected": str(device), "kind": getattr(device, "device_kind", None)},
        "visible_devices": [str(d) for d in jax.devices(args.device)],
        "grid": {"cz": list(ghost_error_scale.CZ_FACTORS), "readout": list(ghost_error_scale.READOUT_FACTORS)},
        "precision": "complex64 storage, Precision.HIGHEST contractions",
        "versions": versions,
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    evolvers: dict[Any, Any] = {}
    for run in runs:
        out["runs"].append(sweep_run(run, device, index, evolvers))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
