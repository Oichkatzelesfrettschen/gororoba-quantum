"""Unattended submission of approved Quandela jobs from a committed schedule.

A schedule, results/quandela/schedules/NAME.json, lists the jobs one written
case approved, in order: each job's frozen case directory with the sha256 of
its cases.json and circuit.json, the sha256 of the request body a pinned plan
built (body_sha256, the body without Perceval's random process_id), the
earliest UTC start, an optional minimum gap after an earlier job's provider
execution end, the case's credit and seconds ceilings, the platform statuses
it admits, and the case's own plan-check and matched-check commands. The
user's approval text travels in the schedule and reaches submission.json
unchanged, so a merged schedule on main is the approval and a workflow input
never is. .github/workflows/quandela-schedule.yml runs step on a timer; the
procedure and its boundaries are in docs/runbooks/quandela-scheduled-runs.md.

The scheduler's state lives beside the schedule in results/quandela/schedules/NAME/:

- KEY.intent.json names the run directory and the workflow run that prepared
  it. It is pushed before submit runs, so a run that dies after the push
  leaves an intent whose workflow run differs from the next one, and that job
  reads interrupted: a person checks the provider's job list, because the
  request may or may not have been posted.
- KEY.hold.json records a stop condition before anything was sent (a plan
  refusal, a changed body, a failed plan check, a submit refused before its
  checkpoint); the prepared run directory is removed, since every directory
  under results/quandela/runs/ is one sent job to scripts/research_state.py.
- KEY.receipt.json records the matched check and the after-job snapshot of a
  collected run; outcome failed stops the schedule.

Jobs run strictly in order, one per step: a held, failed or interrupted job
stops every later one. A due job waits, staging nothing, while the platform
reads a status the job does not admit or the token has a running or queued
job; a job past its optional latest_start holds.

Subcommands:

- check [SCHEDULE ...] (offline) validates every schedule (default: all under
  results/quandela/schedules/): schema, unique keys and run names, earlier-job
  references, ceilings within max_total_credits, input digests equal to the
  tree, check commands that name an existing script under scripts/ with only
  the {plan} and {run} placeholders, snapshot directories under
  results/quandela/, and on every job of an enabled schedule a pinned
  body_sha256 and a run_name no run directory carries without an intent.
- list prints the enabled schedules, one path per line.
- status SCHEDULE (offline) prints each job's state.
- pin SCHEDULE (network, read-only) plans every job and writes its body_sha256.
- step SCHEDULE --run-id ID --deadline EPOCH --work DIR [--plan-only] (network)
  performs the next action and prints one JSON line whose outcome is continue
  or prepared (commit, push and step again) or wait, idle, done or stop (commit
  and end the tick). --plan-only plans the next job in a scratch copy, compares
  its body digest and runs its plan check, and writes nothing to the tree.
- sync SCHEDULE --source ROOT --target ROOT copies the schedule's state
  directory, every run directory an intent names and every snapshot
  directory from one checkout to another.

Usage: "$PYTHON" scripts/qd_schedule.py (check [SCHEDULE ...] | list | status SCHEDULE)
       QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/qd_schedule.py (pin SCHEDULE | step SCHEDULE ...)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]

import qd_platform as qd  # noqa: E402

SCHEDULES = ROOT / "results/quandela/schedules"
RUNS = ROOT / "results/quandela/runs"
CASES = ROOT / "results/quandela/cases"
SCHEMA = "qd-schedule-v1"
INTENT_SCHEMA = "qd-schedule-intent-v1"
HOLD_SCHEMA = "qd-schedule-hold-v1"
RECEIPT_SCHEMA = "qd-schedule-receipt-v1"
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
DIGEST = re.compile(r"[0-9a-f]{64}")
UTC = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
RUN = re.compile(r"\d{4}-\d\d-\d\dT\d{6}Z-(.+)")
INPUTS = ("cases.json", "circuit.json")
PLACEHOLDERS = ("{plan}", "{run}")
# A tick ends its collection this many seconds before the job's deadline, so
# the commit and push of a finished collection fit inside the hosted runner.
COLLECT_MARGIN = 600.0
TAIL = 2000


class ScheduleError(Exception):
    pass


def require(condition: object, message: str) -> None:
    if not condition:
        raise ScheduleError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body_digest(body: dict[str, Any]) -> str:
    """The request body's sha256 without process_id, the one field Perceval draws afresh for every job."""
    fixed = {key: value for key, value in body.items() if key != "process_id"}
    return hashlib.sha256(json.dumps(fixed, sort_keys=True).encode()).hexdigest()


