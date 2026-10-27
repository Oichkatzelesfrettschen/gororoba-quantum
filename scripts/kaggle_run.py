"""Run a repository simulation as a private Kaggle kernel and retain its output.

Simulations of 14 qubits or fewer run on Kaggle; IBM hardware serves 15 or
more qubits or a question about the device itself. A kernel runs on a CPU
machine unless ``--machine`` names an accelerator, which a case requests when
its widest density matrix reaches 12 qubits, or 8 with mid-circuit
measurement: below those widths a T4 is at most 3 times faster than the
kernel's 4 CPUs (docs/notes/kaggle/substrates.md), and the weekly GPU quota
goes to the runs that need it. This script is
the only path from the repository to Kaggle:

- ``push ENTRY --slug SLUG [-- ARGS]`` (ARGS after ``--`` go to ENTRY) resolves ENTRY's repository imports
  (``import X`` and ``from X import`` naming a module under gororoba_quantum/
  or scripts/, transitively, less lazy imports of KERNEL_EXCLUDED_MODULES), bundles them with any ``--include`` file, or
  every tracked file of an ``--include`` directory, as a zip embedded in a
  generated ``run.py``, writes kernel-metadata.json
  (private, internet for the pinned pip install) and pushes the kernel.
  Every bundle also carries KERNEL_FILES. The kernel installs KERNEL_PINS,
  unpacks the bundle and runs kaggle_kernel/kernel_main.py, which records
  the measured substrate, builds the hypercomplex package stack and proves it
  against the retained tables, then runs ENTRY with GOROROBA_AER_DEVICE set
  to the machine's device and returns every file the entry created or
  changed under the repository root.
- ``status RUN_DIR`` reports the kernel state.
- ``collect RUN_DIR`` downloads the run's kernel version into a new capture
  and writes its receipt with the sha256 of every file. The first capture
  carrying exit.json becomes RUN_DIR/output with RUN_DIR/collect.json; every
  other attempt, partial or repeated, stays under RUN_DIR/captures/<id>/.
- ``verify`` checks every retained receipt against the files under its
  output/ directory and the receipt chain of each run, offline.
- ``dataset --slug SLUG --include PATH`` uploads tracked repository files as
  one archive a kernel unpacks; ``artifact --slug SLUG --file PATH --sha256
  HEX`` uploads one verified file (a built wheel) that a kernel reads in
  place. ``push --dataset SLUG`` attaches either kind.
- ``push --gpu-env --gpu-aer cu13`` builds the GPU venv on the CUDA 13 Aer
  wheel (AER_GPU_WHEELS) instead of PyPI's qiskit-aer-gpu-cu11.

``self-test`` builds the Design C kernel in a temporary directory without
network access and checks its bundle digests, metadata and generated code.

``--smoke`` replaces ENTRY with a capacity probe: the widest density-matrix
and statevector GHZ circuits the GPU runs.

Each run directory, results/kaggle/<UTC stamp>-<slug>/, holds submission.json
(entry, arguments, git commit, bundle file digests, pins, machine shape, the
Aer device the entry sees, and the backend, calibration, backend version and
processor type of every bundled calibration snapshot) and the generated
kernel. A Kaggle output is a numerical simulation: it enters
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
import lzma
import os
import re
import subprocess
import sys
import time
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results/kaggle"
MODULE_DIRS = ("gororoba_quantum", "scripts")
# The cu11 wheel's controller_wrappers links libcustatevec.so.1 and
# libcutensornet.so.2 through an RPATH into site-packages/cuquantum/lib, which
# its Requires-Dist cuquantum-cu11 (>=23.3.0,<24.11.0) installs; 24.8.0 is the
# newest release in that range and brings custatevec-cu11 1.6.0.post1 and
# cutensornet-cu11 2.5.0, whose cutensor-cu11>=2.0.1,<3 resolves to 2.2.0.
# Pinning both holds every library Aer's cuStateVec_enable path loads at one
# version.
KERNEL_PINS = (
    "qiskit==2.6.0",
    "qiskit-aer-gpu-cu11==0.17.2",
    "cuquantum-cu11==24.8.0",
    "cutensor-cu11==2.2.0",
    "qiskit-ibm-runtime==0.50.0",
)
# --gpu-env installs these in requirements.txt's qiskit-aer place inside a
# venv on the image's Python 3.13, the newest Python the cu11 wheel ships for.
GPU_ENV_AER_PINS = tuple(pin for pin in KERNEL_PINS if not pin.startswith(("qiskit==", "qiskit-ibm-runtime==")))
# The CUDA 13 libraries the qiskit-aer-gpu-cu13 wheel loads from site-packages;
# _gpu_aer_self_test holds this tuple equal to the recipe's pin file.
CU13_RUNTIME_PINS_FILE = "docs/notes/kaggle/recipes/aer-gpu-cu13-runtime-pins.txt"
CU13_RUNTIME_PINS = (
    "nvidia-cuda-runtime==13.0.96",
    "nvidia-cublas==13.1.1.3",
    "nvidia-cuda-nvrtc==13.0.88",
    "nvidia-cusolver==12.0.4.66",
    "nvidia-cusparse==12.6.3.3",
    "nvidia-nvjitlink==13.0.88",
    "custatevec-cu13==1.15.0",
    "cutensornet-cu13==2.14.0",
    "cutensor-cu13==2.8.1",
)
# ``push --gpu-env --gpu-aer BUILD`` selects the GPU Aer pins of the venv.
# cu11 is PyPI's qiskit-aer-gpu-cu11; cu13 is the wheel
# docs/notes/kaggle/recipes/build_aer_gpu_cu13_wheel.sh builds (CUDA 13.0,
# sm_75 and sm_89 SASS, cuStateVec), which no index serves.
GPU_AER_PINS: dict[str, tuple[str, ...]] = {
    "cu11": GPU_ENV_AER_PINS,
    "cu13": ("qiskit-aer-gpu-cu13==0.17.2", *CU13_RUNTIME_PINS),
}
# A build no index serves: the private dataset slug that holds its wheel as an
# artifact (``kaggle_run.py artifact``), the wheel's file name and its sha256.
# A cu13 push attaches the dataset itself, and the kernel installs only a
# wheel whose bytes match the digest.
AER_GPU_WHEELS: dict[str, tuple[str, str, str]] = {
    "cu13": (
        "gororoba-aer-gpu-cu13-wheel",
        "qiskit_aer_gpu_cu13-0.17.2-cp313-cp313-manylinux_2_39_x86_64.whl",
        "3d40fc33cd6674644807c15364b3e3ac1d417885e08ad255797ae93e886253d5",
    ),
}
# Opt-in pins a --gpu-env venv adds (``push --gpu-env-with GROUP``), each at
# the build host's Arch package version, installed in the same ci/install_pins.sh
# resolve and required at version by kernel_main.gpu_env_failures. torch 2.14.1
# is python-pytorch-opt-cuda's release; PyPI's cp313 wheel links CUDA 13, which
# the T4 image's CUDA 13.0 driver loads, and an entry that needs the GPU proves
# it with torch.cuda before any work.
GPU_ENV_GROUPS: dict[str, tuple[str, ...]] = {"torch": ("torch==2.14.1",)}
# GPUs each accelerator machine carries; kernel_main.gpu_env_failures requires
# nvidia-smi to list them all.
MACHINE_GPUS = {"NvidiaTeslaT4": 2}
# A CPU or TPU host has no NVIDIA GPU, and the cu11 wheel ships cp313 only,
# so those kernels take the CPU build of the same Aer release.
CPU_KERNEL_PINS = ("qiskit==2.6.0", "qiskit-aer==0.17.2", "qiskit-ibm-runtime==0.50.0")
# Usage guides every bundle carries, so an agent or author inside a kernel
# reads the same package manuals, workflow and substrate notes as the host:
# every tracked file under each directory except the captured upstream
# references, which are hash-pinned copies of pages the kernel never reads
# and which alone exceed half of KERNEL_SOURCE_LIMIT.
KERNEL_DOCS = (
    "docs/notes/kaggle",
    "docs/notes/packages",
    "docs/notes/quantum-tools",
    "docs/notes/qiskit-ecosystem.md",
    "docs/notes/qiskit-ecosystem-install-plan.md",
)
KERNEL_DOC_CAPTURES = ("docs/notes/kaggle/site", "docs/notes/kaggle/cli")
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
        # Runtime dependencies match the active CI qualification environment.
        "samplomatic==0.21.0",
        "ibm-quantum-schemas==0.13.20261016",
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
    # The QX simulator's Python binding at the Quantum Inspire environment's
    # version (docs/notes/quantum_inspire/requirements-qi.txt), the emulator
    # the remote QX backend runs; its wheels are cp313 only, so an entry that
    # needs it runs on the image's Python, never under --ci-env.
    "qx-emulator": ("qxelarator==0.10.0",),
}
MAX_ACCELERATOR_SECONDS = 4 * 3600
SMOKE_TIMEOUT_SECONDS = 1800
# A TPU VM session carries no docker image on Kaggle's backend, and a
# docker_image in kernel-metadata.json or a dockerImageVersionId in the
# notebook pins a CPU/GPU image that overrides it (kaggle-api issue 1197).
# A TPU push therefore names no image, asks for the latest pinning, and
# writes a notebook without a "kaggle" metadata block. The session's
# hardware is read from its own output (scripts/tpu_probe.py); the request
# fields establish nothing about it (docs/notes/kaggle/tpu-research.md).
DEFAULT_MACHINE = "cpu"
GPU_MACHINE = "NvidiaTeslaT4"
TPU_MACHINE = "TpuV5E8"
# CI's interpreter (.github/workflows/ci.yml) and the uv that installs it on the
# kernel.
CI_PYTHON = "3.14.7"
UV_PIN = "uv==0.13.0"
# calibration_snapshot.SCHEMA without its version suffix, so every snapshot schema version is recognized.
CALIBRATION_SCHEMA_PREFIX = "gororoba-calibration-snapshot-"
# What ci/install_pins.sh reads; --ci-env bundles them with the entry.
CI_ENV_FILES = (
    "requirements.txt",
    "ci/requirements-ci.txt",
    "ci/install_pins.sh",
    "ci/patches/sympy-1.14.0-mpmath-1.4.patch",
)
# Kaggle's SaveKernel accepts a 706,414-byte run.py and refuses a 1,662,849-byte
# one with HTTP 400 (2026-10-16); the guard sits between the two.
KERNEL_SOURCE_LIMIT = 1_000_000
# Provider cloud clients that authenticate with a token file outside every
# checkout. A kernel holds no provider token, so a function that imports one
# lazily has no reachable call there, and the closure leaves such an import
# out; a module-level import still bundles the client, because importing the
# module that carries it executes the import.
KERNEL_EXCLUDED_MODULES = frozenset({"qd_platform"})
# Files every kernel carries: its program and instructions, and the
# hypercomplex stack check with the tables it must reproduce.
KERNEL_FILES = (
    "kaggle_kernel/kernel_main.py",
    "kaggle_kernel/gpu_env_report.py",
    "kaggle_kernel/AGENTS.md",
    "scripts/algebra_package_tables.py",
    "docs/evidence/algebra_packages/tables.json",
)

RUNNER = r"""
import base64, io, lzma, os, subprocess, sys, zipfile
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
zipfile.ZipFile(io.BytesIO(lzma.decompress(base64.b64decode(BUNDLE)))).extractall(repo)
# The bootstrap imports standard-library modules only. Configure the new
# interpreter's loader before kernel_main reads Aer's environment or capacity.
sys.path.insert(0, str(repo / "kaggle_kernel"))
from kernel_main import native_environment
raise SystemExit(subprocess.run(
    [sys.executable, "-B", "kaggle_kernel/kernel_main.py"], cwd=repo,
    env=native_environment(os.environ),
).returncode)
"""


def kernel_pins(machine: str) -> tuple[str, ...]:
    """The CPU Aer build on CPU and TPU machines, the cu11 GPU build on an NVIDIA machine."""
    return CPU_KERNEL_PINS if machine == "cpu" or machine.startswith("Tpu") else KERNEL_PINS


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


def eager_imports(tree: ast.Module) -> set[int]:
    """The ids of the import statements that run when the module is imported: every one outside a function body."""
    eager: set[int] = set()
    stack: list[ast.AST] = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            continue
        if isinstance(node, ast.Import | ast.ImportFrom):
            eager.add(id(node))
        stack.extend(ast.iter_child_nodes(node))
    return eager


def import_closure(entry: Path) -> list[Path]:
    seen: set[Path] = set()
    stack = [entry]
    while stack:
        path = stack.pop()
        if path in seen:
            continue
        seen.add(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        eager = eager_imports(tree)
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            if id(node) not in eager:
                names = [name for name in names if name.split(".")[0] not in KERNEL_EXCLUDED_MODULES]
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


def kernel_docs() -> list[Path]:
    """Every tracked file of KERNEL_DOCS outside KERNEL_DOC_CAPTURES."""
    captures = tuple((ROOT / name).resolve() for name in KERNEL_DOC_CAPTURES)
    return [
        path
        for docs in KERNEL_DOCS
        for path in tracked_files(docs)
        if not any(path.is_relative_to(capture) for capture in captures)
    ]


def calibration_identity(content: bytes) -> dict[str, Any] | None:
    """Backend identity of one calibration snapshot's bytes (calibration_snapshot.describe), or None for other files.

    backend_version and processor_type appear when the snapshot holds them, and
    every identity names the backend and calibration.
    """
    try:
        data = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not (isinstance(data, dict) and str(data.get("schema", "")).startswith(CALIBRATION_SCHEMA_PREFIX)):
        return None
    fields = ("backend", "calibration", "backend_version", "processor_type")
    return {key: data[key] for key in fields if key in data}


def bundled_calibrations(bundled: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    """calibration_identity of every bundled JSON file that is a calibration snapshot, by bundle path."""
    identities: dict[str, dict[str, Any]] = {}
    for rel, content in sorted(bundled.items()):
        identity = calibration_identity(content) if rel.endswith(".json") else None
        if identity is not None:
            identities[rel] = identity
    return identities


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
    files.extend(kernel_docs())
    for include in args.include:
        files.extend(tracked_files(include))
    ci_env = None
    if getattr(args, "ci_env", False):
        # CI's pins carry CPU Aer, so a GPU machine's host CPUs run the entry
        # exactly as a CPU machine does; a TPU VM has no x86 Python build.
        require(not args.machine.startswith("Tpu") and not smoke, "--ci-env runs an ENTRY on a CPU or GPU machine")
        files.extend(ROOT / name for name in CI_ENV_FILES)
        ci_env = {"python": CI_PYTHON, "uv": UV_PIN}
    dataset_slugs = list(getattr(args, "dataset", []))
    gpu_env = None
    if getattr(args, "gpu_env", False):
        # A CPU machine lists no GPU, so its kernel stops at the preflight with
        # exit 4: the run that proves the fallback error on Kaggle itself. The
        # bootstrap installs --with groups into the image interpreter, which
        # the venv's entry never imports.
        require(
            not args.machine.startswith("Tpu") and not smoke and ci_env is None,
            "--gpu-env runs an ENTRY on a GPU or CPU machine without --ci-env",
        )
        require(not args.with_groups, "--gpu-env installs the repository's pins only; drop --with")
        files.extend(ROOT / name for name in CI_ENV_FILES)
        build = getattr(args, "gpu_aer", None) or "cu11"
        gpu_env = {"uv": UV_PIN, "aer_pins": list(GPU_AER_PINS[build]), "gpus": MACHINE_GPUS.get(args.machine, 1)}
        if build in AER_GPU_WHEELS:
            # The wheel's dataset is attached whether or not --dataset names
            # it, and only a retained artifact record of exactly this file
            # and digest admits the push.
            slug, wheel, digest = AER_GPU_WHEELS[build]
            record = dataset_record(slug)
            require(
                record.get("schema") == ARTIFACT_SCHEMA and record["file"] == wheel and record["sha256"] == digest,
                f"--gpu-aer {build}: dataset record {slug}.json holds {record.get('file')} "
                f"{str(record.get('sha256'))[:12]}, not {wheel} {digest[:12]}; run `artifact` with that wheel",
            )
            if slug not in dataset_slugs:
                dataset_slugs.append(slug)
            gpu_env["find_links"] = {"dataset": record["ref"], "wheel": wheel}
            gpu_env["wheel_sha256"] = digest
            # The recipe's DT_RPATH names the pinned CUDA pip wheels, so the
            # preflight requires every non-driver CUDA library from the venv.
            gpu_env["cuda_in_venv"] = True
        extra = [pin for group in getattr(args, "gpu_env_with", []) for pin in GPU_ENV_GROUPS[group]]
        if extra:
            gpu_env["extra_pins"] = extra
    require(gpu_env is not None or not getattr(args, "gpu_env_with", []), "--gpu-env-with needs --gpu-env")
    require(gpu_env is not None or getattr(args, "gpu_aer", None) is None, "--gpu-aer needs --gpu-env")
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
    contents: dict[str, bytes] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as bundle:
        for path in sorted(set(files)):
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digests[rel] = sha256(data)
            contents[rel] = data
            bundle.writestr(rel, data)
        device = "CPU" if args.machine == "cpu" or args.machine.startswith("Tpu") else "GPU"
        records = [dataset_record(slug) for slug in dataset_slugs]
        # A bundle dataset is unpacked into the repository and checked against
        # its manifest; an artifact stays a file under /kaggle/input.
        datasets = [d for d in records if d.get("schema") != ARTIFACT_SCHEMA]
        artifacts = [d for d in records if d.get("schema") == ARTIFACT_SCHEMA]
        job = {
            "entry": entry_rel,
            "args": list(args.args),
            "smoke": smoke,
            "device": device,
            "pin_groups": {group: list(PIN_GROUPS[group]) for group in getattr(args, "with_groups", [])},
            "datasets": [{"ref": d["ref"], "archive": d["archive"], "files": d["files"]} for d in datasets],
            "ci_env": ci_env,
            "gpu_env": gpu_env,
        }
        if artifacts:
            job["artifacts"] = [{"ref": d["ref"], "file": d["file"], "sha256": d["sha256"]} for d in artifacts]
        bundle.writestr("kaggle_kernel/kernel_job.json", json.dumps(job, indent=1) + "\n")
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    extra = [pin for group in getattr(args, "with_groups", []) for pin in PIN_GROUPS[group]]
    runner = RUNNER.format(pins=list(kernel_pins(args.machine)), extra=extra, bundle=pack_bundle(buffer.getvalue()))
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
        metadata["docker_image_pinning_type"] = "latest"
    if records:
        metadata["dataset_sources"] = [d["ref"] for d in records]
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
        "ci_env": ci_env,
        "gpu_env": gpu_env,
        # kernel_main.entry_aer_device: CI's CPU under --ci-env, else the machine's device.
        "aer_device": "CPU" if ci_env else device,
        "calibration_snapshots": bundled_calibrations(contents),
        "bundle": digests,
        "datasets": {d["ref"]: record_digest(d) for d in records},
        "run_py_sha256": sha256((kernel_dir / "run.py").read_bytes()),
        "pushed_utc": stamp,
    }
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    return submission


def latest_state(ref: str) -> str | None:
    """The KernelWorkerStatus name of the kernel's latest version; None when the account holds no kernel at ref.

    GetKernelSessionStatus answers a slug that holds no kernel with HTTP 403
    or 404 (the Kaggle CLI's kernels_status reports a 401 or 403 as a wrong
    slug); every other failure raises, so the push that asked refuses.
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelSessionStatusRequest
    from requests.exceptions import HTTPError

    owner, slug = ref.split("/")
    api = KaggleApi()
    api.authenticate()
    request = ApiGetKernelSessionStatusRequest()
    request.user_name = owner
    request.kernel_slug = slug
    try:
        with api.build_kaggle_client() as client:
            response = client.kernels.kernels_api_client.get_kernel_session_status(request)
    except HTTPError as error:
        if error.response is not None and error.response.status_code in (403, 404):
            return None
        raise
    return str(response.status.name)


