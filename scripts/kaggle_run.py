"""Run a repository simulation, or a CI shard, as a private Kaggle kernel and retain its output.

Simulations of 14 qubits or fewer run on Kaggle; IBM hardware serves 15 or
more qubits or a question about the device itself. A kernel runs on a CPU
machine unless ``--machine`` names an accelerator, which a case requests when
its widest density matrix reaches local_compute.GPU_MIN_ACTIVE_QUBITS: below
that width a GPU spends its per-call overhead on states the CPU evolves
faster, and the weekly GPU quota goes to the runs that need it. This script is
the only path from the repository to Kaggle:

- ``push ENTRY --slug SLUG [-- ARGS]`` (ARGS after ``--`` go to ENTRY) resolves ENTRY's repository imports
  (``import X`` and ``from X import`` naming a module under gororoba_quantum/
  or scripts/, transitively), bundles them with any ``--include`` file, or
  every tracked file of an ``--include`` directory, as a zip embedded in a
  generated ``run.py``, writes kernel-metadata.json
  (private, internet for the pinned pip install) and pushes the kernel.
  Every bundle also carries KERNEL_FILES. The kernel installs KERNEL_PINS,
  unpacks the bundle and runs kaggle_kernel/kernel_main.py, which records
  the measured substrate, builds the hypercomplex package stack and proves it
  against the retained tables, then runs ENTRY with GOROROBA_AER_DEVICE set
  to the machine's device and returns every file the entry created or
  changed under the repository root.
- ``shards [--tier pr] [--count 6] [--only I,J]`` pushes one CPU kernel per
  CI shard for the committed HEAD. The kernel fetches HEAD from the public
  repository when it is on origin, and otherwise the merge base with
  origin/main plus the bundled files changed since then with their modes and
  deletions; it requires git write-tree to equal HEAD's tree, installs CI's
  Python and pins (ci/install_pins.sh), and runs ci/run_gates.py on that
  shard. Shard runs live under the ignored
  .kaggle-shards/ and are iteration records, never evidence;
  ``shards-report RUN_DIR...`` prints each collected shard's summary and
  failures.
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
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results/kaggle"
MODULE_DIRS = ("gororoba_quantum", "scripts")
KERNEL_PINS = ("qiskit==2.5.2", "qiskit-aer-gpu-cu11==0.17.2")
CPU_KERNEL_PINS = ("qiskit==2.5.2", "qiskit-aer==0.17.2")
DEFAULT_MACHINE = "cpu"
GPU_MACHINE = "NvidiaTeslaT4"
SHARDS = ROOT / ".kaggle-shards"
REMOTE = "https://github.com/Oichkatzelesfrettschen/gororoba-quantum.git"
# CI's interpreter (.github/workflows/ci.yml), the uv that installs it on the
# kernel, and the shellcheck the shellcheck gates call when the image lacks one.
CI_PYTHON = "3.14.7"
UV_PIN = "uv==0.13.0"
SHELLCHECK_PIN = "shellcheck-py==0.10.0.1"
SLOT_POLL_SECONDS = 90
# Kaggle's SaveKernel accepts a 706,414-byte run.py and refuses a 1,662,849-byte
# one with HTTP 400 (2026-10-16); the guard sits between the two.
KERNEL_SOURCE_LIMIT = 1_000_000
# Six shards outnumber the five CPU sessions, so a default run waits for the
# first shards to finish (a pr shard takes about 5 to 10 minutes there).
SLOT_WAIT_SECONDS = 7200
CI_SHARDS = {"pr": 6, "full": 12}
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


def kernel_pins(machine: str) -> tuple[str, ...]:
    return CPU_KERNEL_PINS if machine == "cpu" else KERNEL_PINS


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
        device = "CPU" if args.machine == "cpu" else "GPU"
        datasets = [dataset_record(slug) for slug in getattr(args, "dataset", [])]
        job = {
            "entry": entry_rel,
            "args": list(args.args),
            "smoke": smoke,
            "device": device,
            "datasets": [{"ref": d["ref"], "archive": d["archive"], "files": d["files"]} for d in datasets],
        }
        bundle.writestr("kaggle_kernel/kernel_job.json", json.dumps(job, indent=1) + "\n")
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    runner = RUNNER.format(
        pins=list(kernel_pins(args.machine)), bundle=base64.b64encode(buffer.getvalue()).decode("ascii")
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
        "enable_gpu": args.machine != "cpu" and not args.machine.startswith("Tpu"),
        "enable_tpu": args.machine.startswith("Tpu"),
        "enable_internet": True,
    }
    if args.machine != "cpu":
        metadata["machine_shape"] = args.machine
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
        "bundle": digests,
        "datasets": {d["ref"]: d["archive_sha256"] for d in datasets},
        "run_py_sha256": sha256((kernel_dir / "run.py").read_bytes()),
        "pushed_utc": stamp,
    }
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    return submission


def push(args: argparse.Namespace) -> int:
    # The smoke probe measures the widest circuits a GPU runs; on a CPU
    # machine it would record only that no GPU is attached.
    if args.smoke and args.machine == "cpu":
        args.machine = GPU_MACHINE
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
    """Build the Design C kernel (CPU and GPU) and a shard kernel offline, and check bundles, metadata and code."""
    import py_compile
    import tempfile

    entry = "scripts/design_c_cubic_noise.py"
    data = "docs/evidence/calibration/ibm_kingston.json"
    for machine in (DEFAULT_MACHINE, GPU_MACHINE):
        submission = _self_test_kernel(entry, data, machine)
    with tempfile.TemporaryDirectory() as scratch:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        shard = build_shard_kernel(
            Path(scratch) / "shard", "owner", "2000-01-01T000000Z", head.stdout.strip(), head.stdout.strip(), "pr", 2, 6
        )
        job = bundled_job(Path(scratch) / "shard/kernel/run.py")
        require(job["mode"] == "shards" and job["shard"] == 2 and job["count"] == 6, f"shard job {job}")
        require(job["modes"] == {} and job["deleted"] == [], "HEAD against itself carries an overlay")
        require(shard["tree"] == job["tree"] and job["python"] == CI_PYTHON, "shard job lacks the tree or CI's Python")
        py_compile.compile(str(Path(scratch) / "shard/kernel/run.py"), doraise=True)
    _overlay_self_test()
    print(
        f"kaggle_run self-test: {len(submission['bundle'])} bundled files, private CPU and GPU kernels, "
        "a shard kernel bound to HEAD's tree, an overlay that rebuilds a directory-to-file change, run.py compiles"
    )
    return 0


def _overlay_self_test() -> None:
    """A commit that turns a directory into a file and adds a symlink: the kernel's overlay rebuilds its tree."""
    import os
    import tempfile

    sys.path.insert(0, str(ROOT / "kaggle_kernel"))
    import kernel_main

    identity = ["-c", "user.name=self-test", "-c", "user.email=self-test@localhost"]
    with tempfile.TemporaryDirectory() as scratch:
        repo, overlay = Path(scratch) / "repo", Path(scratch) / "overlay"
        repo.mkdir()

        def run(*args: str) -> str:
            return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout

        run("init", "-q")
        (repo / "node").mkdir()
        (repo / "node/child").write_text("child", encoding="utf-8")
        (repo / "kept").write_text("kept", encoding="utf-8")
        run("add", "-A")
        run(*identity, "commit", "-qm", "base")
        base = run("rev-parse", "HEAD").strip()
        (repo / "node/child").unlink()
        (repo / "node").rmdir()
        (repo / "node").write_text("now a file", encoding="utf-8")
        os.symlink("kept", repo / "link")
        run("add", "-A")
        run(*identity, "commit", "-qm", "head")
        expected = run("rev-parse", "HEAD^{tree}").strip()
        changes = run("diff", "--no-renames", "--name-status", "-z", base, "HEAD").split("\0")
        modes: dict[str, str] = {}
        deleted: list[str] = []
        for code, rel in zip(changes[0:-1:2], changes[1::2], strict=True):
            if code == "D":
                deleted.append(rel)
                continue
            mode, _, blob = run("ls-tree", "HEAD", "--", rel).split()[:3]
            data = subprocess.run(["git", "cat-file", "blob", blob], cwd=repo, check=True, capture_output=True).stdout
            (overlay / rel).parent.mkdir(parents=True, exist_ok=True)
            (overlay / rel).write_bytes(data)
            modes[rel] = mode
        run("checkout", "-q", base)
        kernel_main.apply_overlay(repo, overlay, modes, deleted)
        run("add", "-A")
        require(run("write-tree").strip() == expected, "the overlay does not rebuild a directory-to-file change")


