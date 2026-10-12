"""Exercise evidence rejection under normal and optimized Python interpreters."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CASES: tuple[tuple[str, str | None], ...] = (
    ("valid", None),
    ("corrupt_readme", "retained digest: README.md"),
    ("wrong_retained_length", "retained length: README.md"),
    ("wrong_source_digest", "source digest: cpu_branching_inputs.qpy.gz"),
    ("wrong_source_length", "source length: cpu_branching_inputs.qpy.gz"),
    ("missing_retained_digest", "KeyError: 'sha256'"),
    ("duplicate_manifest_path", "duplicate manifest path"),
    ("missing_noiseless_contract", "KeyError: 'noiseless_oracle_check'"),
    ("false_summary_state", "summary state differs from qualification"),
    ("false_numerical_radius", "full-family simultaneous radius disagrees with recomputation"),
)
MODES: tuple[tuple[str, tuple[str, ...], str | None], ...] = (
    ("normal", (), None),
    ("optimized", ("-O",), None),
    ("double_optimized", ("-OO",), None),
    ("environment_optimized", (), "1"),
)


def _hashes(bundle: Path) -> dict[str, str]:
    return {
        path.relative_to(bundle).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in bundle.rglob("*")
        if path.is_file()
    }


def _rebind_mutated_payload(bundle: Path, filename: str) -> None:
    """Permit numerical and contract mutations to reach checks beyond the digest."""
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    (entry,) = [row for row in manifest["files"] if row["path"] == filename]
    payload = (bundle / filename).read_bytes()
    entry["sha256"] = hashlib.sha256(payload).hexdigest()
    entry["bytes"] = len(payload)
    if filename.endswith(".gz"):
        raw = gzip.decompress(payload)
        entry["source_sha256"] = hashlib.sha256(raw).hexdigest()
        entry["source_bytes"] = len(raw)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def _mutate(bundle: Path, name: str) -> None:
    if name == "valid":
        return
    if name == "corrupt_readme":
        readme = bundle / "README.md"
        readme.write_bytes(readme.read_bytes() + b"\ncorruption\n")
        return
    if name in {
        "wrong_retained_length",
        "wrong_source_digest",
        "wrong_source_length",
        "missing_retained_digest",
        "duplicate_manifest_path",
    }:
        manifest_path = bundle / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        filename = "cpu_branching_inputs.qpy.gz" if name.startswith("wrong_source") else "README.md"
        (entry,) = [row for row in manifest["files"] if row["path"] == filename]
        if name == "wrong_retained_length":
            entry["bytes"] += 1
        elif name == "wrong_source_digest":
            entry["source_sha256"] = "0" * 64
        elif name == "wrong_source_length":
            entry["source_bytes"] += 1
        elif name == "missing_retained_digest":
            del entry["sha256"]
        else:
            manifest["files"].append(dict(entry))
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return
    if name == "false_summary_state":
        filename = "summary.json"
        document = json.loads((bundle / filename).read_text())
        document["state"] = "completed"
        (bundle / filename).write_text(json.dumps(document) + "\n")
    else:
        if name == "missing_noiseless_contract":
            filename = "cpu_branching_qualification.json.gz"
            document = json.loads(gzip.decompress((bundle / filename).read_bytes()))
            del document["noiseless_oracle_check"]
        elif name == "false_numerical_radius":
            filename = "cpu_branching_reuse_analysis.json.gz"
            document = json.loads(gzip.decompress((bundle / filename).read_bytes()))
            document["comparisons"][0]["simultaneous_radius"] += 0.5
        else:
            raise ValueError(f"unknown evidence mutation: {name}")
        (bundle / filename).write_bytes(gzip.compress(json.dumps(document).encode(), mtime=0))
    _rebind_mutated_payload(bundle, filename)


def check(bundle: Path) -> None:
    originals = _hashes(bundle)
    with tempfile.TemporaryDirectory(prefix="evidence-optimization-check-") as directory:
        root = Path(directory)
        for name, expected_error in CASES:
            fixture = root / name
            shutil.copytree(bundle, fixture)
            _mutate(fixture, name)
            fixture_before = _hashes(fixture)
            for mode, flags, optimization in MODES:
                environment = os.environ.copy()
                environment.pop("PYTHONOPTIMIZE", None)
                environment["PYTHONWARNINGS"] = "error"
                if optimization is not None:
                    environment["PYTHONOPTIMIZE"] = optimization
                result = subprocess.run(
                    [sys.executable, "-B", *flags, str(fixture / "verify_evidence.py")],
                    capture_output=True,
                    text=True,
                    env=environment,
                    check=False,
                )
                if expected_error is None:
                    if result.returncode != 0 or "pass verification" not in result.stdout:
                        raise RuntimeError(f"{name}/{mode}: valid evidence fails: {result.stderr}")
                elif (
                    result.returncode == 0
                    or expected_error not in result.stderr
                    or "pass verification" in result.stdout
                ):
                    raise RuntimeError(f"{name}/{mode}: rejection fails: {result.stdout} {result.stderr}")
                if _hashes(fixture) != fixture_before:
                    raise RuntimeError(f"{name}/{mode}: verification changes fixture evidence")
    if _hashes(bundle) != originals:
        raise RuntimeError("verification checks change retained evidence")
    print(
        f"Evidence verification: {len(CASES) * len(MODES)} normal/optimized cases pass; "
        f"{len(originals)} retained files and every fixture retain identical bytes"
    )


if __name__ == "__main__":
    check(Path(__file__).resolve().parent)
