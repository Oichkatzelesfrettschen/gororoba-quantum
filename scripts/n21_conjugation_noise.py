"""Noisy N=21 order finding, baseline against the linear work-register encoding, under retained calibrations.

For each calibration snapshot (calibration_snapshot.py, the same gate,
readout, T1 and T2 channels live_run's noise model carries) the run compiles
and samples two workloads:

- the n21-feedback diagnostic, factor_order_finding(21, 4, 2) with and
  without feed-forward, whose exact labeled laws are (3, 2, 1, 2)/8 and
  (3, 1, 1, 3)/8 (qpe_diagnostics.n21_labeled_law); its observable is the
  signed-contrast difference, ideal 1/4;
- the ten-round factor_order_finding(21, 2, 10), scored by the fraction of
  shots whose phase recovers the order 6 (factoring.decode_counts).

Each workload runs unencoded and under the encoding x = B^-1 v that
scripts/linear_conjugation_search.py ranks best for it: the coset of least
s(4) for the two-round diagnostic, whose multipliers are 16 and 4, and the
coset of least ten-round surrogate for the full circuit.

The rebuilt snapshot Target carries no control flow, so the run adds
if_else, which the Heron Targets list, before compiling. Every circuit
compiles at optimization level 3 on the snapshot Target over the transpiler
seeds, and the seed with the fewest routed CZ (then the least depth) runs.
Sampling uses Aer statevector trajectories under the snapshot's noise model,
an unbiased sample of the density-matrix channel live_run evaluates.

Timing follows live_run's planning model: the Target duration of the
gate-time view (each if_else replaced by its true branch), plus the declared
classical latency per feed-forward stage, plus the repetition delay, per
shot; and the declared per-job overhead. The estimate is a planning input
for a live_run dry run, which stays the admission authority; the module
reads no IBM service and submits nothing.

Usage:
    "$PYTHON" scripts/n21_conjugation_noise.py --search SEARCH.json --snapshots SNAP... --out PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from linear_conjugation_search import coset_columns  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit import ControlFlowOp, IfElseOp  # noqa: E402
from qiskit.transpiler import generate_preset_pass_manager  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
from factoring import decode_counts  # noqa: E402
from order_finding import ENCODED_STRATEGY, factor_order_finding  # noqa: E402
from qpe_diagnostics import n21_labeled_law  # noqa: E402

SCHEMA = "n21-conjugation-noise-v1"
MODULUS = 21
TRANSPILER_SEEDS = tuple(range(8))
OPTIMIZATION_LEVEL = 3
SIMULATOR_SEED = 20261016
# live_run's planning declarations: the repetition delay IBM applies by
# default, the per-stage classical latency, and the retained dynamic job's
# non-circuit charge.
REPETITION_DELAY_SECONDS = 250e-6
CLASSICAL_LATENCY_SECONDS = 20e-6
JOB_OVERHEAD_SECONDS = 2.3
SHOT_TIERS = (4096, 8192, 16384, 32768)
TWO_ROUND_SHOTS = 32768
TEN_ROUND_SHOTS = 16384
TEN_ROUND_ORDER = 6


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"n21_conjugation_noise: {message}")


CIRCUIT_NAMES = (
    "two_round_baseline_ff",
    "two_round_baseline_noff",
    "two_round_encoded_ff",
    "two_round_encoded_noff",
    "ten_round_baseline",
    "ten_round_encoded",
)


def circuits(two_round: tuple[int, ...], ten_round: tuple[int, ...]) -> dict[str, QuantumCircuit]:
    built = {}
    for encoding, columns in (("baseline", None), ("encoded", two_round)):
        for feed_forward in (True, False):
            built[f"two_round_{encoding}_{'ff' if feed_forward else 'noff'}"] = factor_order_finding(
                MODULUS, 4, 2, multiplier_strategy=ENCODED_STRATEGY, feed_forward=feed_forward, work_columns=columns
            )
    for encoding, columns in (("baseline", None), ("encoded", ten_round)):
        built[f"ten_round_{encoding}"] = factor_order_finding(
            MODULUS, 2, 10, multiplier_strategy=ENCODED_STRATEGY, work_columns=columns
        )
    _require(tuple(built) == CIRCUIT_NAMES, "circuit names drifted")
    return built


def _backend(snapshot: dict[str, Any]) -> calibration_snapshot.SnapshotBackend:
    backend, _ = calibration_snapshot.noise_model(snapshot)
    if "if_else" not in backend.target.operation_names:
        backend.target.add_instruction(IfElseOp, name="if_else")
    return backend


def gate_time_view(isa: QuantumCircuit) -> QuantumCircuit:
    """isa with each control-flow op replaced by its first block's gates (live_run._gate_time_view)."""
    out = isa.copy_empty_like()
    for instruction in isa.data:
        if isinstance(instruction.operation, ControlFlowOp):
            body = instruction.operation.blocks[0]
            for sub in body.data:
                out.append(sub.operation, [instruction.qubits[body.find_bit(qubit).index] for qubit in sub.qubits])
        else:
            out.append(instruction)
    return out


