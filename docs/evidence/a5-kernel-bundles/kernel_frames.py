"""Exact principal-Pfaffian kernel frames on every high-nullity A_5 orbit.

For a rank-r bordered skew matrix A, every invertible principal r by r
block B supplies the rational frame [-B^-1*C; I_(16-r)] in pivot/free
order.  The principal blocks cover a constant-rank locus because a skew
matrix has a nonzero principal minor of order equal to its rank.  Rank ten
covers B9, V, VB, V^a_+, and V^a_-; rank eight covers N_+ and N_-.

In original complex coordinates, the two nullity-sixteen cones are

    N_sigma = {z=(w, 0, sigma*i*w): w.w=0, w != 0}, sigma in {+1,-1}.

Write w=a+i*b.  The real locus has a.a=b.b and a.b=0, and its unit
section has a.a=b.b=1/4.  For the rank-eight bordered skew matrix A, every
invertible principal 8 by 8 block B supplies the rational frame
[-B^-1*C; I_8] in pivot/free order.  All principal blocks form a finite
cover because a skew matrix of rank eight has a nonzero principal minor of
order eight.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))

import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

BORDERED_DIMENSION = 16
IMAGINARY_DIMENSION = 15
OCTONION_IMAGINARY_DIMENSION = 7
FRAME_RANK = 8
CHART_COUNT = math.comb(BORDERED_DIMENSION, FRAME_RANK)
ORBIT_SIGNS = (("N_+", 1), ("N_-", -1))
NULLITY_TWELVE_MATRIX_RANK = 10
NULLITY_TWELVE_FRAME_RANK = BORDERED_DIMENSION - NULLITY_TWELVE_MATRIX_RANK
NULLITY_TWELVE_CHART_COUNT = math.comb(BORDERED_DIMENSION, NULLITY_TWELVE_MATRIX_RANK)
NULLITY_TWELVE_ORBITS = (
    ("B9", "B9"),
    ("V", "V"),
    ("VB", "VB"),
    ("Vap", "V^a_+"),
    ("Vam", "V^a_-"),
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _bordered_matrix(z: Sequence[sp.Expr]) -> sp.Matrix:
    """Return A(z, conjugate(z)) from the repository's Cayley-Dickson signs."""
    if len(z) != IMAGINARY_DIMENSION:
        raise ValueError(f"z must have {IMAGINARY_DIMENSION} coordinates")
    conjugate_z = [sp.conjugate(value) for value in z]
    matrix = sp.zeros(BORDERED_DIMENSION)
    for coordinate, value in enumerate(conjugate_z, start=1):
        matrix[0, coordinate] = -value
        matrix[coordinate, 0] = value
    for row in range(1, BORDERED_DIMENSION):
        for column in range(1, BORDERED_DIMENSION):
            product = row ^ column
            if product:
                matrix[row, column] = cd_sign(BORDERED_DIMENSION, product, column) * z[product - 1]
    return matrix


def _nullity_sixteen_z(first: int, second: int, sign: int) -> tuple[sp.Expr, ...]:
    """Return z=(w,0,sign*i*w) for the exact isotropic fixture w=e_first+i*e_second."""
    if sign not in (-1, 1):
        raise ValueError("N sign must be +1 or -1")
    if not 0 <= first < OCTONION_IMAGINARY_DIMENSION or not 0 <= second < OCTONION_IMAGINARY_DIMENSION:
        raise ValueError("fixture indices must lie in [0,7)")
    if first == second:
        raise ValueError("the isotropic fixture needs two distinct coordinates")
    w = [sp.Integer(0)] * OCTONION_IMAGINARY_DIMENSION
    w[first] = sp.Integer(1)
    w[second] = sp.I
    return tuple([*w, sp.Integer(0), *(sign * sp.I * value for value in w)])


def _pfaffian(matrix: sp.Matrix) -> sp.Expr:
    """Compute a small exact Pfaffian by expansion along the first row."""
    if matrix.rows != matrix.cols or matrix.rows % 2:
        raise ValueError("Pfaffian input must be an even square matrix")
    if matrix.rows == 0:
        return sp.Integer(1)
    total = sp.Integer(0)
    for column in range(1, matrix.cols):
        remaining = [index for index in range(matrix.cols) if index not in (0, column)]
        term = matrix[0, column] * _pfaffian(matrix.extract(remaining, remaining))
        total = total + term if column % 2 else total - term
    return sp.expand(total)


