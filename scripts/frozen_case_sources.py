"""Verify that each frozen Quandela case keeps a pinned source revision on main's history.

A reviewed case binds the sha256 of every constructor and analyzer file it names in `analysis_sources` (a campaign
record binds them as `dependencies` rows), and
`qd_platform.acquisition_sources` refuses a plan or submit whose working tree differs from those bytes. Those files
are shared with every other Quandela experiment, so main moves past them. A pin names the revision whose tree holds
every bound byte; the case's check, plan, submit and analysis run in a worktree at that revision, and main's own
copies of the shared files evolve under their own evidence.

`--check PIN [SCOPE ...]` requires every cases.json under a SCOPE directory that binds `analysis_sources` to have a
pin, and, for every pinned case: the revision is an ancestor of HEAD, the case's bytes at HEAD equal
its bytes at the revision (retained bytes are immutable), and every bound source at the revision has its recorded
sha256. It reports which bound files main has since changed, as information. `--worktree PIN CASE DIR` adds a
detached worktree at that case's revision for running the case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "frozen-case-source-pin-v1"


def git(*arguments: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), *arguments], check=True, capture_output=True).stdout


def at(revision: str, path: str) -> bytes:
    """A file's bytes in a revision's tree."""
    try:
        return git("show", f"{revision}:{path}")
    except subprocess.CalledProcessError as error:
        raise ValueError(f"{path} is absent at {revision}") from error


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(pin: Path) -> list[dict[str, str]]:
    record = json.loads(pin.read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA or not isinstance(record.get("cases"), list) or not record["cases"]:
        raise ValueError(f"{pin}: a {SCHEMA} record with a nonempty cases list is required")
    for entry in record["cases"]:
        if not isinstance(entry, dict) or set(entry) != {"case", "revision"}:
            raise ValueError(f"{pin}: every pinned case names exactly its case file and revision")
    return record["cases"]


def bound_sources(record: dict[str, Any]) -> dict[str, str]:
    """The sha256 of every source file a frozen record binds: a case's `analysis_sources`, or a campaign's
    `dependencies` rows of `file` and `sha256`."""
    if isinstance(record.get("analysis_sources"), dict):
        return dict(record["analysis_sources"])
    rows = record.get("dependencies")
    if (
        isinstance(rows, list)
        and rows
        and all(isinstance(row, dict) and set(row) == {"file", "sha256"} for row in rows)
    ):
        return {row["file"]: row["sha256"] for row in rows}
    raise ValueError("a frozen record binds its sources as analysis_sources or as dependencies rows")


def check_case(case: str, revision: str) -> dict[str, Any]:
    """One pinned case's verification; raises on a broken pin and reports main's drift."""
    commit = git("rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    ancestry = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"], check=False)
    if ancestry.returncode != 0:
        raise ValueError(f"{case}: pinned revision {revision} is not an ancestor of HEAD")
    retained = (ROOT / case).read_bytes()
    if retained != at(commit, case):
        raise ValueError(f"{case}: the case bytes differ from their bytes at {revision}")
    sources = bound_sources(json.loads(retained))
    for name, expected in sources.items():
        if sha256(at(commit, name)) != expected:
            raise ValueError(f"{case}: {name} at {revision} does not have the bound sha256")
    drift = sorted(name for name, expected in sources.items() if sha256((ROOT / name).read_bytes()) != expected)
    return {"case": case, "revision": commit, "sources": len(sources), "changed_on_head": drift}


def run_at_pin(pin: Path, case: str, command: list[str], directory: Path) -> subprocess.CompletedProcess[str]:
    """Run a command in a detached worktree at the case's pinned revision and remove the worktree afterwards.

    A frozen case's check and analysis read the bound bytes of files main has moved past, so they run where those
    bytes are; `git worktree remove` without --force refuses a worktree the command left modified.
    """
    revisions = {row["case"]: row["revision"] for row in load(pin)}
    if case not in revisions:
        raise ValueError(f"{case} has no pin in {pin}")
    report = check_case(case, revisions[case])
    git("worktree", "add", "--detach", str(directory), report["revision"])
    try:
        return subprocess.run(command, cwd=directory, text=True, capture_output=True, check=False)
    finally:
        git("worktree", "remove", str(directory))


def run_pinned_audit_test(pin: Path, case: str, node: str, directory: Path) -> None:
    """Run the pinned revision's own copy of an audit test node, which reads the frozen case's bound sources."""
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "-o",
        "addopts=",
        "-m",
        "audit",
        node,
    ]
    result = run_at_pin(pin, case, command, directory)
    if result.returncode:
        raise ValueError(f"{node} at the pin of {case} failed:\n{result.stdout}{result.stderr}")


def bound_cases(scopes: list[Path]) -> list[str]:
    """Every cases.json under the scopes that binds source digests, as a repository-relative path."""
    found = []
    for scope in scopes:
        for path in sorted((ROOT / scope).rglob("cases.json")):
            if isinstance(json.loads(path.read_bytes()).get("analysis_sources"), dict):
                found.append(path.relative_to(ROOT).as_posix())
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", type=Path, metavar="PIN")
    mode.add_argument("--worktree", nargs=3, metavar=("PIN", "CASE", "DIR"))
    parser.add_argument("scopes", nargs="*", type=Path, help="with --check: directories whose bound cases need a pin")
    arguments = parser.parse_args()
    try:
        if arguments.check:
            entries = load(arguments.check)
            unpinned = sorted(set(bound_cases(arguments.scopes)) - {entry["case"] for entry in entries})
            if unpinned:
                raise ValueError(f"bound cases without a source pin: {', '.join(unpinned)}")
            for entry in entries:
                report = check_case(entry["case"], entry["revision"])
                drift = ", ".join(report["changed_on_head"]) or "none"
                print(
                    f"{report['case']}: {report['sources']} sources pinned at {report['revision'][:12]}; "
                    f"changed on HEAD: {drift}"
                )
            return 0
        pin, case, directory = arguments.worktree
        revisions = {row["case"]: row["revision"] for row in load(Path(pin))}
        if case not in revisions:
            raise ValueError(f"{case} has no pin in {pin}")
        report = check_case(case, revisions[case])
        git("worktree", "add", "--detach", directory, report["revision"])
        print(f"{directory}: detached at {report['revision'][:12]}, every bound source of {case} in place")
        return 0
    except (ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"frozen case sources: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
