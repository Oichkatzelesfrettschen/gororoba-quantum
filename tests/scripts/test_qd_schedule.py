import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts")]

import qd_schedule as qs  # noqa: E402

BODY = {"payload": {"command": "sample_count"}, "platform_name": "qpu:belenos", "process_id": "a"}
T0 = qs.utc("2026-11-01T12:00:00Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(qs, "ROOT", tmp_path)
    monkeypatch.setattr(qs, "SCHEDULES", tmp_path / "results/quandela/schedules")
    monkeypatch.setattr(qs, "RUNS", tmp_path / "results/quandela/runs")
    monkeypatch.setattr(qs, "CASES", tmp_path / "results/quandela/cases")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/check_ok.py").write_text("import sys\nsys.exit(0)\n")
    (tmp_path / "scripts/check_no.py").write_text("import sys\nprint('stop condition')\nsys.exit(4)\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/case.md").write_text("written case\n")
    for key in ("j1", "j2"):
        case = tmp_path / "results/quandela/cases/demo" / key
        case.mkdir(parents=True)
        (case / "cases.json").write_text(json.dumps({"job": key}))
        (case / "circuit.json").write_text("{}")
    (tmp_path / "results/quandela/runs").mkdir()
    return tmp_path


def schedule(root: Path, **changes: Any) -> Path:
    jobs = []
    for key in ("j1", "j2"):
        case = root / "results/quandela/cases/demo" / key
        jobs.append(
            {
                "key": key,
                "case_dir": f"results/quandela/cases/demo/{key}",
                "run_name": f"qpu_belenos-demo-{key}",
                "inputs_sha256": {f: sha(case / f) for f in qs.INPUTS},
                "body_sha256": qs.body_digest(BODY),
                "not_before": "2026-11-01T12:00:00Z",
                "after": {"key": "j1", "min_gap_seconds": 3600} if key == "j2" else None,
                "max_credits": 1.12,
                "expected_seconds": 200.0,
                "per_job_credits": 1.0,
                "admit_statuses": ["running"],
                "plan_check": ["scripts/check_ok.py", "--plan-check", "{plan}"],
                "matched_check": ["scripts/check_ok.py", "--matched-check", "{run}"],
                "snapshot_out": None,
            }
        )
    record = {
        "schema": qs.SCHEMA,
        "name": "demo",
        "enabled": True,
        "approval": "approved: two demo jobs",
        "case": "docs/case.md",
        "platform": "qpu:belenos",
        "max_total_credits": 2.24,
        "jobs": jobs,
    }
    for key, value in changes.items():
        if key.startswith("job0_"):
            jobs[0][key[5:]] = value
        else:
            record[key] = value
    path = root / "results/quandela/schedules/demo.json"
    qs.write(path, record)
    return path


class Provider:
    """A stand-in for qd_platform's network calls that writes the files the real ones write."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, body: dict[str, Any] = BODY) -> None:
        self.body = body
        self.plan_error: str | None = None
        self.submit_error: str | None = None
        self.submitted: list[Path] = []
        self.ready = True
        for name in ("plan", "submit", "recover", "collect", "snapshot"):
            monkeypatch.setattr(qs.qd, name, getattr(self, name))

    def plan(self, case_dir: Path, *args: Any) -> dict[str, Any]:
        if self.plan_error:
            raise qs.qd.PlatformError(self.plan_error)
        return {"case": case_dir.name, "body": dict(self.body), "body_sha256": "x"}

    def submit(self, run: Path, platform: str, approval: str, *args: Any) -> dict[str, Any]:
        if self.submit_error:
            raise qs.qd.PlatformError(self.submit_error)
        self.submitted.append(run)
        qs.write(run / "job-body.json", self.body)
        qs.write(run / "submission-state.json", {"phase": "posted", "job_id": f"job-{len(self.submitted)}"})
        qs.write(run / "submission.json", {"job_id": f"job-{len(self.submitted)}", "approval": approval})
        return {"job_id": f"job-{len(self.submitted)}"}

    def recover(self, run: Path) -> dict[str, Any]:
        raise AssertionError("recover is not expected")

    def collect(self, run: Path, poll: float, timeout: float) -> dict[str, Any]:
        if not self.ready:
            raise qs.qd.PlatformError("job is still running")
        qs.write(run / "results.json", {"status": {"status": "completed", "start_time": T0 + 100, "duration": 167}})
        return {}

    def snapshot(self, out: Path) -> None:
        raise AssertionError("snapshot is not expected")


def step(path: Path, now: float, run_id: str = "1.1", plan_only: bool = False) -> dict[str, Any]:
    return qs.step(qs.load(path), run_id, now + 3600, qs.ROOT / "work", plan_only, clock=lambda: now)


def test_load_refuses_each_unsafe_schedule(tree: Path) -> None:
    qs.load(schedule(tree))
    case = tree / "results/quandela/cases/demo/j1/cases.json"
    refusals: dict[str, dict[str, Any]] = {
        "inputs_sha256": {"job0_inputs_sha256": {"cases.json": "0" * 64, "circuit.json": sha(case)}},
        "after": {"job0_after": {"key": "j2", "min_gap_seconds": 0}},
        "exceed": {"max_total_credits": 2.0},
        "enabled": {"job0_body_sha256": None},
        "placeholder": {"job0_plan_check": ["scripts/check_ok.py", "{run}"]},
        "outside": {"job0_case_dir": "docs"},
        "script": {"job0_matched_check": ["../outside.py", "{run}"]},
    }
    for reason, changes in refusals.items():
        with pytest.raises(qs.ScheduleError):
            qs.load(schedule(tree, **changes))
        if reason == "enabled":
            qs.load(schedule(tree, enabled=False, job0_body_sha256=None))


def test_two_jobs_run_in_order_with_the_gap_after_the_provider_execution_end(tree: Path, monkeypatch) -> None:
    path = schedule(tree)
    provider = Provider(monkeypatch)
    if step(path, T0 - 1)["outcome"] != "wait":
        raise AssertionError("a job started before not_before")
    prepared = step(path, T0)
    if prepared["outcome"] != "prepared" or provider.submitted:
        raise AssertionError(prepared)
    outcomes = [step(path, T0 + 1)["outcome"] for _ in range(3)]
    if outcomes != ["continue", "continue", "continue"] or len(provider.submitted) != 1:
        raise AssertionError(outcomes)
    receipt = qs.read(tree / "results/quandela/schedules/demo/j1.receipt.json")
    if receipt["outcome"] != "passed" or qs.read(provider.submitted[0] / "submission.json")["approval"] != (
        "approved: two demo jobs"
    ):
        raise AssertionError(receipt)
    end = T0 + 100 + 167
    waiting = step(path, end + 3599)
    if waiting != {"outcome": "wait", "key": "j2", "state": "pending", "not_before": "2026-11-01T13:04:27Z"}:
        raise AssertionError(waiting)
    if step(path, end + 3600)["outcome"] != "prepared":
        raise AssertionError("j2 did not start after its gap")
    for _ in range(3):
        step(path, end + 3601)
    if step(path, end + 3602) != {"outcome": "done"} or len(provider.submitted) != 2:
        raise AssertionError(provider.submitted)


def test_a_running_job_waits_and_resumes_in_a_later_tick(tree: Path, monkeypatch) -> None:
    path = schedule(tree)
    provider = Provider(monkeypatch)
    step(path, T0)
    step(path, T0)
    provider.ready = False
    if step(path, T0, run_id="2.1")["outcome"] != "wait":
        raise AssertionError("an uncollected job did not wait")
    provider.ready = True
    if step(path, T0, run_id="3.1")["outcome"] != "continue" or len(provider.submitted) != 1:
        raise AssertionError("a later tick resubmitted or failed to collect")


@pytest.mark.parametrize("cause", ["plan", "body", "plan_check"])
def test_a_stop_before_sending_holds_the_job_and_leaves_no_run_directory(tree: Path, monkeypatch, cause) -> None:
    path = (
        schedule(tree, job0_plan_check=["scripts/check_no.py", "{plan}"]) if cause == "plan_check" else schedule(tree)
    )
    provider = Provider(monkeypatch, body={**BODY, "payload": {"command": "other"}} if cause == "body" else BODY)
    if cause == "plan":
        provider.plan_error = "qpu:belenos is calibration"
    held = step(path, T0)
    if held["outcome"] != "stop" or held["stage"] != cause or any((tree / "results/quandela/runs").iterdir()):
        raise AssertionError(held)
    if step(path, T0 + 7200)["state"] != "held" or provider.submitted:
        raise AssertionError("a held schedule continued")


def test_a_submit_refused_after_the_pushed_intent_removes_the_run_from_the_results_branch(tree, monkeypatch) -> None:
    path = schedule(tree)
    provider = Provider(monkeypatch)
    step(path, T0)
    branch = tree / "branch"
    qs.sync(qs.load(path), tree, branch)
    pushed = list((branch / "results/quandela/runs").iterdir())
    provider.submit_error = "the token has a running or queued job"
    if step(path, T0)["stage"] != "submit" or len(pushed) != 1:
        raise AssertionError("the refusal did not hold")
    qs.sync(qs.load(path), tree, branch)
    if (
        any((branch / "results/quandela/runs").iterdir())
        or not (branch / "results/quandela/schedules/demo/j1.hold.json").exists()
    ):
        raise AssertionError("the results branch keeps a run directory without a job")


def test_an_intent_from_another_workflow_run_reads_interrupted(tree: Path, monkeypatch) -> None:
    path = schedule(tree)
    provider = Provider(monkeypatch)
    step(path, T0, run_id="1.1")
    stopped = step(path, T0, run_id="2.1")
    if stopped["state"] != "interrupted" or provider.submitted:
        raise AssertionError(stopped)


def test_a_run_directory_without_an_intent_stops_the_schedule(tree: Path, monkeypatch) -> None:
    path = schedule(tree)
    provider = Provider(monkeypatch)
    (tree / "results/quandela/runs/2026-10-31T120000Z-qpu_belenos-demo-j1").mkdir()
    (tree / "results/quandela/runs/2026-10-31T120000Z-qpu_belenos-demo-j1-repeat").mkdir()
    stopped = step(path, T0)
    if (
        stopped["state"] != "foreign"
        or stopped["run"] != "2026-10-31T120000Z-qpu_belenos-demo-j1"
        or provider.submitted
    ):
        raise AssertionError(stopped)


def test_plan_only_reports_the_digest_and_writes_nothing(tree: Path, monkeypatch) -> None:
    path = schedule(tree, enabled=False)
    Provider(monkeypatch)
    planned = step(path, T0, plan_only=True)
    if planned["outcome"] != "planned" or planned["body_sha256"] != planned["pinned"] or planned["plan_check_code"]:
        raise AssertionError(planned)
    if any((tree / "results/quandela/runs").iterdir()) or (tree / "results/quandela/schedules/demo").exists():
        raise AssertionError("plan-only wrote to the tree")
    if step(path, T0)["outcome"] != "stop":
        raise AssertionError("a disabled schedule ran")


def test_body_digest_equals_across_the_two_retained_runs_of_one_frozen_request() -> None:
    runs = ROOT / "results/quandela/runs"
    first, repeat = (
        qs.read(runs / name / "job-body.json")
        for name in (
            "2026-10-23T195000Z-qpu_belenos-bdsc_stationarity-b1-j1",
            "2026-10-23T201808Z-qpu_belenos-bdsc_stationarity-b1-j1-repeat",
        )
    )
    if first["process_id"] == repeat["process_id"] or qs.body_digest(first) != qs.body_digest(repeat):
        raise AssertionError("the digest does not isolate the frozen request")
    if qs.body_digest({**first, "payload": None}) == qs.body_digest(first):
        raise AssertionError("the digest ignores the payload")
