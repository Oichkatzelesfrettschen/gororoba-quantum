"""Replicated matched-response entry point and staged runner: refusals, stage-1 output, control flow of a dry run."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11"
RUNNER = ROOT / "scripts/qi_replicated_series_run.sh"
ANALYSIS = ROOT / "scripts/qi_replicated_response_analysis.py"
SHELL_PATH = "/usr/bin:/bin"
# Residual SD of the first twelve replicates: 0.02 gives N = 12, 0.025 gives N = 18, 0.05 passes the cap of 60.
SIGMA_FINAL, SIGMA_CONTINUE, SIGMA_CAP = 0.02, 0.025, 0.05


def _check(condition: object) -> None:
    if not condition:
        raise AssertionError


def _fake() -> Any:
    import qi_replicated_series_fake

    return qi_replicated_series_fake


def _build(runs: Path, count: int, sigma: float, effect: float = 0.0, stamp: str = "T") -> list[Path]:
    """Run directories of rep-00 .. rep-(count-1) shaped as the platform's collected runs."""
    fake = _fake()
    out = []
    for index in range(count):
        run = runs / f"{stamp}-tuna17-replicated-q11-rep-{index:02d}"
        shutil.copytree(PROPOSAL / f"rep-{index:02d}", run)
        fake.submit_run(run, "dry-run", index)
        fake.collect_run(run, index, sigma, effect)
        out.append(run)
    return out


def _analysis(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ANALYSIS), *map(str, arguments)], capture_output=True, text=True, check=False
    )


def test_stage1_continue_prints_the_rule_total_and_never_the_mean(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_CONTINUE, effect=0.0123456)
    done = _analysis("--stage1", *runs, "--out", tmp_path / "stage1.json")
    _check(done.returncode == 0)
    _check(done.stdout.splitlines() == ["verdict: continue", "N: 18"])
    record = json.loads((tmp_path / "stage1.json").read_text())
    _check(record["verdict"] == "continue" and record["n"] == 18 and abs(record["s1"] - SIGMA_CONTINUE) < 1e-3)
    _check(
        set(record) == {"schema", "verdict", "s1", "n", "required_total", "proposal_sha256", "replicates", "batch_jobs"}
    )
    text = done.stdout + done.stderr + (tmp_path / "stage1.json").read_text()
    for forbidden in ("0.0123", "mean", "residual", "lag1", "order_difference", "block"):
        _check(forbidden not in text)


@pytest.mark.parametrize(
    ("sigma", "verdict", "total"),
    [(SIGMA_FINAL, "final", "12"), (SIGMA_CONTINUE, "continue", "18"), (SIGMA_CAP, "undecided-at-cap", "12")],
)
def test_stage1_verdicts(tmp_path: Path, sigma: float, verdict: str, total: str) -> None:
    runs = _build(tmp_path / "runs", 12, sigma)
    done = _analysis("--stage1", *runs)
    _check(done.stdout.splitlines() == [f"verdict: {verdict}", f"N: {total}"])


def test_stage1_takes_exactly_the_twelve_stage_one_replicates(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 13, SIGMA_CONTINUE)
    _check(_analysis("--stage1", *runs[:11]).returncode == 1)
    _check(_analysis("--stage1", *runs).returncode == 1)


def test_final_decides_at_the_rules_total_and_cross_checks_stage_one(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 18, SIGMA_CONTINUE)
    stage1 = tmp_path / "stage1.json"
    _check(_analysis("--stage1", *runs[:12], "--out", stage1).returncode == 0)
    final = tmp_path / "final.json"
    done = _analysis("--final", *runs, "--stage1-decision", stage1, "--out", final)
    _check(done.returncode == 0)
    decision = json.loads(final.read_text())["decision"]
    _check(decision["status"] == "not_rejected" and decision["n"] == 18)
    # fewer replicates than the rule's N, and a changed stage-1 record, are refused
    _check(_analysis("--final", *runs[:15], "--out", tmp_path / "x.json").returncode == 1)
    held = json.loads(stage1.read_text())
    held["s1"] *= 1.01
    stage1.write_text(json.dumps(held))
    _check(_analysis("--final", *runs, "--stage1-decision", stage1, "--out", tmp_path / "y.json").returncode == 1)


def test_final_reports_the_stage_one_interval_at_the_cap(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_CAP)
    final = tmp_path / "final.json"
    _check(_analysis("--final", *runs, "--out", final).returncode == 0)
    _check(json.loads(final.read_text())["decision"]["status"] == "undecided_at_cap")


