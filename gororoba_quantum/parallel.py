"""Order-preserving process-parallel map over CPU-bound, picklable work.

Workers start under the spawn method on every platform: forking a process
that already runs Aer or rustworkx thread pools can deadlock a child on a lock
another thread held, while spawn starts each worker from a fresh interpreter.
One pool serves the whole process, so the interpreter and import start-up of
its workers is paid once. The callable travels as pickled bytes keyed by their
sha256; each worker unpickles a given callable once and reuses it for every
later chunk, so a large callable such as a Target with its circuits costs one
deserialization per worker. Results come back in input order, so a parallel
run returns exactly what the serial loop returns.

GOROROBA_WORKERS caps the worker count; 1 runs serially in-process. The
default is the CPU count available to this process.
"""

from __future__ import annotations

import atexit
import hashlib
import math
import multiprocessing
import os
import pickle
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

# Below this many fine-grained items the work does not repay the
# inter-process transfer; a caller whose items each run for seconds passes a
# smaller min_items.
MIN_PARALLEL_ITEMS = 64
# Chunks per worker: enough to balance uneven item costs, few enough that the
# per-chunk callable transfer stays small against the work.
CHUNKS_PER_WORKER = 4
# Callables each worker keeps deserialized; one pipeline stage reuses one.
WORKER_CACHE_SIZE = 4

_pool: ProcessPoolExecutor | None = None
_pool_size = 0
_worker_cache: dict[str, Callable[[Any], Any]] = {}


CGROUP_V2_CPU_MAX = Path("/sys/fs/cgroup/cpu.max")
CGROUP_V1_CPU_QUOTA = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
CGROUP_V1_CPU_PERIOD = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")


def workers() -> int:
    """The worker count: GOROROBA_WORKERS when set, else the CPUs available to this process.

    The affinity mask counts the CPUs the scheduler may use; a container's
    CPU quota (cgroup v2 cpu.max, cgroup v1 cfs_quota_us / cfs_period_us)
    can grant fewer, so the smaller of the two is the count, rounded up to a
    whole worker.
    """
    configured = os.environ.get("GOROROBA_WORKERS")
    if configured is not None:
        count = int(configured)
        if count < 1:
            raise ValueError(f"GOROROBA_WORKERS must be a positive integer, got {configured!r}")
        return count
    # sched_getaffinity honors CPU pinning where the platform provides it
    # (Linux); cpu_count covers macOS and Windows.
    if hasattr(os, "sched_getaffinity"):
        available = len(os.sched_getaffinity(0)) or 1
    else:
        available = os.cpu_count() or 1
    quota = cgroup_cpu_quota()
    return max(1, min(available, math.ceil(quota))) if quota is not None else available


def cgroup_cpu_quota(
    v2_max: Path = CGROUP_V2_CPU_MAX, v1_quota: Path = CGROUP_V1_CPU_QUOTA, v1_period: Path = CGROUP_V1_CPU_PERIOD
) -> float | None:
    """CPUs the enclosing cgroup grants, or None without a quota or outside a cgroup.

    cgroup v2 cpu.max reads "QUOTA PERIOD" in microseconds, "max" for no
    quota; cgroup v1 keeps the quota and period in two files, -1 for no quota.
    A malformed or unreadable file counts as no quota.
    """
    try:
        if v2_max.is_file():
            quota_text, period_text = v2_max.read_text().split()
            if quota_text == "max":
                return None
            quota, period = int(quota_text), int(period_text)
        elif v1_quota.is_file() and v1_period.is_file():
            quota, period = int(v1_quota.read_text()), int(v1_period.read_text())
        else:
            return None
    except (OSError, ValueError):
        return None
    if quota <= 0 or period <= 0:
        return None
    return quota / period


def _executor(count: int) -> ProcessPoolExecutor:
    global _pool, _pool_size
    if _pool is None or _pool_size != count:
        if _pool is not None:
            _pool.shutdown()
        _pool = ProcessPoolExecutor(count, mp_context=multiprocessing.get_context("spawn"))
        _pool_size = count
    return _pool


@atexit.register
def _shutdown() -> None:
    global _pool
    if _pool is not None:
        _pool.shutdown()
        _pool = None


def _run_chunk(key: str, payload: bytes, chunk: list[Any]) -> list[Any]:
    function = _worker_cache.get(key)
    if function is None:
        function = pickle.loads(payload)
        if len(_worker_cache) >= WORKER_CACHE_SIZE:
            _worker_cache.pop(next(iter(_worker_cache)))
        _worker_cache[key] = function
    return [function(item) for item in chunk]


def ordered_map(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = MIN_PARALLEL_ITEMS) -> list[Any]:
    """[function(item) for item in items], spread over the process pool.

    function and every item must pickle; function must be a module-level
    callable or an instance of a module-level class.
    """
    count = min(workers(), len(items))
    if count <= 1 or len(items) < min_items:
        return [function(item) for item in items]
    payload = pickle.dumps(function)
    key = hashlib.sha256(payload).hexdigest()
    size = -(-len(items) // (CHUNKS_PER_WORKER * count))
    chunks = [list(items[start : start + size]) for start in range(0, len(items), size)]
    pool = _executor(count)
    futures = [pool.submit(_run_chunk, key, payload, chunk) for chunk in chunks]
    return [result for future in futures for result in future.result()]
