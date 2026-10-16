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

Both circuits compile with the baseline's preset pass manager on the
captured FakeFez target over the same transpiler seeds, as
``affine_residual_challenger`` compiles its candidates. Admission requires
the checks, no logical-qubit increase, no per-seed regression in routed CZ,
depth or scheduled duration, and a strictly lower median routed CZ. The
cosets come from ``scripts/linear_conjugation_search.py``; a lower surrogate
there is a filter, and this rule decides. The module submits no quantum
work.
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
SKELETON_OPERATIONS = ("h", "if_else", "measure", "reset")
COMPARED_METRICS = ("routed_cz", "depth", "scheduled_duration_dt")


def _baseline_candidate() -> Candidate:
    return next(candidate for candidate in SELECTABLE_CANDIDATES if candidate.name == BASELINE)


def _schedule() -> tuple[int, ...]:
    plan = order_finding_plan(MODULUS, BASE, PHASE_BITS, multiplier_strategy=_baseline_candidate().multiplier_strategy)
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


def equivalence_checks(columns: tuple[int, ...]) -> dict[str, Any]:
    table = linear_encoding(columns)
    checks: dict[str, Any] = {"initial_value": table.index(1)}
    for multiplier in sorted(set(_schedule())):
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


def phase_counts(columns: tuple[int, ...] | None) -> dict[str, int]:
    """Seeded Aer statevector counts of the phase register for one complete circuit."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(method="statevector")
    circuit = transpile(_source(columns), simulator, optimization_level=0)
    counts = simulator.run(circuit, shots=SAMPLED_SHOTS, seed_simulator=SAMPLED_SEED).result().get_counts()
    return dict(sorted(counts.items()))


def total_variation(first: dict[str, int], second: dict[str, int]) -> float:
    keys = first.keys() | second.keys()
    return sum(abs(first.get(key, 0) - second.get(key, 0)) for key in keys) / (2 * SAMPLED_SHOTS)


@lru_cache(maxsize=1)
def _backend() -> FakeFez:
    return FakeFez()


def _source(columns: tuple[int, ...] | None) -> QuantumCircuit:
    if columns is None:
        return _build_source(_baseline_candidate())[0]
    return factor_order_finding(MODULUS, BASE, PHASE_BITS, multiplier_strategy=ENCODED_STRATEGY, work_columns=columns)


def _active_physical_qubits(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits})


def compile_job(job: tuple[tuple[int, ...] | None, int]) -> dict[str, Any]:
    """Compile the baseline (columns None) or one conjugated circuit at one transpiler seed."""
    columns, seed = job
    source = _source(columns)
    backend = _backend()
    compiled = candidate_pass_manager(_baseline_candidate(), seed, backend).run(source)
    return {
        "seed_transpiler": seed,
        "logical_qubits": source.num_qubits,
        "active_physical_qubits": _active_physical_qubits(compiled),
        "routed_cz": int(compiled.count_ops().get("cz", 0)),
        "depth": compiled.depth(),
        "scheduled_duration_dt": int(_gate_time_view(compiled).estimate_duration(backend.target, unit="dt")),
    }


def _record(name: str, columns: tuple[int, ...] | None, runs: list[dict[str, Any]]) -> dict[str, Any]:
    source = _source(columns)
    return {
        "name": name,
        "columns": list(columns) if columns is not None else None,
        "logical_qubits": source.num_qubits,
        "source_operations": dict(sorted((key, int(value)) for key, value in source.count_ops().items())),
        "runs": runs,
        "medians": {metric: statistics.median(run[metric] for run in runs) for metric in COMPARED_METRICS},
    }


def admission(baseline: dict[str, Any], challenger: dict[str, Any], checks_pass: bool) -> dict[str, Any]:
    regressions = [
        {
            "seed_transpiler": challenger_run["seed_transpiler"],
            "metric": metric,
            "baseline": baseline_run[metric],
            "challenger": challenger_run[metric],
        }
        for baseline_run, challenger_run in zip(baseline["runs"], challenger["runs"], strict=True)
        for metric in COMPARED_METRICS
        if challenger_run[metric] > baseline_run[metric]
    ]
    clauses = {
        "logical_equivalence_and_workspace_checks_pass": checks_pass,
        "shared_dynamic_skeleton": all(
            baseline["source_operations"].get(name) == challenger["source_operations"].get(name)
            for name in SKELETON_OPERATIONS
        ),
        "logical_qubits_not_increased": challenger["logical_qubits"] <= baseline["logical_qubits"],
        "every_seed_no_worse_in_cz_depth_duration": not regressions,
        "median_routed_cz_strictly_lower": challenger["medians"]["routed_cz"] < baseline["medians"]["routed_cz"],
    }
    return {
        "clauses": clauses,
        "per_seed_regressions": regressions,
        "verdict": "admitted" if all(clauses.values()) else "rejected",
    }


def capture(search_path: Path, top: int, seeds: tuple[int, ...], output_path: Path | None) -> dict[str, Any]:
    search = json.loads(search_path.read_text(encoding="utf-8"))
    winners = search["summary"]["winners"][:top]
    cosets = [tuple(winner["columns"]) for winner in winners]
    checks = parallel.ordered_map(equivalence_checks, cosets, min_items=2)
    counts = parallel.ordered_map(phase_counts, [None, *cosets], min_items=2)
    for check, coset_counts in zip(checks, counts[1:], strict=True):
        check["sampled_phase_total_variation"] = total_variation(counts[0], coset_counts)
        check["pass"] = check["pass"] and check["sampled_phase_total_variation"] <= SAMPLED_TV_BOUND
    jobs: list[tuple[tuple[int, ...] | None, int]] = [(None, seed) for seed in seeds]
    jobs += [(columns, seed) for columns in cosets for seed in seeds]
    runs = parallel.ordered_map(compile_job, jobs, min_items=2)
    baseline = _record(BASELINE, None, runs[: len(seeds)])
    challengers = []
    for position, (winner, columns, check) in enumerate(zip(winners, cosets, checks, strict=True)):
        start = len(seeds) * (position + 1)
        record = _record(f"conjugated_coset_{winner['index']}", columns, runs[start : start + len(seeds)])
        record["coset_index"] = winner["index"]
        record["surrogate_cx"] = winner["cost"]
        record["checks"] = check
        record["admission"] = admission(baseline, record, check["pass"])
        challengers.append(record)
    admitted = [record for record in challengers if record["admission"]["verdict"] == "admitted"]
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
        "schema_version": 1,
        "capture": "n21-linear-conjugation-challenger",
        "qpu_executed": False,
        "replay_command": " ".join(arguments[:1] + [shlex.quote(argument) for argument in arguments[1:]]),
        "problem": {"modulus": MODULUS, "base": BASE, "phase_bits": PHASE_BITS, "round_multipliers": list(_schedule())},
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
            "logical qubits do not increase, every seed is no worse in routed CZ, depth, and scheduled duration, "
            "and the median routed CZ is strictly lower"
        ),
        "baseline": baseline,
        "challengers": challengers,
        "admitted_coset_indices": [record["coset_index"] for record in admitted],
        "best_admitted": min(admitted, key=lambda record: (record["medians"]["routed_cz"], record["coset_index"]))[
            "coset_index"
        ]
        if admitted
        else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--search", type=Path, required=True, help="merged linear_conjugation_search record")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    seeds = tuple(args.seeds)
    if not seeds or len(set(seeds)) != len(seeds) or args.top < 1:
        raise SystemExit("transpiler seeds must form a nonempty set and --top must be positive")
    record = capture(args.search, args.top, seeds, args.out)
    _write_atomic(args.out, json.dumps(record, indent=2, sort_keys=True) + "\n")
    base = record["baseline"]["medians"]
    print(f"baseline: median_cz={base['routed_cz']} depth={base['depth']} dt={base['scheduled_duration_dt']}")
    for challenger in record["challengers"]:
        medians = challenger["medians"]
        print(
            f"coset {challenger['coset_index']}: surrogate={challenger['surrogate_cx']} "
            f"median_cz={medians['routed_cz']} depth={medians['depth']} dt={medians['scheduled_duration_dt']} "
            f"{challenger['admission']['verdict']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
