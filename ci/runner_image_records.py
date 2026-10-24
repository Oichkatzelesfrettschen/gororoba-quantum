"""The records written in the runner image (ci/runner_image.sh), bound to that image and its pins.

A fitted float byte-replays only under the arithmetic that wrote it: the
libm, Python build, numpy, scipy and OpenBLAS of ci/runner-image/Containerfile
and ci/install_pins.sh. ci/runner_image_records.json binds each such record's
sha256 to the digest of IMAGE_INPUTS (the image, the pins, the script that
runs the producer and the gate environment it runs under) and of the
arithmetic variables run_gates.environment_for assigns; ``check`` (a pr gate)
fails once any of them or a record changes, naming the records to rewrite
through ci/runner_image.sh, before their replay gates report float
differences.

``"$PYTHON" ci/runner_image_records.py write COMMAND...`` runs COMMAND
through ci/runner_image.sh over a snapshot of the tree, copies back every
file the command wrote there and appends a receipt (path, sha256, image
digest) for each to RECEIPTS.
``"$PYTHON" ci/runner_image_records.py add PATH...`` binds records under the
current digest and refuses a path whose bytes carry no receipt for it, so a
record written by a host interpreter, whose libm and Python build differ from
the runner's, never enters the ledger. Once the digest moves, ``add`` accepts
only a set of paths that covers every bound record, so the ledger advances
to the new image in one step after all of them are rewritten. ``check``
verifies the ledger; ``id`` prints the current digest.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest import mock

import run_gates

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ci" / "runner_image_records.json"
SCHEMA = "runner-image-records-v1"
# Receipts live beside the image and its pin venvs, outside every checkout, so a worktree's removal keeps them.
RECEIPTS = (
    Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    / "gororoba-quantum"
    / "runner-image"
    / "receipts.jsonl"
)
IMAGE_INPUTS = (
    "ci/runner-image/Containerfile",
    "requirements.txt",
    "ci/requirements-ci.txt",
    "ci/install_pins.sh",
    "ci/runner_image.sh",
    "ci/gate_env.py",
)
# The variables of run_gates.environment_for that select a kernel, a thread count or the TLS reservation.
ARITHMETIC_VARIABLES = (
    "BLIS_NUM_THREADS",
    "GLIBC_TUNABLES",
    "MKL_NUM_THREADS",
    "NPY_DISABLE_CPU_FEATURES",
    "NUMEXPR_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_CORETYPE",
    "OPENBLAS_NUM_THREADS",
    "QISKIT_NUM_PROCS",
    "RAYON_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def arithmetic_environment() -> dict[str, str]:
    """The arithmetic variables a gate receives from an empty caller environment."""
    with mock.patch.dict("os.environ", {}, clear=True):
        environment = run_gates.environment_for(None)
    return {name: environment[name] for name in ARITHMETIC_VARIABLES}


def requirement_lines(data: bytes) -> bytes:
    """The lines pip installs from a requirements file: comments and blank lines drop out."""
    lines = (line.split(b"#", 1)[0].strip() for line in data.splitlines())
    return b"\n".join(line for line in lines if line)


def image_id(root: Path = ROOT) -> str:
    """sha256 over each image input's path and content, the patches of ci/patches/ in name order, then the
    arithmetic environment.

    A requirements file contributes its requirement lines alone, so a comment edit leaves the installed
    packages, and the digest, unchanged.
    """
    paths = [root / name for name in IMAGE_INPUTS] + sorted((root / "ci" / "patches").iterdir())
    digest = hashlib.sha256()
    for path in paths:
        data = path.read_bytes()
        content = requirement_lines(data) if path.suffix == ".txt" else data
        digest.update(path.relative_to(root).as_posix().encode() + b"\0" + content + b"\0")
    digest.update(json.dumps(arithmetic_environment(), sort_keys=True).encode())
    return digest.hexdigest()


def read(root: Path | None = None) -> dict[str, Any]:
    path = LEDGER if root is None else root / LEDGER.relative_to(ROOT)
    if not path.exists():
        return {"schema": SCHEMA, "image": None, "records": {}}
    return dict(json.loads(path.read_text()))


def problems(ledger: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Each way the ledger fails to bind its records to the current image; a ledger binding no record fails,
    so deleting or emptying ci/runner_image_records.json cannot pass ``check``."""
    if ledger.get("schema") != SCHEMA:
        return [f"the ledger's schema is {ledger.get('schema')!r}, not {SCHEMA}"]
    records = ledger.get("records", {})
    if not isinstance(records, dict):
        return ["the ledger's records is not a map"]
    if not records:
        return ["the ledger binds no record; bind each runner-image record with `add`"]
    found = []
    current = image_id(root)
    if records and ledger.get("image") != current:
        found.append(
            f"the runner image or pins changed ({ledger.get('image')} -> {current}); rewrite every record "
            "below with ci/runner_image.sh and bind them all again with one `add`"
        )
    for name, digest in sorted(records.items()):
        path = root / name
        if not path.is_file():
            found.append(f"{name}: missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            found.append(f"{name}: bytes differ from the ledger")
        elif found and found[0].startswith("the runner image"):
            found.append(f"{name}: written under {ledger.get('image')}")
    return found


def written_since(start_ns: int, root: Path) -> list[Path]:
    """Every file under root, .git and bytecode caches excepted, whose modification time is at or after start_ns."""
    found = []
    for directory, names, files in os.walk(root):
        names[:] = [name for name in names if name not in {".git", "__pycache__"}]
        for name in files:
            path = Path(directory) / name
            if path.is_file() and not path.is_symlink() and path.stat().st_mtime_ns >= start_ns:
                found.append(path)
    return sorted(found)


def write(command: list[str]) -> int:
    """Run command in the runner image over a snapshot of the tree, then copy back and receipt what it wrote.

    The container mounts the snapshot, which no host process touches, so a file the snapshot gains or rewrites
    after the run starts came from the container. .git stays out of the snapshot; the image carries no git.
    """
    image = image_id()
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    snapshot = Path(tempfile.mkdtemp(prefix="write-", dir=RECEIPTS.parent))
    try:
        shutil.copytree(ROOT, snapshot, symlinks=True, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
        # The kernel stamps a write with its coarse clock, which trails time.time_ns() by at most one tick (10 ms at
        # HZ=100, the lowest tick rate Linux builds with); the pause puts every copied file's time below the margin.
        time.sleep(0.05)
        start = time.time_ns() - 10_000_000
        status = subprocess.run(["sh", str(snapshot / "ci" / "runner_image.sh"), *command], cwd=snapshot, check=False)
        if status.returncode != 0:
            return status.returncode
        rows = []
        for path in written_since(start, snapshot):
            name = path.relative_to(snapshot).as_posix()
            (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, ROOT / name)
            rows.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "image": image})
    finally:
        shutil.rmtree(snapshot)
    with RECEIPTS.open("a", encoding="utf-8") as stream:
        stream.writelines(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    return 0


def receipted(name: str, digest: str, image: str) -> bool:
    """Whether a receipt shows ci/runner_image.sh writing these bytes at this path under this image."""
    if not RECEIPTS.is_file():
        return False
    wanted = {"path": name, "sha256": digest, "image": image}
    return any(json.loads(line) == wanted for line in RECEIPTS.read_text(encoding="utf-8").splitlines() if line)


def main(argv: list[str]) -> int:
    command, paths = (argv[0], argv[1:]) if argv else ("", [])
    if command == "id":
        print(image_id())
        return 0
    if command == "write" and paths:
        return write(paths)
    ledger = read()
    if command == "check":
        if not LEDGER.is_file():
            print(f"{LEDGER.relative_to(ROOT)} is missing")
            return 1
        found = problems(ledger)
        for line in found:
            print(line)
        return 1 if found else 0
    if command == "add" and paths:
        records = dict(ledger.get("records", {}))
        current = image_id()
        named = {(Path.cwd() / name).resolve().relative_to(ROOT).as_posix() for name in paths}
        if records and ledger.get("image") != current:
            # A new image rebinds the ledger only when every record bound under the old one is supplied again.
            left = sorted(set(records) - named)
            if left:
                raise SystemExit("\n".join([*problems(ledger), f"add every bound record at once; missing: {left}"]))
            records = {}
        digests = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(named)}
        unreceipted = [name for name, digest in digests.items() if not receipted(name, digest, current)]
        if unreceipted:
            raise SystemExit(
                f"no runner-image receipt for these bytes: {unreceipted}; write each record with "
                '`"$PYTHON" ci/runner_image_records.py write sh -c \'"$PYTHON" PRODUCER ...\'`'
            )
        records.update(digests)
        text = json.dumps({"schema": SCHEMA, "image": current, "records": dict(sorted(records.items()))}, indent=1)
        LEDGER.write_text(text + "\n")
        return 0
    raise SystemExit("usage: runner_image_records.py id | check | add PATH... | write COMMAND...")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
