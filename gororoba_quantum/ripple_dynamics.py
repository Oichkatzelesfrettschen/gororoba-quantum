"""Certify finite associator dynamics and signed sedenion box-kite fringes.

The four-qubit step is U = Rx(pi/2)^tensor4 D, where D is the lower block of
the dimension-32 associator phase. The common fifth-qubit Z factor is removed.
Integer real and imaginary matrices represent U^depth over denominator
4^depth. All columns retain exact norm one, and an exhaustive depth scan
distinguishes the first return of |0000> from the first scalar operator.

The Qiskit oracle is extracted from three composed signed-permutation gates.
The exact prediction uses predict.associator_phase independently. Sedenion
graph edges are reconstructed from basis signs and checked against every
ordered signed row of the complete zero-divisor corpus. The phase circuits
measure the LCU ancilla; a dark fringe represents cancellation in that
postselected branch, while the full state retains norm one.

Default execution emits JSON to stdout. --out writes an explicit evidence
file; --check recomputes its scientific payload and verifies its source hashes.
Dependency versions and floating-point residuals accompany the exact payload
as execution metadata. These local checks use core Qiskit without a backend.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from collections import Counter
from collections.abc import Callable
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any, TypeAlias

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

import parallel
import predict
from boolean_anf import anf_coefficients
from cd_core import cd_multiply, cd_sign, sedenion_zero_divisor_corpus
from designs import design_d_phase_sweep, left_mult_adjoint_gate, left_mult_gate
from select_lcu import phase_oracle_from_truth_table

Pair: TypeAlias = tuple[int, int]
SignedRow: TypeAlias = tuple[int, int, int, int, int, int]
EdgeExperiment: TypeAlias = tuple[int, int, int, int, int]
IntegerMatrix: TypeAlias = list[list[int]]

PAIRS: tuple[Pair, ...] = ((25, 31), (9, 22))
EXPECTED_PERIODS = {(25, 31): (24, 24), (9, 22): (30, 120)}
MAXIMUM_DEPTH = 120
FRAME_DEPTH = 30
CORE_SIZE = 16
TOLERANCE = 1e-12
SOURCE_FILES = (
    "ripple_dynamics.py",
    "boolean_anf.py",
    "cd_core.py",
    "designs.py",
    "parallel.py",
    "predict.py",
    "select_lcu.py",
)


class RippleCheckFailed(RuntimeError):
    """A finite witness or circuit failed its declared validation boundary."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RippleCheckFailed(message)


def _validate_pair(pair: Pair) -> None:
    if type(pair) is not tuple or len(pair) != 2 or any(type(index) is not int for index in pair):
        raise ValueError("associator pair must be a tuple of two integer basis indices")
    if pair not in PAIRS:
        raise ValueError(f"unsupported dimension-32 associator pair {pair}; supported pairs are {PAIRS}")


def _validate_depth(depth: int) -> None:
    if type(depth) is not int or not 0 <= depth <= MAXIMUM_DEPTH:
        raise ValueError(f"depth must be an integer in [0, {MAXIMUM_DEPTH}], got {depth!r}")


def build_oracle(pair: Pair) -> QuantumCircuit:
    """Extract D from signed-permutation gates, independently of predict.py.

    The complete 32-dimensional operator must be diag(D, -D), with every
    entry of D equal to +1 or -1 and D[0] = 1. The last condition permits
    omitting the first oracle only when preparing the zero basis state.
    """
    _validate_pair(pair)
    first, second = pair
    composed = QuantumCircuit(5)
    composed.append(left_mult_gate(32, second), range(5))
    composed.append(left_mult_gate(32, first), range(5))
    composed.append(left_mult_adjoint_gate(32, first ^ second), range(5))
    composed.global_phase = 0 if cd_sign(32, first, second) == 1 else math.pi
    matrix = Operator(composed).data
    signs = np.where(np.diag(matrix).real >= 0, 1, -1)
    _require(float(np.max(np.abs(matrix - np.diag(signs)))) < TOLERANCE, f"{pair}: composed phase diagonal")
    _require(bool(np.array_equal(signs[:CORE_SIZE], -signs[CORE_SIZE:])), f"{pair}: common fifth-qubit Z")
    _require(int(signs[0]) == 1, f"{pair}: zero basis phase")
    return phase_oracle_from_truth_table([int(sign < 0) for sign in signs[:CORE_SIZE]])