def require_no_live_version(
    ref: str,
    state: Callable[[str], str | None] = latest_state,
    versions: Callable[[str], list[dict[str, Any]]] | None = None,
) -> None:
    """Refuse while any version of ref runs or queues; Kaggle answers status for the latest version only.

    A new version leaves every older version's session running, each billing
    its accelerator, so the latest state alone misses an older live session.
    ListKernelVersions (scripts/kaggle_sessions.py) returns every version's
    session; a slug Kaggle does not hold has none. A listing that fails
    refuses the push, since no version's state is then known.
    """
    import kaggle_sessions

    latest = state(ref)
    if latest is None:
        return
    remedy = f"cancel every live version (scripts/kaggle_sessions.py cancel-running {ref}) or push under a new slug"
    require(latest not in kaggle_sessions.LIVE, f"{ref}: the latest version is {latest}; {remedy}")

    def browser_listing(name: str) -> list[dict[str, Any]]:
        return kaggle_sessions.list_versions(name, kaggle_sessions.default_profile())

    try:
        rows = (versions or browser_listing)(ref)
    except Exception as error:
        raise SystemExit(f"{ref}: cannot list its versions ({error!r}); the accelerator push refuses") from error
    live = kaggle_sessions.live_sessions(rows)
    require(
        not live,
        f"{ref}: "
        + ", ".join(f"version {row['version']} is {row['status']} (session {row['session_id']})" for row in live)
        + f"; {remedy}",
    )


