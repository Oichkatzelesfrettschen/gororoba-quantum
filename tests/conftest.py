"""Session setup for the behavioral suite.

ci/ modules import their siblings by bare name (``import run_gates``), as they
do when run as scripts, so ci/ leads sys.path. run_gates itself places
gororoba_quantum/ on the path for parallel.py.

``-n auto`` sizes the xdist pool by parallel.workers(): the affinity and cgroup
quota bound, capped by GOROROBA_WORKERS, which ci/run_gates.py sets to the
gate's allocation for a ``"workers": "all"`` gate. Each test process then runs
in one slot (GOROROBA_WORKERS=1), the environment of the ordinary gates the
tests replace, so a test's own pools never multiply the outer allocation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
sys.path.insert(1, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402


def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    return parallel.workers()


def pytest_configure(config: pytest.Config) -> None:
    # xdist resolves -n auto before configure, so the pool size reads the
    # caller's cap and the workers it spawns inherit the one-slot setting.
    os.environ["GOROROBA_WORKERS"] = "1"
