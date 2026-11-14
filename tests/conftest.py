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

import importlib.util
import os
import platform
import sys
from collections.abc import Callable, Generator, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
sys.path.insert(1, str(ROOT / "gororoba_quantum"))
sys.path.insert(2, str(ROOT / "scripts"))

import math_sources  # noqa: E402
import parallel  # noqa: E402

PLATFORM = f"{sys.platform}-{platform.machine()}"


def _platform_expectations() -> dict[str, tuple[frozenset[str], str]]:
    """EXPECTED of tests/platform_expectations.py, loaded by path: --import-mode=importlib keeps tests/ off sys.path."""
    spec = importlib.util.spec_from_file_location(
        "platform_expectations", Path(__file__).with_name("platform_expectations.py")
    )
    if spec is None or spec.loader is None:
        raise ImportError("tests/platform_expectations.py has no loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected: dict[str, tuple[frozenset[str], str]] = module.EXPECTED
    return expected


EXPECTED = _platform_expectations()


def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    return parallel.workers()


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark each test tests/platform_expectations.py lists for this platform as a strict expected failure.

    The hook runs before -k and -m deselect anything, so a listed ID whose file was collected but which names no
    collected test (renamed, removed or mistyped) stops the session instead of losing its marker in silence. A run
    that names single tests (an argument holding "::") collects part of a file and skips that check."""
    collected = {item.nodeid for item in items}
    if not any("::" in str(argument) for argument in config.args):
        files = {nodeid.partition("::")[0] for nodeid in collected}
        stale = sorted(n for n in EXPECTED if n.partition("::")[0] in files and n not in collected)
        if stale:
            raise pytest.UsageError(f"tests/platform_expectations.py names tests that do not exist: {stale}")
    for item in items:
        expected = EXPECTED.get(item.nodeid)
        if expected is not None and PLATFORM in expected[0]:
            item.add_marker(pytest.mark.xfail(strict=True, reason=f"{PLATFORM}: {expected[1]}"))


def pytest_configure(config: pytest.Config) -> None:
    # xdist resolves -n auto before configure, so the pool size reads the
    # caller's cap and the workers it spawns inherit the one-slot setting.
    os.environ["GOROROBA_WORKERS"] = "1"
    create_perceval_data_directory()


def create_perceval_data_directory() -> None:
    """Create Perceval's persistent-data directory before xdist spawns its workers.

    perceval.utils.persistent_data.PersistentData tests os.path.exists and then calls os.makedirs on import, and
    reports the FileExistsError of a worker that loses that race as a UserWarning, which filterwarnings = error
    turns into a failure. A directory that already exists leaves every worker's import nothing to create. Importing
    perceval also creates the sub-directory perceval.runtime.legacy.job_group.JGRP_DIR_NAME the same way, so it is
    created here too.
    """
    configured = os.environ.get("PCVL_PERSISTENT_PATH")
    if configured:
        root = Path(configured)
    else:
        try:
            from platformdirs import PlatformDirs
        except ImportError:
            return  # without platformdirs no Perceval is installed to import
        root = Path(PlatformDirs("perceval-quandela", "quandela").user_data_dir)
    (root / "job_group").mkdir(parents=True, exist_ok=True)


# The call phase of a test outside the audit marker targets this many seconds
# and fails only past CALL_BUDGET_TOLERANCE times it, so hosted-runner jitter
# around the target never fails a pull request. The hosted pull-request runner
# measures about twice the build host's time. GOROROBA_TEST_CALL_SECONDS
# replaces the target on a contended host; 0 lifts the bound.
CALL_BUDGET_SECONDS = float(os.environ.get("GOROROBA_TEST_CALL_SECONDS", "10"))
CALL_BUDGET_TOLERANCE = 1.5


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    if (
        call.when == "call"
        and report.passed
        and CALL_BUDGET_SECONDS > 0
        and call.duration > CALL_BUDGET_SECONDS * CALL_BUDGET_TOLERANCE
        and item.get_closest_marker("audit") is None
    ):
        report.outcome = "failed"
        report.longrepr = (
            f"{item.nodeid} took {call.duration:.2f} s, over {CALL_BUDGET_TOLERANCE:g} times the"
            f" {CALL_BUDGET_SECONDS:.0f} s pull-request budget:"
            " shrink its input or mark it audit with a small unmarked counterpart"
        )
    return report


class PoolSpy:
    """What a test with forced_pool ran through parallel.ordered_map: the (callable class, item count) of each map
    and the pool sizes that were requested from the executor."""

    def __init__(self) -> None:
        self.maps: list[tuple[str, int]] = []
        self.pools: list[int] = []


@pytest.fixture
def forced_pool(monkeypatch: pytest.MonkeyPatch) -> PoolSpy:
    """Send every parallel.ordered_map through the spawned process pool, whatever its size.

    Each test runs in one CPU slot (pytest_configure sets GOROROBA_WORKERS=1) and the committed pathion series are
    below parallel.MIN_PARALLEL_ITEMS, so their maps run inline. This fixture reports two workers and passes
    min_items=1 to the real ordered_map, which pickles the callable and its items and runs the chunks in spawned
    workers; the returned PoolSpy records the maps and pool requests so a test can require that the pool ran."""
    spy = PoolSpy()
    real_map = parallel.ordered_map
    real_executor = parallel._executor

    def ordered_map(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 1) -> list[Any]:
        spy.maps.append((type(function).__name__, len(items)))
        return real_map(function, items, min_items=1)

    def executor(count: int) -> ProcessPoolExecutor:
        spy.pools.append(count)
        return real_executor(count)

    monkeypatch.setattr(parallel, "workers", lambda: 2)
    monkeypatch.setattr(parallel, "ordered_map", ordered_map)
    monkeypatch.setattr(parallel, "_executor", executor)
    return spy


@pytest.fixture
def math_source() -> Callable[[str], Path]:
    """The path of a Rocq source of gororoba-math (``NAME.v`` of rocq/quantum) at the commit of ci/gororoba_math.pin.

    A test that reads it runs on demand (``audit``), since the pull-request suite reaches no other repository. An
    unset GOROROBA_MATH skips the test unless GOROROBA_MATH_REQUIRED=1; a checkout off the pin fails it.
    """

    def resolve(name: str) -> Path:
        required = os.environ.get(math_sources.REQUIRED_VARIABLE) == "1"
        if not os.environ.get(math_sources.ENVIRONMENT_VARIABLE) and not required:
            pytest.skip(f"{math_sources.ENVIRONMENT_VARIABLE} is unset")
        try:
            math = math_sources.checkout(os.environ, ROOT)
            return math_sources.resolve_reference(math_sources.reference_for(name), math)
        except math_sources.MathSourcesError as error:
            pytest.fail(str(error))

    return resolve