def walk_circuit(pair: Pair, depth: int) -> QuantumCircuit:
    """Build U^depth as a full operator, including the first diagonal action."""
    _validate_depth(depth)
    oracle = build_oracle(pair)
    circuit = QuantumCircuit(4)
    for _ in range(depth):
        circuit.compose(oracle, inplace=True)
        circuit.barrier()
        circuit.rx(math.pi / 2, range(4))
        circuit.barrier()
    return circuit


def _advance(real: IntegerMatrix, imaginary: IntegerMatrix, signs: list[int]) -> tuple[IntegerMatrix, IntegerMatrix]:
    """Left-multiply by the Gaussian-integer numerator 4U."""
    next_real = [[sign * value for value in row] for sign, row in zip(signs, real, strict=True)]
    next_imaginary = [[sign * value for value in row] for sign, row in zip(signs, imaginary, strict=True)]
    for bit_index in range(4):
        for lower in range(CORE_SIZE):
            if lower & (1 << bit_index):
                continue
            upper = lower | (1 << bit_index)
            low_real, low_imaginary = next_real[lower], next_imaginary[lower]
            high_real, high_imaginary = next_real[upper], next_imaginary[upper]
            next_real[lower] = [left + right for left, right in zip(low_real, high_imaginary, strict=True)]
            next_imaginary[lower] = [left - right for left, right in zip(low_imaginary, high_real, strict=True)]
            next_real[upper] = [left + right for left, right in zip(high_real, low_imaginary, strict=True)]
            next_imaginary[upper] = [left - right for left, right in zip(high_imaginary, low_real, strict=True)]
    return next_real, next_imaginary


def _scalar_identity(real: IntegerMatrix, imaginary: IntegerMatrix) -> bool:
    scalar_real, scalar_imaginary = real[0][0], imaginary[0][0]
    return all(
        real[row][column] == (scalar_real if row == column else 0)
        and imaginary[row][column] == (scalar_imaginary if row == column else 0)
        for row in range(CORE_SIZE)
        for column in range(CORE_SIZE)
    )


def _column_norms(real: IntegerMatrix, imaginary: IntegerMatrix, denominator: int) -> None:
    _require(
        all(
            sum(real[row][column] ** 2 + imaginary[row][column] ** 2 for row in range(CORE_SIZE)) == denominator**2
            for column in range(CORE_SIZE)
        ),
        "exact operator column normalization",
    )


def _unitary_step(real: IntegerMatrix, imaginary: IntegerMatrix) -> None:
    for first_column in range(CORE_SIZE):
        for second_column in range(CORE_SIZE):
            inner_real = sum(
                real[row][first_column] * real[row][second_column]
                + imaginary[row][first_column] * imaginary[row][second_column]
                for row in range(CORE_SIZE)
            )
            inner_imaginary = sum(
                real[row][first_column] * imaginary[row][second_column]
                - imaginary[row][first_column] * real[row][second_column]
                for row in range(CORE_SIZE)
            )
            _require(
                inner_real == (CORE_SIZE if first_column == second_column else 0) and inner_imaginary == 0,
                "Gaussian-integer step unitarity",
            )


def _exact_walsh(signs: list[int]) -> list[Fraction]:
    return [
        Fraction(sum(sign * (-1) ** ((basis & outcome).bit_count()) for basis, sign in enumerate(signs)) ** 2, 256)
        for outcome in range(CORE_SIZE)
    ]