def classical_stages(isa: QuantumCircuit) -> int:
    """Measurements that a later if_else waits on: each costs one classical round trip."""
    stages = 0
    pending = False
    for instruction in isa.data:
        name = instruction.operation.name
        if name == "measure":
            pending = True
        elif name == "if_else" and pending:
            stages += 1
            pending = False
    return stages


def compile_job(job: tuple[str, str, int, tuple[int, ...], tuple[int, ...]]) -> dict[str, Any]:
    """Compile one circuit at one transpiler seed on one snapshot's Target."""
    snapshot_path, name, seed, two_round, ten_round = job
    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    backend = _backend(snapshot)
    source = circuits(two_round, ten_round)[name]
    manager = generate_preset_pass_manager(
        optimization_level=OPTIMIZATION_LEVEL, target=backend.target, seed_transpiler=seed
    )
    isa = manager.run(source)
    layout = isa.layout.final_index_layout() if isa.layout is not None else []
    return {
        "seed_transpiler": seed,
        "routed_cz": int(isa.count_ops().get("cz", 0)),
        "depth": isa.depth(),
        "duration_dt": int(gate_time_view(isa).estimate_duration(backend.target, unit="dt")),
        "if_else": int(isa.count_ops().get("if_else", 0)),
        "classical_stages": classical_stages(isa),
        "layout": list(layout),
    }


def _labeled(counts: dict[str, int], shots: int) -> list[float]:
    distribution = [0.0] * 4
    for key, count in counts.items():
        distribution[int(key.replace(" ", ""), 2)] += count / shots
    return distribution


def two_round_summary(results: dict[str, dict[str, Any]], encoding: str) -> dict[str, Any]:
    ff = results[f"two_round_{encoding}_ff"]["distribution"]
    noff = results[f"two_round_{encoding}_noff"]["distribution"]
    ideal_ff = [float(value) for value in n21_labeled_law(True)]
    ideal_noff = [float(value) for value in n21_labeled_law(False)]
    shots = results[f"two_round_{encoding}_ff"]["shots"]
    contrast = (ff[1] - ff[3]) - (noff[1] - noff[3])
    variance = (ff[1] + ff[3] - (ff[1] - ff[3]) ** 2) + (noff[1] + noff[3] - (noff[1] - noff[3]) ** 2)
    standard_error = math.sqrt(variance / shots)
    # Shots per arm for a two-sided 0.05 test with power 0.8 under the
    # normal approximation, at the modeled contrast.
    required = math.ceil(((1.959964 + 0.841621) ** 2) * variance / contrast**2) if contrast > 0 else None
    return {
        "contrast_difference": contrast,
        "ideal_contrast_difference": 0.25,
        "sampling_standard_error": standard_error,
        "feedback_tvd_to_ideal": 0.5 * sum(abs(a - b) for a, b in zip(ff, ideal_ff, strict=True)),
        "no_feedback_tvd_to_ideal": 0.5 * sum(abs(a - b) for a, b in zip(noff, ideal_noff, strict=True)),
        "shots_per_arm_for_power_0_8": required,
    }


