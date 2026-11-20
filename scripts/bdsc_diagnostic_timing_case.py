"""Build and run the sim:belenos timing requests P1 and P2 of the b1 completion-time case.

results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos/CASE.md is the written case: six 12-iteration jobs in
the order P1 P2 P2 P1 P1 P2 measure the wall time of two requests drawn from the retained b1 jobs of that tree, whose
24-iteration jobs ran 300 s (b1-j1, completed) and 305 s (b1-j2, canceled at the platform limit).

The requests are subsets of the retained manifests, not a fresh build. P1 keeps the out-s0 and out-s1 settings of
b1-j1 and P2 the rev-s0 and rev-s1 settings of b1-j2, each setting byte for byte (circuit parameters, compilation seed
and draw indices of the 2026-11-14 ANU draw the retained jobs consumed) and in the retained iteration order. A
reproduced seed is an identifier, so the case takes no new QRNG value, and a subset carries no re-solved float that a
platform could change. Each manifest keeps the retained `diagnostic_case_sha256` and `draw`: the draw belongs to that
case record, so bdsc_diagnostic.draw_claims, which refuses a draw that a manifest of another record names, still admits
the retained tree's rebuild; the analyzer's admission refuses a P run because its job is not a job of the diagnostic.
`timing_case_sha256` binds the timing record, `source_job` the retained manifest, and `successor_sources` the files
that plan, submit and collect a P run (qd_platform.load_case refuses a run whose bound file changed).

Subcommands:
- build [--out DIR] writes case.json, p1/ and p2/ (the default DIR is TREE). The manifests bind the digests of
  SOURCES, so a change to one of them needs a rebuild before the plan; once a directory under results/quandela holds
  a submission receipt or checkpoint beside a P manifest, a file whose bytes differ is refused. check [DIR] requires
  the bytes of a fresh build.
- submit RUN --approval TEXT sends RUN through qd_platform.submit with SubmissionGate as its verify step: under the
  token's submit lock it refuses a request other than the next slot's, a token with a running or queued job, a body
  with mitigations, and every stop condition `next` applies. The manifests name this wrapper as submit_wrapper, so
  qd_platform.py submit refuses them without it.
- record RUN [--poll S] reads the job status on a fixed cadence of S seconds (at most 10), appends (UTC time,
  status, progress, progress message) or the transient error to RUN/status-log.jsonl until the job is terminal, then
  collects it through qd_platform.collect.
- next finds every submitted P run under results/quandela, orders them by submission time and prints the request of
  the next slot, or "complete" after the sixth; it exits 1 when a stop condition of the case has fired.
- analyze applies the decision rules of the case to the six runs and prints the reading as JSON.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py build
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py check
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py next
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py submit RUN --approval TEXT
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py record RUN
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py analyze
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

SOURCE_TREE = ROOT / "results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos"
TREE = ROOT / "results/quandela/cases/bdsc_diagnostic_timing_sim_belenos"
RESULTS = ROOT / "results/quandela"
CASE_DOCUMENT = "results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos/CASE.md"
BUILDER = "scripts/bdsc_diagnostic_timing_case.py"
# qd_platform.submit sends a manifest that names this wrapper only through a verify step carrying the same value.
SUBMIT_WRAPPER = f"{BUILDER} submit"
PLATFORM = "sim:belenos"
# request -> (retained job, its groups the request keeps)
REQUESTS: dict[str, tuple[str, tuple[str, ...]]] = {
    "p1": ("b1-j1", ("out-s0", "out-s1")),
    "p2": ("b1-j2", ("rev-s0", "rev-s1")),
}
# Blocks P1 P2, P2 P1, P1 P2: P1 takes slots 1, 4 and 5 and P2 slots 2, 3 and 6.
ORDER = ("p1", "p2", "p2", "p1", "p1", "p2")
STATES = 6
SOURCE_ITERATIONS = 24
EXPECTED_SECONDS = 150.0
PER_JOB_CREDITS = 1.0
MAX_CREDITS_PER_JOB = 1.08
CREDIT_CAP = 6.48
DURATION_CAP = 1800.0
LIMIT_SECONDS = 300.0
NARROW, WIDE = 0.05, 0.10
FIT_SECONDS = 295.0
MAX_POLL = 10.0
STATUS_LOG = "status-log.jsonl"
# The files that build, plan, submit, record and collect a P run; qd_platform imports oq_platform and qd_records.
SOURCES = (
    BUILDER,
    "gororoba_quantum/qd_records.py",
    "scripts/oq_platform.py",
    "scripts/qd_platform.py",
)


class TimingError(Exception):
    """A refused build, submission, schedule or analysis."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TimingError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(value: object) -> bytes:
    return (json.dumps(value, indent=1) + "\n").encode()


