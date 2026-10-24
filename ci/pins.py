"""Exact-version pins of the CI requirement files, and the interpreters and tools that satisfy them.

A pin file lists one ``name==version`` per line; ``#`` starts a comment.
``mismatches`` imports nothing from the probed environment beyond
importlib.metadata, in a ``-I`` subprocess of that interpreter, so a probe of
a replay interpreter sees that interpreter's site-packages and not the
caller's. ci/install_pins.sh builds every pinned environment, and after the
pin files it installs its ``--no-deps`` pins and applies ci/patches/ to
site-packages; ``environment_mismatches`` holds an interpreter to those too
(``installer_pins``, ``installer_patches``), so a stock environment holding
the pin files' versions alone never stands in for a built one.

GOROROBA_PINS_REQUIRED=1 turns every version fallback into a failure: the
replay interpreter must be named explicitly and match its pins, a lint tool
must be installed at its pin, and a record check that needs the recorded
package versions must find them. CI sets it, so a hosted run never takes a
fallback; a local run without it substitutes a verified equivalent and says
which one.

A local run's equivalent is the running interpreter when it holds every pin,
else the host environment ci/build_host_envs.sh builds for that pin set under
${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/ (HOST_ENVS), the same venv and
installer CI's jobs build. A run that finds neither refuses and names the
build command, since gates run under a drifted interpreter fail on version
differences rather than on the change under test.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINS_REQUIRED = "GOROROBA_PINS_REQUIRED"
# Each historical runtime: the variable naming its interpreter and the pins it holds.
REPLAY_RUNTIMES = {"qiskit-2.5": ("REPLAY_PYTHON", ROOT / "ci" / "requirements-replay.txt")}
REPLAY_VARIABLES = frozenset(variable for variable, _path in REPLAY_RUNTIMES.values())
# The pin files of the current runtime, which every gate without a runtime field runs under.
CURRENT_PINS = (ROOT / "requirements.txt", ROOT / "ci" / "requirements-ci.txt")
# The setup-python version of .github/workflows/ci.yml, which each host environment is built on.
PYTHON_VERSION = "3.14.7"
# Each runtime's host environment directory under the cache; "current" is the default runtime.
HOST_ENVS = {"current": f"ci-py{PYTHON_VERSION}", "qiskit-2.5": f"replay-py{PYTHON_VERSION}"}
BUILD_COMMAND = "sh ci/build_host_envs.sh"

_PROBE = """
import json, sys, sysconfig
from importlib.metadata import PackageNotFoundError, version
found = {}
for name in json.loads(sys.argv[1]):
    try:
        found[name] = version(name)
    except PackageNotFoundError:
        found[name] = None
print(json.dumps({"versions": found, "purelib": sysconfig.get_paths()["purelib"]}))
"""


def read_pins(path: Path) -> dict[str, str]:
    """Every ``name==version`` line of a requirement file, in file order."""
    pins: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        requirement = line.split("#", 1)[0].strip()
        if not requirement:
            continue
        name, separator, version = requirement.partition("==")
        if not separator or not name.strip() or not version.strip():
            raise ValueError(f"{path}: {requirement!r} is not an exact pin")
        pins[name.strip()] = version.strip()
    return pins


def pins_required(environment: Mapping[str, str]) -> bool:
    return environment.get(PINS_REQUIRED) == "1"


def installer_pins(root: Path = ROOT) -> dict[str, str]:
    """The ``--no-deps`` pins root's ci/install_pins.sh installs after the pin files, which win over them."""
    path = root / "ci" / "install_pins.sh"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    return {name: version for name, version in re.findall(r"--no-deps ([A-Za-z0-9_.-]+)==(\S+)", text)}


def installer_patches(root: Path = ROOT) -> list[Path]:
    """The ci/patches/ files ci/install_pins.sh applies to site-packages, in name order."""
    directory = root / "ci" / "patches"
    return sorted(directory.glob("*.patch")) if directory.is_dir() else []


