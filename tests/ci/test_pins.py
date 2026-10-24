"""Contract for ci/pins.py and ci/pinned_tool.py: exact-pin parsing, the replay interpreter's
verification and fallback, the pinned lint tool's substitution, and the refusal of every
fallback under GOROROBA_PINS_REQUIRED=1.
"""

from __future__ import annotations

import json
import re
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
        with patch.object(pins, "mismatches", lambda _python, _pins, _patches=None: list(probe)):
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


def test_installer_state_enters_the_comparison() -> None:
    # ci/install_pins.sh installs its --no-deps pins and patches site-packages
    # after the pin files; an interpreter without either differs from a built one.
    if pins.installer_pins().get("mpmath") != "1.4.1":
        raise AssertionError(f"install_pins.sh's --no-deps pins read {pins.installer_pins()}")
    with TemporaryDirectory(prefix="ci-pins-patch-") as temporary:
        tree = Path(temporary)
        (tree / "ci" / "patches").mkdir(parents=True)
        (tree / "ci" / "install_pins.sh").write_text(
            '"$PYTHON" -m pip install --no-deps pip-package-that-is-absent==2.0\n'
        )
        (tree / "ci" / "patches" / "absent.patch").write_text(
            "--- a/package-that-is-absent/module.py\n+++ b/package-that-is-absent/module.py\n@@ -1 +1 @@\n-old\n+new\n"
        )
        found = pins.environment_mismatches(sys.executable, {}, tree)
        if found != ["pip-package-that-is-absent absent (pin 2.0)", "absent.patch not applied"]:
            raise AssertionError(f"the installer state of a tree reads {found}")
        # A host without the patch binary reports the patch unverified rather than raising.
        run = pins.subprocess.run

        def without_patch(argv: list[str], **options: Any) -> Any:
            if argv[0] == "patch":
                raise FileNotFoundError(2, "No such file or directory", "patch")
            return run(argv, **options)

        with patch.object(pins.subprocess, "run", without_patch):
            found = pins.environment_mismatches(sys.executable, {}, tree)
        if found[1:] != ["absent.patch could not be checked: [Errno 2] No such file or directory: 'patch'"]:
            raise AssertionError(f"the installer state without the patch binary reads {found}")


def test_host_environment_fallback() -> None:
    # A drifted running interpreter falls back to the runtime's host
    # environment when that holds every pin; neither names the build command.
    python = sys.executable
    differing = ["qiskit 2.5.2 (pin 2.6.0)"]
    with TemporaryDirectory(prefix="ci-pins-cache-") as temporary:
        cache = {"XDG_CACHE_HOME": temporary}
        current_host = pins.host_env("current", cache)
        replay_host = pins.host_env("qiskit-2.5", cache)
        if current_host.parent.parent.name != f"ci-py{pins.PYTHON_VERSION}":
            raise AssertionError(f"the current runtime's host environment is {current_host}")

        def resolve(probe: dict[str, list[str]], environment: dict[str, str]) -> dict[str, tuple[str | None, str]]:
            with patch.object(
                pins, "mismatches", lambda candidate, _pins, _patches=None: list(probe.get(candidate, differing))
            ):
                return {
                    "current": pins.resolve_current(environment, python),
                    "replay": pins.resolve_replay("qiskit-2.5", None, environment, python),
                }

        absent = resolve({}, cache)
        for runtime, (chosen, reason) in absent.items():
            if chosen is not None or pins.BUILD_COMMAND not in reason:
                raise AssertionError(f"{runtime} without a host environment chose {chosen} ({reason})")
        for host in (current_host, replay_host):
            host.parent.mkdir(parents=True)
            host.write_text("")
        built = resolve({str(current_host): [], str(replay_host): []}, cache)
        if built["current"][0] != str(current_host) or built["replay"][0] != str(replay_host):
            raise AssertionError(f"a host environment holding every pin was not chosen: {built}")
        drifted = resolve({}, cache)
        if any(chosen is not None for chosen, _reason in drifted.values()):
            raise AssertionError(f"a host environment that differs from its pins was chosen: {drifted}")
        running = resolve({python: []}, cache)
        if running["current"][0] != python or running["replay"][0] != python:
            raise AssertionError(f"a running interpreter holding every pin lost to the host environment: {running}")
        strict = resolve({str(current_host): [], str(replay_host): []}, {**cache, **STRICT})
        if any(chosen is not None for chosen, _reason in strict.values()):
            raise AssertionError(f"{pins.PINS_REQUIRED}=1 took a host environment: {strict}")
        named = resolve({}, {**cache, "PYTHON": "/named/python"})["current"]
        if named[0] != "/named/python" or "runs as named" not in named[1]:
            raise AssertionError(f"an explicit PYTHON was replaced: {named}")
        refused = resolve({}, {**cache, **STRICT, "PYTHON": "/named/python"})["current"]
        if refused[0] is not None:
            raise AssertionError(f"{pins.PINS_REQUIRED}=1 ran a PYTHON that differs from its pins: {refused}")
        with patch.object(pins, "mismatches", lambda candidate, _pins, _patches=None: list(differing)):
            admitted = pins.resolve_current({**cache, "PYTHON": "/named/python"}, python, admission=True)
        if admitted[0] is not None or "cannot decide admission" not in admitted[1]:
            raise AssertionError(f"an admission run took a PYTHON that differs from its pins: {admitted}")
        with patch.object(pins, "mismatches", lambda candidate, _pins, _patches=None: []):
            admitted = pins.resolve_current({**cache, "PYTHON": "/named/python"}, python, admission=True)
        if admitted[0] != "/named/python":
            raise AssertionError(f"an admission run refused a PYTHON holding every pin: {admitted}")
    with TemporaryDirectory(prefix="ci-pins-tree-") as temporary:
        chosen, reason = pins.resolve_current({}, python, Path(temporary))
        if chosen != python or "pins no current runtime" not in reason:
            raise AssertionError(f"a tree without pin files verified {chosen} ({reason})")


