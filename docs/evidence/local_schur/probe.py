"""Retain exact local skew Schur reductions at three rank-path endpoints.

The finite probes certify their own rational matrix identities and derivative
maps. Smooth rank-stratum coverage and global attachments require additional
proofs. The program performs local symbolic arithmetic and writes stdout only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

SOURCE_FILES = (
    "docs/evidence/local_schur/probe.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/rank_attachments.py",
    "gororoba_quantum/rank_charts.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def reduction(matrix: sp.Matrix, complement: sp.Matrix, kernel: sp.Matrix) -> tuple[sp.Matrix, sp.Matrix]:
    """Certify a skew reduction on the stated invertible complement domain."""
    dimension = matrix.rows
    require(matrix.shape == (dimension, dimension), "matrix must be square")
    require(matrix + matrix.T == sp.zeros(dimension), "matrix must be skew-symmetric")
    transform = complement.row_join(kernel)
    require(transform.shape == (dimension, dimension), "basis shape differs from the matrix")
    require(transform.det() != 0, "complement and kernel fail to span")
    pivot = complement.T * matrix * complement
    require(pivot.det() != 0, "point leaves the invertible pivot domain")
    cross = complement.T * matrix * kernel
    diagonal = kernel.T * matrix * kernel
    schur = diagonal + cross.T * pivot.inv() * cross
    lift = transform * sp.Matrix.vstack(-pivot.inv() * cross, sp.eye(kernel.cols))
    require(schur + schur.T == sp.zeros(kernel.cols), "skew Schur identity fails")
    require(matrix.rank() == complement.cols + schur.rank(), "rank identity fails")
    residual = sp.Matrix.vstack(sp.zeros(complement.cols, kernel.cols), schur)
    require(transform.T * matrix * lift == residual, "lift identity fails")
    damaged_lift = lift.copy()
    damaged_lift[0, 0] += 1
    require(transform.T * matrix * damaged_lift != residual, "damaged lift escapes the residual check")
    return schur, lift


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from rank_attachments import path_coefficients, path_matrix
    from rank_charts import multiplication_matrix

    for module_name in ("cd_core", "parallel", "rank_attachments", "rank_charts"):
        loaded = Path(str(sys.modules[module_name].__file__)).resolve()
        require(loaded == (root / "gororoba_quantum" / f"{module_name}.py").resolve(), "import source differs")
    records = []
    parameter = sp.Symbol("t", real=True)
    for endpoint in (0, 1, 2):
        original = path_matrix(endpoint)
        complement = sp.Matrix.hstack(*original.columnspace())
        kernel = sp.Matrix.hstack(*original.nullspace())
        transform = complement.row_join(kernel)
        require(transform.det() != 0, "base complement and kernel fail to span")
        require((complement.T * original * complement).det() != 0, "base pivot is singular")
        require(complement.T * original * kernel == sp.zeros(complement.cols, kernel.cols), "base cross block")
        require(kernel.T * original * kernel == sp.zeros(kernel.cols), "base kernel block")
        perturbations = []
        derivative_columns = []
        for coordinate in range(32):
            if coordinate in (0, 16):
                continue
            direction = [0] * 32
            direction[coordinate] = 1
            differential = kernel.T * sp.Matrix(multiplication_matrix(direction)) * kernel
            derivative_columns.append(
                sp.Matrix(
                    [differential[row, column] for row in range(kernel.cols) for column in range(row + 1, kernel.cols)]
                )
            )
            if coordinate not in (2, 17):
                continue
            vector = [Fraction(value) for value in path_coefficients(endpoint)]
            vector[coordinate] += Fraction(1, 3)
            matrix = sp.Matrix(multiplication_matrix(vector))
            schur, _ = reduction(matrix, complement, kernel)
            perturbations.append(
                {
                    "coordinate": coordinate,
                    "coefficient": "1/3",
                    "full_nullity": 32 - matrix.rank(),
                    "schur_nullity": kernel.cols - schur.rank(),
                    "skew_identity": True,
                    "rank_identity": True,
                    "lift_residual_identity": True,
                    "damaged_lift_rejected": True,
                }
            )
        derivative = sp.Matrix.hstack(*derivative_columns)
        radial = sp.Matrix([value for index, value in enumerate(path_coefficients(endpoint)) if index not in (0, 16)])
        require(derivative * radial == sp.zeros(derivative.rows, 1), "radial direction must lie in the kernel")
        path_direction = path_matrix(parameter).diff(parameter).subs(parameter, endpoint)
        require(kernel.T * path_direction * kernel != sp.zeros(kernel.cols), "path direction retains exceptional rank")
        try:
            reduction(original + sp.eye(32), complement, kernel)
        except RuntimeError as error:
            require(str(error) == "matrix must be skew-symmetric", "nonpure fixture fails outside skew guard")
        else:
            raise RuntimeError("nonpure matrix escapes skew guard")
        records.append(
            {
                "endpoint": endpoint,
                "kernel_dimension": kernel.cols,
                "linear_deformation_rank": derivative.rank(),
                "unit_base_linearized_dimension": 29 - derivative.rank(),
                "path_direction_effective_rank": (kernel.T * path_direction * kernel).rank(),
                "nonpure_matrix_rejected": True,
                "perturbations": perturbations,
            }
        )
    require(source_digests(root) == before, "source bytes change during the probe")
    return {
        "schema": "cayley-dickson-local-skew-schur-probe-v1",
        "scope": "three rational path endpoints and six rational perturbations; global geometry remains unclassified",
        "qpu_executed": False,
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed bytes with the retained result")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    root = bundle.parents[2]
    result = json.dumps(audit(root), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        require(result.encode() == (bundle / "result.json").read_bytes(), "probe output differs from retained bytes")
        print("Local skew Schur probe: rank/lift identities, tangent bounds, controls, and source stability pass")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
