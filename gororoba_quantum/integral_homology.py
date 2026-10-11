"""Verify finite integral chain complexes and compute their homology exactly.

Smith decompositions carry integral unimodular changes of basis. Computing
the next boundary in the resulting kernel basis preserves torsion, which
rational ranks alone discard. A chain complex describes a geometric space
only when a separate construction identifies that space with the complex.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.normalforms import smith_normal_decomp


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer_matrix(matrix: sp.MatrixBase) -> sp.MutableDenseMatrix:
    """Copy an integral matrix, rejecting approximate or nonintegral entries."""
    result = sp.Matrix(matrix)
    _require(all(entry.is_Integer is True for entry in result), "chain matrices require exact integers")
    return result


def matrix_record(matrix: sp.MatrixBase) -> dict[str, object]:
    """Retain dimensions, including those erased by empty nested lists."""
    exact = integer_matrix(matrix)
    return {"shape": list(exact.shape), "rows": [[int(value) for value in row] for row in exact.tolist()]}


def verified_smith(
    matrix: sp.MatrixBase,
) -> tuple[sp.MutableDenseMatrix, sp.MutableDenseMatrix, sp.MutableDenseMatrix]:
    """Return S,U,V after independently checking S=U*A*V and unimodularity."""
    exact = integer_matrix(matrix)
    if min(exact.shape) == 0:
        return exact, sp.eye(exact.rows), sp.eye(exact.cols)
    domain_matrix = DomainMatrix.from_Matrix(exact).convert_to(sp.ZZ)
    diagonal_domain, left_domain, right_domain = smith_normal_decomp(domain_matrix)
    diagonal = sp.Matrix(diagonal_domain.to_Matrix())
    left = sp.Matrix(left_domain.to_Matrix())
    right = sp.Matrix(right_domain.to_Matrix())
    _require(left.shape == (exact.rows, exact.rows), "left Smith basis shape")
    _require(right.shape == (exact.cols, exact.cols), "right Smith basis shape")
    integer_matrix(left)
    integer_matrix(right)
    _require(abs(left.det()) == 1 and abs(right.det()) == 1, "Smith basis must be unimodular")
    _require(left * exact * right == diagonal, "Smith transformation identity failed")
    _require(
        all(
            diagonal[row, column] == 0
            for row in range(diagonal.rows)
            for column in range(diagonal.cols)
            if row != column
        ),
        "Smith form must be diagonal",
    )
    values = [abs(int(diagonal[index, index])) for index in range(min(diagonal.shape))]
    nonzero = [value for value in values if value]
    _require(values == nonzero + [0] * (len(values) - len(nonzero)), "Smith diagonal has an interior zero")
    _require(
        all(second % first == 0 for first, second in zip(nonzero, nonzero[1:], strict=False)),
        "Smith divisibility failed",
    )
    return diagonal, left, right


def integral_homology(chain_ranks: Mapping[int, int], boundaries: Mapping[int, sp.MatrixBase]) -> dict[str, Any]:
    """Compute H_d=ker(d_d)/im(d_(d+1)); omitted boundaries mean zero maps.

    Degree keys remain sparse, so a finite complex in a large dimension does
    not allocate an array for every intervening degree. The result certifies
    the supplied chain complex, independently of any topological realization.
    """
    for degree, rank in chain_ranks.items():
        _require(type(degree) is int and degree >= 0, "chain degrees require nonnegative integers")
        _require(type(rank) is int and rank >= 0, "chain ranks require nonnegative integers")
    for degree in boundaries:
        _require(type(degree) is int and degree >= 0, "boundary degrees require nonnegative integers")
    degrees = sorted(set(chain_ranks) | set(boundaries) | {degree + 1 for degree in chain_ranks})
    maps = {}
    for degree in degrees:
        shape = (chain_ranks.get(degree - 1, 0), chain_ranks.get(degree, 0))
        boundary = integer_matrix(boundaries.get(degree, sp.zeros(*shape)))
        _require(boundary.shape == shape, f"boundary shape disagrees in degree {degree}")
        maps[degree] = boundary
    for degree, boundary in maps.items():
        previous = maps.get(degree - 1)
        if previous is not None:
            _require(previous * boundary == sp.zeros(previous.rows, boundary.cols), "boundary squared is nonzero")

    records = []
    for degree in sorted(chain_ranks):
        chain_rank = chain_ranks[degree]
        if chain_rank == 0:
            continue
        boundary = maps[degree]
        diagonal, left, right = verified_smith(boundary)
        boundary_rank = sum(diagonal[index, index] != 0 for index in range(min(diagonal.shape)))
        next_boundary = maps[degree + 1]
        next_coordinates = integer_matrix(right.inv() * next_boundary)
        _require(
            next_coordinates[:boundary_rank, :] == sp.zeros(boundary_rank, next_boundary.cols), "image escapes kernel"
        )
        kernel_image = next_coordinates[boundary_rank:, :]
        image_diagonal, image_left, image_right = verified_smith(kernel_image)
        image_values = [
            abs(int(image_diagonal[index, index]))
            for index in range(min(image_diagonal.shape))
            if image_diagonal[index, index] != 0
        ]
        records.append(
            {
                "degree": degree,
                "chain_rank": chain_rank,
                "kernel_rank": chain_rank - boundary_rank,
                "image_rank": len(image_values),
                "free_rank": chain_rank - boundary_rank - len(image_values),
                "torsion_invariant_factors": [value for value in image_values if value > 1],
                "boundary": matrix_record(boundary),
                "boundary_smith": matrix_record(diagonal),
                "boundary_left_unimodular": matrix_record(left),
                "boundary_right_unimodular": matrix_record(right),
                "next_boundary_in_kernel_basis": matrix_record(kernel_image),
                "image_smith": matrix_record(image_diagonal),
                "image_left_unimodular": matrix_record(image_left),
                "image_right_unimodular": matrix_record(image_right),
            }
        )
    return {"coefficient_ring": "Z", "boundary_squared_zero": True, "homology": records}


def audit_integral_homology() -> dict[str, object]:
    """Exercise torsion, changed integer bases, and invalid boundary controls."""
    ranks = {0: 1, 1: 2, 2: 1}
    basis_change = sp.Matrix([[1, 2], [0, 1]])
    first_boundary = sp.Matrix([[1, 0]]) * basis_change.inv()
    second_boundary = basis_change * sp.Matrix([[0], [6]])
    report = integral_homology(ranks, {1: first_boundary, 2: second_boundary})
    groups = {row["degree"]: row for row in report["homology"]}
    _require(
        groups[1]["free_rank"] == 0 and groups[1]["torsion_invariant_factors"] == [6], "integer basis torsion fixture"
    )
    sphere = integral_homology({0: 1, 3: 1}, {})
    _require([row["free_rank"] for row in sphere["homology"]] == [1, 1], "sphere chain fixture")
    rejected = 0
    invalid: tuple[tuple[dict[int, int], dict[int, sp.MatrixBase]], ...] = (
        ({0: 1, 1: 1, 2: 1}, {1: sp.ones(1), 2: sp.ones(1)}),
        ({0: 1, 1: 1}, {1: sp.zeros(2, 1)}),
        ({0: 1, 1: 1}, {1: sp.Matrix([[sp.Rational(1, 2)]])}),
        ({0: 1, 1: 1}, {1: sp.Matrix([[0.0]])}),
        ({-1: 1}, {}),
    )
    for invalid_ranks, invalid_boundaries in invalid:
        try:
            integral_homology(invalid_ranks, invalid_boundaries)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid chain complex escapes rejection")
    return {
        "schema": "integral-chain-homology-audit-v1",
        "qpu_executed": False,
        "sympy_version": sp.__version__,
        "scope": "Exact finite chain complexes; topological identification requires an external geometric certificate.",
        "changed_basis_torsion_fixture": report,
        "sphere_fixture": sphere,
        "rejected_invalid_chain_complexes": rejected,
    }


def main() -> int:
    print(json.dumps(audit_integral_homology(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
