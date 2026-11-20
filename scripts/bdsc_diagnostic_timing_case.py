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
  SOURCES, so a change to one of them needs a rebuild before the plan; once a run under results/quandela/runs carries
  a P manifest, a file whose bytes differ is refused. check [DIR] requires the bytes of a fresh build.
- record RUN [--poll S] polls the submitted job's status every S seconds (at most 10) and appends (UTC time, status,
  progress, progress message) to RUN/status-log.jsonl until the job is terminal, then collects it through
  qd_platform.collect.
- next RUN... reads the runs submitted so far, in submission order, and prints the request of the next slot, or
  "complete" after the sixth; it refuses (exit 1) when a stop condition of the case has fired.
- analyze RUN... applies the decision rules of the case to the six collected runs and prints the reading as JSON.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py build
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py check
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py record RUN
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py next [RUN...]
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py analyze RUN RUN RUN RUN RUN RUN
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

SOURCE_TREE = ROOT / "results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos"
TREE = ROOT / "results/quandela/cases/bdsc_diagnostic_timing_sim_belenos"
RUNS = ROOT / "results/quandela/runs"
CASE_DOCUMENT = "results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos/CASE.md"
BUILDER = "scripts/bdsc_diagnostic_timing_case.py"
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
    """A refused build, schedule or analysis."""


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
            "a job ends canceled or failed",
            "a job is submitted before the previous job is collected",
            f"spent credits reach {CREDIT_CAP}",
            f"the sum of reported durations reaches {DURATION_CAP} s",
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
        "recorder": f"{BUILDER} record polls the job status every {MAX_POLL:g} s at most into {STATUS_LOG}",
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


def submitted_runs(runs: Path = RUNS) -> list[str]:
    """Run directories whose cases.json binds a timing record: once one exists, the tree keeps its bytes."""
    return sorted(
        str(path.parent.relative_to(runs))
        for path in runs.glob("*/cases.json")
        if b'"timing_case_sha256"' in path.read_bytes()
    )


def write(directory: Path = TREE, runs: Path = RUNS) -> None:
    """Write the tree. Before the first P run it rewrites a file whose bytes differ, since the manifests bind the
    digests of SOURCES and a change to one of them needs a rebuild before the plan; after it, a differing file is
    refused."""
    flat = files_of(documents())
    changed = [
        str(directory / relative)
        for relative, data in flat.items()
        if (directory / relative).exists() and (directory / relative).read_bytes() != data
    ]
    retained = submitted_runs(runs)
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


def record(run: Path, poll: float = MAX_POLL, timeout: float = 3600.0) -> dict[str, Any]:
    """Log the job status at most every MAX_POLL seconds until it is terminal, then collect the run."""
    import qd_platform

    require(0 < poll <= MAX_POLL, f"--poll {poll} is outside (0, {MAX_POLL:g}]")
    qd_platform.load_case(run)
    job = json.loads((run / "submission.json").read_text(encoding="utf-8"))["job_id"]
    deadline = time.monotonic() + timeout
    log = run / STATUS_LOG
    while True:
        status: dict[str, Any] = qd_platform.patient(
            lambda: qd_platform.request("GET", qd_platform.job_route(job, "status")), job, "status", deadline, poll
        )
        line = {
            "utc": utc_now(),
            "status": status.get("status"),
            "progress": status.get("progress"),
            "progress_message": status.get("progress_message"),
        }
        with log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(line) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if status.get("status") in qd_platform.TERMINAL:
            break
        require(time.monotonic() <= deadline, f"job {job} is still {status.get('status')}")
        time.sleep(poll)
    return qd_platform.collect(run, poll, timeout)


def request_of(run: Path, tree: Path = TREE) -> str:
    """The request whose committed manifest the run carries byte for byte."""
    data = (run / "cases.json").read_bytes()
    for name in REQUESTS:
        if (tree / name / "cases.json").read_bytes() == data:
            return name
    raise TimingError(f"{run}: cases.json is neither committed request")


