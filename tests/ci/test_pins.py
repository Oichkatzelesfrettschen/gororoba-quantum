"""Contract for ci/pins.py and ci/pinned_tool.py: exact-pin parsing, the replay interpreter's
verification and fallback, the pinned lint tool's substitution, and the refusal of every
fallback under GOROROBA_PINS_REQUIRED=1.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import pinned_tool
import pins

STRICT = {pins.PINS_REQUIRED: "1"}


def refuses(action: Callable[[], Any], fragment: str) -> None:
    try:
        action()
    except (SystemExit, ValueError) as error:
        if fragment not in str(error):
            raise AssertionError(f"refused with {error!r}, expected {fragment!r}") from error
        return
    raise AssertionError(f"accepted where {fragment!r} must refuse")


def test_read_pins() -> None:
    with TemporaryDirectory(prefix="ci-pins-") as temporary:
        path = Path(temporary) / "requirements.txt"
        path.write_text("# comment\nnumpy==2.5.4  # trailing\n\nqiskit==2.5.2\n")
        if pins.read_pins(path) != {"numpy": "2.5.4", "qiskit": "2.5.2"}:
            raise AssertionError(f"read_pins parsed {pins.read_pins(path)}")
        path.write_text("numpy>=2\n")
        refuses(lambda: pins.read_pins(path), "not an exact pin")
    for runtime, (_variable, path) in pins.REPLAY_RUNTIMES.items():
        if not pins.read_pins(path):
            raise AssertionError(f"{runtime}: {path.name} pins nothing")


def test_replay_resolution() -> None:
    python = sys.executable
    found = pins.mismatches(python, {"pip-package-that-is-absent": "1.0"})
    if found != ["pip-package-that-is-absent absent (pin 1.0)"]:
        raise AssertionError(f"an absent distribution reads {found}")
    if not pins.mismatches("/nonexistent/python", {"numpy": "1"})[0].startswith("/nonexistent/python could not run"):
        raise AssertionError("an interpreter that cannot start reads as matching")

    def resolve(probe: list[str], explicit: str | None, environment: dict[str, str]) -> tuple[str | None, str]:
        with patch.object(pins, "mismatches", lambda _python, _pins: list(probe)):
            return pins.resolve_replay("qiskit-2.5", explicit, environment, python)

    differing = ["qiskit 2.6.0 (pin 2.5.2)"]
    cases: tuple[tuple[str | None, dict[str, str], list[str], str | None, str], ...] = (
        # explicit flag, environment, probe result, expected interpreter, reason fragment
        ("/flag/python", {"REPLAY_PYTHON": "/env/python"}, [], "/flag/python", "--replay-python"),
        (None, {"REPLAY_PYTHON": "/env/python"}, [], "/env/python", "REPLAY_PYTHON=/env/python"),
        (None, {"REPLAY_PYTHON": "/env/python"}, differing, None, "differs from requirements-replay.txt"),
        (None, {"REPLAY_PYTHON": "/env/python", **STRICT}, [], "/env/python", "holds every pin"),
        (None, {}, [], python, "running interpreter"),
        (None, {}, differing, None, "requires REPLAY_PYTHON; the running interpreter differs"),
        (None, dict(STRICT), [], None, f"{pins.PINS_REQUIRED}=1"),
    )
    for explicit, environment, probe, expected, fragment in cases:
        chosen, reason = resolve(probe, explicit, environment)
        if chosen != expected or fragment not in reason:
            raise AssertionError(f"{explicit}, {environment}, {probe}: chose {chosen} ({reason})")
    # Each tree verifies against its own pin file: a tree whose pins name an
    # absent distribution refuses the interpreter the repository's pins admit.
    with TemporaryDirectory(prefix="ci-pins-tree-") as temporary:
        tree = Path(temporary)
        (tree / "ci").mkdir()
        (tree / "ci" / "requirements-replay.txt").write_text("pip-package-that-is-absent==1.0\n")
        chosen, reason = pins.resolve_replay("qiskit-2.5", python, {}, python, tree)
        if chosen is not None or "pip-package-that-is-absent" not in reason:
            raise AssertionError(f"a tree's own pins were not applied: {chosen} ({reason})")


def test_pinned_tool() -> None:
    uv, python = "/usr/bin/uv", "/usr/bin/python3"
    argv, notice = pinned_tool.command("ruff", ["check", "ci"], "0.17.1", "0.17.1", {}, uv, python)
    if Path(argv[0]).name != "ruff" or argv[1:] != ["check", "ci"] or notice is not None:
        raise AssertionError(f"an installed pin runs {argv} with notice {notice}")
    # An installed mypy runs as the requested interpreter's module, so its
    # imports resolve against that interpreter and not the PATH executable's.
    argv, notice = pinned_tool.command("mypy", ["."], "2.4.0", "2.4.0", {}, uv, python)
    if argv != [python, "-m", "mypy", "."] or notice is not None:
        raise AssertionError(f"an installed mypy pin runs {argv}")
    for reported, version in (
        ("mypy 2.4.0 (compiled: yes)", "2.4.0"),
        ("mypy 2.4.0+local (compiled: no)", "2.4.0+local"),
        ("ruff 0.17.1.post1", "0.17.1.post1"),
    ):
        match = pinned_tool._VERSION.match(reported)
        if match is None or match.group(1) != version:
            raise AssertionError(f"{reported!r} parses as {match and match.group(1)}, not {version}")
    refuses(lambda: pinned_tool.command("mypy", [], "2.4.0", "2.4.0+local", STRICT, uv, python), pins.PINS_REQUIRED)
    argv, notice = pinned_tool.command("ruff", ["check"], "0.17.1", "0.14.11", {}, uv, python)
    if argv != [uv, "tool", "run", "--from", "ruff==0.17.1", "ruff", "check"] or not notice:
        raise AssertionError(f"a ruff mismatch runs {argv}")
    argv, notice = pinned_tool.command("mypy", ["."], "2.4.0", None, {}, uv, python)
    expected = [uv, "run", "--no-project", "--python", python, "--with", "mypy==2.4.0", "--", "mypy", "."]
    if argv != expected or notice is None or "no mypy" not in notice:
        raise AssertionError(f"an absent mypy runs {argv} ({notice})")
    refuses(lambda: pinned_tool.command("ruff", [], "0.17.1", "0.14.11", STRICT, uv, python), pins.PINS_REQUIRED)
    refuses(lambda: pinned_tool.command("mypy", [], "2.4.0", "1.19.1", {}, None, python), "uv is absent")
    refuses(lambda: pinned_tool.command("black", [], "1", "1", {}, uv, python), "is not one of")
    pinned = pins.read_pins(pinned_tool.REQUIREMENTS)
    missing = [tool for tool in pinned_tool.TOOLS if tool not in pinned]
    if missing:
        raise AssertionError(f"{pinned_tool.REQUIREMENTS.name} pins no {', '.join(missing)}")
