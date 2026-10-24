"""Admit or reject the N=21 affine-residual multiplier against one-clean target flips.

Both candidates build the complete ten-round order-finding circuit through
``compile_evidence._build_source`` and compile with the same preset pass
manager, captured FakeFez target, and transpiler seeds. Scheduled duration is
the ``estimate_duration`` of ``live_run._gate_time_view``, a lower bound that
omits classical feed-forward latency; both circuits carry the same H, measure,
reset, and if_else skeleton, so the omitted latency is common to them.

Admission requires the exhaustive logical and workspace checks of
``affine_residual.verification_record``, no logical-qubit increase, no
per-seed regression in routed CZ, depth, or scheduled duration, and a
strictly lower median routed CZ. A rejection is a complete result. The module
submits no quantum work.
"""

from __future__ import annotations

import argparse
import json
import shlex
import statistics
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit
from qiskit_ibm_runtime.fake_provider import FakeFez

import qrng_seeds
from affine_residual import affine_residual_synthesis, minimum_cnot_count, network_cx_surrogate, verification_record
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
from modular_arithmetic import modular_permutation
from order_finding import order_finding_plan
from target_flip import CONTROLLED_CX_COST, target_flip_network

BASELINE = "target_flip_one_clean"
CHALLENGER = "affine_residual_target_flip"
DEFAULT_SEEDS = tuple(range(8))
DEFAULT_OUTPUT = REPOSITORY_ROOT / "results/hw_estimate/n21_affine_residual_challenger.json"
CANDIDATE_SOURCE = "gororoba_quantum/affine_residual.py"
SOURCE_PATHS = (
    CANDIDATE_SOURCE,
    "gororoba_quantum/affine_residual_challenger.py",
    "gororoba_quantum/boolean_anf.py",
    "gororoba_quantum/compile_evidence.py",
    "gororoba_quantum/live_run.py",
    "gororoba_quantum/modular_arithmetic.py",
    "gororoba_quantum/order_finding.py",
    "gororoba_quantum/target_flip.py",
    "requirements.txt",
)
SKELETON_OPERATIONS = ("h", "if_else", "measure", "reset")
COMPARED_METRICS = ("routed_cz", "depth", "scheduled_duration_dt")


def _candidate(name: str) -> Candidate:
    return next(candidate for candidate in SELECTABLE_CANDIDATES if candidate.name == name)


def _active_physical_qubits(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits})


def _compile_run(candidate: Candidate, source: QuantumCircuit, seed: int, backend: FakeFez) -> dict[str, Any]:
    compiled = candidate_pass_manager(candidate, seed, backend).run(source)
    duration_dt = int(_gate_time_view(compiled).estimate_duration(backend.target, unit="dt"))
    return {
        "seed_transpiler": seed,
        "logical_qubits": source.num_qubits,
        "active_physical_qubits": _active_physical_qubits(compiled),
        "routed_cz": int(compiled.count_ops().get("cz", 0)),
        "depth": compiled.depth(),
        "scheduled_duration_dt": duration_dt,
    }


def _candidate_record(name: str, seeds: tuple[int, ...], backend: FakeFez) -> dict[str, Any]:
    candidate = _candidate(name)
    source, coefficients = _build_source(candidate)
    runs = []
    for seed in seeds:
        run = _compile_run(candidate, source, seed, backend)
        print(
            f"compiled candidate={name} seed={seed} cz={run['routed_cz']} depth={run['depth']} "
            f"duration_dt={run['scheduled_duration_dt']}",
            file=sys.stderr,
            flush=True,
        )
        runs.append(run)
    return {
        "name": name,
        "multiplier_strategy": candidate.multiplier_strategy,
        "workspace_contract": candidate.workspace_contract,
        "logical_qubits": source.num_qubits,
        "logical_coefficients": coefficients,
        "source_operations": dict(sorted((key, int(value)) for key, value in source.count_ops().items())),
        "runs": runs,
        "medians": {
            metric: statistics.median(run[metric] for run in runs)
            for metric in ("active_physical_qubits", *COMPARED_METRICS)
        },
    }


def _surrogate_record() -> dict[str, Any]:
    """Count phase-controlled CX equivalents over the ten-round schedule before routing.

    ``minimum_linear_bound`` keeps the residual network and replaces the
    Gauss-Jordan CNOTs by the minimum in-place CNOT count of A, each promoted
    to a Toffoli of weight ``CONTROLLED_CX_COST[1]``. It bounds the direct
    composition with promoted CNOTs; conjugated or relabeled controlled-linear
    constructions lie outside it.
    """
    plan = order_finding_plan(MODULUS, BASE, PHASE_BITS)
    schedule = [resource.multiplier for resource in plan.rounds[plan.leading_identity_rounds :]]
    per_multiplier: dict[int, dict[str, int]] = {}
    for multiplier in sorted(set(schedule)):
        permutation = modular_permutation(MODULUS, multiplier)
        synthesis = affine_residual_synthesis(permutation)
        residual_only = network_cx_surrogate(synthesis.residual_network)
        minimum_cnots = minimum_cnot_count(synthesis.skeleton.linear_rows, synthesis.skeleton.width)
        per_multiplier[multiplier] = {
            "baseline": network_cx_surrogate(target_flip_network(permutation)),
            "challenger": network_cx_surrogate(synthesis.network),
            "minimum_linear_bound": residual_only
            + CONTROLLED_CX_COST[1] * minimum_cnots
            + CONTROLLED_CX_COST[0] * synthesis.skeleton.constant.bit_count(),
            "residual_only": residual_only,
        }
    return {
        "weights": "phase-controlled CX equivalents per cube with 0-4 data controls: "
        + "/".join(str(cost) for cost in CONTROLLED_CX_COST),
        "round_multipliers": schedule,
        "per_multiplier": {str(multiplier): counts for multiplier, counts in per_multiplier.items()},
        "ten_round_totals": {
            key: sum(per_multiplier[multiplier][key] for multiplier in schedule)
            for key in ("baseline", "challenger", "minimum_linear_bound", "residual_only")
        },
    }


