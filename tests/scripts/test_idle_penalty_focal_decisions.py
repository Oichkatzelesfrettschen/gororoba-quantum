"""Contracts of the focal-qubit decisions on synthetic reports: thresholds, the historical reading and retest."""

from __future__ import annotations

from typing import Any

import idle_penalty_focal_decisions as fd
import pytest

MULTIPLIERS = ("kappa_1", "kappa_2star", "kappa_2echo")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _report(run: str, values: dict[int, float], calibration: str = "C1", se: float = 0.05) -> dict[str, Any]:
    qubits = {}
    for index, (qubit, value) in enumerate(sorted(values.items())):
        entry: dict[str, Any] = {"role": "target" if index % 2 == 0 else "spectator", "partner": qubit + 1000}
        for key in MULTIPLIERS:
            entry[key], entry[f"{key}_se"] = value, se
        qubits[str(qubit)] = entry
    return {"identity": {"run": run, "calibration": calibration}, "qubits": qubits}


@pytest.mark.parametrize(
    ("value", "se", "expected"),
    [(3.0, 0.1, "elevated"), (1.0, 0.05, "nominal"), (1.45, 0.05, "unresolved"), (1.6, 0.1, "unresolved")],
)
def test_classify_thresholds(value: float, se: float, expected: str) -> None:
    _expect(fd.classify(value, se) == expected, f"{value} +- {se} reads {fd.classify(value, se)}")


def test_historical_reading() -> None:
    cohort = {q: 1.0 for q in range(10, 20)}
    nominal = fd.decisions(
        [_report("X", cohort | {79: 1.0, 92: 1.05}), _report("Y", cohort | {93: 0.95})], [79, 92, 93], []
    )
    _expect(nominal["historical_kappa_near_3"] == "weakened", nominal["historical_kappa_near_3"])
    _expect(nominal["same_window"], "one calibration read as two")
    elevated = fd.decisions(
        [_report("X", cohort | {79: 3.0, 92: 1.0}), _report("Y", cohort | {93: 1.0})], [79, 92, 93], []
    )
    _expect(elevated["historical_kappa_near_3"] == "supported", elevated["historical_kappa_near_3"])
    missing = fd.decisions([_report("X", cohort | {79: 1.0, 92: 1.0})], [79, 92, 93], [])
    _expect(missing["historical_kappa_near_3"] == "unresolved", "an unplaced focal qubit decided the reading")


def test_same_window_and_retest() -> None:
    cohort = {q: 1.0 + 0.1 * (q % 5) for q in range(10, 30)}
    out = fd.decisions([_report("X", cohort), _report("Y", cohort, calibration="C2")], [10], [])
    _expect(not out["same_window"], "two calibrations read as one")
    retest = out["retest"][0]["kappa_1"]
    _expect(retest["n"] == 20 and abs(retest["pearson_r"] - 1) < 1e-12, f"retest {retest}")
