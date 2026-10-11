"""Capture the N=21 modular-synthesis crossover on the static FakeFez target.

The capture compares target-flip, scratch-free, one-clean, two-clean, and ANF arithmetic
under fixed transpiler seeds. The pass callback records every change in qubit
count, recursive depth, or operation census so synthesis cost and heavy-hex
routing amplification remain separate evidence surfaces. The module submits
no quantum work.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shlex
import statistics
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes.synthesis import HLSConfig
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeFez

from order_finding import factor_order_finding, order_finding_plan

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = tuple(range(20_261_010, 20_261_018))
OPTIMIZATION_LEVEL = 3
MODULUS = 21
BASE = 2
PHASE_BITS = 10
NAMED_PASSES = frozenset({"HighLevelSynthesis", "BasisTranslator", "SabreLayout"})
SOURCE_PATHS = (
    "gororoba_quantum/boolean_anf.py",
    "gororoba_quantum/compile_evidence.py",
    "gororoba_quantum/factoring.py",
    "gororoba_quantum/hybrid_shor.py",
    "gororoba_quantum/modular_arithmetic.py",
    "gororoba_quantum/order_finding.py",
    "gororoba_quantum/target_flip.py",
    "gororoba_quantum/target_flip_certificate.py",
    "proofs/TargetFlipN21.v",
    "scripts/python_call_graph.py",
    "pyproject.toml",
    "requirements.txt",
)


@dataclass(frozen=True)
class Candidate:
    """One controlled-modular-multiplication synthesis contract."""

    name: str
    multiplier_strategy: str
    compiler_workspace_qubits: int
    mcx_hls_method: str | None
    workspace_contract: str


CANDIDATES = (
    Candidate(
        name="target_flip_one_clean",
        multiplier_strategy="target_flip_1_clean",
        compiler_workspace_qubits=0,
        mcx_hls_method=None,
        workspace_contract="one clean workspace restored after each exact Boolean target flip",
    ),
    Candidate(
        name="scratch_free_cycle",
        multiplier_strategy="cycle_transpositions",
        compiler_workspace_qubits=0,
        mcx_hls_method="noaux_v24",
        workspace_contract="zero workspace qubits; explicitly pinned no-auxiliary MCX synthesis",
    ),
    Candidate(
        name="one_clean_cycle",
        multiplier_strategy="cycle_transpositions_1_clean",
        compiler_workspace_qubits=0,
        mcx_hls_method=None,
        workspace_contract="one clean arithmetic workspace qubit restored after every multiplier",
    ),
    Candidate(
        name="two_clean_cycle_control",
        multiplier_strategy="cycle_transpositions",
        compiler_workspace_qubits=2,
        mcx_hls_method="2_clean_kg24",
        workspace_contract="two clean compiler workspace qubits available to every opaque MCX",
    ),
    Candidate(
        name="anf_compute_swap_uncompute",
        multiplier_strategy="anf_compute_swap_uncompute",
        compiler_workspace_qubits=0,
        mcx_hls_method=None,
        workspace_contract="five computed-output qubits restored after each compute-swap-uncompute multiplier",
    ),
)


def _canonical_operation_counts(operation_counts: dict[str, int]) -> dict[str, int]:
    canonical_counts: Counter[str] = Counter()
    for operation_name, count in operation_counts.items():
        canonical_name = "mcx_open" if operation_name.startswith("mcx_o") else operation_name
        canonical_counts[canonical_name] += int(count)
    return dict(sorted(canonical_counts.items()))


def _circuit_snapshot(circuit: QuantumCircuit) -> dict[str, Any]:
    return _dag_snapshot(circuit_to_dag(circuit))


def _dag_snapshot(dag: Any) -> dict[str, Any]:
    return {
        "qubits": dag.num_qubits(),
        "depth": dag.depth(recurse=True),
        "operations": _canonical_operation_counts(dict(dag.count_ops(recurse=True))),
    }


def _snapshot_signature(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":"))


def _build_source(candidate: Candidate, phase_bits: int = PHASE_BITS) -> tuple[QuantumCircuit, dict[str, Any]]:
    plan = order_finding_plan(
        MODULUS,
        BASE,
        phase_bits,
        multiplier_strategy=candidate.multiplier_strategy,
    )
    circuit = factor_order_finding(
        MODULUS,
        BASE,
        phase_bits,
        multiplier_strategy=candidate.multiplier_strategy,
    )
    if candidate.compiler_workspace_qubits:
        circuit.add_register(QuantumRegister(candidate.compiler_workspace_qubits, "compiler_workspace"))
    coefficients = {
        "input_domain": plan.input_domain,
        "work_qubits": plan.work_qubits,
        "phase_bits": plan.phase_bits,
        "arithmetic_workspace_qubits": plan.scratch_qubits,
        "compiler_workspace_qubits": candidate.compiler_workspace_qubits,
        "basis_edge_gates": plan.basis_edge_gates,
        "controlled_target_flips": plan.controlled_target_flips,
        "control_arity_histogram": [
            {"controls": controls, "gate_count": count} for controls, count in plan.control_arity_histogram
        ],
        "forward_anf_terms": plan.forward_anf_terms,
        "inverse_anf_terms": plan.inverse_anf_terms,
        "degree_histogram": [
            {"degree": degree, "term_count": term_count} for degree, term_count in plan.degree_histogram
        ],
        "controlled_swaps": plan.controlled_swaps,
        "controlled_x_gates": plan.controlled_x_gates,
        "maximum_control_count": plan.maximum_control_count,
        "unique_multipliers": list(plan.unique_multipliers),
    }
    return circuit, coefficients


def _pass_capture(
    source_snapshot: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Any]:
    aggregate_resource_transitions: list[dict[str, Any]] = []
    named_snapshots: list[dict[str, Any]] = []
    previous_signature = _snapshot_signature(source_snapshot)

    def capture_callback(**callback_payload: object) -> None:
        nonlocal previous_signature
        compiler_pass = cast(Any, callback_payload["pass_"])
        dag = cast(Any, callback_payload["dag"])
        pass_index = int(cast(Any, callback_payload["count"]))
        pass_name = str(compiler_pass.name())
        snapshot = _dag_snapshot(dag)
        entry = {"pass_index": pass_index, "pass_name": pass_name, **snapshot}
        if pass_name in NAMED_PASSES:
            named_snapshots.append(entry)
        signature = _snapshot_signature(snapshot)
        if signature != previous_signature:
            aggregate_resource_transitions.append(entry)
            previous_signature = signature

    return aggregate_resource_transitions, named_snapshots, capture_callback


def _stage_snapshots(
    source_snapshot: dict[str, Any],
    named_snapshots: list[dict[str, Any]],
    final_snapshot: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    stages = {"source": source_snapshot}
    high_level_synthesis = [entry for entry in named_snapshots if entry["pass_name"] == "HighLevelSynthesis"]
    if high_level_synthesis:
        stages["after_high_level_synthesis"] = high_level_synthesis[0]

    layout_snapshots = [entry for entry in named_snapshots if entry["pass_name"] == "SabreLayout"]
    if layout_snapshots:
        layout_snapshot = layout_snapshots[0]
        layout_pass_index = int(layout_snapshot["pass_index"])
        before_layout = [
            entry
            for entry in named_snapshots
            if entry["pass_name"] == "BasisTranslator" and int(entry["pass_index"]) < layout_pass_index
        ]
        after_layout = [
            entry
            for entry in named_snapshots
            if entry["pass_name"] == "BasisTranslator" and int(entry["pass_index"]) > layout_pass_index
        ]
        if before_layout:
            stages["pre_routing_basis_translation"] = before_layout[-1]
        stages["after_layout_routing"] = layout_snapshot
        if after_layout:
            stages["post_routing_basis_translation"] = after_layout[0]
    stages["final"] = final_snapshot
    return stages


def _compile_candidate(
    candidate: Candidate, seed: int, backend: FakeFez, phase_bits: int = PHASE_BITS
) -> dict[str, Any]:
    source, _ = _build_source(candidate, phase_bits)
    source_snapshot = _circuit_snapshot(source)
    hls_config = HLSConfig(mcx=[candidate.mcx_hls_method]) if candidate.mcx_hls_method is not None else None
    pass_manager = generate_preset_pass_manager(
        optimization_level=OPTIMIZATION_LEVEL,
        backend=backend,
        seed_transpiler=seed,
        hls_config=hls_config,
    )
    aggregate_resource_transitions, named_snapshots, callback = _pass_capture(source_snapshot)
    compiled = pass_manager.run(source, callback=callback)
    final_snapshot = _circuit_snapshot(compiled)
    if compiled.layout is None:
        raise RuntimeError(f"{candidate.name} seed {seed} produced no transpiler layout")
    initial_layout = compiled.layout.initial_index_layout(filter_ancillas=True)
    final_layout = compiled.layout.final_index_layout(filter_ancillas=True)
    logical_qubits = source.num_qubits
    if len(initial_layout) != logical_qubits or len(final_layout) != logical_qubits:
        raise RuntimeError(
            f"{candidate.name} seed {seed} layout lengths "
            f"{len(initial_layout)} and {len(final_layout)} do not match {logical_qubits} logical qubits"
        )
    return {
        "seed_transpiler": seed,
        "initial_layout": initial_layout,
        "final_layout": final_layout,
        "cz_count": int(compiled.count_ops().get("cz", 0)),
        "depth": compiled.depth(),
        "final_operations": _canonical_operation_counts(dict(compiled.count_ops())),
        "stage_snapshots": _stage_snapshots(source_snapshot, named_snapshots, final_snapshot),
        "aggregate_resource_transitions": aggregate_resource_transitions,
    }


def _metric_summary(runs: list[dict[str, Any]], metric: str) -> dict[str, int | float]:
    values = [int(run[metric]) for run in runs]
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": statistics.fmean(values),
    }


def _candidate_record(
    candidate: Candidate, seeds: tuple[int, ...], backend: FakeFez, phase_bits: int = PHASE_BITS
) -> dict[str, Any]:
    source, coefficients = _build_source(candidate, phase_bits)
    runs: list[dict[str, Any]] = []
    for seed in seeds:
        print(f"compile candidate={candidate.name} seed={seed}", file=sys.stderr, flush=True)
        run = _compile_candidate(candidate, seed, backend, phase_bits)
        print(
            f"compiled candidate={candidate.name} seed={seed} cz={run['cz_count']} depth={run['depth']}",
            file=sys.stderr,
            flush=True,
        )
        runs.append(run)
    return {
        "name": candidate.name,
        "multiplier_strategy": candidate.multiplier_strategy,
        "mcx_hls_method": candidate.mcx_hls_method,
        "workspace_contract": candidate.workspace_contract,
        "logical_coefficients": coefficients,
        "source": _circuit_snapshot(source),
        "runs": runs,
        "summary": {
            "cz_count": _metric_summary(runs, "cz_count"),
            "depth": _metric_summary(runs, "depth"),
        },
    }


def _backend_record(backend: FakeFez) -> dict[str, Any]:
    if backend.coupling_map is None:
        raise RuntimeError("FakeFez supplies no coupling map")
    undirected_edges = sorted({tuple(sorted(edge)) for edge in backend.coupling_map.get_edges()})
    degrees = [0] * backend.num_qubits
    for first_qubit, second_qubit in undirected_edges:
        degrees[first_qubit] += 1
        degrees[second_qubit] += 1
    degree_counts = Counter(degrees)
    return {
        "class": "qiskit_ibm_runtime.fake_provider.FakeFez",
        "evidence_surface": "static compiler target; not a live calibration or noise prediction",
        "qubits": backend.num_qubits,
        "undirected_edge_count": len(undirected_edges),
        "undirected_edges": [list(edge) for edge in undirected_edges],
        "maximum_degree": max(degrees),
        "degree_histogram": [
            {"degree": degree, "qubit_count": count} for degree, count in sorted(degree_counts.items())
        ],
        "target_operations": sorted(backend.operation_names),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_output(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", *arguments],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _source_record() -> dict[str, Any]:
    source_files = {path: _sha256(REPOSITORY_ROOT / path) for path in SOURCE_PATHS}
    source_diff = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "diff", "--quiet", "HEAD", "--", *SOURCE_PATHS],
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    if source_diff.returncode not in (0, 1):
        raise RuntimeError(f"git diff returned status {source_diff.returncode}")
    return {
        "commit": _git_output("rev-parse", "HEAD"),
        "source_files_match_commit": source_diff.returncode == 0,
        "files_sha256": source_files,
    }


def _versions() -> dict[str, str]:
    packages = (
        "numpy",
        "qiskit",
        "qiskit-aer",
        "qiskit-ibm-runtime",
        "rustworkx",
        "scipy",
    )
    return {"python": platform.python_version()} | {
        package_name: importlib.metadata.version(package_name) for package_name in packages
    }


def _portable_output_path(output_path: Path | None) -> str | None:
    if output_path is None:
        return None
    resolved_output = output_path.resolve()
    try:
        return resolved_output.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return "<external-output>"


def _replay_command(
    seeds: tuple[int, ...], candidates: tuple[Candidate, ...], output_path: Path | None, phase_bits: int = PHASE_BITS
) -> str:
    arguments = [
        '"$PYTHON"',
        "gororoba_quantum/compile_evidence.py",
        "--seeds",
        *(str(seed) for seed in seeds),
    ]
    if phase_bits != PHASE_BITS:
        arguments.extend(("--phase-bits", str(phase_bits)))
    if len(candidates) != len(CANDIDATES):
        for candidate in candidates:
            arguments.extend(("--candidate", candidate.name))
    portable_output = _portable_output_path(output_path)
    if portable_output is not None:
        arguments.extend(("--out", portable_output))
    return " ".join(arguments[:1] + [shlex.quote(argument) for argument in arguments[1:]])


def capture(
    seeds: tuple[int, ...],
    candidates: tuple[Candidate, ...],
    output_path: Path | None,
    phase_bits: int = PHASE_BITS,
) -> dict[str, Any]:
    """Compile every requested candidate and return one self-describing record."""
    if not 1 <= phase_bits <= PHASE_BITS:
        raise ValueError(f"N=21 precision capture supports 1 through {PHASE_BITS} phase bits, got {phase_bits}")
    backend = FakeFez()
    return {
        "schema_version": 3,
        "capture": "n21-heavy-hex-mcx-workspace",
        "qpu_executed": False,
        "replay_command": _replay_command(seeds, candidates, output_path, phase_bits),
        "problem": {"modulus": MODULUS, "base": BASE, "phase_bits": phase_bits},
        "compiler": {
            "optimization_level": OPTIMIZATION_LEVEL,
            "seeds": list(seeds),
            "versions": _versions(),
        },
        "source": _source_record(),
        "backend": _backend_record(backend),
        "candidates": [_candidate_record(candidate, seeds, backend, phase_bits) for candidate in candidates],
    }


def _write_atomic(output_path: Path, payload: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output_path.name}.", dir=output_path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output_file:
            output_file.write(payload)
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temporary_path, output_path)
        directory_descriptor = os.open(output_path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument(
        "--candidate",
        action="append",
        choices=tuple(candidate.name for candidate in CANDIDATES),
        dest="candidates",
    )
    parser.add_argument("--phase-bits", type=int, default=PHASE_BITS)
    parser.add_argument("--out", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    seeds = tuple(args.seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("transpiler seeds must form a nonempty set")
    requested_names = set(args.candidates) if args.candidates else {candidate.name for candidate in CANDIDATES}
    candidates = tuple(candidate for candidate in CANDIDATES if candidate.name in requested_names)
    record = capture(seeds, candidates, args.out, args.phase_bits)
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.out is None:
        sys.stdout.write(payload)
    else:
        _write_atomic(args.out, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
