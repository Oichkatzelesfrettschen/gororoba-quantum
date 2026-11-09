"""Every retained Quandela case on a per-iteration-compiled QPU types how its preregistered scatter checks carry the
per-seed mesh variance (qd_platform.scatter_check_gaps, strategy.md section 7 rule 1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_platform  # noqa: E402

# Cases whose cases.json bytes the submitted or built request digests pin, written before the typed rule. Each value
# names where its untyped text carries the mesh-variance term, or that it carries none.
UNTYPED = {
    "ascella_cz_tomography_reference": "none: the overdispersion reference draws from the acquisition law alone, and "
    "docs/notes/topics/ascella-cz-tomography-band-results.md reads its failed check against the rule",
    "ascella_cz_ensemble": "estimate_2_mesh_variance: homogeneity_test compares ten seed tables per setting",
    "belenos_mode_swap_interleaved": "mesh_variance: slot_homogeneity adds the per-class per-seed variance sigma_c^2",
}
CASES = sorted((ROOT / "results/quandela/cases").glob("*/*/cases.json"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_the_rule_reads_retained_cases() -> None:
    require(len(CASES) > 100, f"only {len(CASES)} retained cases found")


@pytest.mark.parametrize("path", CASES, ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
def test_scatter_checks_type_a_mesh_variance_term(path: Path) -> None:
    case = json.loads(path.read_text(encoding="utf-8"))
    gaps = qd_platform.scatter_check_gaps(case.get("platforms") or [], case.get("preregistered") or {})
    if path.parent.parent.name in UNTYPED:
        require(bool(gaps), "a listed case that now satisfies the typed rule leaves UNTYPED")
        return
    require(not gaps, f"scatter checks without a typed mesh-variance term: {gaps}")


def test_the_rule_reads_kinds_not_wording() -> None:
    check = {"statistic": "Pearson", "reference": "multinomial draws under the fit"}
    replicate = {"kind": "replicate_seeds", "seeds_per_setting": 5, "degrees_of_freedom": 4}
    anchors = {"kind": "anchors", "anchors": 16, "repeats_per_anchor": 2}
    quiet = {"kind": "non_decisional", "gates": []}
    gating = {"kind": "non_decisional", "gates": ["fidelity verdict"]}
    too_few = {**replicate, "seeds_per_setting": 1}
    cases = (
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
    )
    for platforms, preregistered, expected in cases:
        found = qd_platform.scatter_check_gaps(platforms, preregistered)
        require(found == expected, f"{platforms} {preregistered}: {found} != {expected}")
