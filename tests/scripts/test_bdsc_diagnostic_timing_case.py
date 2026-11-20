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
    assert flat == set(timing.files_of(timing.documents()))
    on_disk = {
        "case.json": (TREE / "case.json").read_bytes(),
        **{
            name: {file: (TREE / name / file).read_bytes() for file in ("cases.json", "circuit.json")}
            for name in timing.REQUESTS
        },
    }
    assert without_sources(on_disk) == without_sources(timing.documents())
    for name in timing.REQUESTS:
        assert sorted(committed(name)["successor_sources"]) == sorted(timing.SOURCES)


@pytest.mark.parametrize("name", sorted(timing.REQUESTS))
def test_each_request_keeps_its_groups_byte_for_byte_in_the_retained_order(name: str) -> None:
    job, groups = timing.REQUESTS[name]
    source, manifest = retained(job), committed(name)
    kept = [s for s in source["settings"] if timing.group_of(s) in groups]
    assert manifest["settings"] == kept
    assert len(kept) == 12 and {timing.group_of(s) for s in kept} == set(groups)
    assert (manifest["iterations"], manifest["max_samples"], manifest["max_shots"]) == (12, 480000, 960000)
    kept_keys = ("diagnostic_case_sha256", "draw", "target_sha256", "mitigations", "max_duration", "circuit")
    assert manifest["platforms"] == source["platforms"]
    for key in kept_keys:
        assert manifest[key] == source[key]
    assert manifest["job"] == name and manifest["source_job"]["job"] == job
    assert manifest["timing_case_sha256"] == timing.sha256_bytes((TREE / "case.json").read_bytes())
    assert (TREE / name / "circuit.json").read_bytes() == (timing.SOURCE_TREE / job / "circuit.json").read_bytes()


def test_the_requests_omit_the_groups_the_case_names() -> None:
    names = {name: {timing.group_of(s) for s in committed(name)["settings"]} for name in timing.REQUESTS}
    assert names == {"p1": {"out-s0", "out-s1"}, "p2": {"rev-s0", "rev-s1"}}
    assert "out-s2-pi" not in {s["name"] for s in committed("p2")["settings"]}


def test_the_retained_draw_stays_claimed_by_its_own_record_only() -> None:
    # The P manifests name the retained draw under the retained record's sha256, so the draw check of the retained
    # tree's rebuild finds no other case that draws from it.
    platform = timing.PLATFORM
    claims = rebound(
        diag.draw_claims,
        case_record=lambda: acquisition.case_record(platform),
        bdsc_cases=acquisition.cases_namespace(platform),
    )(committed("p1")["draw"])
    assert not [path for path in claims if "bdsc_diagnostic_timing_sim_belenos" in path]


@pytest.mark.parametrize(
    ("p1", "p2", "reading"),
    [
        ([150.0, 150.0, 170.0], [150.0, 150.0, 150.0], "service-variation"),
        ([150.0, 151.0, 152.0], [100.0, 101.0, 102.0], "request-cost"),
        ([150.0, 151.0, 152.0], [150.0, 151.0, 152.0], "doubled-above-fit"),
        ([140.0, 141.0, 142.0], [140.0, 141.0, 142.0], "doubled-within-fit"),
        ([150.0, 160.0, 155.0], [150.0, 151.0, 152.0], "inconclusive"),
        ([150.0, 151.0, 152.0], [140.0, 141.0, 142.0], "inconclusive"),
    ],
)
def test_the_decision_rows_of_the_case(p1: list[float], p2: list[float], reading: str) -> None:
    assert timing.decide({"p1": p1, "p2": p2})["reading"] == reading


