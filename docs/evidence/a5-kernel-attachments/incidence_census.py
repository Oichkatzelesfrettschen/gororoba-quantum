"""Exact incidence census and first-order real/complex probe for A_5 kernel attachments."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cache, partial
from pathlib import Path
from typing import Any, TypeAlias, cast

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
NULLITY_EIGHT = HERE.parent / "a5-kernel-bundles-nullity8"
REGULARITY = HERE.parent / "a5-strata-regularity"
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_frames  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-attachments-incidence-census-v1"
MATRIX_DIMENSION = 16
SPLIT_DIMENSION = 15
MOVEMENTS = ("canonical", "unipotent", "boost")
PASSAGE_ORDER = {(8, 12): 0, (12, 16): 1, (8, 16): 2}
SOURCE_PATHS = (
    HERE / "incidence_census.py",
    KERNEL_BUNDLES / "kernel_frames.py",
    NULLITY_EIGHT / "boundary_specializations.py",
    REGULARITY / "verify_regularity_independent.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)

RationalVector: TypeAlias = tuple[Fraction, ...]
RationalMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class IncidenceSpec:
    source_orbit: str
    boundary_orbit: str
    source_nullity: int
    boundary_nullity: int

    @property
    def passage(self) -> str:
        return f"{self.source_nullity}->{self.boundary_nullity}"

    @property
    def name(self) -> str:
        return f"{self.source_orbit}->{self.boundary_orbit}"


@dataclass(frozen=True)
class PointSpec:
    boundary_orbit: str
    movement: str
    coordinates: RationalVector

    @property
    def key(self) -> str:
        return f"{self.boundary_orbit}:{self.movement}"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_strings(values: Sequence[Fraction]) -> list[str]:
    return list(map(str, values))


def _incidence_candidate(pair: tuple[str, str]) -> IncidenceSpec | None:
    source_orbit, boundary_orbit = pair
    source_nullity = independent.NULLITY[source_orbit]
    boundary_nullity = independent.NULLITY[boundary_orbit]
    nullity_pair = (source_nullity, boundary_nullity)
    if nullity_pair not in PASSAGE_ORDER or boundary_orbit not in independent.LOWER[source_orbit]:
        return None
    return IncidenceSpec(source_orbit, boundary_orbit, source_nullity, boundary_nullity)


def _incidence_specs() -> tuple[IncidenceSpec, ...]:
    orbit_pairs = tuple(itertools.permutations(independent.CLOSURES, 2))
    candidates = parallel.ordered_map(_incidence_candidate, orbit_pairs, min_items=1)
    incidences = tuple(candidate for candidate in candidates if candidate is not None)
    return tuple(
        sorted(
            incidences,
            key=lambda incidence: (
                PASSAGE_ORDER[(incidence.source_nullity, incidence.boundary_nullity)],
                incidence.source_orbit,
                incidence.boundary_orbit,
            ),
        )
    )


@cache
def _unipotent_automorphism() -> RationalMatrix:
    nilpotent_derivations = independent.nilpotent_derivations()
    selected_indices = (0, len(nilpotent_derivations) // 2, len(nilpotent_derivations) - 1)
    factors = tuple(independent.expm_nilpotent(nilpotent_derivations[index]) for index in selected_indices)
    product = independent.matmul7(independent.matmul7(factors[0], factors[1]), factors[2])
    _require(independent.is_automorphism(product), "the selected unipotent product is not a G_2 automorphism")
    return tuple(tuple(Fraction(value) for value in row) for row in product)


def _point_spec(task: tuple[str, str], unipotent_automorphism: RationalMatrix) -> PointSpec:
    boundary_orbit, movement = task
    representative = tuple(Fraction(value) for value in independent.REPS[boundary_orbit])
    if movement == "canonical":
        coordinates = representative
    elif movement == "unipotent":
        coordinates = tuple(Fraction(value) for value in independent.act_g2(unipotent_automorphism, representative))
    elif movement == "boost":
        coordinates = tuple(
            Fraction(value)
            for value in independent.act_boost(independent.BOOST[0], independent.BOOST[1], representative)
        )
    else:
        raise ValueError(f"unknown point movement {movement!r}")
    return PointSpec(boundary_orbit, movement, coordinates)


@cache
def _derivative_parts(mutation: str = "") -> tuple[sp.Matrix, sp.Matrix]:
    if mutation not in ("", "anti_interior_wedge"):
        raise ValueError(f"unknown derivative mutation {mutation!r}")
    holomorphic_symbols = sp.symbols("h1:16")
    antiholomorphic_symbols = sp.symbols("a1:16")
    holomorphic_coordinates = tuple(
        sp.I ** coordinate.bit_count() * holomorphic_symbols[coordinate - 1]
        for coordinate in range(1, MATRIX_DIMENSION)
    )
    antiholomorphic_coordinates = tuple(
        sp.conjugate(sp.I ** coordinate.bit_count()) * antiholomorphic_symbols[coordinate - 1]
        for coordinate in range(1, MATRIX_DIMENSION)
    )
    holomorphic = sp.zeros(MATRIX_DIMENSION)
    antiholomorphic = sp.zeros(MATRIX_DIMENSION)
    for coordinate, value in enumerate(antiholomorphic_coordinates, start=1):
        antiholomorphic[0, coordinate] = -value
        antiholomorphic[coordinate, 0] = value
    for row in range(1, MATRIX_DIMENSION):
        for column in range(1, MATRIX_DIMENSION):
            product = row ^ column
            if product:
                holomorphic[row, column] = (
                    cd_sign(MATRIX_DIMENSION, product, column) * holomorphic_coordinates[product - 1]
                )
    if mutation == "anti_interior_wedge":
        antiholomorphic[1, 2] += antiholomorphic_symbols[0]
        antiholomorphic[2, 1] -= antiholomorphic_symbols[0]
    _require(holomorphic.T == -holomorphic, "the holomorphic derivative part is not skew")
    _require(antiholomorphic.T == -antiholomorphic, "the antiholomorphic derivative part is not skew")
    return holomorphic, antiholomorphic


def _point_certificate(point: PointSpec, mutation: str = "") -> dict[str, Any]:
    boundary_nullity = independent.NULLITY[point.boundary_orbit]
    expected_complex_kernel_dimension = boundary_nullity // 2
    expected_matrix_rank = MATRIX_DIMENSION - expected_complex_kernel_dimension
    bordered_matrix = kernel_frames._bordered_matrix(
        kernel_frames._original_z_from_split(cast("Sequence[int]", point.coordinates))
    )
    matrix_rank = int(bordered_matrix.rank())
    pivot = kernel_frames._find_principal_pivot(bordered_matrix, expected_matrix_rank)
    frame, pivot_determinant, pivot_pfaffian = kernel_frames._principal_frame(bordered_matrix, pivot)
    holomorphic, antiholomorphic = _derivative_parts(mutation)
    holomorphic_restriction = sp.simplify(frame.T * holomorphic * frame)
    antiholomorphic_restriction = sp.simplify(frame.T * antiholomorphic * frame)
    zero_restriction = sp.zeros(expected_complex_kernel_dimension)
    memberships = independent.membership(point.coordinates)
    membership_names = tuple(filter(memberships.__getitem__, independent.CLOSURES))
    expected_pattern = independent.pattern(independent.REPS[point.boundary_orbit])
    observed_pattern = independent.pattern(point.coordinates)
    point_nullity = independent.nullity_ly(point.coordinates)
    frame_identity_verified = bordered_matrix * frame == sp.zeros(MATRIX_DIMENSION, expected_complex_kernel_dimension)
    scalar_coordinate_zero = frame[0, :] == sp.zeros(1, expected_complex_kernel_dimension)
    antiholomorphic_restriction_zero = antiholomorphic_restriction == zero_restriction
    movement_is_distinct = point.movement == "canonical" or point.coordinates != tuple(
        independent.REPS[point.boundary_orbit]
    )
    passed = (
        mutation == ""
        and observed_pattern == expected_pattern
        and point_nullity == boundary_nullity
        and matrix_rank == expected_matrix_rank
        and frame.cols == expected_complex_kernel_dimension
        and pivot_pfaffian != 0
        and frame_identity_verified
        and scalar_coordinate_zero
        and antiholomorphic_restriction_zero
        and movement_is_distinct
    )
    return {
        "key": point.key,
        "boundary_orbit": point.boundary_orbit,
        "movement": point.movement,
        "split_coordinates": _fraction_strings(point.coordinates),
        "movement_is_distinct": movement_is_distinct,
        "membership_pattern": observed_pattern,
        "expected_membership_pattern": expected_pattern,
        "memberships": list(membership_names),
        "real_left_nullity": point_nullity,
        "expected_real_left_nullity": boundary_nullity,
        "bordered_matrix_rank": matrix_rank,
        "expected_bordered_matrix_rank": expected_matrix_rank,
        "complex_kernel_dimension": frame.cols,
        "pivot_indices": list(pivot),
        "pivot_pfaffian": str(pivot_pfaffian),
        "pivot_determinant": str(pivot_determinant),
        "frame_identity_verified": frame_identity_verified,
        "scalar_coordinate_row": list(map(str, frame[0, :])),
        "scalar_coordinate_zero": scalar_coordinate_zero,
        "holomorphic_restriction": str(holomorphic_restriction.tolist()),
        "holomorphic_restriction_zero": holomorphic_restriction == zero_restriction,
        "antiholomorphic_restriction": str(antiholomorphic_restriction.tolist()),
        "antiholomorphic_restriction_zero": antiholomorphic_restriction_zero,
        "complex_linear_first_order": antiholomorphic_restriction_zero,
        "mutation": mutation,
        "pass": passed,
    }


def _point_certificate_task(point: PointSpec) -> dict[str, Any]:
    return _point_certificate(point)


def _incidence_row(incidence: IncidenceSpec, point_records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    point_keys = tuple(f"{incidence.boundary_orbit}:{movement}" for movement in MOVEMENTS)
    points = tuple(point_records[key] for key in point_keys)
    source_membership = tuple(incidence.source_orbit in point["memberships"] for point in points)
    boundary_membership = tuple(incidence.boundary_orbit in point["memberships"] for point in points)
    complex_verdicts = tuple(bool(point["complex_linear_first_order"]) for point in points)
    verdict_stable = len(set(complex_verdicts)) == 1
    passed = (
        all(bool(point["pass"]) for point in points)
        and all(source_membership)
        and all(boundary_membership)
        and all(complex_verdicts)
        and verdict_stable
    )
    return {
        "incidence": incidence.name,
        "passage": incidence.passage,
        "source_orbit": incidence.source_orbit,
        "boundary_orbit": incidence.boundary_orbit,
        "source_nullity": incidence.source_nullity,
        "boundary_nullity": incidence.boundary_nullity,
        "point_keys": list(point_keys),
        "source_closure_membership": list(source_membership),
        "boundary_orbit_membership": list(boundary_membership),
        "complex_linearity_verdicts": list(complex_verdicts),
        "moved_point_verdict_stable": verdict_stable,
        "complex_linear_first_order": all(complex_verdicts),
        "pass": passed,
    }


def _mutation_control(point_records: dict[str, dict[str, Any]], point_specs: Sequence[PointSpec]) -> dict[str, Any]:
    target = next(point for point in point_specs if point.key == "B9:canonical")
    baseline = point_records[target.key]
    mutated = _point_certificate(target, "anti_interior_wedge")
    detected = (
        bool(baseline["antiholomorphic_restriction_zero"])
        and not bool(mutated["antiholomorphic_restriction_zero"])
        and bool(baseline["complex_linear_first_order"])
        and not bool(mutated["complex_linear_first_order"])
        and not bool(mutated["pass"])
    )
    return {
        "name": "anti_interior_wedge",
        "target": target.key,
        "input_change": ("add a_1 times the skew basis wedge E_12-E_21 to the antiholomorphic derivative input"),
        "baseline_antiholomorphic_restriction_zero": baseline["antiholomorphic_restriction_zero"],
        "mutated_antiholomorphic_restriction_zero": mutated["antiholomorphic_restriction_zero"],
        "mutated_antiholomorphic_restriction": mutated["antiholomorphic_restriction"],
        "detected": detected,
    }


def build_record() -> dict[str, Any]:
    incidence_specs = _incidence_specs()
    boundary_orbits = tuple(sorted(set(incidence.boundary_orbit for incidence in incidence_specs)))
    point_tasks = tuple(itertools.product(boundary_orbits, MOVEMENTS))
    unipotent_automorphism = _unipotent_automorphism()
    point_specs = parallel.ordered_map(
        partial(_point_spec, unipotent_automorphism=unipotent_automorphism), point_tasks, min_items=1
    )
    point_rows = parallel.ordered_map(_point_certificate_task, point_specs, min_items=1)
    point_records = {str(row["key"]): row for row in point_rows}
    incidence_rows = parallel.ordered_map(
        partial(_incidence_row, point_records=point_records), incidence_specs, min_items=1
    )
    passage_counts = Counter(str(row["passage"]) for row in incidence_rows)
    complex_incidence_count = sum(bool(row["complex_linear_first_order"]) for row in incidence_rows)
    mutation_control = _mutation_control(point_records, point_specs)
    nilpotent_derivations = independent.nilpotent_derivations()
    unipotent_span = independent.q_rank(
        [[entry for row in derivation for entry in row] for derivation in nilpotent_derivations]
    )
    passed = (
        all(bool(row["pass"]) for row in point_rows)
        and all(bool(row["pass"]) for row in incidence_rows)
        and complex_incidence_count == len(incidence_rows)
        and bool(mutation_control["detected"])
    )
    return {
        "schema": SCHEMA,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "scope": {
            "included_nullity_passages": ["8->12", "12->16", "8->16"],
            "same_nullity_incidences": "excluded by the program's constant-rank inference",
            "claim_boundary": (
                "The certificate decides the first-order complex-linearity probe at three exact points per boundary "
                "orbit. It does not determine a Gauss-graph fiber, its higher-order limits, or variation over the "
                "whole boundary orbit."
            ),
        },
        "incidence_derivation": {
            "authority": "verify_regularity_independent.LOWER and .NULLITY",
            "incidence_count": len(incidence_rows),
            "counts_by_passage": dict(sorted(passage_counts.items())),
            "boundary_orbit_count": len(boundary_orbits),
            "point_count": len(point_rows),
            "complex_linear_incidence_count": complex_incidence_count,
        },
        "movement_certificate": {
            "movements": list(MOVEMENTS),
            "nilpotent_derivations_found": len(nilpotent_derivations),
            "nilpotent_span_dimension": unipotent_span,
            "unipotent_product_is_automorphism": independent.is_automorphism(unipotent_automorphism),
            "boost_c": str(independent.BOOST[0]),
            "boost_s": str(independent.BOOST[1]),
            "boost_identity_verified": independent.BOOST[0] ** 2 - independent.BOOST[1] ** 2 == 1,
        },
        "mechanism": {
            "antiholomorphic_support": "the scalar border of A(z,conjugate(z))",
            "certificate": (
                "Every exact boundary-kernel frame has zero scalar-coordinate row, so F^T A^(0,1)(dbar) F "
                "vanishes identically in all fifteen ambient directions."
            ),
        },
        "points": point_rows,
        "incidences": incidence_rows,
        "mutation_control": mutation_control,
        "falsifier": (
            "A closure-derived incidence is absent; an exact point leaves its boundary orbit or source closure; a "
            "point has the wrong nullity; a kernel frame has a nonzero scalar-coordinate row; an antiholomorphic "
            "restriction is nonzero; a moved point reverses the verdict; or the input mutation survives."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the baseline incidence census failed")
    _require(bool(record["mutation_control"]["detected"]), "the derivative-input mutation survived")
    _require(
        record["incidence_derivation"]["incidence_count"]
        == record["incidence_derivation"]["complex_linear_incidence_count"],
        "at least one incidence lacks the exact first-order complex-linearity certificate",
    )


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
