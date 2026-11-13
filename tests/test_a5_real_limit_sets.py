"""The Hermitian splitting of ker C_z and the fiber rows behind the real limit sets from nullity 8 to nullity 12."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import real_limit_sets as rls  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_hermitian_complement_splits_the_kernel_at_an_isotropic_point_and_the_bilinear_one_fails() -> None:
    row = rls._split_record(("e_1 + i e_2", rls.ISOTROPIC_POINT))
    _same((row["kernel_dimension"], row["c_z_annihilates_z"], row["bilinear_norm"]), (7, True, ["0", "0"]))
    _same(row["hermitian"], {"complement_dimension": 6, "direct_sum_is_the_kernel": True, "span_with_z_dimension": 7})
    _same(row["bilinear"]["direct_sum_is_the_kernel"], False)


def test_both_pairings_split_the_kernel_at_a_point_with_nonzero_bilinear_norm() -> None:
    row = rls._split_record(("sum_j j e_j", rls.ANISOTROPIC_POINT))
    _same((row["hermitian"]["direct_sum_is_the_kernel"], row["bilinear"]["direct_sum_is_the_kernel"]), (True, True))


def test_a_fiber_component_that_no_retained_arc_reaches_is_listed() -> None:
    arc = {"component_indices_one_based": [2], "in_fiber": True}
    check = {"holomorphic_kernel_matches_committed_plane_plus_boundary_line": True}
    fixture: dict[str, Any] = {
        "incidence": "fixture",
        "nakayama_generator_count": 6,
        "characteristic_invariants_agree": True,
        "arc_checks": [check, check],
        "rational": {
            "arcs": [arc, arc],
            "image_projective_dimension": 2,
            "image_degree": 2,
            "component_count": 2,
        },
    }
    row = rls._nakayama_row(fixture)
    _same(row["fiber_projective_dimension_degree_components"], [2, 2, 2])
    _same((row["components_reached_by_a_retained_arc"], row["components_without_a_retained_arc"]), ([2], [1]))


@pytest.mark.audit
def test_retained_record_is_the_regenerated_record() -> None:
    record = rls.build_record()
    _same(record["pass"], True)
    _same(rls._record_bytes(record), (ATTACHMENTS / "real-limit-sets-result.json").read_bytes())
