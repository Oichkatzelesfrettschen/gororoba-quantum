"""Retain the calibration each prior IBM job ran under, and today's, as portable snapshots.

A ghost run replays a retained job's circuits in Aer under a chosen
calibration: the one in force when its shots began, today's, or any other
retained state. live_run.py --collect already fetches the execution-time
Target and properties (``backend.properties(datetime=start)`` and
``backend.target_history(datetime=start)``) but keeps them in memory; a
Kaggle kernel holds no IBM credential, so this script writes them as
gororoba_quantum/calibration_snapshot.py snapshots.

``--write`` needs the service. For every job in
results/live/qpu-job-retention-audit.json it reads the PUB execution starts
from the run's collect.json (every collection pass), or the job's
``running`` timestamp from the service when the run keeps no collection,
fetches the calibration at each start, and exports it once per calibration
identity (backend and properties last_update_date) to
docs/evidence/calibration/history/<backend>/<calibration>.json; before writing,
every gate, reset and readout channel the snapshot rebuilds must equal
live_run's noise model built from the same fetch. ``properties(datetime=S)``
returns the update the service held at S, which trails its last_update_date
stamp by some minutes (at the stamp itself it still returns the previous
update), so the fetch at a PUB start names the calibration the service
published for that execution. It also exports each
backend's current calibration, and writes index.json mapping every job and
PUB start to its snapshot. ``--append`` reads each backend's current calibration (read-only) and
records each new identity in history/appended.json, outside the index whose
snapshot set retained ghost results bind; it reads the service only and
submits nothing. ``--add`` indexes only the audited jobs index.json lacks: it
fetches their execution-start calibrations, exports the identities no
retained snapshot carries, and appends the jobs and new files while every
indexed job, the current map and every retained snapshot keep their bytes,
so ghost results bound to the existing snapshot set stay valid and only the
new (run, snapshot) pairs need a ghost (scripts/ghost_run.py --merge).
``--check`` needs no network: every indexed file
exists with its recorded sha256, rebuilds its Target, the index covers
exactly the audited jobs, and every executed member's start maps to a
snapshot carrying the calibration identity its collect.json records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import calibration_snapshot  # noqa: E402
import ibm_account  # noqa: E402

AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
HISTORY = ROOT / "docs/evidence/calibration/history"
INDEX = HISTORY / "index.json"
# Calibrations read after the index was written. ghost_run binds the index's
# snapshot set, so these stay outside it until a ghost run is regenerated.
APPENDED = HISTORY / "appended.json"
BACKENDS = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execution_starts(job: dict[str, Any]) -> list[str]:
    path = ROOT / job["run"] / "collect.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    starts: set[str] = set()
    for collection in data if isinstance(data, list) else [data]:
        timing = ((collection.get("jobs") or {}).get(job["job_id"]) or {}).get("pub_timing", {})
        starts |= {t["execution_window_start"] for t in timing.values() if t.get("execution_window_start")}
    return sorted(starts)


def file_name(calibration: str) -> str:
    return calibration.replace(":", "").replace("+", "p").replace("-", "") + ".json"


def export(backend: Any, name: str, props: Any, target: Any, written: dict[str, str], base: Path = HISTORY) -> str:
    """Snapshot of one fetched calibration, verified against live_run's noise model; returns its path."""
    import live_run

    processor_type = live_run.backend_identity(backend)["processor_type"]
    described = calibration_snapshot.describe(name, target, props, live_run.readout_flips, processor_type)
    snapshot = json.loads(json.dumps(described))
    path = HISTORY / name / file_name(snapshot["calibration"])
    relative = path.relative_to(ROOT).as_posix()
    if relative in written:
        return relative
    omitted = tuple(f"{op}[" for op in snapshot["omitted_operations"])
    live = {
        key: error
        for key, error in calibration_snapshot.channel_table(
            live_run._noise_model(name, live_run.TargetView(name, target), target, props)
        ).items()
        if not key.startswith(omitted)
    }
    rebuilt = calibration_snapshot.channel_table(calibration_snapshot.noise_model(snapshot)[1])
    differing = [k for k in live.keys() | rebuilt.keys() if not (k in live and k in rebuilt and live[k] == rebuilt[k])]
    require(not differing, f"{relative}: {len(differing)} channels differ from live_run, first {sorted(differing)[:3]}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    written[relative] = snapshot["calibration"]
    print(f"{relative}: {len(live)} channels equal to live_run's", flush=True)
    return relative


def index_job(job: dict[str, Any], service: Any, backends: dict[str, Any], written: dict[str, str]) -> dict[str, Any]:
    """One audited job's index entry: each execution start mapped to the snapshot export() returns for it."""
    import live_run

    # The backends' calibration history and the job metrics belong to the
    # service's instance, so both reads require the run's recorded instance.
    ibm_account.require_instance(
        ibm_account.recorded_instance(ROOT / job["run"]),
        live_run._instance_hash(service),
        f"{job['job_id']}: calibration history",
    )
    starts = execution_starts(job)
    source = "collect.json pub_timing"
    if not starts:
        running = service.job(job["job_id"]).metrics()["timestamps"]["running"]
        starts = [running if "+" in running or running.endswith("Z") else running + "+00:00"]
        source = "job metrics timestamps.running"
    backend = backends[job["backend"]]
    windows = []
    for start in starts:
        when = datetime.fromisoformat(start.replace("Z", "+00:00"))
        props = backend.properties(datetime=when)
        target = backend.target_history(datetime=when)
        windows.append({"start": start, "snapshot": export(backend, job["backend"], props, target, written)})
    entry = {"job_id": job["job_id"], "run": job["run"], "backend": job["backend"], "start_source": source}
    return entry | {"windows": windows}


def write() -> int:
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = ibm_account.open_service(QiskitRuntimeService)
    backends = {name: service.backend(name) for name in BACKENDS}
    written: dict[str, str] = {}
    jobs = [index_job(job, service, backends, written) for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]]
    current = {}
    for name, backend in backends.items():
        backend.refresh()
        current[name] = export(backend, name, backend.properties(), backend.target, written)
    files = {
        relative: {"calibration": calibration, "sha256": sha256(ROOT / relative)}
        for relative, calibration in sorted(written.items())
    }
    index: dict[str, Any] = {
        "schema": "ghost-calibration-index-v1",
        "retrieved_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "jobs": jobs,
        "current": current,
        "files": files,
    }
    INDEX.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"{len(jobs)} jobs, {len(files)} distinct calibrations")
    return 0


