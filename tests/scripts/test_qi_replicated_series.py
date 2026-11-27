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


def _strict(*arguments: object) -> subprocess.CompletedProcess[str]:
    """The analysis as a real series calls it: a fabricated run directory is refused."""
    return subprocess.run(
        [sys.executable, str(ANALYSIS), *map(str, arguments)], capture_output=True, text=True, check=False
    )


def _analysis(*arguments: object) -> subprocess.CompletedProcess[str]:
    """The analysis in the explicit dry-run mode the offline stand-in's records need."""
    return _strict("--allow-fabricated", *arguments)


BLINDED = ("0.0123", "mean", "residual", "lag1", "order_difference", "block")


def _blinded(text: str, *paths: Path) -> bool:
    """True when the text names none of the blinded quantities once the checkout and scratch paths are removed.

    A warning line carries the source path, and a checkout or worktree path can hold a blinded word.
    """
    for path in sorted({ROOT, *paths}, key=lambda p: len(str(p)), reverse=True):
        text = text.replace(str(path), "<path>")
    return not any(word in text for word in BLINDED)


def test_blinding_check_ignores_the_paths_and_reads_the_rest() -> None:
    held = Path("/work/a5-covariance-blocks")
    _check(_blinded(f"{held}/gororoba_quantum/x.py:1: RuntimeWarning\nverdict: continue", held))
    _check(_blinded(f"{ROOT}/scripts/x.py:1: note"))
    _check(not _blinded(f"{held}/x.py: block 3", held))
    _check(not _blinded("verdict: continue\nmean: 0.01"))


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
    _check(_blinded(done.stdout + done.stderr + (tmp_path / "stage1.json").read_text(), tmp_path))


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


def test_final_refuses_a_twelve_replicate_series_whose_rule_asks_for_more_and_writes_nothing(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_CONTINUE)
    stage1 = tmp_path / "stage1.json"
    _check(_analysis("--stage1", *runs, "--out", stage1).returncode == 0)
    _check(json.loads(stage1.read_text())["verdict"] == "continue")
    for extra in ((), ("--stage1-decision", stage1)):
        out = tmp_path / f"final-{len(extra)}.json"
        done = _analysis("--final", *runs, *extra, "--out", out)
        _check(done.returncode == 1 and "not final" in done.stderr and not out.exists())


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
    # a dry run writes one level below the directories it is given
    return done.returncode, log.read_text() if log.exists() else "", done.stderr, state / "dry-run"


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


@pytest.mark.audit
def test_a_dry_run_continues_to_the_rules_total_and_writes_the_marker_and_resume_note(tmp_path: Path) -> None:
    code, calls, err, state = _run(tmp_path, {"FAKE_SIGMA": str(SIGMA_CONTINUE)})
    _check(code == 0)
    names = [line for line in calls.splitlines() if line.startswith("submit")]
    _check(names == [f"submit rep-{i:02d}" for i in range(18)])
    _check("stage 1: verdict continue, N 18" in err)
    _check(_marker(state) == "done" and (state / "final.json").exists() and (state / "RESUME.md").exists())
    _check(json.loads((state / "final.json").read_text())["decision"]["n"] == 18)


@pytest.mark.audit
def test_a_dry_run_stops_after_stage_one_when_the_rule_asks_for_twelve_or_for_more_than_the_cap(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path / "a")
    _check(code == 0 and calls.count("submit") == 12 and _marker(state) == "done")
    _check(json.loads((state / "stage1.json").read_text())["verdict"] == "final")
    _check(json.loads((state / "final.json").read_text())["decision"]["n"] == 12)
    code, calls, err, state = _run(tmp_path / "b", {"FAKE_SIGMA": str(SIGMA_CAP)})
    _check(code == 0 and calls.count("submit") == 12 and calls.count("collect") == 12)
    _check(_marker(state) == "done undecided-at-cap" and "undecided at the cap" in err)
    _check(json.loads((state / "stage1.json").read_text())["verdict"] == "undecided-at-cap")
    _check(json.loads((state / "final.json").read_text())["decision"]["status"] == "undecided_at_cap")
    _check((state / "final.out").read_text().splitlines() == ["status: undecided_at_cap", "N: 12"])


