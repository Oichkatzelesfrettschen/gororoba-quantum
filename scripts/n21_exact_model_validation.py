"""Sampled Aer counts against the exact branch-resolved law of the encoded N=21 feedback pair.

The n21-feedback-encoded planning prediction comes from
gororoba_quantum/dynamic_density.py, which evolves the classical-quantum state
of each dynamic circuit exactly under live_run's noise channels. This script
is that prediction's falsifier: it samples the same ISA circuits under the
same calibration snapshot with Aer statevector trajectories (the sampler
live_run's planning uses for dynamic circuits) and requires every exact
outcome probability to lie within the simultaneous Hoeffding radius of the
pooled sampled frequencies.

- ``--sample`` restricts each circuit of an ISA archive and the snapshot to
  the active qubits (snapshot_laws.restrict_circuit and restrict, the same
  channels), samples SHOTS per circuit at SEED on the device
  GOROROBA_AER_DEVICE names, and writes one shard record.
- ``--merge`` pools shard records that share the input digests and carry
  distinct seeds, in seed order.
- ``--check`` recomputes the exact laws from the retained inputs, samples
  nothing, and fails when any probability leaves the radius at total tail
  ``TAIL`` across every outcome of every circuit.
- ``--self-test`` checks multinomial draws from the exact laws (accepted)
  and a draw that moves 0.02 of one circuit's mass (rejected).

Usage:
    "$PYTHON" scripts/n21_exact_model_validation.py --sample --snapshot SNAP --isa QPY --shots M --seed K --out PATH
    "$PYTHON" scripts/n21_exact_model_validation.py --merge SHARD... --out PATH
    "$PYTHON" scripts/n21_exact_model_validation.py --check PATH
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qiskit import QuantumCircuit, qpy  # noqa: E402

import calibration_snapshot  # noqa: E402
import dynamic_density  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

SCHEMA = "n21-exact-model-validation-v1"
TAIL = 1e-3


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _circuits(isa: Path) -> list[QuantumCircuit]:
    with isa.open("rb") as handle:
        return list(qpy.load(handle))


def _restricted(snapshot: dict[str, Any], circuit: QuantumCircuit) -> tuple[QuantumCircuit, dict[str, Any], list[int]]:
    reduced, qubits = snapshot_laws.restrict_circuit(circuit)
    return reduced, snapshot_laws.restrict(snapshot, qubits), qubits


def _exact(item: tuple[dict[str, Any], bytes]) -> list[float]:
    """Exact recorded law of one serialized circuit under its restricted snapshot's noise model."""
    snapshot, payload = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    _view, noise = calibration_snapshot.noise_model(snapshot)
    return [float(value) for value in dynamic_density.probabilities(circuit, noise)]


def _serialized(circuit: QuantumCircuit) -> bytes:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


def exact_laws(snapshot_path: Path, isa: Path) -> dict[str, list[float]]:
    snapshot = json.loads(snapshot_path.read_text())
    items = []
    names = []
    for circuit in _circuits(isa):
        reduced, restricted, _qubits = _restricted(snapshot, circuit)
        items.append((restricted, _serialized(reduced)))
        names.append(circuit.name)
    return dict(zip(names, parallel.ordered_map(_exact, items, min_items=2), strict=True))


def sample(snapshot_path: Path, isa: Path, shots: int, seed: int) -> dict[str, Any]:
    snapshot = json.loads(snapshot_path.read_text())
    device = calibration_snapshot.aer_device()
    counts: dict[str, list[int]] = {}
    seconds: dict[str, float] = {}
    for position, circuit in enumerate(_circuits(isa)):
        reduced, restricted, qubits = _restricted(snapshot, circuit)
        simulator = calibration_snapshot.noise_simulator(restricted, device, method="statevector")
        simulator.set_options(max_parallel_threads=parallel.workers(), seed_simulator=seed + position)
        start = time.perf_counter()
        result = simulator.run(reduced, shots=shots).result().get_counts()
        seconds[circuit.name] = time.perf_counter() - start
        vector = [0] * 2**reduced.num_clbits
        for bits, count in result.items():
            vector[int(bits.replace(" ", ""), 2)] += count
        counts[circuit.name] = vector
    import qiskit
    import qiskit_aer

    return {
        "schema": SCHEMA,
        "snapshot": {"path": str(snapshot_path), "sha256": _sha256(snapshot_path)},
        "isa": {"path": str(isa), "sha256": _sha256(isa)},
        "method": "statevector",
        "device": device,
        "seeds": [seed],
        "shots": shots,
        "counts": counts,
        "wall_seconds": seconds,
        "workers": parallel.workers(),
        "versions": {"qiskit": qiskit.__version__, "qiskit-aer": qiskit_aer.__version__, "numpy": np.__version__},
    }