def utc(text: str) -> float:
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.UTC).timestamp()


def stamp(epoch: float) -> str:
    return datetime.datetime.fromtimestamp(epoch, datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def finite(value: Any, name: str) -> None:
    require(
        isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value) and value >= 0,
        f"{name} {value!r} is not a finite, non-negative number",
    )


def inside(root: Path, relative: str, name: str) -> Path:
    require(isinstance(relative, str) and not Path(relative).is_absolute(), f"{name} must be a relative path")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(root), f"{name} {relative} lies outside {root.relative_to(ROOT)}")
    return path


def check_command(argv: Any, placeholder: str, name: str) -> None:
    require(isinstance(argv, list) and argv and all(isinstance(a, str) for a in argv), f"{name} must be an argv list")
    script = inside(ROOT / "scripts", argv[0], name)
    require(script.suffix == ".py" and script.is_file(), f"{name} names {argv[0]}, not an existing script")
    used = [a for a in argv if "{" in a or "}" in a]
    require(all(a == placeholder for a in used), f"{name} admits only the placeholder {placeholder}")


def load(path: Path) -> dict[str, Any]:
    """The schedule at path, after every offline check."""
    schedule = read(path)
    require(isinstance(schedule, dict) and schedule.get("schema") == SCHEMA, f"{path.name} is not a {SCHEMA}")
    name = schedule.get("name")
    require(isinstance(name, str) and NAME.fullmatch(name) is not None, f"{path.name}: name {name!r}")
    require(path.name == f"{name}.json", f"{path.name} must be named {name}.json")
    require(isinstance(schedule.get("enabled"), bool), f"{name}: enabled must be true or false")
    require(isinstance(schedule.get("approval"), str) and schedule["approval"].strip(), f"{name}: approval is empty")
    require((ROOT / str(schedule.get("case", ""))).is_file(), f"{name}: case {schedule.get('case')!r} is not a file")
    require(isinstance(schedule.get("platform"), str) and schedule["platform"], f"{name}: platform is empty")
    finite(schedule.get("max_total_credits"), f"{name}: max_total_credits")
    jobs = schedule.get("jobs")
    require(isinstance(jobs, list) and jobs, f"{name}: jobs must be a nonempty list")
    keys: list[str] = []
    runs: set[str] = set()
    for job in jobs:
        key = job.get("key")
        require(isinstance(key, str) and KEY.fullmatch(key) is not None, f"{name}: job key {key!r}")
        require(key not in keys, f"{name}: job key {key} repeats")
        where = f"{name}/{key}"
        run_name = job.get("run_name")
        require(isinstance(run_name, str) and KEY.fullmatch(run_name) is not None, f"{where}: run_name {run_name!r}")
        require(run_name not in runs, f"{where}: run_name {run_name} repeats")
        case_dir = inside(CASES, job.get("case_dir"), f"{where}: case_dir")
        digests = job.get("inputs_sha256")
        require(isinstance(digests, dict) and sorted(digests) == sorted(INPUTS), f"{where}: inputs_sha256 keys")
        for file in INPUTS:
            require((case_dir / file).is_file(), f"{where}: {job['case_dir']}/{file} is missing")
            require(sha256_file(case_dir / file) == digests[file], f"{where}: {file} differs from inputs_sha256")
        pinned = job.get("body_sha256")
        require(pinned is None or (isinstance(pinned, str) and DIGEST.fullmatch(pinned) is not None), f"{where}: body")
        require(pinned is not None or not schedule["enabled"], f"{where}: an enabled schedule needs body_sha256")
        require(isinstance(job.get("not_before"), str) and UTC.fullmatch(job["not_before"]), f"{where}: not_before")
        latest = job.get("latest_start")
        require(latest is None or (isinstance(latest, str) and UTC.fullmatch(latest)), f"{where}: latest_start")
        if schedule["enabled"] and not (SCHEDULES / name / f"{key}.intent.json").exists():
            present = named_runs(RUNS, run_name)
            require(
                not present, f"{where}: {present[0].name if present else ''} carries the run_name without an intent"
            )
        after = job.get("after")
        if after is not None:
            require(isinstance(after, dict) and after.get("key") in keys, f"{where}: after must name an earlier job")
            finite(after.get("min_gap_seconds"), f"{where}: min_gap_seconds")
        for field in ("max_credits", "expected_seconds", "per_job_credits"):
            finite(job.get(field), f"{where}: {field}")
        statuses = job.get("admit_statuses")
        require(isinstance(statuses, list) and all(isinstance(s, str) for s in statuses), f"{where}: admit_statuses")
        check_command(job.get("plan_check"), "{plan}", f"{where}: plan_check")
        check_command(job.get("matched_check"), "{run}", f"{where}: matched_check")
        if job.get("snapshot_out") is not None:
            inside(ROOT / "results/quandela", job["snapshot_out"], f"{where}: snapshot_out")
        keys.append(key)
        runs.add(run_name)
    total = sum(job["max_credits"] for job in jobs)
    require(
        total <= schedule["max_total_credits"],
        f"{name}: job ceilings {total:g} exceed {schedule['max_total_credits']:g}",
    )
    return schedule


