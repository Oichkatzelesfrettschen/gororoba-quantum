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

Each workload runs unencoded and under the encoding x = B^-1 v of the coset
that gororoba_quantum/linear_conjugation_challenger.py admits with the fewest
median routed CZ for it, the circuit a hardware case would carry.

The rebuilt snapshot Target carries no control flow, so the run adds
if_else, which the Heron Targets list, before compiling. Every circuit
compiles at optimization level 3 on the snapshot Target over the transpiler
seeds, and the seed with the fewest routed CZ (then the least depth) runs.
Sampling uses Aer statevector trajectories under the snapshot's noise model,
an unbiased sample of the density-matrix channel live_run evaluates, on the
device GOROROBA_AER_DEVICE names. On a T4 host these 7-qubit dynamic
circuits sample 1.5 to 8 times faster on the CPU than on the GPU
(scripts/aer_gpu_probe.py), so the CPU is the default device for them.
Aer carries the noise of the circuit's active qubits only
(snapshot_laws.restrict_circuit and restrict), the same channel on each.

Timing follows live_run's planning model through its own functions: the
Target duration of _gate_time_view (each if_else replaced by its true
branch), plus the declared classical latency per sequential feed-forward
decision (_feed_forward_stages), plus the repetition delay, per shot; and
the declared per-job overhead. The estimate is a planning input
for a live_run dry run, which stays the admission authority; the module
reads no IBM service and submits nothing.

Usage:
    "$PYTHON" scripts/n21_conjugation_noise.py --challenger CHALLENGER.json --snapshots SNAP... --out PATH
    "$PYTHON" scripts/n21_conjugation_noise.py --merge RECORD... --out PATH
    "$PYTHON" scripts/n21_conjugation_noise.py --check PATH
    "$PYTHON" scripts/n21_conjugation_noise.py --check PATH --chain SEARCH CHALLENGER
    "$PYTHON" scripts/n21_conjugation_noise.py --check PATH --all-seeds

--check recompiles every circuit's chosen seed on its retained snapshot and
re-derives the distributions, contrasts, recovery rates and seconds from
the retained counts; it samples nothing. --all-seeds recompiles every seed of
every circuit, requires each retained per_seed_routed_cz entry to equal its
recompiled routed CZ, and re-derives the (routed CZ, depth, seed) choice.
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
import qiskit_aer  # noqa: E402
from linear_conjugation_search import coset_columns  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit import IfElseOp  # noqa: E402
from qiskit.transpiler import generate_preset_pass_manager  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402
from factoring import decode_counts  # noqa: E402
from live_run import _feed_forward_stages, _gate_time_view  # noqa: E402
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
# A replay recompiles on another host: routed CZ, layout and classical stages
# match exactly, while depth and duration follow floating-point single-qubit
# synthesis and match within this relative tolerance (the challenger's).
REPLAY_TOLERANCE = 0.002
EXACT_COMPILE_FIELDS = ("seed_transpiler", "routed_cz", "if_else", "classical_stages", "layout")
# GOROROBA_AER_DEVICE, which a Kaggle kernel sets to its machine's device.
DEVICE = calibration_snapshot.aer_device()


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
        "duration_dt": int(_gate_time_view(isa).estimate_duration(backend.target, unit="dt")),
        "if_else": int(isa.count_ops().get("if_else", 0)),
        "classical_stages": _feed_forward_stages(isa),
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
    # normal approximation, at the modeled contrast's magnitude.
    required = math.ceil(((1.959964 + 0.841621) ** 2) * variance / contrast**2) if contrast != 0 else None
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


def circuit_entry(
    name: str, chosen: dict[str, Any], runs: list[dict[str, Any]], counts: dict[str, int], shots: int, dt: float
) -> dict[str, Any]:
    """Every field of one circuit's result that the compile choice and the counts determine."""
    entry: dict[str, Any] = {
        "shots": shots,
        "chosen": chosen,
        "per_seed_routed_cz": [run["routed_cz"] for run in runs],
        "counts": counts,
        "seconds_by_shots": {
            str(tier): seconds_estimate(chosen["duration_dt"], dt, chosen["classical_stages"], tier)
            for tier in SHOT_TIERS
        },
    }
    if name.startswith("two_round"):
        entry["distribution"] = _labeled(counts, shots)
    else:
        entry["order_recovery_rate"] = ten_round_recovery(counts)
    return entry


