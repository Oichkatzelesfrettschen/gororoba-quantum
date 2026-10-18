"""Exact-version pins of the CI requirement files, and the interpreters and tools that satisfy them.

A pin file lists one ``name==version`` per line; ``#`` starts a comment.
``mismatches`` imports nothing from the probed environment beyond
importlib.metadata, in a ``-I`` subprocess of that interpreter, so a probe of
a replay interpreter sees that interpreter's site-packages and not the
caller's.

GOROROBA_PINS_REQUIRED=1 turns every version fallback into a failure: the
replay interpreter must be named explicitly and match its pins, a lint tool
must be installed at its pin, and a record check that needs the recorded
package versions must find them. CI sets it, so a hosted run never takes a
fallback; a local run without it substitutes a verified equivalent and says
which one.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINS_REQUIRED = "GOROROBA_PINS_REQUIRED"
# Each historical runtime: the variable naming its interpreter and the pins it holds.
REPLAY_RUNTIMES = {"qiskit-2.5": ("REPLAY_PYTHON", ROOT / "ci" / "requirements-replay.txt")}

_PROBE = """
import json, sys
from importlib.metadata import PackageNotFoundError, version
found = {}
for name in json.loads(sys.argv[1]):
    try:
        found[name] = version(name)
    except PackageNotFoundError:
        found[name] = None
print(json.dumps(found))
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


def mismatches(python: str, pins: Mapping[str, str]) -> list[str]:
    """Each pin the interpreter does not hold, as ``name VERSION (pin PIN)``; a launch failure is one entry."""
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
    found = json.loads(completed.stdout)
    return [
        f"{name} {found.get(name) or 'absent'} (pin {version})"
        for name, version in pins.items()
        if found.get(name) != version
    ]


def resolve_replay(
    runtime: str, explicit: str | None, environment: Mapping[str, str], current: str
) -> tuple[str | None, str]:
    """The interpreter for a historical runtime's gates and a one-line account of the choice.

    An explicit interpreter (``--replay-python``) wins over the runtime's
    variable; either must hold every pin. With neither, the running
    interpreter serves when it holds every pin, unless PINS_REQUIRED
    demands an explicit one. None means the runtime's gates cannot run.
    """
    variable, path = REPLAY_RUNTIMES[runtime]
    pins = read_pins(path)
    named = explicit or environment.get(variable)
    source = "--replay-python" if explicit else variable
    if named:
        missing = mismatches(named, pins)
        if missing:
            return None, f"{source}={named} differs from {path.name}: {', '.join(missing)}"
        return named, f"{source}={named} holds every pin of {path.name}"
    if pins_required(environment):
        return None, f"historical runtime {runtime} requires {variable} under {PINS_REQUIRED}=1"
    missing = mismatches(current, pins)
    if missing:
        return None, (
            f"historical runtime {runtime} requires {variable}; the running interpreter differs "
            f"from {path.name}: {', '.join(missing)}"
        )
    return current, f"the running interpreter {current} holds every pin of {path.name}"