def group_of(setting: dict[str, Any]) -> str:
    """The (template, seed slot) group of a setting, the first two fields of its name (out-s0-pi -> out-s0)."""
    return "-".join(str(setting["name"]).split("-")[:2])


def source_digests(root: Path = ROOT) -> dict[str, str]:
    return {name: sha256_bytes((root / name).read_bytes()) for name in SOURCES}


def case_record(source_case: bytes, sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The timing record: requests, slot order, expected seconds and credits, stop conditions and decision rules."""
    return {
        "schema": "bdsc-diagnostic-timing-case-v1",
        "record": "timing_case",
        "case": CASE_DOCUMENT,
        "builder": BUILDER,
        "question": "whether the completion time of the 24-iteration b1 shape varies near the 300 s platform limit "
        "through request cost, service variation, or neither",
        "authorization": "none: the six jobs wait for the owner's approval of the written case",
        "platform": PLATFORM,
        "source_case_sha256": sha256_bytes(source_case),
        "requests": {
            name: {
                "source_job": job,
                "source_cases_sha256": sources[name]["cases_sha256"],
                "groups": list(groups),
                "iterations": sources[name]["iterations"],
            }
            for name, (job, groups) in REQUESTS.items()
        },
        "order": list(ORDER),
        "quantity": "the provider-reported duration of each job, in seconds; wall time from submission to "
        "collection is recorded beside it and not analyzed",
        "resources": {
            "expected_seconds_per_job": EXPECTED_SECONDS,
            "expected_seconds": EXPECTED_SECONDS * len(ORDER),
            "per_job_credits": PER_JOB_CREDITS,
            "max_credits_per_job": MAX_CREDITS_PER_JOB,
            "expected_credits": PER_JOB_CREDITS * len(ORDER),
            "credit_cap": CREDIT_CAP,
            "duration_cap": DURATION_CAP,
        },
        "stop_conditions": [
            "a job ends canceled or failed, or reports a duration at the 300 s limit",
            "a job is submitted before the previous job is collected, or while the token holds a running or queued job",
            "a job body carries a mitigation, or the service reports another platform",
            f"spent credits plus one job's authorization of {MAX_CREDITS_PER_JOB} exceed {CREDIT_CAP}",
            f"the sum of reported durations reaches {DURATION_CAP:g} s before the next submission",
        ],
        "decision": {
            "spread": "s(P) = (max - min) / mean of the three durations of request P",
            "means": "|m1 - m2| / mean(m1, m2) of the replicate means",
            "narrow": NARROW,
            "wide": WIDE,
            "fit_seconds": FIT_SECONDS,
            "deviation": f"a duration above {LIMIT_SECONDS / 2:g} s or below {(1 - WIDE) * LIMIT_SECONDS / 2:g} s "
            "departs from the prediction and is recorded before any rule is applied",
        },
        "recorder": f"{BUILDER} record reads the job status on a fixed {MAX_POLL:g} s cadence into {STATUS_LOG}; a "
        "read that takes longer than the cadence delays the next read, and the log carries each read's own time",
        "submission": SUBMIT_WRAPPER,
    }


def documents(source_tree: Path = SOURCE_TREE, root: Path = ROOT) -> dict[str, Any]:
    """{"case.json": bytes, request: {"cases.json": bytes, "circuit.json": bytes}} of P1 and P2."""
    source_case = (source_tree / "case.json").read_bytes()
    built: dict[str, dict[str, Any]] = {}
    for name, (job, groups) in REQUESTS.items():
        manifest_bytes = (source_tree / job / "cases.json").read_bytes()
        circuit_bytes = (source_tree / job / "circuit.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        require(manifest.get("job") == job, f"{job}: the manifest names job {manifest.get('job')!r}")
        require(manifest.get("platforms") == [PLATFORM], f"{job}: admits {manifest.get('platforms')}")
        require(
            manifest.get("diagnostic_case_sha256") == sha256_bytes(source_case), f"{job}: built from another record"
        )
        require(manifest["circuit"]["sha256"] == sha256_bytes(circuit_bytes), f"{job}: circuit.json differs")
        require(manifest.get("draft") is False and isinstance(manifest.get("draw"), dict), f"{job}: no bound draw")
        require(manifest.get("iterations") == SOURCE_ITERATIONS, f"{job}: {manifest.get('iterations')} iterations")
        settings = manifest["settings"]
        require(len(settings) == SOURCE_ITERATIONS, f"{job}: {len(settings)} settings")
        kept = [setting for setting in settings if group_of(setting) in groups]
        for group in groups:
            names = [s["name"] for s in kept if group_of(s) == group]
            require(len(names) == len(set(names)) == STATES, f"{job}: group {group} holds {names}")
        for key, total in (("max_samples", manifest["max_samples"]), ("max_shots", manifest["max_shots"])):
            require(total % SOURCE_ITERATIONS == 0, f"{job}: {key} {total} is not a per-iteration multiple")
        built[name] = {
            "manifest": manifest,
            "settings": kept,
            "circuit": circuit_bytes,
            "cases_sha256": sha256_bytes(manifest_bytes),
            "iterations": len(kept),
        }
    record_bytes = dump(case_record(source_case, built))
    out: dict[str, Any] = {"case.json": record_bytes}
    for name, (job, _) in REQUESTS.items():
        item = built[name]
        manifest = dict(item["manifest"])
        steps = item["iterations"]
        manifest.update(
            job=name,
            iterations=steps,
            max_samples=manifest["max_samples"] // SOURCE_ITERATIONS * steps,
            max_shots=manifest["max_shots"] // SOURCE_ITERATIONS * steps,
            settings=item["settings"],
            successor_sources=source_digests(root),
            timing_case_sha256=sha256_bytes(record_bytes),
            source_job={"job": job, "cases_sha256": item["cases_sha256"]},
            max_credits=MAX_CREDITS_PER_JOB,
            submit_wrapper=SUBMIT_WRAPPER,
        )
        out[name] = {"cases.json": dump(manifest), "circuit.json": item["circuit"]}
    return out


def files_of(tree: dict[str, Any]) -> dict[str, bytes]:
    flat: dict[str, bytes] = {}
    for name, content in tree.items():
        if isinstance(content, bytes):
            flat[name] = content
        else:
            flat.update({f"{name}/{file}": data for file, data in content.items()})
    return flat


def submitted_runs(results: Path = RESULTS) -> list[str]:
    """Directories under results/quandela that hold a submission receipt or checkpoint beside a cases.json binding a
    timing record: once one exists, the tree keeps its bytes. A staged cases.json alone binds nothing."""
    found = []
    for path in sorted(results.rglob("cases.json")):
        run = path.parent
        sent = (run / "submission.json").is_file() or (run / "submission-state.json").is_file()
        if sent and b'"timing_case_sha256"' in path.read_bytes():
            found.append(str(run.relative_to(results)))
    return found


def write(directory: Path = TREE, results: Path = RESULTS) -> None:
    """Write the tree. Before the first P run it rewrites a file whose bytes differ, since the manifests bind the
    digests of SOURCES and a change to one of them needs a rebuild before the plan; after it, a differing file is
    refused."""
    flat = files_of(documents())
    changed = [
        str(directory / relative)
        for relative, data in flat.items()
        if (directory / relative).exists() and (directory / relative).read_bytes() != data
    ]
    retained = submitted_runs(results)
    require(not (changed and retained), f"runs {retained} bind the tree; retained files differ: {changed}")
    for relative, data in flat.items():
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"bdsc timing: wrote case.json, p1 and p2 under {directory}")


def check(directory: Path = TREE) -> None:
    """The tree equals a fresh build byte for byte and holds nothing else."""
    flat = files_of(documents())
    present = sorted(str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file())
    require(present == sorted(flat), f"tree files differ: {sorted(set(present) ^ set(flat))}")
    for relative, data in flat.items():
        require((directory / relative).read_bytes() == data, f"{relative} differs from a fresh build")
    print(f"bdsc timing: {directory} matches a fresh build")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def instant(text: str) -> datetime.datetime:
    """A recorded UTC stamp as an aware datetime; "Z" and "+00:00" spellings name the same instant."""
    value = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    require(value.tzinfo is not None, f"{text!r} carries no UTC offset")
    return value


def record(run: Path, poll: float = MAX_POLL, timeout: float = 3600.0) -> dict[str, Any]:
    """Read the job status on a fixed cadence of poll seconds (at most MAX_POLL) until it is terminal, then collect.

    Each read starts poll seconds after the previous one started, so the sleep absorbs the read's own latency. A read
    that fails transiently is logged as an error line at its own time and the cadence continues; any other failure
    raises. Every line carries the UTC time the read returned."""
    import qd_platform

    require(0 < poll <= MAX_POLL, f"--poll {poll} is outside (0, {MAX_POLL:g}]")
    _, _, cases_sha256 = qd_platform.load_case(run)
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    require(submission.get("cases_sha256") == cases_sha256, f"{run}: cases.json differs from the submission receipt")
    job = submission["job_id"]
    deadline = time.monotonic() + timeout
    log = run / STATUS_LOG
    tick = time.monotonic()
    while True:
        line: dict[str, Any]
        terminal = False
        try:
            status = qd_platform.request("GET", qd_platform.job_route(job, "status"))
        except qd_platform.PlatformError as error:
            if not qd_platform.transient(error):
                raise
            line = {"utc": utc_now(), "error": str(error)[:200]}
        else:
            line = {
                "utc": utc_now(),
                "status": status.get("status"),
                "progress": status.get("progress"),
                "progress_message": status.get("progress_message"),
            }
            terminal = status.get("status") in qd_platform.TERMINAL
        with log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(line) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if terminal:
            break
        require(time.monotonic() <= deadline, f"job {job} is not terminal after {timeout:g} s")
        tick += poll
        time.sleep(max(0.0, tick - time.monotonic()))
    return qd_platform.collect(run, poll, max(deadline - time.monotonic(), poll))


def request_of(run: Path, tree: Path = TREE) -> str:
    """The request whose committed manifest the run carries byte for byte."""
    data = (run / "cases.json").read_bytes()
    for name in REQUESTS:
        if (tree / name / "cases.json").read_bytes() == data:
            return name
    raise TimingError(f"{run}: cases.json is neither committed request")


def bound_runs(results: Path = RESULTS, tree: Path = TREE) -> list[Path]:
    """Every submitted run under results/quandela that carries a committed request, in submission order.

    A directory that holds only a staged cases.json is not a run; one with a submission checkpoint but no receipt is
    an interrupted submission, which stops the case until qd_platform recover writes its receipt."""
    found: list[tuple[datetime.datetime, Path]] = []
    committed = {(tree / name / "cases.json").read_bytes() for name in REQUESTS}
    for path in sorted(results.rglob("cases.json")):
        run = path.parent
        if run.parent == tree or path.read_bytes() not in committed:
            continue
        receipt, state = run / "submission.json", run / "submission-state.json"
        if not receipt.is_file():
            require(not state.is_file(), f"{run}: interrupted submission; run qd_platform.py recover first")
            continue
        submitted = json.loads(receipt.read_text(encoding="utf-8"))["submitted_utc"]
        found.append((instant(str(submitted)), run))
    return [run for _, run in sorted(found)]


def admitted(runs: list[Path], tree: Path = TREE) -> list[dict[str, Any]]:
    """Each run's facts after the per-job stop conditions of the case, in submission order; raises when one fired."""
    import qd_platform

    require(len(runs) <= len(ORDER), f"{len(runs)} runs; the case has {len(ORDER)} slots")
    facts: list[dict[str, Any]] = []
    previous: datetime.datetime | None = None
    for slot, run in enumerate(runs):
        name = request_of(run, tree)
        require(name == ORDER[slot], f"{run}: slot {slot + 1} runs {ORDER[slot]}, not {name}")
        submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
        require(submission.get("platform") == PLATFORM, f"{run}: submitted to {submission.get('platform')!r}")
        submitted = instant(str(submission["submitted_utc"]))
        require(previous is None or submitted >= previous, f"{run}: submitted before slot {slot} was collected")
        results = run / "results.json"
        require(results.is_file(), f"{run}: not collected")
        collected = json.loads(results.read_text(encoding="utf-8"))
        state = collected["status"]
        require(state.get("status") == "completed", f"{run}: the job ended {state.get('status')}; stop")
        served = collected.get("data", {}).get("platform_name")
        require(served == PLATFORM, f"{run}: the service reports {served!r}")
        body = json.loads((run / "job-body.json").read_text(encoding="utf-8"))
        require(qd_platform.body_mitigations(body) == [], f"{run}: the job body carries mitigations")
        duration = float(state["duration"])
        require(0 < duration < LIMIT_SECONDS, f"{run}: reported duration {duration:g} s reaches the limit; stop")
        previous = instant(str(collected["collected_utc"]))
        facts.append(
            {
                "slot": slot + 1,
                "request": name,
                "run": run.name,
                "duration": duration,
                "charge": float(qd_platform.run_facts(run)["charge"]),
                "submitted_utc": str(submission["submitted_utc"]),
                "collected_utc": str(collected["collected_utc"]),
            }
        )
    return facts


def next_request(runs: list[Path], tree: Path = TREE) -> str:
    """The request of the next slot, or "complete"; raises when a stop condition of the case has fired.

    The caps stop the next submission, so they reserve its budget: the spent credits plus one job's authorization
    must stay within CREDIT_CAP, and the summed reported durations below DURATION_CAP."""
    facts = admitted(runs, tree)
    if len(facts) == len(ORDER):
        return "complete"
    spent = sum(f["charge"] for f in facts)
    seconds = sum(f["duration"] for f in facts)
    require(spent + MAX_CREDITS_PER_JOB <= CREDIT_CAP, f"spent credits {spent:g} leave no room for a job; stop")
    require(seconds < DURATION_CAP, f"reported durations {seconds:g} s reach {DURATION_CAP:g} s; stop")
    return ORDER[len(facts)]


class SubmissionGate:
    """The verify step of qd_platform.submit for one run: the slot, the idle token and the empty mitigation list.

    It runs under the token's submit lock, after the plan whose body is posted, so the runs it reads and the counters
    it checks are the ones the submission sees."""

    submit_wrapper = SUBMIT_WRAPPER

    def __init__(self, run: Path, results: Path = RESULTS, tree: Path = TREE) -> None:
        self.run, self.results, self.tree = run, results, tree

    def __call__(self, checked: dict[str, Any]) -> None:
        import qd_platform

        name = request_of(self.run, self.tree)
        expected = next_request(bound_runs(self.results, self.tree), self.tree)
        if expected != name:
            raise qd_platform.PlatformError(f"the next slot runs {expected}, not {name}")
        counters = checked["availability_at_plan"]
        if counters.get("num_concurrent_jobs") or counters.get("num_jobs_in_queue"):
            raise qd_platform.PlatformError(f"the token has a running or queued job: {counters}")
        if qd_platform.body_mitigations(checked["body"]) != []:
            raise qd_platform.PlatformError("the job body carries mitigations")


def submit(run: Path, approval: str) -> dict[str, Any]:
    import qd_platform

    gate = SubmissionGate(run)
    return qd_platform.submit(
        run, PLATFORM, approval, MAX_CREDITS_PER_JOB, EXPECTED_SECONDS, PER_JOB_CREDITS, verify=gate
    )


def spread(values: list[Fraction]) -> Fraction:
    return (max(values) - min(values)) / (sum(values, Fraction(0)) / len(values))


def decide(durations: dict[str, list[float]]) -> dict[str, Any]:
    """The decision row of the case for three durations of each request, in exact rational arithmetic, so a ratio
    that equals a threshold falls on the side the case names."""
    for name in REQUESTS:
        require(len(durations[name]) == ORDER.count(name), f"{name}: {len(durations[name])} durations")
        require(all(d > 0 for d in durations[name]), f"{name}: a duration is not positive")
    exact = {name: [Fraction(d) for d in durations[name]] for name in REQUESTS}
    # NARROW and WIDE as exact ratios: Fraction(0.05) is the binary64 neighbor of 1/20, not 1/20.
    narrow, wide, fit = Fraction(5, 100), Fraction(10, 100), Fraction(FIT_SECONDS)
    s1, s2 = spread(exact["p1"]), spread(exact["p2"])
    m1, m2 = sum(exact["p1"], Fraction(0)) / 3, sum(exact["p2"], Fraction(0)) / 3
    means = abs(m1 - m2) / ((m1 + m2) / 2)
    mean = (m1 + m2) / 2
    if s1 > wide or s2 > wide:
        reading = "service-variation"
    elif s1 <= narrow and s2 <= narrow and means > wide:
        reading = "request-cost"
    elif s1 <= narrow and s2 <= narrow and means <= narrow:
        reading = "doubled-above-fit" if 2 * mean > fit else "doubled-within-fit"
    else:
        reading = "inconclusive"
    values = {"s_p1": s1, "s_p2": s2, "m_p1": m1, "m_p2": m2, "means": means, "mean": mean}
    return {**{key: float(value) for key, value in values.items()}, "reading": reading}


def analyze(runs: list[Path], tree: Path = TREE) -> dict[str, Any]:
    """The reading of the six runs. The caps gate a further submission only, so the sixth run is read whatever they
    hold; the per-job stop conditions still apply."""
    facts = admitted(runs, tree)
    require(len(facts) == len(ORDER), f"the analysis needs {len(ORDER)} runs, not {len(facts)}")
    durations = {name: [f["duration"] for f in facts if f["request"] == name] for name in REQUESTS}
    low, high = (1 - WIDE) * LIMIT_SECONDS / 2, LIMIT_SECONDS / 2
    deviations = [f["run"] for f in facts if not low <= f["duration"] <= high]
    totals = {"credits": sum(f["charge"] for f in facts), "seconds": sum(f["duration"] for f in facts)}
    return {"runs": facts, "totals": totals, "deviations_from_prediction": deviations, **decide(durations)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--out", type=Path, default=TREE)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("directory", type=Path, nargs="?", default=TREE)
    submit_parser = commands.add_parser("submit")
    submit_parser.add_argument("run", type=Path)
    submit_parser.add_argument("--approval", required=True)
    record_parser = commands.add_parser("record")
    record_parser.add_argument("run", type=Path)
    record_parser.add_argument("--poll", type=float, default=MAX_POLL)
    record_parser.add_argument("--timeout", type=float, default=3600.0)
    commands.add_parser("next")
    commands.add_parser("analyze")
    args = parser.parse_args()
    try:
        if args.command == "build":
            write(args.out)
            check(args.out)
        elif args.command == "check":
            check(args.directory)
        elif args.command == "submit":
            print(json.dumps(submit(args.run, args.approval)["job_id"]))
        elif args.command == "record":
            print(json.dumps(record(args.run, args.poll, args.timeout)["status"], indent=1))
        elif args.command == "next":
            print(next_request(bound_runs()))
        else:
            print(json.dumps(analyze(bound_runs()), indent=1))
    except TimingError as error:
        print(f"bdsc timing: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
