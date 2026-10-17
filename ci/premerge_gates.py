"""Run the fast gates on the tree a merge into main would produce, against main's own result.

A pull request's CI runs on its merge with main as main stood when CI ran.
A gate that checks a record derived from the whole tree (the toolchain
record over every case circuit, the research-state registry over every
retained run) can then pass on two branches separately and fail on their
combination: one branch adds the record or its gate, the other adds or
regenerates an input the record does not yet cover, and git merges both
without a textual conflict. This script builds that combination before the
merge: it checks out BASE (default origin/main) and the merge of REF into
BASE in two detached worktrees, runs the pr-tier gates whose measured
seconds are at most --max-seconds in each tree through that tree's own
ci/run_gates.py, with $PYTHON resolved to an absolute interpreter, and
reports every gate that passes on BASE and fails on the merge, or that the
merge adds and that fails. Gates that fail on both trees are host or main
failures and are listed without failing the run, so a lint or type gate
whose local toolchain differs from CI's does not mask the comparison. A
textual conflict stops the run with the conflicted paths.

The worktrees live under --worktrees (default ~/worktrees/<repository>/premerge,
<repository> naming the primary checkout) and are removed on exit. Exit
status: 0 when the merge introduces no failure, 1 when it does, 2 on a merge
conflict.

Usage: "$PYTHON" ci/premerge_gates.py REF [--base origin/main] [--max-seconds 5] [--no-fetch]
       "$PYTHON" ci/premerge_gates.py --self-test
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAX_SECONDS = 5.0
TAIL_LINES = 20
# The merge commit lives only in the scratch worktree and is never pushed, so it
# carries a local identity and no signature.
MERGE_IDENTITY = ["-c", "user.name=premerge", "-c", "user.email=premerge@localhost", "-c", "commit.gpgSign=false"]
VERDICT = re.compile(r"^(PASS|FAIL) (\S+) ")
FAILURE_TAIL = re.compile(r"^=== (\S+) exit ")


def git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if check and completed.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}:\n{completed.stderr.strip()}")
    return completed.stdout.strip()


def repository_name(repo: Path) -> str:
    """The primary checkout's directory name; a linked worktree's own directory names its branch instead."""
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    return common.parent.name


@contextlib.contextmanager
def worktree(repo: Path, path: Path, commit: str) -> Iterator[Path]:
    """A detached worktree of commit at path, removed with its generated files on exit."""
    git(repo, "worktree", "add", "--detach", str(path), commit)
    try:
        yield path
    finally:
        git(repo, "worktree", "remove", "--force", str(path), check=False)
        git(repo, "worktree", "prune", check=False)


def interpreter() -> str:
    """$PYTHON as an absolute path, since every gate runs with its cwd inside a scratch worktree."""
    named = os.environ.get("PYTHON", sys.executable)
    found = shutil.which(named)
    if found is None:
        raise SystemExit(f"PYTHON={named} names no executable")
    return os.path.abspath(found)


def results(root: Path, max_seconds: float) -> dict[str, tuple[int, str]]:
    """Each gate's status and failure output from the tree's own ci/run_gates.py."""
    python = interpreter()
    environment = {**os.environ, "PYTHON": python}
    completed = subprocess.run(
        [python, "-B", str(root / "ci/run_gates.py"), "--tier", "pr", "--max-seconds", str(max_seconds)],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = completed.stdout.splitlines()
    statuses = {m.group(2): 0 if m.group(1) == "PASS" else 1 for m in map(VERDICT.match, lines) if m}
    if not statuses:
        raise SystemExit(f"{root / 'ci/run_gates.py'} reported no gate:\n{completed.stdout}{completed.stderr}")
    tails: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        if heading := FAILURE_TAIL.match(line):
            current = heading.group(1)
            tails[current] = []
        elif current is not None:
            tails[current].append(line)
    return {name: (status, "\n".join(tails.get(name, []))) for name, status in statuses.items()}


def compare(base: dict[str, tuple[int, str]], merged: dict[str, tuple[int, str]]) -> tuple[list[str], list[str]]:
    """Gates the merge breaks (pass on base or absent there, fail on the merge) and gates failing on both."""
    introduced = [name for name, (status, _) in merged.items() if status != 0 and base.get(name, (0, ""))[0] == 0]
    shared = [name for name, (status, _) in merged.items() if status != 0 and base.get(name, (0, ""))[0] != 0]
    return introduced, shared


def premerge(repo: Path, ref: str, base_ref: str, max_seconds: float, worktrees: Path) -> int:
    base_commit = git(repo, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
    ref_commit = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    worktrees.mkdir(parents=True, exist_ok=True)
    label = f"{base_commit[:12]}-{ref_commit[:12]}"
    try:
        with (
            worktree(repo, worktrees / f"base-{label}", base_commit) as base_tree,
            worktree(repo, worktrees / f"merge-{label}", base_commit) as merge_tree,
        ):
            merged = subprocess.run(
                ["git", "-C", str(merge_tree), *MERGE_IDENTITY, "merge", "--no-ff", "--no-edit", ref_commit],
                capture_output=True,
                text=True,
                check=False,
            )
            if merged.returncode != 0:
                conflicts = git(merge_tree, "diff", "--name-only", "--diff-filter=U", check=False)
                git(merge_tree, "merge", "--abort", check=False)
                print(f"merge of {ref} into {base_ref} conflicts:\n{conflicts or merged.stdout + merged.stderr}")
                return 2
            base_results = results(base_tree, max_seconds)
            merge_results = results(merge_tree, max_seconds)
    finally:
        with contextlib.suppress(OSError):
            worktrees.rmdir()
    introduced, shared = compare(base_results, merge_results)
    for name in introduced:
        tail = "\n".join(merge_results[name][1].splitlines()[-TAIL_LINES:])
        print(f"=== {name} fails on the merge and passes on {base_ref}\n{tail}\n")
    if shared:
        print(f"failing on {base_ref} and on the merge (host or main): {', '.join(shared)}")
    print(
        f"premerge {ref} ({ref_commit[:12]}) into {base_ref} ({base_commit[:12]}): "
        f"{len(merge_results)} gates at most {max_seconds:g} s, {len(introduced)} introduced failures"
    )
    return 1 if introduced else 0


def self_test() -> None:
    """A clean merge where one branch adds a record gate and the other changes its input must fail."""
    with tempfile.TemporaryDirectory(prefix="premerge-contract-") as temporary:
        repo = Path(temporary) / "repo"
        (repo / "ci").mkdir(parents=True)
        git(repo, "init", "-q", "-b", "main")

        def commit(files: dict[str, str], message: str) -> None:
            for name, text in files.items():
                (repo / name).write_text(text)
            git(repo, "add", "-A")
            git(repo, *MERGE_IDENTITY, "commit", "-q", "-m", message)

        def gates(*extra: dict[str, Any]) -> str:
            listed = [{"name": "always", "cwd": ".", "cmd": "true", "seconds": 0.1, "tier": "pr"}, *extra]
            return json.dumps({"gates": listed})

        record_gate = {"name": "record", "cwd": ".", "cmd": 'test "$(cat input)" = "$(cat record)"', "seconds": 0.1}
        host_gate = {"name": "host", "cwd": ".", "cmd": "false", "seconds": 0.1}
        runner = (ROOT / "ci/run_gates.py").read_text(encoding="utf-8")
        commit({"ci/gates.json": gates(host_gate), "ci/run_gates.py": runner, "input": "v1\n"}, "base")
        git(repo, "branch", "adds-record")
        git(repo, "branch", "consistent")
        git(repo, "switch", "-q", "adds-record")
        commit({"ci/gates.json": gates(host_gate, record_gate), "record": "v1\n"}, "record and its gate")
        git(repo, "switch", "-q", "consistent")
        commit({"other": "x\n"}, "unrelated file")
        git(repo, "switch", "-q", "main")
        commit({"input": "v2\n"}, "regenerated input")
        worktrees = Path(temporary) / "worktrees"
        for ref, expected, marker in (
            ("adds-record", 1, "=== record fails on the merge"),
            ("consistent", 0, "0 introduced failures"),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = premerge(repo, ref, "main", DEFAULT_MAX_SECONDS, worktrees)
            text = output.getvalue()
            if status != expected or marker not in text or "(host or main): host" not in text:
                raise RuntimeError(f"premerge {ref} returned {status}, expected {expected}:\n{text}")
            if git(repo, "worktree", "list", "--porcelain").count("worktree ") != 1 or worktrees.exists():
                raise RuntimeError(f"premerge {ref} left a worktree or its directory behind")
        git(repo, "switch", "-q", "-c", "conflicting", "main~1")
        commit({"input": "v3\n"}, "conflicting input")
        git(repo, "switch", "-q", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            status = premerge(repo, "conflicting", "main", DEFAULT_MAX_SECONDS, worktrees)
        if status != 2 or worktrees.exists():
            raise RuntimeError(f"a conflicting merge returned {status}, expected 2, or left its directory")
    print("premerge: a clean merge that breaks a record gate fails, a consistent merge passes, a conflict stops")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("ref", nargs="?", help="branch, tag or commit to merge into BASE")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    parser.add_argument("--no-fetch", action="store_true", help="use the local refs as they stand")
    parser.add_argument("--worktrees", type=Path, help="scratch directory, default ~/worktrees/<repository>/premerge")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        self_test()
        return 0
    if arguments.ref is None:
        parser.error("REF is required unless --self-test")
    if not arguments.no_fetch:
        git(ROOT, "fetch", "--quiet", "origin")
    worktrees = arguments.worktrees or Path.home() / "worktrees" / repository_name(ROOT) / "premerge"
    return premerge(ROOT, arguments.ref, arguments.base, arguments.max_seconds, worktrees)


if __name__ == "__main__":
    sys.exit(main())
