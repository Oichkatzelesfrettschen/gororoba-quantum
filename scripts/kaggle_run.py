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
- ``collect RUN_DIR`` downloads the run's kernel version into RUN_DIR/output
  and writes collect.json with the sha256 of every file.
- ``verify`` checks every retained collect.json against the files under its
  output/ directory, offline.

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
# A TPU host has no NVIDIA GPU, and the cu11 wheel ships cp313 only, so a
# TPU kernel takes the CPU build of the same Aer release.
TPU_KERNEL_PINS = ("qiskit==2.5.2", "qiskit-aer==0.17.2")


def kernel_pins(machine: str) -> tuple[str, ...]:
    return TPU_KERNEL_PINS if machine.startswith("Tpu") else KERNEL_PINS


# Usage guides every bundle carries, so an agent or author inside a kernel
# reads the same package manuals, workflow and substrate notes as the host:
# every tracked file under each directory.
KERNEL_DOCS = (
    "docs/notes/kaggle",
    "docs/notes/packages",
    "docs/notes/quantum-tools",
    "docs/notes/qiskit-ecosystem.md",
    "docs/notes/qiskit-ecosystem-install-plan.md",
)
# Opt-in package groups (``push --with GROUP``), each pinned to the version of
# the build host's Arch package, so a kernel and the host import the same
# releases. The kernel installs them under a constraints file that holds
# KERNEL_PINS and the image's numpy and scipy fixed, and stops unless every
# pin is installed at its version. The algebra packages are not a group: every
# kernel builds them through scripts/algebra_package_tables.py.
PIN_GROUPS: dict[str, tuple[str, ...]] = {
    "quantum-tools": (
        "stim==1.16.0",
        "mthree==3.0.0",
        "runningman==2.3.0",
        "qiskit-ibm-runtime==0.50.0",
        # Runtime's own dependencies, held at the host's versions: unpinned,
        # a kernel resolves ibm-quantum-schemas 0.13 while the host has 0.12.
        "samplomatic==0.21.0",
        "ibm-quantum-schemas==0.12.20260921",
        "qiskit-mitigation==0.1.1",
        # qiskit.qasm3.loads needs the importer and its parser.
        "qiskit-qasm3-import==0.6.0",
        "openqasm3==1.0.1",
        "antlr4-python3-runtime==4.13.2",
        "qiskit-addon-utils==0.4.0",
        "qiskit-experiments==0.14.2",
        "lmfit==1.3.4",
        "quimb==1.15.0",
        "cotengra==0.8.2",
        "autoray==0.11.0",
        "pyzx==0.10.7",
        "galois==0.4.11",
        "numba==0.68.0",
    ),
    # Exact arithmetic beside cd_core: FLINT integers, rationals and
    # matrices (exact rank and nullspace) and p-adic fields; neither defines
    # a Cayley-Dickson table, so neither enters tables.json.
    "exact-arithmetic": ("python-flint==0.9.0", "pyadic==0.3.0"),
}
DEFAULT_MACHINE = "NvidiaTeslaT4"
# A TPU session needs Kaggle's TPU-VM image, which carries libtpu: a script
# kernel pushed with a Tpu machine shape receives the CPU image and runs on a
# 4-core CPU machine whose JAX finds no libtpu.so. Public notebooks that ran
# on TpuV5E8 record this image digest and kernel_type notebook in their
# server metadata (`kaggle kernels pull -m`), so a TPU push uses both.
TPU_DOCKER_IMAGE = "gcr.io/kaggle-images/python@sha256:dafd4ce5668bbf1ad422e4c109e0f18c9623c3a7c7f48b0235f13142755c40b9"
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

import importlib.metadata as metadata

PINS = {pins!r}
EXTRA = {extra!r}
BUNDLE = "{bundle}"

out = Path("/kaggle/working/output")
out.mkdir(parents=True, exist_ok=True)
# The image's numpy and scipy, and its JAX and libtpu where present, stay
# fixed while the pins install.
frozen = []
for name in ("numpy", "scipy", "jax", "jaxlib", "libtpu"):
    try:
        frozen.append(f"{{name}}=={{metadata.version(name)}}")
    except metadata.PackageNotFoundError:
        pass