def exact_walk(pair: Pair) -> tuple[dict[str, Any], float]:
    """Check every positive depth through the bounded operator return."""
    _validate_pair(pair)
    full_signs = predict.associator_phase(32, *pair)
    signs = full_signs[:CORE_SIZE]
    _require(full_signs[CORE_SIZE:] == [-sign for sign in signs], f"{pair}: exact fifth-qubit factor")
    _require(signs[0] == 1, f"{pair}: exact initial phase")
    oracle = build_oracle(pair)
    oracle_error = float(np.max(np.abs(Operator(oracle).data - np.diag(signs))))
    _require(oracle_error < TOLERANCE, f"{pair}: oracle versus independent algebra")
    real = [[int(row == column) for column in range(CORE_SIZE)] for row in range(CORE_SIZE)]
    imaginary = [[0] * CORE_SIZE for _ in range(CORE_SIZE)]
    denominator = 1
    state_returns: list[int] = []
    state_return_phases: list[dict[str, Any]] = []
    operator_returns: list[int] = []
    frames: list[dict[str, Any]] = []
    qiskit_error = oracle_error
    expected_state_return, expected_operator_return = EXPECTED_PERIODS[pair]
    for depth in range(expected_operator_return + 1):
        _column_norms(real, imaginary, denominator)
        if depth == 1:
            _unitary_step(real, imaginary)
        fractions = [Fraction(real[row][0] ** 2 + imaginary[row][0] ** 2, denominator**2) for row in range(CORE_SIZE)]
        if depth <= FRAME_DEPTH:
            collision = sum((value * value for value in fractions), Fraction(0))
            frames.append(
                {
                    "depth": depth,
                    "probabilities": [float(value) for value in fractions],
                    "exact_probabilities": [str(value) for value in fractions],
                    "return_probability": float(fractions[0]),
                    "return_exact": str(fractions[0]),
                    "collision_K": float(collision),
                    "collision_exact": str(collision),
                }
            )
        if depth == 2:
            _require(fractions == _exact_walsh(signs)[::-1], f"{pair}: exact depth-two complemented Walsh bridge")
        if depth and fractions[0] == 1:
            state_returns.append(depth)
            state_return_phases.append(
                {
                    "depth": depth,
                    "real": str(Fraction(real[0][0], denominator)),
                    "imaginary": str(Fraction(imaginary[0][0], denominator)),
                }
            )
        if depth and _scalar_identity(real, imaginary):
            operator_returns.append(depth)
            _require(real[0][0] == denominator and imaginary[0][0] == 0, f"{pair}: operator returns as +I")
        if depth <= min(FRAME_DEPTH, expected_operator_return) or depth == expected_operator_return:
            circuit = walk_circuit(pair, depth)
            probabilities = Statevector(circuit).probabilities()
            qiskit_error = max(
                qiskit_error, float(np.max(np.abs(probabilities - [float(value) for value in fractions])))
            )
            if depth in (1, 2, 4, expected_operator_return):
                exact_operator = (
                    np.asarray(real, dtype=float) / denominator + 1j * np.asarray(imaginary, dtype=float) / denominator
                )
                qiskit_error = max(qiskit_error, float(np.max(np.abs(Operator(circuit).data - exact_operator))))
        if depth < expected_operator_return:
            real, imaginary = _advance(real, imaginary, signs)
            denominator *= 4
    _require(qiskit_error < TOLERANCE, f"{pair}: circuit disagreement {qiskit_error}")
    _require(state_returns[0:1] == [expected_state_return], f"{pair}: first state return {state_returns}")
    _require(operator_returns == [expected_operator_return], f"{pair}: first scalar operator return {operator_returns}")
    # Extend the shorter exact cycle to the shared visualization frame range.
    while len(frames) <= FRAME_DEPTH:
        depth = len(frames)
        frames.append({**frames[depth % expected_operator_return], "depth": depth})
    coefficients = anf_coefficients([int(sign < 0) for sign in signs])
    return (
        {
            "id": f"{pair[0]}-{pair[1]}",
            "label": f"({pair[0]}, {pair[1]})",
            "pair": list(pair),
            "dimension": 32,
            "qubits": 4,
            "anf_masks": list(coefficients),
            "monomial_counts": {
                str(degree): count
                for degree, count in sorted(Counter(mask.bit_count() for mask in coefficients).items())
            },
            "first_state_return": state_returns[0],
            "first_operator_return": operator_returns[0],
            "recurrence_certificate": {
                "operator_scan_depths": [1, expected_operator_return],
                "state_returns_in_scan": state_returns,
                "state_return_equivalence": "up to global phase",
                "state_return_phases": state_return_phases,
                "scalar_operator_returns_in_scan": operator_returns,
                "operator_return_scalar": "1",
                "all_column_norms_exact": True,
                "one_step_gram_identity_exact": True,
                "gaussian_integer_denominator": "4^depth",
                "fifth_qubit_factor": "Z on qubit 4",
            },
            "depth_two_walsh_xor_mask": 15,
            "frames": frames,
        },
        qiskit_error,
    )


