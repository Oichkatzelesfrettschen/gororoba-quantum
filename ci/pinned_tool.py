"""Run ruff or mypy at the version ci/requirements-ci.txt pins.

Usage: "$PYTHON" ci/pinned_tool.py TOOL ARGS...

The installed tool runs directly when it reports the pin exactly, which is
the CI case: each runs as the requesting interpreter's module, ``"$PYTHON" -m
ruff`` and ``"$PYTHON" -m mypy``, so the version checked is the
interpreter's own distribution and mypy's imports resolve against that
interpreter's packages; a ruff executable earlier on PATH from another
install never stands in for it. Otherwise, unless GOROROBA_PINS_REQUIRED=1, uv runs
the pinned release: ruff through ``uv tool run``, which needs nothing from
the project environment, and mypy through ``uv run --no-project --python
"$PYTHON" --with mypy==PIN``, which layers the pinned mypy over the calling
interpreter's site-packages so imports resolve against the packages that
interpreter holds. A host interpreter can hold other package versions than
CI's (qiskit 2.5.2 against 2.6.0), so a host mypy run checks the same
mypy release against that host's stubs; the two can still differ where those
stubs differ. One line on stderr names the substitution.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

import pins

REQUIREMENTS = Path(__file__).resolve().parent / "requirements-ci.txt"
TOOLS = ("ruff", "mypy")
# The whole version token after the tool's name, so 2.4.0+local or
# 0.17.1.post1 never reads as the release 2.4.0 or 0.17.1.
_VERSION = re.compile(r"^\S+ (\S+)")


def launcher(tool: str, python: str) -> list[str]:
    """The tool as the requesting interpreter's module, so the version probed is the one that runs."""
    return [python, "-m", tool]


def installed_version(tool: str, python: str) -> str | None:
    try:
        completed = subprocess.run(
            [*launcher(tool, python), "--version"], capture_output=True, text=True, check=False, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _VERSION.match(completed.stdout.strip())
    return match.group(1) if completed.returncode == 0 and match else None


def command(
    tool: str,
    arguments: Sequence[str],
    pin: str,
    installed: str | None,
    environment: Mapping[str, str],
    uv: str | None,
    python: str,
) -> tuple[list[str], str | None]:
    """The argv that runs TOOL at PIN and the substitution notice, or SystemExit naming why none can."""
    if tool not in TOOLS:
        raise SystemExit(f"pinned_tool: {tool!r} is not one of {', '.join(TOOLS)}")
    if installed == pin:
        return [*launcher(tool, python), *arguments], None
    found = f"{tool} {installed}" if installed else f"no {tool}"
    if pins.pins_required(environment):
        raise SystemExit(f"pinned_tool: {found} is installed; {pins.PINS_REQUIRED}=1 requires {tool} {pin}")
    if uv is None:
        raise SystemExit(f"pinned_tool: {found} is installed and uv is absent; install {tool}=={pin} or uv")
    notice = f"pinned_tool: {found} is installed; running {tool} {pin} through uv"
    if tool == "ruff":
        return [uv, "tool", "run", "--from", f"ruff=={pin}", "ruff", *arguments], notice
    return [uv, "run", "--no-project", "--python", python, "--with", f"mypy=={pin}", "--", "mypy", *arguments], notice


def main(argv: Sequence[str]) -> int:
    if not argv:
        raise SystemExit("usage: pinned_tool.py TOOL ARGS...")
    tool, arguments = argv[0], list(argv[1:])
    pinned = pins.read_pins(REQUIREMENTS)
    if tool not in pinned:
        raise SystemExit(f"pinned_tool: {REQUIREMENTS.name} pins no {tool}")
    argv_out, notice = command(
        tool,
        arguments,
        pinned[tool],
        installed_version(tool, sys.executable),
        os.environ,
        shutil.which("uv"),
        sys.executable,
    )
    if notice:
        print(notice, file=sys.stderr, flush=True)
    return subprocess.run(argv_out, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
