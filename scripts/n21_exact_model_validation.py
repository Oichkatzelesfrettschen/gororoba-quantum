"""Sampled Aer counts against the exact branch-resolved law of the encoded N=21 feedback pair.

The n21-feedback-encoded planning prediction comes from
gororoba_quantum/dynamic_density.py, which evolves the classical-quantum state
of each dynamic circuit exactly under live_run's noise channels. This script
is that prediction's falsifier: it samples the same ISA circuits under the
same calibration snapshot with Aer statevector trajectories (the method
local_compute's density_matrix_dynamic_statevector policy selects for a
dynamic batch; live_run.noise_simulator's density_matrix default applies to
the others) and applies n21_exact_planning.validate_exact: every exact
outcome probability within the simultaneous Hoeffding radius of the pooled
sampled frequencies, and each endpoint arm's signed score and the endpoint
contrast within their own Hoeffding radii, the members and contracts read
from the record retained beside the ISA.

- ``--sample`` restricts each circuit of an ISA archive and the snapshot to
  the active qubits (snapshot_laws.restrict_circuit and restrict, the same
  channels), samples SHOTS per circuit at SEED on the device
  GOROROBA_AER_DEVICE names, and writes one shard record.
- ``--merge`` pools shard records that share the input digests and carry
  distinct seeds, in seed order.
- ``--check`` recomputes the exact laws from the retained inputs, samples
  nothing, and fails when any probability leaves the radius at total tail
  ``TAIL`` across every outcome of every circuit, or when an arm score or the
  contrast leaves its radius at ``TAIL`` split over those checks; it prints
  each arm's and the contrast's gap with its normal z score beside the
  Hoeffding verdict.
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
import law_encoding  # noqa: E402
import n21_exact_planning  # noqa: E402
import parallel  # noqa: E402
import qrng_seeds  # noqa: E402
import snapshot_laws  # noqa: E402
from experiment_optimizer import ObservableContract, ObservableTerm  # noqa: E402

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
    merged = dict(
        first,
        seeds=sorted(seeds),
        shots=sum(record["shots"] for record in ordered),
        counts=counts,
        wall_seconds={str(min(record["seeds"])): record["wall_seconds"] for record in ordered},
        shards=len(ordered),
        versions=[record["versions"] for record in ordered],
    )
    # Every shard's seed_source survives the merge, so each consumed QRNG index stays on record.
    sources = [record["seed_source"] for record in ordered if "seed_source" in record]
    merged.pop("seed_source", None)
    if sources:
        merged["seed_sources"] = sources
    return merged


def endpoint(record_path: Path) -> tuple[dict[str, str], tuple[ObservableContract, ...]]:
    """Circuit name to member, and the observable contracts, of the retained record beside the ISA."""
    retained = json.loads(record_path.read_text())
    members = {}
    for pub in retained["execution_pubs"]:
        if len(pub["components"]) != 1 or len(pub["components"][0]["registers_by_replica"]) != 1:
            raise ValueError(f"{pub['name']}: validation needs one single-replica component per circuit")
        members[pub["name"]] = pub["components"][0]["member"]
    contracts = tuple(
        ObservableContract(
            **{key: value for key, value in contract.items() if key != "terms"},
            terms=tuple(
                ObservableTerm(t["member"], tuple(law_encoding.dense(t["values"])), t["sign"])
                for t in contract["terms"]
            ),
        )
        for contract in retained["observable_contracts"]
    )
    return members, contracts


def compare(
    record: dict[str, Any],
    laws: dict[str, list[float]],
    members: dict[str, str],
    contracts: tuple[ObservableContract, ...],
) -> dict[str, Any]:
    """validate_exact on the pooled counts, with each score check's normal z score from the exact law."""
    if set(record["counts"]) != set(laws) or set(laws) != set(members):
        raise ValueError("record circuits differ from the ISA archive or its record")
    shots = int(record["shots"])
    rows = []
    circuits = {}
    for name, vector in sorted(record["counts"].items()):
        if sum(vector) != shots:
            raise ValueError(f"{name}: counts sum to {sum(vector)}, not {shots}")
        frequency = np.asarray(vector, dtype=float) / shots
        law = np.asarray(laws[name], dtype=float)
        rows.append({"entry": members[name], "replica": 0, "exact": law.tolist(), "sampled": frequency.tolist()})
        circuits[name] = {
            "member": members[name],
            "exact": [round(float(value), 12) for value in law],
            "sampled": [round(float(value), 12) for value in frequency],
            "max_gap": float(np.max(np.abs(frequency - law))),
        }
    result = n21_exact_planning.validate_exact(rows, contracts, shots, TAIL)
    exact_by_member = {row["entry"]: np.asarray(row["exact"]) for row in rows}
    variances = {}
    for contract in contracts:
        for term in contract.terms:
            values = np.asarray(term.values, dtype=float)
            law = exact_by_member[term.member]
            variances[term.member] = float(law @ values**2 - (law @ values) ** 2) / shots
    for member, arm in result["arms"].items():
        arm["z"] = arm["gap"] / math.sqrt(variances[member])
    for contract in contracts:
        row = result["contrasts"].get(contract.name)
        if row is not None:
            row["z"] = row["gap"] / math.sqrt(math.fsum(variances[term.member] for term in contract.terms))
    return {
        "shots": shots,
        "tail": TAIL,
        "radius": result["radius"],
        "passed": result["passed"],
        "failures": result["failures"],
        "arms": result["arms"],
        "contrasts": result["contrasts"],
        "circuits": circuits,
    }


