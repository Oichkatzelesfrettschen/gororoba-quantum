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

CONFIG_B64 = (
    "eyJqb2JzIjogW3sibmFtZSI6ICJzbGltZ2ItbjIxLXAzMjAyOSIsICJzY3JpcHQiOiAicmluZyByPTMyMDI5LCh0MSx0Mix0Myx0"
    "NCx0NSx0Nix0Nyx0OCksZHA7XG5pZGVhbCBKPXQzXjItdDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIq"
    "dDgsdDQqdDUqdDgtdDMqdDYqdDgtdDMqdDUtdDQqdDUrdDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUq"
    "dDYrdDZeMix0Myp0NCp0OC10NSp0Nip0OC10Myp0NC10NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEq"
    "dDUtdDEqdDYtMip0NCp0OCx0MSp0NCp0OCt0Mip0Nip0OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1"
    "KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2LTIqdDMqdDgsdDEqdDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0"
    "Mip0Myp0NSt0MSp0NV4yLXQyKnQ0KnQ2LXQxKnQ2XjItMip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3Qx"
    "KnQzKnQ1K3QyKnQ1XjIrdDEqdDQqdDYtMip0Myp0NC0yKnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEq"
    "dDMqdDYrdDIqdDUqdDYtMip0Myp0NC0yKnQ0XjItMip0NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDhe"
    "Myt0Ml4yLTQqdDIqdDgsdDYqdDdeMip0OC10Nip0OF4zLXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIr"
    "Myp0Nip0OF4yKzIqdDEqdDMrMip0MSp0NCs0KnQyKnQ1LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDhe"
    "My10MSp0Mip0NC10Ml4yKnQ2LXQ1KnQ3XjIrdDYqdDdeMiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0"
    "NSs0KnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NCp0N14yKnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3"
    "XjIrdDMqdDheMiszKnQ0KnQ4XjItNCp0Mip0My0yKnQyKnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDde"
    "Mip0OC10Myp0OF4zK3QyXjIqdDQrdDEqdDIqdDYtdDMqdDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0"
    "Mip0NCsyKnQxKnQ1LTIqdDEqdDYrMip0Myp0OC0yKnQ0KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXIt"
    "c2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDIxKSk7XG5cIlJFU1VMVCBtc1wi"
    "LHJ0aW1lci10MCxcInNiX3NpemVcIixuY29scyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixu"
    "Y29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjEtcDMyMDI5L3MudHh0XCIscyk7"
    "IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjEtcDMyMDI5L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7"
    "Im5hbWUiOiAic2xpbWdiLW4yMi1wMzIwMjkiLCAic2NyaXB0IjogInJpbmcgcj0zMjAyOSwodDEsdDIsdDMsdDQsdDUsdDYsdDcs"
    "dDgpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjItdDVeMit0Nl4yLHQxXjItdDJeMit0N14yLXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4"
    "LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2K3Q0KnQ2LHQ0XjIqdDgtdDZeMip0OC10Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMq"
    "dDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10NV4yK3Q1KnQ2LHQyKnQ0KnQ4K3QxKnQ2KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIq"
    "dDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEqdDMtdDEqdDQtdDIqdDYtMip0Nip0OCx0Mip0Myp0OCt0MSp0NSp0OC10Mip0My10"
    "MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4K3QyKnQ1KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEq"
    "dDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMqdDUtMip0NCp0NSsyKnQzKnQ2KzIqdDQqdDYsdDIqdDReMit0MSp0Myp0NSt0Mip0"
    "NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDVeMisyKnQ1KnQ2LHQyKnQzKnQ0K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1"
    "KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYrMip0Nl4yLHQ3XjIqdDheMi10OF40LTIqdDdeMip0OCs0KnQ4XjMrdDJeMi00KnQy"
    "KnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0Mip0My10Ml4yKnQ1K3Q1KnQ3XjItdDYqdDdeMi10NSp0OF4yKzMqdDYqdDheMisy"
    "KnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NSp0N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQt"
    "dDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0NSp0OF4yLXQ2KnQ4XjIrMip0MSp0MysyKnQxKnQ0LTIqdDIqdDUrNCp0Mip0Nisy"
    "KnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10NCp0OF4zK3QyXjIqdDMrdDEqdDIqdDUtdDMqdDdeMi10NCp0N14yK3QzKnQ4XjIr"
    "Myp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0yKnQxKnQ1KzIqdDEqdDYtMip0Myp0OCsyKnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDhe"
    "Myt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjItdDQqdDdeMiszKnQzKnQ4XjIrdDQqdDheMi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0"
    "NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtcbm9wdGlvbihyZWRTQik7IHN5c3RlbShcIi0tdGlja3MtcGVyLXNlY1wiLDEwMDAp"
    "OyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1zbGltZ2IoSittYXhpZGVhbCgyMikpO1xuXCJSRVNVTFQgbXNcIixydGltZXItdDAs"
    "XCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVhbCBCPWtiYXNlKHMpOyBcIlJFU1VMVCBrYmFzZV9zaXplXCIsbmNvbHMoQik7XG5z"
    "aG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9zbGltZ2ItbjIyLXAzMjAyOS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3"
    "IC9rYWdnbGUvd29ya2luZy9zbGltZ2ItbjIyLXAzMjAyOS9rYmFzZS50eHRcIixCKTtcbnF1aXQ7XG4ifV0sICJqb2Jfc2Vjb25k"
    "cyI6IDQxMDAwfQ=="
)
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