def push(args: argparse.Namespace) -> int:
    # The smoke probe measures the widest circuits a GPU runs; on a CPU
    # machine it would record only that no GPU is attached. It finishes in
    # minutes, so it carries a short ceiling when none is given.
    if args.smoke and args.machine == "cpu":
        args.machine = GPU_MACHINE
    if args.smoke and not args.timeout:
        args.timeout = SMOKE_TIMEOUT_SECONDS
    # An accelerator session bills its whole wall time against the weekly
    # quota and runs to the 12-hour limit unless it ends or is cancelled by
    # its session id (scripts/kaggle_sessions.py), so a GPU or TPU push states
    # its ceiling; Kaggle ends the session at --timeout.
    require(
        args.machine == "cpu" or 0 < args.timeout <= MAX_ACCELERATOR_SECONDS,
        f"a {args.machine} push needs --timeout SECONDS (at most {MAX_ACCELERATOR_SECONDS})",
    )
    if args.machine != "cpu":
        require_no_live_version(f"{username()}/{args.slug}")
    revision = git_commit()
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = RESULTS / f"{stamp}-{args.slug}"
    build_kernel(args, run_dir, username(), stamp, revision)
    kernel_dir = run_dir / "kernel"
    import shutil

    # SaveKernel refuses a run.py above KERNEL_SOURCE_LIMIT with a bare HTTP
    # 400, so the size is checked before the request names the cause.
    size = (kernel_dir / "run.py").stat().st_size
    if size > KERNEL_SOURCE_LIMIT:
        shutil.rmtree(run_dir)
        raise SystemExit(
            f"run.py is {size} bytes, above Kaggle's script limit (KERNEL_SOURCE_LIMIT {KERNEL_SOURCE_LIMIT}); "
            "drop --include paths or attach them as a dataset"
        )
    push_args = ["kernels", "push", "-p", str(kernel_dir)]
    if args.machine != "cpu":
        # kernel-metadata.json's machine_shape alone runs the kernel on a CPU
        # machine; the push's --accelerator selects the hardware.
        push_args += ["--accelerator", args.machine]
    if args.timeout:
        push_args += ["-t", str(args.timeout)]
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
    if version is None:
        raise AssertionError
    submission = submission_of(run_dir)
    submission["kernel_version"] = int(version.group(1))
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    print(reply)
    print(run_dir.relative_to(ROOT))
    return 0


def _dataset_history_self_test() -> None:
    """Three uploads of one dataset keep every archive; a foreign digest or ref is refused."""
    ref = "owner/data"

    def upload(digest: str, files: int) -> dict[str, Any]:
        return {
            "ref": ref,
            "archive_sha256": digest,
            "git_commit": digest[:7],
            "files": {str(k): "" for k in range(files)},
        }

    first = with_history(upload("a" * 64, 1), None)
    third = with_history(upload("c" * 64, 3), with_history(upload("b" * 64, 2), first))
    require(first["history"] == [], "a first upload carries history")
    require([entry["files"] for entry in third["history"]] == [2, 1], f"history out of order {third['history']}")
    for digest in ("a", "b", "c"):
        require_dataset_version("run", ref, digest * 64, third)
    for action, fragment in (
        (lambda: require_dataset_version("run", ref, "d" * 64, third), "is no recorded version"),
        (lambda: require_dataset_version("run", "owner/other", "c" * 64, third), "has the record of"),
        (lambda: with_history({**upload("e" * 64, 1), "ref": "owner/other"}, third), "replaced by"),
    ):
        try:
            action()
        except SystemExit as reason:
            require(fragment in str(reason), f"dataset history: {reason} lacks {fragment!r}")
            continue
        raise SystemExit(f"dataset history: expected a failure naming {fragment!r}")


def self_test(args: argparse.Namespace) -> int:
    """Build the Design C kernel (CPU, GPU and TPU) offline, and check bundles, metadata and code."""

    entry = "scripts/design_c_cubic_noise.py"
    data = "docs/evidence/calibration/ibm_kingston.json"
    for machine in (DEFAULT_MACHINE, GPU_MACHINE, TPU_MACHINE):
        submission = _self_test_kernel(entry, data, machine)
    _native_tls_self_test()
    _killed_entry_self_test()
    _calibration_identity_self_test()
    _gpu_env_self_test(data)
    _gpu_aer_self_test(data)
    _push_guard_self_test()
    _dataset_history_self_test()
    print(
        f"kaggle_run self-test: {len(submission['bundle'])} bundled files, private CPU, GPU and TPU kernels "
        "with their Aer device and bundled calibration identity, "
        "an entry killed mid-run keeps its stdout and record, "
        "a GPU-environment kernel whose pin and GPU checks name every fallback, "
        "a cu13 GPU Aer kernel admitted only on its verified wheel artifact, "
        "an accelerator push refused while an older version runs, "
        "a re-versioned dataset that keeps every earlier archive"
    )
    return 0


def _calibration_identity_self_test() -> None:
    """calibration_identity reads the identity fields of a snapshot and nothing from other bytes."""
    synthetic = {
        "schema": f"{CALIBRATION_SCHEMA_PREFIX}v2",
        "backend": "ibm_fixture",
        "calibration": "2000-01-01T00:00:00+00:00",
        "backend_version": "1.2.3",
        "processor_type": {"family": "Heron", "revision": "2"},
        "instructions": {},
    }
    expected = {key: synthetic[key] for key in ("backend", "calibration", "backend_version", "processor_type")}
    require(calibration_identity(json.dumps(synthetic).encode()) == expected, "snapshot identity fields")
    require(
        calibration_identity(b'{"schema": "other-schema-v1"}') is None and calibration_identity(b"\xff") is None,
        "a file that is no calibration snapshot yields an identity",
    )


def _push_guard_self_test() -> None:
    """require_no_live_version over stubbed states and version listings; no Kaggle call."""

    def row(version: int, status: str) -> dict[str, Any]:
        return {"session_id": 100 + version, "version": version, "status": status, "created": None, "kernel_id": 7}

    def refused(latest: str | None, rows: list[dict[str, Any]]) -> str | None:
        listed: list[str] = []

        def versions(ref: str) -> list[dict[str, Any]]:
            listed.append(ref)
            return rows

        try:
            require_no_live_version("owner/slug", lambda ref: latest, versions)
        except SystemExit as stop:
            return str(stop)
        require(listed == ([] if latest is None else ["owner/slug"]), f"listing calls {listed}")
        return None

    older = refused("COMPLETE", [row(1, "RUNNING"), row(2, "COMPLETE")])
    require(older is not None and "version 1 is RUNNING (session 101)" in older, f"older running version: {older}")
    queued = refused("ERROR", [row(1, "COMPLETE"), row(2, "QUEUED"), row(3, "ERROR")])
    require(queued is not None and "version 2 is QUEUED" in queued, f"older queued version: {queued}")
    latest = refused("RUNNING", [row(1, "RUNNING")])
    require(latest is not None and "the latest version is RUNNING" in latest, f"latest running version: {latest}")
    require(refused("COMPLETE", [row(1, "ERROR"), row(2, "COMPLETE")]) is None, "finished versions refuse the push")
    require(refused(None, []) is None, "a new slug refuses the push")

    def failing(ref: str) -> list[dict[str, Any]]:
        raise RuntimeError("no browser")

    try:
        require_no_live_version("owner/slug", lambda ref: "COMPLETE", failing)
    except SystemExit as stop:
        require("cannot list its versions" in str(stop), f"failed listing: {stop}")
    else:
        raise SystemExit("a failed version listing lets the push through")


