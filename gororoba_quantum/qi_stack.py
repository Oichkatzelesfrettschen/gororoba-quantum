"""The Quantum Inspire toolchain interpreter: resolution, one probe, and the live-or-replay choice.

qxelarator 0.10.0 ships cp313 wheels only and qiskit-quantuminspire 0.18.5
caps Qiskit below 2.4, so the Quantum Inspire stack (qxelarator, libqasm,
OpenSquirrel) runs under its own Python 3.13 interpreter, installed from
docs/notes/quantum_inspire/requirements-qi.txt and named by the QI_PYTHON
environment variable; the repository's own interpreter calls it as a
subprocess. interpreter() reads QI_PYTHON alone, so a host that leaves it
unset runs every gate on its replay path whatever is installed there.

probe() runs the interpreter once per process: it imports qxelarator,
cqasm.v3x (libqasm's analyzer) and opensquirrel and reports their
distribution versions, which must equal the lock's pins. A seeded qxelarator
run and an OpenSquirrel compilation reproduce a retained record byte for
byte only on the pinned build, so a version difference makes the stack
unavailable rather than a source of mismatches.

live(component, fallback) is the branch a check path takes: True when the
probe passed, so the caller runs the live toolchain and compares its output
with the retained record; otherwise it prints one line naming the replay
path and returns False. GOROROBA_QI_REQUIRED=1, which
``ci/run_gates.py --requires qi`` exports, turns an unavailable stack into a
failure, so the CI job that installs the stack never passes on a replay.

The module uses the standard library alone and imports under both
interpreters.
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "docs/notes/quantum_inspire/requirements-qi.txt"
DISTRIBUTIONS = ("qxelarator", "libqasm", "opensquirrel")
PROBE_SECONDS = 180
REQUIRED = "GOROROBA_QI_REQUIRED"
# libqasm 1.2.1 and qxelarator 0.10.0 are SWIG modules whose builtin types
# lack __module__, which Python 3.13 reports as a DeprecationWarning at import.
PROBE = """
import json, platform, warnings
from importlib import metadata
warnings.filterwarnings("ignore", r"builtin type \\w+ has no __module__ attribute", DeprecationWarning)
import qxelarator, cqasm.v3x, opensquirrel
names = {names!r}
print(json.dumps({{"python": platform.python_version(), **{{n: metadata.version(n) for n in names}}}}))
"""


@dataclass(frozen=True)
class Probe:
    interpreter: str | None
    available: bool
    reason: str
    versions: dict[str, str] = field(default_factory=dict)


def interpreter() -> str | None:
    """QI_PYTHON as set in the environment, None when unset or empty."""
    return os.environ.get("QI_PYTHON") or None


def pins(lock: Path = LOCK) -> dict[str, str]:
    """The lock's exact versions of the probed distributions."""
    found = {}
    for line in lock.read_text(encoding="utf-8").splitlines():
        name, separator, version = line.partition("==")
        if separator and name.strip() in DISTRIBUTIONS:
            found[name.strip()] = version.strip()
    missing = sorted(set(DISTRIBUTIONS) - found.keys())
    if missing:
        raise SystemExit(f"{lock.relative_to(ROOT)} pins no {', '.join(missing)}")
    return found


@functools.cache
def probe() -> Probe:
    """One import-and-version run of QI_PYTHON, cached for the life of the process."""
    named = interpreter()
    if named is None:
        return Probe(None, False, "QI_PYTHON is unset")
    try:
        completed = subprocess.run(
            [named, "-I", "-B", "-c", PROBE.format(names=DISTRIBUTIONS)],
            capture_output=True,
            text=True,
            timeout=PROBE_SECONDS,
            check=False,
        )
    except OSError as error:
        return Probe(named, False, f"QI_PYTHON={named} does not start: {error.strerror or error}")
    except subprocess.TimeoutExpired:
        return Probe(named, False, f"QI_PYTHON={named} did not import the stack within {PROBE_SECONDS} s")
    if completed.returncode != 0:
        tail = (completed.stderr.strip().splitlines() or ["no output"])[-1]
        return Probe(named, False, f"QI_PYTHON={named} cannot import the stack: {tail}")
    versions = json.loads(completed.stdout)
    wanted = pins()
    differing = [
        f"{name} {versions[name]} (lock {wanted[name]})" for name in DISTRIBUTIONS if versions[name] != wanted[name]
    ]
    if differing:
        return Probe(named, False, f"QI_PYTHON={named} differs from the lock: {', '.join(differing)}", versions)
    return Probe(named, True, "available", versions)


def required() -> bool:
    return os.environ.get(REQUIRED) == "1"


def live(component: str, fallback: str) -> bool:
    """True when the stack is available; else one line naming the replay path, or a failure under REQUIRED."""
    result = probe()
    if result.available:
        return True
    if required():
        raise SystemExit(f"{component} unavailable under {REQUIRED}=1: {result.reason}")
    print(f"{component} unavailable: {fallback} ({result.reason})")
    return False


def run(arguments: list[str], stdin: str | None = None) -> str:
    """stdout of QI_PYTHON with the given arguments from the repository root; a nonzero exit fails the caller."""
    named = interpreter()
    if named is None:
        raise SystemExit("QI_PYTHON is unset")
    completed = subprocess.run([named, *arguments], cwd=ROOT, input=stdin, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        tail = "\n".join(completed.stderr.splitlines()[-20:])
        raise SystemExit(f"{named} {' '.join(arguments)} exited {completed.returncode}:\n{tail}")
    return completed.stdout
