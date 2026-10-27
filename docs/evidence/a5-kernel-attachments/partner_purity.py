"""Exact structural proof that partners of nonzero doubly pure A_5 elements are doubly pure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_frames  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-attachments-partner-purity-v1"
BORDERED_DIMENSION = 16
IMAGINARY_DIMENSION = BORDERED_DIMENSION - 1
SIGN_MUTATION = "flip_e1_e2_skew_pair"
SOURCE_PATHS = (
    HERE / "partner_purity.py",
    ROOT / "docs" / "design" / "a5-kernel-attachments-program.md",
    KERNEL_BUNDLES / "kernel_frames.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _interior_entry(
    row: int,
    column: int,
    z_coordinates: tuple[sp.Symbol, ...],
    mutation: str,
) -> sp.Expr:
    if mutation not in ("", SIGN_MUTATION):
        raise ValueError(f"unknown sign mutation {mutation!r}")
    if row == column:
        return sp.Integer(0)
    row_basis = row + 1
    column_basis = column + 1
    product_basis = row_basis ^ column_basis
    sign = cd_sign(BORDERED_DIMENSION, product_basis, column_basis)
    if mutation == SIGN_MUTATION and {row_basis, column_basis} == {1, 2}:
        sign = -sign
    return sp.Integer(sign) * z_coordinates[product_basis - 1]


def _interior_matrix(z_coordinates: tuple[sp.Symbol, ...], mutation: str) -> sp.Matrix:
    return sp.Matrix(
        IMAGINARY_DIMENSION,
        IMAGINARY_DIMENSION,
        lambda row, column: _interior_entry(row, column, z_coordinates, mutation),
    )


def _case_record(mutation: str) -> dict[str, Any]:
    z_coordinates = tuple(sp.symbols(f"z1:{BORDERED_DIMENSION}"))
    conjugate_coordinates = tuple(sp.symbols(f"zbar1:{BORDERED_DIMENSION}"))
    partner_coordinates = sp.Matrix(sp.symbols(f"u1:{BORDERED_DIMENSION}"))
    partner_scalar = sp.symbols("a")
    interior_matrix = _interior_matrix(z_coordinates, mutation)
    repository_matrix = kernel_frames._bordered_matrix(z_coordinates)
    repository_interior = repository_matrix.extract(range(1, BORDERED_DIMENSION), range(1, BORDERED_DIMENSION))
    z_column = sp.Matrix(z_coordinates)
    z_row = z_column.T
    conjugate_column = sp.Matrix(conjugate_coordinates)
    right_identity = (interior_matrix * z_column).applyfunc(sp.expand)
    left_identity = (z_row * interior_matrix).applyfunc(sp.expand)
    hermitian_pairing = sp.expand((z_row * conjugate_column)[0])
    lower_equation = partner_scalar * conjugate_column + interior_matrix * partner_coordinates
    projected_equation = sp.expand((z_row * lower_equation)[0])
    projected_partner_remainder = sp.expand(projected_equation - partner_scalar * hermitian_pairing)
    return {
        "mutation": mutation or "baseline",
        "interior_matches_repository_bordered_block": interior_matrix == repository_interior,
        "interior_is_skew": interior_matrix.T == -interior_matrix,
        "right_identity_Cz_z_zero": right_identity == sp.zeros(IMAGINARY_DIMENSION, 1),
        "left_identity_zT_Cz_zero": left_identity == sp.zeros(1, IMAGINARY_DIMENSION),
        "projected_partner_remainder_zero": projected_partner_remainder == 0,
        "right_identity_first_coordinate": str(right_identity[0]),
        "projected_partner_remainder": str(projected_partner_remainder),
        "hermitian_pairing": str(hermitian_pairing),
    }


def _antiholomorphic_border_certificate() -> dict[str, Any]:
    direction = sp.Matrix(sp.symbols(f"dbar1:{BORDERED_DIMENSION}"))
    antiholomorphic_border = sp.zeros(BORDERED_DIMENSION)
    antiholomorphic_border[0, 1:] = -direction.T
    antiholomorphic_border[1:, 0] = direction
    pure_embedding = sp.zeros(BORDERED_DIMENSION, IMAGINARY_DIMENSION)
    pure_embedding[1:, :] = sp.eye(IMAGINARY_DIMENSION)
    generic_restriction = pure_embedding.T * antiholomorphic_border * pure_embedding
    return {
        "antiholomorphic_derivative_has_only_scalar_border": (
            antiholomorphic_border[0, 0] == 0
            and antiholomorphic_border.extract(range(1, BORDERED_DIMENSION), range(1, BORDERED_DIMENSION))
            == sp.zeros(IMAGINARY_DIMENSION)
        ),
        "restriction_to_zero_scalar_hyperplane_is_zero": generic_restriction == sp.zeros(IMAGINARY_DIMENSION),
    }


def _positive_norm_certificate() -> dict[str, Any]:
    real_parts = sp.Matrix(sp.symbols(f"x1:{BORDERED_DIMENSION}", real=True))
    imaginary_parts = sp.Matrix(sp.symbols(f"y1:{BORDERED_DIMENSION}", real=True))
    complex_coordinates = real_parts + sp.I * imaginary_parts
    hermitian_norm = sp.expand((complex_coordinates.T * sp.conjugate(complex_coordinates))[0])
    euclidean_norm = sp.expand((real_parts.T * real_parts)[0] + (imaginary_parts.T * imaginary_parts)[0])
    return {
        "hermitian_norm": str(hermitian_norm),
        "euclidean_sum_of_squares": str(euclidean_norm),
        "hermitian_norm_equals_euclidean_norm": sp.expand(hermitian_norm - euclidean_norm) == 0,
        "nonzero_real_input_has_positive_norm": ("A nonzero real coordinate pair (x,y) has sum_j (x_j^2+y_j^2)>0."),
    }


def build_record() -> dict[str, Any]:
    case_records = parallel.ordered_map(_case_record, ("", SIGN_MUTATION), min_items=1)
    baseline, mutated = case_records
    positive_norm = _positive_norm_certificate()
    antiholomorphic_border = _antiholomorphic_border_certificate()
    baseline_pass = (
        bool(baseline["interior_matches_repository_bordered_block"])
        and bool(baseline["interior_is_skew"])
        and bool(baseline["right_identity_Cz_z_zero"])
        and bool(baseline["left_identity_zT_Cz_zero"])
        and bool(baseline["projected_partner_remainder_zero"])
        and bool(positive_norm["hermitian_norm_equals_euclidean_norm"])
        and bool(antiholomorphic_border["restriction_to_zero_scalar_hyperplane_is_zero"])
    )
    mutation_detected = (
        bool(mutated["interior_is_skew"])
        and not bool(mutated["interior_matches_repository_bordered_block"])
        and not bool(mutated["right_identity_Cz_z_zero"])
        and not bool(mutated["left_identity_zT_Cz_zero"])
        and not bool(mutated["projected_partner_remainder_zero"])
    )
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    passed = baseline_pass and mutation_detected
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"sympy": sp.__version__},
        "scope": {
            "algebra": "real Cayley-Dickson algebra A_5 in the repository split-complex coordinates",
            "domain": "every nonzero doubly pure left factor",
            "claim_boundary": (
                "The proof forces both scalar coordinates of every left-annihilating partner to vanish. It does not "
                "classify the remaining partner coordinates or any Gauss-graph limit set."
            ),
        },
        "baseline": baseline,
        "positive_norm": positive_norm,
        "antiholomorphic_border": antiholomorphic_border,
        "inference": {
            "lower_kernel_equation": "a*conjugate(z)+C_z*u=0",
            "projected_equation": "a*(z^T*conjugate(z))=0",
            "nonzero_input_conclusion": "a=0",
            "real_coordinate_conclusion": (
                "Every partner has zero e_0 and e_16 coordinates, so every complex kernel vector has zero scalar row."
            ),
            "first_order_consequence": (
                "The antiholomorphic bordered derivative restricts to zero on every boundary kernel at every "
                "nonzero doubly pure point."
            ),
        },
        "mutation_control": {
            "name": SIGN_MUTATION,
            "input_change": (
                "flip the Cayley-Dickson signs for the skew pair e_1*e_2 and e_2*e_1 before constructing C_z"
            ),
            "mutated": mutated,
            "detected": mutation_detected,
        },
        "falsifier": (
            "The reconstructed interior block differs from the repository bordered matrix; C_z is not skew; C_z*z "
            "or z^T*C_z is nonzero; z^T*conjugate(z) does not reduce to the positive Euclidean norm; the projected "
            "equation retains a partner-coordinate term; or the skew-pair sign mutation survives."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the partner-purity proof record failed")
    _require(bool(record["mutation_control"]["detected"]), "the Cayley-Dickson sign mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
