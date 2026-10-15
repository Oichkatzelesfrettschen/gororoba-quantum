"""Run a repository simulation as a private Kaggle GPU kernel and retain its output.

Simulations of 14 qubits or fewer run on Kaggle's Aer GPU kernels; IBM
hardware serves 15 or more qubits or a question about the device itself.
This script is the only path from the repository to Kaggle:

- ``push ENTRY --slug SLUG [-- ARGS]`` (ARGS after ``--`` go to ENTRY) resolves ENTRY's repository imports
  (``import X`` and ``from X import`` naming a module under gororoba_quantum/
  or scripts/, transitively), bundles them with any ``--include`` data files
  as a zip embedded in a generated ``run.py``, writes kernel-metadata.json
  (private, GPU, internet for the pinned pip install) and pushes the kernel.
  The kernel installs the pins in KERNEL_PINS, records the environment, runs
  ENTRY from the unpacked repository root with ``GOROROBA_AER_DEVICE=GPU``,
  and copies every file the run created or changed under the repository
  root into ``/kaggle/working/output``.
- ``status RUN_DIR`` reports the kernel state.
- ``collect RUN_DIR`` downloads the kernel output into RUN_DIR/output and
  writes collect.json with the sha256 of every file.

``self-test`` builds the Design C kernel in a temporary directory without
network access and checks its bundle digests, metadata and generated code.

``--smoke`` replaces ENTRY with an environment probe: the Aer devices, the
GPU name and the wall time of a 14-qubit density-matrix circuit on the GPU.

Each run directory, results/kaggle/<UTC stamp>-<slug>/, holds submission.json
(entry, arguments, git commit, bundle file digests, pins, machine shape) and
the generated kernel. A Kaggle output is a numerical simulation: it enters
docs/state/research_state.json only through a CPU replay gate on a reduced
case. Credentials stay in the Kaggle CLI's own store (``kaggle auth login``).
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results/kaggle"
MODULE_DIRS = ("gororoba_quantum", "scripts")
KERNEL_PINS = ("qiskit==2.5.2", "qiskit-aer-gpu-cu11==0.17.2")
DEFAULT_MACHINE = "NvidiaTeslaT4"
SMOKE_QUBITS = 14

RUNNER = r"""
import base64, hashlib, io, json, os, platform, subprocess, sys, time, zipfile
from pathlib import Path

PINS = {pins!r}
ENTRY = {entry!r}
ARGS = {args!r}
SMOKE = {smoke!r}
SMOKE_QUBITS = {smoke_qubits!r}
BUNDLE = "{bundle}"

out = Path("/kaggle/working/output")
out.mkdir(parents=True, exist_ok=True)
pip = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *PINS], capture_output=True, text=True)
(out / "pip.txt").write_text(pip.stdout + pip.stderr)
if pip.returncode:
    raise SystemExit(f"pip install failed: {{pip.returncode}}")
repo = Path("/kaggle/working/repo")
zipfile.ZipFile(io.BytesIO(base64.b64decode(BUNDLE))).extractall(repo)
before = {{p: hashlib.sha256(p.read_bytes()).hexdigest() for p in repo.rglob("*") if p.is_file()}}

from importlib.metadata import version
import qiskit_aer
env = {{
    "python": platform.python_version(),
    "packages": {{name: version(name) for name in ("qiskit", "qiskit-aer-gpu-cu11", "numpy", "scipy")}},
    "aer_devices": list(qiskit_aer.AerSimulator().available_devices()),
    "gpu": subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout.strip().splitlines(),
}}
(out / "environment.json").write_text(json.dumps(env, indent=1) + "\n")
print(json.dumps(env), flush=True)

if SMOKE:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(SMOKE_QUBITS)
    qc.h(0)
    for q in range(SMOKE_QUBITS - 1):
        qc.cx(q, q + 1)
    qc.measure_all()
    sim = AerSimulator(method="density_matrix", device="GPU")
    start = time.time()
    counts = sim.run(transpile(qc, sim), shots=1024, seed_simulator=7).result().get_counts()
    smoke = {{"qubits": SMOKE_QUBITS, "method": "density_matrix", "device": "GPU",
              "wall_seconds": round(time.time() - start, 3), "counts": counts}}
    (out / "smoke.json").write_text(json.dumps(smoke, indent=1, sort_keys=True) + "\n")
    print(json.dumps(smoke), flush=True)
    raise SystemExit(0)

