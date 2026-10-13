"""Replay exact path limits, a cone attachment, and ordinary-doubling transport."""

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
    "docs/evidence/kernel_limits/replay.py",
    "docs/evidence/kernel_limits/proof_obligations.json",
    "docs/notes/annihilator_kernel_limits.md",
    "gororoba_quantum/kernel_limits.py",
    "gororoba_quantum/kernel_limit_contracts.py",
    "gororoba_quantum/circle_kernel_attachments.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/rank_charts.py",
    "gororoba_quantum/four_support_rank.py",
)
ENTRY_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
_validated_snapshot: dict[str, str] | None = None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def hashes(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def digest(matrix: sp.MatrixBase) -> str:
    payload = {"shape": matrix.shape, "entries": [[str(value) for value in row] for row in matrix.tolist()]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def product(first: list[Fraction], second: list[Fraction]) -> list[Fraction]:
    if len(first) == 1:
        return [first[0] * second[0]]
    half = len(first) // 2
    low_first, high_first = first[:half], first[half:]
    low_second, high_second = second[:half], second[half:]

    def conjugate(values: list[Fraction]) -> list[Fraction]:
        return [values[0], *[-value for value in values[1:]]]

    left = product(low_first, low_second)
    subtract = product(conjugate(high_second), high_first)
    right = product(high_second, low_first)
    add = product(high_first, conjugate(low_second))
    return [a - b for a, b in zip(left, subtract, strict=True)] + [a + b for a, b in zip(right, add, strict=True)]


def doubling() -> list[dict[str, Any]]:
    from kernel_limits import cd_polynomial_matrix, certify_kernel_limit

    parameter = sp.Symbol("u", real=True)
    values = [sp.Integer(0)] * 32
    values[1] = values[18] = sp.Integer(1)
    values[3] = values[27] = parameter
    base_operator = cd_polynomial_matrix(values, parameter)
    certificate = certify_kernel_limit(base_operator, parameter)
    admitted = sp.Rational(1, 3)
    projector = sp.Matrix(certificate.projector).subs(parameter, admitted)
    limit = sp.Matrix(certificate.limit_projector)
    frame = sp.Matrix(certificate.kernel_frame).subs(parameter, admitted)
    endpoint_frame = sp.Matrix(certificate.endpoint_frame)
    records = []
    for stage in range(5, 9):
        dimension = len(values)
        require(dimension == 2**stage, "ordinary embedding dimension differs")
        operator = cd_polynomial_matrix(values, parameter).subs(parameter, admitted)
        endpoint_operator = cd_polynomial_matrix(values, parameter).subs(parameter, 0)
        require(operator * frame == sp.zeros(dimension, frame.cols), "embedded generic kernel fails")
        require(
            endpoint_operator * endpoint_frame == sp.zeros(dimension, endpoint_frame.cols),
            "embedded endpoint kernel fails",
        )
        require(
            projector * frame == frame and projector * projector == projector and projector.T == projector,
            "embedded projector fails",
        )
        require(
            limit * limit == limit and limit.T == limit and endpoint_operator * limit == sp.zeros(dimension),
            "embedded limit fails",
        )
        require(projector.trace() == frame.cols and limit.trace() == frame.cols, "embedded trace rank fails")
        require(
            frame.cols == 8 * 2 ** (stage - 5) and endpoint_frame.cols == 12 * 2 ** (stage - 5),
            "embedded dimension formula fails",
        )
        first = [Fraction(index + 1, dimension + 1) for index in range(dimension)]
        second = [Fraction((-1) ** index, index + 1) for index in range(dimension)]
        independent = product(first, second)
        actual = cd_polynomial_matrix(first, parameter) * sp.Matrix([sp.Rational(value) for value in second])
        require(
            actual == sp.Matrix([sp.Rational(value) for value in independent]), "independent recursive product differs"
        )
        p = 4 * 2 ** (stage - 5)
        records.append(
            {
                "stage": stage,
                "dimension": dimension,
                "generic_nullity": frame.cols,
                "endpoint_nullity": endpoint_frame.cols,
                "projector_sha256": digest(projector),
                "limit_projector_sha256": digest(limit),
                "attachment_image_homology_degrees": [0, p + 1, 2 * p - 1, 2 * p],
                "restricted_incidence_homotopy_sphere_dimension": 3 * p - 1,
                "independent_recursive_product_verified": True,
            }
        )
        if stage < 8:
            conjugation = sp.diag(1, *([-1] * (dimension - 1)))
            right = cd_polynomial_matrix(values, parameter, "right").subs(parameter, admitted)
            require(right == -conjugation * operator * conjugation, "pure right/left conjugation fails")
            values = [*values, *([sp.Integer(0)] * dimension)]
            next_operator = cd_polynomial_matrix(values, parameter).subs(parameter, admitted)
            require(next_operator == sp.diag(operator, right), "ordinary embedding block action fails")
            previous_gram = frame.T * frame
            previous_endpoint_gram = endpoint_frame.T * endpoint_frame
            frame = sp.diag(frame, conjugation * frame)
            endpoint_frame = sp.diag(endpoint_frame, conjugation * endpoint_frame)
            require(frame.T * frame == sp.diag(previous_gram, previous_gram), "independence Gram induction fails")
            require(
                endpoint_frame.T * endpoint_frame == sp.diag(previous_endpoint_gram, previous_endpoint_gram),
                "endpoint Gram induction fails",
            )
            projector = sp.diag(projector, conjugation * projector * conjugation)
            limit = sp.diag(limit, conjugation * limit * conjugation)
    return records


def topology() -> dict[str, Any]:
    # S1 x S3 has four product cells. Suspending its reduced chains four
    # times gives the attachment-image degrees. The note proves the model.
    circle_cells, sphere_cells = (0, 1), (0, 3)
    product_cells = sorted(left + right for left in circle_cells for right in sphere_cells)
    reduced_cells = [degree for degree in product_cells if degree > 0]
    attachment_cells = [0, *[degree + 4 for degree in reduced_cells]]
    require(attachment_cells == [0, 5, 7, 8], "join chain degree shift differs")
    boundaries: dict[int, list[int]] = {degree: [] for degree in attachment_cells}
    require(all(len(entries) == 0 for entries in boundaries.values()), "product/suspension boundary differs")
    cup_targets = [(left, right, left + right) for left in attachment_cells[1:] for right in attachment_cells[1:]]
    require(all(target > 8 for _, _, target in cup_targets), "cup degree exclusion fails")
    return {
        "identified_space": "S3 * (S1 x S3)",
        "product_cell_degrees": product_cells,
        "reduced_suspension_shift": 4,
        "homology": {str(degree): "Z" for degree in attachment_cells},
        "torsion": "zero",
        "positive_cup_products": "zero",
        "cell_boundaries": boundaries,
        "cup_degree_checks": cup_targets,
        "restricted_total_incidence_sdr_target": "S11",
        "scope": (
            "attachment image and total pair incidence of the named affine cone slice; ambient pair space remains open"
        ),
    }


def worker_origins(root: Path) -> None:
    require(
        Path(__file__).resolve() == (root / SOURCE_FILES[0]).resolve(),
        "worker replay source differs from the declared checkout",
    )
    for source in SOURCE_FILES:
        if source.startswith("gororoba_quantum/") and Path(source).stem in sys.modules:
            loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
            require(loaded == (root / source).resolve(), "worker module differs from declared checkout: " + source)


def bind_snapshot(root: Path, expected: dict[str, str]) -> None:
    global _validated_snapshot
    worker_origins(root)
    require(ENTRY_SOURCE_SHA256 == expected[SOURCE_FILES[0]], "cached replay code differs from expected source")
    require(hashes(root) == expected, "source snapshot changes before audit")
    if _validated_snapshot is None:
        for source in SOURCE_FILES:
            # The spawn executor imports parallel before dispatch. Family
            # modules require a validated snapshot before their first import.
            if source.startswith("gororoba_quantum/") and Path(source).stem != "parallel":
                require(Path(source).stem not in sys.modules, "unbound cached source module: " + source)
        _validated_snapshot = expected.copy()
    else:
        require(_validated_snapshot == expected, "cached source snapshot differs from expected source")


def independent_family(task: tuple[str, str, dict[str, str]]) -> dict[str, object]:
    name, directory, expected = task
    root = Path(directory).resolve()
    sys.path.insert(0, str(root / "gororoba_quantum"))
    bind_snapshot(root, expected)
    if name == "paths":
        from kernel_limit_contracts import audit_kernel_limits

        operation = audit_kernel_limits
    elif name == "cone":
        from circle_kernel_attachments import audit_circle_kernel_attachments

        operation = audit_circle_kernel_attachments
    else:
        raise ValueError("unknown kernel attachment evidence family")
    worker_origins(root)
    result = operation()
    worker_origins(root)
    require(hashes(root) == expected, "worker source snapshot changes during audit")
    return result


def audit(root: Path) -> dict[str, Any]:
    before = hashes(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    bind_snapshot(root, before)
    from parallel import ordered_map

    tasks = [(name, str(root.resolve()), before) for name in ("paths", "cone")]
    paths, circle = ordered_map(independent_family, tasks, min_items=2)
    all_stage = doubling()
    obligations = json.loads((root / "docs/evidence/kernel_limits/proof_obligations.json").read_text())
    require(
        obligations["rocq_status"] == "deferred-until-approved-run-results", "formalization workflow boundary differs"
    )
    for source in SOURCE_FILES:
        if source.startswith("gororoba_quantum/") and Path(source).stem in sys.modules:
            loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
            require(loaded == (root / source).resolve(), "loaded source differs from declared checkout")
    require(hashes(root) == before, "source changes during replay")
    return {
        "schema": "annihilator-kernel-attachment-evidence-v1",
        "versions": {"python": platform.python_version(), "sympy": sp.__version__},
        "qpu_executed": False,
        "polynomial_path_certificates": paths,
        "affine_cone_certificates": circle,
        "ordinary_doubling": all_stage,
        "topological_model": topology(),
        "formalization_obligations": obligations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    result = json.dumps(audit(bundle.parents[2]), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        require(
            result.encode() == (bundle / "result.json").read_bytes(),
            "kernel attachment replay differs from retained bytes",
        )
        print("Kernel limits, cone ranks/bundles, attachment image, doubling and source hashes pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
