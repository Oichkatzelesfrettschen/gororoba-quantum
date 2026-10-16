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
live_run's noise model built from the same fetch. It also exports each
backend's current calibration, and writes index.json mapping every job and
PUB start to its snapshot. ``--check`` needs no network: every indexed file
exists with its recorded sha256, rebuilds its Target, and the index covers
exactly the audited jobs.
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

AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
HISTORY = ROOT / "docs/evidence/calibration/history"
INDEX = HISTORY / "index.json"
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


def export(backend: Any, name: str, props: Any, target: Any, written: dict[str, str]) -> str:
    """Snapshot of one fetched calibration, verified against live_run's noise model; returns its path."""
    import live_run

    snapshot = json.loads(json.dumps(calibration_snapshot.describe(name, target, props, live_run.readout_flips)))
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


def write() -> int:
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    backends = {name: service.backend(name) for name in BACKENDS}
    written: dict[str, str] = {}
    jobs = []
    for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]:
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
        jobs.append(entry | {"windows": windows})
    current = {}
    for name, backend in backends.items():
        backend.refresh()
        current[name] = export(backend, name, backend.properties(), backend.target, written)
    files = {
        relative: {"calibration": calibration, "sha256": sha256(ROOT / relative)}
        for relative, calibration in sorted(written.items())
    }
    index = {
        "schema": "ghost-calibration-index-v1",
        "retrieved_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "jobs": jobs,
        "current": current,
        "files": files,
    }
    INDEX.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"{len(jobs)} jobs, {len(files)} distinct calibrations")
    return 0


def check() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    require(index.get("schema") == "ghost-calibration-index-v1", "unexpected index schema")
    audited = {(job["job_id"], job["run"]) for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]}
    require({(job["job_id"], job["run"]) for job in index["jobs"]} == audited, "index jobs differ from the audit")
    referenced = {w["snapshot"] for job in index["jobs"] for w in job["windows"]} | set(index["current"].values())
    require(referenced == set(index["files"]), "index references and files differ")
    for relative, entry in index["files"].items():
        path = ROOT / relative
        require(sha256(path) == entry["sha256"], f"{relative} differs from its recorded sha256")
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        require(snapshot["calibration"] == entry["calibration"], f"{relative}: calibration identity differs")
        calibration_snapshot.round_trip(snapshot)
    print(f"ghost calibrations: {len(index['jobs'])} jobs, {len(index['files'])} snapshots round-trip")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write() if args.write else check()


if __name__ == "__main__":
    sys.exit(main())