def test_a_failed_binding_of_the_profile_unit_stops_the_series_with_a_marker(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path, {"FAKE_BAD_READOUT_REP": "rep-00"})
    _check(code != 0 and calls.splitlines() == ["submit rep-00", "collect rep-00"])
    _check(_marker(state).startswith("failed binding check of"))


def test_a_restart_skips_collected_replicates_and_collects_a_submitted_one_without_a_second_submit(
    tmp_path: Path,
) -> None:
    code, calls, _, state = _run(tmp_path, {"FAKE_COLLECT_FAIL_REP": "rep-02"})
    _check(code != 0 and _marker(state).startswith("failed rep-02: collection failed"))
    _check(
        calls.splitlines()
        == ["submit rep-00", "collect rep-00", "submit rep-01", "collect rep-01", "submit rep-02", "collect rep-02"]
    )
    (tmp_path / "calls.log").unlink()
    code, calls, _, state = _run(tmp_path, {"FAKE_FAIL_REP": "rep-04"})
    _check(code != 0 and _marker(state).startswith("failed rep-04"))
    _check(calls.splitlines() == ["collect rep-02", "submit rep-03", "collect rep-03", "submit rep-04"])


def test_failed_provider_jobs_stop_the_series_without_a_collect_and_a_restart_stops_the_same_way(
    tmp_path: Path,
) -> None:
    code, calls, _, state = _run(tmp_path, {"FAKE_JOBS_FAIL_REP": "rep-02"})
    _check(code != 0)
    _check(
        calls.splitlines() == ["submit rep-00", "collect rep-00", "submit rep-01", "collect rep-01", "submit rep-02"]
    )
    marker = _marker(state)
    _check(
        marker
        == "failed rep-02: provider jobs failed: Quantum backend error: OSError [Errno 28] No space left on device"
    )
    run = tmp_path / "runs" / "dry-run" / "T-tuna17-replicated-q11-rep-02"
    record = json.loads((run / "provider-failure.json").read_text())
    _check(record["schema"] == "qi-provider-failure-v1" and len(record["jobs"]) == 3)
    _check(all(job["status"] == "failed" for job in record["jobs"]) and not (run / "results.json").exists())
    (tmp_path / "calls.log").unlink()
    code, calls, _, state = _run(tmp_path, {"FAKE_JOBS_FAIL_REP": "rep-02"})
    _check(code != 0 and calls == "" and _marker(state) == marker)
    # the same restart without the fake failure still stops: the record on the directory decides
    code, calls, _, state = _run(tmp_path)
    _check(code != 0 and calls == "" and _marker(state) == marker)


def test_a_restart_on_a_submitted_replicate_reads_the_provider_status_before_collecting(tmp_path: Path) -> None:
    code, _, _, state = _run(tmp_path, {"FAKE_COLLECT_FAIL_REP": "rep-00"})
    _check(code != 0 and _marker(state).startswith("failed rep-00: collection failed"))
    (tmp_path / "calls.log").unlink()
    code, calls, _, state = _run(tmp_path, {"FAKE_JOBS_FAIL_REP": "rep-00"})
    _check(code != 0 and calls == "" and _marker(state).startswith("failed rep-00: provider jobs failed: "))