def test_binding_prints_no_residual_and_refuses_a_bad_readout(tmp_path: Path) -> None:
    (run,) = _build(tmp_path / "runs", 1, SIGMA_CONTINUE, effect=0.0123456)
    done = _analysis("--binding", run)
    _check(done.returncode == 0)
    report = json.loads(done.stdout)
    _check(report["batch"] == "rep-00" and report["readout_error"] == 0.0)
    for forbidden in ("0.0123", "residual", "frequenc"):
        _check(forbidden not in done.stdout)
    fake = _fake()
    bad = tmp_path / "bad" / "T-tuna17-replicated-q11-rep-00"
    shutil.copytree(PROPOSAL / "rep-00", bad)
    fake.submit_run(bad, "dry-run", 0)
    fake.collect_run(bad, 0, SIGMA_CONTINUE, 0.0, bad_readout=True)
    refused = _analysis("--binding", bad)
    _check(refused.returncode == 1 and "readout" in refused.stderr)


def test_a_batch_job_id_reused_by_two_replicates_is_refused(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_FINAL)
    # run 11 now claims run 10's batch job and job ids in receipt and collection alike
    for name in ("submission.json", "results.json"):
        source = json.loads((runs[10] / name).read_text())
        target = json.loads((runs[11] / name).read_text())
        if name == "submission.json":
            target["batch_job"] = source["batch_job"]
            for mine, theirs in zip(target["jobs"], source["jobs"], strict=True):
                mine["job"] = theirs["job"]
        else:
            for mine, theirs in zip(target["jobs"], source["jobs"], strict=True):
                mine["job"]["id"] = theirs["job"]["id"]
                mine["job"]["batch_job_id"] = theirs["job"]["batch_job_id"]
                mine["results"][0]["job_id"] = theirs["job"]["id"]
        (runs[11] / name).write_text(json.dumps(target, indent=1))
    done = _analysis("--stage1", *runs)
    _check(done.returncode == 1 and ("repeats" in done.stderr or "rise" in done.stderr))


def test_a_run_of_another_proposal_is_refused(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_FINAL)
    # a manifest with changed bytes, its receipt digest kept consistent so the shared reader accepts the run
    manifest = json.loads((runs[3] / "cases.json").read_text())
    manifest["provider_execution_authorized"] = True
    data = (json.dumps(manifest, indent=1) + "\n").encode()
    (runs[3] / "cases.json").write_bytes(data)
    receipt = json.loads((runs[3] / "submission.json").read_text())
    receipt["cases_sha256"] = hashlib.sha256(data).hexdigest()
    (runs[3] / "submission.json").write_text(json.dumps(receipt, indent=1))
    done = _analysis("--stage1", *runs)
    _check(done.returncode == 1 and "not a replicate of this proposal" in done.stderr)


def test_a_replicate_given_twice_is_refused(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_FINAL)
    twin = tmp_path / "twin"
    shutil.copytree(runs[2], twin)
    done = _analysis("--stage1", *runs, twin)
    _check(done.returncode == 1 and "twice" in done.stderr)


# --- runner -----------------------------------------------------------------------------------------------------


def _run(
    tmp_path: Path, extra: dict[str, str] | None = None, arguments: list[str] | None = None
) -> tuple[int, str, str, Path]:
    env = {
        "PATH": SHELL_PATH,
        "PYTHON": sys.executable,
        "FAKE_LOG": str(tmp_path / "calls.log"),
        "QI_PAUSE_SLEEP": "0",
        "FAKE_SIGMA": str(SIGMA_FINAL),
        **(extra or {}),
    }
    state = tmp_path / "state"
    command = [
        "sh",
        str(RUNNER),
        "--dry-run",
        "--runs-dir",
        str(tmp_path / "runs"),
        "--state-dir",
        str(state),
        "--stamp",
        "T",
        *(arguments or []),
    ]
    done = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    log = tmp_path / "calls.log"
    return done.returncode, log.read_text() if log.exists() else "", done.stderr, state


def _marker(state: Path) -> str:
    return (state / "marker").read_text().strip()


def test_the_runner_does_nothing_without_the_approval_and_the_arming_argument(tmp_path: Path) -> None:
    env = {"PATH": SHELL_PATH, "PYTHON": sys.executable, "QI_PYTHON": sys.executable}
    runs = tmp_path / "runs"
    for arguments in (
        [],
        ["--approval", "QUOTE"],
        ["--submit-replicated-q11"],
        ["--approval", "QUOTE", "--submit-replicated-q11"],
        ["--approval", "", "--submit-replicated-q11", "--deadline", "60"],
        ["--approval", "QUOTE", "--submit-replicated-q11-x", "--deadline", "60"],
        ["--dry-run", "--approval", "QUOTE", "--runs-dir", str(runs), "--state-dir", str(tmp_path / "s")],
        ["--dry-run", "--submit-replicated-q11", "--runs-dir", str(runs), "--state-dir", str(tmp_path / "s")],
        ["--dry-run"],
    ):
        done = subprocess.run(["sh", str(RUNNER), *arguments], capture_output=True, text=True, env=env, check=False)
        _check(done.returncode == 2)
    _check(not runs.exists() and not (tmp_path / "s").exists())


