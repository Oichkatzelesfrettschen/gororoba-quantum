"""The pool's worker count stays within the memory the process reports, and a pooled map keeps the serial verdicts."""

from __future__ import annotations

import pickle
from pathlib import Path

import pytest
import research_state

import parallel

GIB = 2**30


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _synthetic_host(tmp_path: Path, available_kib: int, limits: dict[str, tuple[str, int]]) -> dict[str, Path]:
    """A /proc/meminfo, /proc/self/cgroup and cgroup tree; limits maps a cgroup path to (memory.max, memory.current)."""
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(f"MemTotal: 99999999 kB\nMemAvailable: {available_kib} kB\n")
    proc_cgroup = tmp_path / "cgroup"
    proc_cgroup.write_text("0::/a/b\n")
    root = tmp_path / "fs"
    for path, (limit, current) in limits.items():
        node = root / path
        node.mkdir(parents=True)
        (node / "memory.max").write_text(f"{limit}\n")
        (node / "memory.current").write_text(f"{current}\n")
    return {"proc_cgroup": proc_cgroup, "cgroup_root": root, "meminfo": meminfo}


def test_available_memory_is_the_tightest_headroom(tmp_path: Path) -> None:
    host = _synthetic_host(tmp_path, 40 * GIB // 1024, {"a/b": ("max", 0), "a": (str(16 * GIB), 4 * GIB)})
    _require(parallel.available_memory(**host) == 12 * GIB, "the ancestor limit's headroom did not bind")
    host = _synthetic_host(tmp_path / "host", 10 * GIB // 1024, {"a": (str(16 * GIB), 0)})
    _require(parallel.available_memory(**host) == 10 * GIB, "MemAvailable did not bind under a looser limit")
    missing = tmp_path / "none"
    _require(parallel.available_memory(missing, missing, missing) is None, "an absent source reported a figure")


def test_worker_count_fits_the_reported_memory() -> None:
    worker = research_state.SELF_TEST_WORKER_BYTES
    _require(parallel.memory_workers(worker, 16 * GIB) == 16 * GIB // worker, "16 GiB admits the wrong count")
    _require(parallel.memory_workers(worker, worker - 1) == 1, "a small limit must still leave one worker")
    _require(parallel.memory_workers(worker, None) is None, "an unknown limit must not cap")


def test_ordered_map_requests_no_more_workers_than_fit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "4")
    parallel._shutdown()
    try:
        seen = parallel.ordered_map(
            parallel._process_budget, list(range(16)), min_items=1, worker_bytes=GIB, available_bytes=2 * GIB
        )
        _require(len({pid for _, pid, _, _ in seen}) <= 2, "the pool used more workers than the injected limit fits")
    finally:
        parallel._shutdown()


def test_two_workers_return_the_serial_verdicts(monkeypatch: pytest.MonkeyPatch) -> None:
    items = list(range(24))
    serial = [parallel._square(item) for item in items]
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    parallel._shutdown()
    try:
        pooled = parallel.ordered_map(parallel._square, items, min_items=1, worker_bytes=GIB, available_bytes=8 * GIB)
    finally:
        parallel._shutdown()
    _require(pooled == serial, "the pooled list differs from the serial list")


def test_case_verdict_pickles_without_loaded_state_and_cases_are_unique() -> None:
    registry = {"schema": "synthetic"}
    verdict = pickle.loads(pickle.dumps(research_state.CaseVerdict(registry)))
    _require(verdict._registry == registry and verdict._loaded is None, "a pickled verdict carried loaded state")
    names = [name for name, _, _ in research_state._case_specs()]
    _require(len(names) == len(set(names)) and len(names) > 1, "self-test case names repeat")