def schedule(runs: list[Path], tree: Path = TREE) -> list[dict[str, Any]]:
    """Each run's facts after the stop conditions, in submission order; raises when a condition has fired."""
    import qd_platform

    require(len(runs) <= len(ORDER), f"{len(runs)} runs; the case has {len(ORDER)} slots")
    facts: list[dict[str, Any]] = []
    previous_collected = ""
    for slot, run in enumerate(runs):
        name = request_of(run, tree)
        require(name == ORDER[slot], f"{run}: slot {slot + 1} runs {ORDER[slot]}, not {name}")
        submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
        require(submission.get("platform") == PLATFORM, f"{run}: submitted to {submission.get('platform')!r}")
        submitted = str(submission["submitted_utc"])
        require(submitted > previous_collected, f"{run}: submitted before slot {slot} was collected")
        results = run / "results.json"
        require(results.is_file(), f"{run}: not collected")
        collected = json.loads(results.read_text(encoding="utf-8"))
        state = collected["status"]
        require(state.get("status") == "completed", f"{run}: the job ended {state.get('status')}; stop")
        previous_collected = str(collected["collected_utc"])
        facts.append(
            {
                "slot": slot + 1,
                "request": name,
                "run": run.name,
                "duration": float(state["duration"]),
                "charge": float(qd_platform.run_facts(run)["charge"]),
                "submitted_utc": submitted,
                "collected_utc": previous_collected,
            }
        )
    spent = sum(f["charge"] for f in facts)
    seconds = sum(f["duration"] for f in facts)
    require(spent < CREDIT_CAP, f"spent credits {spent:g} reach the cap {CREDIT_CAP}; stop")
    require(seconds < DURATION_CAP, f"reported durations {seconds:g} s reach {DURATION_CAP:g} s; stop")
    return facts


def spread(values: list[float]) -> float:
    return (max(values) - min(values)) / statistics.fmean(values)


def decide(durations: dict[str, list[float]]) -> dict[str, Any]:
    """The decision row of the case for three durations of each request."""
    for name in REQUESTS:
        require(len(durations[name]) == ORDER.count(name), f"{name}: {len(durations[name])} durations")
    s1, s2 = spread(durations["p1"]), spread(durations["p2"])
    m1, m2 = statistics.fmean(durations["p1"]), statistics.fmean(durations["p2"])
    means = abs(m1 - m2) / statistics.fmean([m1, m2])
    mean = statistics.fmean(durations["p1"] + durations["p2"])
    if s1 > WIDE or s2 > WIDE:
        reading = "service-variation"
    elif s1 <= NARROW and s2 <= NARROW and means > WIDE:
        reading = "request-cost"
    elif s1 <= NARROW and s2 <= NARROW and means <= NARROW:
        reading = "doubled-above-fit" if 2 * mean > FIT_SECONDS else "doubled-within-fit"
    else:
        reading = "inconclusive"
    return {"s_p1": s1, "s_p2": s2, "m_p1": m1, "m_p2": m2, "means": means, "mean": mean, "reading": reading}


def analyze(runs: list[Path], tree: Path = TREE) -> dict[str, Any]:
    require(len(runs) == len(ORDER), f"the analysis needs {len(ORDER)} runs, not {len(runs)}")
    facts = schedule(runs, tree)
    durations = {name: [f["duration"] for f in facts if f["request"] == name] for name in REQUESTS}
    deviations = [f["run"] for f in facts if not (1 - WIDE) * LIMIT_SECONDS / 2 <= f["duration"] <= LIMIT_SECONDS / 2]
    return {"runs": facts, "deviations_from_prediction": deviations, **decide(durations)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--out", type=Path, default=TREE)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("directory", type=Path, nargs="?", default=TREE)
    record_parser = commands.add_parser("record")
    record_parser.add_argument("run", type=Path)
    record_parser.add_argument("--poll", type=float, default=MAX_POLL)
    record_parser.add_argument("--timeout", type=float, default=3600.0)
    next_parser = commands.add_parser("next")
    next_parser.add_argument("runs", type=Path, nargs="*")
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        if args.command == "build":
            write(args.out)
            check(args.out)
        elif args.command == "check":
            check(args.directory)
        elif args.command == "record":
            print(json.dumps(record(args.run, args.poll, args.timeout)["status"], indent=1))
        elif args.command == "next":
            facts = schedule(args.runs)
            print("complete" if len(facts) == len(ORDER) else ORDER[len(facts)])
        else:
            print(json.dumps(analyze(args.runs), indent=1))
    except TimingError as error:
        print(f"bdsc timing: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
