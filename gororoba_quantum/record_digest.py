"""The retained measurement records whose ``--check`` binds their bytes by sha256.

A calibration reading, a timing, a sampled GPU counter or a seeded count taken at acquisition time has
no offline recomputation, so a ``--check`` that rebuilds only the derived fields passes a record whose
raw value changed. ``require_retained`` closes that gap: it requires the file's sha256 to equal that of
a retained record in RETAINED, so a changed byte anywhere in the file fails the check. A new acquisition
adds its record's digest to RETAINED in the change that retains it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# sha256 of the file's bytes -> its repository path.
RETAINED: dict[str, str] = {
    "2417655318d2d61de2c97361c42d3e0eba769f7613473b8df38b5e1cb9900346": "docs/evidence/calibration/ibm_kingston.json",
    "a02433aa2b4611a0e215ffb32c48c35d75d47ea9ef0f52987afbf8c5d8697805": (
        "results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config/output/output/aer_gpu_probe.json"
    ),
    "34d186f02b7a8b8b01aa855fe656961ce88b53e27f0cac99ef4609b97e9db082": (
        "docs/evidence/aer_gpu_configuration/result.json"
    ),
    "1615733e29819adc3dbaa0aacc5ed71061c29c6ed2effeef86ecbe425e21fab2": (
        "results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config/output/output/aer_gpu_probe.json"
    ),
    "90af2331f9a6183533eec1b2f077a1e13c640ec2fd70513acf601a87565f3ffc": (
        "results/kaggle/2026-10-18T041945Z-gororoba-ghost-branching-t4/output/output/ghost_branching_benchmark.json"
    ),
    "24aafaa7bd5af776bec287e04feae4684ad2a264a3e89bcd4396dc45a71a26ab": (
        "docs/evidence/ghost_error_scale_branching/benchmark-host.json"
    ),
}


def require_retained(path: Path) -> str:
    """The sha256 of PATH's bytes; raises ValueError unless it equals a retained record's."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest not in RETAINED:
        raise ValueError(
            f"{path}: sha256 {digest} matches no retained record; a changed value or an unregistered record"
        )
    return digest