run_env = dict(os.environ, GOROROBA_AER_DEVICE="GPU", PYTHON=sys.executable)
proc = subprocess.run([sys.executable, "-B", ENTRY, *ARGS], cwd=repo, env=run_env, capture_output=True, text=True)
(out / "stdout.txt").write_text(proc.stdout)
(out / "stderr.txt").write_text(proc.stderr)
print(proc.stdout[-4000:], proc.stderr[-4000:], sep="\n", flush=True)
for path in repo.rglob("*"):
    if path.is_file() and before.get(path) != hashlib.sha256(path.read_bytes()).hexdigest():
        target = out / "repo" / path.relative_to(repo)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
(out / "exit.json").write_text(json.dumps({{"returncode": proc.returncode}}) + "\n")
raise SystemExit(proc.returncode)
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def kaggle(*args: str) -> str:
    proc = subprocess.run(["kaggle", *args], capture_output=True, text=True)
    require(proc.returncode == 0, f"kaggle {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout


def username() -> str:
    for line in kaggle("config", "view").splitlines():
        key, _, value = line.strip().lstrip("- ").partition(":")
        if key.strip() == "username" and value.strip() not in ("", "None"):
            return value.strip()
    raise SystemExit("no Kaggle account: run `kaggle auth login`")


def module_path(name: str) -> Path | None:
    top = name.split(".")[0]
    for directory in MODULE_DIRS:
        candidate = ROOT / directory / f"{top}.py"
        if candidate.is_file():
            return candidate
    return None


def import_closure(entry: Path) -> list[Path]:
    seen: set[Path] = set()
    stack = [entry]
    while stack:
        path = stack.pop()
        if path in seen:
            continue
        seen.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            for name in names:
                found = module_path(name)
                if found is not None and found not in seen:
                    stack.append(found)
    return sorted(seen)


def git_commit() -> str:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True)
    return head.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")


