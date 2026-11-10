"""Kaggle CPU kernel body of the E8-bar -> VB export-lever campaign.

make_kernels.py writes one kernel per prime from this file, replacing CONFIG_B64 with the base64 of its job list. The
kernel installs passagemath Singular 4.4.1, runs every job four at a time and writes /kaggle/working/summary.json.
It exits 1 when any job failed (see `failures`), so a failed export never reads as a successful kernel.

Kaggle stops a CPU session at 12 hours. Every job gets the smaller of its own deadline and the time left before
SESSION_SECONDS (12 h less a margin for setup and the final write), so the kernel always ends by itself, and
summary.json is rewritten after every finished job, so a session that ends early keeps every finished result.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import sysconfig
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

CONFIG_B64 = ""
OUT = Path("/kaggle/working")
DIGESTS = ("s.txt", "kbase.txt")
SESSION_SECONDS = 12 * 3600 - 1200


def failures(jobs: dict[str, dict[str, Any]]) -> list[str]:
    """Jobs that did not finish: a nonzero exit (124 for the deadline), no RESULT line (Singular exits 0 on
    SIGTERM), or a missing output digest."""
    return [
        name
        for name, job in jobs.items()
        if job["rc"] != 0 or not job["results"] or any(f not in job["sha256"] for f in DIGESTS)
    ]


def _singular() -> Path:
    paths = sysconfig.get_paths()
    candidates = (Path(paths[key]) / "sage_wheels" / "bin" / "Singular" for key in ("purelib", "platlib"))
    return next(path for path in candidates if path.exists())


def _seconds_left(started: float, seconds: int) -> int:
    """The job deadline: its own limit, cut to the session time left (at least 1 s, so `timeout` ends it at once)."""
    return max(1, min(seconds, int(SESSION_SECONDS - (time.time() - started))))


def _run(binary: Path, seconds: int, job: dict[str, str]) -> tuple[str, dict[str, Any]]:
    work = OUT / job["name"]
    work.mkdir(parents=True, exist_ok=True)
    (work / "input.sing").write_text(job["script"])
    start = time.time()
    command = ["timeout", "-k", "30", str(seconds), str(binary), "-q", "--no-rc", "input.sing"]
    done = subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
    (work / "out.log").write_text(done.stdout + done.stderr)
    digests = {f: hashlib.sha256((work / f).read_bytes()).hexdigest() for f in DIGESTS if (work / f).exists()}
    results = [line for line in done.stdout.splitlines() if line.startswith("RESULT")]
    record = {"rc": done.returncode, "seconds": round(time.time() - start, 1), "sha256": digests, "results": results}
    return job["name"], record


def main() -> None:
    config = json.loads(base64.b64decode(CONFIG_B64))
    started = time.time()
    install = [sys.executable, "-m", "pip", "install", "-q", "passagemath-singular==10.8.13"]
    subprocess.run(install, check=True)
    binary = _singular()
    version = subprocess.run(
        [str(binary), "--dump-versiontuple"], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False
    )
    jobs: dict[str, dict[str, Any]] = {}
    lock = threading.Lock()

    def write() -> dict[str, object]:
        summary: dict[str, object] = {
            "cpu_count": os.cpu_count(),
            "singular": version.stdout.strip(),
            "jobs": dict(jobs),
            "pending": [job["name"] for job in config["jobs"] if job["name"] not in jobs],
            "failed": failures(jobs),
            "total_seconds": round(time.time() - started, 1),
        }
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
        return summary

    def one(job: dict[str, str]) -> None:
        name, record = _run(binary, _seconds_left(started, config["job_seconds"]), job)
        with lock:
            jobs[name] = record
            write()

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, config["jobs"]))
    summary = write()
    print(json.dumps(summary, indent=1))
    if summary["failed"] or summary["pending"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
