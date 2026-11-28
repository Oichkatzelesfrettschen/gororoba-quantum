"""Bounded fixtures for the off-cone mechanisms analysis: mechanism signatures, void rules and refusals."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import belenos_offcone_mechanisms_analyze as ana
import pytest

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quandela/cases/belenos_offcone_mechanisms"
LEVELS = (1500, 10000, 60000)


def make_entry(source: int, level: int, presences: int, perf: float = 0.01) -> dict[str, Any]:
    return {
        "name": f"s{source}-n{level}",
        "source": source,
        "level": level,
        "samples": level,
        "mesh_sha256": "29dc6ef8" if source == 20 else "500c4fab",
        "cone_size": 16,
        "ideal_share_detectors": 1.0 if source == 20 else 0.5,
        "acquisition_s": level / perf / 1e6,
        "presence_modes": list(range(presences)),
        "presences": presences,
        "breaks_1_to_31": 0,
        "mode_5_presence": 0,
        "mode_5_clicks": 0,
        "in_block_cone": 0.99,
        "tvd_cone_from_ideal": 0.09,
        "off_cone_clicks": {},
        "primary_clicks": 0,
        "presences_by_floor": {},
        "void": [],
    }


def make_job(name: str, rule: Any, perf: Any = lambda level: 0.01) -> dict[str, Any]:
    entries = [
        make_entry(source, level, rule(source, level, rep), perf(level))
        for rep in range(5)
        for level in LEVELS
        for source in (20, 22)
    ]
    return {"job": name, "entries": entries}


def jobs_of(rule: Any, rule_01: Any = None, perf: Any = lambda level: 0.01) -> dict[str, dict[str, Any]]:
    return {
        "job-00": make_job("job-00", rule, perf),
        "job-01": make_job("job-01", rule_01 or rule, perf),
        "job-02": make_job("job-02", rule, perf),
    }


def read(jobs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return ana.verdicts(jobs, ana.contrasts(jobs))


def test_the_exact_test_matches_closed_forms() -> None:
    if abs(ana.binomial_two_sided(0, 15, 0.5) - 2 * 0.5**15) > 1e-12:
        raise AssertionError("tail of the symmetric null")
    if (
        abs(ana.binomial_two_sided(5, 10, 0.5) - 1.0) > 1e-9
        or abs(ana.binomial_two_sided(2, 10, 0.5) - 0.109375) > 1e-9
    ):
        raise AssertionError("two-sided sum of masses not above the observed")
    if ana.binomial_two_sided(0, 0, 0.3) != 1.0:
        raise AssertionError("an empty count reads p = 1")


def test_balancing_signature_reads_balancing() -> None:
    # Packets in both default jobs at either source and level, none when the server processing is off.
    got = read(jobs_of(lambda s, n, r: 3, lambda s, n, r: 0))
    if got["case_reading"] != "balancing" or got["falsifier_layer"]["balancing"] != "survives":
        raise AssertionError(got)


def test_episodes_signature_reads_episodes() -> None:
    # Source 20 lights the detectors that read packets, source 22 does not, in every job.
    got = read(jobs_of(lambda s, n, r: 4 if s == 20 else 0))
    if got["case_reading"] != "episodes" or got["falsifier_layer"]["balancing"] != "falsified":
        raise AssertionError(got)


def test_window_samples_signature_reads_window_samples() -> None:
    # One rate per sample at both sources and every level (2 of 5 repeats read one presence at 1500 samples).
    got = read(
        jobs_of(
            lambda s, n, r: {1500: int(r < 2), 10000: 3, 60000: 18}[n],
            perf=lambda n: {1500: 0.001, 10000: 0.02, 60000: 0.06}[n],
        )
    )
    if got["case_reading"] != "window_samples" or got["falsifier_layer"]["window_time"] != "falsified":
        raise AssertionError(got)


def test_window_time_signature_reads_window_time() -> None:
    # Presences proportional to the acquisition time: the 1500 level (low physical_perf, long per sample) reads high.
    got = read(
        jobs_of(
            lambda s, n, r: {1500: 8, 10000: 10, 60000: 18}[n],
            perf=lambda n: {1500: 0.001, 10000: 0.01, 60000: 0.06}[n],
        )
    )
    if got["case_reading"] != "window_time" or got["falsifier_layer"]["window_samples"] != "falsified":
        raise AssertionError(got)


def test_a_rejected_drift_contrast_reads_no_attribution() -> None:
    jobs = jobs_of(lambda s, n, r: 4 if s == 20 else 0)
    for entry in jobs["job-02"]["entries"]:
        entry["presences"] = 0
    got = read(jobs)
    if got["case_reading"] != "no attribution" or not got["drift_rejected"]:
        raise AssertionError(got)


def row(**changes: Any) -> dict[str, Any]:
    base = {
        "name": "e",
        "samples": 1500,
        "mesh_sha256": "29dc6ef8" + "0" * 56,
        "cone_modes": list(range(8, 24)),
        "off_cone_by_mode": {"5": 40, "6": 33, "3": 31},
    }
    return base | changes


def test_presence_counts_other_modes_from_32_and_keeps_mode_5_apart() -> None:
    entry = ana.entry_of(
        row(), {"input_mode": 20, "max_samples": 1500}, "|0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0>", 0.1
    )
    if (entry["presences"], entry["mode_5_presence"], entry["breaks_1_to_31"], entry["void"]) != (1, 1, 1, []):
        raise AssertionError(entry)


@pytest.mark.parametrize(
    ("mode", "computed", "changes"),
    [
        (20, "|" + ",".join("2" if k == 20 else "0" for k in range(24)) + ">", {}),
        (20, "|" + ",".join("1" if k == 22 else "0" for k in range(24)) + ">", {}),
        (20, "|" + ",".join("1" if k == 20 else "0" for k in range(24)) + ">", {"samples": 1499}),
        (20, "|" + ",".join("1" if k == 20 else "0" for k in range(24)) + ">", {"mesh_sha256": "500c4fab" + "0" * 56}),
        (22, "|" + ",".join("1" if k == 22 else "0" for k in range(24)) + ">", {"cone_modes": list(range(5, 24))}),
    ],
)
def test_each_void_rule_marks_the_entry_void(mode: int, computed: str, changes: dict[str, Any]) -> None:
    entry = ana.entry_of(row(**changes), {"input_mode": mode, "max_samples": 1500}, computed, 0.1)
    if not entry["void"]:
        raise AssertionError(entry)


def test_a_trailing_entry_without_its_pair_is_dropped() -> None:
    if ana.complete_pairs([{}, {}, {}]) != [{}, {}] or ana.complete_pairs([{}, {}]) != [{}, {}]:
        raise AssertionError("pair completion")


def copy_run(tmp_path: Path, job: str = "job-00") -> Path:
    target = tmp_path / job
    shutil.copytree(CASES / job, target)
    return target


def test_a_retained_run_validates_and_reads_thirty_entries() -> None:
    got = ana.run_entries(CASES / "job-00")
    if len(got["entries"]) != 30 or got["couplers_checked"] != "unread":
        raise AssertionError(got["couplers_checked"])


def test_a_run_with_live_differing_couplers_is_refused(tmp_path: Path) -> None:
    run = copy_run(tmp_path)
    path = run / "results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["couplers_checked"] = "live-differ"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ana.AnalysisError, match="couplers_checked"):
        ana.run_entries(run)


def test_a_run_with_altered_raw_bytes_is_refused(tmp_path: Path) -> None:
    run = copy_run(tmp_path)
    path = run / "raw/result.json"
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(ana.AnalysisError, match="validate_run"):
        ana.run_entries(run)


def test_the_decision_rule_is_the_builders_rejection_region() -> None:
    for n, share in ((15, 0.5), (12, 0.0244), (30, 1 / 3)):
        region = set(ana.case_lib.rejection_region(n, share))
        got = {k for k in range(n + 1) if ana.binomial_two_sided(k, n, share) < ana.ALPHA}
        if region != got:
            raise AssertionError((n, share, region ^ got))


def test_the_time_law_share_weights_the_low_level_by_the_physical_perf_ratio() -> None:
    if abs(ana.TIME_LAW_RATIO - 17.6) > 0.05 or abs(ana.time_law_share(1500, 60000, 17.6) - 26400 / 86400) > 1e-12:
        raise AssertionError(ana.TIME_LAW_RATIO)


def test_the_episodes_bound_follows_the_returned_mesh_shares() -> None:
    entries = [make_entry(20, 1500, 0), make_entry(22, 1500, 0)]
    if abs(ana.episodes_share(entries) - 0.5 / 1.5) > 1e-12:
        raise AssertionError(ana.episodes_share(entries))


def test_a_source_split_beyond_the_episodes_bound_is_flagged() -> None:
    got = read(jobs_of(lambda s, n, r: 4 if s == 20 else 0))
    if not got["episodes_exceeded_by_source_split"]:
        raise AssertionError(got)
    even = read(jobs_of(lambda s, n, r: 4 if s == 20 else 2))
    if even["episodes_exceeded_by_source_split"]:
        raise AssertionError(even)


BASE = {"in_block_cone": {"min": 0.45}, "tvd_cone_from_ideal": {"max": 0.82}}


def collapse(jobs: dict[str, dict[str, Any]], in_block: float = 0.2, tvd: float = 0.87) -> None:
    for job in jobs.values():
        for entry in job["entries"]:
            entry["in_block_cone"], entry["tvd_cone_from_ideal"] = in_block, tvd


def test_the_baseline_is_the_job_16_envelope_on_mesh_29dc6ef8() -> None:
    base = ana.baseline()
    if (
        base["entries"] != 13
        or base["in_block_cone"]["min"] != 0.450353
        or base["tvd_cone_from_ideal"]["max"] != 0.819035
    ):
        raise AssertionError(base)
    if base["entries_at_in_block_cone_0_98_or_more"] != 11:
        raise AssertionError("job-16 holds 11 entries at 0.98 or more and two failing entries")


def test_a_healthy_routing_state_leaves_the_case_reading_to_the_contrasts() -> None:
    jobs = jobs_of(lambda s, level, rep: 0)
    got = ana.verdicts(jobs, ana.contrasts(jobs), BASE)
    if got["routing_collapsed_jobs"] or got["case_reading"] != "no attribution":
        raise AssertionError(got)


def test_a_collapsed_routing_state_withholds_every_mechanism_and_the_reading() -> None:
    # source 22 reads no presence and source 20 reads 3 per entry: ungated, the contrasts would name episodes
    jobs = jobs_of(lambda s, level, rep: 3 if s == 20 else 0, perf=lambda level: 0.01)
    if ana.verdicts(jobs, ana.contrasts(jobs))["case_reading"] != "episodes":
        raise AssertionError("the ungated reading is the one the gate must withhold")
    collapse(jobs)
    got = ana.verdicts(jobs, ana.contrasts(jobs), BASE)
    if got["case_reading"] != "routing collapsed, mechanisms unread" or set(got["falsifier_layer"].values()) != {
        "withheld"
    }:
        raise AssertionError(got)
    if got["routing_collapsed_jobs"] != ["job-00", "job-01", "job-02"]:
        raise AssertionError(got["routing_collapsed_jobs"])


def test_the_gate_reads_the_median_and_fails_closed_without_a_source_20_entry() -> None:
    jobs = jobs_of(lambda s, level, rep: 0)
    entries = [e for e in jobs["job-00"]["entries"] if e["source"] == 20]
    for entry in entries[:2]:
        entry["in_block_cone"], entry["tvd_cone_from_ideal"] = 0.1, 0.9  # a minority of failing entries
    if not ana.routing_gate(jobs["job-00"], BASE)["passes"]:
        raise AssertionError("two failing entries of fifteen leave the median inside the envelope")
    for entry in entries[:9]:
        entry["in_block_cone"] = 0.1
    if ana.routing_gate(jobs["job-00"], BASE)["passes"]:
        raise AssertionError("a median below the envelope fails")
    only_22 = {"job": "job-00", "entries": [e for e in jobs["job-00"]["entries"] if e["source"] == 22]}
    if ana.routing_gate(only_22, BASE)["passes"]:
        raise AssertionError("a job without a source-20 entry fails closed")


def test_the_click_contrast_reads_an_amplification_the_binary_count_saturates_on() -> None:
    def rule(source: int, level: int, rep: int) -> int:
        return 1 if source == 20 and level == 60000 else 0

    jobs = jobs_of(rule)
    for name, job in jobs.items():
        for entry in job["entries"]:
            if entry["source"] == 20 and entry["level"] == 60000:
                clicks = 40 if name == "job-01" else 60
                entry["off_cone_clicks"], entry["primary_clicks"] = {"6": clicks}, clicks
    got = ana.click_contrast(jobs)
    if got["default_over_mitigations_off_click_rate"] != 1.5:
        raise AssertionError(got["default_over_mitigations_off_click_rate"])
    (cell,) = got["saturated_cells"]
    if (cell["source"], cell["level"], cell["modes"], cell["entries"]) != (20, 60000, [6], 15):
        raise AssertionError(cell)
    if (
        cell["clicks"] != {"job-00": 300, "job-01": 200, "job-02": 300}
        or cell["default_over_mitigations_off_click_rate"] != 1.5
    ):
        raise AssertionError(cell)
    if not got["binary_indicator_saturated"] or not got["job_01_share_test"]["rejects"]:
        raise AssertionError(got)


def test_the_floor_sensitivity_recounts_presences_per_factor() -> None:
    jobs = jobs_of(lambda s, level, rep: 1)
    for job in jobs.values():
        for entry in job["entries"]:
            entry["presences_by_floor"] = {"0.5": 2, "1.0": 1, "2.0": 0}
    got = ana.floor_sensitivity(jobs)
    if [got[k]["presences"]["job-00"] for k in ("0.5", "1.0", "2.0")] != [60, 30, 0]:
        raise AssertionError(got)
    if got["2.0"]["mitigation"] is not None:
        raise AssertionError("a floor with no presence has no mitigation contrast")


def test_the_caveat_follows_the_recorded_coupler_states() -> None:
    def job(live: str, compiled: str) -> dict[str, Any]:
        return {"couplers_checked": live, "compiled_couplers_checked": compiled, "architecture_source": "carried"}

    both = ana.caveat({"a": job("unread", "match")})
    live_read = ana.caveat({"a": job("live-match", "unread")})
    if "match" not in both or "unread" not in both or both == live_read or "matched the retained" not in live_read:
        raise AssertionError((both, live_read))