Path("/tmp/constraints.txt").write_text("\n".join([*PINS, *frozen]) + "\n")
pip = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-c", "/tmp/constraints.txt", *PINS, *EXTRA],
    capture_output=True,
    text=True,
)
(out / "pip.txt").write_text(pip.stdout + pip.stderr)
if pip.returncode:
    raise SystemExit(f"pip install failed: {{pip.returncode}}")
for pin in [*PINS, *EXTRA, *frozen]:
    name, wanted = pin.split("==")
    if metadata.version(name) != wanted:
        raise SystemExit(f"{{name}} is {{metadata.version(name)}}, pinned {{wanted}}")
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


def tracked_files(include: str) -> list[Path]:
    """A repository file, or every tracked file under a repository directory."""
    path = (ROOT / include).resolve()
    require(path.is_relative_to(ROOT) and path.exists(), f"{include} is not a repository path")
    if not path.is_dir():
        return [path]
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", path.relative_to(ROOT).as_posix()],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / name for name in tracked.split("\0") if name]


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
    for docs in KERNEL_DOCS:
        files.extend(tracked_files(docs))
    for include in args.include:
        files.extend(tracked_files(include))
    bundled = sorted({path.relative_to(ROOT).as_posix() for path in files})
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", *bundled], cwd=ROOT, capture_output=True, text=True, check=True
    )
    # git status above ignores untracked files so that run directories stay
    # clean; a bundled input outside the index makes the revision irreproducible.
    untracked = sorted(set(bundled) - set(filter(None, listed.stdout.split("\0"))))
    if untracked and not revision.endswith("-dirty"):
        revision += "-dirty"
    buffer = io.BytesIO()
    digests: dict[str, str] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(set(files)):
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digests[rel] = sha256(data)
            bundle.writestr(rel, data)
        device = "CPU" if args.machine == "cpu" or args.machine.startswith("Tpu") else "GPU"
        datasets = [dataset_record(slug) for slug in getattr(args, "dataset", [])]
        job = {
            "entry": entry_rel,
            "args": list(args.args),
            "smoke": smoke,
            "device": device,
            "pin_groups": {group: list(PIN_GROUPS[group]) for group in getattr(args, "with_groups", [])},
            "datasets": [{"ref": d["ref"], "archive": d["archive"], "files": d["files"]} for d in datasets],
        }
        bundle.writestr("kaggle_kernel/kernel_job.json", json.dumps(job, indent=1) + "\n")
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    extra = [pin for group in getattr(args, "with_groups", []) for pin in PIN_GROUPS[group]]
    runner = RUNNER.format(
        pins=list(kernel_pins(args.machine)), extra=extra, bundle=base64.b64encode(buffer.getvalue()).decode("ascii")
    )
    (kernel_dir / "run.py").write_text(runner, encoding="utf-8")
    tpu = args.machine.startswith("Tpu")
    if tpu:
        # The same program as the notebook's single code cell.
        notebook = {
            "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": runner}],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        (kernel_dir / "run.ipynb").write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    kernel_id = f"{owner}/{args.slug}"
    metadata = {
        "id": kernel_id,
        "title": args.slug,
        "code_file": "run.ipynb" if tpu else "run.py",
        "language": "python",
        "kernel_type": "notebook" if tpu else "script",
        "is_private": True,
        "enable_gpu": args.machine != "cpu" and not args.machine.startswith("Tpu"),
        "enable_tpu": args.machine.startswith("Tpu"),
        "enable_internet": True,
    }
    if args.machine != "cpu":
        metadata["machine_shape"] = args.machine
    if tpu:
        metadata["docker_image"] = TPU_DOCKER_IMAGE
    if datasets:
        metadata["dataset_sources"] = [d["ref"] for d in datasets]
    (kernel_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
    submission = {
        "schema": "kaggle-aer-submission-v1",
        "kernel": kernel_id,
        "machine_shape": args.machine,
        "entry": entry_rel,
        "args": list(args.args),
        "smoke": smoke,
        "git_commit": revision,
        "untracked_inputs": untracked,
        "pins": list(kernel_pins(args.machine)),
        "pin_groups": {group: list(PIN_GROUPS[group]) for group in getattr(args, "with_groups", [])},
        "bundle": digests,
        "datasets": {d["ref"]: d["archive_sha256"] for d in datasets},
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
    import shutil

    try:
        reply = kaggle(*push_args).strip()
    except SystemExit:
        shutil.rmtree(run_dir)
        raise
    if "successfully pushed" not in reply:
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
        entry=entry,
        smoke=False,
        include=[data],
        args=["--pairs", "1,16"],
        slug="self-test",
        machine=DEFAULT_MACHINE,
        with_groups=["quantum-tools"],
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
        require(all(pin in runner for pin in PIN_GROUPS["quantum-tools"]), "run.py lacks a group pin")
        for docs in KERNEL_DOCS:
            for path in tracked_files(docs):
                require(path.relative_to(ROOT).as_posix() in submission["bundle"], f"bundle lacks {path}")
        require(
            submission["pin_groups"] == {"quantum-tools": list(PIN_GROUPS["quantum-tools"])},
            "submission does not record the pin group",
        )
        require(submission["untracked_inputs"] == [], f"untracked bundled inputs {submission['untracked_inputs']}")
    print(f"kaggle_run self-test: {len(submission['bundle'])} bundled files, private GPU kernel, run.py compiles")
    return 0


DATASETS = RESULTS / "datasets"
ARCHIVE = "repository-files.bundle"


def dataset_record(slug: str) -> dict[str, Any]:
    path = DATASETS / f"{slug}.json"
    require(path.is_file(), f"no retained dataset record {path.relative_to(ROOT)}; run `dataset` first")
    return dict(json.loads(path.read_text(encoding="utf-8")))


def dataset(args: argparse.Namespace) -> int:
    """Upload repository files as a private Kaggle dataset: one tar archive and its sha256 manifest.

    The archive carries a non-archive extension so Kaggle stores its bytes
    unchanged; a kernel that attaches the dataset unpacks it and verifies every
    file against the manifest before its entry runs.
    """
    import tarfile
    import tempfile

    files = sorted({path for include in args.include for path in tracked_files(include)})
    # A dataset records the revision its files came from, so every file must
    # be tracked; push instead reports untracked bundled inputs and marks the
    # revision dirty.
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", *(path.relative_to(ROOT).as_posix() for path in files)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    untracked = sorted(set(files) - {ROOT / name for name in listed.split("\0") if name})
    require(not untracked, f"untracked dataset inputs: {[path.relative_to(ROOT).as_posix() for path in untracked]}")
    require(bool(files), "the dataset names no files")
    manifest = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in files}
    owner = username()
    ref = f"{owner}/{args.slug}"
    with tempfile.TemporaryDirectory() as scratch:
        staging = Path(scratch)
        with tarfile.open(staging / ARCHIVE, "w:gz") as archive:
            for path in files:
                archive.add(path, arcname=path.relative_to(ROOT).as_posix(), recursive=False)
        metadata = {"title": args.slug, "id": ref, "licenses": [{"name": "unknown"}]}
        (staging / "dataset-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
        archive_sha256 = sha256((staging / ARCHIVE).read_bytes())
        exists = subprocess.run(["kaggle", "datasets", "status", ref], capture_output=True, text=True).returncode == 0
        if exists:
            reply = kaggle("datasets", "version", "-p", str(staging), "-m", f"files at {git_commit()}", "-r", "skip")
        else:
            reply = kaggle("datasets", "create", "-p", str(staging), "-r", "skip")
    record = {
        "schema": "kaggle-dataset-v1",
        "ref": ref,
        "archive": ARCHIVE,
        "archive_sha256": archive_sha256,
        "git_commit": git_commit(),
        "includes": list(args.include),
        "files": manifest,
        "reply": reply.strip()[-300:],
    }
    DATASETS.mkdir(parents=True, exist_ok=True)
    (DATASETS / f"{args.slug}.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"{ref}: {len(manifest)} files, archive {archive_sha256[:12]}")
    return 0


def submission_of(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "submission.json"
    require(path.is_file(), f"{run_dir} has no submission.json")
    return json.loads(path.read_text(encoding="utf-8"))


def kernel_ref(submission: dict[str, Any]) -> str:
    """owner/slug/version for a run that recorded its version, owner/slug for one that predates it."""
    version = submission.get("kernel_version")
    return f"{submission['kernel']}/{version}" if version is not None else submission["kernel"]


def status(args: argparse.Namespace) -> int:
    print(kaggle("kernels", "status", kernel_ref(submission_of(Path(args.run_dir)))).strip())
    return 0


def collect(args: argparse.Namespace) -> int:
    """Download the run's own kernel version and record the sha256 of every returned file.

    `kernels status` reports the slug's latest version whatever version it
    names, so a later push would hide this run's state. The versioned output
    carries kaggle_kernel/kernel_main.py's exit.json, written on every exit
    path, and that file alone decides completion.
    """
    import shutil

    run_dir = Path(args.run_dir).resolve()
    submission = submission_of(run_dir)
    require("kernel_version" in submission, f"{run_dir} records no kernel version to collect")
    versioned = kernel_ref(submission)
    reported = kaggle("kernels", "status", versioned).strip()
    out = run_dir / "output"
    # A refused earlier attempt leaves its partial download here; the ledger
    # describes one complete download, so every retry starts empty.
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    kaggle("kernels", "output", versioned, "-p", str(out))
    for stray in out.iterdir():
        # The kernel's results live in output/ and its log beside it; anything
        # else under /kaggle/working is scratch that Kaggle also returns.
        if stray.is_dir() and stray.name != "output":
            shutil.rmtree(stray)
    exit_file = out / "output" / "exit.json"
    # The reported status names the slug's latest version, so it cannot stand
    # in for a missing exit.json: such a version is unfinished or died before
    # kernel_main ran, and its downloaded files stay for inspection unledgered.
    require(
        exit_file.is_file(),
        f"{versioned} returned no exit.json (status of the latest version: {reported}); "
        f"{out.relative_to(ROOT)} holds what it returned and no collect.json was written",
    )
    returncode = json.loads(exit_file.read_text(encoding="utf-8"))["returncode"]
    state = "COMPLETE" if returncode == 0 else "ERROR"
    files = {p.relative_to(out).as_posix(): sha256(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}
    record = {
        "schema": "kaggle-aer-collect-v1",
        "kernel": versioned,
        "state": state,
        "collected_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ"),
        "files": files,
    }
    (run_dir / "collect.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))
    return 0


def verify(args: argparse.Namespace) -> int:
    """Every retained collect.json names exactly the files under its output/ with their sha256.

    A versioned run's ledger must include the exit.json collection required;
    an earlier, unversioned run keeps the status Kaggle reported then.
    """
    runs = sorted(RESULTS.glob("*/collect.json"))
    for path in runs:
        run_dir = path.parent
        record = json.loads(path.read_text(encoding="utf-8"))
        out = run_dir / "output"
        present = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
        require(present == set(record["files"]), f"{run_dir.name}: output files differ from collect.json")
        for rel, digest in record["files"].items():
            require(sha256((out / rel).read_bytes()) == digest, f"{run_dir.name}: {rel} differs from its sha256")
        submission = submission_of(run_dir)
        require(record["kernel"] == kernel_ref(submission), f"{run_dir.name}: kernel differs")
        # Runs pushed before push recorded kernel versions also predate
        # exit.json and keep the status Kaggle reported; every versioned run
        # was collected on its exit.json.
        require(
            "kernel_version" not in submission or "output/exit.json" in record["files"],
            f"{run_dir.name}: a versioned run's ledger lacks output/exit.json",
        )
    require(bool(runs), f"no collect.json under {RESULTS.relative_to(ROOT)}")
    print(f"kaggle runs: {len(runs)} collected outputs match their sha256 ledgers")
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
    push_parser.add_argument("--dataset", action="append", default=[], help="retained dataset slug to attach")
    push_parser.add_argument(
        "--with",
        dest="with_groups",
        action="append",
        default=[],
        choices=sorted(PIN_GROUPS),
        help="opt-in package group the kernel installs at the host's versions",
    )
    push_parser.set_defaults(func=push)
    sub.add_parser("self-test").set_defaults(func=self_test)
    dataset_parser = sub.add_parser("dataset")
    dataset_parser.add_argument("--slug", required=True)
    dataset_parser.add_argument("--include", action="append", required=True, help="repository file or directory")
    dataset_parser.set_defaults(func=dataset)
    sub.add_parser("verify").set_defaults(func=verify)
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