def test_the_failure_message_is_one_line_of_at_most_300_characters(tmp_path: Path) -> None:
    import qi_platform_job_status as status

    run = tmp_path / "run"
    run.mkdir()
    (run / "submission.json").write_text(json.dumps({"batch_job": 7, "jobs": [{"job": 1}, {"job": 2}]}))
    long = "line one\n\n  line   two " + "x" * 400
    rows = {1: {"id": 1, "status": "completed"}, 2: {"id": 2, "status": "failed", "message": long}}
    _check(status.report(run, lambda job: rows[job]) == status.EXIT_FAILED)
    message = json.loads((run / "provider-failure.json").read_text())["message"]
    _check(len(message) == 300 and message.startswith("line one line two xxx") and "\n" not in message)
    ok = tmp_path / "ok"
    ok.mkdir()
    (ok / "submission.json").write_text(json.dumps({"batch_job": 8, "jobs": [{"job": 1}]}))
    _check(status.report(ok, lambda job: {"id": job, "status": "running"}) == 0)
    _check(not (ok / "provider-failure.json").exists())


def test_a_checkpoint_without_a_receipt_and_another_stamp_each_stop_the_series(tmp_path: Path) -> None:
    runs = tmp_path / "runs" / "dry-run"
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
    code, calls, err, _ = _run(tmp_path / "a", {"FAKE_REFUSE": "2", "FAKE_FAIL_REP": "rep-01"})
    _check(code != 0 and "rep-00: sleep 6" in err and calls.count("refused") == 2 and "collect rep-00" in calls)
    code, calls, _, state = _run(tmp_path / "b", {"FAKE_REFUSE": "99"})
    _check(code != 0 and calls.count("submit rep-00") == 10 and "stopped after 10 refusal" in _marker(state))


def test_the_deadline_bounds_the_series(tmp_path: Path) -> None:
    code, calls, _, state = _run(tmp_path, arguments=["--deadline", "0"])
    _check(code != 0 and calls == "" and "deadline" in _marker(state))


def _altered_proposal(tmp_path: Path) -> Path:
    """A copy of the proposal whose shot count differs in proposal.json and in the manifest of rep-00."""
    altered = tmp_path / "altered"
    shutil.copytree(PROPOSAL, altered)
    for path in (altered / "proposal.json", altered / "rep-00" / "cases.json"):
        text = path.read_text()
        _check("16384" in text)
        path.write_text(text.replace("16384", "8192"))
    return altered


def test_an_altered_proposal_stops_the_series_before_any_copy_or_submit(tmp_path: Path) -> None:
    altered = _altered_proposal(tmp_path)
    code, calls, _, state = _run(tmp_path, arguments=["--proposal", str(altered)])
    _check(code != 0 and calls == "" and _marker(state).startswith("failed the proposal differs"))
    _check(not list((tmp_path / "runs").rglob("*rep-*")))
    runs, states = tmp_path / "armed-runs", tmp_path / "armed-state"
    done, stub_calls = _armed(tmp_path, runs, states, extra=("--proposal", str(altered)))
    _check(done.returncode != 0 and stub_calls == [] and not list(runs.glob("*rep-*")))
    _check((states / "marker").read_text().startswith("failed the proposal differs"))


def test_the_proposal_check_passes_the_frozen_proposal_and_refuses_a_changed_circuit(tmp_path: Path) -> None:
    done = _strict("--proposal-check")
    _check(done.returncode == 0 and done.stdout.startswith("proposal: "))
    altered = tmp_path / "altered"
    shutil.copytree(PROPOSAL, altered)
    circuit = sorted((altered / "rep-05").glob("*.cq"))[0]
    circuit.write_text(circuit.read_text() + "\n")
    refused = _strict("--proposal-check", "--proposal", altered)
    _check(refused.returncode == 1 and "rep-05" in refused.stderr)


def test_a_changed_run_copy_stops_the_series_before_any_submit(tmp_path: Path) -> None:
    run = tmp_path / "runs" / "dry-run" / "T-tuna17-replicated-q11-rep-00"
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


# --- fabricated records stay out of an armed series ----------------------------------------------------------------


def _stub(tmp_path: Path) -> Path:
    """A stand-in for the Quantum Inspire interpreter that answers the status read and refuses every other call."""
    stub = tmp_path / "qi_stub.sh"
    stub.write_text(
        '#!/bin/sh\nif [ "$1" = "-c" ]; then echo online; exit 0; fi\n'
        'echo "$*" >>"$STUB_LOG"\necho "stub route refuses" >&2\nexit 1\n'
    )
    stub.chmod(0o755)
    return stub