def state_dir(schedule: dict[str, Any], root: Path | None = None) -> Path:
    return (root or ROOT) / SCHEDULES.relative_to(ROOT) / schedule["name"]


def named_runs(runs: Path, run_name: str) -> list[Path]:
    if not runs.is_dir():
        return []
    return [p for p in sorted(runs.iterdir()) if p.is_dir() and (m := RUN.fullmatch(p.name)) and m[1] == run_name]


def intent_run(schedule: dict[str, Any], job: dict[str, Any], path: Path) -> str:
    """The run directory name an intent on the data branch names, refused unless it is this job's own.

    The data branch is written by every tick and readable by anyone who can
    push to it, so a name outside results/quandela/runs/ would let sync copy
    branch content over the code a later step runs with the token.
    """
    intent = read(path)
    run = intent.get("run") if isinstance(intent, dict) else None
    match = RUN.fullmatch(run) if isinstance(run, str) else None
    require(
        intent.get("schema") == INTENT_SCHEMA
        and intent.get("schedule") == schedule["name"]
        and intent.get("key") == job["key"]
        and match is not None
        and match[1] == job["run_name"]
        and isinstance(intent.get("run_id"), str),
        f"{path.name} does not name a run of {schedule['name']}/{job['key']}",
    )
    return str(run)


def job_state(
    schedule: dict[str, Any], job: dict[str, Any], run_id: str, root: Path | None = None
) -> tuple[str, Path | None]:
    """The job's state and its run directory, read from the scheduler's files and the run's own records."""
    states = state_dir(schedule, root)
    runs = (root or ROOT) / RUNS.relative_to(ROOT)
    if (states / f"{job['key']}.hold.json").exists():
        return "held", None
    intent_path = states / f"{job['key']}.intent.json"
    if not intent_path.exists():
        present = named_runs(runs, job["run_name"])
        return ("foreign", present[0]) if present else ("pending", None)
    run = runs / intent_run(schedule, job, intent_path)
    receipt_path = states / f"{job['key']}.receipt.json"
    if receipt_path.exists():
        outcome = read(receipt_path).get("outcome")
        require(outcome in ("passed", "failed"), f"{receipt_path.name}: outcome {outcome!r}")
        return str(outcome), run
    if not run.is_dir():
        return "interrupted", run
    if (run / "results.json").exists():
        return "collected", run
    if (run / "submission.json").exists():
        return "submitted", run
    if (run / "submission-state.json").exists():
        return ("posted" if read(run / "submission-state.json").get("phase") == "posted" else "interrupted"), run
    if (run / "job-body.json").exists() or read(intent_path)["run_id"] != run_id:
        return "interrupted", run
    return "prepared", run


def execution_end(run: Path) -> float:
    status = read(run / "results.json")["status"]
    return float(status["start_time"]) + float(status["duration"])