def build_kernel(args: argparse.Namespace, run_dir: Path, owner: str, stamp: str) -> dict[str, Any]:
    """Write run_dir/kernel (run.py and kernel-metadata.json) and run_dir/submission.json."""
    smoke = args.entry is None
    require(smoke == args.smoke, "give ENTRY or --smoke, not both")
    files: list[Path] = []
    entry_rel = None
    if not smoke:
        entry = (ROOT / args.entry).resolve()
        require(entry.is_file() and entry.is_relative_to(ROOT), f"{args.entry} is not a repository file")
        entry_rel = entry.relative_to(ROOT).as_posix()
        files = import_closure(entry)
    for include in args.include:
        path = (ROOT / include).resolve()
        require(path.is_file() and path.is_relative_to(ROOT), f"{include} is not a repository file")
        files.append(path)
    buffer = io.BytesIO()
    digests: dict[str, str] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(set(files)):
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digests[rel] = sha256(data)
            bundle.writestr(rel, data)
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    runner = RUNNER.format(
        pins=list(KERNEL_PINS),
        entry=entry_rel,
        args=list(args.args),
        smoke=smoke,
        smoke_qubits=SMOKE_QUBITS,
        bundle=base64.b64encode(buffer.getvalue()).decode("ascii"),
    )
    (kernel_dir / "run.py").write_text(runner, encoding="utf-8")
    kernel_id = f"{owner}/{args.slug}"
    metadata = {
        "id": kernel_id,
        "title": args.slug,
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "machine_shape": args.machine,
    }
    (kernel_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
    submission = {
        "schema": "kaggle-aer-submission-v1",
        "kernel": kernel_id,
        "machine_shape": args.machine,
        "entry": entry_rel,
        "args": list(args.args),
        "smoke": smoke,
        "git_commit": git_commit(),
        "pins": list(KERNEL_PINS),
        "bundle": digests,
        "run_py_sha256": sha256((kernel_dir / "run.py").read_bytes()),
        "pushed_utc": stamp,
    }
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    return submission


def push(args: argparse.Namespace) -> int:
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = RESULTS / f"{stamp}-{args.slug}"
    build_kernel(args, run_dir, username(), stamp)
    kernel_dir = run_dir / "kernel"
    push_args = ["kernels", "push", "-p", str(kernel_dir)]
    if args.timeout:
        push_args += ["-t", str(args.timeout)]
    print(kaggle(*push_args).strip())
    print(run_dir.relative_to(ROOT))
    return 0


def self_test(args: argparse.Namespace) -> int:
    """Build the Design C kernel offline and check its bundle, metadata and generated code."""
    import py_compile
    import tempfile

    entry = "scripts/design_c_cubic_noise.py"
    data = "docs/evidence/calibration/ibm_kingston.json"
    build_args = argparse.Namespace(
        entry=entry, smoke=False, include=[data], args=["--pairs", "1,16"], slug="self-test", machine=DEFAULT_MACHINE
    )
    with tempfile.TemporaryDirectory() as scratch:
        run_dir = Path(scratch) / "run"
        submission = build_kernel(build_args, run_dir, "owner", "2000-01-01T000000Z")
        for needed in (entry, data, "gororoba_quantum/calibration_snapshot.py", "gororoba_quantum/cd_core.py"):
            require(needed in submission["bundle"], f"bundle lacks {needed}")
        for rel, digest in submission["bundle"].items():
            require(digest == sha256((ROOT / rel).read_bytes()), f"bundle digest of {rel} differs from the tree")
        metadata = json.loads((run_dir / "kernel/kernel-metadata.json").read_text(encoding="utf-8"))
        require(metadata["is_private"] is True and metadata["enable_gpu"] is True, "kernel is not a private GPU kernel")
        require(metadata["id"] == "owner/self-test", f"kernel id {metadata['id']}")
        py_compile.compile(str(run_dir / "kernel/run.py"), doraise=True)
        runner = (run_dir / "kernel/run.py").read_text(encoding="utf-8")
        require(all(pin in runner for pin in KERNEL_PINS), "run.py lacks a pin")
    print(f"kaggle_run self-test: {len(submission['bundle'])} bundled files, private GPU kernel, run.py compiles")
    return 0


def submission_of(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "submission.json"
    require(path.is_file(), f"{run_dir} has no submission.json")
    return json.loads(path.read_text(encoding="utf-8"))


def status(args: argparse.Namespace) -> int:
    print(kaggle("kernels", "status", submission_of(Path(args.run_dir))["kernel"]).strip())
    return 0


def collect(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    kernel = submission_of(run_dir)["kernel"]
    state = kaggle("kernels", "status", kernel)
    require("COMPLETE" in state or "ERROR" in state, f"{kernel} has not finished: {state.strip()}")
    out = run_dir / "output"
    out.mkdir(exist_ok=True)
    kaggle("kernels", "output", kernel, "-p", str(out))
    files = {p.relative_to(out).as_posix(): sha256(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}
    record = {
        "schema": "kaggle-aer-collect-v1",
        "kernel": kernel,
        "state": state.strip().rsplit(" ", 1)[-1].strip('"'),
        "collected_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ"),
        "files": files,
    }
    (run_dir / "collect.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    push_parser = sub.add_parser("push")
    push_parser.add_argument("entry", nargs="?", help="repository-relative script the kernel runs")
    push_parser.add_argument("--slug", required=True, help="Kaggle kernel slug (lowercase, dashes)")
    push_parser.add_argument("--smoke", action="store_true", help="run the environment probe instead of ENTRY")
    push_parser.add_argument("--include", action="append", default=[], help="extra repository file to bundle")
    push_parser.add_argument("--machine", default=DEFAULT_MACHINE, help="Kaggle machine_shape")
    push_parser.add_argument("--timeout", type=int, default=0, help="kernel run-time limit in seconds")
    push_parser.set_defaults(func=push)
    sub.add_parser("self-test").set_defaults(func=self_test)
    for name, func in (("status", status), ("collect", collect)):
        sub_parser = sub.add_parser(name)
        sub_parser.add_argument("run_dir")
        sub_parser.set_defaults(func=func)
    argv = sys.argv[1:]
    entry_args: list[str] = []
    if "--" in argv:
        split = argv.index("--")
        argv, entry_args = argv[:split], argv[split + 1 :]
    args = parser.parse_args(argv)
    args.args = entry_args
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
