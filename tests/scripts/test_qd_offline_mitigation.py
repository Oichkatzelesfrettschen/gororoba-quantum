"""Bounded fixtures for the offline application of Perceval's error mitigations to retained Belenos counts."""

from __future__ import annotations

import json
from pathlib import Path

import perceval as pcvl
import pytest
import qd_offline_mitigation as mit

ROOT = Path(__file__).resolve().parents[2]
RAW_RUN = ROOT / "results/quandela/runs/2026-10-21T162332Z-qpu_belenos-bdsc_qualification-tc-none-e1"
JOB16 = ROOT / "results/quandela/runs/2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16"


def need(run: Path) -> None:
    if not (run / "raw/result.json").exists():
        pytest.skip(f"{run.name} is not checked out")


def test_mitigation_state_reads_the_manifest_field() -> None:
    if mit.mitigation_state({"mitigations": []}) != "none" or mit.mitigation_state({"job": "x"}) != "server_default":
        raise AssertionError("mitigation_state")
    if mit.mitigation_state({"mitigations": ["DetectorBalancing"]}) != "explicit":
        raise AssertionError("an explicit list is neither none nor the server default")


def test_counts_distribution_normalizes_the_retained_count_text() -> None:
    dist = mit.counts_distribution("|1,0>=3\n|0,1>=1\n")
    if abs(dist[pcvl.BasicState([1, 0])] - 0.75) > 1e-12 or abs(sum(dist.values()) - 1.0) > 1e-12:
        raise AssertionError(dist)


def test_balancing_recovers_the_lossless_distribution_from_lossy_number_resolving_detectors() -> None:
    processor = pcvl.Processor("SLOS", pcvl.BS())
    processor.with_input(pcvl.BasicState([1, 1]))
    ideal = processor.probs()["results"]
    lossy = [pcvl.Detector.pnr(), pcvl.Detector.pnr()]
    for detector in lossy:
        detector.efficiency = 0.6
    measured = pcvl.Processor("SLOS", pcvl.BS())
    for mode, detector in enumerate(lossy):
        measured.add(mode, detector)
    measured.with_input(pcvl.BasicState([1, 1]))
    raw = measured.probs()["results"]
    balanced = mit.balance_detectors(raw, 2, lossy)
    distance = 0.5 * sum(abs(balanced.get(state, 0.0) - ideal.get(state, 0.0)) for state in set(balanced) | set(ideal))
    raw_distance = 0.5 * sum(abs(raw.get(state, 0.0) - ideal.get(state, 0.0)) for state in set(raw) | set(ideal))
    if distance > 1e-9 or raw_distance < 0.3:
        raise AssertionError((distance, raw_distance))


def test_photon_recycling_reports_a_one_photon_distribution_as_not_applicable() -> None:
    dist = mit.counts_distribution("|1,0>=3\n|0,1>=1\n")
    result = mit.recycle(dist, 1)
    if result["status"] != "not_applicable" or "ideal photon count" not in result["reason"]:
        raise AssertionError(result)


def test_distinguishable_photon_mitigation_needs_sub_computations_that_grow_with_order() -> None:
    low = mit.dpm_overhead([1, 1, 1, 0, 0, 0], 1)
    high = mit.dpm_overhead([1, 1, 1, 0, 0, 0], 2)
    if not 1 <= low <= high:
        raise AssertionError((low, high))


def test_a_seeded_conversion_to_counts_reproduces_and_an_unseeded_one_does_not() -> None:
    dist = mit.counts_distribution("|1,0>=300\n|0,1>=100\n|1,1>=50\n")
    first = mit.seeded_counts(dist, 1000, 12345)
    second = mit.seeded_counts(dist, 1000, 12345)
    other = mit.seeded_counts(dist, 1000, 54321)
    if first != second or first == other:
        raise AssertionError((first, second, other))


def test_a_run_with_the_server_default_mitigation_is_refused_without_the_opt_in() -> None:
    need(JOB16)
    with pytest.raises(mit.MitigationError, match="server"):
        mit.read_run(JOB16, allow_server_default=False)


def test_an_unmitigated_run_reads_with_balancing_applied_and_the_rest_classified() -> None:
    need(RAW_RUN)
    record = mit.read_run(RAW_RUN, allow_server_default=False, only=(0,))
    entry = record["entries"][0]
    if record["state"] != "none" or entry["detector_balancing"]["status"] != "applied":
        raise AssertionError(entry)
    if abs(entry["detector_balancing"]["mass_after"] - 1.0) > 1e-9:
        raise AssertionError(entry["detector_balancing"])
    if (
        entry["photon_recycling"]["status"] != "not_applicable"
        or entry["distinguishable_photon"]["status"] != "needs_server"
    ):
        raise AssertionError(entry)
    json.dumps(record)
