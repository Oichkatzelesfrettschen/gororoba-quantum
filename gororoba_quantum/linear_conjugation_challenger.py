"""Admit or reject N=21 order finding conjugated by an uncontrolled linear map B.

The conjugated circuit prepares the work register in B^-1 |1> and applies,
in every round, the one-clean target-flip network of g_k = B^-1 f_k B under
the phase control. Each round then equals (I x B^-1) C(f_k) (I x B), the
operations between rounds touch only the control qubit, and the work
register is never measured, so the phase register carries the baseline's
distribution exactly. The capture checks that chain: g_k is B^-1 f_k B on
all 32 register values, every controlled network maps |c, x, 0> to
|c, g_k^c(x), 0> with amplitude +1 on both control branches, and both
complete circuits share the H, measure, reset and if_else skeleton. As an
independent check, Aer samples both complete circuits with one simulator seed
and the phase-register distributions must agree within a total variation of
SAMPLED_TV_BOUND.

Two problems are admitted separately. The ten-round circuit
factor_order_finding(21, 2, 10) takes the cosets of least schedule surrogate;
the two-round n21-feedback diagnostic factor_order_finding(21, 4, 2), whose
multipliers are 16 and 4, takes the cosets of least s(4) and compiles both
its feed-forward and its no-feed-forward arm. Every circuit compiles with the
baseline's preset pass manager on the captured FakeFez target over the same
transpiler seeds, as ``affine_residual_challenger`` compiles its candidates.
Admission requires the checks, no logical-qubit increase, no per-seed
regression in routed CZ, depth or scheduled duration on any arm, and a
strictly lower median routed CZ on every arm. The cosets come from
``scripts/linear_conjugation_search.py``; a lower surrogate there is a
filter, and this rule decides. ``--check`` recompiles the baseline and the
best admitted coset of each problem and requires the retained runs. The
module submits no quantum work.
"""

from __future__ import annotations

import argparse
import json
import shlex
import statistics
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit_ibm_runtime.fake_provider import FakeFez

import parallel
from compile_evidence import (
    BASE,
    MODULUS,
    OPTIMIZATION_LEVEL,
    PHASE_BITS,
    REPOSITORY_ROOT,
    SELECTABLE_CANDIDATES,
    Candidate,
    _build_source,
    _portable_output_path,
    _sha256,
    _versions,
    _write_atomic,
    candidate_pass_manager,
)
from live_run import _gate_time_view
from modular_arithmetic import (
    _append_controlled_target_flips,
    conjugated_permutation,
    linear_encoding,
    modular_permutation,
)
from order_finding import ENCODED_STRATEGY, factor_order_finding, order_finding_plan
from target_flip import CONTROLLED_CX_COST, TargetCube, target_flip_network

BASELINE = "target_flip_one_clean"
DEFAULT_SEEDS = tuple(range(8))
DEFAULT_TOP = 8
DEFAULT_OUTPUT = REPOSITORY_ROOT / "results/hw_estimate/n21_linear_conjugation_challenger.json"
WIDTH = 5
SIZE = 1 << WIDTH
SOURCE_PATHS = (
    "gororoba_quantum/linear_conjugation_challenger.py",
    "scripts/linear_conjugation_search.py",
    "gororoba_quantum/compile_evidence.py",
    "gororoba_quantum/live_run.py",
    "gororoba_quantum/modular_arithmetic.py",
    "gororoba_quantum/order_finding.py",
    "gororoba_quantum/target_flip.py",
    "requirements.txt",
)
SAMPLED_SHOTS = 4000
SAMPLED_SEED = 7
SAMPLED_TV_BOUND = 0.02
# (base, phase bits, feed-forward arms, search ranking) per admitted problem.
PROBLEMS = {
    "ten_round": (BASE, PHASE_BITS, (True,), "winners"),
    "two_round": (4, 2, (True, False), "s4_winners"),
}
SKELETON_OPERATIONS = ("h", "if_else", "measure", "reset")
COMPARED_METRICS = ("routed_cz", "depth", "scheduled_duration_dt")
# Routed CZ and qubit counts replay exactly on every host. Depth and duration
# follow single-qubit synthesis, whose floating-point rounding depends on the
# BLAS build: one layer and 18 dt of 131,793 separate an AOCL host from pip's
# numpy wheels, so a replay accepts these two within this relative tolerance.
REPLAY_TOLERANCE = 0.002
EXACT_FIELDS = ("seed_transpiler", "logical_qubits", "active_physical_qubits", "routed_cz")