def bundled_job(run_py: Path) -> dict[str, Any]:
    """The kernel_job.json inside a generated run.py's embedded bundle."""
    found = re.search(r'BUNDLE = "([^"]+)"', run_py.read_text(encoding="utf-8"))
    require(found is not None, f"{run_py} embeds no bundle")
    assert found is not None
    archive = zipfile.ZipFile(io.BytesIO(base64.b64decode(found.group(1))))
    return dict(json.loads(archive.read("kaggle_kernel/kernel_job.json")))


def _self_test_kernel(entry: str, data: str, machine: str) -> dict[str, Any]:
    import py_compile
    import tempfile

    build_args = argparse.Namespace(
        entry=entry, smoke=False, include=[data], args=["--pairs", "1,16"], slug="self-test", machine=machine
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
        gpu = machine != "cpu"
        require(
            metadata["is_private"] is True and metadata["enable_gpu"] is gpu, f"{machine}: kernel metadata {metadata}"
        )
        require(("machine_shape" in metadata) is gpu, f"{machine}: machine_shape {metadata.get('machine_shape')}")
        require(metadata["id"] == "owner/self-test", f"kernel id {metadata['id']}")
        py_compile.compile(str(run_dir / "kernel/run.py"), doraise=True)
        runner = (run_dir / "kernel/run.py").read_text(encoding="utf-8")
        require(all(pin in runner for pin in kernel_pins(machine)), f"{machine}: run.py lacks a pin")
        require(submission["untracked_inputs"] == [], f"untracked bundled inputs {submission['untracked_inputs']}")
    return submission


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


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def build_shard_kernel(
    run_dir: Path, owner: str, stamp: str, base: str, head: str, tier: str, shard: int, count: int, machine: str = "cpu"
) -> dict[str, Any]:
    """The kernel of one CI shard of head: KERNEL_FILES, and the files changed since base as an overlay."""
    changes = git("diff", "--no-renames", "--name-status", "-z", base, head).split("\0")
    modes: dict[str, str] = {}
    deleted: list[str] = []
    buffer = io.BytesIO()
    digests: dict[str, str] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for always in KERNEL_FILES:
            for path in import_closure(ROOT / always) if always.endswith(".py") else [ROOT / always]:
                rel = path.relative_to(ROOT).as_posix()
                data = path.read_bytes()
                digests[rel] = sha256(data)
                bundle.writestr(rel, data)
        for status_code, rel in zip(changes[0:-1:2], changes[1::2], strict=True):
            if status_code == "D":
                deleted.append(rel)
                continue
            mode, _, blob = git("ls-tree", head, "--", rel).split(maxsplit=3)[:3]
            data = subprocess.run(["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True, check=True).stdout
            modes[rel] = mode
            digests[f"overlay/{rel}"] = sha256(data)
            bundle.writestr(f"kaggle_kernel/overlay/{rel}", data)
        job = {
            "mode": "shards",
            "remote": REMOTE,
            "base": base,
            "head": head,
            "tree": git("rev-parse", f"{head}^{{tree}}").strip(),
            "modes": modes,
            "deleted": deleted,
            "tier": tier,
            "shard": shard,
            "count": count,
            "python": CI_PYTHON,
            "uv": UV_PIN,
            "shellcheck": SHELLCHECK_PIN,
            "entry": None,
            "args": [],
            "smoke": False,
            "device": "CPU",
            "datasets": [],
        }
        bundle.writestr("kaggle_kernel/kernel_job.json", json.dumps(job, indent=1) + "\n")
    kernel_dir = run_dir / "kernel"
    kernel_dir.mkdir(parents=True)
    pins = kernel_pins(machine)
    runner = RUNNER.format(pins=list(pins), bundle=base64.b64encode(buffer.getvalue()).decode("ascii"))
    (kernel_dir / "run.py").write_text(runner, encoding="utf-8")
    slug = f"gororoba-ci-shard-{shard}-of-{count}"
    metadata = {
        "id": f"{owner}/{slug}",
        "title": slug,
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": machine != "cpu" and not machine.startswith("Tpu"),
        "enable_tpu": machine.startswith("Tpu"),
        "enable_internet": True,
    }
    if machine != "cpu":
        metadata["machine_shape"] = machine
    (kernel_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=1) + "\n", encoding="utf-8")
    submission = {
        "schema": "kaggle-ci-shard-v1",
        "kernel": metadata["id"],
        "machine_shape": machine,
        "base": base,
        "head": head,
        "tree": job["tree"],
        "tier": tier,
        "shard": shard,
        "count": count,
        "overlay_files": len(modes),
        "deleted_files": len(deleted),
        "pins": list(pins),
        "bundle": digests,
        "run_py_sha256": sha256((kernel_dir / "run.py").read_bytes()),
        "pushed_utc": stamp,
    }
    (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
    return submission


def push_shard(run_dir: Path, machine: str, timeout: int) -> tuple[bool, str]:
    """Push a built shard kernel; (pushed, reply). A full session pool refuses with "session count"."""
    push_args = ["kernels", "push", "-p", str(run_dir / "kernel")]
    if machine != "cpu":
        push_args += ["--accelerator", machine]
    if timeout:
        push_args += ["-t", str(timeout)]
    proc = subprocess.run(["kaggle", *push_args], capture_output=True, text=True)
    reply = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0 and "successfully pushed" in reply, reply


def shards(args: argparse.Namespace) -> int:
    """Push one kernel per CI shard of the committed HEAD on the first machine with a free session."""
    import shutil

    revision = git_commit()
    require(not revision.endswith("-dirty"), "shards test a commit: commit or stash the tracked changes first")
    git("fetch", "-q", "origin")
    # A commit already on origin is fetched as itself and carries no overlay;
    # an unpushed commit overlays its changes on the merge base with
    # origin/main, which has to fit Kaggle's script source limit.
    pushed = bool(git("branch", "-r", "--contains", revision).strip())
    base = revision if pushed else git("merge-base", "HEAD", "origin/main").strip()
    owner = username()
    # CI runs the pr tier on 6 shards and the full tier on 12
    # (.github/workflows/ci.yml); run_gates assigns gates by the count.
    args.count = args.count or CI_SHARDS[args.tier]
    only = [int(x) for x in args.only.split(",")] if args.only else list(range(args.count))
    require(all(0 <= i < args.count for i in only), f"--only {args.only} lies outside 0..{args.count - 1}")
    machines = args.machine.split(",")
    for shard in only:
        waited = 0
        while True:
            pushed = False
            for machine in machines:
                stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
                run_dir = SHARDS / f"{stamp}-{revision[:12]}-shard-{shard}-of-{args.count}"
                build_shard_kernel(run_dir, owner, stamp, base, revision, args.tier, shard, args.count, machine)
                size = (run_dir / "kernel/run.py").stat().st_size
                if size > KERNEL_SOURCE_LIMIT:
                    shutil.rmtree(run_dir)
                    raise SystemExit(
                        f"shard {shard}: the overlay makes run.py {size} bytes, above Kaggle's script limit "
                        f"(KERNEL_SOURCE_LIMIT {KERNEL_SOURCE_LIMIT}); push the branch so the kernel fetches HEAD"
                    )
                pushed, reply = push_shard(run_dir, machine, args.timeout)
                if pushed:
                    break
                shutil.rmtree(run_dir)
                # Each machine type has its own batch session pool (five CPU,
                # two GPU); a full pool refuses the push, and the next machine
                # in the preference list takes the shard.
                if "session count" not in reply:
                    raise SystemExit(f"kaggle refused shard {shard} on {machine}: {reply}")
            if pushed or waited >= args.slot_wait:
                break
            time.sleep(SLOT_POLL_SECONDS)
            waited += SLOT_POLL_SECONDS
        require(pushed, f"every machine in {machines} stayed full for {waited} s: {reply}")
        version = re.search(r"Kernel version (\d+) successfully pushed", reply)
        require(version is not None, f"push reply names no kernel version: {reply}")
        assert version is not None
        submission = submission_of(run_dir)
        submission["kernel_version"] = int(version.group(1))
        (run_dir / "submission.json").write_text(json.dumps(submission, indent=1) + "\n", encoding="utf-8")
        print(f"{run_dir} on {machine}", flush=True)
    return 0


def shards_report(args: argparse.Namespace) -> int:
    """Each collected shard's summary line and failing gates; nonzero when any shard failed or is missing."""
    bad = 0
    for name in args.run_dirs:
        run_dir = Path(name).resolve()
        out = run_dir / "output" / "output"
        submission = submission_of(run_dir)
        label = f"shard {submission['shard']}/{submission['count']} at {submission['head'][:12]}"
        result = out / "shard.json"
        if not result.is_file():
            exit_file = out / "exit.json"
            code = json.loads(exit_file.read_text())["returncode"] if exit_file.is_file() else "none"
            print(f"{label}: no gate result (kernel exit {code}); see {out}")
            bad += 1
            continue
        shard = json.loads(result.read_text(encoding="utf-8"))
        print(f"{label}: {' '.join(shard['summary'])} in {shard['seconds']} s")
        for line in (out / "gates.txt").read_text(encoding="utf-8").splitlines():
            if line.startswith("FAIL "):
                print(f"  {line[:160]}")
        bad += shard["returncode"] != 0
    return 1 if bad else 0


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
    push_parser.set_defaults(func=push)
    sub.add_parser("self-test").set_defaults(func=self_test)
    dataset_parser = sub.add_parser("dataset")
    dataset_parser.add_argument("--slug", required=True)
    dataset_parser.add_argument("--include", action="append", required=True, help="repository file or directory")
    dataset_parser.set_defaults(func=dataset)
    sub.add_parser("verify").set_defaults(func=verify)
    shards_parser = sub.add_parser("shards")
    shards_parser.add_argument("--tier", choices=("pr", "full"), default="pr")
    shards_parser.add_argument("--count", type=int, help="shard count (CI's: 6 for pr, 12 for full)")
    shards_parser.add_argument("--only", help="comma-separated shard indices (all by default)")
    shards_parser.add_argument("--timeout", type=int, default=0, help="kernel run-time limit in seconds")
    shards_parser.add_argument(
        "--machine",
        default=DEFAULT_MACHINE,
        help="machines in preference order, comma-separated (cpu, NvidiaTeslaT4, TpuV5E8); a full pool falls through",
    )
    shards_parser.add_argument(
        "--slot-wait",
        type=int,
        default=SLOT_WAIT_SECONDS,
        help="seconds to wait for a free session before giving up",
    )
    shards_parser.set_defaults(func=shards)
    report_parser = sub.add_parser("shards-report")
    report_parser.add_argument("run_dirs", nargs="+")
    report_parser.set_defaults(func=shards_report)
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