def _find_principal_pivot(matrix: sp.Matrix, matrix_rank: int = FRAME_RANK) -> tuple[int, ...]:
    """Choose an invertible principal block by exact skew elimination."""
    if not 0 < matrix_rank <= BORDERED_DIMENSION or matrix_rank % 2:
        raise ValueError("skew-matrix pivot rank must be a positive even integer at most 16")
    selected: tuple[int, ...] = ()
    while len(selected) < matrix_rank:
        remaining = tuple(index for index in range(BORDERED_DIMENSION) if index not in selected)
        extension = next(
            (
                pair
                for pair in itertools.combinations(remaining, 2)
                if matrix.extract((*selected, *pair), (*selected, *pair)).det() != 0
            ),
            None,
        )
        if extension is None:
            raise RuntimeError("rank-eight bordered matrix has no principal pivot extension")
        selected = (*selected, *extension)
    return selected


def _principal_frame(matrix: sp.Matrix, pivot_indices: Sequence[int]) -> tuple[sp.Matrix, sp.Expr, sp.Expr]:
    """Construct the rational Schur frame and its determinant/Pfaffian denominator."""
    pivot = tuple(pivot_indices)
    if not pivot or len(pivot) % 2 or len(pivot) >= BORDERED_DIMENSION or len(set(pivot)) != len(pivot):
        raise ValueError("a bordered skew chart needs a distinct, nonempty, proper even pivot set")
    free = tuple(index for index in range(BORDERED_DIMENSION) if index not in pivot)
    block = matrix.extract(pivot, pivot)
    upper_right = matrix.extract(pivot, free)
    determinant = sp.expand(block.det())
    if determinant == 0:
        raise ValueError("principal chart denominator vanishes")
    pfaffian = _pfaffian(block)
    _require(sp.expand(determinant - pfaffian * pfaffian) == 0, "principal determinant differs from Pfaffian squared")
    frame = sp.zeros(BORDERED_DIMENSION, len(free))
    pivot_rows = -block.inv() * upper_right
    for row_position, row in enumerate(pivot):
        for column in range(len(free)):
            frame[row, column] = pivot_rows[row_position, column]
    for row_position, row in enumerate(free):
        frame[row, row_position] = 1
    return frame, determinant, pfaffian


def _mutated_bordered_matrix(matrix: sp.Matrix, mutation: str) -> sp.Matrix:
    if mutation == "":
        return matrix
    if mutation != "flip_border_sign":
        raise ValueError(f"unknown mutation {mutation!r}")
    mutated = matrix.copy()
    mutated[0, 1] = -mutated[0, 1]
    return mutated