def _baseline_candidate() -> Candidate:
    return next(candidate for candidate in SELECTABLE_CANDIDATES if candidate.name == BASELINE)


def _schedule(problem: str) -> tuple[int, ...]:
    base, phase_bits, _, _ = PROBLEMS[problem]
    plan = order_finding_plan(MODULUS, base, phase_bits, multiplier_strategy=ENCODED_STRATEGY)
    return tuple(resource.multiplier for resource in plan.rounds[plan.leading_identity_rounds :])


def _controlled_network_maps(network: tuple[TargetCube, ...], permutation: tuple[int, ...]) -> bool:
    """|c, x, 0> -> |c, permutation^c(x), 0> with amplitude +1, control on qubit 0 and scratch last."""
    circuit = QuantumCircuit(1 + WIDTH + 1)
    _append_controlled_target_flips(circuit, 0, list(range(1, 1 + WIDTH)), [1 + WIDTH], network)
    matrix = Operator(circuit).data
    for control in (0, 1):
        for value in range(SIZE):
            image = permutation[value] if control else value
            column = control | value << 1
            expected = np.zeros(matrix.shape[0], dtype=complex)
            expected[control | image << 1] = 1
            if not np.allclose(matrix[:, column], expected, atol=1e-12):
                return False
    return True


def equivalence_checks(job: tuple[str, tuple[int, ...]]) -> dict[str, Any]:
    problem, columns = job
    table = linear_encoding(columns)
    checks: dict[str, Any] = {"initial_value": table.index(1)}
    for multiplier in sorted(set(_schedule(problem))):
        f = modular_permutation(MODULUS, multiplier)
        g = conjugated_permutation(f, columns)
        network = target_flip_network(g)
        checks[str(multiplier)] = {
            "conjugation_exhaustive": all(table[g[value]] == f[table[value]] for value in range(SIZE)),
            "controlled_network_both_branches_clean_workspace": _controlled_network_maps(network, g),
            "cx_surrogate": sum(CONTROLLED_CX_COST[cube.control_mask.bit_count()] for cube in network),
        }
    checks["pass"] = all(
        entry["conjugation_exhaustive"] and entry["controlled_network_both_branches_clean_workspace"]
        for key, entry in checks.items()
        if key.isdigit()
    )
    return checks


def source(problem: str, columns: tuple[int, ...] | None, feed_forward: bool) -> QuantumCircuit:
    base, phase_bits, _, _ = PROBLEMS[problem]
    return factor_order_finding(
        MODULUS,
        base,
        phase_bits,
        multiplier_strategy=ENCODED_STRATEGY,
        feed_forward=feed_forward,
        work_columns=columns,
    )


