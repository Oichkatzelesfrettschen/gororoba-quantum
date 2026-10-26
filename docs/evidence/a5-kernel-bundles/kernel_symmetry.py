"""Exact kernel transport and complex-structure checks for the A_5 rank strata.

The transport proved by the Pfaffian record is antilinear in the transported
input:

    phi(y x) = A(z, conjugate(z)) conjugate(phi(x)).

This script checks that formula, the formula without input conjugation, and
the action of J = L_(e_16) on every nullity-12 and nullity-16 orbit
representative from the regularity record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))

import rederive_strata_equations as equations  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

DIMENSION = 32
HALF_DIMENSION = 16
HIGH_NULLITY_ORBITS = ("B9", "V", "VB", "Vap", "Vam", "Np", "Nm")


@dataclass(frozen=True)
class GaussianRational:
    """A Gaussian rational represented without floating-point conversion."""

    real: Fraction
    imaginary: Fraction

    def __add__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(self.real + other.real, self.imaginary + other.imaginary)

    def __neg__(self) -> GaussianRational:
        return GaussianRational(-self.real, -self.imaginary)

    def __sub__(self, other: GaussianRational) -> GaussianRational:
        return self + (-other)

    def __mul__(self, other: GaussianRational) -> GaussianRational:
        return GaussianRational(
            self.real * other.real - self.imaginary * other.imaginary,
            self.real * other.imaginary + self.imaginary * other.real,
        )

    def conjugate(self) -> GaussianRational:
        return GaussianRational(self.real, -self.imaginary)

    def __bool__(self) -> bool:
        return self.real != 0 or self.imaginary != 0


GAUSSIAN_ZERO = GaussianRational(Fraction(0), Fraction(0))
GAUSSIAN_I = GaussianRational(Fraction(0), Fraction(1))
GAUSSIAN_MINUS_I = GaussianRational(Fraction(0), Fraction(-1))


def _gaussian_sum(values: Sequence[GaussianRational]) -> GaussianRational:
    total = GAUSSIAN_ZERO
    for value in values:
        total = total + value
    return total


def _gaussian_matrix_vector_product(
    matrix: Sequence[Sequence[GaussianRational]], vector: Sequence[GaussianRational]
) -> tuple[GaussianRational, ...]:
    return tuple(_gaussian_sum([entry * value for entry, value in zip(row, vector, strict=True)]) for row in matrix)


def _rational_matrix_vector_product(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    return tuple(sum((entry * value for entry, value in zip(row, vector, strict=True)), Fraction(0)) for row in matrix)


def _gaussian_rank(matrix: Sequence[Sequence[GaussianRational]]) -> int:
    """Complex rank from the rank of the rational realification."""
    order = len(matrix)
    realification = [[entry.real for entry in row] + [-entry.imaginary for entry in row] for row in matrix] + [
        [entry.imaginary for entry in row] + [entry.real for entry in row] for row in matrix
    ]
    rational_rank = equations.qrank(realification)
    if rational_rank % 2:
        raise ArithmeticError(f"Gaussian matrix realification has odd rank {rational_rank}")
    if any(len(row) != order for row in matrix):
        raise ValueError("Gaussian matrix must be square")
    return rational_rank // 2


def _phi(vector: Sequence[Fraction]) -> tuple[GaussianRational, ...]:
    """phi(r, s) = r + i conjugate(s) for x = (r, s) in A_5."""
    if len(vector) != DIMENSION:
        raise ValueError(f"A_5 vector must have {DIMENSION} coordinates")
    return tuple(
        GaussianRational(vector[index], vector[HALF_DIMENSION + index] * (1 if index == 0 else -1))
        for index in range(HALF_DIMENSION)
    )


def _bordered_matrix(y: Sequence[Fraction]) -> tuple[tuple[GaussianRational, ...], ...]:
    """A(z, conjugate(z)) for z_k = y_k + i y_(16+k), k = 1..15."""
    z = tuple(GaussianRational(y[index], y[HALF_DIMENSION + index]) for index in range(1, HALF_DIMENSION))
    conjugate_z = tuple(value.conjugate() for value in z)
    cross_rows: list[tuple[GaussianRational, ...]] = []
    for row_index in range(1, HALF_DIMENSION):
        row: list[GaussianRational] = []
        for column_index in range(1, HALF_DIMENSION):
            product_index = row_index ^ column_index
            row.append(
                GAUSSIAN_ZERO
                if product_index == 0
                else GaussianRational(
                    Fraction(cd_sign(HALF_DIMENSION, product_index, column_index)) * z[product_index - 1].real,
                    Fraction(cd_sign(HALF_DIMENSION, product_index, column_index)) * z[product_index - 1].imaginary,
                )
            )
        cross_rows.append(tuple(row))
    return (tuple([GAUSSIAN_ZERO, *(-value for value in conjugate_z)]),) + tuple(
        tuple([conjugate_z[row_index], *cross_rows[row_index]]) for row_index in range(HALF_DIMENSION - 1)
    )


def _kernel_vector_check(
    item: tuple[
        tuple[tuple[Fraction, ...], ...],
        tuple[tuple[Fraction, ...], ...],
        tuple[tuple[GaussianRational, ...], ...],
        tuple[Fraction, ...],
    ],
) -> dict[str, bool]:
    left_matrix, j_matrix, bordered, kernel_vector = item
    phi_vector = _phi(kernel_vector)
    conjugate_phi_vector = tuple(value.conjugate() for value in phi_vector)
    j_vector = _rational_matrix_vector_product(j_matrix, kernel_vector)
    phi_j_vector = _phi(j_vector)
    conjugate_phi_j_vector = tuple(value.conjugate() for value in phi_j_vector)
    return {
        "left_kernel": not any(_rational_matrix_vector_product(left_matrix, kernel_vector)),
        "transport_conjugated": not any(_gaussian_matrix_vector_product(bordered, conjugate_phi_vector)),
        "transport_unconjugated": not any(_gaussian_matrix_vector_product(bordered, phi_vector)),
        "j_preserves_kernel": not any(_rational_matrix_vector_product(left_matrix, j_vector)),
        "phi_j_equals_i_phi": phi_j_vector == tuple(GAUSSIAN_I * value for value in phi_vector),
        "conjugate_phi_j_equals_minus_i_conjugate_phi": conjugate_phi_j_vector
        == tuple(GAUSSIAN_MINUS_I * value for value in conjugate_phi_vector),
    }


def _representative_check(item: tuple[str, str]) -> dict[str, Any]:
    orbit, mutation = item
    split_point = [Fraction(value) for value in regularity.REPS[orbit]]
    y = tuple(equations.y_from_split(split_point))
    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, y))
    j_vector = [Fraction(0)] * DIMENSION
    j_vector[HALF_DIMENSION] = Fraction(-1 if mutation == "wrong_j_phase" else 1)
    j_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, j_vector))
    bordered = _bordered_matrix(y)
    kernel_basis = [tuple(row) for row in equations.nullspace(left_matrix)]
    vector_items = [(left_matrix, j_matrix, bordered, vector) for vector in kernel_basis]
    vector_checks = parallel.ordered_map(_kernel_vector_check, vector_items, min_items=1)
    real_nullity = len(kernel_basis)
    complex_nullity = HALF_DIMENSION - _gaussian_rank(bordered)
    transport_failures = sum(
        not row["transport_unconjugated" if mutation == "omit_input_conjugation" else "transport_conjugated"]
        for row in vector_checks
    )
    row_pass = (
        real_nullity == 2 * complex_nullity
        and transport_failures == 0
        and all(row["left_kernel"] and row["j_preserves_kernel"] for row in vector_checks)
        and all(row["phi_j_equals_i_phi"] for row in vector_checks)
        and all(row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in vector_checks)
    )
    return {
        "orbit": orbit,
        "real_nullity": real_nullity,
        "complex_nullity": complex_nullity,
        "kernel_basis_vectors": real_nullity,
        "transport_with_input_conjugation": all(row["transport_conjugated"] for row in vector_checks),
        "transport_without_input_conjugation": all(row["transport_unconjugated"] for row in vector_checks),
        "transport_failures": transport_failures,
        "j_preserves_kernel": all(row["j_preserves_kernel"] for row in vector_checks),
        "phi_j_equals_i_phi": all(row["phi_j_equals_i_phi"] for row in vector_checks),
        "conjugate_phi_j_equals_minus_i_conjugate_phi": all(
            row["conjugate_phi_j_equals_minus_i_conjugate_phi"] for row in vector_checks
        ),
        "pass": row_pass,
    }


def representative_kernel_checks(mutation: str = "") -> dict[str, Any]:
    """Check the transport and J action on the seven representatives of nullity at least 12."""
    if mutation not in ("", "omit_input_conjugation", "wrong_j_phase"):
        raise ValueError(f"unknown mutation {mutation!r}")
    items = [(orbit, mutation) for orbit in HIGH_NULLITY_ORBITS]
    rows = parallel.ordered_map(_representative_check, items, min_items=1)
    return {"mutation": mutation, "rows": rows, "pass": all(row["pass"] for row in rows)}


def build_result() -> dict[str, Any]:
    checks = representative_kernel_checks()
    unconjugated_failures = sum(
        row["kernel_basis_vectors"] for row in checks["rows"] if not row["transport_without_input_conjugation"]
    )
    return {
        "schema": "a5-kernel-symmetry-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "kernel_transport": {
            **checks,
            "proved_formula": "phi(y*x) = A(z, conjugate(z)) * conjugate(phi(x))",
            "program_formula": "phi(y*x) = A(z, conjugate(z)) * phi(x)",
            "program_formula_status": "refuted" if unconjugated_failures else "not refuted",
            "representatives_refuting_program_formula": [
                row["orbit"] for row in checks["rows"] if not row["transport_without_input_conjugation"]
            ],
        },
        "pass": checks["pass"] and unconjugated_failures > 0,
    }


def self_test() -> None:
    baseline = representative_kernel_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline kernel transport or J check failed")
    missing_conjugation = representative_kernel_checks(mutation="omit_input_conjugation")
    if missing_conjugation["pass"]:
        raise RuntimeError("transport mutation without input conjugation passed")
    wrong_j_phase = representative_kernel_checks(mutation="wrong_j_phase")
    if wrong_j_phase["pass"]:
        raise RuntimeError("J-phase mutation passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if not args.self_test and args.out is None:
        parser.error("choose --self-test and/or --out")
    if args.self_test:
        self_test()
        print("kernel transport self-test: pass")
    if args.out is not None:
        result = build_result()
        if not result["pass"]:
            raise RuntimeError("kernel transport result failed")
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