def merge(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise SystemExit("merge needs at least one shard record")
    first = records[0]
    for record in records:
        if record["schema"] != SCHEMA or record["snapshot"] != first["snapshot"] or record["isa"] != first["isa"]:
            raise SystemExit("shard records differ in schema or input digests")
    seeds = [seed for record in records for seed in record["seeds"]]
    if len(set(seeds)) != len(seeds):
        raise SystemExit("shard records repeat a seed")
    ordered = sorted(records, key=lambda record: min(record["seeds"]))
    counts = {
        name: [sum(record["counts"][name][k] for record in ordered) for k in range(len(vector))]
        for name, vector in first["counts"].items()
    }
    return dict(
        first,
        seeds=sorted(seeds),
        shots=sum(record["shots"] for record in ordered),
        counts=counts,
        wall_seconds={str(min(record["seeds"])): record["wall_seconds"] for record in ordered},
        shards=len(ordered),
        versions=[record["versions"] for record in ordered],
    )


def compare(record: dict[str, Any], laws: dict[str, list[float]]) -> dict[str, Any]:
    """Every exact probability against the pooled frequency at a simultaneous Hoeffding radius."""
    if set(record["counts"]) != set(laws):
        raise ValueError("record circuits differ from the ISA archive")
    outcomes = sum(len(vector) for vector in record["counts"].values())
    shots = int(record["shots"])
    radius = dynamic_density.hoeffding_radius(shots, outcomes, TAIL)
    rows = {}
    passed = True
    for name, vector in sorted(record["counts"].items()):
        if sum(vector) != shots:
            raise ValueError(f"{name}: counts sum to {sum(vector)}, not {shots}")
        frequency = np.asarray(vector, dtype=float) / shots
        law = np.asarray(laws[name], dtype=float)
        gap = float(np.max(np.abs(frequency - law)))
        passed &= gap <= radius
        rows[name] = {
            "exact": [round(float(value), 12) for value in law],
            "sampled": [round(float(value), 12) for value in frequency],
            "max_gap": gap,
            "signed_contrast_exact": float(law[1] - law[3]),
            "signed_contrast_sampled": float(frequency[1] - frequency[3]),
        }
    return {"shots": shots, "tail": TAIL, "radius": radius, "passed": bool(passed), "circuits": rows}


def check(path: Path) -> dict[str, Any]:
    record = json.loads(path.read_text())
    snapshot = ROOT / record["snapshot"]["path"]
    isa = ROOT / record["isa"]["path"]
    if _sha256(snapshot) != record["snapshot"]["sha256"] or _sha256(isa) != record["isa"]["sha256"]:
        raise SystemExit(f"{path}: retained input digests differ")
    result = compare(record, exact_laws(snapshot, isa))
    if not result["passed"]:
        raise SystemExit(f"{path}: exact law leaves the sampled radius: {json.dumps(result, indent=1)}")
    return result


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


SELF_TEST_SNAPSHOT = ROOT / "docs/evidence/calibration/history/ibm_kingston/20261016T1213360700.json"
SELF_TEST_ISA = ROOT / "results/live/2026-10-17T003834.987727Z/isa.qpy"


def self_test() -> None:
    laws = exact_laws(SELF_TEST_SNAPSHOT, SELF_TEST_ISA)
    shots = 2_000_000
    generator = np.random.default_rng(20261017)
    counts = {name: [int(v) for v in generator.multinomial(shots, law)] for name, law in laws.items()}
    record = {"shots": shots, "counts": counts}
    accepted = compare(record, laws)
    _require(accepted["passed"], f"multinomial draw rejected: {accepted}")
    name = sorted(counts)[0]
    shifted = list(counts[name])
    moved = int(0.02 * shots)
    shifted[0] -= moved
    shifted[1] += moved
    rejected = compare({"shots": shots, "counts": dict(counts, **{name: shifted})}, laws)
    _require(not rejected["passed"], "a 0.02 mass shift passed the check")
    for law in laws.values():
        _require(math.isclose(math.fsum(law), 1.0, abs_tol=1e-9), "an exact law is unnormalized")
    print(f"n21 exact model validation: multinomial draw accepted at radius {accepted['radius']:.5f}; shift rejected")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sample", action="store_true")
    mode.add_argument("--merge", nargs="+", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--isa", type=Path)
    parser.add_argument("--shots", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.check is not None:
        result = check(args.check)
        print(json.dumps({key: result[key] for key in ("shots", "radius", "passed")}))
        return 0
    if args.out is None:
        raise SystemExit("--out is required")
    if args.sample:
        if None in (args.snapshot, args.isa, args.shots, args.seed):
            raise SystemExit("--sample needs --snapshot, --isa, --shots and --seed")
        record = sample(args.snapshot, args.isa, args.shots, args.seed)
    else:
        record = merge([json.loads(path.read_text()) for path in args.merge])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