def phase_counts(job: tuple[str, tuple[int, ...] | None, bool]) -> dict[str, int]:
    """Seeded Aer statevector counts of the phase register for one complete circuit."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(method="statevector")
    circuit = transpile(source(*job), simulator, optimization_level=0)
    counts = simulator.run(circuit, shots=SAMPLED_SHOTS, seed_simulator=SAMPLED_SEED).result().get_counts()
    return dict(sorted(counts.items()))


def total_variation(first: dict[str, int], second: dict[str, int]) -> float:
    keys = first.keys() | second.keys()
    return sum(abs(first.get(key, 0) - second.get(key, 0)) for key in keys) / (2 * SAMPLED_SHOTS)


@lru_cache(maxsize=1)
def _backend() -> FakeFez:
    return FakeFez()


def _active_physical_qubits(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits})


def compile_job(job: tuple[str, tuple[int, ...] | None, bool, int]) -> dict[str, Any]:
    """Compile one arm of the baseline (columns None) or of one encoded circuit at one transpiler seed."""
    problem, columns, feed_forward, seed = job
    circuit = source(problem, columns, feed_forward)
    backend = _backend()
    compiled = candidate_pass_manager(_baseline_candidate(), seed, backend).run(circuit)
    return {
        "seed_transpiler": seed,
        "logical_qubits": circuit.num_qubits,
        "active_physical_qubits": _active_physical_qubits(compiled),
        "routed_cz": int(compiled.count_ops().get("cz", 0)),
        "depth": compiled.depth(),
        "scheduled_duration_dt": int(_gate_time_view(compiled).estimate_duration(backend.target, unit="dt")),
    }


def _arm_name(feed_forward: bool) -> str:
    return "feed_forward" if feed_forward else "no_feed_forward"


def _record(problem: str, name: str, columns: tuple[int, ...] | None, runs: dict[str, list[Any]]) -> dict[str, Any]:
    arms = {}
    for feed_forward in PROBLEMS[problem][2]:
        circuit = source(problem, columns, feed_forward)
        arm_runs = runs[_arm_name(feed_forward)]
        arms[_arm_name(feed_forward)] = {
            "logical_qubits": circuit.num_qubits,
            "source_operations": dict(sorted((key, int(value)) for key, value in circuit.count_ops().items())),
            "runs": arm_runs,
            "medians": {metric: statistics.median(run[metric] for run in arm_runs) for metric in COMPARED_METRICS},
        }
    return {"name": name, "columns": list(columns) if columns is not None else None, "arms": arms}


def admission(baseline: dict[str, Any], challenger: dict[str, Any], checks_pass: bool) -> dict[str, Any]:
    regressions = [
        {
            "arm": arm,
            "seed_transpiler": challenger_run["seed_transpiler"],
            "metric": metric,
            "baseline": baseline_run[metric],
            "challenger": challenger_run[metric],
        }
        for arm, base_arm in baseline["arms"].items()
        for baseline_run, challenger_run in zip(base_arm["runs"], challenger["arms"][arm]["runs"], strict=True)
        for metric in COMPARED_METRICS
        if challenger_run[metric] > baseline_run[metric]
    ]
    arms = list(baseline["arms"])
    clauses = {
        "logical_equivalence_and_workspace_checks_pass": checks_pass,
        "shared_dynamic_skeleton": all(
            baseline["arms"][arm]["source_operations"].get(name)
            == challenger["arms"][arm]["source_operations"].get(name)
            for arm in arms
            for name in SKELETON_OPERATIONS
        ),
        "logical_qubits_not_increased": all(
            challenger["arms"][arm]["logical_qubits"] <= baseline["arms"][arm]["logical_qubits"] for arm in arms
        ),
        "every_seed_no_worse_in_cz_depth_duration": not regressions,
        "median_routed_cz_strictly_lower": all(
            challenger["arms"][arm]["medians"]["routed_cz"] < baseline["arms"][arm]["medians"]["routed_cz"]
            for arm in arms
        ),
    }
    return {
        "clauses": clauses,
        "per_seed_regressions": regressions,
        "verdict": "admitted" if all(clauses.values()) else "rejected",
    }


def best_admitted(challengers: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The admitted challenger with the fewest median routed CZ summed over arms, then the lowest coset index."""
    return min(
        (record for record in challengers if record["admission"]["verdict"] == "admitted"),
        key=lambda record: (
            sum(arm["medians"]["routed_cz"] for arm in record["arms"].values()),
            record["coset_index"],
        ),
        default=None,
    )