def due_time(schedule: dict[str, Any], job: dict[str, Any], root: Path | None = None) -> float:
    """The earliest start: not_before, and the provider's execution end of the named earlier job plus its gap."""
    start = utc(job["not_before"])
    after = job.get("after")
    if after is not None:
        earlier = next(j for j in schedule["jobs"] if j["key"] == after["key"])
        _, run = job_state(schedule, earlier, "", root)
        if run is None:
            raise ScheduleError(f"{job['key']}: {after['key']} has no run directory")
        start = max(start, execution_end(run) + after["min_gap_seconds"])
    return start


def run_check(argv: list[str], value: Path) -> tuple[int, str]:
    """A case check from the schedule, run from the checkout with this interpreter."""
    # The plan lies in the runner's scratch directory outside the checkout; the run lies inside it.
    args = [str(value) if a == "{plan}" else str(value.relative_to(ROOT)) if a == "{run}" else a for a in argv]
    done = subprocess.run(
        [sys.executable, "-B", str(ROOT / argv[0]), *args[1:]],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return done.returncode, (done.stdout + done.stderr)[-TAIL:]


def plan_record(checked: dict[str, Any]) -> dict[str, Any]:
    """The plan as qd_platform.py plan prints it, the form every --plan-check reads."""
    return {key: value for key, value in checked.items() if key != "body"}


def planned(schedule: dict[str, Any], job: dict[str, Any], case_dir: Path, work: Path) -> dict[str, Any]:
    """Plan the job in case_dir, compare its body digest and run its plan check; raises on the first stop."""
    checked = qd.plan(
        case_dir,
        schedule["platform"],
        job["max_credits"],
        job["expected_seconds"],
        job["per_job_credits"],
        tuple(job["admit_statuses"]),
    )
    digest = body_digest(checked["body"])
    plan_path = work / f"{job['key']}-plan.json"
    write(plan_path, plan_record(checked))
    code, output = run_check(job["plan_check"], plan_path)
    return {"body_sha256": digest, "plan_check_code": code, "plan_check_output": output}


def hold(schedule: dict[str, Any], job: dict[str, Any], run_id: str, stage: str, reason: str) -> dict[str, Any]:
    record = {
        "schema": HOLD_SCHEMA,
        "schedule": schedule["name"],
        "key": job["key"],
        "run_id": run_id,
        "stage": stage,
        "reason": reason[-TAIL:],
        "held_utc": qd.now(),
    }
    write(state_dir(schedule) / f"{job['key']}.hold.json", record)
    return {"outcome": "stop", "key": job["key"], "state": "held", "stage": stage, "reason": reason[-TAIL:]}


def not_ready(schedule: dict[str, Any], job: dict[str, Any]) -> str:
    """Why the platform or the token cannot take the job now, or empty; a passing condition, never a hold.

    A platform in calibration or a token busy with another job is a reason to
    wait, while a plan refusal after these reads is a stop condition of the case.
    """
    statuses = ("available", *job["admit_statuses"])
    platform = schedule["platform"]
    explorer = qd.explorer_row(platform)["status"]
    if explorer not in statuses:
        return f"{platform} is {explorer}"
    processor = qd.get(qd.platform_route(platform)).get("status")
    if processor not in statuses:
        return f"{platform} processor is {processor}"
    counters = qd.availability()
    if counters["num_concurrent_jobs"] or counters["num_jobs_in_queue"]:
        return f"the token has a running or queued job: {counters}"
    return ""


def prepare(schedule: dict[str, Any], job: dict[str, Any], run_id: str, work: Path, now: float) -> dict[str, Any]:
    """Stage the run directory, plan it, require the pinned body and the plan check, then write the intent."""
    run = RUNS / f"{stamp(now)}-{job['run_name']}"
    require(not run.exists(), f"{run.relative_to(ROOT)} exists")
    run.mkdir(parents=True)
    for file in INPUTS:
        shutil.copyfile(ROOT / job["case_dir"] / file, run / file)
        require(sha256_file(run / file) == job["inputs_sha256"][file], f"{job['key']}: {file} changed while copied")
    stage, reason = "plan", ""
    try:
        result = planned(schedule, job, run, work)
        if result["body_sha256"] != job["body_sha256"]:
            stage, reason = "body", f"plan body {result['body_sha256']} differs from the pinned {job['body_sha256']}"
        elif result["plan_check_code"] != 0:
            stage, reason = "plan_check", result["plan_check_output"]
    except qd.PlatformError as error:
        reason = str(error)
    if reason:
        shutil.rmtree(run)
        return hold(schedule, job, run_id, stage, reason)
    intent = {
        "schema": INTENT_SCHEMA,
        "schedule": schedule["name"],
        "key": job["key"],
        "run": run.name,
        "run_id": run_id,
        "prepared_utc": qd.now(),
    }
    write(state_dir(schedule) / f"{job['key']}.intent.json", intent)
    return {"outcome": "prepared", "key": job["key"], "run": run.name}


def send(schedule: dict[str, Any], job: dict[str, Any], run: Path, run_id: str) -> dict[str, Any]:
    """Submit a run this workflow run prepared; a refusal before the checkpoint is a hold."""
    try:
        record = qd.submit(
            run,
            schedule["platform"],
            schedule["approval"],
            job["max_credits"],
            job["expected_seconds"],
            job["per_job_credits"],
            tuple(job["admit_statuses"]),
        )
    except qd.PlatformError as error:
        if any((run / name).exists() for name in ("job-body.json", "submission-state.json")):
            return {"outcome": "stop", "key": job["key"], "state": "interrupted", "reason": str(error)[-TAIL:]}
        # The intent stays, so sync removes the pushed run directory from the results branch too.
        shutil.rmtree(run)
        return hold(schedule, job, run_id, "submit", str(error))
    return {"outcome": "continue", "key": job["key"], "job_id": record["job_id"]}


def post(schedule: dict[str, Any], job: dict[str, Any], run: Path, run_id: str) -> dict[str, Any]:
    """Run the matched check and the after-job snapshot of a collected run and write its receipt."""
    code, output = run_check(job["matched_check"], run)
    snapshot: str | None = None
    if code == 0 and job.get("snapshot_out") is not None:
        try:
            qd.snapshot(ROOT / job["snapshot_out"])
            snapshot = job["snapshot_out"]
        except qd.PlatformError as error:
            code, output = 1, f"snapshot: {error}"
    outcome = "passed" if code == 0 else "failed"
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "schedule": schedule["name"],
        "key": job["key"],
        "run": run.name,
        "run_id": run_id,
        "outcome": outcome,
        "matched_check_code": code,
        "matched_check_output": output,
        "snapshot": snapshot,
        "received_utc": qd.now(),
    }
    write(state_dir(schedule) / f"{job['key']}.receipt.json", receipt)
    return {"outcome": "continue" if outcome == "passed" else "stop", "key": job["key"], "state": outcome}