def backend_summary(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The two-round contrasts and the job-seconds estimates one backend's circuit results determine."""
    encodings = ("baseline", "encoded")
    return {
        "two_round": {encoding: two_round_summary(results, encoding) for encoding in encodings},
        "two_round_job_seconds": {
            encoding: {
                str(tier): JOB_OVERHEAD_SECONDS
                + sum(results[f"two_round_{encoding}_{arm}"]["seconds_by_shots"][str(tier)] for arm in ("ff", "noff"))
                for tier in SHOT_TIERS
            }
            for encoding in encodings
        },
        "ten_round_job_seconds": {
            encoding: {
                str(tier): JOB_OVERHEAD_SECONDS + results[f"ten_round_{encoding}"]["seconds_by_shots"][str(tier)]
                for tier in SHOT_TIERS
            }
            for encoding in encodings
        },
    }


def check(record: dict[str, Any], all_seeds: bool = False) -> str:
    """Recompile each chosen seed on its snapshot and re-derive every summary from the retained counts.

    With all_seeds every seed of every circuit is recompiled, which binds the
    whole per_seed_routed_cz list and the compile choice to the compiler.
    """
    _require(record.get("schema") == SCHEMA, "not an n21-conjugation-noise record")
    two_round = tuple(record["encodings"]["two_round"]["columns"])
    ten_round = tuple(record["encodings"]["ten_round"]["columns"])
    _require(record["ten_round_reference"]["uniform_recovery_rate"] == uniform_recovery_rate(), "uniform floor")
    # The noiseless reference is a seeded sample; another host's floating
    # point may move single outcomes, so it must agree within four binomial
    # standard errors.
    retained_ideal = record["ten_round_reference"]["ideal_recovery_rate"]
    ideal = ideal_recovery_rate(circuits(two_round, ten_round)["ten_round_baseline"], TEN_ROUND_SHOTS)
    _require(
        abs(ideal - retained_ideal) <= 4 * math.sqrt(retained_ideal * (1 - retained_ideal) / TEN_ROUND_SHOTS),
        f"noiseless recovery {ideal} against the retained {retained_ideal}",
    )
    jobs = []
    for backend in record["backends"]:
        path = ROOT / backend["snapshot"]
        _require(hashlib.sha256(path.read_bytes()).hexdigest() == backend["snapshot_sha256"], f"{path} changed")
        jobs += [
            (str(path), name, seed, two_round, ten_round)
            for name in CIRCUIT_NAMES
            for seed in (TRANSPILER_SEEDS if all_seeds else (backend["circuits"][name]["chosen"]["seed_transpiler"],))
        ]
    recompiled = iter(parallel.ordered_map(compile_job, jobs, min_items=2))
    for backend in record["backends"]:
        snapshot = json.loads((ROOT / backend["snapshot"]).read_text(encoding="utf-8"))
        for name in CIRCUIT_NAMES:
            retained = backend["circuits"][name]
            runs = [next(recompiled) for _ in (TRANSPILER_SEEDS if all_seeds else (0,))]
            chosen = retained["chosen"]
            if all_seeds:
                _require(
                    [run["routed_cz"] for run in runs] == retained["per_seed_routed_cz"],
                    f"{backend['backend']} {name}: recompiled per-seed routed CZ "
                    f"{[run['routed_cz'] for run in runs]} against {retained['per_seed_routed_cz']}",
                )
                best = min(runs, key=lambda run: (run["routed_cz"], run["depth"], run["seed_transpiler"]))
                _require(
                    best["seed_transpiler"] == chosen["seed_transpiler"],
                    f"{backend['backend']} {name}: the fewest-CZ, least-depth seed is {best['seed_transpiler']}, "
                    f"the record chose {chosen['seed_transpiler']}",
                )
            run = next(run for run in runs if run["seed_transpiler"] == chosen["seed_transpiler"])
            _require(
                all(run[field] == chosen[field] for field in EXACT_COMPILE_FIELDS)
                and all(
                    abs(run[metric] - chosen[metric]) <= REPLAY_TOLERANCE * chosen[metric]
                    for metric in ("depth", "duration_dt")
                ),
                f"{backend['backend']} {name}: recompiled {run} against {chosen}",
            )
            expected = circuit_entry(
                name, retained["chosen"], [], retained["counts"], retained["shots"], snapshot["dt"]
            )
            expected["per_seed_routed_cz"] = retained["per_seed_routed_cz"]
            _require(
                min(retained["per_seed_routed_cz"]) == retained["chosen"]["routed_cz"],
                f"{backend['backend']} {name}: the chosen seed is not the fewest-CZ seed",
            )
            _require(sum(retained["counts"].values()) == retained["shots"], f"{name}: counts do not sum to shots")
            derived = {key: retained[key] for key in expected}
            _require(derived == expected, f"{backend['backend']} {name}: derived fields differ")
        summary = backend_summary(backend["circuits"])
        _require(all(backend[key] == value for key, value in summary.items()), f"{backend['backend']}: summary")
    scope = "compilations over every seed" if all_seeds else "chosen compilations"
    return f"{len(jobs)} {scope} and every derived field reproduced"


def admitted(challenger: dict[str, Any], problem: str) -> tuple[int, tuple[int, ...]]:
    """The best admitted coset of one problem in a linear_conjugation_challenger record."""
    entry = challenger["problems"][problem]
    _require(entry["best_admitted"] is not None, f"the challenger admitted no {problem} coset")
    best = next(record for record in entry["challengers"] if record["coset_index"] == entry["best_admitted"])
    columns = tuple(best["columns"])
    _require(coset_columns()[best["coset_index"]] == columns, f"{problem}: columns differ from the coset index")
    return best["coset_index"], columns


def run(challenger: dict[str, Any], snapshot_paths: list[Path]) -> dict[str, Any]:
    two_round_index, two_round = admitted(challenger, "two_round")
    ten_round_index, ten_round = admitted(challenger, "ten_round")
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
        results: dict[str, dict[str, Any]] = {}
        for index, name in enumerate(names):
            start = (position * len(names) + index) * len(TRANSPILER_SEEDS)
            runs = compiled[start : start + len(TRANSPILER_SEEDS)]
            chosen = min(runs, key=lambda run: (run["routed_cz"], run["depth"], run["seed_transpiler"]))
            manager = generate_preset_pass_manager(
                optimization_level=OPTIMIZATION_LEVEL, target=backend.target, seed_transpiler=chosen["seed_transpiler"]
            )
            active, qubits = snapshot_laws.restrict_circuit(manager.run(built[name]))
            # On a GPU the simulator batches shots of the circuits without
            # control flow and runs the feed-forward ones shot by shot
            # (calibration_snapshot.SnapshotSimulator).
            simulator = calibration_snapshot.noise_simulator(
                snapshot_laws.restrict(snapshot, qubits), DEVICE, method="statevector"
            )
            simulator.set_options(max_parallel_threads=parallel.workers())
            shots = TWO_ROUND_SHOTS if name.startswith("two_round") else TEN_ROUND_SHOTS
            sampled = time.perf_counter()
            counts = simulator.run(active, shots=shots, seed_simulator=SIMULATOR_SEED + index).result().get_counts()
            entry = circuit_entry(name, chosen, runs, dict(sorted(counts.items())), shots, snapshot["dt"])
            entry["simulation_seconds"] = round(time.perf_counter() - sampled, 3)
            results[name] = entry
            print(
                f"{snapshot['backend']} {name}: cz={chosen['routed_cz']} sim={entry['simulation_seconds']}s", flush=True
            )
        backends.append(
            {
                "backend": snapshot["backend"],
                "calibration": snapshot["calibration"],
                **calibration_snapshot.backend_identity(snapshot),
                "snapshot": str(path.relative_to(ROOT)),
                "snapshot_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "circuits": results,
                **backend_summary(results),
            }
        )
    return {
        "schema": SCHEMA,
        "qpu_executed": False,
        "encodings": {
            "two_round": {"columns": list(two_round), "coset_index": two_round_index},
            "ten_round": {"columns": list(ten_round), "coset_index": ten_round_index},
        },
        "challenger_record_sha256": hashlib.sha256(json.dumps(challenger, sort_keys=True).encode()).hexdigest(),
        "compiler": {
            "optimization_level": OPTIMIZATION_LEVEL,
            "seeds": list(TRANSPILER_SEEDS),
            "rule": "fewest routed CZ, then depth, then seed",
        },
        "simulation": {
            "method": "statevector trajectories",
            "device": DEVICE,
            "qiskit_aer": qiskit_aer.__version__,
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


def rederive(backend: dict[str, Any]) -> dict[str, Any]:
    """A backend entry with every field the compile choices and counts determine computed afresh."""
    snapshot = json.loads((ROOT / backend["snapshot"]).read_text(encoding="utf-8"))
    circuits_out = {}
    for name, retained in backend["circuits"].items():
        entry = circuit_entry(name, retained["chosen"], [], retained["counts"], retained["shots"], snapshot["dt"])
        entry["per_seed_routed_cz"] = retained["per_seed_routed_cz"]
        if "simulation_seconds" in retained:
            entry["simulation_seconds"] = retained["simulation_seconds"]
        circuits_out[name] = entry
    return {**backend, "circuits": circuits_out, **backend_summary(circuits_out)}


def merge(records: list[dict[str, Any]]) -> dict[str, Any]:
    """One record holding every backend of per-backend records that agree on everything else.

    Every derived field is computed afresh from each backend's compile choices
    and counts, so the merged record follows this script's derivations.
    """
    shared = [key for key in records[0] if key not in ("backends", "compile_seconds")]
    for record in records[1:]:
        differing = [key for key in shared if record.get(key) != records[0].get(key)]
        _require(not differing, f"records disagree on {differing}")
    merged = {key: records[0][key] for key in shared}
    merged["backends"] = sorted(
        (
            {**rederive(backend), "compile_seconds": record["compile_seconds"]}
            for record in records
            for backend in record["backends"]
        ),
        key=lambda backend: backend["backend"],
    )
    names = [backend["backend"] for backend in merged["backends"]]
    _require(len(set(names)) == len(names), f"a backend repeats: {names}")
    return merged


def check_chain(search_path: Path, challenger_path: Path, noise: dict[str, Any]) -> str:
    """The challenger names the retained search file's digest, and the noise record the challenger's."""
    challenger = json.loads(challenger_path.read_text(encoding="utf-8"))
    search_digest = hashlib.sha256(search_path.read_bytes()).hexdigest()
    _require(challenger["search_record_sha256"] == search_digest, f"{challenger_path} names another search record")
    challenger_digest = hashlib.sha256(json.dumps(challenger, sort_keys=True).encode()).hexdigest()
    _require(noise["challenger_record_sha256"] == challenger_digest, "the noise record names another challenger record")
    return "search -> challenger -> noise digests agree"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--challenger", type=Path, help="linear_conjugation_challenger record naming the admitted cosets"
    )
    parser.add_argument("--snapshots", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, help="retained record to replay without sampling")
    parser.add_argument("--merge", type=Path, nargs="+", help="per-backend records to combine into --out")
    parser.add_argument("--all-seeds", action="store_true", help="with --check, recompile every transpiler seed")
    parser.add_argument(
        "--chain", type=Path, nargs=2, metavar=("SEARCH", "CHALLENGER"), help="with --check, bind the record chain"
    )
    args = parser.parse_args()
    if args.check and args.chain:
        record = json.loads(args.check.read_text(encoding="utf-8"))
        print(f"n21_conjugation_noise: {check_chain(args.chain[0], args.chain[1], record)}")
        return 0
    if args.check:
        print(f"n21_conjugation_noise: {check(json.loads(args.check.read_text(encoding='utf-8')), args.all_seeds)}")
        return 0
    if args.merge:
        _require(args.out is not None, "--merge needs --out")
        merged = merge([json.loads(path.read_text(encoding="utf-8")) for path in args.merge])
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf-8")
        return 0
    _require(args.challenger and args.snapshots and args.out, "--challenger, --snapshots and --out are required")
    challenger = json.loads(args.challenger.read_text(encoding="utf-8"))
    _require(
        challenger.get("capture") == "n21-linear-conjugation-challenger", "--challenger is not a challenger record"
    )
    record = run(challenger, [path.resolve() for path in args.snapshots])
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