def _gpu_env_self_test(data: str) -> None:
    """A --gpu-env kernel bundles the pin files and its spec, and gpu_env_failures names every fallback.

    A report holding every pin, the GPU Aer as the only owner of
    qiskit_aer/__init__.py, both GPUs, and GPU Bell runs with cuStateVec
    passes; each single change away from it is named.
    """
    import tempfile

    sys.path.insert(0, str(ROOT / "kaggle_kernel"))
    import kernel_main

    build_args = argparse.Namespace(
        entry="scripts/aer_gpu_probe.py",
        smoke=False,
        include=[data],
        args=["--require-gpu"],
        slug="self-test",
        machine=GPU_MACHINE,
        with_groups=[],
        gpu_env=True,
    )
    with tempfile.TemporaryDirectory() as scratch:
        submission = build_kernel(build_args, Path(scratch) / "run", "owner", "2000-01-01T000000Z", "0" * 40)
        job = bundled_job(Path(scratch) / "run/kernel/run.py")
    spec: dict[str, Any] = {"uv": UV_PIN, "aer_pins": list(GPU_ENV_AER_PINS), "gpus": MACHINE_GPUS[GPU_MACHINE]}
    require(job["gpu_env"] == submission["gpu_env"] == spec, f"GPU environment spec {job['gpu_env']}")
    require(all(name in submission["bundle"] for name in CI_ENV_FILES), "a --gpu-env bundle lacks the pin files")
    pins = kernel_main.pinned(ROOT, spec["aer_pins"])
    require(
        "qiskit-aer" not in pins and pins["qiskit-aer-gpu-cu11"] == "0.17.2" and pins["numpy"] == "2.5.4",
        f"GPU environment pins {pins}",
    )
    run = {"success": True, "device": "GPU", "cuStateVec_enable": False}
    report: dict[str, Any] = {
        "installed": dict(pins),
        "qiskit_aer_owners": ["qiskit_aer_gpu_cu11"],
        "devices": ["CPU", "GPU"],
        "foreign_paths": [],
        "runs": {"gpu": run, "custatevec": {**run, "cuStateVec_enable": True}},
    }
    passing = kernel_main.gpu_env_failures(pins, report, 2, 2)
    require(passing == [], f"a GPU environment that holds every pin fails: {passing}")
    changes = {
        "a version": ({**report, "installed": {**pins, "numpy": "2.1.3"}}, 2),
        "the CPU Aer owner": ({**report, "qiskit_aer_owners": ["qiskit-aer", "qiskit-aer-gpu-cu11"]}, 2),
        "a missing GPU": (report, 1),
        "the device list": ({**report, "devices": ["CPU"]}, 2),
        "a CPU Bell run": ({**report, "runs": {**report["runs"], "gpu": {**run, "device": "CPU"}}}, 2),
        "cuStateVec off": ({**report, "runs": {**report["runs"], "custatevec": run}}, 2),
        "a raised run": ({**report, "runs": {**report["runs"], "custatevec": {"error": "RuntimeError"}}}, 2),
        "an image path": ({**report, "foreign_paths": ["/usr/local/lib/python3.13/dist-packages"]}, 2),
        "an unlisted sys.path": ({key: value for key, value in report.items() if key != "foreign_paths"}, 2),
    }
    for change, (changed, listed) in changes.items():
        require(bool(kernel_main.gpu_env_failures(pins, changed, 2, listed)), f"gpu_env_failures passes {change}")
    with tempfile.TemporaryDirectory() as scratch:
        torch_args = argparse.Namespace(**{**vars(build_args), "gpu_env_with": ["torch"]})
        build_kernel(torch_args, Path(scratch) / "run", "owner", "2000-01-01T000000Z", "0" * 40)
        torch_job = bundled_job(Path(scratch) / "run/kernel/run.py")
    require(
        torch_job["gpu_env"] == {**spec, "extra_pins": list(GPU_ENV_GROUPS["torch"])},
        f"torch spec {torch_job['gpu_env']}",
    )
    torch_pins = kernel_main.pinned(ROOT, spec["aer_pins"] + torch_job["gpu_env"]["extra_pins"])
    require(torch_pins["torch"] == "2.14.1", f"GPU environment pins {torch_pins}")
    require(
        kernel_main.gpu_env_failures(torch_pins, {**report, "installed": {**pins, "torch": "2.14.1"}}, 2, 2) == []
        and bool(kernel_main.gpu_env_failures(torch_pins, report, 2, 2)),
        "gpu_env_failures does not hold the torch pin",
    )
    with tempfile.TemporaryDirectory() as scratch:
        try:
            build_kernel(
                argparse.Namespace(**{**vars(build_args), "with_groups": ["quantum-tools"]}),
                Path(scratch) / "run",
                "owner",
                "2000-01-01T000000Z",
                "0" * 40,
            )
        except SystemExit:
            pass
        else:
            raise SystemExit("kaggle_run self-test: --gpu-env accepted a --with group")


def _expect_refusal(action: Callable[[], object], fragment: str, case: str) -> None:
    try:
        action()
    except SystemExit as reason:
        require(fragment in str(reason), f"{case}: {reason} lacks {fragment!r}")
        return
    raise SystemExit(f"kaggle_run self-test: {case} was accepted")


