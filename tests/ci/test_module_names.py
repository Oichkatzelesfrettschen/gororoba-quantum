"""tests/conftest.py puts ci/, gororoba_quantum/ and scripts/ on sys.path, so a bare import names one file
only while no module basename repeats across the three directories.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_basename_repeats_across_import_roots() -> None:
    names = Counter(
        path.stem for directory in ("ci", "gororoba_quantum", "scripts") for path in (ROOT / directory).glob("*.py")
    )
    repeated = sorted(name for name, count in names.items() if count > 1)
    if repeated:
        raise AssertionError(f"module names repeat across ci/, gororoba_quantum/ and scripts/: {repeated}")