def ten_round_recovery(counts: Mapping[str, int]) -> float:
    keyed: dict[str | int, int] = {key: count for key, count in counts.items()}
    recovered = 0
    for recovery, count in decode_counts(keyed, 10, MODULUS, 2):
        if TEN_ROUND_ORDER in recovery.orders:
            recovered += count
    return recovered / sum(counts.values())


def uniform_recovery_rate() -> float:
    """Order-6 recovery when every ten-bit phase outcome is equally likely, the fully depolarized floor."""
    return ten_round_recovery({format(value, "010b"): 1 for value in range(1 << 10)})


def ideal_recovery_rate(circuit: QuantumCircuit, shots: int) -> float:
    """Order-6 recovery of the noiseless circuit, sampled with the same shot count."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(method="statevector", max_parallel_threads=parallel.workers())
    isa = transpile(circuit, simulator, optimization_level=0)
    return ten_round_recovery(simulator.run(isa, shots=shots, seed_simulator=SIMULATOR_SEED).result().get_counts())


def seconds_estimate(duration_dt: int, dt: float, stages: int, shots: int) -> float:
    per_shot = duration_dt * dt + stages * CLASSICAL_LATENCY_SECONDS + REPETITION_DELAY_SECONDS
    return shots * per_shot


def run(search: dict[str, Any], snapshot_paths: list[Path]) -> dict[str, Any]:
    two_round_index = search["summary"]["s4_winners"][0]["index"]
    two_round = tuple(search["summary"]["s4_winners"][0]["columns"])
    _require(coset_columns()[two_round_index] == two_round, "the s4 winner's columns differ from its coset index")
    ten_round = tuple(search["summary"]["winners"][0]["columns"])
    built = circuits(two_round, ten_round)
    names = list(CIRCUIT_NAMES)
    jobs = [
        (str(path), name, seed, two_round, ten_round)
        for path in snapshot_paths
        for name in names
        for seed in TRANSPILER_SEEDS
    ]
    started = time.perf_counter()
    compiled = parallel.ordered_map(compile_job, jobs, min_items=2)
    compile_seconds = time.perf_counter() - started
    backends = []
    for position, path in enumerate(snapshot_paths):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        backend = _backend(snapshot)
        simulator = calibration_snapshot.noise_simulator(snapshot, "CPU")
        simulator.set_options(method="statevector", max_parallel_threads=parallel.workers())
        results: dict[str, dict[str, Any]] = {}
        for index, name in enumerate(names):
            start = (position * len(names) + index) * len(TRANSPILER_SEEDS)
            runs = compiled[start : start + len(TRANSPILER_SEEDS)]
            chosen = min(runs, key=lambda run: (run["routed_cz"], run["depth"], run["seed_transpiler"]))
            manager = generate_preset_pass_manager(
                optimization_level=OPTIMIZATION_LEVEL, target=backend.target, seed_transpiler=chosen["seed_transpiler"]
            )
            isa = manager.run(built[name])
            shots = TWO_ROUND_SHOTS if name.startswith("two_round") else TEN_ROUND_SHOTS
            sampled = time.perf_counter()
            counts = simulator.run(isa, shots=shots, seed_simulator=SIMULATOR_SEED + index).result().get_counts()
            entry: dict[str, Any] = {
                "shots": shots,
                "chosen": chosen,
                "per_seed_routed_cz": [run["routed_cz"] for run in runs],
                "simulation_seconds": round(time.perf_counter() - sampled, 3),
                "counts": dict(sorted(counts.items())),
                "seconds_by_shots": {
                    str(tier): seconds_estimate(chosen["duration_dt"], snapshot["dt"], chosen["classical_stages"], tier)
                    for tier in SHOT_TIERS
                },
            }
            if name.startswith("two_round"):
                entry["distribution"] = _labeled(counts, shots)
            else:
                entry["order_recovery_rate"] = ten_round_recovery(counts)
            results[name] = entry
            print(
                f"{snapshot['backend']} {name}: cz={chosen['routed_cz']} sim={entry['simulation_seconds']}s", flush=True
            )
        two_round_pair = {encoding: two_round_summary(results, encoding) for encoding in ("baseline", "encoded")}
        job_seconds = {
            encoding: {
                str(tier): JOB_OVERHEAD_SECONDS
                + sum(results[f"two_round_{encoding}_{arm}"]["seconds_by_shots"][str(tier)] for arm in ("ff", "noff"))
                for tier in SHOT_TIERS
            }
            for encoding in ("baseline", "encoded")
        }
        backends.append(
            {
                "backend": snapshot["backend"],
                "calibration": snapshot["calibration"],
                "snapshot": str(path.relative_to(ROOT)),
                "snapshot_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "circuits": results,
                "two_round": two_round_pair,
                "two_round_job_seconds": job_seconds,
                "ten_round_job_seconds": {
                    encoding: {
                        str(tier): JOB_OVERHEAD_SECONDS
                        + results[f"ten_round_{encoding}"]["seconds_by_shots"][str(tier)]
                        for tier in SHOT_TIERS
                    }
                    for encoding in ("baseline", "encoded")
                },
            }
        )
    return {
        "schema": SCHEMA,
        "qpu_executed": False,
        "encodings": {
            "two_round": {"columns": list(two_round), "coset_index": two_round_index},
            "ten_round": {"columns": list(ten_round), "coset_index": search["summary"]["winners"][0]["index"]},
        },
        "search_record_sha256": hashlib.sha256(json.dumps(search, sort_keys=True).encode()).hexdigest(),
        "compiler": {
            "optimization_level": OPTIMIZATION_LEVEL,
            "seeds": list(TRANSPILER_SEEDS),
            "rule": "fewest routed CZ, then depth, then seed",
        },
        "simulation": {
            "method": "statevector trajectories",
            "seed_base": SIMULATOR_SEED,
            "workers": parallel.workers(),
        },
        "timing_model": {
            "repetition_delay_seconds": REPETITION_DELAY_SECONDS,
            "classical_latency_seconds_per_stage": CLASSICAL_LATENCY_SECONDS,
            "job_overhead_seconds": JOB_OVERHEAD_SECONDS,
            "duration": (
                "Target duration of the gate-time view; a lower bound that omits scheduler alignment and reset "
                "residuals"
            ),
        },
        "ten_round_reference": {
            "uniform_recovery_rate": uniform_recovery_rate(),
            "ideal_recovery_rate": ideal_recovery_rate(built["ten_round_baseline"], TEN_ROUND_SHOTS),
        },
        "compile_seconds": round(compile_seconds, 3),
        "backends": backends,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--search", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    search = json.loads(args.search.read_text(encoding="utf-8"))
    _require(search.get("mode") == "exhaustive", "--search must be a merged exhaustive record")
    record = run(search, [path.resolve() for path in args.snapshots])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for backend in record["backends"]:
        for encoding, summary in backend["two_round"].items():
            print(
                f"{backend['backend']} two-round {encoding}: contrast {summary['contrast_difference']:.4f} "
                f"+/- {summary['sampling_standard_error']:.4f}, "
                f"shots/arm for power 0.8: {summary['shots_per_arm_for_power_0_8']}"
            )
        for encoding in ("baseline", "encoded"):
            print(
                f"{backend['backend']} ten-round {encoding}: order recovery "
                f"{backend['circuits'][f'ten_round_{encoding}']['order_recovery_rate']:.4f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
