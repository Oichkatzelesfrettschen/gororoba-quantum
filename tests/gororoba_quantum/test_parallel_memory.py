"""The pool's worker count stays within the memory the process reports, and a pooled map keeps the serial verdicts."""

from __future__ import annotations

import os
import pickle
import time
from pathlib import Path

import pytest
import research_state

import parallel
import parallel_memory

GIB = 2**30


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _synthetic_host(tmp_path: Path, available_kib: int, limits: dict[str, tuple[str, int | None]]) -> dict[str, Path]:
    """A /proc/meminfo, /proc/self/cgroup and cgroup tree; limits maps a cgroup path to (memory.max, memory.current).

    A current of None leaves memory.current absent; the empty path is the root node.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(f"MemTotal: 99999999 kB\nMemAvailable: {available_kib} kB\n")
    proc_cgroup = tmp_path / "cgroup"
    proc_cgroup.write_text("0::/a/b\n")
    root = tmp_path / "fs"
    for path, (limit, current) in limits.items():
        node = root / path
        node.mkdir(parents=True, exist_ok=True)
        (node / "memory.max").write_text(f"{limit}\n")
        if current is not None:
            (node / "memory.current").write_text(f"{current}\n")
    return {"proc_cgroup": proc_cgroup, "cgroup_root": root, "meminfo": meminfo}


def _available(tmp_path: Path, name: str, available_gib: int, limits: dict[str, tuple[str, int | None]]) -> int | None:
    return parallel_memory.available_memory(**_synthetic_host(tmp_path / name, available_gib * GIB // 1024, limits))


def test_available_memory_is_the_tightest_headroom(tmp_path: Path) -> None:
    both = _available(tmp_path, "both", 40, {"a/b": ("max", 0), "a": (str(16 * GIB), 4 * GIB)})
    _require(both == 12 * GIB, "the ancestor limit's headroom did not bind")
    looser = _available(tmp_path, "looser", 10, {"a": (str(16 * GIB), 0)})
    _require(looser == 10 * GIB, "MemAvailable did not bind under a looser limit")
    root = _available(tmp_path, "root", 40, {"": (str(8 * GIB), 3 * GIB), "a/b": ("max", 0)})
    _require(root == 5 * GIB, "the limit on the root node did not bind")
    over = _available(tmp_path, "over", 40, {"a": (str(4 * GIB), 6 * GIB)})
    _require(over == 0, "use above the limit did not leave no room")
    no_current = _available(tmp_path, "no-current", 10, {"a/b": (str(2 * GIB), None), "a": (str(4 * GIB), GIB)})
    _require(no_current == 3 * GIB, "a leaf without memory.current hid the ancestor limit")
    malformed = _available(tmp_path, "malformed", 10, {"a/b": ("lots", 0), "a": (str(4 * GIB), GIB)})
    _require(malformed == 3 * GIB, "a malformed leaf memory.max hid the ancestor limit")
    missing = tmp_path / "none"
    _require(parallel_memory.available_memory(missing, missing, missing) is None, "an absent source reported a figure")


def test_worker_count_fits_the_reported_memory() -> None:
    worker = research_state.SELF_TEST_WORKER_BYTES
    _require(parallel_memory.memory_workers(worker, 16 * GIB) == 16 * GIB // worker, "16 GiB admits the wrong count")
    _require(parallel_memory.memory_workers(worker, 3 * worker) == 3, "three workers' room admits the wrong count")
    _require(parallel_memory.memory_workers(worker, worker - 1) == 1, "a small limit must still leave one worker")
    _require(parallel_memory.memory_workers(worker, None) is None, "an unknown limit must not cap")


def _pid_after_pause(item: int) -> tuple[int, int]:
    time.sleep(0.05)
    return item * item, os.getpid()


def _record_pool_sizes(monkeypatch: pytest.MonkeyPatch) -> list[tuple[int, int]]:
    """Wrap parallel._executor; each entry is (the count requested, the worker limit of the pool returned)."""
    sizes: list[tuple[int, int]] = []
    real = parallel._executor

    def recording(count: int) -> parallel.ProcessPoolExecutor:
        pool = real(count)
        limit: int = pool._max_workers  # type: ignore[attr-defined]
        sizes.append((count, limit))
        return pool

    monkeypatch.setattr(parallel, "_executor", recording)
    return sizes


def _four_cpus(monkeypatch: pytest.MonkeyPatch) -> None:
    """Four CPUs and no inherited cap; the memory cap travels through GOROROBA_WORKERS, which workers() reads."""
    monkeypatch.delenv("GOROROBA_WORKERS", raising=False)
    monkeypatch.setattr(parallel, "available_cpus", lambda: 4)


def test_bounded_map_requests_no_more_workers_than_fit(monkeypatch: pytest.MonkeyPatch) -> None:
    _four_cpus(monkeypatch)
    sizes = _record_pool_sizes(monkeypatch)
    parallel._shutdown()
    try:
        seen = parallel_memory.bounded_ordered_map(
            parallel._square, list(range(16)), GIB, available_bytes=2 * GIB, min_items=1
        )
        monkeypatch.setattr(parallel_memory, "available_memory", lambda: None)
        uncapped = parallel_memory.bounded_ordered_map(parallel._square, list(range(16)), GIB, min_items=1)
    finally:
        parallel._shutdown()
    _require(seen == [item * item for item in range(16)], "the capped pool returned the wrong list")
    _require(uncapped == seen, "the uncapped pool returned the wrong list")
    _require(sizes[:1] == [(2, 2)], f"two workers' room must build a pool of two, got {sizes}")
    _require(sizes[1:] == [(4, 4)], f"an unknown limit must leave the process budget, got {sizes}")


def test_two_workers_return_the_serial_verdicts(monkeypatch: pytest.MonkeyPatch) -> None:
    _four_cpus(monkeypatch)
    items = list(range(24))
    serial = [item * item for item in items]
    parallel._shutdown()
    try:
        pooled = parallel_memory.bounded_ordered_map(
            _pid_after_pause, items, GIB, available_bytes=2 * GIB, min_items=1
        )
    finally:
        parallel._shutdown()
    _require([value for value, _ in pooled] == serial, "the pooled list differs from the serial list")
    pids = {pid for _, pid in pooled}
    _require(os.getpid() not in pids and len(pids) == 2, f"two worker processes must share the chunks, got {pids}")


def _cap_seen(item: int) -> str | None:
    return os.environ.get("GOROROBA_WORKERS")


def _fails(item: int) -> int:
    raise ValueError("stop")


def test_worker_cap_is_set_for_the_call_and_restored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parallel, "available_cpus", lambda: 4)
    monkeypatch.delenv("GOROROBA_WORKERS", raising=False)
    during = parallel_memory.bounded_ordered_map(_cap_seen, [0, 1], GIB, available_bytes=2 * GIB, min_items=99)
    _require(during == ["2", "2"], f"the call did not run under the memory cap, got {during}")
    _require("GOROROBA_WORKERS" not in os.environ, "an absent GOROROBA_WORKERS did not stay absent")
    monkeypatch.setenv("GOROROBA_WORKERS", "3")
    during = parallel_memory.bounded_ordered_map(_cap_seen, [0], GIB, available_bytes=2 * GIB, min_items=99)
    _require(during == ["2"], f"a looser caller cap displaced the memory cap, got {during}")
    _require(os.environ.get("GOROROBA_WORKERS") == "3", "a present GOROROBA_WORKERS was not restored")
    tighter = parallel_memory.bounded_ordered_map(_cap_seen, [0], GIB, available_bytes=9 * GIB, min_items=99)
    _require(tighter == ["3"], f"the memory cap raised the caller's cap, got {tighter}")
    with pytest.raises(ValueError, match="stop"):
        parallel_memory.bounded_ordered_map(_fails, [0], GIB, available_bytes=GIB, min_items=99)
    _require(os.environ.get("GOROROBA_WORKERS") == "3", "a failing call left GOROROBA_WORKERS changed")


def test_case_verdict_pickles_without_loaded_state_and_cases_are_unique() -> None:
    registry = {"schema": "synthetic"}
    verdict = research_state.CaseVerdict(registry)
    vars(verdict).update(_loaded=("sentinel",), _specs=["sentinel"])
    restored = pickle.loads(pickle.dumps(verdict))
    _require(restored._registry == registry, "a pickled verdict lost its registry")
    _require(restored._loaded is None and restored._specs is None, "a pickled verdict carried loaded state")
    names = [name for name, _, _ in research_state._case_specs()]
    _require(len(names) == len(set(names)) and len(names) > 1, "self-test case names repeat")
