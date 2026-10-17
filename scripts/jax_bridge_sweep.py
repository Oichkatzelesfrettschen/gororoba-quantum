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
the largest probability difference is recorded per run. A replica whose
difference exceeds PARITY_TOLERANCE is listed as skipped with the gap, its
distances do not count, and the script exits 1. Replicas with reset,
mid-circuit measurement or classical control are listed as skipped with the
reason. The export of each replica at each CZ factor and the Aer reference
of each replica are independent CPU-bound items and run through
parallel.ordered_map, each worker keeping the noise models and simulators it
builds; the batched JAX replay stays in the parent process on the requested
device. ``--device`` names the JAX platform the replay must use
(cpu, gpu or tpu); a missing platform raises instead of falling back, and
the output records the platform of every result array.
"""

from __future__ import annotations

import argparse
import hashlib
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
import parallel  # noqa: E402

SCHEMA = "jax-bridge-sweep-v1"
# Largest admitted |p_JAX - p_Aer| over the factor-1 distribution. Aer evolves
# in complex128 while the JAX replay stores complex64 (unit roundoff 2^-24,
# about 6e-8) and contracts at Precision.HIGHEST, so its rounding grows with
# the op count from that floor; 1e-5 leaves two orders of magnitude above the
# complex64 floor and still fails an export, ordering or readout defect, which
# moves probabilities by far more.
PARITY_TOLERANCE = 1e-5
# An export or Aer reference runs for about a second and each noise model or
# simulator build for over ten, so two items already repay the pool transfer.
MIN_PARALLEL_ITEMS = 2
SELF_TEST_RUN = "results/live/2026-10-13T032011.664435Z"
SELF_TEST_REPLICAS = 4


def aer_probabilities(circuit: QuantumCircuit, program: jax_bridge.Program, simulator: Any) -> np.ndarray:
    """Aer's density matrix on the program's qubits, with the terminal measurements replaced by save_density_matrix."""
    body = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    for instruction in circuit.data:
        if instruction.operation.name != "measure":
            body.append(instruction.operation, instruction.qubits, instruction.clbits)
    body.save_density_matrix(qubits=[body.qubits[q] for q in program.physical])
    rho = np.asarray(simulator.run(body, shots=1).result().data(0)["density_matrix"])
    return jax_bridge.probabilities(program, np.diag(rho))


class SnapshotStage:
    """A pool stage over a run's snapshots: only the snapshots pickle, and each
    process builds an Aer object on first use and keeps it for later items."""

    def __init__(self, snapshots: dict[str, dict[str, Any]]) -> None:
        self.snapshots = snapshots
        self._built: dict[Any, Any] = {}

    def __getstate__(self) -> dict[str, Any]:
        return {"snapshots": self.snapshots}

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.snapshots = state["snapshots"]
        self._built = {}


class ExportAt(SnapshotStage):
    """jax_bridge.export of one replica at one CZ factor, or the UnsupportedCircuit reason."""

    def __call__(self, item: tuple[str, float, QuantumCircuit]) -> jax_bridge.Program | str:
        relative, factor, replica = item
        if (relative, factor) not in self._built:
            scaled = ghost_error_scale.scaled(self.snapshots[relative], factor, 1.0)
            self._built[(relative, factor)] = calibration_snapshot.noise_model(scaled)[1]
        try:
            return jax_bridge.export(replica, self._built[(relative, factor)])
        except jax_bridge.UnsupportedCircuit as reason:
            return str(reason)


class AerReference(SnapshotStage):
    """Aer's factor-1 distribution of one replica under its snapshot's noise simulator."""

    def __call__(self, item: tuple[str, QuantumCircuit, jax_bridge.Program]) -> np.ndarray:
        relative, replica, program = item
        if relative not in self._built:
            self._built[relative] = calibration_snapshot.noise_simulator(self.snapshots[relative], "CPU")
        return aer_probabilities(replica, program, self._built[relative])


def export_replicas(
    snapshots: dict[str, dict[str, Any]], items: list[tuple[str, QuantumCircuit]], factors: tuple[float, ...]
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """Programs at every factor and the factor-1 Aer reference of each (snapshot, replica), or its skip reason.

    The export items run factor-major, so a contiguous chunk of the pool
    mostly shares one noise model and a worker builds few of them; the Aer
    references then run with one simulator per snapshot per worker.
    """
    start = time.perf_counter()
    flat = parallel.ordered_map(
        ExportAt(snapshots),
        [(relative, c, replica) for c in factors for relative, replica in items],
        MIN_PARALLEL_ITEMS,
    )
    exported = time.perf_counter()
    base = factors.index(1.0)
    results: list[dict[str, Any]] = []
    for i in range(len(items)):
        programs = [flat[f * len(items) + i] for f in range(len(factors))]
        reasons = [p for p in programs if isinstance(p, str)]
        results.append({"skipped": reasons[0]} if reasons else {"programs": programs})
    supported = [(i, r) for i, r in enumerate(results) if "programs" in r]
    references = parallel.ordered_map(
        AerReference(snapshots),
        [(items[i][0], items[i][1], r["programs"][base]) for i, r in supported],
        MIN_PARALLEL_ITEMS,
    )
    for (_, r), reference in zip(supported, references, strict=True):
        r["reference"] = reference
    return results, {"export": exported - start, "parity": time.perf_counter() - exported}


def parity_failure(gap: float) -> str | None:
    """The skip reason of a replica whose factor-1 distribution differs from Aer's by more than PARITY_TOLERANCE."""
    if gap > PARITY_TOLERANCE:
        return f"factor-1 probabilities differ from Aer by {gap:.3g} > {PARITY_TOLERANCE:g}"
    return None


