"""Exercise ripple HTML path admission and byte-preserving check mode."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import render_ripple_visualization as renderer

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_RELATIVE = Path("gororoba_quantum/visualizations/cayley_dickson_ripples.html")
REJECTION = "output must differ from the evidence and template paths"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def snapshot(directory: Path) -> dict[str, tuple[object, ...]]:
    """Record fixture names, link targets, file identities, bytes, and mtimes."""
    contents: dict[str, tuple[object, ...]] = {}
    for path in (directory, *sorted(directory.rglob("*"))):
        name = path.relative_to(directory).as_posix()
        status = path.lstat()
        identity = (status.st_dev, status.st_ino, status.st_nlink, status.st_mtime_ns)
        if path.is_symlink():
            contents[name] = ("symlink", os.readlink(path), *identity)
        elif path.is_file():
            contents[name] = ("file", path.read_bytes(), *identity)
        else:
            contents[name] = ("directory", *identity)
    return contents


def invoke(script: Path, evidence: Path, output: Path, check: bool) -> subprocess.CompletedProcess[str]:
    optimization = [f"-{'O' * sys.flags.optimize}"] if sys.flags.optimize else []
    return subprocess.run(
        [
            sys.executable,
            *optimization,
            str(script),
            "--evidence",
            str(evidence),
            "--out",
            str(output),
            *(["--check"] if check else []),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def copied_renderer(directory: Path) -> Path:
    """Run the real entry point against copied inputs instead of repository files."""
    script = directory / "scripts/render_ripple_visualization.py"
    script.parent.mkdir(parents=True)
    script.write_bytes(Path(renderer.__file__).read_bytes())
    return script


def rejected_alias(directory: Path, protected: str, alias_kind: str) -> int:
    script = copied_renderer(directory)
    evidence = directory / "evidence/evidence.json"
    template = directory / TEMPLATE_RELATIVE
    inputs = {"evidence": evidence, "template": template}
    for name, path in inputs.items():
        if name == protected and alias_kind == "dangling_directory_symlink":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if name != protected or not alias_kind.startswith("dangling_"):
            # Invalid data proves that alias admission precedes input parsing.
            path.write_bytes(f"{name} must remain unread on rejected invocations\n".encode())
    target = inputs[protected]
    output = directory / "alias.html"
    if alias_kind == "direct":
        output = target
    elif alias_kind == "canonical":
        child = target.parent / "child"
        child.mkdir()
        output = child / ".." / target.name
    elif alias_kind in {"file_symlink", "dangling_file_symlink"}:
        output.symlink_to(target)
    elif alias_kind in {"directory_symlink", "dangling_directory_symlink"}:
        linked_directory = directory / "linked-directory"
        linked_directory.symlink_to(target.parent, target_is_directory=True)
        output = linked_directory / target.name
    elif alias_kind == "hardlink":
        output.hardlink_to(target)
    else:
        raise RuntimeError(f"unknown alias kind: {alias_kind}")
    before = snapshot(directory)
    for check in (False, True):
        process = invoke(script, evidence, output, check)
        require(
            process.returncode == 1 and REJECTION in process.stderr,
            f"{protected}/{alias_kind}/check={check}: alias reached input parsing or was accepted",
        )
        require(process.stdout == "", "rejected CLI wrote stdout")
        require(snapshot(directory) == before, f"{protected}/{alias_kind}: rejected CLI changed fixture")
    return 2


def checked_outcome(
    directory: Path, script: Path, evidence: Path, output: Path, error_fragment: str | None = None
) -> None:
    """Check the public CLI and preserve the complete fixture for each outcome."""
    before_check = snapshot(directory)
    process = invoke(script, evidence, output, True)
    if error_fragment is None:
        require(process.returncode == 0 and process.stderr == "", f"valid check failed: {process.stderr}")
    else:
        require(
            process.returncode == 1 and error_fragment in process.stderr,
            f"check failed to report {error_fragment!r}: {process.stderr}",
        )
    require(process.stdout == "", "check CLI wrote stdout")
    require(snapshot(directory) == before_check, "check changed fixture names, identities, bytes, or mtimes")


def accepted_output(directory: Path, evidence_bytes: bytes, template_bytes: bytes, retained_html: bytes) -> None:
    script = copied_renderer(directory)
    evidence = directory / "evidence.json"
    template = directory / TEMPLATE_RELATIVE
    template.parent.mkdir(parents=True)
    evidence.write_bytes(evidence_bytes)
    template.write_bytes(template_bytes)
    output = directory / "new-directory/explorer.html"
    checked_outcome(directory, script, evidence, output, os.strerror(errno.ENOENT))
    checked_outcome(directory, script, evidence, directory / "missing.html", os.strerror(errno.ENOENT))
    before_inputs = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (evidence, template)}
    process = invoke(script, evidence, output, False)
    require(process.returncode == 0 and process.stderr == "", f"valid renderer failed: {process.stderr}")
    require(output.read_bytes() == retained_html, "valid HTML differs from the retained artifact")
    for path, original in before_inputs.items():
        require((path.read_bytes(), path.stat().st_mtime_ns) == original, "valid write changed a renderer input")
    checked_outcome(directory, script, evidence, output)
    output.write_bytes(b"changed HTML\n")
    checked_outcome(directory, script, evidence, output, "HTML differs")
    checked_outcome(directory, script, evidence, output.parent, os.strerror(errno.EISDIR))

    evidence.unlink()
    checked_outcome(directory, script, evidence, output, os.strerror(errno.ENOENT))
    evidence.write_bytes(b"invalid JSON\n")
    checked_outcome(directory, script, evidence, output, "Expecting value")
    evidence.write_bytes(b"{}\n")
    checked_outcome(directory, script, evidence, output, "proposed_hardware_depths: expected 5 entries")
    evidence.write_bytes(evidence_bytes)
    template.unlink()
    checked_outcome(directory, script, evidence, output, os.strerror(errno.ENOENT))
    template.write_bytes(b"<html>missing evidence marker</html>\n")
    checked_outcome(directory, script, evidence, output, "exactly one evidence marker")


def main() -> int:
    evidence = ROOT / "results/ripple/evidence.json"
    artifact = ROOT / "results/ripple/cayley-dickson-ripples.html"
    retained = {path: path.read_bytes() for path in (evidence, renderer.TEMPLATE, artifact)}
    retained_mtimes = {path: path.stat().st_mtime_ns for path in retained}
    kinds = (
        "direct",
        "canonical",
        "file_symlink",
        "directory_symlink",
        "dangling_file_symlink",
        "dangling_directory_symlink",
        "hardlink",
    )
    rejected = 0
    with TemporaryDirectory(prefix="ripple-render-path-contract-") as temporary:
        directory = Path(temporary)
        for protected in ("evidence", "template"):
            for kind in kinds:
                rejected += rejected_alias(directory / f"{protected}-{kind}", protected, kind)
        accepted_output(directory / "valid", retained[evidence], retained[renderer.TEMPLATE], retained[artifact])
    require(
        all(path.read_bytes() == original for path, original in retained.items()), "repository artifact bytes changed"
    )
    require(
        all(path.stat().st_mtime_ns == original for path, original in retained_mtimes.items()),
        "repository artifact mtimes changed",
    )
    print(
        json.dumps(
            {
                "schema": "ripple-renderer-path-contracts-v1",
                "rejected_cli_aliases": rejected,
                "protected_inputs": ["evidence", "template"],
                "alias_kinds": list(kinds),
                "write_and_check_modes": True,
                "valid_html_matches_retained": True,
                "successful_and_failed_checks_preserve_fixture": True,
                "fixture_root_mtime_preserved": True,
                "retained_artifact_mtimes_preserved": True,
                "check_outcomes": [
                    "missing_output_parent",
                    "missing_output",
                    "matching_html",
                    "differing_html",
                    "output_is_directory",
                    "missing_evidence",
                    "invalid_evidence_json",
                    "invalid_evidence_shape",
                    "missing_template",
                    "invalid_template_marker",
                ],
                "retained_html_sha256": hashlib.sha256(retained[artifact]).hexdigest(),
                "retained_evidence_sha256": hashlib.sha256(retained[evidence]).hexdigest(),
                "retained_template_sha256": hashlib.sha256(retained[renderer.TEMPLATE]).hexdigest(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
