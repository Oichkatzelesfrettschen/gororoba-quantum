"""IQM Resonance circuit jobs: a deterministic case, a ceiling-gated submission and a lossless collection.

IQM Server bills a pay-as-you-go job its runtime rounded up to whole seconds times the quantum
computer's price per second (docs/notes/iqm/README.md, "Cost"). A job is a POST of
iqm.station_control.api.job.circuit to /api/v1/jobs/{qc}/circuit: circuits of native operations
(prx with angle and phase in radians, cz, measure with a key), shots, and options such as
heralding_mode and active_reset_cycles. The job record (GET /api/v1/jobs/{id}) reports
compilation.execution_runtime_estimate_seconds and metrics with compilation, execution, runtime and
billed seconds; the measurements artifact holds every shot's bits per circuit and key.

Subcommands:

- build DIR writes the case named by DIR's last component (timing-pilot or reset-billing-pilot):
  cases.json and one circuit JSON per circuit file; check DIR regenerates it and compares bytes and
  file sets.
- submit CASE_DIR JOB --qc QC --approval QUOTE --approved-cases-sha256 HEX --max-credits C
  (network) copies the case into results/iqm/runs/STAMP-QC-CASE-JOB/, refuses unless cases.json
  carries the approved digest, the quantum computer is online and healthy, and the job's expected
  seconds rounded up times the live price per second stay within C, and refuses a job that already
  has a run directory for that quantum computer; it then writes submission-state.json exclusively
  before the POST, reads the account credit, posts the job and writes submission.json with the job
  id and the quoted approval. --dry runs every refusal and prints the job without copying or sending.
- collect RUN_DIR [--poll S] [--timeout S] (network) waits for a terminal status, keeps the job
  record and, for a completed job, the measurements and measurement_counts artifacts byte for byte
  under raw/, reads the credit again and writes results.json: status, metrics, credits charged and
  per-circuit shot counts.
- analyze RUN_DIR... --out FILE [--replay] writes (or with --replay compares) the reset and billing
  pilot's H1-H4 decisions from its retained runs.
- --self-test runs build, check, submit and collect against a stubbed transport on a temporary
  copy: the digest, ceiling, health and duplicate-submission refusals, a completed and a failed job.

Usage: "$PYTHON" scripts/iqm_jobs.py (build DIR | check DIR | --self-test)
       IQM_TOKENS_FILE=TOKENS.json "$PYTHON" scripts/iqm_jobs.py submit CASE_DIR JOB --qc QC \
           --approval QUOTE --approved-cases-sha256 HEX --max-credits C
       IQM_TOKENS_FILE=TOKENS.json "$PYTHON" scripts/iqm_jobs.py collect RUN_DIR
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import iqm_platform  # noqa: E402
from iqm_platform import API, Client, PlatformError, read_tokens, sha256, tokens_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "results/iqm/runs"
CASE_SCHEMA = "iqm-circuit-case-v1"
SUBMISSION_SCHEMA = "iqm-submission-v1"
RESULTS_SCHEMA = "iqm-results-v1"
TERMINAL = ("completed", "failed", "cancelled")
ARTIFACTS = ("measurements", "measurement_counts")
CREDIT_QUERY = "query($a: UUID!){ credit(accountId: $a) { currentBalance expiresAt } }"

# Timing pilot. One X on QB1 and its readout; the four jobs separate a per-job overhead (j1 against
# j2), a per-shot cost (j2 - j1 over 3000 shots), a per-circuit cost (j3 against j2 at equal total
# shots) and the effect of active reset (j4 against j2). The per-shot prior is Garnet's calibrated
# passive reset: reset_wait 298 us plus a 2 us end delay and the 480 ns readout
# (docs/evidence/iqm/qc/garnet/calibration/set.json), so 0.3 ms per shot.
PILOT = "timing-pilot"
PILOT_QUBIT = "QB1"
SHOT_SECONDS = 0.0003
PILOT_JOBS = (
    ("j1-1x1000-passive", 1, 1000, None),
    ("j2-1x4000-passive", 1, 4000, None),
    ("j3-20x200-passive", 20, 200, None),
    ("j4-1x4000-active1", 1, 4000, 1),
)
# Reset and billing pilot. The garnet:mock runtime estimates of the timing pilot fit a fixed
# JOB_SECONDS per job plus each shot's schedule, with no cost per extra circuit, and active reset
# shortening a shot from its passive reset_wait to ACTIVE_SHOT_SECONDS. Each job reads X and a bare
# measure on QB1, so the bare measure carries the initialization error each reset leaves.
RESET_PILOT = "reset-billing-pilot"
# The quantum computers an approved case may run on: its free mock twin and the QPU it was planned for.
PILOT_QCS = ["garnet:mock", "garnet"]
JOB_SECONDS = 1.6
ACTIVE_SHOT_SECONDS = 0.0000087
RESET_JOBS = (
    ("p-2x2000-passive", 2000, None, SHOT_SECONDS),
    ("a-2x2000-active1", 2000, 1, ACTIVE_SHOT_SECONDS),
)


def dump(value: Any) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def now_stamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H%M%SZ")


def x_circuit(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "instructions": [
            {"name": "prx", "locus": [PILOT_QUBIT], "args": {"angle": math.pi, "phase": 0.0}},
            {"name": "measure", "locus": [PILOT_QUBIT], "args": {"key": "m"}},
        ],
    }


def zero_circuit(name: str) -> dict[str, Any]:
    return {"name": name, "instructions": [{"name": "measure", "locus": [PILOT_QUBIT], "args": {"key": "m"}}]}


def job_row(job: str, files: dict[str, str], names: list[str], shots: int, active: int | None, seconds: float) -> dict:
    return {
        "job": job,
        "circuits": [{"file": rel, "sha256": sha256(files[rel].encode())} for rel in names],
        "shots": shots,
        "options": {"heralding_mode": "none", "active_reset_cycles": active},
        "expected_seconds": round(seconds, 3),
    }


def build_timing() -> dict[str, str]:
    files: dict[str, str] = {}
    jobs = []
    for job, circuits, shots, active in PILOT_JOBS:
        names = []
        for n in range(circuits):
            rel = f"circuits/{job}-{n:02d}.json"
            files[rel] = dump(x_circuit(f"{job}-{n:02d}"))
            names.append(rel)
        jobs.append(job_row(job, files, names, shots, active, circuits * shots * SHOT_SECONDS))
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": PILOT,
            "question": "What does IQM bill per job, per shot, per circuit and with active reset on Garnet?",
            "ideal": {"circuit": f"X on {PILOT_QUBIT}, then measure", "p1": 1.0},
            "shot_seconds_prior": SHOT_SECONDS,
            "qcs": PILOT_QCS,
            "jobs": jobs,
        }
    )
    return files


def build_reset() -> dict[str, str]:
    files: dict[str, str] = {}
    jobs = []
    for job, shots, active, shot_seconds in RESET_JOBS:
        names = []
        for kind, make in (("x", x_circuit), ("zero", zero_circuit)):
            rel = f"circuits/{job}-{kind}.json"
            files[rel] = dump(make(f"{job}-{kind}"))
            names.append(rel)
        jobs.append(job_row(job, files, names, shots, active, JOB_SECONDS + len(names) * shots * shot_seconds))
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": RESET_PILOT,
            "question": (
                "Does Garnet bill ceil(its compiler estimate), does that estimate follow a fixed job cost plus each "
                "shot's schedule, does active reset run and keep initialization, and does the calibration-built "
                "simulator predict QB1?"
            ),
            "ideal": {"x": {"p1": 1.0}, "zero": {"p1": 0.0}},
            "estimate_model": {
                "job_seconds": JOB_SECONDS,
                "passive_shot_seconds": SHOT_SECONDS,
                "active_shot_seconds": ACTIVE_SHOT_SECONDS,
                "source": "garnet:mock execution_runtime_estimate_seconds of the timing pilot",
            },
            "qcs": PILOT_QCS,
            "jobs": jobs,
        }
    )
    return files


CASES = {PILOT: build_timing, RESET_PILOT: build_reset}


def build(name: str = PILOT) -> dict[str, str]:
    """Relative path -> text of the named case."""
    if name not in CASES:
        raise PlatformError(f"no case named {name}; the cases are {sorted(CASES)}")
    return CASES[name]()


def write_case(directory: Path) -> None:
    for rel, text in build(directory.name).items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def check_case(directory: Path) -> None:
    files = build(directory.name)
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if present != set(files):
        raise PlatformError(f"{directory}: files differ from the build: {sorted(present ^ set(files))}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise PlatformError(f"{directory}/{rel} differs from the build")


def load_job(case_dir: Path, job: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    raw = (case_dir / "cases.json").read_bytes()
    case = json.loads(raw)
    if case.get("schema") != CASE_SCHEMA:
        raise PlatformError(f"{case_dir}/cases.json is not {CASE_SCHEMA}")
    rows = [row for row in case["jobs"] if row["job"] == job]
    if len(rows) != 1:
        raise PlatformError(f"{case_dir}: job {job} is not in the case")
    for circuit in rows[0]["circuits"]:
        if sha256((case_dir / circuit["file"]).read_bytes()) != circuit["sha256"]:
            raise PlatformError(f"{case_dir}/{circuit['file']} differs from its recorded sha256")
    return case, rows[0], sha256(raw)


def body_of(case_dir: Path, row: dict[str, Any]) -> dict[str, Any]:
    body: dict[str, Any] = {
        "circuits": [json.loads((case_dir / c["file"]).read_text(encoding="utf-8")) for c in row["circuits"]],
        "shots": row["shots"],
        "heralding_mode": row["options"]["heralding_mode"],
    }
    if row["options"]["active_reset_cycles"] is not None:
        body["active_reset_cycles"] = row["options"]["active_reset_cycles"]
    if row["options"].get("calibration_set_id"):
        body["calibration_set_id"] = row["options"]["calibration_set_id"]
    return body


def credit(client: Client) -> dict[str, Any]:
    account = client.graphql("{ me { currentAccount { id } } }")["me"]["currentAccount"]["id"]
    value: dict[str, Any] = client.graphql(CREDIT_QUERY, {"a": account})["credit"]
    return value


def get_json(client: Client, path: str) -> Any:
    status, body = client.get(path)
    if status != 200:
        raise PlatformError(f"GET {path} answered {status}: {body[:200]!r}")
    return json.loads(body)


def submit(
    case_dir: Path,
    job: str,
    qc: str,
    approval: str,
    approved_sha256: str,
    max_credits: float,
    client: Client,
    runs: Path = RUNS,
    stamp: str | None = None,
    dry: bool = False,
) -> Path:
    case, row, cases_sha256 = load_job(case_dir, job)
    if not approval.strip():
        raise PlatformError("a submission carries the user's quoted approval")
    if cases_sha256 != approved_sha256:
        raise PlatformError(f"cases.json sha256 {cases_sha256} is not the approved {approved_sha256}")
    if qc not in case.get("qcs", []):
        raise PlatformError(f"{qc} is not among the case's approved quantum computers {case.get('qcs')}")
    record = get_json(client, f"{API}/quantum-computers/{qc}")
    if record.get("operational_status") != "online" or not record.get("health", {}).get("healthy"):
        raise PlatformError(f"{qc} is {record.get('operational_status')}, healthy {record.get('health')}")
    price = float(record["pricing"]["payg_price_per_second"])
    # IQM bills ceil(runtime) and offers no job-side cap. The garnet:mock and Garnet estimates add a fixed
    # JOB_SECONDS to each shot's schedule and exceeded the measured runtime of every pilot job, so the
    # ceiling carries that fixed cost on top of the case's expected seconds.
    ceiling = math.ceil(JOB_SECONDS + row["expected_seconds"]) * price
    if ceiling > max_credits:
        raise PlatformError(f"{job} expects {ceiling:.2f} credits on {qc}, above the approved {max_credits}")
    suffix = f"-{qc.replace(':', '_')}-{case['case']}-{job}"
    run_dir = runs / f"{stamp or now_stamp()}{suffix}"
    if dry:
        refuse_earlier(runs, suffix, job, qc)
        body = body_of(case_dir, row)
        print(
            f"{run_dir.name}: dry, {len(body['circuits'])} circuits x {body['shots']} shots, "
            f"ceiling {ceiling:.2f} credits at {price} per second; nothing sent"
        )
        return run_dir
    import fcntl

    runs.mkdir(parents=True, exist_ok=True)
    # The lock spans the duplicate check, the copy and the POST, so two submissions of one case never both pass.
    fd = os.open(case_dir, os.O_RDONLY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise PlatformError(f"another submission holds {case_dir}") from None
        refuse_earlier(runs, suffix, job, qc)
        return post_job(case_dir, run_dir, job, qc, approval, approved_sha256, max_credits, price, client)
    finally:
        os.close(fd)


def refuse_earlier(runs: Path, suffix: str, job: str, qc: str) -> None:
    """One run directory per quantum computer, case and job: an earlier one, even without submission.json,
    may stand for a job already on the server, which the job list settles before anything is resent."""
    earlier = sorted(runs.glob(f"*{suffix}"))
    if earlier:
        raise PlatformError(f"{job} on {qc} already has {earlier[0].name}; collect it or settle it first")


def post_job(
    case_dir: Path,
    run_dir: Path,
    job: str,
    qc: str,
    approval: str,
    approved_sha256: str,
    max_credits: float,
    price: float,
    client: Client,
) -> Path:
    before = credit(client)
    shutil.copytree(case_dir, run_dir)
    # The copy is what gets sent, so it must carry the approved digest and its circuits their recorded ones.
    try:
        _, row, copied = load_job(run_dir, job)
        if copied != approved_sha256:
            raise PlatformError(f"the copied cases.json sha256 {copied} is not the approved {approved_sha256}")
    except PlatformError:
        shutil.rmtree(run_dir)
        raise
    body = body_of(run_dir, row)
    encoded = json.dumps(body, sort_keys=True).encode()
    # The exclusive checkpoint precedes the POST: an existing one means the job may already be on the server.
    fd = os.open(run_dir / "submission-state.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as handle:
        handle.write(dump({"state": "posting", "qc": qc, "job": job, "body_sha256": sha256(encoded)}))
    status, reply = client.post(f"{API}/jobs/{qc}/circuit", body)
    if 400 <= status < 500:
        # A 4xx refusal created no job, so the copy goes and the corrected case can be submitted again.
        shutil.rmtree(run_dir)
        raise PlatformError(f"POST {qc} circuit refused with {status}: {reply}")
    if status not in (200, 201, 202) or not isinstance(reply, dict) or "id" not in reply:
        (run_dir / "submission-unconfirmed.json").write_text(dump({"status": status, "reply": reply}))
        raise PlatformError(f"POST {qc} circuit answered {status}: {reply}; the job list settles whether it exists")
    (run_dir / "submission.json").write_text(
        dump(
            {
                "schema": SUBMISSION_SCHEMA,
                "job_id": reply["id"],
                "qc": qc,
                "job": job,
                "cases_sha256": approved_sha256,
                "body_sha256": sha256(encoded),
                "approval": approval,
                "max_credits": max_credits,
                "price_per_second": price,
                "expected_seconds": row["expected_seconds"],
                "credit_before": before,
                "submitted_at": iqm_platform.now(),
            }
        )
    )
    print(f"{run_dir.name}: job {reply['id']}")
    return run_dir


def collect(run_dir: Path, client: Client, poll: float = 5.0, timeout: float = 3600.0) -> dict[str, Any]:
    """Collect a terminal job once; a run already collected keeps its first results.json, whose credit
    delta a later collection would mix with every job charged since."""
    retained = run_dir / "results.json"
    if retained.exists():
        results: dict[str, Any] = json.loads(retained.read_text(encoding="utf-8"))
        for name, digest in results["raw_sha256"].items():
            if sha256((run_dir / "raw" / name).read_bytes()) != digest:
                raise PlatformError(f"{run_dir}/raw/{name} differs from its recorded sha256")
        return results
    submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
    job_id = submission["job_id"]
    deadline = time.monotonic() + timeout
    while True:
        status, body = client.get(f"{API}/jobs/{job_id}")
        if status != 200:
            raise PlatformError(f"GET job {job_id} answered {status}")
        record = json.loads(body)
        if record["status"] in TERMINAL:
            break
        if time.monotonic() > deadline:
            raise PlatformError(f"job {job_id} is still {record['status']}")
        time.sleep(poll)
    raw = run_dir / "raw"
    raw.mkdir(exist_ok=True)
    kept: dict[str, str] = {}

    def keep(name: str, data: bytes) -> None:
        path = raw / name
        if path.exists() and path.read_bytes() != data:
            raise PlatformError(f"{path} is retained with other bytes")
        path.write_bytes(data)
        kept[name] = sha256(data)

    keep("job.json", body)
    shots: list[int] = []
    if record["status"] == "completed":
        for artifact in ARTIFACTS:
            status, data = client.get(f"{API}/jobs/{job_id}/artifacts/{artifact}")
            if status != 200:
                raise PlatformError(f"GET {artifact} of {job_id} answered {status}")
            keep(f"{artifact}.json", data)
        for circuit in json.loads((raw / "measurements.json").read_bytes()):
            lengths = {len(values) for values in circuit.values()}
            if len(lengths) != 1:
                raise PlatformError(f"job {job_id}: keys of one circuit hold different shot counts")
            shots.append(lengths.pop())
    after = credit(client)
    charged = float(submission["credit_before"]["currentBalance"]) - float(after["currentBalance"])
    results = {
        "schema": RESULTS_SCHEMA,
        "job_id": job_id,
        "status": record["status"],
        "metrics": record.get("metrics"),
        "compilation": record.get("compilation"),
        "errors": record.get("errors"),
        "shots_per_circuit": shots,
        "credit_after": after,
        "credits_charged": round(charged, 6),
        # The credit delta covers every job of the account in the window; billed seconds belong to this job.
        "billed_credits": round(
            float((record.get("metrics") or {}).get("billed_seconds") or 0.0) * float(submission["price_per_second"]), 6
        ),
        "raw_sha256": kept,
    }
    (run_dir / "results.json").write_text(dump(results))
    return results


def shots_ok(returned: list[int], row: dict[str, Any]) -> bool:
    """Every circuit returned the case's shots, or at most that many under all-zeros heralding, which
    discards each shot whose pre-circuit measurement is not all zeros."""
    heralded = row["options"].get("heralding_mode") == "zeros"
    if len(returned) != len(row["circuits"]):
        return False
    return all(0 < n <= row["shots"] if heralded else n == row["shots"] for n in returned)


def run_facts(run_dir: Path) -> dict[str, Any]:
    """The registry facts of one retained run, after checking it against its own receipts.

    The case files match cases.json, submission.json names the job, QC, approval and cases digest,
    results.json names the same job with a terminal status, every raw file keeps the sha256
    results.json records, and a completed job returns the case's shots for every circuit. The charge
    is billed_seconds times the price per second the submission recorded.
    """
    submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
    if submission.get("schema") != SUBMISSION_SCHEMA or not submission.get("approval"):
        raise PlatformError(f"{run_dir}: submission.json is not an approved {SUBMISSION_SCHEMA} receipt")
    _, row, cases_sha256 = load_job(run_dir, submission["job"])
    if cases_sha256 != submission["cases_sha256"]:
        raise PlatformError(f"{run_dir}: cases.json differs from the submission receipt")
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    if results.get("schema") != RESULTS_SCHEMA or results["job_id"] != submission["job_id"]:
        raise PlatformError(f"{run_dir}: results.json names another job")
    if results["status"] not in TERMINAL:
        raise PlatformError(f"{run_dir}: job status {results['status']} is not terminal")
    for name, digest in results["raw_sha256"].items():
        if sha256((run_dir / "raw" / name).read_bytes()) != digest:
            raise PlatformError(f"{run_dir}/raw/{name} differs from its recorded sha256")
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    if record["id"] != submission["job_id"] or record["status"] != results["status"]:
        raise PlatformError(f"{run_dir}: raw/job.json disagrees with results.json")
    if results["status"] == "completed" and not shots_ok(results["shots_per_circuit"], row):
        raise PlatformError(f"{run_dir}: a circuit returned other than {row['shots']} shots")
    billed = float((record.get("metrics") or {}).get("billed_seconds") or 0.0)
    return {
        "created_at": submission["submitted_at"],
        "backends": [submission["qc"]],
        "jobs": 1,
        "circuits": len(row["circuits"]),
        "statuses": {results["status"]: 1},
        "charge": round(billed * float(submission["price_per_second"]), 6),
        "detail": f"{billed:g} billed seconds",
    }


# Preregistered predictions of the reset and billing pilot (docs/design/iqm-garnet-timing-pilot.md),
# computed by iqm_sim from Garnet calibration set 9069c4ef: X on QB1 reads (1 - p/2)(1 - e10) + (p/2) e01
# and a bare measure reads e01, the unheralded P(1 | 0). Z_STOP is the three-standard-error decision rule.
PREDICTED = {"x": 0.9817, "zero": 0.0046}
PREDICTION_CALIBRATION = "9069c4ef-7ab6-4e50-be4f-c91d71c3a06d"
Z_STOP = 3.0
ESTIMATE_TOLERANCE = 0.05


def p1_of(run_dir: Path) -> dict[str, dict[str, float]]:
    """P(1) and its binomial standard error per circuit kind of a completed run."""
    measurements = json.loads((run_dir / "raw/measurements.json").read_bytes())
    _, row, _ = load_job(run_dir, json.loads((run_dir / "submission.json").read_text())["job"])
    out = {}
    for entry, circuit in zip(row["circuits"], measurements, strict=True):
        bits = [shot[0] for shot in circuit["m"]]
        p = sum(bits) / len(bits)
        out[entry["file"].rsplit("-", 1)[-1].removesuffix(".json")] = {
            "p1": p,
            "se": math.sqrt(max(p * (1 - p), 1 / len(bits)) / len(bits)),
            "shots": len(bits),
        }
    return out


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """H1-H4 of the reset and billing pilot from its retained runs (mock and hardware)."""
    runs = []
    for run_dir in sorted(run_dirs):
        facts = run_facts(run_dir)
        submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
        record = json.loads((run_dir / "raw/job.json").read_bytes())
        metrics = record["metrics"]
        case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        row = [r for r in case["jobs"] if r["job"] == submission["job"]][0]
        runs.append(
            {
                "run": run_dir.name,
                "qc": submission["qc"],
                "job": submission["job"],
                "expected_seconds": row["expected_seconds"],
                "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
                "execution_seconds": metrics["execution_seconds"],
                "runtime_seconds": metrics["runtime_seconds"],
                "billed_seconds": metrics["billed_seconds"],
                "charge": facts["charge"],
                "p1": p1_of(run_dir),
            }
        )
    hardware = {r["job"]: r for r in runs if r["qc"] == "garnet"}
    passive, active = hardware["p-2x2000-passive"], hardware["a-2x2000-active1"]
    h1 = [
        {
            "job": r["job"],
            "billed": r["billed_seconds"],
            "ceil_estimate": math.ceil(r["estimate_seconds"]),
            "ceil_runtime": math.ceil(r["runtime_seconds"]),
        }
        for r in hardware.values()
    ]
    # H2 concerns Garnet's estimate; the mock schedules its own 400 us reset, so its rows carry no decision.
    h2 = [
        {"job": r["job"], "departure": round(r["estimate_seconds"] - r["expected_seconds"], 6)}
        for r in hardware.values()
    ]
    h2_mock = [
        {"job": r["job"], "qc": r["qc"], "departure": round(r["estimate_seconds"] - r["expected_seconds"], 6)}
        for r in runs
        if r["qc"] != "garnet"
    ]
    zero_gap = active["p1"]["zero"]["p1"] - passive["p1"]["zero"]["p1"]
    zero_se = math.hypot(active["p1"]["zero"]["se"], passive["p1"]["zero"]["se"])
    h4 = [
        {
            "job": r["job"],
            "kind": kind,
            "predicted": PREDICTED[kind],
            "measured": value["p1"],
            "z": (value["p1"] - PREDICTED[kind]) / value["se"],
        }
        for r in hardware.values()
        for kind, value in r["p1"].items()
        if r is passive
    ]
    return {
        "schema": "iqm-reset-billing-analysis-v1",
        "runs": runs,
        "per_shot_seconds": {
            r["job"]: r["execution_seconds"] / sum(v["shots"] for v in r["p1"].values()) for r in hardware.values()
        },
        "h1_billed_is_ceil_estimate": {
            "rows": h1,
            "holds": all(row["billed"] == row["ceil_estimate"] for row in h1),
            "billed_is_ceil_runtime": all(row["billed"] == row["ceil_runtime"] for row in h1),
        },
        "h2_estimate_model": {
            "rows": h2,
            "tolerance": ESTIMATE_TOLERANCE,
            "holds": all(abs(row["departure"]) <= ESTIMATE_TOLERANCE for row in h2),
            "mock_rows": h2_mock,
        },
        "h3_active_reset_keeps_initialization": {
            "ran": active["billed_seconds"] > 0 and active["p1"]["zero"]["shots"] > 0,
            "zero_p1_active_minus_passive": zero_gap,
            "z": zero_gap / zero_se,
            "holds": zero_gap / zero_se <= Z_STOP,
        },
        "h4_simulator_predicts_qb1": {
            "calibration_set": PREDICTION_CALIBRATION,
            "rows": h4,
            "holds": all(abs(row["z"]) <= Z_STOP for row in h4),
        },
        "credits_charged": round(sum(r["charge"] for r in runs), 6),
    }


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []


def self_test() -> str:
    jobs: dict[str, dict[str, Any]] = {}
    state = {"balance": 30.0, "healthy": True, "posts": 0}
    shots_back: dict[str, int | None] = {"value": None}

    def transport(
        method: str, url: str, body: bytes | None, headers: dict[str, str]
    ) -> tuple[int, dict[str, str], bytes]:
        path = url.split("://", 1)[1].split("/", 1)[1]
        if path == "api/graphql":
            query = json.loads(body or b"{}")["query"]
            if "me" in query:
                return 200, {}, json.dumps({"data": {"me": {"currentAccount": {"id": "acct"}}}}).encode()
            return 200, {}, json.dumps({"data": {"credit": {"currentBalance": f"{state['balance']:.2f}"}}}).encode()
        if path.startswith(f"{API}/quantum-computers/"):
            return (
                200,
                {},
                json.dumps(
                    {
                        "operational_status": "online",
                        "health": {"healthy": state["healthy"]},
                        "pricing": {"payg_price_per_second": "0.50"},
                    }
                ).encode(),
            )
        if method == "POST" and path.endswith("/circuit"):
            if state.get("refuse"):
                return 400, {}, json.dumps({"error_code": "invalid_input", "message": "stub"}).encode()
            state["posts"] += 1
            sent = json.loads(body or b"{}")
            job_id = f"job-{state['posts']}"
            jobs[job_id] = sent
            return 202, {}, json.dumps({"id": job_id}).encode()
        job_id = path.split("/")[3]
        sent = jobs[job_id]
        if path.endswith("measurements"):
            n = shots_back["value"] or sent["shots"]
            return 200, {}, json.dumps([{"m": [[1]] * n} for _ in sent["circuits"]]).encode()
        if path.endswith("measurement_counts"):
            return 200, {}, json.dumps([{"measurement_keys": ["m"], "counts": {"1": sent["shots"]}}]).encode()
        status = "failed" if sent["shots"] == 1000 and state.get("fail") else "completed"
        state["balance"] -= 1.0 if status == "completed" else 0.0
        return 200, {}, json.dumps({"id": job_id, "status": status, "metrics": {"billed_seconds": 2.0}}).encode()

    def refused(call: Any, words: str) -> None:
        try:
            call()
        except PlatformError as error:
            if words not in str(error):
                raise RuntimeError(f"refused for another reason: {error}") from error
        else:
            raise RuntimeError(f"accepted where it must refuse ({words})")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        case, runs = root / PILOT, root / "runs"
        write_case(case)
        check_case(case)
        (case / "circuits/j1-1x1000-passive-00.json").write_text("{}\n")
        refused(lambda: check_case(case), "differs from the build")
        write_case(case)
        approved = sha256((case / "cases.json").read_bytes())
        client = Client("token", transport, "https://stub")
        job = "j2-1x4000-passive"
        refused(lambda: submit(case, job, "garnet", "", approved, 5, client, runs, "s0"), "quoted approval")
        refused(lambda: submit(case, job, "garnet", "approved", "0" * 64, 5, client, runs, "s0"), "not the approved")
        refused(lambda: submit(case, job, "emerald", "approved", approved, 5, client, runs, "s0"), "approved quantum")
        import fcntl

        holder = os.open(case, os.O_RDONLY)
        fcntl.flock(holder, fcntl.LOCK_EX)
        try:
            refused(lambda: submit(case, job, "garnet", "approved", approved, 5, client, runs, "s0"), "holds")
        finally:
            os.close(holder)
        copy = shutil.copytree

        def tampering_copy(src: Path, dst: Path, *args: Any, **kwargs: Any) -> Any:
            out = copy(src, dst, *args, **kwargs)
            if (Path(dst) / "cases.json").exists():
                (Path(dst) / "circuits/j2-1x4000-passive-00.json").write_text("{}\n")
            return out

        shutil.copytree = tampering_copy  # type: ignore[assignment]
        try:
            refused(lambda: submit(case, job, "garnet", "approved", approved, 5, client, runs, "s0"), "differs")
        finally:
            shutil.copytree = copy
        if state["posts"] or any(runs.glob("s0-*")):
            raise RuntimeError("a tampered copy posted or kept its run directory")
        refused(
            lambda: submit(case, job, "garnet", "approved", approved, 0.5, client, runs, "s0"), "above the approved"
        )
        state["healthy"] = False
        refused(lambda: submit(case, job, "garnet", "approved", approved, 5, client, runs, "s0"), "healthy")
        state["healthy"] = True
        if state["posts"] or (runs.exists() and any(runs.iterdir())):
            raise RuntimeError("a refused submission posted or copied the case")
        submit(case, job, "garnet", "approved", approved, 5, client, runs, "s0", dry=True)
        if state["posts"] or (runs.exists() and any(runs.iterdir())):
            raise RuntimeError("a dry submission posted or copied the case")
        run = submit(case, job, "garnet", "approved", approved, 5, client, runs, "s1")
        # A rerun under a new stamp refuses, also once submission.json is gone and only the checkpoint is left.
        (run / "submission.json").rename(run / "submission.kept")
        refused(lambda: submit(case, job, "garnet", "approved", approved, 5, client, runs, "s2"), "already has")
        (run / "submission.kept").rename(run / "submission.json")
        if state["posts"] != 1:
            raise RuntimeError(f"{state['posts']} posts for one approved job")
        state["refuse"] = True
        refused(
            lambda: submit(case, job, "garnet:mock", "approved", approved, 5, client, runs, "s2"), "refused with 400"
        )
        state["refuse"] = False
        if list(runs.glob("*-garnet_mock-*")):
            raise RuntimeError("a refused POST left its run directory")
        mock = submit(case, job, "garnet:mock", "approved", approved, 5, client, runs, "s2")
        if not mock.name.endswith("-garnet_mock-timing-pilot-" + job):
            raise RuntimeError(f"the mock run is named {mock.name}")
        results = collect(run, client, poll=0)
        if results["status"] != "completed" or results["shots_per_circuit"] != [4000]:
            raise RuntimeError(f"collect read {results}")
        if (
            results["billed_credits"] != 1.0
            or results["credits_charged"] != 1.0
            or set(results["raw_sha256"])
            != {
                "job.json",
                *(f"{a}.json" for a in ARTIFACTS),
            }
        ):
            raise RuntimeError(f"collect kept {results}")
        collect(run, client, poll=0)
        facts = run_facts(run)
        if facts["statuses"] != {"completed": 1} or facts["charge"] != 1.0 or facts["backends"] != ["garnet"]:
            raise RuntimeError(f"run_facts read {facts}")
        kept = (run / "raw/measurements.json").read_bytes()
        (run / "raw/measurements.json").write_text("[]")
        refused(lambda: run_facts(run), "differs from its recorded sha256")
        (run / "raw/measurements.json").write_bytes(kept)
        (run / "raw/job.json").write_text("{}")
        refused(lambda: collect(run, client, poll=0), "differs from its recorded sha256")
        state["fail"] = True
        failed = submit(case, "j1-1x1000-passive", "garnet", "approved", approved, 5, client, runs, "s3")
        results = collect(failed, client, poll=0)
        if results["status"] != "failed" or results["shots_per_circuit"] or set(results["raw_sha256"]) != {"job.json"}:
            raise RuntimeError(f"a failed job collected as {results}")
        state["fail"] = False
        shots_back["value"] = 3999
        short = submit(case, "j4-1x4000-active1", "garnet", "approved", approved, 5, client, runs, "s4")
        sent = jobs[json.loads((short / "submission.json").read_text())["job_id"]]
        if sent.get("active_reset_cycles") != 1 or "active_reset_cycles" in jobs["job-2"]:
            raise RuntimeError("active_reset_cycles is not sent exactly where the case sets it")
        if collect(short, client, poll=0)["shots_per_circuit"] != [3999]:
            raise RuntimeError("collect does not report the shots the service returned")
        refused(lambda: run_facts(short), "returned other than")
        plain = {"circuits": [{}, {}], "shots": 100, "options": {"heralding_mode": "none"}}
        heralded = {**plain, "options": {"heralding_mode": "zeros"}}
        if not shots_ok([100, 100], plain) or shots_ok([99, 100], plain) or shots_ok([100], plain):
            raise RuntimeError("shots_ok misreads an unheralded job")
        if not shots_ok([61, 100], heralded) or shots_ok([0, 100], heralded) or shots_ok([101, 100], heralded):
            raise RuntimeError("shots_ok misreads a heralded job")
    return "iqm jobs: build, check, approval, digest, ceiling, health, checkpoint and collection refusals pass"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    for name in ("build", "check"):
        sub.add_parser(name).add_argument("directory", type=Path)
    sm = sub.add_parser("submit")
    sm.add_argument("case_dir", type=Path)
    sm.add_argument("job")
    sm.add_argument("--qc", required=True)
    sm.add_argument("--approval", required=True)
    sm.add_argument("--approved-cases-sha256", required=True)
    sm.add_argument("--max-credits", type=float, required=True)
    sm.add_argument("--dry", action="store_true", help="run every refusal and print the job; send nothing")
    co = sub.add_parser("collect")
    co.add_argument("run_dir", type=Path)
    co.add_argument("--poll", type=float, default=5.0)
    co.add_argument("--timeout", type=float, default=3600.0)
    an = sub.add_parser("analyze")
    an.add_argument("run_dirs", type=Path, nargs="+")
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true", help="compare --out with the recomputation")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.command == "build":
        write_case(args.directory)
    elif args.command == "check":
        check_case(args.directory)
        print(f"{args.directory}: matches the build")
    elif args.command == "analyze":
        text = dump(analyze(args.run_dirs))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise PlatformError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    elif args.command in ("submit", "collect"):
        client = Client(read_tokens(tokens_path())["access_token"])
        if args.command == "submit":
            submit(
                args.case_dir,
                args.job,
                args.qc,
                args.approval,
                args.approved_cases_sha256,
                args.max_credits,
                client,
                dry=args.dry,
            )
        else:
            print(json.dumps(collect(args.run_dir, client, args.poll, args.timeout), indent=1))
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