def merged_index(
    index: dict[str, Any], appended: dict[str, Any], jobs: list[dict[str, Any]], digests: dict[str, dict[str, str]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """The index with jobs appended in audit order and their new snapshots listed, and the appended record.

    Every existing job, the current map and every listed file keep their
    entries; files stay in sorted path order, as write() lists them. A window
    on a snapshot appended.json holds moves that snapshot into the index with
    its recorded calibration and sha256, since check() refuses a path both
    indexed and appended. digests gives the calibration and sha256 of every
    other path the new windows name.
    """
    known = {job["job_id"] for job in index["jobs"]}
    require(all(job["job_id"] not in known for job in jobs), "an added job is already indexed")
    require(len({job["job_id"] for job in jobs}) == len(jobs), "an added job repeats")
    named = {w["snapshot"] for job in jobs for w in job["windows"]}
    files = dict(index["files"])
    remaining = dict(appended["files"])
    for relative in sorted(named - set(files)):
        if relative in remaining:
            entry = remaining.pop(relative)
            files[relative] = {"calibration": entry["calibration"], "sha256": entry["sha256"]}
        else:
            require(relative in digests, f"{relative}: no calibration and sha256 for a new snapshot")
            files[relative] = {"calibration": digests[relative]["calibration"], "sha256": digests[relative]["sha256"]}
    out = dict(index, jobs=[*index["jobs"], *jobs], files=dict(sorted(files.items())))
    return out, dict(appended, files=remaining)


def add() -> int:
    """Index the audited jobs index.json lacks and export only the snapshots their execution starts name.

    Read-only against the service, like --write, but every indexed job, the
    current map, retrieved_utc and every retained snapshot keep their bytes:
    export() returns a known calibration identity without rewriting its file.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    appended: dict[str, Any] = {"schema": "ghost-calibration-appended-v1", "files": {}}
    if APPENDED.is_file():
        appended = json.loads(APPENDED.read_text(encoding="utf-8"))
    known = {job["job_id"] for job in index["jobs"]}
    missing = [job for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"] if job["job_id"] not in known]
    if not missing:
        print("ghost calibrations: every audited job is indexed")
        return 0
    service = ibm_account.open_service(QiskitRuntimeService)
    backends = {name: service.backend(name) for name in sorted({job["backend"] for job in missing})}
    written = {relative: entry["calibration"] for relative, entry in index["files"].items()}
    written |= {relative: entry["calibration"] for relative, entry in appended["files"].items()}
    retrieved = datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")
    jobs = [index_job(job, service, backends, written) | {"retrieved_utc": retrieved} for job in missing]
    digests = {
        relative: {"calibration": calibration, "sha256": sha256(ROOT / relative)}
        for relative, calibration in written.items()
        if relative not in index["files"] and relative not in appended["files"]
    }
    out, rest = merged_index(index, appended, jobs, digests)
    INDEX.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    if APPENDED.is_file():
        APPENDED.write_text(json.dumps(rest, indent=1) + "\n", encoding="utf-8")
    print(f"added {len(jobs)} jobs, {len(out['files']) - len(index['files'])} snapshots")
    return 0


def self_test() -> None:
    """merged_index on a synthetic index: existing entries keep their bytes, appended snapshots move, repeats fail."""
    old_job: dict[str, Any] = {
        "job_id": "a",
        "run": "results/live/r0",
        "backend": "ibm_x",
        "windows": [{"start": "s0", "snapshot": "p0"}],
    }
    index: dict[str, Any] = {
        "schema": "ghost-calibration-index-v1",
        "retrieved_utc": "2026-01-01T00:00Z",
        "jobs": [old_job],
        "current": {"ibm_x": "p2"},
        "files": {"p0": {"calibration": "c0", "sha256": "0"}, "p2": {"calibration": "c2", "sha256": "2"}},
    }
    appended: dict[str, Any] = {
        "schema": "ghost-calibration-appended-v1",
        "files": {"p1": {"calibration": "c1", "sha256": "1"}},
    }
    new_job: dict[str, Any] = {
        "job_id": "b",
        "run": "results/live/r1",
        "backend": "ibm_x",
        "windows": [
            {"start": "s1", "snapshot": "p1"},
            {"start": "s2", "snapshot": "p3"},
            {"start": "s3", "snapshot": "p0"},
        ],
    }
    before = json.dumps(index, indent=1)
    out, rest = merged_index(index, appended, [new_job], {"p3": {"calibration": "c3", "sha256": "3"}})
    require(json.dumps(index, indent=1) == before, "self-test: merged_index mutated its input")
    require(out["jobs"] == [old_job, new_job], "self-test: jobs are not the old ones followed by the added one")
    require(out["current"] == index["current"] and out["retrieved_utc"] == index["retrieved_utc"], "self-test: header")
    require(list(out["files"]) == ["p0", "p1", "p2", "p3"], "self-test: files are not in sorted path order")
    require(all(out["files"][k] == v for k, v in index["files"].items()), "self-test: an indexed file changed")
    require(out["files"]["p1"] == {"calibration": "c1", "sha256": "1"}, "self-test: the appended snapshot moved wrong")
    require(rest["files"] == {}, "self-test: the moved snapshot stays appended")
    text = json.dumps(out, indent=1)
    require(text.startswith(before.split('"jobs"')[0]), "self-test: header bytes changed")
    cases: list[tuple[tuple[list[dict[str, Any]], dict[str, dict[str, str]]], str]] = [
        (([old_job], {}), "already indexed"),
        (([new_job, new_job], {"p3": {"calibration": "c3", "sha256": "3"}}), "repeats"),
        (([new_job], {}), "p3: no calibration"),
    ]
    for bad, fragment in cases:
        try:
            merged_index(index, appended, *bad)
        except SystemExit as reason:
            require(fragment in str(reason), f"self-test: {reason} lacks {fragment!r}")
            continue
        raise SystemExit(f"self-test: expected a failure naming {fragment!r}")
    print("ghost calibrations self-test: --add keeps every indexed entry and lists new snapshots in order")


def append() -> int:
    """Read each backend's current calibration and record each new identity in APPENDED."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = ibm_account.open_service(QiskitRuntimeService)
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    record = json.loads(APPENDED.read_text(encoding="utf-8")) if APPENDED.is_file() else {"files": {}}
    # export() returns a known identity without verifying or rewriting it, so
    # a retained snapshot keeps the bytes its recorded sha256 names.
    written = {relative: entry["calibration"] for relative, entry in index["files"].items()}
    written |= {relative: entry["calibration"] for relative, entry in record["files"].items()}
    for name in BACKENDS:
        backend = service.backend(name)
        backend.refresh()
        relative = export(backend, name, backend.properties(), backend.target, written)
        if relative not in index["files"] and relative not in record["files"]:
            record["files"][relative] = {
                "backend": name,
                "calibration": written[relative],
                "sha256": sha256(ROOT / relative),
                "retrieved_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
            }
    record = {"schema": "ghost-calibration-appended-v1", "files": dict(sorted(record["files"].items()))}
    APPENDED.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"appended: {len(record['files'])} snapshots outside the index")
    return 0


def check() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    require(index.get("schema") == "ghost-calibration-index-v1", "unexpected index schema")
    audited = sorted(
        (job["job_id"], job["run"], job["backend"]) for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]
    )
    indexed = sorted((job["job_id"], job["run"], job["backend"]) for job in index["jobs"])
    require(indexed == audited, "index jobs differ from the audit or repeat one")
    referenced = {w["snapshot"] for job in index["jobs"] for w in job["windows"]} | set(index["current"].values())
    require(referenced == set(index["files"]), "index references and files differ")
    for relative, entry in index["files"].items():
        path = ROOT / relative
        require(sha256(path) == entry["sha256"], f"{relative} differs from its recorded sha256")
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        require(snapshot["calibration"] == entry["calibration"], f"{relative}: calibration identity differs")
        calibration_snapshot.round_trip(snapshot)
    appended = json.loads(APPENDED.read_text(encoding="utf-8"))["files"] if APPENDED.is_file() else {}
    on_disk = {path.relative_to(ROOT).as_posix() for name in BACKENDS for path in (HISTORY / name).glob("*.json")}
    unlisted = sorted(on_disk - set(index["files"]) - set(appended))
    require(not unlisted, f"retained snapshots neither indexed nor appended: {unlisted}")
    for relative, entry in appended.items():
        require(relative not in index["files"], f"{relative} is both indexed and appended")
        require(sha256(ROOT / relative) == entry["sha256"], f"{relative} differs from its recorded sha256")
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        require(snapshot["calibration"] == entry["calibration"], f"{relative}: calibration identity differs")
        require(snapshot["backend"] == entry["backend"], f"{relative}: backend differs")
        calibration_snapshot.round_trip(snapshot)
    # live_run --collect records the calibration identity each member's PUB
    # ran under; the snapshot its start maps to must carry that identity.
    starts = {(job["run"], w["start"]): w["snapshot"] for job in index["jobs"] for w in job["windows"]}
    members = 0
    for run in sorted({job["run"] for job in index["jobs"]}):
        path = ROOT / run / "collect.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for collection in data if isinstance(data, list) else [data]:
            for member, executed in (collection.get("executed") or {}).items():
                snapshot = starts.get((run, executed.get("start")))
                require(snapshot is not None, f"{run} {member}: execution start {executed.get('start')} is not indexed")
                recorded = executed.get("calibration")
                require(
                    recorded is None or index["files"][snapshot]["calibration"] == recorded,
                    f"{run} {member}: snapshot {snapshot} differs from the recorded calibration {recorded}",
                )
                members += recorded is not None
    print(
        f"ghost calibrations: {len(index['jobs'])} jobs, {len(index['files'])} indexed and {len(appended)} appended "
        "snapshots round-trip, "
        f"{members} executed members map to their recorded calibration"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--append", action="store_true")
    mode.add_argument("--add", action="store_true", help="index only the audited jobs index.json lacks")
    mode.add_argument("--self-test", action="store_true", help="exercise --add's merge on a synthetic index")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.add:
        return add()
    if args.append:
        return append()
    return write() if args.write else check()


if __name__ == "__main__":
    sys.exit(main())
