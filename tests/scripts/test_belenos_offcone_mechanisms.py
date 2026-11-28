"""Bounded fixtures for the Belenos off-cone mechanisms case: schedule balance, exact power and the written jobs."""

from __future__ import annotations

import functools
import json
import math

import belenos_offcone_mechanisms as boc
import pytest

import qd_records


@functools.cache
def documents() -> dict[str, bytes]:
    return boc.documents()


def manifest(job: str = "job-00") -> dict:
    return json.loads(documents()[f"{job}/cases.json"])


def test_every_level_gives_both_sources_the_same_samples_and_the_job_opens_at_1500() -> None:
    rows = boc.schedule()
    for level in boc.LEVELS:
        if boc.exposure(rows, level=level, source=20) != boc.exposure(rows, level=level, source=22):
            raise AssertionError(level)
    if rows[0]["max_samples"] != min(boc.LEVELS) or [r["input_mode"] for r in rows[:2]] != [20, 22]:
        raise AssertionError(rows[:2])
    if len(rows) != 2 * sum(boc.REPEATS) or len({r["name"] for r in rows}) != len(rows):
        raise AssertionError(len(rows))


def test_the_written_jobs_read_as_one_seeded_iterator_with_sources_and_budgets() -> None:
    for job in boc.JOBS:
        case = manifest(job)
        if qd_records.iteration_form(case) != "seeded":
            raise AssertionError(job)
        if case["max_samples"] != sum(s["max_samples"] for s in case["settings"]) or case["iterations"] != 30:
            raise AssertionError(job)
        if {s["compilation_seed"] for s in case["settings"]} != {20}:
            raise AssertionError("the compilation seed is the identifier of mesh 29dc6ef8")
        if case["expected_seconds"] > boc.DURATION_MARGIN * boc.MAX_DURATION:
            raise AssertionError(case["expected_seconds"])
    if (
        "mitigations" in manifest("job-00")
        or "mitigations" in manifest("job-02")
        or manifest("job-01")["mitigations"] != []
    ):
        raise AssertionError("only job-01 turns the server mitigations off")
    if json.loads(documents()["job-00/cases.json"])["settings"] != manifest("job-02")["settings"]:
        raise AssertionError("the default jobs repeat one schedule")
    if not 24 <= len(manifest()["settings"]) <= 30 or boc.worst_seconds(boc.schedule()) > boc.MAX_DURATION:
        raise AssertionError("the entry count leaves the duration bound")


def test_a_mixed_input_mode_list_is_refused() -> None:
    case = manifest()
    case["settings"][3] = {k: v for k, v in case["settings"][3].items() if k != "input_mode"}
    with pytest.raises(qd_records.RecordError):
        qd_records.iteration_form(case)
    case = manifest()
    case["settings"][3]["input_mode"] = True
    with pytest.raises(qd_records.RecordError):
        qd_records.iteration_form(case)