def _signed_product_zero(row: SignedRow) -> bool:
    low, high, first_sign, partner_low, partner_high, second_sign = row
    operand = [0.0] * 16
    partner = [0.0] * 16
    operand[low], operand[high] = 1.0, float(first_sign)
    partner[partner_low], partner[partner_high] = 1.0, float(second_sign)
    return cd_multiply(16, operand, partner) == [0.0] * 16


def _check_signed_row(row: SignedRow) -> None:
    _require(_signed_product_zero(row), f"signed zero-divisor row {row}")


def _box_kite(constant: int) -> tuple[dict[str, Any], list[EdgeExperiment], list[SignedRow]]:
    vertices = [{"id": low, "low": low, "high": low ^ (8 ^ constant)} for low in range(1, 8) if low != constant]
    edges: list[dict[str, int]] = []
    struts: list[list[int]] = []
    rows: list[SignedRow] = []
    experiments: list[EdgeExperiment] = []
    for first, second in combinations(vertices, 2):
        low, high = first["low"], first["high"]
        partner_low, partner_high = second["low"], second["high"]
        if low ^ partner_low == constant:
            struts.append([low, partner_low])
            continue
        sign = -cd_sign(16, low, partner_low) * cd_sign(16, high, partner_high)
        edges.append({"source": low, "target": partner_low, "sign": sign})
        experiments.append((low, high, partner_low, partner_high, sign))
        for first_sign in (-1, 1):
            second_sign = first_sign * sign
            rows.append((low, high, first_sign, partner_low, partner_high, second_sign))
            rows.append((partner_low, partner_high, second_sign, low, high, first_sign))
    edge_signs = {frozenset((edge["source"], edge["target"])): edge["sign"] for edge in edges}
    faces: list[list[int]] = []
    for face in combinations([vertex["id"] for vertex in vertices], 3):
        face_edges = [frozenset(edge) for edge in combinations(face, 2)]
        if all(edge in edge_signs for edge in face_edges):
            _require(math.prod(edge_signs[edge] for edge in face_edges) == -1, f"box kite {constant}: face {face}")
            faces.append(list(face))
    _require(len(edges) == 12 and len(struts) == 3 and len(faces) == 8, f"box kite {constant}: octahedron counts")
    degrees = Counter(vertex for edge in edges for vertex in (edge["source"], edge["target"]))
    _require(set(degrees.values()) == {4} and len(degrees) == 6, f"box kite {constant}: degree four")
    _require(
        Counter(vertex for strut in struts for vertex in strut) == Counter(vertex["id"] for vertex in vertices),
        f"box kite {constant}: opposite pairs",
    )
    return (
        {
            "id": constant,
            "strutConstant": constant,
            "vertices": vertices,
            "edges": edges,
            "struts": struts,
            "negative_triangle_count": len(faces),
            "negative_triangles": faces,
        },
        experiments,
        rows,
    )


