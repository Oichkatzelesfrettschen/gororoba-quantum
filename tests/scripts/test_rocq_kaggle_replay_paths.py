"""Contract for the path handling of rocq_kaggle_replay.main: every external path that reaches a replay is absolute.

A replay runs from a shadow root in another working directory, so a relative --gororoba-root, --gororoba-math-root,
--rocq or $GOROROBA_MATH must resolve against the directory the driver started in.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import pytest
import rocq_kaggle_replay as driver


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(
        [
            "git",
            "-C",
            str(directory),
            "-c",
            "core.fsmonitor=false",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@e.invalid",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def build(tmp_path: Path) -> tuple[str, str]:
    """An open checkout and a math checkout, a fake rocq, and the commit of the open checkout."""
    opened = tmp_path / "work/open"
    opened.mkdir(parents=True)
    git(opened, "init", "-q")
    git(opened, "commit", "-q", "--allow-empty", "-m", "x")
    math = tmp_path / "work/math"
    (math / "rocq/quantum").mkdir(parents=True)
    (math / "rocq/quantum/_RocqProject").write_text("One.v\n", encoding="utf-8")
    git(math, "init", "-q")
    git(math, "add", ".")
    git(math, "commit", "-q", "-m", "x")
    banner = driver.TOOLCHAIN.read_text(encoding="utf-8")
    rocq = tmp_path / "work/bin/rocq"
    rocq.parent.mkdir()
    rocq.write_text(f"#!/bin/sh\ncat <<'EOF'\n{banner}EOF\n", encoding="utf-8")
    rocq.chmod(0o755)
    return git(opened, "rev-parse", "HEAD"), git(math, "rev-parse", "HEAD")


@pytest.mark.parametrize("math_through", ["flag", "environment"])
def test_relative_roots_reach_the_replays_as_absolute_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, math_through: str
) -> None:
    commit, math_head = build(tmp_path)
    seen: list[Any] = []

    def record(function: Any, items: list[Any], **_options: Any) -> list[tuple[str, dict[str, Any]]]:
        seen.extend(items)
        return []

    monkeypatch.setattr(driver.parallel, "ordered_map", record)
    monkeypatch.setattr(driver.math_sources, "read_pin", lambda _root=None: math_head)
    monkeypatch.delenv("GOROROBA_MATH", raising=False)
    arguments = [
        "--gororoba-commit",
        commit,
        "--gororoba-root",
        "open",
        "--rocq",
        "bin/rocq",
        "--only",
        "cd-twisted-product",
    ]
    if math_through == "flag":
        arguments += ["--gororoba-math-root", "math"]
    else:
        monkeypatch.setenv("GOROROBA_MATH", "math")
    monkeypatch.chdir(tmp_path / "work")
    monkeypatch.setattr("sys.argv", ["rocq_kaggle_replay.py", *arguments, "--out", str(tmp_path / "out.json")])
    if driver.main() != 0:
        raise AssertionError("the driver failed with relative roots")
    (name, rocq, gororoba, math) = seen[0]
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    for path in (rocq, gororoba, math):
        if not Path(path).is_absolute() or not Path(path).exists():
            raise AssertionError(f"{path} does not resolve from another working directory")
    if os.environ.get("GOROROBA_MATH") and not Path(os.environ["GOROROBA_MATH"]).is_absolute():
        raise AssertionError("GOROROBA_MATH stayed relative")
