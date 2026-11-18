"""Memory-bounded ordered_map: the pool is sized to the memory the process can still allocate.

bounded_ordered_map(function, items, worker_bytes) divides available_memory() by the resident
bytes one worker needs (memory_workers) and runs parallel.ordered_map with the process budget
capped at that count. The cap travels through GOROROBA_WORKERS, which parallel.workers() reads
and which can only lower the CPU-derived budget; the variable is set for the one call and
restored afterwards, so a variable that was absent stays absent. available_memory() is a
snapshot of MemAvailable and the room under every cgroup memory limit: it keeps no reserve for
the parent process or for growth after the snapshot, so worker_bytes carries that margin.
Both functions read the cgroup hierarchy through parallel._cgroup_ancestors, the walk that
cgroup_cpu_quota already uses.
"""

from __future__ import annotations

import contextlib
import os
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any

import parallel

PROC_MEMINFO = Path("/proc/meminfo")
WORKERS_VARIABLE = "GOROROBA_WORKERS"


def available_memory(
    proc_cgroup: Path = parallel.PROC_SELF_CGROUP,
    cgroup_root: Path = parallel.CGROUP_ROOT,
    meminfo: Path = PROC_MEMINFO,
) -> int | None:
    """Bytes this process can still allocate: the smallest of MemAvailable and the room under each cgroup limit.

    A cgroup v2 line "0::/path" places memory.max ("max" for none) and memory.current under
    cgroup_root/path and in every ancestor up to the root; the room at a node is its limit minus
    its current use, and a limit on an ancestor binds the descendant. An unreadable or
    malformed file contributes nothing, and None means no source reported a figure.
    """
    room: list[int] = []
    try:
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemAvailable:"):
                room.append(int(line.split()[1]) * 1024)
    except (OSError, ValueError, IndexError):
        pass
    try:
        lines = proc_cgroup.read_text().splitlines()
    except OSError:
        lines = []
    for line in lines:
        fields = line.split(":", 2)
        if len(fields) == 3 and fields[0] == "0" and fields[1] == "":
            for node in parallel._cgroup_ancestors(cgroup_root, fields[2]):
                try:
                    limit_text = (node / "memory.max").read_text().strip()
                    if limit_text != "max":
                        room.append(max(0, int(limit_text) - int((node / "memory.current").read_text())))
                except (OSError, ValueError):
                    continue
    return min(room) if room else None


def memory_workers(worker_bytes: int, available: int | None) -> int | None:
    """Workers of worker_bytes each that fit in available bytes, at least one; None when available is unknown."""
    if available is None:
        return None
    return max(1, available // worker_bytes)


@contextlib.contextmanager
def _worker_cap(count: int) -> Iterator[None]:
    """GOROROBA_WORKERS set to count for the block; the previous value, or its absence, returns on exit."""
    previous = os.environ.get(WORKERS_VARIABLE)
    os.environ[WORKERS_VARIABLE] = str(count)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(WORKERS_VARIABLE, None)
        else:
            os.environ[WORKERS_VARIABLE] = previous


def bounded_ordered_map(
    function: Callable[[Any], Any],
    items: Sequence[Any],
    worker_bytes: int,
    available_bytes: int | None = None,
    min_items: int = parallel.MIN_PARALLEL_ITEMS,
) -> list[Any]:
    """parallel.ordered_map with at most as many workers as fit in memory, worker_bytes each.

    available_bytes defaults to available_memory(); with no figure the process budget stands.
    A worker_bytes below one byte raises ValueError.
    """
    if worker_bytes < 1:
        raise ValueError(f"worker_bytes must be a positive byte count, got {worker_bytes}")
    fit = memory_workers(worker_bytes, available_memory() if available_bytes is None else available_bytes)
    if fit is None:
        return parallel.ordered_map(function, items, min_items=min_items)
    with _worker_cap(min(parallel.workers(), fit)):
        return parallel.ordered_map(function, items, min_items=min_items)
