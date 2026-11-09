"""Kaggle CPU kernel body of the E8-bar -> VB export-lever campaign.

make_kernels.py writes one kernel per prime from this file, replacing CONFIG_B64 with the base64 of its job list. The
kernel installs passagemath Singular 4.4.1, runs every job four at a time and writes /kaggle/working/summary.json.
It exits 1 when any job failed (see `failures`), so a failed export never reads as a successful kernel.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import sysconfig
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

CONFIG_B64 = ""
OUT = Path("/kaggle/working")
DIGESTS = ("s.txt", "kbase.txt")


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
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = dict(pool.map(lambda job: _run(binary, config["job_seconds"], job), config["jobs"]))
    summary: dict[str, object] = {
        "cpu_count": os.cpu_count(),
        "singular": version.stdout.strip(),
        "jobs": jobs,
        "failed": failures(jobs),
        "total_seconds": round(time.time() - started, 1),
    }
    text = json.dumps(summary, indent=1)
    (OUT / "summary.json").write_text(text)
    print(text)
    if summary["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
