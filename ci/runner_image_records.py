"""The records written in the runner image (ci/runner_image.sh), bound to that image and its pins.

A fitted float byte-replays only under the arithmetic that wrote it: the
libm, Python build, numpy, scipy and OpenBLAS of ci/runner-image/Containerfile
and ci/install_pins.sh. ci/runner_image_records.json binds each such record's
sha256 to the digest of IMAGE_INPUTS (the image, the pins, the script that
runs the producer and the gate environment it runs under) and of
LEDGER_ARITHMETIC, the kernel, thread and loader variables every record of
the ledger was written under; ``check`` (a pr gate)
fails once any of them or a record changes, naming the records to rewrite
through ci/runner_image.sh, before their replay gates report float
differences.

``"$PYTHON" ci/runner_image_records.py write COMMAND...`` runs COMMAND
under LEDGER_ARITHMETIC through ci/runner_image.sh over a snapshot of the tree, copies back every
file the command wrote there and appends a receipt (path, sha256, image
digest) for each to RECEIPTS.
``"$PYTHON" ci/runner_image_records.py add PATH...`` binds records under the
current digest and refuses a path whose bytes carry no receipt for it, so a
record written by a host interpreter, whose libm and Python build differ from
the runner's, never enters the ledger. Once the digest moves, ``add`` accepts
only a set of paths that covers every bound record, so the ledger advances
to the new image in one step after all of them are rewritten. ``check``
verifies the ledger and the replay declarations of ci/gates.json; ``id``
prints the current digest.

A gate that byte-compares a retained record names it in its ``replays``
list. ``replay_problems`` requires each gate whose command compares a record
through ``ci/replay_check.py RETAINED``, ``| cmp - FILE`` or ``--out FILE``
beside ``--check`` or ``--replay`` to declare that record, each declared
record (each file of a declared directory) to be bound in this ledger, to
be JSON holding no float, or to carry a reason under the ledger's ``exempt``
map, and each bound record to be declared by some gate. A float record outside the ledger escapes the image
rebinding that keeps its replay exact, and a bound record no gate replays
forces rewrites that verify nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ci" / "runner_image_records.json"
GATES = ROOT / "ci" / "gates.json"
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
# The kernel, thread and loader variables the ledger's records were written under: the OpenBLAS Haswell core and
# numpy's x86-64-v3 dispatch cap select one AVX2 path, and single-threaded libraries fix the reduction order. The
# ledger declares them rather than reading run_gates.environment_for, so a gate environment that computes on the
# runner's native path leaves the digest, and every record ``write`` reproduces, on this path
# (docs/design/native-numeric-replay.md).
LEDGER_ARITHMETIC = {
    "BLIS_NUM_THREADS": "1",
    "GLIBC_TUNABLES": "glibc.rtld.optional_static_tls=4096",
    "MKL_NUM_THREADS": "1",
    "NPY_DISABLE_CPU_FEATURES": "X86_V4 AVX512_ICL AVX512_SPR",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_CORETYPE": "Haswell",
    "OPENBLAS_NUM_THREADS": "1",
    "QISKIT_NUM_PROCS": "1",
    "RAYON_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


def arithmetic_environment() -> dict[str, str]:
    """The arithmetic variables every record of the ledger was written under."""
    return dict(LEDGER_ARITHMETIC)


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


def compared_records(gate: dict[str, Any]) -> list[str]:
    """The repository-relative records a gate's command compares through ci/replay_check.py, ``| cmp -`` or
    --out beside --check or --replay; a producer that compares a path it names internally declares it by hand.
    A path under a shell variable names a scratch output, not a record."""
    lexer = shlex.shlex(gate["cmd"], posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    segments: list[list[str]] = [[]]
    for token in lexer:
        if token in {"&&", "||", ";"}:
            segments.append([])
        else:
            segments[-1].append(token)
    found = []
    for words in segments:
        named = []
        for index, word in enumerate(words[:-1]):
            if word.endswith("replay_check.py"):
                named.append(words[index + 1])
            # cmp of two stored files proves a copy; cmp of standard input or of a scratch output under a shell
            # variable compares a fresh output with the record.
            if word == "cmp" and index + 2 < len(words) and (words[index + 1] == "-" or "$" in words[index + 1]):
                named.append(words[index + 2])
        if "--out" in words[:-1] and ("--check" in words or "--replay" in words):
            named.append(words[words.index("--out") + 1])
        found += [os.path.normpath(os.path.join(gate.get("cwd", "."), name)) for name in named if "$" not in name]
    return found


def holds_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(holds_float(item) for item in value.values())
    if isinstance(value, list):
        return any(holds_float(item) for item in value)
    return False


def float_free(path: Path) -> bool:
    """Whether path is a JSON file holding no float, whose replay therefore needs no runner arithmetic."""
    if not path.is_file() or path.suffix != ".json":
        return False
    return not holds_float(json.loads(path.read_text(encoding="utf-8")))


def replay_problems(gates: list[dict[str, Any]], ledger: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Each compared record a gate leaves undeclared, each declared record neither bound, float-free nor
    exempt, and each bound record no gate declares. A declared directory stands for every file under it,
    and an exempt entry covers the files under it."""
    records, exempt = ledger.get("records", {}), ledger.get("exempt", {})
    found, declared = [], set()
    for gate in gates:
        replays = gate.get("replays", [])
        for name in sorted(set(compared_records(gate)) - set(replays)):
            found.append(f"{gate['name']} compares {name} without declaring it in replays")
        for name in replays:
            declared.add(name)
            if name in exempt:
                continue
            path = root / name
            files = sorted(item for item in path.rglob("*") if item.is_file()) if path.is_dir() else [path]
            for item in files:
                member = item.relative_to(root).as_posix()
                declared.add(member)
                if member in exempt or any(member.startswith(f"{entry}/") for entry in exempt):
                    continue
                if member not in records and not float_free(item):
                    found.append(
                        f"{gate['name']} replays {member}, which is not float-free JSON and is not bound; write it "
                        "with `write` and bind it with `add`"
                    )
    for name in sorted(set(records) - declared):
        found.append(f"{name} is bound but no gate declares it in replays")
    for name, reason in sorted(exempt.items()):
        covered = name in declared or any(name.startswith(f"{entry}/") for entry in declared)
        if not covered or not isinstance(reason, str) or not reason.strip():
            found.append(f"exempt {name} needs a declaring gate and a reason")
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
        # env applies the ledger's arithmetic after ci/gate_env.py assigns the gate environment, so it wins.
        pinned = ["env", *(f"{name}={value}" for name, value in sorted(LEDGER_ARITHMETIC.items()))]
        status = subprocess.run(
            ["sh", str(snapshot / "ci" / "runner_image.sh"), *pinned, *command], cwd=snapshot, check=False
        )
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
        found = problems(ledger) + replay_problems(json.loads(GATES.read_text())["gates"], ledger)
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
        bound = {**ledger, "schema": SCHEMA, "image": current, "records": dict(sorted(records.items()))}
        text = json.dumps(bound, indent=1)
        LEDGER.write_text(text + "\n")
        return 0
    raise SystemExit("usage: runner_image_records.py id | check | add PATH... | write COMMAND...")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