def step(
    schedule: dict[str, Any],
    run_id: str,
    deadline: float,
    work: Path,
    plan_only: bool = False,
    clock: Callable[[], float] = time.time,
) -> dict[str, Any]:
    """Perform the next action of the schedule's first unfinished job."""
    if not schedule["enabled"] and not plan_only:
        return {"outcome": "stop", "reason": f"{schedule['name']} is disabled"}
    for job in schedule["jobs"]:
        state, run = job_state(schedule, job, run_id)
        if state == "passed":
            continue
        if state in ("held", "failed", "interrupted", "foreign"):
            where = run.name if run is not None else None
            return {"outcome": "stop", "key": job["key"], "state": state, "run": where}
        if plan_only:
            if state != "pending":
                return {"outcome": "idle", "key": job["key"], "state": state}
            scratch = work / "plan-only" / job["run_name"]
            scratch.mkdir(parents=True, exist_ok=True)
            for file in INPUTS:
                shutil.copyfile(ROOT / job["case_dir"] / file, scratch / file)
            result = planned(schedule, job, scratch, work)
            return {"outcome": "planned", "key": job["key"], "pinned": job["body_sha256"], **result}
        if run is not None and state == "posted":
            qd.recover(run)
            return {"outcome": "continue", "key": job["key"], "state": "submitted"}
        if run is not None and state == "submitted":
            try:
                qd.collect(run, 10.0, max(60.0, deadline - clock() - COLLECT_MARGIN))
            except qd.PlatformError as error:
                return {"outcome": "wait", "key": job["key"], "state": state, "reason": str(error)[-TAIL:]}
            return {"outcome": "continue", "key": job["key"], "state": "collected"}
        if run is not None and state == "collected":
            return post(schedule, job, run, run_id)
        if run is not None and state == "prepared":
            return send(schedule, job, run, run_id)
        start = due_time(schedule, job)
        latest = job.get("latest_start")
        if latest is not None and clock() > utc(latest):
            return hold(schedule, job, run_id, "latest_start", f"no start before {latest}")
        if clock() < start:
            when = datetime.datetime.fromtimestamp(start, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            return {"outcome": "wait", "key": job["key"], "state": state, "not_before": when}
        busy = not_ready(schedule, job)
        if busy:
            return {"outcome": "wait", "key": job["key"], "state": state, "reason": busy}
        return prepare(schedule, job, run_id, work, clock())
    return {"outcome": "done"}


def sync(schedule: dict[str, Any], source: Path, target: Path) -> list[str]:
    """Copy the schedule's state, its intents' run directories and its snapshots from source to target."""
    states = state_dir(schedule, source)
    paths = [states.relative_to(source)] if states.is_dir() else []
    for job in schedule["jobs"]:
        intent = states / f"{job['key']}.intent.json"
        if intent.exists():
            paths.append(RUNS.relative_to(ROOT) / intent_run(schedule, job, intent))
        if job.get("snapshot_out") is not None:
            paths.append(Path(job["snapshot_out"]))
    copied = []
    for relative in paths:
        if (source / relative).is_dir():
            links = [p for p in (source / relative).rglob("*") if p.is_symlink()]
            require(not links and not (source / relative).is_symlink(), f"{relative} carries a symbolic link")
            shutil.copytree(source / relative, target / relative, dirs_exist_ok=True)
            copied.append(str(relative))
        elif (target / relative).is_dir():
            # A held job's run directory carries no sent job, and every directory under runs/ must.
            shutil.rmtree(target / relative)
            copied.append(f"removed {relative}")
    return copied


def pin(path: Path, work: Path) -> dict[str, str]:
    """Plan every job read-only and write its body digest into the schedule."""
    schedule = load(path)
    pinned = {}
    for job in schedule["jobs"]:
        scratch = work / "pin" / job["run_name"]
        scratch.mkdir(parents=True, exist_ok=True)
        for file in INPUTS:
            shutil.copyfile(ROOT / job["case_dir"] / file, scratch / file)
        result = planned(schedule, job, scratch, work)
        require(result["plan_check_code"] == 0, f"{job['key']}: plan check failed\n{result['plan_check_output']}")
        job["body_sha256"] = pinned[job["key"]] = result["body_sha256"]
    write(path, schedule)
    return pinned


def all_schedules() -> list[Path]:
    return sorted(SCHEDULES.glob("*.json")) if SCHEDULES.is_dir() else []


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check")
    p.add_argument("schedules", type=Path, nargs="*")
    sub.add_parser("list")
    for name in ("status", "pin", "step", "sync"):
        p = sub.add_parser(name)
        p.add_argument("schedule", type=Path)
        if name in ("pin", "step"):
            p.add_argument("--work", type=Path, required=True, help="scratch directory for plans")
        if name == "step":
            p.add_argument("--run-id", required=True, help="the workflow run id and attempt")
            p.add_argument("--deadline", type=float, required=True, help="UTC epoch seconds the tick must end by")
            p.add_argument("--plan-only", action="store_true")
        if name == "sync":
            p.add_argument("--source", type=Path, required=True)
            p.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            for path in args.schedules or all_schedules():
                schedule = load(path.resolve())
                print(f"{schedule['name']}: {len(schedule['jobs'])} jobs, enabled {str(schedule['enabled']).lower()}")
        elif args.command == "list":
            for path in all_schedules():
                if load(path)["enabled"]:
                    print(path.relative_to(ROOT))
        elif args.command == "status":
            schedule = load(args.schedule.resolve())
            for job in schedule["jobs"]:
                state, run = job_state(schedule, job, "")
                print(job["key"], state, run.name if run is not None else "-")
        elif args.command == "pin":
            for key, digest in pin(args.schedule.resolve(), args.work).items():
                print(key, digest)
        elif args.command == "step":
            outcome = step(load(args.schedule.resolve()), args.run_id, args.deadline, args.work, args.plan_only)
            print(json.dumps(outcome, sort_keys=True))
        else:
            for copied in sync(load(args.schedule.resolve()), args.source.resolve(), args.target.resolve()):
                print(copied)
    except (ScheduleError, qd.PlatformError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    sys.exit(main())