@pytest.mark.parametrize("job", boc.JOBS)
def test_the_offline_payload_sends_each_source_budget_and_policy(job: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    import perceval as pcvl
    import qd_platform
    from perceval.providers.quandela.rpc_handler import RPCHandler

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"][boc.PLATFORM]
    monkeypatch.setattr(RPCHandler, "fetch_platform_details", lambda self: processor)
    monkeypatch.setattr(qd_platform, "token", lambda: "offline-test-token")
    case = manifest(job)
    built = qd_platform.payload(root, case, json.loads(documents()[f"{job}/circuit.json"]), boc.PLATFORM)
    computation = pcvl.serialization.deserialize(built["body"]["payload"]["computation"])
    entries = computation.iterations
    if len(entries) != len(case["settings"]):
        raise AssertionError(len(entries))
    for entry, setting in zip(entries, case["settings"], strict=True):
        state = [int(x) for x in str(entry["input_state"]).strip("|>").split(",")]
        if state != [int(k == setting["input_mode"]) for k in range(24)]:
            raise AssertionError((setting["name"], state))
        if (entry["max_samples"], entry["max_shots"], entry["compilation_seed"]) != (
            setting["max_samples"],
            setting["max_shots"],
            setting["compilation_seed"],
        ):
            raise AssertionError(setting["name"])
    want: list[object] | None = [] if job == "job-01" else None
    if qd_platform.body_mitigations(built["body"]) != want:
        raise AssertionError(job)


def test_the_binomial_rejection_region_is_exact() -> None:
    # Eight fair trials reject at 0 and 8 only (p = 2 / 256 = 0.0078), not at 1 or 7 (p = 18 / 256 = 0.0703).
    if boc.rejection_region(8, 0.5) != (0, 8):
        raise AssertionError(boc.rejection_region(8, 0.5))
    if not math.isclose(sum(boc.binomial_pmf(12, k, 0.3) for k in range(13)), 1.0, rel_tol=1e-12):
        raise AssertionError("the binomial pmf does not sum to 1")


def test_power_keeps_its_size_and_rises_with_the_rate_ratio() -> None:
    table = boc.power_table(boc.schedule())
    for scenario, by_ratio in table["source_contrast"]["power_by_rate_ratio_source_20_over_22"].items():
        if by_ratio["1.0"] > boc.ALPHA or not by_ratio["1.5"] < by_ratio["2.0"] < by_ratio["3.0"]:
            raise AssertionError((scenario, by_ratio))
    fixed = table["source_contrast"]["power_by_rate_ratio_source_20_over_22"]["fixed_total"]
    scaled = table["source_contrast"]["power_by_rate_ratio_source_20_over_22"]["source_22_scaled"]
    if any(scaled[r] > fixed[r] for r in fixed if r != "1.0"):
        raise AssertionError("halving source 22 lowers the total and cannot add power")
    if table["drift_contrast"]["power_by_rate_ratio_job_02_over_job_00"]["1.0"] > boc.ALPHA:
        raise AssertionError(table["drift_contrast"])
    if table["level_contrast"]["size_of_sample_law_test"] > boc.ALPHA:
        raise AssertionError(table["level_contrast"])
    mitigation = table["mitigation_contrast"]["power_by_rate_ratio_of_job_01"]
    if mitigation["0.0"] < 0.99 or mitigation["1.0"] > boc.ALPHA:
        raise AssertionError(table["mitigation_contrast"])


def test_the_retained_case_files_equal_the_rebuild() -> None:
    boc.build(check_only=True)


def test_the_primary_rate_excludes_mode_5_and_the_total_is_not_inflated() -> None:
    if boc.PRESENCE_PER_SAMPLE != 49 / 452_000 or boc.MODE5_PER_SAMPLE != 31 / 452_000:
        raise AssertionError((boc.PRESENCE_PER_SAMPLE, boc.MODE5_PER_SAMPLE))
    table = boc.power_table(boc.schedule())
    total = sum(r["max_samples"] for r in boc.schedule())
    if table["expected_presences_per_job"] != round(49 / 452_000 * total, 2):
        raise AssertionError(table["expected_presences_per_job"])
    split = table["expected_presences_by_source_per_job"]
    if abs(sum(split.values()) - table["expected_presences_per_job"]) > 0.02:
        raise AssertionError(split)
    observable = manifest()["preregistered"]["observable"]
    if "other than mode 5" not in observable or "separate secondary readout" not in observable:
        raise AssertionError(observable)


def test_the_source_ratio_bound_follows_the_served_mesh_and_degeneracy_is_named() -> None:
    shares = boc.ideal_shares()
    if not (shares[20]["detectors_20_21"] > 0.999 and 0.59 < shares[22]["detectors_20_21"] < 0.60):
        raise AssertionError(shares)
    if not math.isclose(boc.source_ratio_bound(), 1 / shares[22]["detectors_20_21"], abs_tol=2e-3):
        raise AssertionError(boc.source_ratio_bound())
    prereg = manifest()["preregistered"]
    separation = prereg["source_separation"]
    if separation["max_rate_ratio_source_20_over_22"] != boc.source_ratio_bound():
        raise AssertionError(separation)
    if "source-independent photon-triggered episodes" not in separation["degenerate_with_window_samples"]:
        raise AssertionError(separation)
    if (
        str(boc.source_ratio_bound())
        not in prereg["power"]["source_contrast"]["power_by_rate_ratio_source_20_over_22"]["fixed_total"]
    ):
        raise AssertionError("the power table omits the attainable bound")


def test_the_mitigation_arm_is_unconditional_and_source_22_may_return_its_own_mesh() -> None:
    prereg = manifest()["preregistered"]
    if (
        "25 presences" in prereg["void"]
        or "rate not reproduced" in prereg["void"]
        or "gates a later one" not in prereg["jobs"]
    ):
        raise AssertionError(prereg["jobs"])
    if (
        "source-22 entry is void when its returned mesh" not in prereg["void"]
        or "whichever it is" not in prereg["void"]
    ):
        raise AssertionError(prereg["void"])
    if (
        "completed pairs" not in prereg["void"]
        or "creates no click on a zero-count mode" not in prereg["mechanisms"]["balancing"]
    ):
        raise AssertionError(prereg)
