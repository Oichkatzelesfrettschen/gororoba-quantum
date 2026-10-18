"""Print the CI runner's detected hardware and interpreter for the job log."""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path


def _read(path: str) -> str:
    try:
        return Path(path).read_text()
    except OSError:
        return ""


def main() -> int:
    import numpy
    import scipy.linalg  # noqa: F401
    from threadpoolctl import threadpool_info

    fields = ("internal_api", "version", "num_threads", "threading_layer", "architecture")
    pools = [{key: pool.get(key) for key in fields} for pool in threadpool_info()]
    print(f"native_threadpools: {json.dumps(pools, sort_keys=True)}")
    print(f"numpy: {numpy.__version__}")
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    cpuinfo = _read("/proc/cpuinfo")
    model = next((line.split(":", 1)[1].strip() for line in cpuinfo.splitlines() if line.startswith("model name")), "")
    flags = next((line.split(":", 1)[1].split() for line in cpuinfo.splitlines() if line.startswith("flags")), [])
    meminfo = {
        line.split(":")[0]: line.split(":")[1].strip()
        for line in _read("/proc/meminfo").splitlines()
        if line.startswith(("MemTotal", "MemAvailable"))
    }
    quota = _read("/sys/fs/cgroup/cpu.max").strip()
    print(f"cpu_model: {model}")
    print(f"logical_cpus: {os.cpu_count()}  affinity_cpus: {affinity}  cgroup_cpu_max: {quota or 'none'}")
    print(f"avx2: {'avx2' in flags}  avx512f: {'avx512f' in flags}")
    print(f"memory: {meminfo}")
    print(f"glibc_tunables: {os.environ.get('GLIBC_TUNABLES', '')}")
    print(f"python: {sys.version.split()[0]} {platform.python_implementation()} {platform.machine()}")
    print(f"platform: {platform.platform()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
