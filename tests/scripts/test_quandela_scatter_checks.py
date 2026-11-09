"""Every retained Quandela case on a per-iteration-compiled QPU states how its preregistered scatter check carries the
per-seed mesh variance (qd_platform.scatter_check_gaps, strategy.md section 7 rule 1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_platform  # noqa: E402

# Cases frozen and run before the rule: their cases.json bytes are pinned by the submitted request digests, and
# docs/notes/topics/ascella-cz-tomography-band-results.md reads their failed scatter check against it.
FROZEN = {"ascella_cz_tomography_reference"}
CASES = sorted((ROOT / "results/quandela/cases").glob("*/*/cases.json"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_the_rule_reads_retained_cases() -> None:
    require(len(CASES) > 100, f"only {len(CASES)} retained cases found")


@pytest.mark.parametrize("path", CASES, ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
def test_scatter_checks_name_a_mesh_variance_term(path: Path) -> None:
    case = json.loads(path.read_text(encoding="utf-8"))
    gaps = qd_platform.scatter_check_gaps(case.get("platforms") or [], case.get("preregistered") or {})
    if path.parent.parent.name in FROZEN:
        require(bool(gaps), "a frozen case that now satisfies the rule leaves FROZEN")
        return
    require(not gaps, f"scatter checks without a mesh-variance term: {gaps}")


def test_the_rule_rejects_an_acquisition_only_reference() -> None:
    check = {"statistic": "Pearson", "reference": "multinomial draws under the fit"}
    replicate = {**check, "mesh_variance": "replicate seeds: five seeds per setting, between-seed spread pooled"}
    descriptive = {**check, "mesh_variance": "descriptive: every setting runs on its own seed"}
    cases = (
        (["qpu:ascella"], {"overdispersion": check}, ["overdispersion"]),
        (["sim:ascella"], {"overdispersion": check}, []),
        (["qpu:belenos"], {"overdispersion": replicate}, []),
        (["qpu:ascella"], {"model_check": descriptive}, []),
        (["qpu:ascella"], {"overdispersion": {**check, "mesh_variance": ""}}, ["overdispersion"]),
    )
    for platforms, preregistered, expected in cases:
        found = qd_platform.scatter_check_gaps(platforms, preregistered)
        require(found == expected, f"{platforms} {preregistered}: {found} != {expected}")
