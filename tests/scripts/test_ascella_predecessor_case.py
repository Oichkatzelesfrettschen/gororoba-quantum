"""The Ascella predecessor case is one eight-iteration job of retained seed-0 settings."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import ascella_predecessor_case as case
import pytest
import qd_platform as qd

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "results/quandela/cases/ascella_predecessor/job-00"
SOURCE = ROOT / "results/quandela/cases/ascella_signed_coherence/job-00"
JOB00_RUN = ROOT / "results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00"
JOB02_RUN = ROOT / "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02"


def test_contrast_coefficients_expose_even_and_odd_drift_directions() -> None:
    positions = (-3, -1, 1, 3)
    common = tuple(Fraction(value, 2) for value in (1, -1, -1, 1))
    reversal = tuple(Fraction(value, 2) for value in (-1, 1, -1, 1))
    registered = manifest()["preregistered"]
    if (
        tuple(map(Fraction, registered["common_coefficients"])) != common
        or tuple(map(Fraction, registered["reversal_coefficients"])) != reversal
    ):
        raise AssertionError("the coefficient analysis must match the frozen acquisition case")
    for weights, expected in ((common, (0, 0, 8, 0, 80)), (reversal, (0, 2, 0, 26, 0))):
        moments = tuple(
            sum(weight * position**degree for weight, position in zip(weights, positions, strict=True))
            for degree in range(5)
        )
        if moments != expected:
            raise AssertionError("the contrast must expose its exact polynomial drift sensitivity")
    if sum(weight for weight, assigned in zip(common, (True, False, False, True), strict=True) if assigned) != 1:
        raise AssertionError("the common contrast must have unit additive-condition gain")


def test_fixed_allocation_has_explicit_sufficient_power_regions() -> None:
    """The union event bounds decision power as well as interval precision."""
    decision_factor = 12 * math.log(2) + math.log(8 / 0.05)
    power_factor = 12 * math.log(2) + math.log(8 / 0.20)
    radius_sum = 2 * (math.sqrt(decision_factor) + math.sqrt(power_factor)) / math.sqrt(2 * 32768)
    if not math.isclose(radius_sum, 0.0556616975517971, abs_tol=1e-15):
        raise AssertionError("decision and power deviations both enter the sufficient region")
    for population, expected in ((0.15, 40610), (0.16, 28201), (0.0462, 35076), (0.0654, 84803)):
        required = 2 * (math.sqrt(decision_factor) + math.sqrt(power_factor)) ** 2 / (population - 0.1) ** 2
        if math.floor(required) + 1 != expected:
            raise AssertionError("the sensitivity table must size decision power rather than radius alone")
    if not math.isclose(2 * case.subset_radius(8, 32768), 0.028590910871208422, abs_tol=1e-15):
        raise AssertionError("the power calculation must use the frozen case's simultaneous radius")


def test_eight_target_successor_still_accepts_a_cubic_drift_counterexample() -> None:
    positions = (-7, -5, -3, -1, 1, 3, 5, 7)
    weights = tuple(Fraction(value, 4) for value in (1, -1, -1, 1, -1, 1, 1, -1))
    moments = tuple(
        sum(weight * position**degree for weight, position in zip(weights, positions, strict=True))
        for degree in range(4)
    )
    if moments != (0, 0, 0, -96):
        raise AssertionError("the successor removes quadratic index drift while retaining cubic sensitivity")
    counts = (263, 10509, 15115, 16337, 16431, 17653, 22259, 32505)
    if counts != tuple(16384 + 47 * position**3 for position in positions):
        raise AssertionError("the falsifier must contain pure cubic drift")
    contrast = sum(weight * Fraction(count, 32768) for weight, count in zip(weights, counts, strict=True))
    if abs(contrast) != Fraction(141, 1024) or float(abs(contrast)) - 2 * case.subset_radius(16, 32768) <= 0.1:
        raise AssertionError("the signed successor can clear the margin without a predecessor effect")


SCHEDULE = (
    ("A", "theta2-x-arm1", "predecessor", 0),
    ("A", "theta2-x-arm0", "target", 1),
    ("A", "theta0-x-arm0", "predecessor", 0),
    ("A", "theta2-x-arm0", "target", 1),
    ("B", "theta0-x-arm0", "predecessor", 0),
    ("B", "theta2-x-arm0", "target", 1),
    ("B", "theta2-x-arm1", "predecessor", 0),
    ("B", "theta2-x-arm0", "target", 1),
)


def manifest() -> dict[str, Any]:
    return json.loads((CASE / "cases.json").read_text(encoding="utf-8"))


def test_check_reproduces_the_retained_bytes() -> None:
    rebuilt = case.check()
    if rebuilt["family"] != "ascella_predecessor" or rebuilt["platforms"] != ["qpu:ascella"]:
        raise AssertionError(rebuilt["platforms"])
    if rebuilt["command"] != "sample_count" or rebuilt["mitigations"] != [] or rebuilt["iterations"] != 8:
        raise AssertionError(rebuilt["iterations"])


def test_schedule_uses_job00_columns_on_odd_target_slots() -> None:
    settings = manifest()["settings"]
    source = {row["name"]: row for row in json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))["settings"]}
    actual = [(row["order"], row["source_name"], row["role"], row["slot"]) for row in settings]
    if actual != list(SCHEDULE) or [row["observation_index"] for row in settings] != list(range(8)):
        raise AssertionError(actual)
    if (CASE / "circuit.json").read_bytes() != (SOURCE / "circuit.json").read_bytes():
        raise AssertionError("circuit.json is not the job-00 template bytes")
    for row in settings:
        origin = source[row["source_name"]]
        if row["source_observation_index"] != origin["observation_index"]:
            raise AssertionError(row["name"])
        for key in ("circuit_params", "column", "operator", "compilation_seed"):
            if row[key] != origin[key]:
                raise AssertionError(f"{row['name']} {key}")
        if "mutation" in row["source_name"] or row["role"] not in {"predecessor", "target"}:
            raise AssertionError(row["name"])


def test_requested_separation_radius_and_credit_hold() -> None:
    record = manifest()
    source = {row["name"]: row for row in json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))["settings"]}
    laws = {
        name: case.probabilities(source[name]["column"]) for name in ("theta2-x-arm0", "theta2-x-arm1", "theta0-x-arm0")
    }
    pairs = (
        ("theta2-x-arm0", "theta2-x-arm1"),
        ("theta2-x-arm0", "theta0-x-arm0"),
        ("theta2-x-arm1", "theta0-x-arm0"),
    )
    for left, right in pairs:
        distance = case.total_variation(laws[left], laws[right])
        if distance < 0.5:
            raise AssertionError(f"{left} {right} {distance}")
    epsilon = case.subset_radius(8, 32768)
    registered = record["preregistered"]
    if registered["two_law_radius"] != 2.0 * epsilon or not registered["two_law_radius"] < 0.1:
        raise AssertionError(registered["two_law_radius"])
    if record["max_samples"] != 262144 or record["max_shots"] != 262144:
        raise AssertionError((record["max_samples"], record["max_shots"]))
    if record["max_credits"] != case.charge(32768) or registered["expected_credits"] != case.charge(32768):
        raise AssertionError(record["max_credits"])
    if registered["contrast_pairs"] != [[1, 3], [7, 5]] or registered["target_only"] != "absent":
        raise AssertionError(registered["contrast_pairs"])
    if registered["auto_retry"] is not False:
        raise AssertionError(registered["auto_retry"])


def test_frozen_circuits_match_the_retained_blobs() -> None:
    identity = manifest()["preregistered"]["compilation_identity"]
    source_cases = json.loads((JOB00_RUN / "cases.json").read_text(encoding="utf-8"))
    source_results = json.loads((JOB00_RUN / "results.json").read_text(encoding="utf-8"))
    index = next(i for i, row in enumerate(source_cases["settings"]) if row["name"] == "theta2-x-arm0")
    target = case.sha256_text(source_results["iterations"][index]["result_fields"]["computed_circuit"])
    if identity["target"]["computed_circuit_sha256"] != target:
        raise AssertionError(target)
    anchors = json.loads((JOB02_RUN / "cases.json").read_text(encoding="utf-8"))
    anchor_results = json.loads((JOB02_RUN / "results.json").read_text(encoding="utf-8"))
    hashed = [
        case.sha256_text(row["result_fields"]["computed_circuit"])
        for setting, row in zip(anchors["settings"], anchor_results["iterations"], strict=True)
        if setting["compilation_seed"] == source_cases["settings"][index]["compilation_seed"]
    ]
    if hashed != [target] * 8:
        raise AssertionError(hashed[:1])


@pytest.mark.parametrize("processor_status", ["available", "running"])
def test_running_platform_admission_preserves_queue_and_status_gates(
    monkeypatch: pytest.MonkeyPatch, processor_status: str
) -> None:
    record = manifest()
    if record["preregistered"]["admitted_platform_statuses"] != ["available", "running"]:
        raise AssertionError("the written case must explicitly admit queueing")
    row = {"status": "running", "max_duration": 300, "price_per_shot": 1e-6, "type": "qpu"}
    processor = {"status": processor_status, "perfs": {}}
    counters = {"num_concurrent_jobs": 0, "num_jobs_in_queue": 0}
    monkeypatch.setattr(qd, "explorer_row", lambda platform: row)
    monkeypatch.setattr(qd, "get", lambda route: processor)
    monkeypatch.setattr(qd, "availability", lambda: counters)
    monkeypatch.setattr(qd, "hom_warning", lambda *args: None)
    monkeypatch.setattr(
        qd,
        "payload",
        lambda *args: {"estimated_shots": 262144, "body": {}, "versions": {}, "payload_version_basis": "test"},
    )

    def planned() -> dict[str, Any]:
        return qd.plan(CASE, "qpu:ascella", 1.032768, 40, 1, ("running",))

    admitted = planned()
    if admitted["admitted_statuses"] != ["available", "running"]:
        raise AssertionError(admitted)
    with pytest.raises(qd.PlatformError, match="is running"):
        qd.plan(CASE, "qpu:ascella", 1.032768, 40, 1)
    for field in counters:
        counters[field] = 1
        with pytest.raises(qd.PlatformError, match="running or queued"):
            planned()
        counters[field] = 0
    for status in ("calibration", "maintenance"):
        processor["status"] = status
        with pytest.raises(qd.PlatformError, match="processor is"):
            planned()
    processor["status"] = processor_status
    row["status"] = "maintenance"
    with pytest.raises(qd.PlatformError, match="is maintenance"):
        planned()