def environment_mismatches(python: str, pins: Mapping[str, str], root: Path = ROOT) -> list[str]:
    """``mismatches`` against the pins plus root's installer pins, and each installer patch left unapplied."""
    return mismatches(python, {**pins, **installer_pins(root)}, installer_patches(root))


def mismatches(python: str, pins: Mapping[str, str], patches: list[Path] | None = None) -> list[str]:
    """Each pin the interpreter does not hold, as ``name VERSION (pin PIN)``, then each patch its site-packages
    lacks; a launch failure is one entry."""
    try:
        completed = subprocess.run(
            [python, "-I", "-c", _PROBE, json.dumps(list(pins))],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [f"{python} could not run: {error}"]
    if completed.returncode != 0:
        return [f"{python} exited {completed.returncode}: {completed.stderr.strip()[-200:]}"]
    probe = json.loads(completed.stdout)
    found = probe["versions"]
    missing = [
        f"{name} {found.get(name) or 'absent'} (pin {version})"
        for name, version in pins.items()
        if found.get(name) != version
    ]
    for patch in patches or []:
        with patch.open("rb") as stream:
            try:
                applied = subprocess.run(
                    ["patch", "-R", "--dry-run", "-s", "-f", "-p1", "-d", probe["purelib"]],
                    stdin=stream,
                    capture_output=True,
                    check=False,
                    timeout=120,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                missing.append(f"{patch.name} could not be checked: {error}")
                continue
        if applied.returncode != 0:
            missing.append(f"{patch.name} not applied")
    return missing


def resolve_replay(
    runtime: str,
    explicit: str | None,
    environment: Mapping[str, str],
    current: str,
    root: Path = ROOT,
) -> tuple[str | None, str]:
    """The interpreter for a historical runtime's gates and a one-line account of the choice.

    An explicit interpreter (``--replay-python``) wins over the runtime's
    variable; either must hold every pin of ROOT's own pin file, so a tree
    that changes the pins is verified against its own. With neither, the
    running interpreter serves when it holds every pin, unless PINS_REQUIRED
    demands an explicit one. None means the runtime's gates cannot run.
    """
    variable, default_path = REPLAY_RUNTIMES[runtime]
    path = root / default_path.relative_to(ROOT)
    pins = read_pins(path)
    named = explicit or environment.get(variable)
    source = "--replay-python" if explicit else variable
    if named:
        missing = environment_mismatches(named, pins, root)
        if missing:
            return None, f"{source}={named} differs from {path.name}: {', '.join(missing)}"
        return named, f"{source}={named} holds every pin of {path.name}"
    if pins_required(environment):
        return None, f"historical runtime {runtime} requires {variable} under {PINS_REQUIRED}=1"
    missing = environment_mismatches(current, pins, root)
    if not missing:
        return current, f"the running interpreter {current} holds every pin of {path.name}"
    host = host_env(runtime, environment)
    if host.is_file() and not environment_mismatches(str(host), pins, root):
        return str(host), f"the host environment {host} holds every pin of {path.name}"
    return None, (
        f"historical runtime {runtime} requires {variable}; the running interpreter differs "
        f"from {path.name}: {', '.join(missing)}; {BUILD_COMMAND} builds {host}"
    )


def host_env(runtime: str, environment: Mapping[str, str]) -> Path:
    """The interpreter of a runtime's host environment, ``current`` for the default runtime."""
    cache = environment.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(cache) / "gororoba-quantum" / HOST_ENVS[runtime] / "bin" / "python3"


def current_pins(root: Path = ROOT) -> dict[str, str]:
    """The current runtime's pins from root's requirements.txt and ci/requirements-ci.txt, later files winning."""
    merged: dict[str, str] = {}
    for default_path in CURRENT_PINS:
        path = root / default_path.relative_to(ROOT)
        if path.is_file():
            merged.update(read_pins(path))
    return merged


def resolve_current(
    environment: Mapping[str, str], current: str, root: Path = ROOT, admission: bool = False
) -> tuple[str | None, str]:
    """The interpreter for current-runtime gates and a one-line account of the choice.

    An explicit $PYTHON is the caller's choice: it runs whatever it holds,
    with the differing pins named, unless PINS_REQUIRED demands every pin or
    the run decides admission (``run_gates.py --changed-files``, the merge
    verdict), whose gates count only under the pinned runtime. Without one,
    the running interpreter serves when it holds every pin, then the host
    environment; None means no interpreter holds them. A tree without pin
    files verifies nothing.
    """
    pins = current_pins(root)
    files = " and ".join(path.name for path in CURRENT_PINS)
    named = environment.get("PYTHON")
    if not pins:
        return named or current, f"{named or current}: the tree pins no current runtime"
    if named:
        missing = environment_mismatches(named, pins, root)
        if not missing:
            return named, f"PYTHON={named} holds every pin of {files}"
        if pins_required(environment):
            return None, f"PYTHON={named} differs from {files} under {PINS_REQUIRED}=1: {', '.join(missing)}"
        if admission:
            return None, f"PYTHON={named} differs from {files} and cannot decide admission: {', '.join(missing)}"
        return named, f"PYTHON={named} differs from {files} and runs as named: {', '.join(missing)}"
    missing = environment_mismatches(current, pins, root)
    if not missing:
        return current, f"the running interpreter {current} holds every pin of {files}"
    if pins_required(environment):
        return None, f"the running interpreter differs from {files} under {PINS_REQUIRED}=1: {', '.join(missing)}"
    host = host_env("current", environment)
    if host.is_file() and not environment_mismatches(str(host), pins, root):
        return str(host), f"the host environment {host} holds every pin of {files}"
    return None, (
        f"the running interpreter {current} differs from {files}: {', '.join(missing)}; {BUILD_COMMAND} builds {host}"
    )


# The pins each ci/pr_checks.sh lane needs: lint runs only ruff, the others import the whole runtime.
LANES = ("lint", "types", "tests", "gates")


def resolve_lane(lane: str, environment: Mapping[str, str], current: str, root: Path = ROOT) -> tuple[str | None, str]:
    """The interpreter a ci/pr_checks.sh lane runs under and a one-line account of the choice.

    An explicit $PYTHON runs when it holds the lane's pins and is never replaced. Without one, the host
    environment serves when it holds them, which no CI runner builds, then the running interpreter. None names
    the differing pins and, when the host environment holds them, the command that runs the lane under it.
    """
    if lane not in LANES:
        raise ValueError(f"lane {lane!r} is not one of {', '.join(LANES)}")
    pins = current_pins(root)
    if not pins:
        bare = environment.get("PYTHON") or current
        return bare, f"{bare}: the tree pins no current runtime"
    wanted = {"ruff": pins["ruff"]} if lane == "lint" else pins

    def differs(python: str) -> list[str]:
        return mismatches(python, wanted) if lane == "lint" else environment_mismatches(python, wanted, root)

    host = host_env("current", environment)
    host_holds = host.is_file() and not differs(str(host))
    named = environment.get("PYTHON")
    if not named and host_holds:
        return str(host), f"the host environment {host} holds the {lane} pins"
    candidate = named or current
    missing = differs(candidate)
    if not missing:
        return candidate, f"{candidate} holds the {lane} pins"
    hint = f"; run PYTHON={host} sh ci/pr_checks.sh {lane}" if host_holds else f"; {BUILD_COMMAND} builds {host}"
    return None, f"{candidate} differs from the {lane} pins: {', '.join(missing)}{hint}"


def main(argv: list[str]) -> int:
    """``pins.py lane LANE``: print the lane's interpreter, or its refusal on stderr with exit 2."""
    if len(argv) != 2 or argv[0] != "lane":
        raise SystemExit("usage: pins.py lane lint|types|tests|gates")
    chosen, reason = resolve_lane(argv[1], os.environ, sys.executable)
    if chosen is None:
        print(f"pr_checks: {reason}", file=sys.stderr)
        return 2
    print(chosen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