def _armed(
    tmp_path: Path, runs: Path, state: Path, stamp: str = "T", extra: tuple[str, ...] = ()
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """The armed runner with every provider route replaced by the stub; the stub log lists what it was asked."""
    log = tmp_path / "stub.log"
    log.unlink(missing_ok=True)
    env = {
        "PATH": SHELL_PATH,
        "PYTHON": sys.executable,
        "QI_PYTHON": str(_stub(tmp_path)),
        "QI_SUBMIT_LEASE_COMMAND": "true",
        "STUB_LOG": str(log),
    }
    command = [
        "sh",
        str(RUNNER),
        "--approval",
        "QUOTE",
        "--submit-replicated-q11",
        "--deadline",
        "600",
        "--stamp",
        stamp,
        "--runs-dir",
        str(runs),
        "--state-dir",
        str(state),
        *extra,
    ]
    done = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    return done, (log.read_text().splitlines() if log.exists() else [])


@pytest.mark.parametrize("mark", [".fabricated", "submission", "results"])
def test_every_analysis_mode_refuses_a_fabricated_run_directory_unless_dry_run_mode_is_explicit(
    tmp_path: Path, mark: str
) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_FINAL)
    # the three marks are independent: strip two and the remaining one still refuses
    for run in runs:
        if mark != ".fabricated":
            (run / ".fabricated").unlink()
        for name in ("submission", "results"):
            if name != mark:
                data = json.loads((run / f"{name}.json").read_text())
                del data["fabricated"]
                (run / f"{name}.json").write_text(json.dumps(data, indent=1))
    for arguments in (["--binding", runs[0]], ["--stage1", *runs], ["--final", *runs, "--out", tmp_path / "f.json"]):
        refused = _strict(*arguments)
        _check(refused.returncode == 1 and "fabricated" in refused.stderr)
        _check(_analysis(*arguments).returncode == 0)


def test_a_run_directory_without_any_mark_enters_the_analysis(tmp_path: Path) -> None:
    runs = _build(tmp_path / "runs", 12, SIGMA_FINAL)
    for run in runs:
        (run / ".fabricated").unlink()
        for name in ("submission", "results"):
            data = json.loads((run / f"{name}.json").read_text())
            del data["fabricated"]
            (run / f"{name}.json").write_text(json.dumps(data, indent=1))
    _check(_strict("--binding", runs[0]).returncode == 0)
    done = _strict("--stage1", *runs)
    _check(done.returncode == 0 and done.stdout.splitlines() == ["verdict: final", "N: 12"])


def test_an_armed_series_refuses_a_fabricated_run_directory_before_any_provider_call(tmp_path: Path) -> None:
    fake = _fake()
    run = tmp_path / "runs" / "T-tuna17-replicated-q11-rep-00"
    shutil.copytree(PROPOSAL / "rep-00", run)
    fake.submit_run(run, "dry-run", 0)  # a fabricated receipt without results: a real collect would read a batch id
    done, stub_calls = _armed(tmp_path, tmp_path / "runs", tmp_path / "state")
    _check(done.returncode != 0 and stub_calls == [])
    _check("fabricated dry-run record" in (tmp_path / "state" / "marker").read_text())


def test_an_armed_series_refuses_a_runs_or_state_directory_that_holds_a_dry_run_marker(tmp_path: Path) -> None:
    for which in ("runs", "state"):
        base = tmp_path / f"stub-{which}"
        base.mkdir()
        dirs = {"runs": tmp_path / "r" / which, "state": tmp_path / "s" / which}
        dirs[which].mkdir(parents=True)
        (dirs[which] / ".dry-run").write_text("")
        done, stub_calls = _armed(base, dirs["runs"], dirs["state"])
        _check(done.returncode == 2 and "dry-run marker" in done.stderr and stub_calls == [])
        _check(not (dirs["state"] / "marker").exists())


