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
default is half the logical CPUs available to this process, rounded down
with a minimum of one.
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


PROC_SELF_CGROUP = Path("/proc/self/cgroup")
CGROUP_ROOT = Path("/sys/fs/cgroup")


def workers() -> int:
    """The worker count: GOROROBA_WORKERS when set, else default_threads()."""
    configured = os.environ.get("GOROROBA_WORKERS")
    if configured is not None:
        count = int(configured)
        if count < 1:
            raise ValueError(f"GOROROBA_WORKERS must be a positive integer, got {configured!r}")
        return count
    return default_threads()


def default_threads() -> int:
    """Half the available logical CPU budget, rounded down with a minimum of one.

    Affinity and cgroup quotas bound available_cpus(). Sharing that budget
    between local quantum preparation and other workstation work keeps the
    process-pool and Aer defaults consistent. Explicit worker and simulation
    thread counts retain their independent overrides.
    """
    return max(1, available_cpus() // 2)


def available_cpus() -> int:
    """The CPUs available to this process.

    The affinity mask counts the CPUs the scheduler may use; the process's
    cgroup hierarchy can grant fewer through a CPU quota on its own cgroup or
    any ancestor, so the smaller of the two is the count, rounded up to a
    whole CPU.
    """
    # sched_getaffinity honors CPU pinning where the platform provides it
    # (Linux); cpu_count covers macOS and Windows.
    if hasattr(os, "sched_getaffinity"):
        available = len(os.sched_getaffinity(0)) or 1
    else:
        available = os.cpu_count() or 1
    quota = cgroup_cpu_quota()
    return max(1, min(available, math.ceil(quota))) if quota is not None else available


def cgroup_cpu_quota(proc_cgroup: Path = PROC_SELF_CGROUP, cgroup_root: Path = CGROUP_ROOT) -> float | None:
    """CPUs the process's cgroup hierarchy grants: the tightest quota on its cgroup or any ancestor, or None.

    /proc/self/cgroup names the process's cgroup in each hierarchy. A cgroup
    v2 line "0::/path" places cpu.max ("QUOTA PERIOD" in microseconds, "max"
    for none) under cgroup_root/path and in every ancestor directory up to the
    root. A cgroup v1 line whose controllers include cpu places
    cpu.cfs_quota_us (-1 for none) and cpu.cfs_period_us under the cpu
    controller mount, cgroup_root/cpu or cgroup_root/cpu,cpuacct. Quotas on
    ancestors bind the descendant, so the minimum over the walk is the grant.
    An unreadable or malformed file counts as no quota at that node.
    """
    try:
        lines = proc_cgroup.read_text().splitlines()
    except OSError:
        return None
    quotas: list[float] = []
    for line in lines:
        fields = line.split(":", 2)
        if len(fields) != 3:
            continue
        hierarchy, controllers, path = fields
        if hierarchy == "0" and controllers == "":
            for node in _cgroup_ancestors(cgroup_root, path):
                quota = _cgroup_v2_quota(node / "cpu.max")
                if quota is not None:
                    quotas.append(quota)
        elif "cpu" in controllers.split(","):
            for mount in (cgroup_root / "cpu", cgroup_root / "cpu,cpuacct"):
                if not mount.is_dir():
                    continue
                for node in _cgroup_ancestors(mount, path):
                    quota = _cgroup_v1_quota(node / "cpu.cfs_quota_us", node / "cpu.cfs_period_us")
                    if quota is not None:
                        quotas.append(quota)
                break
    return min(quotas) if quotas else None


def _cgroup_ancestors(mount: Path, path: str) -> list[Path]:
    """The cgroup directory named by path under mount, then each ancestor up to mount."""
    parts = [part for part in path.strip("/").split("/") if part]
    return [mount.joinpath(*parts[:depth]) for depth in range(len(parts), -1, -1)]


def _cgroup_v2_quota(cpu_max: Path) -> float | None:
    try:
        quota_text, period_text = cpu_max.read_text().split()
        if quota_text == "max":
            return None
        quota, period = int(quota_text), int(period_text)
    except (OSError, ValueError):
        return None
    return quota / period if quota > 0 and period > 0 else None


def _cgroup_v1_quota(quota_file: Path, period_file: Path) -> float | None:
    try:
        quota, period = int(quota_file.read_text()), int(period_file.read_text())
    except (OSError, ValueError):
        return None
    return quota / period if quota > 0 and period > 0 else None


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
