"""Run a repository simulation as a private Kaggle GPU kernel and retain its output.

Simulations of 14 qubits or fewer run on Kaggle's Aer GPU kernels; IBM
hardware serves 15 or more qubits or a question about the device itself.
This script is the only path from the repository to Kaggle:

- ``push ENTRY --slug SLUG [-- ARGS]`` (ARGS after ``--`` go to ENTRY) resolves ENTRY's repository imports
  (``import X`` and ``from X import`` naming a module under gororoba_quantum/
  or scripts/, transitively), bundles them with any ``--include`` file, or
  every tracked file of an ``--include`` directory, as a zip embedded in a
  generated ``run.py``, writes kernel-metadata.json
  (private, GPU, internet for the pinned pip install) and pushes the kernel.
  Every bundle also carries KERNEL_FILES. The kernel installs KERNEL_PINS,
  unpacks the bundle and runs kaggle_kernel/kernel_main.py, which records
  the measured substrate, builds the hypercomplex package stack and proves it
  against the retained tables, then runs ENTRY with
  ``GOROROBA_AER_DEVICE=GPU`` and returns every file the entry created or
  changed under the repository root.
- ``status RUN_DIR`` reports the kernel state.
- ``collect RUN_DIR`` downloads the kernel output into RUN_DIR/output and
  writes collect.json with the sha256 of every file.

``self-test`` builds the Design C kernel in a temporary directory without
network access and checks its bundle digests, metadata and generated code.

``--smoke`` replaces ENTRY with a capacity probe: the widest density-matrix
and statevector GHZ circuits the GPU runs.

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
import re
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
# Files every kernel carries: its program and instructions, and the
# hypercomplex stack check with the tables it must reproduce.
KERNEL_FILES = (
    "kaggle_kernel/kernel_main.py",
    "kaggle_kernel/AGENTS.md",
    "scripts/algebra_package_tables.py",
    "docs/evidence/algebra_packages/tables.json",
)

RUNNER = r"""
import base64, io, subprocess, sys, zipfile
from pathlib import Path

PINS = {pins!r}
BUNDLE = "{bundle}"

out = Path("/kaggle/working/output")
out.mkdir(parents=True, exist_ok=True)
pip = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *PINS], capture_output=True, text=True)
(out / "pip.txt").write_text(pip.stdout + pip.stderr)
if pip.returncode:
    raise SystemExit(f"pip install failed: {{pip.returncode}}")
repo = Path("/tmp/gororoba/repo")
zipfile.ZipFile(io.BytesIO(base64.b64decode(BUNDLE))).extractall(repo)
raise SystemExit(subprocess.run([sys.executable, "-B", "kaggle_kernel/kernel_main.py"], cwd=repo).returncode)
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
    """HEAD, marked dirty when a tracked file differs; run directories are untracked until committed."""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return head.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")


def build_kernel(args: argparse.Namespace, run_dir: Path, owner: str, stamp: str, revision: str) -> dict[str, Any]:
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
    for always in KERNEL_FILES:
        files.extend(import_closure(ROOT / always) if always.endswith(".py") else [ROOT / always])
    for include in args.include:
        path = (ROOT / include).resolve()
        require(path.is_relative_to(ROOT) and path.exists(), f"{include} is not a repository path")
        if path.is_dir():
            tracked = subprocess.run(
                ["git", "ls-files", "-z", "--", path.relative_to(ROOT).as_posix()],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            files.extend(ROOT / name for name in tracked.split("\0") if name)
        else:
            files.append(path)
    buffer = io.BytesIO()
    digests: dict[str, str] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(set(files)):
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digests[rel] = sha256(data)
            bundle.writestr(rel, data)
        device = "CPU" if args.machine == "cpu" else "GPU"
        job = {"entry": entry_rel, "args": list(args.args), "smoke": smoke, "device": device}
        bundle.writestr("kaggle_kernel/kernel_job.json", json.dumps(job, indent=1) + "\n")
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    runner = RUNNER.format(pins=list(KERNEL_PINS), bundle=base64.b64encode(buffer.getvalue()).decode("ascii"))
    (kernel_dir / "run.py").write_text(runner, encoding="utf-8")
    kernel_id = f"{owner}/{args.slug}"
    metadata = {
        "id": kernel_id,
        "title": args.slug,
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": args.machine != "cpu" and not args.machine.startswith("Tpu"),
        "enable_tpu": args.machine.startswith("Tpu"),
        "enable_internet": True,
    }
    if args.machine != "cpu":
        metadata["machine_shape"] = args.machine
    (kernel_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
    submission = {
        "schema": "kaggle-aer-submission-v1",
        "kernel": kernel_id,
        "machine_shape": args.machine,
        "entry": entry_rel,
        "args": list(args.args),
        "smoke": smoke,
        "git_commit": revision,
        "pins": list(KERNEL_PINS),
        "bundle": digests,
        "run_py_sha256": sha256((kernel_dir / "run.py").read_bytes()),
        "pushed_utc": stamp,
    }
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    return submission


def push(args: argparse.Namespace) -> int:
    revision = git_commit()
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = RESULTS / f"{stamp}-{args.slug}"
    build_kernel(args, run_dir, username(), stamp, revision)
    kernel_dir = run_dir / "kernel"
    push_args = ["kernels", "push", "-p", str(kernel_dir)]
    if args.machine != "cpu":
        # kernel-metadata.json's machine_shape alone runs the kernel on a CPU
        # machine; the push's --accelerator selects the hardware.
        push_args += ["--accelerator", args.machine]
    if args.timeout:
        push_args += ["-t", str(args.timeout)]
    reply = kaggle(*push_args).strip()
    if "successfully pushed" not in reply:
        import shutil

        shutil.rmtree(run_dir)
        raise SystemExit(f"kaggle refused the push: {reply}")
    version = re.search(r"Kernel version (\d+) successfully pushed", reply)
    require(version is not None, f"push reply names no kernel version: {reply}")
    assert version is not None
    submission = submission_of(run_dir)
    submission["kernel_version"] = int(version.group(1))
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    print(reply)
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
        submission = build_kernel(build_args, run_dir, "owner", "2000-01-01T000000Z", "0" * 40)
        expected = (entry, data, "gororoba_quantum/calibration_snapshot.py", "gororoba_quantum/cd_core.py")
        for needed in (*expected, *KERNEL_FILES):
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
    submission = submission_of(run_dir)
    kernel = submission["kernel"]
    # An unversioned `kernels output` returns the latest version, which a later
    # push to the same slug replaces; the run's own version is the one it owns.
    require("kernel_version" in submission, f"{run_dir} records no kernel version to collect")
    versioned = f"{kernel}/{submission['kernel_version']}"
    state = kaggle("kernels", "status", kernel)
    require("COMPLETE" in state or "ERROR" in state, f"{kernel} has not finished: {state.strip()}")
    out = run_dir / "output"
    out.mkdir(exist_ok=True)
    kaggle("kernels", "output", versioned, "-p", str(out))
    for stray in out.iterdir():
        # The kernel's results live in output/ and its log beside it; anything
        # else under /kaggle/working is scratch that Kaggle also returns.
        if stray.is_dir() and stray.name != "output":
            import shutil

            shutil.rmtree(stray)
    files = {p.relative_to(out).as_posix(): sha256(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}
    record = {
        "schema": "kaggle-aer-collect-v1",
        "kernel": versioned,
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
    push_parser.add_argument("--include", action="append", default=[], help="repository file or directory to bundle")
    push_parser.add_argument("--machine", default=DEFAULT_MACHINE, help="machine_shape, or cpu")
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
