"""Exact finite references for basis overlaps, signed cancellation and amplification.

The three product bases follow Lemma 1.2 of the source note
docs/notes/papers/openai-2026-mub-dimension-six.md. The Tao exponents follow
equation 2 transcribed in openai-2026-hadamard-order-six-fourier-certificates.md.
These finite identities establish circuit targets, rather than an exclusion
of every fourth basis or a physical spacetime interpretation.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product
from typing import Any

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from cd_core import cd_multiply_exact, cd_sign
from parallel import ordered_map

ComplexMatrix = NDArray[np.complex128]
ACTIVE_INDICES = (0, 1, 2, 4, 5, 6)
LEAKAGE_INDICES = (3, 7)
BASIS_NAMES = ("computational", "product_fourier", "product_chirped", "tao")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _reduced(matrix: Any) -> Any:
    return matrix.applyfunc(sp.expand)


@lru_cache(maxsize=1)
def _exact_bases() -> dict[str, Any]:
    omega = (-1 + sp.I * sp.sqrt(3)) / 2
    fourier = sp.Matrix(3, 3, lambda row, column: sp.expand(omega ** ((row * column) % 3))) / sp.sqrt(3)
    hadamard = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    qubit_chirped = sp.diag(1, sp.I) * hadamard
    qutrit_chirped = sp.diag(1, omega, omega) * fourier

    def tao_entry(row: int, column: int) -> Any:
        if row == 0 or column == 0 or row == column:
            return sp.Integer(1)
        exponent = 1 if (row - column) % 5 in (1, 4) else 2
        return sp.expand(omega**exponent)

    return {
        "computational": sp.ImmutableMatrix(sp.eye(6)),
        "product_fourier": sp.ImmutableMatrix(sp.kronecker_product(hadamard, fourier)),
        "product_chirped": sp.ImmutableMatrix(sp.kronecker_product(qubit_chirped, qutrit_chirped)),
        "tao": sp.ImmutableMatrix(sp.Matrix(6, 6, tao_entry) / sp.sqrt(6)),
    }


def _numeric(matrix: Any) -> ComplexMatrix:
    return np.asarray(matrix.evalf(17).tolist(), dtype=np.complex128)


def mub_bases(include_tao: bool = False) -> dict[str, ComplexMatrix]:
    """Return independent numeric copies; Tao is a specified comparison basis."""
    names = BASIS_NAMES if include_tao else BASIS_NAMES[:3]
    return {name: _numeric(_exact_bases()[name]) for name in names}


def embedded_basis(name: str) -> ComplexMatrix:
    """Extend a six-dimensional basis by identity on leakage indices 3 and 7."""
    _require(name in BASIS_NAMES, f"unknown basis {name!r}")
    result = np.eye(8, dtype=np.complex128)
    result[np.ix_(ACTIVE_INDICES, ACTIVE_INDICES)] = _numeric(_exact_bases()[name])
    return result


def transition_matrix(preparation: str, measurement: str) -> ComplexMatrix:
    """Return measurement-adjoint times preparation in the six-mode encoding."""
    _require(preparation in BASIS_NAMES and measurement in BASIS_NAMES, "unknown preparation or measurement basis")
    bases = _exact_bases()
    return _numeric(bases[measurement].H * bases[preparation])


def _overlap_record(pair: tuple[str, str]) -> dict[str, Any]:
    preparation, measurement = pair
    bases = _exact_bases()
    amplitudes = _reduced(bases[measurement].H * bases[preparation])
    probabilities = amplitudes.applyfunc(lambda value: sp.expand(value * sp.conjugate(value)))
    residuals = probabilities.applyfunc(lambda value: sp.Abs(value - sp.Rational(1, 6)))
    return {
        "preparation": preparation,
        "measurement": measurement,
        "probabilities": [[str(value) for value in row] for row in probabilities.tolist()],
        "maximum_unbiasedness_residual": str(max(residuals)),
        "orthonormal": _reduced(bases[preparation].H * bases[preparation]) == sp.eye(6),
    }


def _binary_rank(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def _signed_product(dim: int, left_indices: tuple[int, int], right_indices: tuple[int, int], sign: int) -> list[str]:
    left = [0] * dim
    right = [0] * dim
    left[left_indices[0]] = left[left_indices[1]] = 1
    right[right_indices[0]], right[right_indices[1]] = 1, sign
    return [str(value) for value in cd_multiply_exact(dim, left, right)]


def fano_reference() -> dict[str, Any]:
    """Certify incidence and distinguish mod-two parity from real sign cancellation."""
    lines = sorted({tuple(sorted((left, right, left ^ right))) for left, right in combinations(range(1, 8), 2)})
    rows = [sum(1 << (point - 1) for point in line) for line in lines]
    rank = _binary_rank(rows)
    # The same XOR skeleton in the octonions has even fibers modulo two,
    # while cd_core supplies its nonzero product over the real coefficients.
    counterexample = _signed_product(8, (1, 2), (4, 7), 1)
    return {
        "lines": [list(line) for line in lines],
        "incidence_rank_gf2": rank,
        "common_plus_eigenspace_dimension": 2 ** (7 - rank),
        "x_line_checks_commute": True,
        "x_z_intersection_parities": [[(left & right).bit_count() % 2 for right in rows] for left in rows],
        "sign_lift_counterexample": {
            "dimension": 8,
            "left": [1, 2],
            "right": [4, 7],
            "matching_xor": (1 ^ 2) == (4 ^ 7),
            "real_product": counterexample,
        },
    }


def _exact_quarter_mass() -> dict[str, Any]:
    preparation = sp.ones(4, 4)
    for row, column in product(range(4), repeat=2):
        preparation[row, column] = sp.Rational((-1) ** ((row & column).bit_count()), 2)
    oracle = sp.diag(1, 1, 1, -1)
    reflection = sp.ones(4, 4) / 2 - sp.eye(4)
    return {
        "preparation": preparation,
        "oracle": oracle,
        "reflection": reflection,
        "amplified": reflection * oracle * preparation,
        "omit_oracle": reflection * preparation,
        "omit_reflection": oracle * preparation,
    }


def quarter_mass_operators() -> dict[str, ComplexMatrix]:
    """Two-qubit operators with success predicate computational index 3."""
    return {name: _numeric(matrix) for name, matrix in _exact_quarter_mass().items()}


def sedenion_operators() -> dict[str, ComplexMatrix]:
    """Full LCU witness with selector bit 4 and signed data index bits 0..3."""
    first = np.zeros((16, 16), dtype=np.complex128)
    second = np.zeros((16, 16), dtype=np.complex128)
    for column in range(16):
        first[1 ^ column, column] = cd_sign(16, 1, column)
        second[10 ^ column, column] = cd_sign(16, 10, column)
    even, odd = (first + second) / 2, (first - second) / 2
    kernel = np.zeros(32, dtype=np.complex128)
    bright = np.zeros(32, dtype=np.complex128)
    kernel[4], kernel[15] = 1 / np.sqrt(2), -1 / np.sqrt(2)
    bright[4], bright[15] = 1 / np.sqrt(2), 1 / np.sqrt(2)
    return {
        "left_first": first,
        "left_second": second,
        "witness": np.block([[even, odd], [odd, even]]),
        "kernel_input": kernel,
        "bright_input": bright,
    }


def spectral_reference() -> dict[str, Any]:
    """Rational two-state example separates expectation, return and LCU success."""
    projector = sp.Matrix([[sp.Rational(1, 4), sp.sqrt(3) / 4], [sp.sqrt(3) / 4, sp.Rational(3, 4)]])
    approximate = sp.Rational(3, 4) * projector
    alpha = sp.Integer(2)
    return {
        "projector_identity": projector * projector == projector,
        "exact_expectation": str(projector[0, 0]),
        "exact_return_probability": str(projector[0, 0] ** 2),
        "exact_projection_probability": str((projector.H * projector)[0, 0]),
        "lcu_normalization": str(alpha),
        "exact_lcu_success_probability": str((projector.H * projector)[0, 0] / alpha**2),
        "approximate_expectation": str(approximate[0, 0]),
        "approximate_success_probability": str((approximate.H * approximate)[0, 0]),
        "approximate_lcu_success_probability": str((approximate.H * approximate)[0, 0] / alpha**2),
        "scope": "finite operator identities; infinite group projection remains research-blocked",
    }


@lru_cache(maxsize=1)
def _reference_report() -> dict[str, Any]:
    overlaps = ordered_map(_overlap_record, list(product(BASIS_NAMES, repeat=2)))
    quarter = _exact_quarter_mass()
    success = {
        name: str(matrix[3, 0] ** 2) for name, matrix in quarter.items() if name != "oracle" and name != "reflection"
    }
    kernel_product = _signed_product(16, (1, 10), (4, 15), -1)
    bright_product = _signed_product(16, (1, 10), (4, 15), 1)
    left_nested_sign = cd_sign(8, 1, 2) * cd_sign(8, 1 ^ 2, 4)
    right_nested_sign = cd_sign(8, 2, 4) * cd_sign(8, 1, 2 ^ 4)
    return {
        "schema": "quantum-experiment-references-v1",
        "basis_order": list(BASIS_NAMES),
        "active_indices": list(ACTIVE_INDICES),
        "leakage_indices": list(LEAKAGE_INDICES),
        "overlaps": overlaps,
        "fano": fano_reference(),
        "sedenion": {
            "kernel_product": kernel_product,
            "bright_product": bright_product,
            "kernel_ancilla_zero_probability": str(sum(sp.Rational(value) ** 2 for value in kernel_product) / 8),
            "bright_ancilla_zero_probability": str(sum(sp.Rational(value) ** 2 for value in bright_product) / 8),
            "strut_constant": 8 ^ 1 ^ 10,
        },
        "associator": {
            "dimension": 8,
            "basis_triple": [1, 2, 4],
            "output_index": 1 ^ 2 ^ 4,
            "left_nested_sign": left_nested_sign,
            "right_nested_sign": right_nested_sign,
            "associator_coefficient": left_nested_sign - right_nested_sign,
        },
        "spectral": spectral_reference(),
        "quarter_mass": {
            "success_index": 3,
            "success_probabilities": success,
            "ry_comparator_angle": "pi/3",
            "operators": {
                name: [[str(value) for value in row] for row in matrix.tolist()] for name, matrix in quarter.items()
            },
            "unitarity": {name: matrix.H * matrix == sp.eye(4) for name, matrix in quarter.items()},
        },
    }


def reference_report() -> dict[str, Any]:
    """Return a JSON-compatible independent copy of the exact reference report."""
    import copy

    return copy.deepcopy(_reference_report())


def self_check() -> dict[str, Any]:
    """Reject broken reference identities and return the exact certificate data."""
    report = reference_report()
    for record in report["overlaps"]:
        _require(record["orthonormal"], f"nonunitary basis {record['preparation']}")
        if record["preparation"] != record["measurement"] and "tao" not in (
            record["preparation"],
            record["measurement"],
        ):
            _require(record["maximum_unbiasedness_residual"] == "0", "product bases are not unbiased")
    fano = report["fano"]
    _require(fano["incidence_rank_gf2"] == 4, "Fano incidence rank changed")
    _require(
        any(value != "0" for value in fano["sign_lift_counterexample"]["real_product"]),
        "sign-lift counterexample failed",
    )
    sedenion = report["sedenion"]
    _require(all(value == "0" for value in sedenion["kernel_product"]), "sedenion kernel product failed")
    bright_norm_squared = sum(sp.Rational(value) ** 2 for value in sedenion["bright_product"])
    _require(bright_norm_squared == 8, "sedenion bright normalization failed")
    _require(report["spectral"]["projector_identity"], "spectral projector identity failed")
    _require(report["associator"]["associator_coefficient"] != 0, "nonassociative reference triple failed")
    _require(all(report["quarter_mass"]["unitarity"].values()), "quarter-mass full operator is not unitary")
    _require(
        report["quarter_mass"]["success_probabilities"]
        == {"preparation": "1/4", "amplified": "1", "omit_oracle": "1/4", "omit_reflection": "1/4"},
        "quarter-mass control probabilities failed",
    )
    return report
