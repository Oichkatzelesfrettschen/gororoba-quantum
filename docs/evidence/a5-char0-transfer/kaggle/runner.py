"""Kaggle CPU kernel body of one characteristic-0 check of X- -> N-.

make_kernels.py writes one kernel per check from this file, replacing CONFIG_B64 with the base64 of its configuration
(branch, pinned commit, repository, driver arguments, record name). The kernel fetches that commit of the public
repository, installs passagemath Singular 4.4.1, sympy and python-flint, puts a `systemd-run` shim on PATH (the drivers wrap Singular in a
user scope that a Kaggle container lacks; the shim drops the scope options so the session's own RAM bounds Singular)
and runs the driver unchanged. It copies the driver's record and log to /kaggle/working and exits 1 unless the driver
exited 0 and wrote a record with a verdict (see `failed`).
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import time
from pathlib import Path

CONFIG_B64 = ""
OUT = Path("/kaggle/working")
WORK = Path("/kaggle/tmp")
SHIM = '#!/bin/sh\nwhile [ "$#" -gt 0 ] && [ "$1" != Singular ]; do shift; done\nexec "$@"\n'


def failed(rc: int, record: dict[str, object] | None) -> bool:
    """A check failed when its driver exited nonzero, wrote no record, or wrote one without a verdict."""
    return rc != 0 or record is None or "verdict" not in record


def _singular() -> Path:
    paths = sysconfig.get_paths()
    candidates = (Path(paths[key]) / "sage_wheels" / "bin" / "Singular" for key in ("purelib", "platlib"))
    return next(path for path in candidates if path.exists())


def main() -> None:
    config = json.loads(base64.b64decode(CONFIG_B64))
    started = time.time()
    WORK.mkdir(parents=True, exist_ok=True)
    repo = WORK / "repo"
    # Fetch the pinned commit alone (GitHub serves a full sha), so the kernel replays the same drivers after the branch
    # moves or merges.
    for command in (
        ["git", "init", "-q", str(repo)],
        ["git", "-C", str(repo), "fetch", "-q", "--depth", "1", "--filter=blob:none", config["repo"], config["commit"]],
        ["git", "-C", str(repo), "checkout", "-q", "FETCH_HEAD"],
    ):
        subprocess.run(command, check=True)
    packages = ["passagemath-singular==10.8.13", "python-flint==0.9.0", "sympy"]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *packages], check=True)
    if not Path("/usr/bin/time").exists():
        subprocess.run(["apt-get", "install", "-y", "-q", "time"], check=False)
    shims = WORK / "bin"
    shims.mkdir(exist_ok=True)
    (shims / "Singular").symlink_to(_singular())
    (shims / "systemd-run").write_text(SHIM)
    (shims / "systemd-run").chmod(0o755)
    env = dict(os.environ, PATH=f"{shims}:{os.environ['PATH']}", GLIBC_TUNABLES="glibc.rtld.optional_static_tls=4096")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True)
    start = time.time()
    done = subprocess.run(
        [sys.executable, *config["args"]],
        cwd=repo,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    (OUT / "driver.log").write_text(done.stdout + done.stderr)
    source = repo / "docs" / "evidence" / "a5-char0-transfer" / config["record"]
    record = json.loads(source.read_text()) if source.exists() else None
    if source.exists():
        shutil.copy(source, OUT / source.name)
    summary = {
        "repo_head": head.stdout.strip(),
        "args": config["args"],
        "rc": done.returncode,
        "verdict": record.get("verdict") if record else None,
        "failed": failed(done.returncode, record),
        "seconds": round(time.time() - start, 1),
        "total_seconds": round(time.time() - started, 1),
        "cpu_count": os.cpu_count(),
    }
    text = json.dumps(summary, indent=1)
    (OUT / "summary.json").write_text(text)
    print(text)
    if summary["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