def box_kites() -> tuple[list[dict[str, Any]], list[EdgeExperiment], list[SignedRow]]:
    results = parallel.ordered_map(_box_kite, list(range(1, 8)), min_items=2)
    graphs = [result[0] for result in results]
    experiments = [experiment for result in results for experiment in result[1]]
    rows = sorted(row for result in results for row in result[2])
    corpus = sedenion_zero_divisor_corpus()
    _require(len(rows) == len(set(rows)) == len(corpus) == 336, "complete signed-corpus cardinality")
    _require(set(rows) == set(corpus), "graph reconstruction versus independent signed-corpus enumeration")
    parallel.ordered_map(_check_signed_row, rows, min_items=32)
    return graphs, experiments, rows


def check_edge(edge: EdgeExperiment) -> float:
    low, high, partner_low, partner_high, sign = edge
    maximum_error = 0.0
    for phase_index in range(8):
        phase = phase_index * math.pi / 4
        circuit = design_d_phase_sweep((low, high), (partner_low, partner_high), phase)
        state = Statevector(circuit.remove_final_measurements(inplace=False))
        observed = float(state.probabilities([4])[0])
        expected = (1 - sign * math.cos(phase)) / 2
        maximum_error = max(
            maximum_error, abs(observed - expected), abs(float(np.vdot(state.data, state.data).real) - 1)
        )
    _require(maximum_error < TOLERANCE, f"edge {edge}: circuit mismatch {maximum_error}")
    return maximum_error


def _expect_rejection(operation: Callable[[], object], label: str) -> None:
    try:
        operation()
    except (ValueError, RippleCheckFailed):
        return
    raise RippleCheckFailed(f"negative control survived: {label}")


def _self_checks(rows: list[SignedRow]) -> list[str]:
    _expect_rejection(lambda: walk_circuit(PAIRS[0], -1), "negative depth")
    _expect_rejection(lambda: walk_circuit(PAIRS[0], True), "Boolean depth")
    _expect_rejection(lambda: walk_circuit(PAIRS[0], MAXIMUM_DEPTH + 1), "unbounded depth")
    _expect_rejection(lambda: build_oracle((True, 31)), "Boolean basis index")
    _expect_rejection(lambda: build_oracle((1, 2)), "unsupported pair")
    wrong_row = (*rows[0][:5], -rows[0][5])
    _expect_rejection(lambda: _check_signed_row(wrong_row), "zero-divisor sign mutation")
    real = [[int(row == column) for column in range(CORE_SIZE)] for row in range(CORE_SIZE)]
    imaginary = [[0] * CORE_SIZE for _ in range(CORE_SIZE)]
    real[1][1] = -1
    _require(not _scalar_identity(real, imaginary), "state return must differ from operator return")
    real[1][0] = 1
    _expect_rejection(lambda: _column_norms(real, imaginary, 1), "normalization mutation")
    full_signs = predict.associator_phase(32, *PAIRS[0])[:CORE_SIZE]
    wrong_signs = list(full_signs)
    wrong_signs[1] *= -1
    oracle = Operator(build_oracle(PAIRS[0])).data
    _require(float(np.max(np.abs(oracle - np.diag(wrong_signs)))) > 1, "associator sign mutation")
    return [
        "negative-depth",
        "boolean-depth",
        "unbounded-depth",
        "boolean-index",
        "unsupported-pair",
        "zero-divisor-sign",
        "state-versus-operator-return",
        "normalization",
        "associator-sign",
    ]