def check(path: Path) -> dict[str, Any]:
    record = json.loads(path.read_text())
    snapshot = ROOT / record["snapshot"]["path"]
    isa = ROOT / record["isa"]["path"]
    if _sha256(snapshot) != record["snapshot"]["sha256"] or _sha256(isa) != record["isa"]["sha256"]:
        raise SystemExit(f"{path}: retained input digests differ")
    members, contracts = endpoint(isa.parent / "record.json")
    result = compare(record, exact_laws(snapshot, isa), members, contracts)
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
    members, contracts = endpoint(SELF_TEST_ISA.parent / "record.json")
    shots = 2_000_000
    generator = np.random.default_rng(20261017)
    counts = {name: [int(v) for v in generator.multinomial(shots, law)] for name, law in laws.items()}
    record = {"shots": shots, "counts": counts}
    accepted = compare(record, laws, members, contracts)
    _require(accepted["passed"], f"multinomial draw rejected: {accepted}")
    name = sorted(counts)[0]
    shifted = list(counts[name])
    moved = int(0.02 * shots)
    shifted[0] -= moved
    shifted[1] += moved
    rejected = compare({"shots": shots, "counts": dict(counts, **{name: shifted})}, laws, members, contracts)
    _require(not rejected["passed"], "a 0.02 mass shift passed the check")
    # A score bias inside the probability radius: move 0.9 of the probability
    # radius from label 11 to label 01 of one arm, a signed-score shift of 1.8
    # probability radii, which the arm's Bernstein radius refuses.
    moved = int(0.9 * accepted["radius"] * shots)
    biased = list(counts[name])
    biased[1] += moved
    biased[3] -= moved
    scored = compare({"shots": shots, "counts": dict(counts, **{name: biased})}, laws, members, contracts)
    _require(
        not scored["passed"] and all("probability gap" not in failure for failure in scored["failures"]),
        f"a score bias inside the probability radius passed or tripped the probability check: {scored['failures']}",
    )
    for law in laws.values():
        _require(math.isclose(math.fsum(law), 1.0, abs_tol=1e-9), "an exact law is unnormalized")
    print(
        f"n21 exact model validation: multinomial draw accepted at radius {accepted['radius']:.5f}; shift rejected; "
        "a score bias inside the probability radius rejected at the arm radius"
    )


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
    qrng_seeds.add_seed_argument(parser, "--seed")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.check is not None:
        result = check(args.check)
        print(json.dumps({key: result[key] for key in ("shots", "radius", "passed", "arms", "contrasts")}))
        return 0
    if args.out is None:
        raise SystemExit("--out is required")
    if args.sample:
        if None in (args.snapshot, args.isa, args.shots, args.seed):
            raise SystemExit("--sample needs --snapshot, --isa, --shots and --seed")
        record = sample(args.snapshot, args.isa, args.shots, args.seed)
        record["seed_source"] = qrng_seeds.seed_record(
            "scripts/n21_exact_model_validation.py",
            "--seed",
            f"{qrng_seeds.repo_relative(args.snapshot)} {qrng_seeds.repo_relative(args.isa)}",
            args.seed_source,
        )
    else:
        record = merge([json.loads(path.read_text()) for path in args.merge])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
