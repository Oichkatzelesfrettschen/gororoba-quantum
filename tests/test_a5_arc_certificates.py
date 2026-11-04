"""Arc certificates of the A_5 exceptional fibers: the P2 family on a few grid points, its mutations, the records."""

import dataclasses
import json
import re
import sys
from pathlib import Path

import pytest

ARCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "arcs"
sys.path.insert(0, str(ARCS_DIR))

import arc_targets as T  # noqa: E402
import certify as C  # noqa: E402
from gen_family import P1_FAMILY, P2_FAMILY  # noqa: E402

TARGET = T.TARGETS["e8nm-p32009"]
POINTS = [(1, 2, 1, 4, 2), (3, 5, 6, 11, 3), (7, 13, 19, 4, 10)]
P2_LOG = (TARGET.directory / "families" / f"fam_{P2_FAMILY.tag}.log").read_text()
P1_LOG = (TARGET.directory / "families" / f"fam_{P1_FAMILY.tag}.log").read_text()


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_p2_family_certificate_on_grid_points() -> None:
    res = C.certify(TARGET, P2_FAMILY, "P2", P2_LOG, POINTS)
    _check(res["points_checked"] == len(POINTS))
    _check(res["order_nu"] == 2)
    _check(all(v == 0 for v in res["failures"].values()))
    _check(set(res["jacobian_rank"].values()) == {4})


def test_p1_family_certificate_on_grid_points() -> None:
    res = C.certify(TARGET, P1_FAMILY, "P1", P1_LOG, POINTS[:2])
    _check(res["order_nu"] == 5)
    _check(all(v == 0 for v in res["failures"].values()))
    _check(set(res["jacobian_rank"].values()) == {5})


def test_corrupted_symbolic_vector_fails_the_certificate() -> None:
    corrupted = re.sub(r"^(FJ 3 .*)$", r"\1+1", P2_LOG, count=1, flags=re.M)
    _check(corrupted != P2_LOG)
    res = C.certify(TARGET, P2_FAMILY, "P2", corrupted, POINTS)
    _check(res["failures"]["symbolic"] == len(POINTS))


def test_opposite_sign_of_t9_leaves_the_slice() -> None:
    flipped = dataclasses.replace(TARGET, sign9=-TARGET.sign9)
    res = C.certify(flipped, P2_FAMILY, "P2", P2_LOG, POINTS)
    _check(res["failures"]["J_nonzero"] > 0)
    _check(res["failures"]["symbolic"] > 0)


def test_the_certificate_separates_the_components() -> None:
    res = C.certify(TARGET, P2_FAMILY, "P1", P2_LOG, POINTS)
    _check(res["failures"]["not_target"] == len(POINTS))


def test_relation_file_digest_binds_to_the_registry() -> None:
    other = dataclasses.replace(TARGET, k2_relations=T.TARGETS["e8nm-p32029"].k2_relations)
    with pytest.raises(ValueError):
        T.k2_ideal(other)


@pytest.mark.parametrize("name", sorted(T.TARGETS))
def test_inputs_of_every_target_verify(name: str) -> None:
    target = T.TARGETS[name]
    _check(len(T.k2_ideal(target).split(",")) == 148)
    _check(T.check_generator_order(target) != "")


@pytest.mark.parametrize("name", sorted(T.TARGETS))
def test_retained_records_certify_both_components(name: str) -> None:
    directory = T.TARGETS[name].directory
    summary = json.loads((directory / "campaign_summary.json").read_text())
    for record, rank in (("result.json", 4), ("result_P1.json", 5)):
        res = json.loads((directory / record).read_text())
        _check(res["certified"] is True)
        _check(res["jacobian_rank"] == rank)
        _check(sum(res["numeric_grid_failures"].values()) == 0)
    _check(summary["hilbert"]["sqrt_k2"]["5"] == 861)
    _check(summary["hilbert"]["sqrt_k2"]["5"] <= summary["hilbert"]["k2"]["5"])