def _admission(
    baseline: dict[str, Any], challenger: dict[str, Any], checks_pass: bool, skeleton_matches: bool
) -> dict[str, Any]:
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
        "shared_dynamic_skeleton": skeleton_matches,
        "logical_qubits_not_increased": challenger["logical_qubits"] <= baseline["logical_qubits"],
        "every_seed_no_worse_in_cz_depth_duration": not regressions,
        "median_routed_cz_strictly_lower": challenger["medians"]["routed_cz"] < baseline["medians"]["routed_cz"],
    }
    return {
        "rule": (
            "admit only when the exhaustive logical-equivalence and workspace checks pass, logical qubits do not "
            "increase, every seed is no worse in routed CZ, depth, and scheduled duration, and the median routed "
            "CZ is strictly lower"
        ),
        "clauses": clauses,
        "per_seed_regressions": regressions,
        "verdict": "admitted" if all(clauses.values()) else "rejected",
    }


def capture(
    seeds: tuple[int, ...], output_path: Path | None, seed_spellings: list[str] | None = None
) -> dict[str, Any]:
    """Run the checks, compile both candidates, and evaluate the admission rule."""
    synthesis = verification_record(MODULUS, (2, 4, 16))
    checks_pass = all(
        entry["checks"]["composition_a_after_r_equals_f"]
        and entry["checks"]["controlled_operator_both_branches_clean_workspace"]
        for entry in synthesis["multipliers"]
    )
    backend = FakeFez()
    baseline = _candidate_record(BASELINE, seeds, backend)
    challenger = _candidate_record(CHALLENGER, seeds, backend)
    skeleton_matches = all(
        baseline["source_operations"].get(name) == challenger["source_operations"].get(name)
        for name in SKELETON_OPERATIONS
    )
    arguments = ['"$PYTHON"', "gororoba_quantum/affine_residual_challenger.py"]
    if seeds != DEFAULT_SEEDS:
        arguments.extend(("--seeds", *(seed_spellings if seed_spellings is not None else map(str, seeds))))
    portable_output = _portable_output_path(output_path)
    if portable_output is not None:
        arguments.extend(("--out", portable_output))
    return {
        "schema_version": 1,
        "capture": "n21-affine-residual-challenger",
        "qpu_executed": False,
        "replay_command": " ".join(arguments[:1] + [shlex.quote(argument) for argument in arguments[1:]]),
        "problem": {"modulus": MODULUS, "base": BASE, "phase_bits": PHASE_BITS},
        "compiler": {
            "target": "qiskit_ibm_runtime.fake_provider.FakeFez",
            "optimization_level": OPTIMIZATION_LEVEL,
            "seeds": list(seeds),
            "dt_seconds": backend.target.dt,
            "versions": _versions(),
        },
        "duration_model": (
            "estimate_duration over the true-branch gate-time view; a lower bound that omits classical "
            "feed-forward latency, common to both candidates through their shared dynamic skeleton"
        ),
        "candidate_source_sha256": _sha256(REPOSITORY_ROOT / CANDIDATE_SOURCE),
        "source_files_sha256": {path: _sha256(REPOSITORY_ROOT / path) for path in SOURCE_PATHS},
        "synthesis": synthesis,
        "surrogate_cx": _surrogate_record(),
        "candidates": [baseline, challenger],
        "admission": _admission(baseline, challenger, checks_pass, skeleton_matches),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    qrng_seeds.add_seed_argument(parser, "--seeds", nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = _parser().parse_args()
    seeds = tuple(args.seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("transpiler seeds must form a nonempty set")
    non_default = any(source != "default" for source in args.seeds_source)
    record = capture(seeds, args.out, qrng_seeds.spellings(seeds, args.seeds_source) if non_default else None)
    if non_default:
        record["seed_source"] = qrng_seeds.seed_record(
            "gororoba_quantum/affine_residual_challenger.py",
            "--seeds",
            qrng_seeds.repo_relative(args.out),
            args.seeds_source,
        )
    _write_atomic(args.out, json.dumps(record, indent=2, sort_keys=True) + "\n")
    for candidate in record["candidates"]:
        medians = candidate["medians"]
        print(
            f"{candidate['name']}: logical_qubits={candidate['logical_qubits']} "
            f"median_cz={medians['routed_cz']} median_depth={medians['depth']} "
            f"median_duration_dt={medians['scheduled_duration_dt']}"
        )
    admission = record["admission"]
    failed = sorted(name for name, passed in admission["clauses"].items() if not passed)
    print(f"verdict: {admission['verdict']}" + (f" (failed: {', '.join(failed)})" if failed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