def _problem_record(problem: str, winners: list[dict[str, Any]], seeds: tuple[int, ...]) -> dict[str, Any]:
    arms = PROBLEMS[problem][2]
    cosets = [tuple(winner["columns"]) for winner in winners]
    checks = parallel.ordered_map(equivalence_checks, [(problem, columns) for columns in cosets], min_items=2)
    count_jobs = [(problem, columns, feed_forward) for columns in [None, *cosets] for feed_forward in arms]
    counts = parallel.ordered_map(phase_counts, count_jobs, min_items=2)
    for position, check in enumerate(checks):
        variations = [
            total_variation(counts[arm], counts[len(arms) * (position + 1) + arm]) for arm in range(len(arms))
        ]
        check["sampled_phase_total_variation"] = max(variations)
        check["pass"] = check["pass"] and check["sampled_phase_total_variation"] <= SAMPLED_TV_BOUND
    jobs = [
        (problem, columns, feed_forward, seed) for columns in [None, *cosets] for feed_forward in arms for seed in seeds
    ]
    runs = parallel.ordered_map(compile_job, jobs, min_items=2)
    per_circuit = len(arms) * len(seeds)

    def arm_runs(position: int) -> dict[str, list[Any]]:
        block = runs[position * per_circuit : (position + 1) * per_circuit]
        return {
            _arm_name(feed_forward): block[index * len(seeds) : (index + 1) * len(seeds)]
            for index, feed_forward in enumerate(arms)
        }

    baseline = _record(problem, BASELINE, None, arm_runs(0))
    challengers = []
    for position, (winner, columns, check) in enumerate(zip(winners, cosets, checks, strict=True)):
        record = _record(problem, f"encoded_coset_{winner['index']}", columns, arm_runs(position + 1))
        record["coset_index"] = winner["index"]
        record["surrogate"] = {"s4": winner["s4"], "s2": winner["s2"], "ten_round_cost": winner["cost"]}
        record["checks"] = check
        record["admission"] = admission(baseline, record, check["pass"])
        challengers.append(record)
    admitted = [record for record in challengers if record["admission"]["verdict"] == "admitted"]
    best = best_admitted(challengers)
    base, phase_bits, _, ranking = PROBLEMS[problem]
    return {
        "circuit": f"factor_order_finding({MODULUS}, {base}, {phase_bits})",
        "round_multipliers": list(_schedule(problem)),
        "ranking": ranking,
        "arms": [_arm_name(feed_forward) for feed_forward in arms],
        "baseline": baseline,
        "challengers": challengers,
        "admitted_coset_indices": [record["coset_index"] for record in admitted],
        "best_admitted": best["coset_index"] if best is not None else None,
    }


def capture(search_path: Path, top: int, seeds: tuple[int, ...], output_path: Path | None) -> dict[str, Any]:
    search = json.loads(search_path.read_text(encoding="utf-8"))
    baseline_source = _build_source(_baseline_candidate())[0]
    _require(
        dict(baseline_source.count_ops()) == dict(source("ten_round", None, True).count_ops()),
        "factor_order_finding's ten-round baseline differs from compile_evidence's target_flip_one_clean source",
    )
    problems = {
        problem: _problem_record(problem, search["summary"][ranking][:top], seeds)
        for problem, (_, _, _, ranking) in PROBLEMS.items()
    }
    arguments = ['"$PYTHON"', "gororoba_quantum/linear_conjugation_challenger.py", "--search", str(search_path)]
    if top != DEFAULT_TOP:
        arguments.extend(("--top", str(top)))
    if seeds != DEFAULT_SEEDS:
        arguments.extend(("--seeds", *(str(seed) for seed in seeds)))
    portable_output = _portable_output_path(output_path)
    if portable_output is not None:
        arguments.extend(("--out", portable_output))
    backend = _backend()
    return {
        "schema_version": 2,
        "capture": "n21-linear-conjugation-challenger",
        "qpu_executed": False,
        "replay_command": " ".join(arguments[:1] + [shlex.quote(argument) for argument in arguments[1:]]),
        "modulus": MODULUS,
        "compiler": {
            "target": "qiskit_ibm_runtime.fake_provider.FakeFez",
            "optimization_level": OPTIMIZATION_LEVEL,
            "pass_manager": f"candidate_pass_manager({BASELINE}) for every circuit",
            "seeds": list(seeds),
            "dt_seconds": backend.target.dt,
            "versions": _versions(),
        },
        "duration_model": (
            "estimate_duration over the true-branch gate-time view; a lower bound that omits classical "
            "feed-forward latency, common to every circuit through the shared dynamic skeleton"
        ),
        "search_record_sha256": _sha256(search_path),
        "source_files_sha256": {path: _sha256(REPOSITORY_ROOT / path) for path in SOURCE_PATHS},
        "sampled_phase_check": {
            "shots": SAMPLED_SHOTS,
            "seed": SAMPLED_SEED,
            "total_variation_bound": SAMPLED_TV_BOUND,
        },
        "rule": (
            "admit a coset only when its equivalence and workspace checks pass, the dynamic skeleton matches, "
            "logical qubits do not increase, every seed of every arm is no worse in routed CZ, depth, and "
            "scheduled duration, and the median routed CZ is strictly lower on every arm"
        ),
        "problems": problems,
    }


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"linear_conjugation_challenger: {message}")


