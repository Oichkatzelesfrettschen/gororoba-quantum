"""The real nullity-4 points of V(Q) n V(G): the identities, the witnesses, the retained points and the record rules."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_gauss_image as gauss  # noqa: E402
import nullity4_qg_intersection as qg  # noqa: E402
import sympy as sp  # noqa: E402

SLOW = {"kernel_independence"}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _identity_param(name: str) -> Any:
    return pytest.param(name, marks=pytest.mark.audit) if name in SLOW else name


@pytest.mark.parametrize("name", [_identity_param(name) for name in qg.IDENTITIES])
def test_exact_identity_holds(name: str) -> None:
    _same(qg.identity(name), True)


def test_kernel_vector_needs_its_signs() -> None:
    # The first vector with the sign of its first coordinate reversed leaves the kernel of M(z(s)).
    m = qg.msym(qg.normal_point(qg.S))
    k0 = qg.kernel_vectors(qg.S)[0]
    _same(all(sp.expand(entry) == 0 for entry in m * sp.Matrix(k0)), True)
    k0[0] = -k0[0]
    _same(all(sp.expand(entry) == 0 for entry in m * sp.Matrix(k0)), False)


def test_reduction_of_the_fiber_to_the_common_kernel() -> None:
    # dim L = 2 (dim C(P) - 2): the retained grid classes of the stratum are (common kernel, cut) = (3, 1) and (5, 3).
    classes = {key: count for key, count in gauss.KERNEL_FORM_GRID.items() if key[0] == qg.STRATUM}
    _same(sorted((key[1], key[3], key[4]) for key in classes), [(2, 3, 1), (6, 5, 3)])
    for fiber, _, common, cut in ((key[1], key[2], key[3], key[4]) for key in classes):
        _same(fiber, 2 * cut)
        _same(cut, common - 2)


def test_common_kernel_dimensions_of_the_three_planes() -> None:
    # At s = 2 the planes of the three lines have dim C(P) = 5, 4, 4 and the nullity of M(k1) is 7; the plane
    # (k0, k1) through no line has dim C(P) = 3.
    _same(qg.special_facts(2), [5, 4, 4, 7])
    k0, k1, _ = qg.kernel_vectors(sp.Integer(2))
    generic = [sp.expand(a + 3 * b) for a, b in zip(k0, k1, strict=True)]
    stack = [*qg.msym(k0).tolist(), *qg.msym(generic).tolist()]
    _same(15 - qg._rank(stack), 3)


def test_line_x_has_nullity_seven_over_the_function_field() -> None:
    _same(qg.line_x_rank(), qg.LINE_X_RANK)
    # Dropping k2 leaves the vertex k1 alone, whose rank is also 8; the sum of the rank of the whole line and the
    # rank of M(k0), 12, are different.
    k0 = qg.kernel_vectors(qg.S)[0]
    _same(qg._function_field_rank(qg.msym(k0).applyfunc(sp.expand)), 12)


def test_special_values_of_s_raise_the_line_x() -> None:
    _same(qg.special_facts(1), [7, 4, 4, 9])
    _same(qg.special_facts(0), [5, 4, 4, 7])


@pytest.mark.parametrize("label", ["s = 0, x", "s = 0, y", "s = 0, z"])
def test_witness_has_the_pinned_facts(label: str) -> None:
    s, plane = int(label.split(",")[0].split("=")[1]), label[-1]
    found_label, row, point = qg.witness_facts((s, plane))
    _same(found_label, label)
    _same(row, qg.WITNESS_FACTS[label])
    _same(point, qg.WITNESS_POINTS[label])


def test_witness_for_the_wrong_plane_changes_the_fiber() -> None:
    # The point orthogonal to the plane x has kernel plane P_x; reading its fiber from another point of K moves it.
    x = qg.real_point_facts([sp.sympify(entry) for entry in qg.WITNESS_POINTS["s = 0, x"]])
    y = qg.real_point_facts([sp.sympify(entry) for entry in qg.WITNESS_POINTS["s = 0, y"]])
    _same((x["fiber"], y["fiber"]), (6, 4))


def test_retained_point_has_the_plane_x_facts() -> None:
    rows = qg.retained_points()
    _same(len(rows), qg.RETAINED_POINTS)
    _same(qg.retained_facts(rows[0]), qg.RETAINED_FACTS)
    # The same point with its eighth coordinate changed leaves V(Q) and is no longer a nullity-4 point.
    bad = copy.deepcopy(rows[0])
    bad["split_point"][7] = 3
    with pytest.raises(RuntimeError):
        qg.retained_facts(bad)


def test_totally_isotropic_points_have_rank_ten() -> None:
    _same(qg.isotropic_rank(0), [10, 2])


def test_scan_block_reads_the_special_values() -> None:
    _same(qg.scan_block((0, 6)), [[12, 7, 5, 4, 4, 5], [12, 9, 7, 4, 4, 1]])


def _record() -> dict[str, Any]:
    return json.loads(qg.RECORD.read_text(encoding="utf-8"))


def test_pinned_record_passes_its_rules() -> None:
    record = _record()
    _same(qg.verdict(record), [])
    _same(record["pass"], True)
    _same(qg._serialized(record), qg.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("a scan count", lambda r: r["scan"][0].__setitem__(5, r["scan"][0][5] - 1)),
        ("a witness fiber", lambda r: r["witnesses"]["s = 2, y"].__setitem__(4, 6)),
        ("a witness point", lambda r: r["witness_points"]["s = 2, x"].__setitem__(0, "0")),
        ("an identity", lambda r: r["identities"].__setitem__("kernel_sextic", False)),
        ("a retained fact", lambda r: r["retained_facts"][0].__setitem__(2, 4)),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any) -> None:
    record = _record()
    mutate(record)
    if not qg.verdict(record):
        raise AssertionError(label)
