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


REGION = [73, 79, 92, 93, 94, 95]


def test_historical_reading_is_a_region_rank_test() -> None:
    cohort = {q: 1.0 + 0.01 * (q % 37) for q in range(10, 50)}
    high = fd.decisions([_report("X", cohort | {q: 3.0 + 0.01 * q for q in REGION})], [79, 92, 93], [], REGION)
    _expect(high["historical_kappa_near_3"]["verdict"] == "supported", str(high["historical_kappa_near_3"]))
    low = fd.decisions([_report("X", cohort | {q: 0.9 + 0.001 * q for q in REGION})], [79, 92, 93], [], REGION)
    _expect(low["historical_kappa_near_3"]["verdict"] == "weakened", str(low["historical_kappa_near_3"]))
    one = fd.decisions(
        [_report("X", cohort | {q: 0.9 + 0.001 * q for q in REGION} | {93: 3.0})], [79, 92, 93], [], REGION
    )
    _expect(one["historical_kappa_near_3"]["verdict"] != "supported", "one outlier qubit decided the region")
    split = [_report("X", cohort | {73: 0.9, 79: 0.91, 92: 0.92}), _report("Y", {93: 0.93, 94: 0.94, 95: 0.95})]
    _expect(fd.decisions(split, [], [], REGION)["historical_kappa_near_3"]["verdict"] == "weakened", "pooling failed")
    missing = fd.decisions([_report("X", cohort | {79: 1.0, 92: 1.0})], [79, 92, 93], [], REGION)
    _expect(missing["historical_kappa_near_3"]["verdict"] == "unresolved", "an unplaced region qubit decided")


def test_same_window_and_retest() -> None:
    cohort = {q: 1.0 + 0.1 * (q % 5) for q in range(10, 30)}
    out = fd.decisions([_report("X", cohort), _report("Y", cohort, calibration="C2")], [10], [], [10])
    _expect(not out["same_window"], "two calibrations read as one")
    retest = out["retest"][0]["kappa_1"]
    _expect(retest["n"] == 20 and abs(retest["pearson_r"] - 1) < 1e-12, f"retest {retest}")


def test_calibration_split_withholds_the_pooled_reading() -> None:
    cohort = {q: 1.0 + 0.01 * (q % 37) for q in range(10, 50)}
    region = {q: 3.0 + 0.01 * q for q in REGION}
    split = fd.decisions(
        [_report("R", cohort | region), _report("X", cohort, calibration="C2")], [79, 92, 93], [], REGION
    )
    reading = split["historical_kappa_near_3"]
    _expect(reading["verdict"] == "split", str(reading))
    _expect(reading["per_run"]["R"]["verdict"] == "supported", str(reading))
    _expect(reading["per_run"]["X"]["verdict"] == "unresolved", str(reading))