def test_lane_resolution() -> None:
    # A pr_checks lane runs an explicit PYTHON only when it holds the lane's pins, takes the host environment
    # when PYTHON is unset, and refuses a drifted interpreter with the command that runs the lane correctly.
    python = sys.executable
    differing = ["ruff 0.14.11 (pin 0.17.1)"]
    with TemporaryDirectory(prefix="ci-pins-lane-") as temporary:
        cache = {"XDG_CACHE_HOME": temporary}
        host = pins.host_env("current", cache)
        asked: list[dict[str, str]] = []

        def resolve(lane: str, holding: set[str], environment: dict[str, str]) -> tuple[str | None, str]:
            def probe(candidate: str, wanted: dict[str, str], _patches: object = None) -> list[str]:
                asked.append(dict(wanted))
                return [] if candidate in holding else list(differing)

            with patch.object(pins, "mismatches", probe):
                return pins.resolve_lane(lane, environment, python)

        refuses(lambda: resolve("audit", set(), cache), "not one of")
        chosen, reason = resolve("lint", set(), cache)
        if chosen is not None or pins.BUILD_COMMAND not in reason:
            raise AssertionError(f"a drifted lint interpreter without a host environment ran: {chosen} ({reason})")
        if asked[-1] != {"ruff": pins.current_pins()["ruff"]}:
            raise AssertionError(f"lint probed pins beyond ruff: {asked[-1]}")
        resolve("tests", {python}, cache)
        if set(asked[-1]) < set(pins.current_pins()):
            raise AssertionError("tests probed fewer than every current pin")
        if resolve("lint", {python}, cache)[0] != python:
            raise AssertionError("a running interpreter holding the lint pins was refused")
        host.parent.mkdir(parents=True)
        host.write_text("")
        for lane in pins.LANES:
            if resolve(lane, {str(host)}, cache)[0] != str(host):
                raise AssertionError(f"{lane} with PYTHON unset passed over a host environment holding its pins")
        chosen, reason = resolve("types", {str(host)}, {**cache, "PYTHON": "/named/python"})
        if chosen is not None or f"PYTHON={host} sh ci/pr_checks.sh types" not in reason:
            raise AssertionError(f"a drifted explicit PYTHON was not refused with the host command: {reason}")
        if resolve("tests", {"/named/python", str(host)}, {**cache, "PYTHON": "/named/python"})[0] != "/named/python":
            raise AssertionError("an explicit PYTHON holding every pin was replaced")


def test_host_environment_python_version() -> None:
    # The host environments sit on the Python CI's setup-python installs.
    workflow = (pins.ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    script = (pins.ROOT / "ci/build_host_envs.sh").read_text(encoding="utf-8")
    if f'python-version: "{pins.PYTHON_VERSION}"' not in workflow:
        raise AssertionError(f"ci.yml installs no Python {pins.PYTHON_VERSION}")
    if f"python_version={pins.PYTHON_VERSION}\n" not in script:
        raise AssertionError(f"ci/build_host_envs.sh builds on another Python than {pins.PYTHON_VERSION}")


def test_pinned_tool() -> None:
    uv, python = "/usr/bin/uv", "/usr/bin/python3"
    # An installed pin runs as the requesting interpreter's module, so the distribution whose version was probed
    # runs, never a PATH executable of another install, and mypy's imports resolve against that interpreter.
    argv, notice = pinned_tool.command("ruff", ["check", "ci"], "0.17.1", "0.17.1", {}, uv, python)
    if argv != [python, "-m", "ruff", "check", "ci"] or notice is not None:
        raise AssertionError(f"an installed pin runs {argv} with notice {notice}")
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


def test_gate_lint_tools_are_pinned() -> None:
    # A bare ruff or mypy resolves through PATH, where a host install of
    # another release reports its own defects as gate failures.
    gates = json.loads((pins.ROOT / "ci/gates.json").read_text(encoding="utf-8"))["gates"]
    bare = re.compile(r"(?:(?:^|&&|\|\||;|\||\$\(|\bthen|\bxargs)\s*(?:\w+=\S+\s+)*|-m\s+)(?:ruff|mypy)\b")
    unpinned = [gate["name"] for gate in gates if bare.search(gate["cmd"])]
    if unpinned:
        raise AssertionError(f"gates run ruff or mypy outside ci/pinned_tool.py: {', '.join(unpinned)}")
    planted = (
        "MYPYPATH=docs mypy docs",
        '"$PYTHON" -m mypy scripts',
        "true && ruff check ci",
        "git ls-files | xargs ruff check",
        "test -d ci && $(ruff check ci)",
    )
    pinned = ('MYPYPATH=docs "$PYTHON" ci/pinned_tool.py mypy docs', '"$PYTHON" ../ci/pinned_tool.py ruff check .')
    if not all(bare.search(command) for command in planted) or any(bare.search(command) for command in pinned):
        raise AssertionError("the bare-tool pattern misreads a planted command")