def test_a_dry_run_continues_to_the_rules_total_and_writes_the_marker_and_resume_note(tmp_path: Path) -> None:
    code, calls, err, state = _run(tmp_path, {"FAKE_SIGMA": str(SIGMA_CONTINUE)})
    _check(code == 0)
    names = [line for line in calls.splitlines() if line.startswith("submit")]
    _check(names == [f"submit rep-{i:02d}" for i in range(18)])
    _check("stage 1: verdict continue, N 18" in err)
    _check(_marker(state) == "done" and (state / "final.json").exists() and (state / "RESUME.md").exists())
    _check(json.loads((state / "final.json").read_text())["decision"]["n"] == 18)


def test_a_dry_run_stops_after_stage_one_when_the_rule_asks_for_twelve_or_for_more_than_the_cap(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path / "a")
    _check(code == 0 and calls.count("submit") == 12 and _marker(state) == "done")
    code, calls, _, state = _run(tmp_path / "b", {"FAKE_SIGMA": str(SIGMA_CAP)})
    _check(code == 0 and calls.count("submit") == 12)
    _check(json.loads((state / "final.json").read_text())["decision"]["status"] == "undecided_at_cap")


def test_a_failed_binding_of_the_profile_unit_stops_the_series_with_a_marker(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path, {"FAKE_BAD_READOUT_REP": "rep-00"})
    _check(code != 0 and calls.splitlines() == ["submit rep-00", "collect rep-00"])
    _check(_marker(state).startswith("failed binding check of"))


def test_a_restart_skips_collected_replicates_and_collects_a_submitted_one_without_a_second_submit(
    tmp_path: Path,
) -> None:
    code, calls, _, state = _run(tmp_path, {"FAKE_COLLECT_FAIL_REP": "rep-03"})
    _check(code != 0 and _marker(state).startswith("failed rep-03: collection failed"))
    _check(calls.count("submit") == 4)
    (tmp_path / "calls.log").unlink()
    code, calls, _, state = _run(tmp_path)
    _check(code == 0 and _marker(state) == "done")
    lines = calls.splitlines()
    _check(lines[0] == "collect rep-03" and lines[1] == "submit rep-04")
    _check(not any(line.endswith(f"rep-0{i}") for line in lines for i in range(3)))
    _check(sum(line.startswith("submit") for line in lines) == 8)


def test_a_checkpoint_without_a_receipt_and_another_stamp_each_stop_the_series(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run = runs / "T-tuna17-replicated-q11-rep-00"
    shutil.copytree(PROPOSAL / "rep-00", run)
    (run / "submission-state.json").write_text("{}")
    code, calls, _, state = _run(tmp_path)
    _check(code != 0 and calls == "" and "reconcile" in _marker(state))
    shutil.rmtree(runs)
    shutil.copytree(PROPOSAL / "rep-00", runs / "U-tuna17-replicated-q11-rep-00")
    code, calls, _, state = _run(tmp_path, {"FAKE_LOG": str(tmp_path / "c2.log")})
    _check(code != 0 and "holds this series under stamp U" in _marker(state))


def test_a_refused_pause_is_retried_and_ten_refusals_stop_the_replicate(tmp_path: Path) -> None:
    code, calls, err, _ = _run(tmp_path / "a", {"FAKE_REFUSE": "2"})
    _check(code == 0 and "rep-00: sleep 6" in err and calls.count("refused") == 2)
    code, calls, _, state = _run(tmp_path / "b", {"FAKE_REFUSE": "99"})
    _check(code != 0 and calls.count("submit rep-00") == 10 and "stopped after 10 refusal" in _marker(state))


def test_the_deadline_bounds_the_series(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path, arguments=["--deadline", "0"])
    _check(code != 0 and calls == "" and "deadline" in _marker(state))


def test_a_changed_run_copy_stops_the_series_before_any_submit(tmp_path: Path) -> None:
    run = tmp_path / "runs" / "T-tuna17-replicated-q11-rep-00"
    shutil.copytree(PROPOSAL / "rep-00", run)
    (run / "readout-0.cq").write_text("changed\n")
    code, calls, _, state = _run(tmp_path)
    _check(code != 0 and calls == "" and "differs" in _marker(state))


def test_the_dry_run_refuses_the_retained_runs_directory() -> None:
    done = subprocess.run(
        [
            "sh",
            str(RUNNER),
            "--dry-run",
            "--runs-dir",
            str(ROOT / "results/quantum_inspire/runs"),
            "--state-dir",
            "/nonexistent-state",
        ],
        capture_output=True,
        text=True,
        env={"PATH": SHELL_PATH, "PYTHON": sys.executable},
        check=False,
    )
    _check(done.returncode == 2)


def test_the_runner_script_is_shellcheck_clean() -> None:
    tool = shutil.which("shellcheck")
    if tool is None:
        pytest.skip("shellcheck is not installed")
    done = subprocess.run([tool, "-S", "error", str(RUNNER)], capture_output=True, text=True, check=False)
    _check(done.returncode == 0)