def source_hashes() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def audit_ripples() -> dict[str, Any]:
    """Regenerate the entire bounded certificate without writing files."""
    initial_hashes = source_hashes()
    walk_results = parallel.ordered_map(exact_walk, list(PAIRS), min_items=2)
    pairs = [result[0] for result in walk_results]
    _require(pairs[0]["monomial_counts"] == pairs[1]["monomial_counts"], "matched ANF degree counts")
    _require(pairs[0]["monomial_counts"] == {"1": 2, "2": 3, "3": 2}, "matched ANF term counts")
    _require([pair["frames"][4]["return_exact"] for pair in pairs] == ["9/16", "1/4"], "depth-four returns")
    contrast = Fraction(pairs[0]["frames"][4]["return_exact"]) - Fraction(pairs[1]["frames"][4]["return_exact"])
    _require(contrast == Fraction(5, 16), "depth-four return contrast")
    graphs, experiments, rows = box_kites()
    edge_errors = parallel.ordered_map(check_edge, experiments, min_items=16)
    self_checks = _self_checks(rows)
    _require(source_hashes() == initial_hashes, "source hashes changed during verification")
    return {
        "schema": "cayley-dickson-ripple-evidence-v1",
        "status": "Exact finite predictions and local core-Qiskit circuit checks",
        "pairs": pairs,
        "depth_four_return_contrast_exact": str(contrast),
        "boxkites": graphs,
        "boxkite_counts": {
            "vertices": 42,
            "edges": len(experiments),
            "signed_rows": len(rows),
            "negative_triangles": 56,
        },
        "signed_zero_divisor_rows": [list(row) for row in rows],
        "boxkite_phase_checks": len(experiments) * 8,
        "boxkite_phase_indices": list(range(8)),
        "boxkite_phase_radians": "phase_index*pi/4",
        "boxkite_ancilla_zero_probability": "(1-sign*cos(phase))/2",
        "self_checks": self_checks,
        "source_sha256": initial_hashes,
        "proposed_hardware_depths": [0, 1, 2, 3, 4],
        "geometry": "Hamming shells and octahedra are schematic algebraic embeddings, not chip positions",
        "execution_metadata": {
            "dependency_versions": {package: importlib.metadata.version(package) for package in ("numpy", "qiskit")},
            "maximum_pair_errors": [result[1] for result in walk_results],
            "maximum_edge_error": max(edge_errors),
            "tolerance": TOLERANCE,
        },
    }


def _canonical_payload(evidence: dict[str, Any]) -> str:
    payload = {key: value for key, value in evidence.items() if key != "execution_metadata"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_evidence(record: object, expected: dict[str, Any]) -> None:
    """Require exact science/source agreement and bounded retained residuals."""
    _require(isinstance(record, dict), "evidence must be a JSON object")
    if not isinstance(record, dict):
        return
    _require(set(record) == set(expected), "evidence top-level fields")
    metadata = record.get("execution_metadata")
    _require(isinstance(metadata, dict), "execution metadata must be an object")
    if not isinstance(metadata, dict):
        return
    _require(set(metadata) == set(expected["execution_metadata"]), "execution metadata fields")
    versions = metadata.get("dependency_versions")
    _require(isinstance(versions, dict), "dependency versions must be an object")
    if not isinstance(versions, dict):
        return
    _require(
        set(versions) == {"numpy", "qiskit"}
        and all(isinstance(version, str) and version for version in versions.values()),
        "dependency version names",
    )
    errors = metadata.get("maximum_pair_errors")
    _require(isinstance(errors, list) and len(errors) == len(PAIRS), "pair error count")
    if not isinstance(errors, list):
        return
    _require(type(metadata.get("tolerance")) is float and metadata["tolerance"] == TOLERANCE, "numerical tolerance")
    for residual in [*errors, metadata.get("maximum_edge_error")]:
        _require(
            type(residual) in (int, float) and math.isfinite(residual) and 0 <= residual < TOLERANCE,
            "retained numerical residual",
        )
    _require(_canonical_payload(record) == _canonical_payload(expected), "scientific payload or source hashes differ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--out", type=Path, help="write JSON evidence to this explicit path")
    mode.add_argument("--check", type=Path, help="recompute and validate a retained JSON evidence file")
    arguments = parser.parse_args()
    evidence = audit_ripples()
    if arguments.check is not None:
        record = json.loads(arguments.check.read_text(encoding="utf-8"))
        check_evidence(record, evidence)
        print("ripple evidence: scientific payload, source hashes, and numerical bounds verified")
    elif arguments.out is not None:
        arguments.out.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(evidence, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
