import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qi_bdsc_pauli_cases as cases  # noqa: E402

QX_ANALYSIS = ROOT / "results/quantum_inspire/bdsc_pauli_qx_analysis.json"


def cell(kind: str, state: str, mean: float, variance: float, **extra: Any) -> dict[str, Any]:
    return {
        "kind": kind,
        "state": state,
        "patch": 0,
        "shots": 100,
        "parity_mean": mean,
        "parity_variance": variance,
        "parity_tensor_model_mitigated": None,
        **extra,
    }


def deterministic_cells(variance: float) -> list[dict[str, Any]]:
    return [
        cell("quadrature", "k1", -0.5, variance, quadrature={"sin_coefficient": -1.0}),
        cell("quadrature", "b1", 0.5, variance, quadrature={"sin_coefficient": 1.0}),
        cell("quadrature", "e7", 0.0, variance, quadrature={"sin_coefficient": 0.0}),
        cell("cosine", "k1", 0.5, variance, quadrature={"cos_coefficient": 1.0}),
        cell("cosine", "b1", -0.5, variance, quadrature={"cos_coefficient": -1.0}),
    ]


def strict(text: str) -> Any:
    def refuse(token: str) -> float:
        raise ValueError(token)

    return json.loads(text, parse_constant=refuse)


def test_zero_variance_quadrature_is_exact_strict_json() -> None:
    out = cases.quadrature(deterministic_cells(0.0), [0])["patch-0"]
    if out["amplitude_chi2"] is not None or out["amplitude_exact"] is not True or not out["visibility_supported"]:
        raise AssertionError(out)
    text = cases.dumps_analysis({"quadrature": out})
    if strict(text) != json.loads(text):
        raise AssertionError("strict and default parses differ")


def test_finite_quadrature_keeps_its_chi_square() -> None:
    out = cases.quadrature(deterministic_cells(0.25), [0])["patch-0"]
    if not isinstance(out["amplitude_chi2"], float) or out["amplitude_exact"] is not False:
        raise AssertionError(out)


def test_non_finite_float_is_refused_on_write() -> None:
    with pytest.raises(ValueError, match="Out of range"):
        cases.dumps_analysis({"amplitude_chi2": float("inf")})


def test_retained_v3_analysis_has_infinity_and_reads_as_v4_exact() -> None:
    text = QX_ANALYSIS.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="Infinity"):
        strict(text)
    record = cases.parse_analysis(text)
    if record["schema"] != cases.ANALYSIS_SCHEMA:
        raise AssertionError(record["schema"])
    rows = list(record["quadrature"].values())
    if not any(r["amplitude_exact"] for r in rows) or any(r["amplitude_chi2"] == float("inf") for r in rows):
        raise AssertionError("an infinite chi-square survived the upgrade")
    strict(cases.dumps_analysis(record))


def test_v4_record_round_trips_through_parse_analysis() -> None:
    record = {
        "schema": cases.ANALYSIS_SCHEMA,
        "quadrature": cases.quadrature(deterministic_cells(0.0), [0]),
    }
    text = cases.dumps_analysis(record)
    if cases.dumps_analysis(cases.parse_analysis(text)) != text:
        raise AssertionError("round trip differs")