@pytest.mark.audit
def test_a_dry_run_leaves_the_directories_an_armed_series_reads_untouched(tmp_path: Path) -> None:
    runs, state = tmp_path / "runs", tmp_path / "state"
    code, calls, _, dry_state = _run(tmp_path)
    _check(code == 0 and calls.count("submit") == 12 and _marker(dry_state) == "done")
    # every dry-run file sits below DIR/dry-run, so a series that reads DIR sees no run directory of it
    _check([p.name for p in runs.iterdir()] == ["dry-run"] and [p.name for p in state.iterdir()] == ["dry-run"])
    _check((runs / "dry-run" / ".dry-run").exists() and (state / "dry-run" / ".dry-run").exists())
    # the same stamp, runs directory and state directory under the armed arguments
    done, stub_calls = _armed(tmp_path, runs, state)
    _check(done.returncode != 0 and not (state / "final.json").exists())
    _check(len(stub_calls) == 1 and " submit " in stub_calls[0] and "rep-00" in stub_calls[0])
    _check(not any("collect" in line for line in stub_calls))
    # the dry-run directories themselves are refused
    done, stub_calls = _armed(tmp_path, runs / "dry-run", tmp_path / "state2")
    _check(done.returncode == 2 and stub_calls == [] and not (state / "final.json").exists())
    done, stub_calls = _armed(tmp_path, tmp_path / "runs2", state / "dry-run")
    _check(done.returncode == 2 and stub_calls == [])


@pytest.mark.audit
def test_a_deadline_that_expires_in_stage_two_leaves_a_counted_marker_and_a_restart_completes(
    tmp_path: Path,
) -> None:
    shim = tmp_path / "shim"
    shim.mkdir()
    skew = tmp_path / "skew"
    clock = shim / "date"
    clock.write_text(
        '#!/bin/sh\nskew=0\n[ -r "$SKEW_FILE" ] && skew=$(cat "$SKEW_FILE")\n'
        'case "$*" in\n*+%s*) echo $(($(/bin/date +%s) + skew)) ;;\n*) exec /bin/date "$@" ;;\nesac\n'
    )
    clock.chmod(0o755)
    env = {
        "PATH": f"{shim}:{SHELL_PATH}",
        "SKEW_FILE": str(skew),
        "FAKE_SIGMA": str(SIGMA_CONTINUE),
        "FAKE_SKEW_REP": "rep-13",
        "FAKE_SKEW_FILE": str(skew),
        "FAKE_SKEW_SECONDS": "100000",
    }
    code, calls, _, state = _run(tmp_path, env)
    _check(code != 0 and calls.count("submit") == 14)
    _check(
        _marker(state).startswith("failed the deadline of 3600 s passed before rep-14")
        and "14 replicates collected of 18" in _marker(state)
    )
    note = (state / "RESUME.md").read_text()
    _check("collected when this note was written: 14" in note and "Stage-2 target N: 18" in note)
    _check("refuses a partial series" in note)
    runs = sorted((tmp_path / "runs" / "dry-run").glob("T-tuna17-replicated-q11-rep-*"))
    _check(len(runs) == 14)
    partial = _analysis("--final", *runs, "--stage1-decision", state / "stage1.json", "--out", tmp_path / "x.json")
    _check(partial.returncode == 1 and "refused" in partial.stderr and not (tmp_path / "x.json").exists())
    # a restart with the same stamp, under a clock that has not skipped, submits only the missing replicates
    skew.unlink()
    (tmp_path / "calls.log").unlink()
    code, calls, _, state = _run(tmp_path, {"SKEW_FILE": str(skew), "FAKE_SIGMA": str(SIGMA_CONTINUE)})
    _check(code == 0 and _marker(state) == "done")
    _check(
        [line for line in calls.splitlines() if line.startswith("submit")]
        == [f"submit rep-{i:02d}" for i in range(14, 18)]
    )
    _check(json.loads((state / "final.json").read_text())["decision"]["n"] == 18)