class Runs:
    """Synthetic collected runs of the committed requests under a scratch directory."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.made: list[Path] = []

    def add(self, name: str, duration: float = 150.0, status: str = "completed", gap: int = 0) -> Path:
        slot = len(self.made)
        run = self.root / f"run-{slot}-{name}"
        run.mkdir()
        (run / "cases.json").write_bytes((TREE / name / "cases.json").read_bytes())
        minute = 10 * slot - gap
        submitted = f"2026-12-01T10:{minute:02d}:00+00:00"
        collected = f"2026-12-01T10:{10 * slot + 5:02d}:00+00:00"
        (run / "submission.json").write_text(json.dumps({"platform": timing.PLATFORM, "submitted_utc": submitted}))
        results = {"status": {"status": status, "duration": duration}, "collected_utc": collected}
        (run / "results.json").write_text(json.dumps(results))
        self.made.append(run)
        return run


@pytest.fixture
def runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Runs:
    monkeypatch.setattr(qd_platform, "run_facts", lambda run: {"charge": 1.0})
    return Runs(tmp_path)


def test_the_schedule_admits_the_six_slots_and_the_analysis_reads_them(runs: Runs) -> None:
    for name in timing.ORDER:
        runs.add(name, duration=148.0)
    result = timing.analyze(runs.made)
    assert [f["request"] for f in result["runs"]] == list(timing.ORDER)
    assert result["reading"] == "doubled-above-fit" and result["deviations_from_prediction"] == []


@pytest.mark.parametrize(
    ("make", "message"),
    [
        (lambda r: (r.add("p2"),), "slot 1 runs p1"),
        (lambda r: (r.add("p1", status="canceled"),), "ended canceled"),
        (lambda r: (r.add("p1"), r.add("p2", gap=6)), "before slot 1 was collected"),
        (lambda r: tuple(r.add(n, duration=300.0) for n in timing.ORDER), "reach 1800"),
    ],
)
def test_the_schedule_refuses_each_stop_condition(
    runs: Runs, make: Callable[[Runs], tuple[Path, ...]], message: str
) -> None:
    made = make(runs)
    with pytest.raises(timing.TimingError, match=message):
        timing.schedule(list(made))


def test_the_schedule_refuses_the_credit_cap(runs: Runs, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qd_platform, "run_facts", lambda run: {"charge": 1.1})
    made = [runs.add(name) for name in timing.ORDER]
    with pytest.raises(timing.TimingError, match="reach the cap"):
        timing.schedule(made)


def test_the_recorder_logs_each_status_read_then_collects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "submission.json").write_text(json.dumps({"job_id": "job-1"}))
    answers = iter(
        [
            {"status": "running", "progress": 0.5, "progress_message": "step 1"},
            {"status": "completed", "progress": 1.0, "progress_message": None},
        ]
    )
    sleeps: list[float] = []
    monkeypatch.setattr(qd_platform, "load_case", lambda directory: ({}, {}, ""))
    monkeypatch.setattr(qd_platform, "request", lambda method, route: next(answers))
    monkeypatch.setattr(qd_platform, "collect", lambda directory, poll, timeout: {"status": "collected"})
    monkeypatch.setattr(timing.time, "sleep", sleeps.append)
    assert timing.record(run, poll=10.0) == {"status": "collected"}
    lines = [json.loads(line) for line in (run / timing.STATUS_LOG).read_text().splitlines()]
    assert [line["status"] for line in lines] == ["running", "completed"] and sleeps == [10.0]
    with pytest.raises(timing.TimingError, match="outside"):
        timing.record(run, poll=11.0)


def test_a_rebuild_is_refused_once_a_run_binds_the_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tree, runs = tmp_path / "tree", tmp_path / "runs"
    timing.write(tree, runs)
    (tree / "p1" / "cases.json").write_bytes(b"{}\n")
    timing.write(tree, runs)
    (tree / "p1" / "cases.json").write_bytes(b"{}\n")
    (runs / "r1").mkdir(parents=True)
    (runs / "r1" / "cases.json").write_bytes((tree / "p2" / "cases.json").read_bytes())
    with pytest.raises(timing.TimingError, match="bind the tree"):
        timing.write(tree, runs)
