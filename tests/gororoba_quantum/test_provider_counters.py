"""Contracts of provider_counters: population nesting, censoring, cap and billing separation, exposure scenarios.

The retained-evidence replays of docs/evidence/provider-counter-audit/ run under the audit marker.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import provider_counters as pc
from provider_counters import Counter, CounterError, Population, Status

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/evidence/provider-counter-audit"
TELEPORTATION = ROOT / "results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00"


def observed(name: str, value: int, population: Population, scope: str = "iteration:0") -> Counter:
    return Counter(name, value, population, scope, Status.OBSERVED, "fixture")


def test_equal_acceptance_leaves_the_trial_population_unidentified() -> None:
    # Ten accepted samples of twenty detections fit twenty incident trials or two thousand: the acceptance is one
    # half either way, and no counter fixes the no-detection rate.
    first = pc.quandela_iteration({"nb_shots_used": 20}, 10, "iteration:0", max_shots=None, max_samples=None)
    second = pc.quandela_iteration({"nb_shots_used": 20}, 10, "iteration:0", max_shots=None, max_samples=None)
    if first.acceptance().value != 0.5 or second.acceptance().value != 0.5:
        raise AssertionError("accepted-per-detection must read one half")
    for latent in (20, 2000):
        trials = observed("source_triggers", latent, Population.SOURCE_TRIGGER)
        if pc.ratio(first.detection_events, trials, "detection").value != 20 / latent:
            raise AssertionError("an observed trial counter would separate the two cases")
    per_trial = pc.ratio(first.samples, first.source_triggers, "per trial")
    if per_trial.value is not None or per_trial.reason != "a counter is unavailable":
        raise AssertionError("a per-trial rate needs an observed trial counter")


def test_photon_filter_and_logical_postselection_nest() -> None:
    one_photon = pc.quandela_iteration({"nb_shots_used": 1500}, 1500, "iteration:0", max_shots=3000, max_samples=1500)
    if one_photon.acceptance().value != 1.0 or one_photon.detection_events.terminated_by != "max_samples":
        raise AssertionError("a one-photon filter keeps every detection event and ends at its sample budget")
    multiphoton = pc.quandela_iteration(
        {"nb_shots_used": 162604}, 5000, "iteration:0", max_shots=2000000, max_samples=5000, accepted=4000
    )
    logical = multiphoton.logical_acceptance()
    filtered = multiphoton.acceptance().value
    if logical is None or logical.value != 0.8 or filtered is None or abs(filtered - 5000 / 162604) > 1e-15:
        raise AssertionError("logical acceptance divides by samples, filter acceptance by detections")
    with pytest.raises(CounterError):
        pc.quandela_iteration({"nb_shots_used": 10}, 11, "iteration:0", max_shots=None, max_samples=None)
    with pytest.raises(CounterError):
        pc.ratio(multiphoton.detection_events, multiphoton.samples, "inverted")


def test_threshold_detection_shares_the_detection_population() -> None:
    # A threshold detector reports a click pattern, not a photon number: a two-click sample is a detection event
    # passing the filter at two clicks, and the population chain is the same as for number resolution.
    events = observed("clicks", 100, Population.DETECTION_EVENT)
    two_click = observed("two_click", 7, Population.PHOTON_FILTERED_SAMPLE)
    if pc.ratio(two_click, events, "two or more clicks").value != 0.07:
        raise AssertionError(two_click)


def test_shot_budget_termination_is_censored() -> None:
    entry = {"nb_shots_used": 1200000, "physical_perf": 0.0}
    counters = pc.quandela_iteration(entry, 0, "iteration:0", max_shots=1200000, max_samples=900)
    if counters.detection_events.terminated_by != "max_shots" or counters.acceptance().value != 0.0:
        raise AssertionError("an iteration that reports its whole max_shots ended by the shot budget")
    if counters.extra != {"physical_perf": 0.0}:
        raise AssertionError("provider performance fields pass through verbatim")


def test_reaching_both_caps_names_neither_as_the_stop() -> None:
    # Ascella signed-coherence jobs 04 to 07 request max_shots = max_samples = 32768 and return 32768 of each.
    counters = pc.quandela_iteration({"nb_shots_used": 32768}, 32768, "iteration:0", max_shots=32768, max_samples=32768)
    if counters.detection_events.terminated_by != "both":
        raise AssertionError(counters.detection_events)


def test_top_level_shots_of_an_iterated_job_is_a_cap() -> None:
    iterated = pc.quandela_top_level_shots({"shots": 16384}, iterated=True, job_max_shots=16384)
    if iterated.population is not Population.REQUESTED_CAP or iterated.status is not Status.REQUESTED:
        raise AssertionError(iterated)
    # Mesh job-14: one iteration, top-level shots 10000 against a job-level max_shots of 20000.
    if pc.quandela_top_level_shots({"shots": 10000}, iterated=True, job_max_shots=20000).available:
        raise AssertionError("a top-level value that differs from the request has no identified population")
    single = pc.quandela_top_level_shots({"shots": 10000}, iterated=False, job_max_shots=20000)
    if single.population is not Population.DETECTION_EVENT:
        raise AssertionError(single)
    iterations = [observed("nb_shots_used", 8192, Population.DETECTION_EVENT, f"iteration:{k}") for k in range(8)]
    job = pc.total(iterations, "nb_shots_used", "job")
    if job.value != 65536 or job.status is not Status.OBSERVED:
        raise AssertionError(job)
    with pytest.raises(CounterError):
        pc.total([*iterations, iterated], "mixed", "job")
    with pytest.raises(CounterError):
        pc.total([iterations[0], iterations[0]], "repeated", "job")


def test_caps_and_billing_never_divide_a_population() -> None:
    samples = observed("samples", 10, Population.PHOTON_FILTERED_SAMPLE)
    cap = Counter("max_shots", 20, Population.REQUESTED_CAP, "iteration:0", Status.REQUESTED, "request")
    billed = Counter("billed_shots", 20.0, Population.BILLING, "iteration:0", Status.OBSERVED, "usage report")
    for denominator in (cap, billed):
        with pytest.raises(CounterError):
            pc.ratio(samples, denominator, "invalid")
    caps = pc.total(
        [cap, Counter("max_shots", 30, Population.REQUESTED_CAP, "iteration:1", Status.REQUESTED, "request")],
        "max_shots",
        "job",
    )
    if caps.value != 50 or caps.status is not Status.REQUESTED:
        raise AssertionError("cap arithmetic stays requested")
    with pytest.raises(CounterError):
        Counter("max_shots", 20, Population.REQUESTED_CAP, "job", Status.OBSERVED, "request")


@pytest.mark.parametrize(
    ("entry", "samples"),
    [({}, 0), ({"nb_shots_used": 0}, 0), ({"nb_shots_used": None}, 0)],
    ids=["missing", "empty", "null"],
)
def test_empty_failed_and_missing_results_stay_unavailable(entry: dict[str, int | None], samples: int) -> None:
    counters = pc.quandela_iteration(entry, samples, "iteration:0", max_shots=10, max_samples=5)
    acceptance = counters.acceptance()
    if acceptance.value is not None or acceptance.reason is None:
        raise AssertionError(acceptance)
    missing = pc.unavailable("nb_shots_used", Population.DETECTION_EVENT, "iteration:1", "absent")
    partial = pc.total([observed("nb_shots_used", 5, Population.DETECTION_EVENT), missing], "nb_shots_used", "job")
    if partial.available:
        raise AssertionError("a total over a missing iteration is unavailable")


def test_modeled_quantities_carry_assumptions_and_robustness_needs_every_scenario() -> None:
    with pytest.raises(CounterError):
        Counter("exposure_s", 0.2, Population.TIME_SECONDS, "job", Status.MODELED, "model")
    scenarios = pc.exposure_seconds(10000, 0.0074, 4.94, 13, "job")
    if set(scenarios) != {"none", "physical_perf_model", "job_duration"}:
        raise AssertionError(scenarios)
    seconds = scenarios["physical_perf_model"].value
    if seconds is None or abs(seconds - 10000 / (0.0074 * 4.94e6)) > 1e-12 or not scenarios["job_duration"].assumptions:
        raise AssertionError(scenarios)
    if pc.exposure_seconds(10, None, 4.94, None, "job")["physical_perf_model"].available:
        raise AssertionError("a missing physical_perf leaves the timing model unavailable")
    if not pc.robust([True, True, True]) or pc.robust([True, False, True]) or pc.robust([True, None]):
        raise AssertionError("robust requires every scenario available and agreeing")


def test_state_dependent_detection_changes_observed_input_proportions() -> None:
    # Two inputs launched equally often with detection probabilities 0.1 and 0.4 return samples in proportion
    # 1 : 4; the sample counts alone cannot restore the equal launch profile.
    samples = {
        "a": observed("samples", 100, Population.PHOTON_FILTERED_SAMPLE, "input:a"),
        "b": observed("samples", 400, Population.PHOTON_FILTERED_SAMPLE, "input:b"),
    }
    triggers = {
        label: pc.unavailable("source_triggers", Population.SOURCE_TRIGGER, f"input:{label}", "absent")
        for label in samples
    }
    if any(pc.ratio(samples[k], triggers[k], "per trial").value is not None for k in samples):
        raise AssertionError("per-input trial rates need trial counters")
    share = pc.total(list(samples.values()), "samples", "inputs")
    if share.value != 500 or samples["a"].value != 100:
        raise AssertionError("the observed input share reflects detection, not launch")


def test_retained_teleportation_iteration_reads_as_censored_detection_events() -> None:
    outer = json.loads((TELEPORTATION / "raw/result.json").read_text(encoding="utf-8"))
    entries = json.loads(outer["results"])["results_list"]
    counters = [
        pc.quandela_iteration(entry, 0, f"iteration:{k}", max_shots=outer["shots"], max_samples=900)
        for k, entry in enumerate(entries)
    ]
    if [c.detection_events.terminated_by for c in counters] != ["max_shots"] * 6:
        raise AssertionError("every rehearsal iteration ended by its shot budget")
    job = pc.total([c.detection_events for c in counters], "nb_shots_used", "job")
    if (
        job.value != 7200000
        or pc.quandela_top_level_shots(outer, iterated=True, job_max_shots=1200000).value != 1200000
    ):
        raise AssertionError("the job total sums iterations; the top-level shots is one iteration's cap")


REPLAYS = ("quandela_counter_table.py", "gate_model_counter_census.py", "exposure_sensitivity.py")


@pytest.mark.audit
@pytest.mark.parametrize("script", REPLAYS)
def test_audit_replays_reproduce_their_retained_output_without_touching_inputs(script: str) -> None:
    # Every file the replays read lies under results/ or docs/evidence/; git status over both trees, untracked
    # files included, proves the replay changed and added nothing there.
    status = ["git", "status", "--porcelain", "--untracked-files=all", "--", "results", "docs/evidence"]
    before = subprocess.run(status, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    env = {**os.environ, "GLIBC_TUNABLES": "glibc.rtld.optional_static_tls=4096"}
    subprocess.run([sys.executable, "-B", str(AUDIT / script), "--check"], cwd=ROOT, env=env, check=True)
    after = subprocess.run(status, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    if before != after:
        raise AssertionError(f"a replay changed retained evidence: {after}")


RUNS = ROOT / "results/quandela/runs"


def view(run: str) -> pc.QuandelaRecord:
    import qd_platform

    directory = RUNS / run
    results = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    budgets = qd_platform.iteration_budgets(json.loads((directory / "cases.json").read_text(encoding="utf-8")))
    return pc.quandela_record(results, budgets)


def test_record_view_of_an_iterated_mesh_job_types_every_counter() -> None:
    record = view("2026-10-18T030133Z-qpu_belenos-belenos_mesh-job-03")
    if (
        not record.iterated
        or record.top_level.population is not Population.REQUESTED_CAP
        or record.top_level.value != 3000
    ):
        raise AssertionError(record.top_level)
    if record.detection_events.value != 24000 or len(record.iterations) != 16:
        raise AssertionError(record.detection_events)
    first = record.iterations[0]
    if first is None or first.acceptance().value != 1.0 or first.detection_events.terminated_by != "max_samples":
        raise AssertionError(first)


def test_record_view_of_a_single_job_reads_its_top_level_shots_as_detections() -> None:
    record = view("2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04")
    (only,) = record.iterations
    if record.iterated or record.top_level.population is not Population.DETECTION_EVENT or only is None:
        raise AssertionError(record)
    if only.detection_events.value != 10000 or only.samples.value != 10000:
        raise AssertionError(only.record())


@pytest.mark.parametrize(
    ("run", "expected"),
    [
        ("2026-10-18T190504Z-qpu_belenos-belenos_mesh-job-14", "unavailable top-level shots"),
        ("2026-10-26T204432Z-qpu_ascella-ascella_signed_coherence-job-04", "both"),
        ("2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00", "max_shots"),
    ],
)
def test_record_view_of_the_retained_edge_cases(run: str, expected: str) -> None:
    record = view(run)
    if expected == "unavailable top-level shots":
        if record.top_level.available:
            raise AssertionError("mesh job-14's top-level shots differs from its request")
        return
    stops = {i.detection_events.terminated_by for i in record.iterations if i is not None}
    if stops != {expected}:
        raise AssertionError(stops)


@pytest.mark.parametrize("run", ["ascella-static-input-readiness", "ascella-hypercomplex-order-pilot"])
def test_record_view_leaves_an_uncounted_answer_unavailable(run: str) -> None:
    record = view(run)
    uncounted = any(i is not None for i in record.iterations) or record.detection_events.available
    if not record.partial or uncounted or record.top_level.available:
        raise AssertionError(record.record())


def test_record_view_keeps_a_counted_partial_answer_with_no_samples() -> None:
    # qd_platform.result_summary parses ':PCVL:BSCount:{}' of a cancelled single job into this summary.
    results = {"shots": 100, "shots_used": 100, "partial": True, "counts": {}, "samples": 0, "result_fields": {}}
    (only,) = pc.quandela_record(results, [(1000, 2000)]).iterations
    if only is None or only.detection_events.value != 100 or only.samples.value != 0:
        raise AssertionError("an empty counted answer observes its detections and zero samples")
    if only.acceptance().value != 0.0:
        raise AssertionError(only.acceptance())
    uncounted = {k: v for k, v in results.items() if k != "shots_used"}
    if pc.quandela_record(uncounted, [(1000, 2000)]).iterations != (None,):
        raise AssertionError("an answer without shots_used and without counts stays uncounted")


def test_record_view_reads_an_absent_result_as_unavailable() -> None:
    # qd_platform.collect writes result_absent, and no answer fields, when an error job's result route answers 404.
    results = {"status": {"status": "error", "shots": 0}, "result_absent": "GET result: HTTP 404"}
    record = pc.quandela_record(results, [(1000, 2000)])
    if record.iterations or record.top_level.available or record.detection_events.available or not record.partial:
        raise AssertionError(record.record())


@pytest.mark.audit
def test_record_view_agrees_with_the_counter_table_on_every_retained_run() -> None:
    import re

    table = json.loads((AUDIT / "quandela_counter_table.json").read_text(encoding="utf-8"))
    for row in table["runs"]:
        directory = RUNS / row["run"]
        if not (directory / "results.json").is_file() or not (directory / "cases.json").is_file():
            continue
        record = view(row["run"])
        body = (directory / "job-body.json").read_text(encoding="utf-8")
        caps = {int(v) for v in re.findall(r'max_shots\\?"?\s*[:=]\s*(\d+)', body)}
        if record.iterated and record.top_level.available and record.top_level.value not in caps:
            raise AssertionError(f"{row['run']}: the top-level cap is not the job body's max_shots")
        counted = [i for i in record.iterations if i is not None]
        reported = [i["nb_shots_used"] for i in row["iterations"]]
        if record.iterated and not record.partial and [i.detection_events.value for i in counted] != reported:
            raise AssertionError(f"{row['run']}: detection events differ from the raw nb_shots_used")