def _gpu_aer_self_test(data: str) -> None:
    """--gpu-aer: cu11 stays the default spec, cu13 needs its artifact record, and the kernel verifies the wheel.

    The artifact records live in a temporary DATASETS directory, and the
    kernel side reads a temporary /kaggle/input tree, so no Kaggle call or
    repository write happens.
    """
    import tempfile
    from unittest.mock import patch

    sys.path.insert(0, str(ROOT / "kaggle_kernel"))
    import kernel_main

    listed = [
        line.strip()
        for line in (ROOT / CU13_RUNTIME_PINS_FILE).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    require(tuple(listed) == CU13_RUNTIME_PINS, f"CU13_RUNTIME_PINS differs from {CU13_RUNTIME_PINS_FILE}: {listed}")
    cu11 = ("qiskit-aer-gpu-cu11==0.17.2", "cuquantum-cu11==24.8.0", "cutensor-cu11==2.2.0")
    require(GPU_AER_PINS["cu11"] == GPU_ENV_AER_PINS == cu11, f"cu11 GPU Aer pins {GPU_AER_PINS['cu11']}")
    base = argparse.Namespace(
        entry="scripts/aer_gpu_probe.py",
        smoke=False,
        include=[data],
        args=["--require-gpu"],
        slug="self-test",
        machine=GPU_MACHINE,
        with_groups=[],
        gpu_env=True,
    )

    def built(**changes: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        with tempfile.TemporaryDirectory() as scratch:
            run = Path(scratch) / "run"
            submission = build_kernel(
                argparse.Namespace(**{**vars(base), **changes}), run, "owner", "2000-01-01T000000Z", "0" * 40
            )
            metadata = json.loads((run / "kernel/kernel-metadata.json").read_text(encoding="utf-8"))
            return submission, bundled_job(run / "kernel/run.py"), metadata

    default_submission, default_job, default_metadata = built()
    explicit_submission, explicit_job, explicit_metadata = built(gpu_aer="cu11")
    spec = {"uv": UV_PIN, "aer_pins": list(cu11), "gpus": MACHINE_GPUS[GPU_MACHINE]}
    require(
        json.dumps(default_job) == json.dumps(explicit_job)
        and default_job["gpu_env"] == spec
        and "artifacts" not in default_job
        and "dataset_sources" not in default_metadata
        and default_metadata == explicit_metadata
        and default_submission["gpu_env"] == explicit_submission["gpu_env"] == spec
        and default_submission["datasets"] == {},
        f"the cu11 default changed: {default_job['gpu_env']} {explicit_job['gpu_env']}",
    )
    _expect_refusal(lambda: built(gpu_env=False, gpu_aer="cu11"), "--gpu-aer needs --gpu-env", "--gpu-aer alone")

    slug, wheel, digest = AER_GPU_WHEELS["cu13"]
    ref = f"owner/{slug}"
    with tempfile.TemporaryDirectory() as scratch, patch.dict(globals(), {"DATASETS": Path(scratch)}):
        record_path = Path(scratch) / f"{slug}.json"
        _expect_refusal(lambda: built(gpu_aer="cu13"), "no retained dataset record", "cu13 without a record")
        valid = {"schema": ARTIFACT_SCHEMA, "ref": ref, "file": wheel, "sha256": digest, "size": 1, "history": []}
        for change, value in (("sha256", "0" * 64), ("file", "other.whl"), ("schema", "kaggle-dataset-v1")):
            record_path.write_text(json.dumps({**valid, change: value}), encoding="utf-8")
            _expect_refusal(lambda: built(gpu_aer="cu13"), "run `artifact`", f"cu13 with a record of another {change}")
        record_path.write_text(json.dumps(valid), encoding="utf-8")
        submission, job, metadata = built(gpu_aer="cu13")
        attached, attached_job, _ = built(gpu_aer="cu13", dataset=[slug])
    cu13_pins = ["qiskit-aer-gpu-cu13==0.17.2", *CU13_RUNTIME_PINS]
    cu13_spec: dict[str, Any] = {
        "uv": UV_PIN,
        "aer_pins": cu13_pins,
        "gpus": MACHINE_GPUS[GPU_MACHINE],
        "find_links": {"dataset": ref, "wheel": wheel},
        "wheel_sha256": digest,
        "cuda_in_venv": True,
    }
    require(
        job["gpu_env"] == submission["gpu_env"] == cu13_spec
        and job["datasets"] == []
        and job["artifacts"] == [{"ref": ref, "file": wheel, "sha256": digest}]
        and metadata["dataset_sources"] == [ref]
        and submission["datasets"] == attached["datasets"] == {ref: digest}
        and attached_job["artifacts"] == job["artifacts"],
        f"cu13 kernel spec {job['gpu_env']} artifacts {job.get('artifacts')} sources {metadata.get('dataset_sources')}",
    )
    pins = kernel_main.pinned(ROOT, cu13_pins)
    require(
        "qiskit-aer" not in pins and "qiskit-aer-gpu-cu11" not in pins and pins["qiskit-aer-gpu-cu13"] == "0.17.2",
        f"cu13 GPU environment pins {pins}",
    )
    run = {"success": True, "device": "GPU", "cuStateVec_enable": False}
    report: dict[str, Any] = {
        "installed": dict(pins),
        "qiskit_aer_owners": ["qiskit-aer-gpu-cu13"],
        "devices": ["CPU", "GPU"],
        "foreign_paths": [],
        "runs": {"gpu": run, "custatevec": {**run, "cuStateVec_enable": True}},
    }
    require(kernel_main.gpu_env_failures(pins, report, 2, 2) == [], "a holding cu13 environment fails")
    for change, changed in (
        ("the cu11 owner", {**report, "qiskit_aer_owners": ["qiskit-aer-gpu-cu11"]}),
        ("a missing cuStateVec wheel", {**report, "installed": {**pins, "custatevec-cu13": None}}),
    ):
        require(bool(kernel_main.gpu_env_failures(pins, changed, 2, 2)), f"gpu_env_failures passes {change}")
    # With the venv as cuda_root, a library the loader took from the image
    # fails while the host driver's libcuda.so passes; the retained T4 run's
    # report, mapped inside the kernel's venv, holds the rule.
    venv = kernel_main.GPU_VENV
    site = venv / "lib/python3.13/site-packages"
    report["cuda_libraries"] = [
        str(site / "cuquantum/lib/libcustatevec.so.1"),
        str(site / "nvidia/cu13/lib/libcudart.so.13"),
        "/usr/local/nvidia/lib64/libcuda.so.580.178.04",
    ]
    require(kernel_main.gpu_env_failures(pins, report, 2, 2, venv) == [], "venv CUDA libraries fail")
    for change, libraries in (
        ("an image cuStateVec", [*report["cuda_libraries"], "/usr/local/cuda/lib64/libcustatevec.so.1"]),
        ("no mapped CUDA library", []),
    ):
        changed = {**report, "cuda_libraries": libraries}
        require(bool(kernel_main.gpu_env_failures(pins, changed, 2, 2, venv)), f"gpu_env_failures passes {change}")
    t4_run = ROOT / "results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config"
    retained = json.loads((t4_run / "output/output/gpu_env.json").read_text(encoding="utf-8"))
    require(
        kernel_main.gpu_env_failures(retained["pins"], retained["report"], 2, retained["listed_gpus"], venv) == [],
        f"the retained cu13 T4 report fails the venv rule: {retained['report'].get('cuda_libraries')}",
    )

    payload = b"self-test wheel bytes"
    kernel_spec = {**cu13_spec, "wheel_sha256": sha256(payload)}
    with tempfile.TemporaryDirectory() as scratch:
        inputs, wheelhouse = Path(scratch) / "input", Path(scratch) / "wheelhouse"
        mounted = inputs / "datasets/owner" / slug / wheel
        missing, refused = kernel_main.verified_wheel(kernel_spec, inputs, wheelhouse)
        require(bool(refused) and not wheelhouse.exists(), f"a missing wheel is admitted: {missing}")
        mounted.parent.mkdir(parents=True)
        mounted.write_bytes(payload)
        admitted, refused = kernel_main.verified_wheel(kernel_spec, inputs, wheelhouse)
        require(
            refused == []
            and admitted["find_links"] == str(wheelhouse)
            and (wheelhouse / wheel).read_bytes() == payload
            and admitted["sha256"] == kernel_spec["wheel_sha256"],
            f"a verified wheel is refused: {admitted} {refused}",
        )
        (wheelhouse / wheel).unlink()
        mounted.write_bytes(payload + b"!")
        changed, refused = kernel_main.verified_wheel(kernel_spec, inputs, wheelhouse)
        require(
            len(refused) == 1 and "has sha256" in refused[0] and not (wheelhouse / wheel).exists(),
            f"a changed wheel is admitted: {changed} {refused}",
        )

        def no_install(name: str, *args: str, **kwargs: Any) -> str:
            raise SystemExit(f"gpu_interpreter ran {name} on an unverified wheel")

        with patch.object(kernel_main, "checked", no_install):
            _, _, record = kernel_main.gpu_interpreter(ROOT, kernel_spec, Path(scratch) / "venv", inputs, wheelhouse)
        require(
            record["failures"] == refused and record["wheel"]["sha256"] == sha256(payload + b"!"),
            f"gpu_interpreter's refusal record {record}",
        )

        # A verified wheel installs as a direct reference to its copy, so no
        # index can supply qiskit-aer-gpu-cu13; every other pin stays exact.
        mounted.write_bytes(payload)
        calls: dict[str, dict[str, str]] = {}
        scratch_site = Path(scratch) / "venv" / site.relative_to(venv)
        scratch_libraries = [str(scratch_site / Path(name).relative_to(site)) for name in report["cuda_libraries"][:2]]
        holding = json.dumps({**report, "installed": dict(pins), "cuda_libraries": scratch_libraries})

        def recorded(name: str, *args: str, **kwargs: Any) -> str:
            calls[name] = dict(kwargs.get("env") or {})
            return holding if name == "gpu-env-report" else ""

        with patch.object(kernel_main, "checked", recorded), patch.object(kernel_main, "gpus", return_value=[{}, {}]):
            _, _, record = kernel_main.gpu_interpreter(ROOT, kernel_spec, Path(scratch) / "venv", inputs, wheelhouse)
        install = calls["install-pins"]["AER_PINS"].split()
        require(
            install[0] == f"qiskit-aer-gpu-cu13@{(wheelhouse / wheel).as_uri()}"
            and install[1:] == list(CU13_RUNTIME_PINS)
            and calls["install-pins"]["PIP_FIND_LINKS"] == str(wheelhouse)
            and record["failures"] == []
            and record["wheel"]["find_links"] == str(wheelhouse),
            f"the verified wheel's install: {install} {record.get('failures')}",
        )

        # Every attached artifact, not only the GPU wheel, is checked against
        # its retained digest before the entry runs.
        entry = {"ref": ref, "file": wheel, "sha256": sha256(payload)}
        checked = kernel_main.verify_artifacts([entry], inputs)
        require(
            checked == {ref: {"path": str(mounted), "sha256": entry["sha256"], "size": len(payload)}},
            f"a matching artifact reads {checked}",
        )
        _expect_refusal(
            lambda: kernel_main.verify_artifacts([{**entry, "ref": "owner/absent"}], inputs),
            "0 files named",
            "an artifact absent from the inputs",
        )
        mounted.write_bytes(payload + b"!")
        _expect_refusal(lambda: kernel_main.verify_artifacts([entry], inputs), "has sha256", "a changed artifact")

    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / wheel
        path.write_bytes(payload)
        _expect_refusal(lambda: artifact_record(path, "0" * 64, ref), "has sha256", "an artifact of other bytes")
        first = with_history({**artifact_record(path, sha256(payload), ref), "git_commit": "a" * 7}, None)
    second = with_history({**first, "sha256": "b" * 64, "size": 2, "git_commit": "b" * 7}, first)
    require(
        second["history"] == [{"sha256": sha256(payload), "size": len(payload), "git_commit": "a" * 7}],
        f"artifact history {second['history']}",
    )
    require_dataset_version("run", ref, sha256(payload), second)
    require_dataset_version("run", ref, "b" * 64, second)
    _expect_refusal(lambda: require_dataset_version("run", ref, "c" * 64, second), "is no recorded version", "a stray")
    bundle = {"schema": "kaggle-dataset-v1", "ref": ref, "archive_sha256": "d" * 64, "git_commit": "d", "files": {}}
    _expect_refusal(lambda: with_history(bundle, second), "is kaggle-artifact-v1", "a bundle over an artifact")


def _native_tls_self_test() -> None:
    """Every scientific child receives loader capacity before startup; GPU calls use synthetic reports."""
    import os
    import tempfile
    from types import SimpleNamespace
    from unittest.mock import Mock, patch

    sys.path.insert(0, str(ROOT / "kaggle_kernel"))
    import kernel_main

    tunable = kernel_main.STATIC_TLS_TUNABLE
    for original, expected in (
        ("", f"{tunable}=4096"),
        (f"glibc.malloc.trim_threshold=1024:{tunable}=512", f"glibc.malloc.trim_threshold=1024:{tunable}=4096"),
        (f"{tunable}=8192:glibc.malloc.arena_max=2", f"glibc.malloc.arena_max=2:{tunable}=8192"),
        (f"{tunable}=invalid:{tunable}=2048", f"{tunable}=4096"),
    ):
        source = {"GLIBC_TUNABLES": original, "CUSTOM_FLAG": "retained"}
        updated = kernel_main.native_environment(source)
        require(updated == source | {"GLIBC_TUNABLES": expected}, f"native loader environment {updated}")
        require(source["GLIBC_TUNABLES"] == original, "native_environment mutates the caller's environment")
        require(kernel_main.native_environment(updated) == updated, "native loader capacity changes on repeat")

    with patch.dict(os.environ, {"GLIBC_TUNABLES": "glibc.malloc.arena_max=2"}):
        expected_environment = kernel_main.native_environment(os.environ)
        launch = Mock(return_value=subprocess.CompletedProcess([], 0))
        # Execute the generated bootstrap's launch statements, after bundle
        # extraction, with process creation replaced by an argument recorder.
        generated = ast.parse(RUNNER.format(pins=(), extra=(), bundle=""))
        tail = ast.Module(body=generated.body[-3:], type_ignores=[])
        namespace = {
            "repo": ROOT,
            "os": os,
            "sys": SimpleNamespace(executable=sys.executable, path=[]),
            "subprocess": SimpleNamespace(run=launch),
        }
        try:
            exec(compile(tail, "<generated kernel launch>", "exec"), namespace)
        except SystemExit as result:
            require(result.code == 0, f"bootstrap launch exits {result.code}")
        require(launch.call_count == 1, "bootstrap launches more than one kernel interpreter")
        require(launch.call_args.kwargs["env"] == expected_environment, "bootstrap child lacks startup TLS capacity")
        require(
            launch.call_args.args[0] == [sys.executable, "-B", "kaggle_kernel/kernel_main.py"],
            "bootstrap changes the kernel interpreter arguments",
        )

        with patch.object(kernel_main, "checked", return_value="") as checked:
            _, environment = kernel_main.ci_interpreter(ROOT, UV_PIN, CI_PYTHON)
        require(
            environment["GLIBC_TUNABLES"] == expected_environment["GLIBC_TUNABLES"], "CI interpreter lacks native TLS"
        )
        require(environment["GOROROBA_AER_DEVICE"] == "CPU", "CI interpreter changes its Aer device")
        for call in checked.call_args_list[-2:]:
            require(call.kwargs["env"] == environment, "CI install or freeze lacks the startup environment")

        def checked_gpu(name: str, *args: str, **kwargs: Any) -> str:
            del args
            if name == "gpu-env-report":
                require(
                    kwargs["env"]["GLIBC_TUNABLES"] == expected_environment["GLIBC_TUNABLES"],
                    "GPU report child lacks startup TLS capacity",
                )
                return "{}"
            return ""

        with (
            patch.object(kernel_main, "checked", checked_gpu),
            patch.object(kernel_main, "gpus", return_value=[]),
            patch.object(kernel_main, "gpu_env_failures", return_value=[]),
        ):
            _, environment, _ = kernel_main.gpu_interpreter(
                ROOT, {"uv": UV_PIN, "aer_pins": list(GPU_ENV_AER_PINS), "gpus": 2}
            )
        require(
            environment["GLIBC_TUNABLES"] == expected_environment["GLIBC_TUNABLES"], "GPU interpreter lacks native TLS"
        )
        require(environment["GOROROBA_AER_DEVICE"] == "GPU", "GPU interpreter changes its Aer device")

        with (
            patch.object(kernel_main, "gpus", return_value=[{}]),
            patch.object(kernel_main, "DM_WIDTHS", (1,)),
            patch.object(kernel_main, "SV_WIDTHS", (1,)),
            patch.object(kernel_main, "write"),
            patch.object(
                kernel_main.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, '{"width": 1, "ok": true}\n', ""),
            ) as trials,
        ):
            kernel_main.capacity()
        require(trials.call_count == 2, "mock capacity probe changes its trial count")
        for trial in trials.call_args_list:
            require(trial.kwargs["env"] == expected_environment, "capacity child lacks startup TLS capacity")

        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch)
            stub = "import os; print(os.environ['GLIBC_TUNABLES'])"
            process = kernel_main.start_entry([sys.executable, "-c", stub], out, dict(os.environ), out)
            require(process.wait(timeout=30) == 0, "native TLS entry child failed")
            require(
                (out / "stdout.txt").read_text().strip() == expected_environment["GLIBC_TUNABLES"],
                "entry child lacks startup TLS capacity",
            )