def _real_and_imaginary(value: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    real, imaginary = sp.expand_complex(value).as_real_imag()
    return sp.expand(real), sp.expand(imaginary)


def _exact_fraction(value: sp.Expr) -> Fraction:
    rational = sp.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


def _real_coordinates_from_z(z: Sequence[sp.Expr]) -> tuple[Fraction, ...]:
    """Recover the doubly pure real A_5 element y from z_k=y_k+i*y_(16+k)."""
    y = [sp.Integer(0)] * 32
    for coordinate, value in enumerate(z, start=1):
        real, imaginary = _real_and_imaginary(value)
        y[coordinate] = real
        y[BORDERED_DIMENSION + coordinate] = imaginary
    return tuple(_exact_fraction(value) for value in y)


def _psi_inverse(vector: sp.Matrix) -> sp.Matrix:
    """Invert psi=conjugate o phi from C^16 to the real A_5 coordinates."""
    if vector.shape != (BORDERED_DIMENSION, 1):
        raise ValueError("psi inverse expects one complex bordered-kernel vector")
    real_parts: list[sp.Expr] = []
    imaginary_parts: list[sp.Expr] = []
    for coordinate, value in enumerate(vector):
        real, imaginary = _real_and_imaginary(value)
        real_parts.append(real)
        imaginary_parts.append(-imaginary if coordinate == 0 else imaginary)
    return sp.Matrix([*real_parts, *imaginary_parts])


def _real_kernel_frame(frame: sp.Matrix) -> sp.Matrix:
    """Realify a complex frame through psi inverse, including its i multiples."""
    columns: list[sp.Matrix] = []
    for column in range(frame.cols):
        complex_column = frame[:, column]
        columns.extend((_psi_inverse(complex_column), _psi_inverse(sp.I * complex_column)))
    return sp.Matrix.hstack(*columns)


def _fixture_check(task: tuple[str, int, int, int, str]) -> dict[str, Any]:
    orbit, sign, first, second, mutation = task
    z = _nullity_sixteen_z(first, second, sign)
    isotropic = sp.expand(sum((value * value for value in z[:7]), sp.Integer(0))) == 0
    expected_second_half = tuple(sign * sp.I * value for value in z[:7])
    parameterization_verified = isotropic and z[7] == 0 and tuple(z[8:]) == expected_second_half
    bordered = _bordered_matrix(z)
    _require(bordered.T == -bordered, "bordered matrix is not skew")
    pivot = _find_principal_pivot(bordered)
    frame, determinant, pfaffian = _principal_frame(bordered, pivot)
    free = tuple(index for index in range(BORDERED_DIMENSION) if index not in pivot)
    tested_matrix = _mutated_bordered_matrix(bordered, mutation)
    frame_identity_verified = tested_matrix * frame == sp.zeros(BORDERED_DIMENSION, FRAME_RANK)
    frame_rank_verified = frame.extract(free, range(FRAME_RANK)) == sp.eye(FRAME_RANK)
    y = _real_coordinates_from_z(z)
    left_matrix = sp.Matrix(left_mult_matrix_exact(32, y))
    real_frame = _real_kernel_frame(frame)
    left_kernel_verified = left_matrix * real_frame == sp.zeros(32, 2 * FRAME_RANK)
    real_frame_rank_verified = real_frame.rank() == 2 * FRAME_RANK
    return {
        "orbit": orbit,
        "fixture": [first + 1, second + 1],
        "parameterization_verified": parameterization_verified,
        "pivot_indices": list(pivot),
        "pivot_pfaffian": str(pfaffian),
        "pivot_determinant": str(determinant),
        "coverage_witness": pfaffian != 0,
        "frame_identity_verified": frame_identity_verified,
        "frame_rank_verified": frame_rank_verified,
        "left_kernel_verified": left_kernel_verified,
        "real_frame_rank_verified": real_frame_rank_verified,
        "frame": [[str(frame[row, column]) for column in range(FRAME_RANK)] for row in range(BORDERED_DIMENSION)],
        "pass": parameterization_verified
        and pfaffian != 0
        and frame_identity_verified
        and frame_rank_verified
        and left_kernel_verified
        and real_frame_rank_verified,
    }


def _symbolic_parameterization_check(sign: int) -> dict[str, bool]:
    """Verify the N sign, isotropy equations, and unit-section normalization symbolically."""
    a = sp.symbols("a1:8", real=True)
    b = sp.symbols("b1:8", real=True)
    w = [a[index] + sp.I * b[index] for index in range(OCTONION_IMAGINARY_DIMENSION)]
    z = [*w, sp.Integer(0), *(sign * sp.I * value for value in w)]
    split = [sp.expand(sp.I ** (-index.bit_count()) * z[index - 1]) for index in range(1, 16)]
    eta = tuple((-1) ** index.bit_count() for index in range(1, 8))
    split_isotropy = sp.expand(sum((eta[index] * split[index] ** 2 for index in range(7)), sp.Integer(0)))
    expected_isotropy = sp.expand(
        sum((a[index] ** 2 - b[index] ** 2 + 2 * sp.I * a[index] * b[index] for index in range(7)), sp.Integer(0))
    )
    norm_squared = sp.expand(sum((value * sp.conjugate(value) for value in z), sp.Integer(0)))
    expected_norm = sp.expand(2 * sum((a[index] ** 2 + b[index] ** 2 for index in range(7)), sp.Integer(0)))
    return {
        "middle_coordinate_zero": split[7] == 0,
        "second_half_sign": all(sp.expand(split[8 + index] - sign * split[index]) == 0 for index in range(7)),
        "isotropy_equations": sp.expand(split_isotropy - expected_isotropy) == 0,
        "unit_norm_equation": sp.expand(norm_squared - expected_norm) == 0,
    }


def _original_z_from_split(split_point: Sequence[int]) -> tuple[sp.Expr, ...]:
    """Convert z'_1,...,z'_15 to z_k=i^popcount(k) z'_k."""
    if len(split_point) != IMAGINARY_DIMENSION:
        raise ValueError(f"split point must have {IMAGINARY_DIMENSION} coordinates")
    return tuple(sp.I ** index.bit_count() * value for index, value in enumerate(split_point, start=1))


def _nullity_twelve_representative_check(task: tuple[str, str, str]) -> dict[str, Any]:
    orbit_key, orbit_label, mutation = task
    split_point = regularity.REPS[orbit_key]
    ideals = regularity.closure_ideals()
    membership_pattern = tuple(name for name in regularity.DIMS if regularity.member(ideals[name], split_point))
    expected_pattern = tuple(
        name for name in regularity.DIMS if name == orbit_key or orbit_key in regularity.EXPECTED_LOWER[name]
    )
    representative_membership_verified = membership_pattern == expected_pattern
    z = _original_z_from_split(split_point)
    bordered = _bordered_matrix(z)
    _require(bordered.T == -bordered, "bordered matrix is not skew")
    pivot = _find_principal_pivot(bordered, NULLITY_TWELVE_MATRIX_RANK)
    frame, determinant, pfaffian = _principal_frame(bordered, pivot)
    free = tuple(index for index in range(BORDERED_DIMENSION) if index not in pivot)
    tested_matrix = _mutated_bordered_matrix(bordered, mutation)
    frame_identity_verified = tested_matrix * frame == sp.zeros(BORDERED_DIMENSION, NULLITY_TWELVE_FRAME_RANK)
    frame_rank_verified = frame.extract(free, range(NULLITY_TWELVE_FRAME_RANK)) == sp.eye(NULLITY_TWELVE_FRAME_RANK)
    y = _real_coordinates_from_z(z)
    left_matrix = sp.Matrix(left_mult_matrix_exact(32, y))
    real_frame = _real_kernel_frame(frame)
    left_kernel_verified = left_matrix * real_frame == sp.zeros(32, 2 * NULLITY_TWELVE_FRAME_RANK)
    real_frame_rank_verified = real_frame.rank() == 2 * NULLITY_TWELVE_FRAME_RANK
    return {
        "orbit": orbit_label,
        "representative_key": orbit_key,
        "representative_membership_verified": representative_membership_verified,
        "membership_pattern": list(membership_pattern),
        "expected_membership_pattern": list(expected_pattern),
        "bordered_rank": NULLITY_TWELVE_MATRIX_RANK,
        "frame_columns": NULLITY_TWELVE_FRAME_RANK,
        "pivot_indices": list(pivot),
        "pivot_pfaffian": str(pfaffian),
        "pivot_determinant": str(determinant),
        "coverage_witness": pfaffian != 0,
        "frame_identity_verified": frame_identity_verified,
        "frame_rank_verified": frame_rank_verified,
        "left_kernel_verified": left_kernel_verified,
        "real_frame_rank_verified": real_frame_rank_verified,
        "frame": [
            [str(frame[row, column]) for column in range(NULLITY_TWELVE_FRAME_RANK)]
            for row in range(BORDERED_DIMENSION)
        ],
        "pass": representative_membership_verified
        and pfaffian != 0
        and frame_identity_verified
        and frame_rank_verified
        and left_kernel_verified
        and real_frame_rank_verified,
    }


def nullity_sixteen_frame_checks(mutation: str = "") -> dict[str, Any]:
    """Verify the finite N_+- frame cover on deterministic exact fixtures."""
    if mutation not in ("", "flip_border_sign"):
        raise ValueError(f"unknown mutation {mutation!r}")
    pairs = tuple(itertools.combinations(range(OCTONION_IMAGINARY_DIMENSION), 2))
    tasks = [(orbit, sign, first, second, mutation) for orbit, sign in ORBIT_SIGNS for first, second in pairs]
    fixture_rows = parallel.ordered_map(_fixture_check, tasks, min_items=1)
    symbolic_rows = {orbit: _symbolic_parameterization_check(sign) for orbit, sign in ORBIT_SIGNS}
    orbit_rows = []
    for orbit, _sign in ORBIT_SIGNS:
        rows = [row for row in fixture_rows if row["orbit"] == orbit]
        symbolic = symbolic_rows[orbit]
        orbit_rows.append(
            {
                "orbit": orbit,
                "bordered_rank": FRAME_RANK,
                "frame_columns": FRAME_RANK,
                "parameterization_verified": all(symbolic.values())
                and all(row["parameterization_verified"] for row in rows),
                "frame_identity_verified": all(row["frame_identity_verified"] for row in rows),
                "frame_identity_failure_count": sum(not row["frame_identity_verified"] for row in rows),
                "frame_rank_verified": all(row["frame_rank_verified"] for row in rows),
                "left_kernel_verified": all(row["left_kernel_verified"] for row in rows),
                "real_frame_rank_verified": all(row["real_frame_rank_verified"] for row in rows),
                "coverage_witness": all(row["coverage_witness"] for row in rows),
                "fixture_count": len(rows),
                "representative": rows[0],
                "symbolic_parameterization": symbolic,
                "pass": all(symbolic.values()) and all(row["pass"] for row in rows),
            }
        )
    return {
        "schema": "a5-nullity-sixteen-kernel-frames-v1",
        "mutation": mutation,
        "chart_count": CHART_COUNT,
        "chart_indexing": "all 8-subsets I of {0,...,15}",
        "chart_domain": "N_sigma intersect {pf(A_I,I) != 0}",
        "rational_frame": "in pivot/free order, F_I=[-B_I^(-1) C_I; I_8]",
        "polynomial_frame": "in pivot/free order, Fhat_I=[-adj(B_I) C_I; det(B_I) I_8]",
        "degeneracy_locus": "pf(B_I)=0, equivalently det(B_I)=pf(B_I)^2=0",
        "coverage_argument": (
            "rank(A)=8 on N_sigma; the principal-rank theorem for skew matrices gives an order-eight "
            "principal block with nonzero Pfaffian at every point"
        ),
        "parameterization": ("z=(w,0,sigma*i*w), w=a+i*b, a.a=b.b, a.b=0; on the unit section a.a=b.b=1/4"),
        "fixture_scope": "all 21 coordinate isotropic two-planes for each sign",
        "orbits": orbit_rows,
        "pass": all(row["pass"] for row in orbit_rows),
    }


def nullity_twelve_frame_checks(mutation: str = "") -> dict[str, Any]:
    """Verify the common principal-Pfaffian frame cover on all five nullity-twelve orbits."""
    if mutation not in ("", "flip_border_sign"):
        raise ValueError(f"unknown mutation {mutation!r}")
    tasks = [(orbit_key, orbit_label, mutation) for orbit_key, orbit_label in NULLITY_TWELVE_ORBITS]
    orbit_rows = parallel.ordered_map(_nullity_twelve_representative_check, tasks, min_items=1)
    return {
        "schema": "a5-nullity-twelve-kernel-frames-v1",
        "mutation": mutation,
        "chart_count": NULLITY_TWELVE_CHART_COUNT,
        "chart_indexing": "all 10-subsets I of {0,...,15}",
        "chart_domain": "each nullity-twelve orbit intersect {pf(A_I,I) != 0}",
        "rational_frame": "in pivot/free order, F_I=[-B_I^(-1) C_I; I_6]",
        "polynomial_frame": "in pivot/free order, Fhat_I=[-adj(B_I) C_I; det(B_I) I_6]",
        "degeneracy_locus": "pf(B_I)=0, equivalently det(B_I)=pf(B_I)^2=0",
        "coverage_argument": (
            "rank(A)=10 on every nullity-twelve orbit; the principal-rank theorem for skew matrices gives an "
            "order-ten principal block with nonzero Pfaffian at every point"
        ),
        "parameterizations": {
            "B9": "(u',0,v') with u',v' independent, isotropic, and u' cross v'=0",
            "V": "(alpha*w,mu,beta*w) with eta(w)!=0, mu!=0, and (alpha^2-beta^2)*eta(w)=mu^2",
            "VB": "(alpha*n,0,beta*n) with n!=0 null and alpha^2!=beta^2",
            "V^a_+": "(w,0,w) with eta(w)!=0",
            "V^a_-": "(w,0,-w) with eta(w)!=0",
        },
        "orbits": orbit_rows,
        "pass": all(row["pass"] for row in orbit_rows),
    }


def build_result() -> dict[str, Any]:
    nullity_sixteen = nullity_sixteen_frame_checks()
    nullity_twelve = nullity_twelve_frame_checks()
    mutated_sixteen = nullity_sixteen_frame_checks(mutation="flip_border_sign")
    mutated_twelve = nullity_twelve_frame_checks(mutation="flip_border_sign")
    result = {
        "schema": "a5-high-nullity-kernel-frames-v2",
        "nullity_sixteen": nullity_sixteen,
        "nullity_twelve": nullity_twelve,
        "mutation_control": {
            "mutation": "flip_border_sign",
            "nullity_sixteen_detected": not mutated_sixteen["pass"],
            "nullity_sixteen_frame_identity_failure_count": sum(
                row["frame_identity_failure_count"] for row in mutated_sixteen["orbits"]
            ),
            "nullity_twelve_detected": not mutated_twelve["pass"],
            "nullity_twelve_frame_identity_failure_count": sum(
                not row["frame_identity_verified"] for row in mutated_twelve["orbits"]
            ),
        },
        "pass": nullity_sixteen["pass"] and nullity_twelve["pass"],
    }
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def _self_test_mutation_task(item: tuple[str, str]) -> tuple[str, dict[str, Any]]:
    """Build one independent frame mutation for the parent self-test."""
    nullity, mutation = item
    if nullity == "sixteen":
        return nullity, nullity_sixteen_frame_checks(mutation=mutation)
    if nullity == "twelve":
        return nullity, nullity_twelve_frame_checks(mutation=mutation)
    raise ValueError(f"unknown nullity family {nullity!r}")


def self_test() -> None:
    baseline_sixteen = nullity_sixteen_frame_checks()
    if not baseline_sixteen["pass"]:
        raise RuntimeError("baseline nullity-sixteen frame check failed")
    baseline_twelve = nullity_twelve_frame_checks()
    if not baseline_twelve["pass"]:
        raise RuntimeError("baseline nullity-twelve frame check failed")
    mutations = dict(
        parallel.ordered_map(
            _self_test_mutation_task,
            [("sixteen", "flip_border_sign"), ("twelve", "flip_border_sign")],
            min_items=1,
        )
    )
    mutated_sixteen = mutations["sixteen"]
    if mutated_sixteen["pass"] or all(row["frame_identity_verified"] for row in mutated_sixteen["orbits"]):
        raise RuntimeError("nullity-sixteen bordered-sign mutation escaped detection")
    mutated_twelve = mutations["twelve"]
    if mutated_twelve["pass"] or all(row["frame_identity_verified"] for row in mutated_twelve["orbits"]):
        raise RuntimeError("nullity-twelve bordered-sign mutation escaped detection")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.check is not None and (arguments.self_test or arguments.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if arguments.self_test:
        self_test()
        print("high-nullity kernel-frame self-test: pass")
        return 0
    result = build_result()
    if not result["pass"]:
        raise RuntimeError("high-nullity kernel-frame result failed")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.check is not None:
        if payload.encode() != arguments.check.read_bytes():
            raise SystemExit(f"kernel_frames.py: fresh JSON differs byte-for-byte from {arguments.check}")
        print(f"kernel_frames.py: fresh JSON matches {arguments.check}")
    elif arguments.out is None:
        print(payload, end="")
    else:
        arguments.out.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