def replay(programs: list[jax_bridge.Program], device: Any, evolvers: dict[Any, Any]) -> tuple[np.ndarray, set[str]]:
    """Register diagonals of every program from one batched JAX call on device, and the result platforms."""
    import jax

    stacked = jax_bridge.stack_programs(programs)
    if not stacked:
        # A replica that only measures leaves |0...0> unchanged; readout alone acts.
        diagonals = np.zeros((len(programs), 2 ** programs[0].n))
        diagonals[:, 0] = 1.0
        return diagonals, set()
    key = (tuple(programs[0].structure()), programs[0].n)
    if key not in evolvers:
        evolvers[key] = jax_bridge.make_jax_evolver(programs[0].structure(), programs[0].n)
    arrays = [jax.device_put(kraus.astype(np.complex64), device) for _, kraus in stacked]
    replayed = evolvers[key](arrays).block_until_ready()
    return np.asarray(replayed, dtype=np.float64), {d.platform for d in replayed.devices()}


def sweep_run(run_name: str, device: Any, index: dict[str, Any], evolvers: dict[Any, Any]) -> dict[str, Any]:
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    snapshots: dict[str, dict[str, Any]] = {}
    for m in members:
        relative = execution[m]
        snapshots.setdefault(relative, json.loads((ROOT / relative).read_text(encoding="utf-8")))
    keys = [(m, k) for m in members for k in range(len(prepared["replicas"][m][1]))]
    exports, seconds = export_replicas(
        snapshots, [(execution[m], prepared["replicas"][m][1][k]) for m, k in keys], ghost_error_scale.CZ_FACTORS
    )
    seconds["replay"] = 0.0
    base = ghost_error_scale.CZ_FACTORS.index(1.0)
    tvd: dict[str, list[list[list[float]]]] = {}
    skipped: dict[str, str] = {}
    parity = 0.0
    platforms: set[str] = set()
    for (m, k), exported in zip(keys, exports, strict=True):
        if "skipped" in exported:
            skipped[f"{m}#{k}"] = exported["skipped"]
            continue
        programs = exported["programs"]
        start = time.perf_counter()
        diagonals, used = replay(programs, device, evolvers)
        seconds["replay"] += time.perf_counter() - start
        platforms.update(used)
        replayed = jax_bridge.probabilities(programs[base], diagonals[base])
        gap = float(np.max(np.abs(replayed - exported["reference"])))
        parity = max(parity, gap)
        reason = parity_failure(gap)
        if reason is not None:
            skipped[f"{m}#{k}"] = reason
            continue
        measured = prepared["measured"][m][k]
        tvd.setdefault(m, []).append(
            [
                [
                    round(ghost_run.tv(measured, jax_bridge.probabilities(program, diagonal, readout_scale=r)), 6)
                    for r in ghost_error_scale.READOUT_FACTORS
                ]
                for program, diagonal in zip(programs, diagonals, strict=True)
            ]
        )
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


def self_test() -> int:
    """Factor-1 exports of retained replicas meet PARITY_TOLERANCE in numpy complex128 against Aer.

    The printed digest covers every Kraus stack and Aer reference, so runs
    under GOROROBA_WORKERS=1 and the default pool print the same digest.
    """
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    prepared = ghost_run.prepare(SELF_TEST_RUN, index)
    ghost_run.require("skipped" not in prepared, f"{SELF_TEST_RUN}: {prepared.get('skipped')}")
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution][:SELF_TEST_REPLICAS]
    snapshots = {execution[m]: json.loads((ROOT / execution[m]).read_text(encoding="utf-8")) for m in members}
    results, _ = export_replicas(snapshots, [(execution[m], prepared["replicas"][m][1][0]) for m in members], (1.0,))
    digest = hashlib.sha256()
    for m, result in zip(members, results, strict=True):
        ghost_run.require("programs" in result, f"{m}: {result.get('skipped')}")
        (program,) = result["programs"]
        numpy_replay = jax_bridge.probabilities(program, np.diag(jax_bridge.evolve_numpy(program)))
        gap = float(np.max(np.abs(numpy_replay - result["reference"])))
        ghost_run.require(parity_failure(gap) is None, f"{m}: numpy complex128 replay differs from Aer by {gap:.3g}")
        digest.update(result["reference"].tobytes())
        for qargs, kraus in program.ops:
            digest.update(repr(qargs).encode() + kraus.tobytes())
    ghost_run.require(parity_failure(PARITY_TOLERANCE) is None, "a gap at the tolerance passes")
    ghost_run.require(parity_failure(2 * PARITY_TOLERANCE) is not None, "a gap above the tolerance fails")
    print(f"jax_bridge_sweep self-test: {len(members)} replicas, sha256 {digest.hexdigest()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--device", choices=("cpu", "gpu", "tpu"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.device is None or args.out is None:
        parser.error("--device and --out are required")
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
        "parity_tolerance": PARITY_TOLERANCE,
        "versions": versions,
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    evolvers: dict[Any, Any] = {}
    for run in runs:
        out["runs"].append(sweep_run(run, device, index, evolvers))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    failed = [run["run"] for run in out["runs"] if run.get("max_abs_probability_minus_aer", 0.0) > PARITY_TOLERANCE]
    if failed:
        print(f"Aer parity above {PARITY_TOLERANCE:g} in {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
