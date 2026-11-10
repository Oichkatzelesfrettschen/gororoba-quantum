"""Every retained Quandela case on a per-iteration-compiled QPU types how its preregistered scatter checks carry the
per-seed mesh variance (qd_platform.scatter_check_gaps, strategy.md section 7 rule 1)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_platform  # noqa: E402

CASES = sorted((ROOT / "results/quandela/cases").glob("*/*/cases.json"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_the_rule_reads_retained_cases() -> None:
    require(len(CASES) > 100, f"only {len(CASES)} retained cases found")


@pytest.mark.parametrize("path", CASES, ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
def test_scatter_checks_type_a_mesh_variance_term(path: Path) -> None:
    case = json.loads(path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    gaps = qd_platform.scatter_check_gaps(case.get("platforms") or [], case.get("preregistered") or {})
    listed = qd_platform.UNTYPED_SCATTER_CASES.get(digest)
    if listed is not None:
        require(listed[0] == f"{path.parent.parent.name}/{path.parent.name}", f"{digest} is listed as {listed[0]}")
        require(tuple(gaps) == listed[1], f"listed gaps {listed[1]} differ from {gaps}")
        return
    for platform in case.get("platforms") or []:
        refusal = qd_platform.scatter_check_refusal(case, digest, platform)
        require(refusal is None, f"untyped scatter checks on {platform}: {gaps}")


def test_every_listed_untyped_case_is_retained() -> None:
    digests = {hashlib.sha256(p.read_bytes()).hexdigest() for p in CASES}
    missing = sorted(set(qd_platform.UNTYPED_SCATTER_CASES) - digests)
    require(not missing, f"UNTYPED_SCATTER_CASES lists digests no retained case has: {missing}")


def test_plan_refusal_binds_the_digest() -> None:
    checks: dict[str, Any] = {"overdispersion": {"statistic": "Pearson"}}
    case: dict[str, Any] = {"platforms": ["qpu:ascella"], "preregistered": checks}
    legacy = next(d for d, (name, _) in qd_platform.UNTYPED_SCATTER_CASES.items() if name.endswith("reference/job-00"))
    refuse = qd_platform.scatter_check_refusal
    require(refuse(case, legacy, "qpu:ascella") is None, "the listed digest with its gaps passes")
    require(refuse(case, "0" * 64, "qpu:ascella") is not None, "an unlisted digest is refused")
    extra = {**case, "preregistered": {**checks, "homogeneity": "Pearson"}}
    require(refuse(extra, legacy, "qpu:ascella") is not None, "a listed digest with other gaps is refused")
    mixed = {**case, "platforms": ["qpu:belenos", "sim:belenos"]}
    require(refuse(mixed, "0" * 64, "sim:belenos") is None, "a simulator plan of a QPU-admitting case is refused")
    require(refuse(mixed, "0" * 64, "qpu:belenos") is not None, "the QPU plan of the same case passes")


def test_the_rule_reads_kinds_not_wording() -> None:
    check = {"statistic": "Pearson", "reference": "multinomial draws under the fit"}
    replicate = {"kind": "replicate_seeds", "seeds_per_setting": 5, "degrees_of_freedom": 4}
    anchors = {"kind": "anchors", "anchors": 16, "repeats_per_anchor": 2}
    quiet = {"kind": "non_decisional", "gates": []}
    gating = {"kind": "non_decisional", "gates": ["fidelity verdict"]}
    too_few = {**replicate, "seeds_per_setting": 1}
    cases: tuple[tuple[list[str], dict[str, Any], list[str]], ...] = (
        (["qpu:ascella"], {"overdispersion": check}, ["overdispersion"]),
        (["sim:ascella"], {"overdispersion": check}, []),
        (["qpu:belenos"], {"overdispersion": {**check, "mesh_variance": replicate}}, []),
        (["qpu:ascella"], {"model_check": {**check, "mesh_variance": anchors}}, []),
        (["qpu:ascella"], {"model_check": {**check, "mesh_variance": quiet}}, []),
        (["qpu:ascella"], {"model_check": {**check, "mesh_variance": gating}}, ["model_check"]),
        (["qpu:ascella"], {"goodness_of_fit": "Pearson against multinomial draws"}, ["goodness_of_fit"]),
        (["qpu:ascella"], {"goodness_of_fit": "Pearson", "mesh_variance": replicate}, []),
        (["qpu:ascella"], {"readings": {"homogeneity": check}}, ["readings/homogeneity"]),
        (["qpu:ascella"], {"homogeneity_alpha": 0.01}, []),
        (["qpu:ascella"], {"overdispersion": {**check, "mesh_variance": "replicate seeds: five"}}, ["overdispersion"]),
        (["qpu:ascella"], {"overdispersion": {**check, "mesh_variance": too_few}}, ["overdispersion"]),
        (["qpu:ascella"], {"validation": check}, ["validation"]),
        (["qpu:ascella"], {"checks": [check]}, ["checks/0"]),
        (["qpu:ascella"], {"checks": [{**check, "mesh_variance": replicate}]}, []),
        (["qpu:ascella"], {"checks": [check], "mesh_variance": anchors}, []),
        (
            ["qpu:ascella"],
            {"overdispersion": {**check, "mesh_variance": replicate, "chi_square_rule": "reject above 0.95"}},
            [],
        ),
    )
    for platforms, preregistered, expected in cases:
        found = qd_platform.scatter_check_gaps(platforms, preregistered)
        require(found == expected, f"{platforms} {preregistered}: {found} != {expected}")
