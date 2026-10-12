"""Audit a retained run's declared experiment sources without rewriting its evidence.

The source closure comes from the retained commit. Broader directory dirt and
unmanifested Python files remain separate observations. Audit output supplies
provenance evidence and grants zero QPU submission authorization.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

AUDIT_CONTRACT = "declared-experiment-source-closure-v1"
RUNNER_PATH = Path("gororoba_quantum/live_run.py")
MANIFEST_NAME = "EXPERIMENT_SOURCE_MANIFEST"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git(repo: Path, *arguments: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", "-C", str(repo), *arguments], stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as error:
        raise ValueError("Git cannot read the requested source evidence") from error


def _manifest(source: bytes) -> tuple[str, ...]:
    tree = ast.parse(source)
    assignments = [
        statement
        for statement in tree.body
        if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == MANIFEST_NAME for target in statement.targets)
    ]
    if len(assignments) != 1:
        raise ValueError("committed runner must declare one literal experiment source manifest")
    manifest = ast.literal_eval(assignments[0].value)
    if not isinstance(manifest, tuple) or not manifest or any(not isinstance(name, str) for name in manifest):
        raise ValueError("experiment source manifest must be a nonempty tuple of filenames")
    if len(set(manifest)) != len(manifest):
        raise ValueError("experiment source manifest contains duplicate filenames")
    if any(Path(name).name != name or not re.fullmatch(r"[A-Za-z0-9_]+\.py", name) for name in manifest):
        raise ValueError("experiment source manifest must name sibling Python source files")
    if RUNNER_PATH.name not in manifest:
        raise ValueError("experiment source manifest must include its declaring runner")
    return tuple(manifest)


def _pins(requirements: bytes) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in requirements.decode().splitlines():
        content = line.split("#", 1)[0].strip()
        if not content:
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s;]+)", content)
        if match is None:
            raise ValueError("requirements must contain exact package==version pins")
        package, version = match.groups()
        if package in pins:
            raise ValueError("requirements contain a duplicate package pin")
        pins[package] = version
    if not pins:
        raise ValueError("requirements contain no dependency pins")
    return pins


def audit(
    repo: Path,
    record_path: Path,
    *,
    installed_version: Callable[[str], str] = importlib.metadata.version,
) -> dict[str, Any]:
    """Compare source bytes and versions while preserving the recorded dirt flag."""
    repo = repo.resolve()
    record_path = (record_path if record_path.is_absolute() else repo / record_path).resolve()
    try:
        relative_record = record_path.relative_to(repo)
    except ValueError as error:
        raise ValueError("the retained record must reside under the audited repository") from error
    record_bytes = record_path.read_bytes()
    record = json.loads(record_bytes)
    head = record["code_commit"]["head"]
    if not isinstance(head, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", head):
        raise ValueError("recorded commit identity is invalid")
    if type(record["code_commit"]["sources_modified"]) is not bool:
        raise ValueError("recorded sources_modified must be Boolean")
    if _git(repo, "cat-file", "-t", head).strip() != b"commit":
        raise ValueError("recorded Git object must be a commit")
    committed_runner = _git(repo, "show", f"{head}:{RUNNER_PATH.as_posix()}")
    manifest = _manifest(committed_runner)
    source_rows: list[dict[str, Any]] = []
    committed_digest = hashlib.sha256()
    for name in manifest:
        relative = RUNNER_PATH.parent / name
        current = (repo / relative).read_bytes()
        committed = _git(repo, "show", f"{head}:{relative.as_posix()}")
        source_rows.append(
            {
                "path": relative.as_posix(),
                "working_sha256": _sha256(current),
                "commit_sha256": _sha256(committed),
                "working_bytes": len(current),
                "commit_bytes": len(committed),
                "equal": current == committed,
            }
        )
        if current != committed:
            raise ValueError(f"declared source differs from recorded commit: {relative.as_posix()}")
        committed_digest.update(name.encode())
        committed_digest.update(committed)
    if committed_digest.hexdigest() != record["experiment_digest"]:
        raise ValueError("record experiment digest differs from its committed source closure")

    requirements = (repo / "requirements.txt").read_bytes()
    committed_requirements = _git(repo, "show", f"{head}:requirements.txt")
    if requirements != committed_requirements:
        raise ValueError("requirements differ from recorded commit")
    pins = _pins(requirements)
    recorded_versions = record["versions"]
    if not isinstance(recorded_versions, dict) or not recorded_versions:
        raise ValueError("recorded runtime versions must be a nonempty mapping")
    if set(recorded_versions) - set(pins):
        raise ValueError("a recorded dependency lacks a requirements pin")
    dependencies = []
    for package, pinned in sorted(pins.items()):
        installed = installed_version(package)
        recorded = recorded_versions.get(package)
        if installed != pinned or (package in recorded_versions and recorded != installed):
            raise ValueError(f"dependency version mismatch: {package}")
        dependencies.append(
            {
                "package": package,
                "pinned": pinned,
                "installed": installed,
                "recorded": recorded,
                "pin_matches_installed": True,
                "recorded_matches_installed": recorded == installed if package in recorded_versions else None,
            }
        )

    directory_status = _git(repo, "status", "--porcelain", "--", RUNNER_PATH.parent.as_posix()).decode().splitlines()
    unmanifested = sorted(
        path.relative_to(repo).as_posix()
        for path in (repo / RUNNER_PATH.parent).glob("*.py")
        if path.name not in manifest
    )
    # A second byte check detects source drift while the Git/version reads run.
    for row in source_rows:
        if _sha256((repo / row["path"]).read_bytes()) != row["working_sha256"]:
            raise ValueError("declared source changes during the audit")
    if (repo / "requirements.txt").read_bytes() != requirements or record_path.read_bytes() != record_bytes:
        raise ValueError("requirements or retained record changes during the audit")
    return {
        "audit_contract": AUDIT_CONTRACT,
        "scope": (
            "Declared experiment-source bytes, requirements pins, installed dependency metadata, and retained record. "
            "Broader directory dirt and unmanifested Python files remain separate. "
            "Source equality grants no QPU approval."
        ),
        "record": relative_record.as_posix(),
        "record_sha256": _sha256(record_bytes),
        "recorded_commit": head,
        "recorded_sources_modified": record["code_commit"]["sources_modified"],
        "recorded_experiment_digest": record["experiment_digest"],
        "computed_commit_closure_digest": committed_digest.hexdigest(),
        "source_file_count": len(source_rows),
        "source_files": source_rows,
        "requirements": {
            "working_sha256": _sha256(requirements),
            "commit_sha256": _sha256(committed_requirements),
            "equal": True,
        },
        "dependencies": dependencies,
        "audit_python_version": platform.python_version(),
        "observed_directory_status": directory_status,
        "unmanifested_python_files": unmanifested,
        "unmanifested_scope": "Closure exclusion alone assigns no safety or completion status.",
        "audit_script": Path(__file__).name,
        "audit_script_sha256": _sha256(Path(__file__).read_bytes()),
        "verdict": "declared_source_closure_and_dependency_versions_match",
        "record_bytes_unchanged": True,
    }


def write_report(destination: Path, report: dict[str, Any], record_path: Path) -> None:
    """Write a separate audit artifact and preserve every existing run artifact."""
    destination = destination.resolve()
    record_path = record_path.resolve()
    if destination.suffix != ".json":
        raise ValueError("audit output must have a .json suffix")
    if destination == record_path:
        raise ValueError("audit output must differ from the retained record")
    if destination.exists():
        try:
            existing = json.loads(destination.read_bytes())
        except (ValueError, UnicodeDecodeError) as error:
            raise ValueError("audit output refuses to replace an existing non-audit artifact") from error
        if not isinstance(existing, dict) or existing.get("audit_contract") != AUDIT_CONTRACT:
            raise ValueError("audit output refuses to replace an existing non-audit artifact")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent, delete=False) as stream:
            temporary_path = Path(stream.name)
            json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _verify() -> None:
    with tempfile.TemporaryDirectory(prefix="source-closure-check-") as directory:
        repo = Path(directory)
        source = repo / RUNNER_PATH.parent
        source.mkdir()
        runner = b'EXPERIMENT_SOURCE_MANIFEST = ("live_run.py", "model.py")\n'
        model = b"VALUE = 1\n"
        (source / "live_run.py").write_bytes(runner)
        (source / "model.py").write_bytes(model)
        (repo / "requirements.txt").write_text("numpy==2.5.4\n")
        _git(repo, "init", "--quiet")
        _git(repo, "add", "gororoba_quantum", "requirements.txt")
        _git(
            repo,
            "-c",
            "user.name=SourceAudit",
            "-c",
            "user.email=source-audit@example.invalid",
            "commit",
            "-qm",
            "fixture",
        )
        head = _git(repo, "rev-parse", "HEAD").decode().strip()
        digest = hashlib.sha256(b"live_run.py" + runner + b"model.py" + model).hexdigest()
        record_path = repo / "results" / "record.json"
        record_path.parent.mkdir()
        record = {
            "code_commit": {"head": head, "sources_modified": True},
            "experiment_digest": digest,
            "versions": {"numpy": "2.5.4"},
        }
        record_path.write_text(json.dumps(record))
        (source / "notes.md").write_text("uncommitted explanation\n")
        (source / "unqualified.py").write_text("VALUE = 2\n")

        def version(_package: str) -> str:
            return "2.5.4"

        report = audit(repo, record_path, installed_version=version)
        assert report["source_file_count"] == 2
        assert report["recorded_sources_modified"] is True
        assert report["observed_directory_status"]
        assert report["unmanifested_python_files"] == ["gororoba_quantum/unqualified.py"]
        before = record_path.read_bytes()
        output = record_path.parent / "source-closure.json"
        write_report(output, report, record_path)
        assert record_path.read_bytes() == before
        assert json.loads(output.read_bytes()) == report

        for path, mutation in (
            (source / "model.py", b"VALUE = 3\n"),
            (source / "live_run.py", b'EXPERIMENT_SOURCE_MANIFEST = ("live_run.py",)\n'),
            (repo / "requirements.txt", b"numpy==0.0.0\n"),
            (record_path, json.dumps(record | {"experiment_digest": "0" * 64}).encode()),
            (record_path, json.dumps(record | {"versions": {"numpy": "0.0.0"}}).encode()),
        ):
            original = path.read_bytes()
            path.write_bytes(mutation)
            try:
                audit(repo, record_path, installed_version=version)
            except ValueError:
                pass
            else:
                raise AssertionError(f"mutation passes source audit: {path.name}")
            finally:
                path.write_bytes(original)
        try:
            audit(repo, record_path, installed_version=lambda _package: "0.0.0")
        except ValueError:
            pass
        else:
            raise AssertionError("installed-version mutation passes source audit")
        try:
            write_report(record_path, report, record_path)
        except ValueError:
            pass
        else:
            raise AssertionError("audit output replaces the retained record")
        assert record_path.read_bytes() == before
    print(
        "Source closure: clean declared bytes, broader dirt, mutations, dependency pins, and output preservation pass"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.check:
        if any(value is not None for value in (arguments.repo, arguments.record, arguments.out)):
            parser.error("--check runs independently of repository/record/output arguments")
        _verify()
        return 0
    if arguments.repo is None or arguments.record is None:
        parser.error("--repo and --record are required")
    repo = arguments.repo.resolve()
    record_path = arguments.record if arguments.record.is_absolute() else repo / arguments.record
    destination = arguments.out if arguments.out is not None else record_path.parent / "source-closure.json"
    try:
        report = audit(repo, record_path)
        write_report(destination, report, record_path)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, importlib.metadata.PackageNotFoundError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"{report['verdict']}; files={report['source_file_count']}; "
        f"recorded_sources_modified={report['recorded_sources_modified']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
