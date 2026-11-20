"""The sim:belenos timing requests keep the retained b1 settings and apply the case's stop and decision rules."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import bdsc_diagnostic as diag
import bdsc_diagnostic_acquisition_case as acquisition
import bdsc_diagnostic_timing_case as timing
import pytest
import qd_platform

from rebound import rebound

TREE = timing.TREE


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def committed(name: str) -> dict[str, Any]:
    return json.loads((TREE / name / "cases.json").read_bytes())


def retained(job: str) -> dict[str, Any]:
    return json.loads((timing.SOURCE_TREE / job / "cases.json").read_bytes())


def without_sources(tree: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, content in tree.items():
        if isinstance(content, bytes):
            out[name] = content
            continue
        manifest = json.loads(content["cases.json"])
        manifest.pop("successor_sources")
        out[name] = {"cases.json": manifest, "circuit.json": content["circuit.json"]}
    return out


def test_the_committed_tree_equals_a_fresh_build_apart_from_the_source_digests() -> None:
    # The manifests bind the digests of timing.SOURCES; a change to one of those files calls for a rebuild before the
    # plan (the strict comparison is the check subcommand), so the pull-request test compares everything else.
    flat = {str(p.relative_to(TREE)) for p in TREE.rglob("*") if p.is_file()}
    require(flat == set(timing.files_of(timing.documents())), f"tree files differ from a fresh build: {sorted(flat)}")
    on_disk = {
        "case.json": (TREE / "case.json").read_bytes(),
        **{
            name: {file: (TREE / name / file).read_bytes() for file in ("cases.json", "circuit.json")}
            for name in timing.REQUESTS
        },
    }
    require(without_sources(on_disk) == without_sources(timing.documents()), "the tree differs from a fresh build")
    for name in timing.REQUESTS:
        require(sorted(committed(name)["successor_sources"]) == sorted(timing.SOURCES), f"{name}: bound sources")


@pytest.mark.parametrize("name", sorted(timing.REQUESTS))
def test_each_request_keeps_its_groups_byte_for_byte_in_the_retained_order(name: str) -> None:
    job, groups = timing.REQUESTS[name]
    source, manifest = retained(job), committed(name)
    kept = [s for s in source["settings"] if timing.group_of(s) in groups]
    require(manifest["settings"] == kept, f"{name}: settings differ from the retained {job} subset")
    require(len(kept) == 12 and {timing.group_of(s) for s in kept} == set(groups), f"{name}: {len(kept)} settings")
    budgets = (manifest["iterations"], manifest["max_samples"], manifest["max_shots"])
    require(budgets == (12, 480000, 960000), f"{name}: budgets {budgets}")
    kept_keys = ("diagnostic_case_sha256", "draw", "target_sha256", "mitigations", "max_duration", "circuit")
    require(manifest["platforms"] == source["platforms"], f"{name}: platforms")
    for key in kept_keys:
        require(manifest[key] == source[key], f"{name}: {key} differs from {job}")
    require(manifest["job"] == name and manifest["source_job"]["job"] == job, f"{name}: job names")
    record = timing.sha256_bytes((TREE / "case.json").read_bytes())
    require(manifest["timing_case_sha256"] == record, f"{name}: timing record digest")
    circuit = (TREE / name / "circuit.json").read_bytes()
    require(circuit == (timing.SOURCE_TREE / job / "circuit.json").read_bytes(), f"{name}: circuit differs from {job}")


def test_the_requests_omit_the_groups_the_case_names() -> None:
    names = {name: {timing.group_of(s) for s in committed(name)["settings"]} for name in timing.REQUESTS}
    require(names == {"p1": {"out-s0", "out-s1"}, "p2": {"rev-s0", "rev-s1"}}, f"groups {names}")
    require("out-s2-pi" not in {s["name"] for s in committed("p2")["settings"]}, "P2 carries out-s2-pi")


def test_the_retained_draw_stays_claimed_by_its_own_record_only() -> None:
    # The P manifests name the retained draw under the retained record's sha256, so the draw check of the retained
    # tree's rebuild finds no other case that draws from it.
    platform = timing.PLATFORM
    claims = rebound(
        diag.draw_claims,
        case_record=lambda: acquisition.case_record(platform),
        bdsc_cases=acquisition.cases_namespace(platform),
    )(committed("p1")["draw"])
    timing_claims = [path for path in claims if "bdsc_diagnostic_timing_sim_belenos" in path]
    require(not timing_claims, f"the retained draw is claimed by {timing_claims}")


@pytest.mark.parametrize(
    ("p1", "p2", "reading"),
    [
        ([150.0, 150.0, 170.0], [150.0, 150.0, 150.0], "service-variation"),
        ([150.0, 151.0, 152.0], [100.0, 101.0, 102.0], "request-cost"),
        ([150.0, 151.0, 152.0], [150.0, 151.0, 152.0], "doubled-above-fit"),
        ([140.0, 141.0, 142.0], [140.0, 141.0, 142.0], "doubled-within-fit"),
        ([150.0, 160.0, 155.0], [150.0, 151.0, 152.0], "inconclusive"),
        ([150.0, 151.0, 152.0], [140.0, 141.0, 142.0], "inconclusive"),
        # |m1 - m2| / mean is exactly 1/20 here, which binary64 rounds above 0.05; the rule reads "at most 5 %".
        ([150.0, 150.0, 151.0], [143.0, 143.0, 143.0], "doubled-within-fit"),
        # Exactly 2 x mean = 295 s sits within the fit, and a spread of exactly 10 % is not above it.
        ([147.5, 147.5, 147.5], [147.5, 147.5, 147.5], "doubled-within-fit"),
        ([140.0, 147.0, 154.0], [147.0, 147.0, 147.0], "inconclusive"),
    ],
)
def test_the_decision_rows_of_the_case(p1: list[float], p2: list[float], reading: str) -> None:
    decided = timing.decide({"p1": p1, "p2": p2})
    require(decided["reading"] == reading, f"{decided} reads {decided['reading']}, not {reading}")


def test_a_zero_duration_is_refused() -> None:
    with pytest.raises(timing.TimingError, match="not positive"):
        timing.decide({"p1": [0.0, 0.0, 0.0], "p2": [150.0, 150.0, 150.0]})


class Runs:
    """Synthetic submitted and collected runs of the committed requests under a scratch results tree."""

    def __init__(self, root: Path) -> None:
        self.root = root / "results"
        self.made: list[Path] = []

    def add(
        self, name: str, duration: float = 148.0, status: str = "completed", gap: int = 0, platform: str = "sim:belenos"
    ) -> Path:
        slot = len(self.made)
        run = self.root / "runs" / f"run-{slot}-{name}"
        run.mkdir(parents=True)
        (run / "cases.json").write_bytes((TREE / name / "cases.json").read_bytes())
        minute = 10 * slot - gap
        submitted = f"2026-12-01T10:{minute:02d}:00+00:00"
        collected = f"2026-12-01T10:{10 * slot + 5:02d}:00Z"
        (run / "submission.json").write_text(json.dumps({"platform": timing.PLATFORM, "submitted_utc": submitted}))
        (run / "job-body.json").write_text(json.dumps({"payload": {}}))
        results = {
            "status": {"status": status, "duration": duration},
            "collected_utc": collected,
            "data": {"platform_name": platform},
        }
        (run / "results.json").write_text(json.dumps(results))
        self.made.append(run)
        return run


@pytest.fixture
def runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Runs:
    monkeypatch.setattr(qd_platform, "run_facts", lambda run: {"charge": 1.0})
    monkeypatch.setattr(qd_platform, "body_mitigations", lambda body: [])
    return Runs(tmp_path)


def test_the_runs_are_found_in_submission_order_and_read_after_the_sixth_slot(runs: Runs) -> None:
    for name in timing.ORDER:
        runs.add(name, duration=299.0)
    staged = runs.root / "runs" / "staged"
    staged.mkdir()
    (staged / "cases.json").write_bytes((TREE / "p1" / "cases.json").read_bytes())
    found = timing.bound_runs(runs.root)
    require(found == runs.made, f"found {found}")
    require(timing.next_request(found) == "complete", "six admitted runs complete the case")
    result = timing.analyze(found)
    # Six durations of 299 s sum past 1800 s; the cap gates a further submission and leaves the reading intact.
    require(result["reading"] == "doubled-above-fit", f"reading {result['reading']}")
    require(len(result["deviations_from_prediction"]) == 6, f"deviations {result['deviations_from_prediction']}")


def test_an_interrupted_submission_stops_the_discovery(runs: Runs) -> None:
    run = runs.add("p1")
    (run / "submission.json").unlink()
    (run / "submission-state.json").write_text("{}")
    with pytest.raises(timing.TimingError, match="interrupted submission"):
        timing.bound_runs(runs.root)


@pytest.mark.parametrize(
    ("make", "message"),
    [
        (lambda r: (r.add("p2"),), "slot 1 runs p1"),
        (lambda r: (r.add("p1", status="canceled"),), "ended canceled"),
        (lambda r: (r.add("p1", duration=300.0),), "reaches the limit"),
        (lambda r: (r.add("p1", platform="qpu:belenos"),), "the service reports"),
        (lambda r: (r.add("p1"), r.add("p2", gap=6)), "before slot 1 was collected"),
    ],
)
def test_each_per_job_stop_condition_refuses(
    runs: Runs, make: Callable[[Runs], tuple[Path, ...]], message: str
) -> None:
    made = make(runs)
    with pytest.raises(timing.TimingError, match=message):
        timing.next_request(list(made))


def test_a_submission_in_the_second_of_the_previous_collection_is_admitted(runs: Runs) -> None:
    first = runs.add("p1")
    second = runs.add("p2")
    receipt = json.loads((second / "submission.json").read_text())
    receipt["submitted_utc"] = "2026-12-01T10:05:00+00:00"
    (second / "submission.json").write_text(json.dumps(receipt))
    require(timing.next_request([first, second]) == "p2", "the same second spelled Z and +00:00 is one instant")


def test_the_caps_reserve_the_next_job(runs: Runs, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qd_platform, "run_facts", lambda run: {"charge": 1.1})
    made = [runs.add(name) for name in timing.ORDER[:5]]
    with pytest.raises(timing.TimingError, match="leave no room"):
        timing.next_request(made)


def test_the_mitigation_list_of_a_run_is_read(runs: Runs, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qd_platform, "body_mitigations", lambda body: ["detector-balancing"])
    run = runs.add("p1")
    with pytest.raises(timing.TimingError, match="carries mitigations"):
        timing.next_request([run])


def checked(concurrent: int = 0, queued: int = 0) -> dict[str, Any]:
    return {"availability_at_plan": {"num_concurrent_jobs": concurrent, "num_jobs_in_queue": queued}, "body": {}}


def staged(runs: Runs, name: str) -> Path:
    run = runs.root / "runs" / f"staged-{name}"
    run.mkdir(parents=True)
    (run / "cases.json").write_bytes((TREE / name / "cases.json").read_bytes())
    return run


def test_the_submission_gate_admits_the_next_slot_on_an_idle_token(runs: Runs) -> None:
    runs.add("p1")
    timing.SubmissionGate(staged(runs, "p2"), runs.root)(checked())
    require(timing.SubmissionGate.submit_wrapper == committed("p1")["submit_wrapper"], "wrapper capability")


@pytest.mark.parametrize(
    ("name", "plan", "message"),
    [
        ("p2", checked(), "next slot runs p1"),
        ("p1", checked(concurrent=1), "running or queued"),
        ("p1", checked(queued=1), "running or queued"),
    ],
)
def test_the_submission_gate_refuses(runs: Runs, name: str, plan: dict[str, Any], message: str) -> None:
    with pytest.raises(qd_platform.PlatformError, match=message):
        timing.SubmissionGate(staged(runs, name), runs.root)(plan)


def test_qd_platform_submit_refuses_a_p_run_without_the_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qd_platform, "load_case", lambda directory: (committed("p1"), {}, "x"))
    with pytest.raises(qd_platform.PlatformError, match="submits only through"):
        qd_platform.submit(TREE / "p1", timing.PLATFORM, "approval", 1.08, 150.0, 1.0)


class Clock:
    """A monotonic clock that a read advances by its latency and a sleep by its argument."""

    def __init__(self, latency: float) -> None:
        self.now, self.latency = 0.0, latency
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def test_the_recorder_reads_on_a_fixed_cadence_and_logs_transient_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "submission.json").write_text(json.dumps({"job_id": "job-1", "cases_sha256": "x"}))
    clock = Clock(latency=3.0)
    answers: list[Any] = [
        {"status": "running", "progress": 0.5, "progress_message": "step 1"},
        qd_platform.RefusedError("busy", code=503),
        {"status": "completed", "progress": 1.0, "progress_message": None},
    ]

    def request(method: str, route: str) -> Any:
        clock.now += clock.latency
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(qd_platform, "load_case", lambda directory: ({}, {}, "x"))
    monkeypatch.setattr(qd_platform, "request", request)
    monkeypatch.setattr(qd_platform, "collect", lambda directory, poll, timeout: {"status": "collected"})
    monkeypatch.setattr(timing.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(timing.time, "sleep", clock.sleep)
    require(timing.record(run, poll=10.0) == {"status": "collected"}, "the recorder did not collect")
    lines = [json.loads(line) for line in (run / timing.STATUS_LOG).read_text().splitlines()]
    require([line.get("status") for line in lines] == ["running", None, "completed"], f"logged {lines}")
    require("busy" in lines[1]["error"], f"logged {lines[1]}")
    # Each read starts 10 s after the previous one started, so the 3 s read latency shortens the sleep to 7 s.
    require(clock.sleeps == [7.0, 7.0], f"slept {clock.sleeps}")
    with pytest.raises(timing.TimingError, match="outside"):
        timing.record(run, poll=11.0)


def test_the_recorder_refuses_a_run_whose_receipt_names_another_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "submission.json").write_text(json.dumps({"job_id": "job-1", "cases_sha256": "y"}))
    monkeypatch.setattr(qd_platform, "load_case", lambda directory: ({}, {}, "x"))
    with pytest.raises(timing.TimingError, match="submission receipt"):
        timing.record(run)


def test_a_rebuild_is_refused_once_a_submission_binds_the_tree(tmp_path: Path) -> None:
    tree, results = tmp_path / "tree", tmp_path / "results"
    timing.write(tree, results)
    (tree / "p1" / "cases.json").write_bytes(b"{}\n")
    stage = results / "runs" / "r1"
    stage.mkdir(parents=True)
    (stage / "cases.json").write_bytes((TREE / "p2" / "cases.json").read_bytes())
    # A staged copy without a receipt binds nothing, so the rebuild still runs.
    timing.write(tree, results)
    (tree / "p1" / "cases.json").write_bytes(b"{}\n")
    (stage / "submission-state.json").write_text("{}")
    with pytest.raises(timing.TimingError, match="bind the tree"):
        timing.write(tree, results)
