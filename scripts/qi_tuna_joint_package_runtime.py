"""Measure installed-package agreement on retained Tuna joint-response data."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import algebra_package_tables
import hypercomplex
import hypercomplex_engine
import hyprat
import mpmath
import numpy as np
import pandas as pd
import qi_tuna_joint_algebra
import qi_tuna_joint_response
import SplitOct
import sympy
from flint import fmpq
from qi_tuna_destination_one_analysis import ROOT, SHOTS, digest, json_bytes
from scipy.linalg import hadamard
from scipy.spatial.distance import euclidean, jensenshannon

sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

PACKAGES = {
    "hypercomplex": hypercomplex,
    "hypercomplex-engine": hypercomplex_engine,
    "hyprat": hyprat,
    "splitoct": SplitOct,
}
JOINT = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
ALGEBRA = ROOT / "docs/evidence/tuna-projector-geometry/joint-algebra-analysis.json"


def audit_dimension(dimension: int) -> dict[str, Any]:
    """Check every basis product of three installed ordinary implementations."""
    level = dimension.bit_length() - 1
    algebra = hypercomplex.cayley_dickson_algebra(level, Fraction)
    units = [
        hyprat.Hy.from_array([int(coordinate == index) for coordinate in range(dimension)])
        for index in range(dimension)
    ]
    engine_signs, engine_indices = hypercomplex_engine.build_table("standard", level)
    for left in range(dimension):
        for right in range(dimension):
            index = left ^ right
            sign = cd_sign(dimension, left, right)
            expected = [Fraction(sign if coordinate == index else 0) for coordinate in range(dimension)]
            if list((algebra.e(left) * algebra.e(right)).coefficients()) != expected:
                raise ValueError("hypercomplex installed basis table differs")
            if list((units[left] * units[right]).to_array()) != expected:
                raise ValueError("hyprat installed basis table differs")
            if (int(engine_signs[left][right]), int(engine_indices[left][right])) != (sign, index):
                raise ValueError("hypercomplex-engine installed basis table differs")
    return {
        "dimension": dimension,
        "basis_pairs_per_implementation": dimension * dimension,
        "implementations": list(qi_tuna_joint_algebra.ORDINARY_PACKAGES),
        "basis_map": "identity",
    }


def split_control() -> dict[str, int]:
    """Compare the complete installed split table and all associator signs."""
    standard, _ = hypercomplex_engine.build_table("standard", 3)
    split, indices = hypercomplex_engine.build_table("split", 3)
    units = [SplitOct.SplitOctonion([int(coordinate == index) for coordinate in range(8)]) for index in range(8)]
    for left in range(8):
        for right in range(8):
            expected = [int(split[left][right]) if coordinate == left ^ right else 0 for coordinate in range(8)]
            if int(indices[left][right]) != left ^ right or list((units[left] * units[right]).x) != expected:
                raise ValueError("installed split implementations disagree")
    for left in range(8):
        for middle in range(8):
            for right in range(8):
                if algebra_package_tables.omega(standard, left, middle, right) != algebra_package_tables.omega(
                    split, left, middle, right
                ):
                    raise ValueError("ordinary and split associator signs differ")
    if int(standard[4][4]) != -1 or int(split[4][4]) != 1:
        raise ValueError("ordinary and split e4 squares must differ")
    return {"associator_triples_checked": 512, "ordinary_e4_square": -1, "split_e4_square": 1}


def analyze_job(task: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    """Compare the installed packages on one validated ordered-shot record."""
    case_name, job = task
    raw = ROOT / job["raw"]
    shots = json.loads(raw.read_bytes())
    if digest(raw) != job["raw_sha256"]:
        raise ValueError("shot data differ from the joint-response record")
    columns = job["early_classical_bits"] + [4, 11, 6]
    indices = pd.Series(
        [sum(int(shot[19 - column]) << position for position, column in enumerate(columns)) for shot in shots]
    )
    histogram = indices.value_counts().reindex(range(64), fill_value=0).sort_index().to_numpy()
    if (
        histogram.tolist() != job["joint_counts"]
        or (hadamard(64, dtype=np.int64) @ histogram).tolist() != job["parity_numerators"]
    ):
        raise ValueError("installed pandas/SciPy results differ from the joint replay")
    counts = job["disagreement_counts"]
    algebra = hypercomplex.cayley_dickson_algebra(3, Fraction)
    vector = algebra.e(0) * 0
    for index, count in enumerate(counts):
        vector = vector + Fraction(count, SHOTS) * algebra.e(index)
    left, right = algebra.e(1), algebra.e(6)
    calculated = ((left * right) * vector - left * (right * vector)).coefficients()
    other_vector = hyprat.Hy.from_array([Fraction(count, SHOTS) for count in counts])
    other_left = hyprat.Hy.from_array([0, 1, 0, 0, 0, 0, 0, 0])
    other_right = hyprat.Hy.from_array([0, 0, 0, 0, 0, 0, 1, 0])
    other = ((other_left * other_right) * other_vector - other_left * (other_right * other_vector)).to_array()
    if list(calculated) != list(other):
        raise ValueError("installed exact algebras disagree on a data-derived associator")
    return {
        "case": case_name,
        "batch": job["batch"],
        "job": job["job"],
        "raw_sha256": job["raw_sha256"],
        "associator_norm_squared": str(sum(value * value for value in calculated)),
    }


def capture(archives: Path) -> dict[str, Any]:
    """Bind installed releases, replay the retained data and use the installed packages."""
    bindings = {name: algebra_package_tables.bind_installation(name, archives) for name in PACKAGES}
    for name, module in PACKAGES.items():
        algebra_package_tables.require_bound(module, name)
    joint = qi_tuna_joint_response.analyze()
    if json_bytes(joint) != JOINT.read_bytes():
        raise ValueError("retained joint response differs from its validated replay")
    algebra = qi_tuna_joint_algebra.analyze()
    if json_bytes(algebra) != ALGEBRA.read_bytes():
        raise ValueError("retained algebra summary differs from its validated replay")
    jobs = ordered_map(analyze_job, [(name, row) for name, case in joint["cases"].items() for row in case["jobs"]])
    expected = {(name, row["batch"]): row for name, rows in algebra["cases"].items() for row in rows}
    for row in jobs:
        reference = expected[row["case"], row["batch"]]
        if row["associator_norm_squared"] != reference["associator_norm_squared"]:
            raise ValueError("installed algebra result differs from retained source-bound table replay")
    numerator = joint["cases"]["nominal_one"]["parity_response_numerators"][54]
    sympy_value = sympy.Rational(numerator, 2 * SHOTS)
    flint_value = fmpq(numerator, 2 * SHOTS)
    if str(sympy_value) != str(flint_value):
        raise ValueError("SymPy and FLINT disagree on the exact response contrast")
    with mpmath.workdps(60):
        radius = mpmath.sqrt(3 * mpmath.log(25200) / SHOTS)
        rounded = mpmath.mpf(joint["nominal_one_posthoc_uncertainty"]["response_radius_upper"])
        if not 0 <= rounded - radius < mpmath.mpf("0.000000000001"):
            raise ValueError("mpmath rejects the retained response radius rounding")
    distances = {}
    for name, case in joint["cases"].items():
        probabilities = np.array([job["joint_counts"] for job in case["jobs"]], dtype=np.float64) / SHOTS
        baseline = (probabilities[0] + probabilities[2]) / 2
        distances[name] = {
            "hellinger_decimal_12_places": format(
                euclidean(np.sqrt(probabilities[1]), np.sqrt(baseline)) / math.sqrt(2), ".12f"
            ),
            "jensen_shannon_distance_sqrt_bits_decimal_12_places": format(
                jensenshannon(probabilities[1], baseline, base=2), ".12f"
            ),
        }
    distributions = [*PACKAGES, "numpy", "scipy", "pandas", "sympy", "python-flint", "mpmath"]
    return {
        "schema": "qi-tuna-joint-package-runtime-observation-v1",
        "archive_bindings": bindings,
        "archive_sha256": {name: algebra_package_tables.RELEASES[name][2] for name in PACKAGES},
        "versions": {name: importlib.metadata.version(name) for name in distributions},
        "dimension_tables": ordered_map(audit_dimension, [8, 16]),
        "split_control": split_control(),
        "jobs": jobs,
        "exact_nominal_one_response": str(sympy_value),
        "descriptive_distances": distances,
        "inputs": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in (
                JOINT,
                ALGEBRA,
                ROOT / "scripts/algebra_package_tables.py",
                ROOT / "gororoba_quantum/cd_core.py",
            )
        },
        "producer_sha256": digest(Path(__file__)),
        "boundary": (
            "This local observation binds imported package files to release archives and compares their exact "
            "arithmetic with retained binary data. Package encodings do not establish a physical algebra, "
            "state population, calibration or causal destination effect. Distances are descriptive float64 values."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    content = json_bytes(capture(arguments.archives))
    with arguments.out.open("xb") as destination:
        destination.write(content)
    print("Installed source-bound packages reproduce the six retained joint-data algebra summaries.")


if __name__ == "__main__":
    main()
