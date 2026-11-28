"""The placement model of the orientation-architecture analysis reproduces the three retained dry runs, and the merged
diagonal is the retained operator (docs/design/pathion-kernel-map-orientation-architecture.md)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

EVIDENCE = Path(__file__).resolve().parents[2] / "docs" / "evidence" / "pathion-kernel-map" / "orientation-architecture"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _load() -> ModuleType:
    sys.path.insert(0, str(EVIDENCE))
    spec = importlib.util.spec_from_file_location("orientation_architecture", EVIDENCE / "orientation_architecture.py")
    if spec is None or spec.loader is None:
        raise ImportError(str(EVIDENCE))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def analysis() -> ModuleType:
    return _load()


def test_model_reproduces_the_retained_placements(analysis: ModuleType) -> None:
    validation, decomposition = analysis.validation_and_decomposition()
    placed = {b: v["placed"] for b, v in validation.items()}
    require(placed == {"ibm_fez": 4, "ibm_kingston": 8, "ibm_marrakesh": 3}, f"placed regions {placed}")
    for backend, row in validation.items():
        require(row["exclusions_match"], f"{backend}: exclusions")
        require(row["candidates_at_floor"] == row["record_floor_candidates"], f"{backend}: candidates")
        require(row["max_score_error"] < 1e-9, f"{backend}: score")
        require(row["max_ln_esp_error"] < 1e-9 and row["max_ln_coherence_error"] < 1e-9, f"{backend}: terms")
    # the coherence term is the most negative term of ln(score) in all 15 placed regions
    require(sum(v["dominant_counts"]["coherence"] for v in decomposition.values()) == 15, "dominant term")


def test_merged_diagonal_is_the_retained_operator(analysis: ModuleType) -> None:
    require(analysis.operator_invariants()["all_equal"], "merged or sparse circuit departs from its retained operator")


def test_model_rejects_a_perturbed_calibration(analysis: ModuleType) -> None:
    """Known-bad input: one raised CZ error changes the score, so the equalities above are not vacuous."""
    model = analysis.M
    pattern = model.patterns()["ibm_kingston"]
    dev = model.Dev(model.device("ibm_kingston", "dry"))
    ops = pattern["members"]["kmo_ctrl_e1pe26_plus"]["ops"]
    identity = {q: q for q in pattern["replica0"]}
    base = model.score_terms(ops, identity, dev)["ln_score"]
    edge = next(e for e in dev.cz if e[0] in identity and e[1] in identity)
    dev.cz[edge] = {**dev.cz[edge], "error": dev.cz[edge]["error"] + 0.01}
    require(model.score_terms(ops, identity, dev)["ln_score"] < base - 1e-4, "score ignores the CZ error")