def _killed_entry_self_test() -> None:
    """A stub entry prints, writes its record under the output directory and is killed: both survive."""
    import os
    import tempfile

    sys.path.insert(0, str(ROOT / "kaggle_kernel"))
    import kernel_main

    stub = (
        "import pathlib, sys, time\n"
        "print('row 1')\n"
        "pathlib.Path(sys.argv[1]).write_text('{\"rows\": [1]}', encoding='utf-8')\n"
        "time.sleep(60)\n"
    )
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch)
        record = out / "record.json"
        env = {key: value for key, value in os.environ.items() if key != "PYTHONUNBUFFERED"}
        proc = kernel_main.start_entry([sys.executable, "-c", stub, str(record)], out, env, out)
        deadline = time.monotonic() + 30
        while not record.exists() and time.monotonic() < deadline and proc.poll() is None:
            time.sleep(0.05)
        proc.kill()
        proc.wait()
        stdout = (out / "stdout.txt").read_text(encoding="utf-8")
        require(record.is_file(), "a killed entry's record under the output directory is missing")
        require(stdout == "row 1\n", f"a killed entry's stdout reads {stdout!r}")


def pack_bundle(archive: bytes) -> str:
    """A stored zip as one xz stream in base64, the BUNDLE string run.py embeds.

    Per-member deflate compresses each file alone; one xz stream over the
    stored archive also removes the redundancy between files, which keeps
    run.py about a third smaller under KERNEL_SOURCE_LIMIT.
    """
    return base64.b64encode(lzma.compress(archive, preset=9 | lzma.PRESET_EXTREME)).decode("ascii")


def bundled_job(run_py: Path) -> dict[str, Any]:
    """The kernel_job.json inside a generated run.py's embedded bundle."""
    found = re.search(r'BUNDLE = "([^"]+)"', run_py.read_text(encoding="utf-8"))
    require(found is not None, f"{run_py} embeds no bundle")
    if found is None:
        raise AssertionError
    archive = zipfile.ZipFile(io.BytesIO(lzma.decompress(base64.b64decode(found.group(1)))))
    return dict(json.loads(archive.read("kaggle_kernel/kernel_job.json")))


def _self_test_kernel(entry: str, data: str, machine: str) -> dict[str, Any]:
    import py_compile
    import tempfile

    build_args = argparse.Namespace(
        entry=entry,
        smoke=False,
        include=[data],
        args=["--pairs", "1,16"],
        slug="self-test",
        machine=machine,
        with_groups=["quantum-tools"],
    )
    with tempfile.TemporaryDirectory() as scratch:
        run_dir = Path(scratch) / "run"
        submission = build_kernel(build_args, run_dir, "owner", "2000-01-01T000000Z", "0" * 40)
        expected = (entry, data, "gororoba_quantum/calibration_snapshot.py", "gororoba_quantum/cd_core.py")
        for needed in (*expected, *KERNEL_FILES):
            require(needed in submission["bundle"], f"bundle lacks {needed}")
        # The entry reaches qd_platform only through quandela_qrng.draw's lazy import.
        require(
            "scripts/qd_platform.py" not in submission["bundle"], "bundle carries a lazily imported provider client"
        )
        for rel, digest in submission["bundle"].items():
            require(digest == sha256((ROOT / rel).read_bytes()), f"bundle digest of {rel} differs from the tree")
        metadata = json.loads((run_dir / "kernel/kernel-metadata.json").read_text(encoding="utf-8"))
        gpu = machine not in ("cpu",) and not machine.startswith("Tpu")
        require(
            metadata["is_private"] is True and metadata["enable_gpu"] is gpu, f"{machine}: kernel metadata {metadata}"
        )
        require(
            ("machine_shape" in metadata) is (machine != "cpu"),
            f"{machine}: machine_shape {metadata.get('machine_shape')}",
        )
        require(metadata["id"] == "owner/self-test", f"kernel id {metadata['id']}")
        py_compile.compile(str(run_dir / "kernel/run.py"), doraise=True)
        runner = (run_dir / "kernel/run.py").read_text(encoding="utf-8")
        # run.py's own decoding, so the kernel unpacks exactly the bundled bytes.
        embedded = re.search(r'BUNDLE = "([^"]+)"', runner)
        require(embedded is not None, f"{machine}: run.py embeds no bundle")
        if embedded is None:
            raise AssertionError
        unpacked = zipfile.ZipFile(io.BytesIO(lzma.decompress(base64.b64decode(embedded.group(1)))))
        members = {name: sha256(unpacked.read(name)) for name in unpacked.namelist()}
        require(
            {name: members.get(name) for name in submission["bundle"]} == submission["bundle"],
            f"{machine}: run.py's bundle differs from the tree",
        )
        require(len(runner.encode("utf-8")) <= KERNEL_SOURCE_LIMIT, f"{machine}: run.py exceeds KERNEL_SOURCE_LIMIT")
        require(all(pin in runner for pin in kernel_pins(machine)), f"{machine}: run.py lacks a pin")
        require(all(pin in runner for pin in PIN_GROUPS["quantum-tools"]), f"{machine}: run.py lacks a group pin")
        for path in kernel_docs():
            require(path.relative_to(ROOT).as_posix() in submission["bundle"], f"bundle lacks {path}")
        for name in KERNEL_DOC_CAPTURES:
            require(not any(rel.startswith(name + "/") for rel in submission["bundle"]), f"bundle carries {name}")
        require(
            submission["pin_groups"] == {"quantum-tools": list(PIN_GROUPS["quantum-tools"])},
            f"{machine}: submission does not record the pin group",
        )
        if machine.startswith("Tpu"):
            notebook = json.loads((run_dir / "kernel/run.ipynb").read_text(encoding="utf-8"))
            require(notebook["cells"][0]["source"] == runner, "the TPU notebook cell differs from run.py")
            require(
                metadata["kernel_type"] == "notebook"
                and "docker_image" not in metadata
                and metadata["docker_image_pinning_type"] == "latest"
                and "kaggle" not in notebook["metadata"]
                and "dockerImageVersionId" not in json.dumps(notebook["metadata"]),
                f"TPU kernel pins an image: {metadata} {notebook['metadata']}",
            )
        require(submission["untracked_inputs"] == [], f"untracked bundled inputs {submission['untracked_inputs']}")
        device = bundled_job(run_dir / "kernel/run.py")["device"]
        require(submission["aer_device"] == device == ("GPU" if gpu else "CPU"), f"{machine}: Aer device {device}")
        snapshot = json.loads((ROOT / data).read_text(encoding="utf-8"))
        identity = submission["calibration_snapshots"].get(data, {})
        require(
            set(submission["calibration_snapshots"]) == {data}
            and identity.get("backend") == snapshot["backend"]
            and identity.get("calibration") == snapshot["calibration"]
            and all(
                identity.get(key) == snapshot[key] for key in ("backend_version", "processor_type") if key in snapshot
            ),
            f"{machine}: bundled calibration identity {submission['calibration_snapshots']}",
        )
    return submission