def replay_matches(recompiled: dict[str, Any], retained: dict[str, Any]) -> float | None:
    """The largest relative depth or duration deviation, or None when an exact field differs."""
    if any(recompiled[field] != retained[field] for field in EXACT_FIELDS):
        return None
    return max(
        abs(recompiled[metric] - retained[metric]) / retained[metric] for metric in ("depth", "scheduled_duration_dt")
    )


def check(record: dict[str, Any]) -> str:
    """Recompile the baseline and the best admitted coset of every problem and re-derive their admission.

    Exact fields must match; depth and duration within REPLAY_TOLERANCE; and the
    best coset's admission, recomputed from the recompiled runs of both, must
    keep its verdict.
    """
    _require(record.get("capture") == "n21-linear-conjugation-challenger", "not a challenger record")
    _require(set(record["problems"]) == set(PROBLEMS), f"the record covers {sorted(record['problems'])}")
    seeds = tuple(record["compiler"]["seeds"])
    replayed = 0
    deviation = 0.0
    for problem, entry in record["problems"].items():
        arms = PROBLEMS[problem][2]
        circuits: list[tuple[dict[str, Any], tuple[int, ...] | None]] = [(entry["baseline"], None)]
        best = best_admitted(entry["challengers"])
        derived = best["coset_index"] if best is not None else None
        _require(
            entry["best_admitted"] == derived, f"{problem}: best_admitted {entry['best_admitted']} is not {derived}"
        )
        if best is not None:
            circuits.append((best, tuple(best["columns"])))
            _require(equivalence_checks((problem, tuple(best["columns"])))["pass"], f"{problem}: best coset fails")
        rebuilt = []
        for retained, columns in circuits:
            jobs = [(problem, columns, feed_forward, seed) for feed_forward in arms for seed in seeds]
            runs = parallel.ordered_map(compile_job, jobs, min_items=2)
            expected = [run for feed_forward in arms for run in retained["arms"][_arm_name(feed_forward)]["runs"]]
            for run, kept in zip(runs, expected, strict=True):
                matched = replay_matches(run, kept)
                if matched is None or matched > REPLAY_TOLERANCE:
                    raise SystemExit(
                        f"linear_conjugation_challenger: {problem} {retained['name']} seed "
                        f"{kept['seed_transpiler']}: recompiled {run} against {kept}"
                    )
                deviation = max(deviation, matched)
            per_arm = {
                _arm_name(feed_forward): runs[index * len(seeds) : (index + 1) * len(seeds)]
                for index, feed_forward in enumerate(arms)
            }
            rebuilt.append(_record(problem, retained["name"], columns, per_arm))
            replayed += len(runs)
        if best is not None:
            verdict = admission(rebuilt[0], rebuilt[1], best["checks"]["pass"])["verdict"]
            _require(verdict == best["admission"]["verdict"], f"{problem}: the recompiled admission is {verdict}")
        for challenger in entry["challengers"]:
            verdict = admission(entry["baseline"], challenger, challenger["checks"]["pass"])
            _require(verdict == challenger["admission"], f"{problem} {challenger['name']}: admission differs")
    return f"{replayed} compilations replayed (largest depth or duration deviation {deviation:.5f}); best " + ", ".join(
        f"{problem}={entry['best_admitted']}" for problem, entry in record["problems"].items()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--search", type=Path, help="merged linear_conjugation_search record")
    mode.add_argument("--check", type=Path, help="retained challenger record to replay")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.check:
        print(f"linear_conjugation_challenger: {check(json.loads(args.check.read_text(encoding='utf-8')))}")
        return 0
    seeds = tuple(args.seeds)
    if not seeds or len(set(seeds)) != len(seeds) or args.top < 1:
        raise SystemExit("transpiler seeds must form a nonempty set and --top must be positive")
    record = capture(args.search, args.top, seeds, args.out)
    _write_atomic(args.out, json.dumps(record, indent=2, sort_keys=True) + "\n")
    for problem, entry in record["problems"].items():
        for candidate in [entry["baseline"], *entry["challengers"]]:
            medians = "; ".join(
                f"{arm} cz={values['medians']['routed_cz']} depth={values['medians']['depth']} "
                f"dt={values['medians']['scheduled_duration_dt']}"
                for arm, values in candidate["arms"].items()
            )
            verdict = candidate.get("admission", {}).get("verdict", "baseline")
            print(f"{problem} {candidate['name']}: {medians} {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
