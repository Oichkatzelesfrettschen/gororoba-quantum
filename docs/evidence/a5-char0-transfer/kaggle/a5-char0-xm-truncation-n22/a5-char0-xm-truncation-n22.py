"""Kaggle CPU kernel body of one characteristic-0 check of X- -> N-.

make_kernels.py writes one kernel per check from this file, replacing CONFIG_B64 with the base64 of its configuration
(branch, pinned commit, repository, driver arguments, record name). The kernel fetches that commit of the public
repository, installs passagemath Singular 4.4.1, sympy and python-flint, puts a `systemd-run` shim on PATH (the
drivers wrap Singular in a user scope that a Kaggle container lacks; the shim drops the scope options so the session's
own RAM bounds Singular) and runs the driver unchanged. It copies the driver's record and log to /kaggle/working and
exits 1 unless the driver exited 0 and wrote a record with a verdict (see `failed`).

Three limits end a run, in this order. The driver's own --timeout (rewritten here to the time left) ends Singular and
writes a `blocked_timeout` record. `timeout` around the driver fires 300 s later. The Kaggle run-time limit of the
push (`kaggle kernels push --timeout 41400`, 11.5 hours, SESSION_SECONDS) fires last and cancels the session; a
cancelled session keeps the files already written to /kaggle/working and nothing a process still held in memory.

Every stream is therefore written to /kaggle/working as it is produced: driver.log holds the driver's output,
singular.log the output of every Singular call (the `systemd-run` shim tees it, line-buffered; the driver's STAGE
lines carry its position and Singular's wall clock), and summary.json is rewritten every minute with the stage,
the elapsed seconds and the last line of each log. A session that ends early shows how far it got.
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

CONFIG_B64 = (
    "eyJicmFuY2giOiAiYTUtY2hhcjAtcXVhZHJpY3MtaXNvLXc4IiwgImNvbW1pdCI6ICIwMGI3ZDYzYzI2MTUzNWQzMjhmNzMzNjlm"
    "YmE1NGFlN2Q1MTJkNjRkIiwgInJlcG8iOiAiaHR0cHM6Ly9naXRodWIuY29tL09pY2hrYXR6ZWxlc2ZyZXR0c2NoZW4vZ29yb3Jv"
    "YmEtcXVhbnR1bSIsICJhcmdzIjogWyJkb2NzL2V2aWRlbmNlL2E1LWNoYXIwLXRyYW5zZmVyL3RydW5jYXRpb25fY2hlY2sucHki"
    "LCAiLS1zbHVnIiwgInhtLW5tIiwgIi0tb3JkZXIiLCAiMjIiLCAiLS10aW1lb3V0IiwgIjIwMDAwIl0sICJyZWNvcmQiOiAidHJ1"
    "bmNhdGlvbi14bS1ubS1uMjIuanNvbiJ9"
)
OUT = Path("/kaggle/working")
WORK = Path("/kaggle/tmp")
SESSION_SECONDS = 41400
STOP_MARGIN = 600
DRIVER_MARGIN = 300
HEARTBEAT_SECONDS = 60


def shim(out: Path) -> str:
    """The systemd-run stand-in: it runs the Singular command with stdout and stderr appended to logs under OUT.

    Both streams reach their file as Singular writes them, so a kill of the driver, whose pipes hold the only other
    copy, leaves every line written before it.
    """
    return (
        "#!/bin/bash\n"
        'while [ "$#" -gt 0 ] && [ "$1" != Singular ]; do shift; done\n'
        f'exec stdbuf -oL -eL "$@" > >(tee -a {out}/singular.log) 2> >(tee -a {out}/singular.stderr.log >&2)\n'
    )


def run_logged(command: list[str], log: Path, check: bool = True) -> None:
    """Runs a setup command with its output appended to LOG, so a failed fetch or install leaves its message."""
    with log.open("a") as handle:
        handle.write("+ " + " ".join(command) + "\n")
        handle.flush()
        subprocess.run(command, check=check, stdout=handle, stderr=subprocess.STDOUT)  # noqa: S603


def last_line(path: Path) -> str:
    """The last nonempty line of a log, cut to 300 characters; empty when the log is absent."""
    if not path.exists():
        return ""
    with path.open("rb") as handle:
        handle.seek(max(0, path.stat().st_size - 4096))
        lines = [line for line in handle.read().decode("utf-8", "replace").splitlines() if line.strip()]
    return lines[-1][:300] if lines else ""


def driver_args(args: list[str], seconds: int) -> list[str]:
    """The driver arguments with the value of --timeout replaced by the seconds left for it."""
    out = list(args)
    if "--timeout" in out:
        out[out.index("--timeout") + 1] = str(seconds)
    return out


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
    (OUT / "summary.json").write_text(json.dumps({"args": config["args"], "stage": "setup"}, indent=1))
    WORK.mkdir(parents=True, exist_ok=True)
    repo = WORK / "repo"
    # Fetch the pinned commit alone (GitHub serves a full sha), so the kernel replays the same drivers after the branch
    # moves or merges.
    for command in (
        ["git", "init", "-q", str(repo)],
        ["git", "-C", str(repo), "fetch", "-q", "--depth", "1", "--filter=blob:none", config["repo"], config["commit"]],
        ["git", "-C", str(repo), "checkout", "-q", "FETCH_HEAD"],
    ):
        run_logged(command, OUT / "setup.log")
    packages = ["passagemath-singular==10.8.13", "python-flint==0.9.0", "sympy"]
    run_logged([sys.executable, "-m", "pip", "install", "-q", *packages], OUT / "setup.log")
    if not Path("/usr/bin/time").exists():
        run_logged(["apt-get", "install", "-y", "-q", "time"], OUT / "setup.log", check=False)
    shims = WORK / "bin"
    shims.mkdir(exist_ok=True)
    (shims / "Singular").symlink_to(_singular())
    (shims / "systemd-run").write_text(shim(OUT))
    (shims / "systemd-run").chmod(0o755)
    env = dict(os.environ, PATH=f"{shims}:{os.environ['PATH']}", GLIBC_TUNABLES="glibc.rtld.optional_static_tls=4096")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True)
    start = time.time()
    budget = int(SESSION_SECONDS - STOP_MARGIN - (time.time() - started))
    args = driver_args(config["args"], budget - DRIVER_MARGIN)
    state = {"repo_head": head.stdout.strip(), "args": args, "stage": "driver", "cpu_count": os.cpu_count()}
    with (OUT / "driver.log").open("w") as log:
        process = subprocess.Popen(
            ["timeout", "-k", "60", str(budget), sys.executable, "-u", *args],
            cwd=repo,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        while True:
            try:
                returncode = process.wait(timeout=HEARTBEAT_SECONDS)
                break
            except subprocess.TimeoutExpired:
                beat = {
                    **state,
                    "seconds": round(time.time() - start, 1),
                    "total_seconds": round(time.time() - started, 1),
                    "driver_last": last_line(OUT / "driver.log"),
                    "singular_last": last_line(OUT / "singular.log"),
                }
                (OUT / "summary.json").write_text(json.dumps(beat, indent=1))
                print(json.dumps(beat), flush=True)
    source = repo / "docs" / "evidence" / "a5-char0-transfer" / config["record"]
    record = json.loads(source.read_text()) if source.exists() else None
    if source.exists():
        shutil.copy(source, OUT / source.name)
    summary = {
        "repo_head": head.stdout.strip(),
        "args": args,
        "stage": "finished",
        "rc": returncode,
        "verdict": record.get("verdict") if record else None,
        "failed": failed(returncode, record),
        "seconds": round(time.time() - start, 1),
        "total_seconds": round(time.time() - started, 1),
        "cpu_count": os.cpu_count(),
        "singular_last": last_line(OUT / "singular.log"),
    }
    text = json.dumps(summary, indent=1)
    (OUT / "summary.json").write_text(text)
    print(text)
    if summary["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
