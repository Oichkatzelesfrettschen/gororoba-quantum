"""The interpreter, distribution, tool and environment identity a gate result depends on.

ci/premerge_gates.py keys its base-result cache and ci/gate_ledger.py keys
each gate's cached pass by this identity, so a pin, interpreter, PATH tool
or gate-visible variable change invalidates both. Environment values enter
as sha256 digests, so a credential a variable carries (QISKIT_IBM_TOKEN
matches the QISKIT_ prefix) never reaches a cache or ledger file.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

# Gates read these to choose a device, toolchain, live or replay path, thread
# count, SIMD dispatch or warning policy, so each one's value enters the identity.
KEY_PREFIXES = (
    "GOROROBA_",
    "QI_",
    "OQ_",
    "QD_",
    "QISKIT_",
    "PYTHON",
    "OMP_",
    "OPENBLAS_",
    "MKL_",
    "BLIS_",
    "VECLIB_",
    "NUMEXPR_",
    "NPY_",
    "RAYON_",
    "MYPY",
    "MPL",
    "UV_",
    "XDG_",
    "LD_",
    "CUDA_",
)
KEY_VARIABLES = (
    "GLIBC_TUNABLES",
    "PATH",
    "HOME",
    "VIRTUAL_ENV",
    "TMPDIR",
    "KAGGLE_KERNEL_RUN_TYPE",
    "LANG",
    "LC_ALL",
    "TZ",
)
# Credential locations: a gate takes its live or offline path on whether one is
# set, so presence enters the identity while the value and file never do.
PRESENCE_VARIABLES = ("IQM_TOKENS_FILE", "OPENQUANTUM_SDK_KEY", "ANU_QRNG_KEY_FILE", "QUANDELA_TOKEN_FILE")
# ci/install_pins.sh applies these to installed distributions whose name and
# version the interpreter identity already records.
PATCHES = Path(__file__).resolve().parent / "patches"
# The read tracer's own variables name a per-run scratch directory; a gate
# observes nothing through them, so they stay out of the identity.
TRACE_VARIABLES = ("GOROROBA_READ_TRACE", "GOROROBA_READ_TRACE_ROOT", "GOROROBA_READ_TRACE_PYTHONS")
# Gates run these from PATH (ci/pinned_tool.py prefers an installed ruff or
# mypy at its pin and otherwise runs the pin through uv), so each one's
# resolved file identity enters the key.
KEY_TOOLS = ("ruff", "mypy", "uv", "shellcheck", "git", "sha256sum", "rocq")
# These name interpreters of the separate service stacks; their installed
# distributions enter the key beside the path.
KEY_INTERPRETERS = ("QI_PYTHON", "OQ_PYTHON", "QD_PYTHON")
DISTRIBUTIONS = (
    "import importlib.metadata as m, json, sys; "
    "print(json.dumps([sys.version, sorted({(d.metadata['Name'] or '', d.version) for d in m.distributions()})]))"
)


def interpreter_identity(python: str) -> list[Any]:
    """The interpreter's real path, version and installed distributions as a gate run under it sees them."""
    completed = subprocess.run(
        [python, "-c", DISTRIBUTIONS], cwd=tempfile.gettempdir(), capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise SystemExit(f"{python} cannot list its distributions:\n{completed.stderr.strip()}")
    return [os.path.realpath(python), json.loads(completed.stdout)]


def tool_identity(name: str, path: str | None = None) -> list[Any] | None:
    """The resolved path, size and modification time of a PATH tool, or None when PATH lacks it."""
    found = shutil.which(name, path=path)
    if found is None:
        return None
    real = os.path.realpath(found)
    status = os.stat(real)
    return [real, status.st_size, status.st_mtime_ns]


def keyed(name: str) -> bool:
    return (name.startswith(KEY_PREFIXES) or name in KEY_VARIABLES) and name not in TRACE_VARIABLES


def identity(environment: Mapping[str, str], python: str, replay: Mapping[str, str]) -> dict[str, Any]:
    """The components naming the host a gate runs on: interpreters, tools and keyed variables."""
    variables = {
        name: hashlib.sha256(value.encode()).hexdigest() for name, value in sorted(environment.items()) if keyed(name)
    }
    services = {
        name: interpreter_identity(environment[name])
        for name in KEY_INTERPRETERS
        if environment.get(name) and os.access(environment[name], os.X_OK)
    }
    patches = {
        path.relative_to(PATCHES).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PATCHES.rglob("*"))
        if path.is_file()
    }
    return {
        "python": interpreter_identity(python),
        "patches": patches,
        "present": {name: bool(environment.get(name)) for name in PRESENCE_VARIABLES},
        "replay": {variable: interpreter_identity(path) for variable, path in sorted(replay.items())},
        "environment": variables,
        "services": services,
        "tools": {name: tool_identity(name, environment.get("PATH")) for name in KEY_TOOLS},
    }
