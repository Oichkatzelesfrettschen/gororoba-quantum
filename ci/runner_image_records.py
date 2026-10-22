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

``"$PYTHON" ci/runner_image_records.py add PATH...`` binds records just
written under the current digest. Once the digest moves, ``add`` accepts
only a set of paths that covers every bound record, so the ledger advances
to the new image in one step after all of them are rewritten. ``check``
verifies the ledger; ``id`` prints the current digest.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from unittest import mock

import run_gates

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ci" / "runner_image_records.json"
SCHEMA = "runner-image-records-v1"
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
    records = ledger.get("records", {})
    if not isinstance(records, dict):
        return ["the ledger's records is not a map"]
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


def main(argv: list[str]) -> int:
    command, paths = (argv[0], argv[1:]) if argv else ("", [])
    if command == "id":
        print(image_id())
        return 0
    ledger = read()
    if command == "check":
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
        for name in sorted(named):
            records[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        text = json.dumps({"schema": SCHEMA, "image": current, "records": dict(sorted(records.items()))}, indent=1)
        LEDGER.write_text(text + "\n")
        return 0
    raise SystemExit("usage: runner_image_records.py id | check | add PATH...")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
