"""Session setup for the behavioral suite.

Modules under ci/, gororoba_quantum/ and scripts/ import their siblings by
bare name (``import run_gates``), as they do when run as scripts, so the
three directories lead sys.path; no basename repeats across them.

``-n auto`` sizes the xdist pool by parallel.workers(): the affinity and cgroup
quota bound, capped by GOROROBA_WORKERS, which ci/run_gates.py sets to the
gate's allocation for a ``"workers": "all"`` gate. Each test process then runs
in one slot (GOROROBA_WORKERS=1), the environment of the ordinary gates the
tests replace, so a test's own pools never multiply the outer allocation.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
sys.path.insert(1, str(ROOT / "gororoba_quantum"))
sys.path.insert(2, str(ROOT / "scripts"))

import parallel  # noqa: E402


def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    return parallel.workers()


def pytest_configure(config: pytest.Config) -> None:
    # xdist resolves -n auto before configure, so the pool size reads the
    # caller's cap and the workers it spawns inherit the one-slot setting.
    os.environ["GOROROBA_WORKERS"] = "1"
    create_perceval_data_directory()


def create_perceval_data_directory() -> None:
    """Create Perceval's persistent-data directory before xdist spawns its workers.

    perceval.utils.persistent_data.PersistentData tests os.path.exists and then calls os.makedirs on import, and
    reports the FileExistsError of a worker that loses that race as a UserWarning, which filterwarnings = error
    turns into a failure. A directory that already exists leaves every worker's import nothing to create.
    """
    configured = os.environ.get("PCVL_PERSISTENT_PATH")
    if configured:
        Path(configured).mkdir(parents=True, exist_ok=True)
        return
    try:
        from platformdirs import PlatformDirs
    except ImportError:
        return  # without platformdirs no Perceval is installed to import
    Path(PlatformDirs("perceval-quandela", "quandela").user_data_dir).mkdir(parents=True, exist_ok=True)


# The call phase of a test outside the audit marker fails past this many
# seconds. The hosted pull-request runner measures about twice the build
# host's time, and its slowest unmarked test took 4.97 s.
# GOROROBA_TEST_CALL_SECONDS replaces the bound on a contended host; 0 lifts it.
CALL_BUDGET_SECONDS = float(os.environ.get("GOROROBA_TEST_CALL_SECONDS", "10"))


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    if (
        call.when == "call"
        and report.passed
        and CALL_BUDGET_SECONDS > 0
        and call.duration > CALL_BUDGET_SECONDS
        and item.get_closest_marker("audit") is None
    ):
        report.outcome = "failed"
        report.longrepr = (
            f"{item.nodeid} took {call.duration:.2f} s, over the {CALL_BUDGET_SECONDS:.0f} s pull-request budget:"
            " shrink its input or mark it audit with a small unmarked counterpart"
        )
    return report