DATASETS = RESULTS / "datasets"
ARCHIVE = "repository-files.bundle"
# A dataset that holds one file the kernel reads in place (a wheel no index
# serves); its record carries the file's name, sha256 and size.
ARTIFACT_SCHEMA = "kaggle-artifact-v1"


def dataset_record(slug: str) -> dict[str, Any]:
    path = DATASETS / f"{slug}.json"
    shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    require(path.is_file(), f"no retained dataset record {shown}; run `dataset` or `artifact` first")
    return dict(json.loads(path.read_text(encoding="utf-8")))


def record_digest(record: dict[str, Any]) -> str:
    """The sha256 a run records for an attached dataset: the artifact file's, or the bundle archive's."""
    return str(record["sha256"] if record.get("schema") == ARTIFACT_SCHEMA else record["archive_sha256"])


def with_history(record: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    """The record with every earlier version, newest first.

    A bundle version keeps its archive digest, commit and file count; an
    artifact version keeps its file digest, size and commit.
    """
    history: list[dict[str, Any]] = []
    if previous is not None:
        require(previous["ref"] == record["ref"], f"dataset record {previous['ref']} replaced by {record['ref']}")
        require(
            previous.get("schema") == record.get("schema"),
            f"dataset record {previous['ref']} is {previous.get('schema')}, not {record.get('schema')}",
        )
        if record.get("schema") == ARTIFACT_SCHEMA:
            entry = {"sha256": previous["sha256"], "size": previous["size"], "git_commit": previous["git_commit"]}
        else:
            entry = {"archive_sha256": previous["archive_sha256"], "git_commit": previous["git_commit"]}
            entry["files"] = len(previous["files"])
        history = [entry, *previous.get("history", [])]
    return {**record, "history": history}


def require_dataset_version(run: str, ref: str, digest: str, record: dict[str, Any]) -> None:
    """A run's attached archive or artifact is the record's current version or one its history names."""
    field = "sha256" if record.get("schema") == ARTIFACT_SCHEMA else "archive_sha256"
    versions = {record_digest(record), *(entry[field] for entry in record.get("history", []))}
    require(record["ref"] == ref, f"{run}: dataset {ref} has the record of {record['ref']}")
    require(digest in versions, f"{run}: dataset {ref} archive {digest[:12]} is no recorded version")


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
    # The prior record is read and its ref checked before the upload, so a
    # refused re-version leaves no unrecorded remote version behind.
    path = DATASETS / f"{args.slug}.json"
    previous = dict(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else None
    require(
        previous is None or previous["ref"] == ref,
        f"dataset record {path.name} holds {previous and previous['ref']}, not {ref}",
    )
    with tempfile.TemporaryDirectory() as scratch:
        staging = Path(scratch)
        with tarfile.open(staging / ARCHIVE, "w:gz") as archive:
            for member in files:
                archive.add(member, arcname=member.relative_to(ROOT).as_posix(), recursive=False)
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
    path.write_text(json.dumps(with_history(record, previous), indent=1) + "\n", encoding="utf-8")
    print(f"{ref}: {len(manifest)} files, archive {archive_sha256[:12]}")
    return 0


def artifact_record(path: Path, expected_sha256: str, ref: str) -> dict[str, Any]:
    """The kaggle-artifact-v1 fields of one file, refused when its bytes differ from the expected digest."""
    require(path.is_file(), f"{path} is not a file")
    digest = sha256(path.read_bytes())
    require(digest == expected_sha256.lower(), f"{path.name} has sha256 {digest}, not {expected_sha256}")
    return {"schema": ARTIFACT_SCHEMA, "ref": ref, "file": path.name, "sha256": digest, "size": path.stat().st_size}


def artifact(args: argparse.Namespace) -> int:
    """Upload one file, verified against --sha256, as a private Kaggle dataset that holds nothing else.

    The file travels outside git (a built wheel); its record names the bytes
    a push may attach, and a kernel reads the file under /kaggle/input
    instead of unpacking it into the repository.
    """
    import shutil
    import tempfile

    # The bytes are checked before any Kaggle call.
    fields = artifact_record(Path(args.file).resolve(), args.sha256, "")
    ref = f"{username()}/{args.slug}"
    fields["ref"] = ref
    path = DATASETS / f"{args.slug}.json"
    previous = dict(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else None
    require(
        previous is None or (previous["ref"] == ref and previous.get("schema") == ARTIFACT_SCHEMA),
        f"dataset record {path.name} holds {previous and previous['ref']} ({previous and previous.get('schema')}), "
        f"not the artifact {ref}",
    )
    with tempfile.TemporaryDirectory() as scratch:
        staging = Path(scratch)
        shutil.copyfile(args.file, staging / fields["file"])
        require(sha256((staging / fields["file"]).read_bytes()) == fields["sha256"], "the staged copy differs")
        metadata = {"title": args.slug, "id": ref, "licenses": [{"name": "unknown"}]}
        (staging / "dataset-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
        exists = subprocess.run(["kaggle", "datasets", "status", ref], capture_output=True, text=True).returncode == 0
        message = f"{fields['file']} {fields['sha256'][:12]}"
        if exists:
            reply = kaggle("datasets", "version", "-p", str(staging), "-m", message, "-r", "skip")
        else:
            reply = kaggle("datasets", "create", "-p", str(staging), "-r", "skip")
    record = {**fields, "git_commit": git_commit(), "reply": reply.strip()[-300:]}
    DATASETS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(with_history(record, previous), indent=1) + "\n", encoding="utf-8")
    print(f"{ref}: {fields['file']} {fields['size']} bytes, sha256 {fields['sha256'][:12]}")
    return 0


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


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


def download_version(owner: str, slug: str, version: int, target: Path) -> list[str]:
    """Every output file and the log of one kernel version, laid out as `kaggle kernels output` lays them out.

    The Kaggle CLI parses OWNER/SLUG/N and then sends no version, so it
    returns the slug's latest version whatever N says; kagglesdk's
    ListKernelSessionOutput takes the version as version_label "vN".
    """
    import urllib.request

    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

    api = KaggleApi()
    api.authenticate()
    written: list[str] = []
    token: str | None = None
    log: str | None = None
    with api.build_kaggle_client() as client:
        while True:
            request = ApiListKernelSessionOutputRequest()
            request.user_name = owner
            request.kernel_slug = slug
            request.version_label = f"v{version}"
            request.page_size = 50
            if token:
                request.page_token = token
            response = client.kernels.kernels_api_client.list_kernel_session_output(request)
            for item in response.files or []:
                path = target / item.file_name
                require(
                    path.resolve().is_relative_to(target.resolve()), f"output path {item.file_name} escapes {target}"
                )
                path.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(item.url, timeout=300) as download:
                    path.write_bytes(download.read())
                written.append(item.file_name)
            log = log or response.log
            token = response.next_page_token
            if not token:
                break
    if log:
        (target / f"{slug}.log").write_text(log, encoding="utf-8")
        written.append(f"{slug}.log")
    return written


CAPTURE_SCHEMA = "kaggle-aer-collect-v2"


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


RECEIPT_STAGING = ".collect.json.tmp"


def _publish_new(path: Path, record: dict[str, Any]) -> None:
    """Publish RECORD at PATH whole or not at all, and never over an existing receipt.

    The bytes reach disk in a staging file first; link(2) then creates PATH
    atomically and fails when PATH exists, so a killed writer leaves at most
    a staging file, which recovery removes.
    """
    staging = path.parent / RECEIPT_STAGING
    with staging.open("xb") as handle:
        handle.write((json.dumps(record, indent=1) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    os.link(staging, path)
    staging.unlink()
    _fsync_dir(path.parent)


def _manifest(out: Path) -> dict[str, str]:
    return {p.relative_to(out).as_posix(): sha256(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}


def receipt_chain(run_dir: Path) -> list[Path]:
    """Every receipt of RUN_DIR in write order.

    A v1 collect.json predates captures and comes first; every v2 receipt,
    the primary collect.json included, carries its capture id, a UTC stamp
    that sorts in write order.
    """
    primary = run_dir / "collect.json"
    legacy: list[Path] = []
    stamped: list[tuple[str, Path]] = []
    candidates = sorted((run_dir / "captures").glob("*/collect.json")) + ([primary] if primary.is_file() else [])
    for path in candidates:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["schema"] == CAPTURE_SCHEMA:
            stamped.append((record["capture"], path))
        else:
            legacy.append(path)
    return legacy + [path for _, path in sorted(stamped)]


def _new_capture(run_dir: Path) -> tuple[str, Path]:
    """A capture id later than every receipt of RUN_DIR and its directory, created exclusively."""
    chain = receipt_chain(run_dir)
    last = json.loads(chain[-1].read_text(encoding="utf-8")).get("capture", "") if chain else ""
    while True:
        capture_id = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S.%fZ")
        if capture_id > last:
            break
    directory = run_dir / "captures" / capture_id
    directory.parent.mkdir(exist_ok=True)
    directory.mkdir()
    return capture_id, directory


def _capture_record(run_dir: Path, capture_id: str, kernel: str, state: str, out: Path) -> dict[str, Any]:
    chain = receipt_chain(run_dir)
    return {
        "schema": CAPTURE_SCHEMA,
        "kernel": kernel,
        "capture": capture_id,
        "state": state,
        "collected_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ"),
        "submission_sha256": sha256((run_dir / "submission.json").read_bytes()),
        "predecessor_sha256": sha256(chain[-1].read_bytes()) if chain else None,
        "files": _manifest(out),
    }


def _preserve_unreceipted(run_dir: Path, kernel: str) -> None:
    """Give every tree no receipt describes its own capture with an UNRECEIPTED receipt.

    Such a tree is an output/ refused before captures existed, an output/
    promoted by an attempt killed before it wrote collect.json, or a capture
    killed before it wrote its receipt. The tree moves to a new capture id,
    so the chain stays in write order. A tree or capture directory holding
    no file carries no bytes and is removed, as is a staging receipt that a
    killed _publish_new left unlinked.
    """
    import shutil

    for staging in [run_dir / RECEIPT_STAGING, *sorted((run_dir / "captures").glob(f"*/{RECEIPT_STAGING}"))]:
        staging.unlink(missing_ok=True)
    sources = [d / "output" for d in sorted((run_dir / "captures").glob("*")) if not (d / "collect.json").exists()]
    if not (run_dir / "collect.json").exists():
        sources.append(run_dir / "output")
    for out in sources:
        if out.exists() and any(p.is_file() for p in out.rglob("*")):
            capture_id, directory = _new_capture(run_dir)
            os.rename(out, directory / "output")
            _fsync_dir(out.parent)
            _fsync_dir(directory)
            record = _capture_record(run_dir, capture_id, kernel, "UNRECEIPTED", directory / "output")
            _publish_new(directory / "collect.json", record)
        elif out.exists():
            shutil.rmtree(out)
        if out.parent != run_dir and out.parent.exists():
            require(
                not any(p.is_file() for p in out.parent.rglob("*")),
                f"{out.parent} holds files outside output/ and no receipt",
            )
            shutil.rmtree(out.parent)


def collect(args: argparse.Namespace) -> int:
    """Download the run's own kernel version into a new capture and record the sha256 of every returned file.

    `kernels status` reports the slug's latest version whatever version it
    names, so a later push would hide this run's state. The versioned output
    carries kaggle_kernel/kernel_main.py's exit.json, written on every exit
    path, and that file alone decides completion. No attempt rewrites or
    removes an earlier one: the first capture carrying exit.json is promoted
    by rename to RUN_DIR/output with RUN_DIR/collect.json, and every other
    capture keeps its bytes and receipt under RUN_DIR/captures/<id>/. Each
    receipt binds submission.json and its predecessor receipt by sha256. An
    exclusive lock on RUN_DIR serializes concurrent collections of one run.
    """
    import fcntl
    import shutil

    run_dir = Path(args.run_dir).resolve()
    submission = submission_of(run_dir)
    require("kernel_version" in submission, f"{run_dir} records no kernel version to collect")
    versioned = kernel_ref(submission)
    reported = kaggle("kernels", "status", versioned).strip()
    lock = os.open(run_dir, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _preserve_unreceipted(run_dir, versioned)
        capture_id, directory = _new_capture(run_dir)
        out = directory / "output"
        out.mkdir()
        owner, slug = submission["kernel"].split("/")
        try:
            download_version(owner, slug, int(submission["kernel_version"]), out)
        except BaseException as reason:
            record = _capture_record(run_dir, capture_id, versioned, "FAILED", out)
            record["error"] = f"{type(reason).__name__}: {reason}"
            _publish_new(directory / "collect.json", record)
            raise
        discarded: dict[str, str] = {}
        for stray in sorted(out.iterdir()):
            # Kaggle returns all of /kaggle/working: the kernel's results in
            # output/, its log beside it, and the repository bundle the push
            # uploaded. The receipt keeps each discarded file's digest.
            if stray.is_dir() and stray.name != "output":
                discarded |= {f"{stray.name}/{rel}": digest for rel, digest in _manifest(stray).items()}
                shutil.rmtree(stray)
        exit_file = out / "output" / "exit.json"
        if exit_file.is_file():
            returncode = json.loads(exit_file.read_text(encoding="utf-8"))["returncode"]
            state = "COMPLETE" if returncode == 0 else "ERROR"
        else:
            state = "PARTIAL"
        record = _capture_record(run_dir, capture_id, versioned, state, out)
        record["reported_status"] = reported
        record["discarded"] = discarded
        primary = run_dir / "collect.json"
        if state != "PARTIAL" and not primary.exists() and not (run_dir / "output").exists():
            os.rename(out, run_dir / "output")
            _fsync_dir(run_dir)
            _publish_new(primary, record)
            directory.rmdir()
            if not any(directory.parent.iterdir()):
                directory.parent.rmdir()
            _fsync_dir(run_dir)
            receipt = primary
        else:
            receipt = directory / "collect.json"
            _publish_new(receipt, record)
    finally:
        os.close(lock)
    # The reported status names the slug's latest version, so it cannot stand
    # in for a missing exit.json: such a version is unfinished or died before
    # kernel_main ran, and its capture keeps what it returned.
    require(
        state != "PARTIAL",
        f"{versioned} returned no exit.json (status of the latest version: {reported}); "
        f"{receipt.relative_to(ROOT)} records what it returned",
    )
    print(json.dumps(record, indent=1))
    return 0


def _verify_tree(name: str, record: dict[str, Any], out: Path) -> None:
    present = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    require(present == set(record["files"]), f"{name}: output files differ from its receipt")
    for rel, digest in record["files"].items():
        require(sha256((out / rel).read_bytes()) == digest, f"{name}: {rel} differs from its sha256")


def verify(args: argparse.Namespace) -> int:
    """Every retained receipt names exactly the files under its output/ with their sha256.

    A versioned run's primary collect.json must include the exit.json
    collection required; an earlier, unversioned run keeps the status Kaggle
    reported then. Each v2 receipt binds the run's submission.json and the
    receipt written before it, so the chain of a run holds every attempt.
    """
    runs = sorted(RESULTS.glob("*/collect.json"))
    captured = 0
    for path in runs:
        run_dir = path.parent
        record = json.loads(path.read_text(encoding="utf-8"))
        _verify_tree(run_dir.name, record, run_dir / "output")
        submission = submission_of(run_dir)
        require(record["kernel"] == kernel_ref(submission), f"{run_dir.name}: kernel differs")
        # Runs pushed before push recorded kernel versions also predate
        # exit.json and keep the status Kaggle reported; every versioned run
        # was collected on its exit.json.
        require(
            "kernel_version" not in submission or "output/exit.json" in record["files"],
            f"{run_dir.name}: a versioned run's ledger lacks output/exit.json",
        )
        for ref, digest in submission.get("datasets", {}).items():
            require_dataset_version(run_dir.name, ref, digest, dataset_record(ref.split("/")[1]))
    for captures in sorted(RESULTS.glob("*/captures")):
        run_dir = captures.parent
        submission = submission_of(run_dir)
        for directory in sorted(captures.iterdir()):
            name = f"{run_dir.name}/captures/{directory.name}"
            require((directory / "collect.json").is_file(), f"{name} has no receipt")
            record = json.loads((directory / "collect.json").read_text(encoding="utf-8"))
            require(record["capture"] == directory.name, f"{name}: receipt names capture {record['capture']}")
            require(record["kernel"] == kernel_ref(submission), f"{name}: kernel differs")
            if record["state"] in ("COMPLETE", "ERROR"):
                require("output/exit.json" in record["files"], f"{name}: a {record['state']} capture lacks exit.json")
            _verify_tree(name, record, directory / "output")
            captured += 1
    for run_dir in sorted({p.parent for p in runs} | {c.parent for c in RESULTS.glob("*/captures")}):
        submission_digest = sha256((run_dir / "submission.json").read_bytes())
        previous: str | None = None
        for path in receipt_chain(run_dir):
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["schema"] == CAPTURE_SCHEMA:
                name = path.relative_to(RESULTS).as_posix()
                require(record["submission_sha256"] == submission_digest, f"{name}: submission.json differs")
                require(
                    record["predecessor_sha256"] == previous, f"{name}: predecessor differs from the receipt before it"
                )
            previous = sha256(path.read_bytes())
    require(bool(runs), f"no collect.json under {RESULTS.relative_to(ROOT)}")
    print(
        f"kaggle runs: {len(runs)} collected outputs and {captured} further captures match their sha256 ledgers, "
        "receipt chains and recorded dataset versions"
    )
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
    push_parser.add_argument(
        "--ci-env",
        action="store_true",
        help="run ENTRY under CI's Python and pins (CPU Aer on a CPU or GPU machine) for a CI-replayed record",
    )
    push_parser.add_argument(
        "--gpu-env",
        action="store_true",
        help="run ENTRY in a venv of the repository's pins with GPU Aer; the kernel stops unless Aer reaches the GPU",
    )
    push_parser.add_argument(
        "--gpu-env-with",
        dest="gpu_env_with",
        action="append",
        default=[],
        choices=sorted(GPU_ENV_GROUPS),
        help="with --gpu-env, a pin group the venv adds at the host's versions",
    )
    push_parser.add_argument(
        "--gpu-aer",
        dest="gpu_aer",
        choices=sorted(GPU_AER_PINS),
        help="with --gpu-env, the GPU Aer build (default cu11); cu13 attaches its wheel dataset",
    )
    push_parser.set_defaults(func=push)
    sub.add_parser("self-test").set_defaults(func=self_test)
    dataset_parser = sub.add_parser("dataset")
    dataset_parser.add_argument("--slug", required=True)
    dataset_parser.add_argument("--include", action="append", required=True, help="repository file or directory")
    dataset_parser.set_defaults(func=dataset)
    artifact_parser = sub.add_parser("artifact")
    artifact_parser.add_argument("--slug", required=True)
    artifact_parser.add_argument("--file", required=True, help="the one file the dataset holds")
    artifact_parser.add_argument("--sha256", required=True, help="the file's expected sha256")
    artifact_parser.set_defaults(func=artifact)
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
