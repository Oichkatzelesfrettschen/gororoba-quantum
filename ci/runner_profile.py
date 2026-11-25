"""Profile of the machine a CI job runs on: CPU model, cores, steal time and a fixed calibration workload.

    "$PYTHON" ci/runner_profile.py [--json PATH] [--github-env]

The hosted runners of one label differ in per-core speed: the pull-request suite has summed 844 s on one run and 1,811 s
on another with a warm environment (GitHub jobs API and pytest JUnit reports, 2026-11-24). The workload here is fixed
single-threaded work (an integer loop and a NumPy matrix product at one BLAS thread), so its time measures the core the
job received. Steal time from /proc/stat separates a slow core from a host that takes CPU away from the guest.
`--github-env` exports GOROROBA_RUNNER_CALIBRATION_SECONDS (the median wall time of the workload) for later steps.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402 - the thread caps above must precede the import

REPEATS = 5


def cpu_identity() -> dict[str, object]:
    """Model name, logical CPUs and mean clock from /proc/cpuinfo; empty fields off Linux."""
    models: list[str] = []
    clocks: list[float] = []
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition(":")
            if key.strip() == "model name":
                models.append(value.strip())
            elif key.strip() == "cpu MHz":
                clocks.append(float(value))
    except OSError:
        pass
    return {
        "model": models[0] if models else platform.processor(),
        "logical_cpus": os.cpu_count(),
        "affinity_cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "mean_mhz": round(statistics.fmean(clocks), 1) if clocks else None,
    }


def cpu_ticks() -> dict[str, int]:
    """Aggregate jiffies of /proc/stat: user, system, idle, iowait and steal; empty off Linux."""
    try:
        fields = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()
    except OSError:
        return {}
    names = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
    return {name: int(value) for name, value in zip(names, fields[1:9], strict=False)}


def workload() -> tuple[float, float]:
    """Wall and process seconds of one fixed single-threaded workload."""
    rng = np.random.default_rng(20261124)
    a = rng.standard_normal((320, 320))
    wall, cpu = time.perf_counter(), time.process_time()
    total = 0
    for i in range(9_000_000):
        total = (total + i * i) % 1_000_003
    for _ in range(60):
        a = np.tanh(a @ a.T / 320.0)
    if total < 0 or not np.isfinite(a).all():
        raise RuntimeError("calibration workload produced an impossible value")
    return time.perf_counter() - wall, time.process_time() - cpu


def profile() -> dict[str, object]:
    before = cpu_ticks()
    runs = [workload() for _ in range(REPEATS)]
    after = cpu_ticks()
    delta = {k: after[k] - before[k] for k in before if k in after}
    busy = sum(delta.values()) or 1
    return {
        "cpu": cpu_identity(),
        "calibration_wall_seconds": [round(w, 4) for w, _ in runs],
        "calibration_process_seconds": [round(c, 4) for _, c in runs],
        "calibration_median_wall": round(statistics.median(w for w, _ in runs), 4),
        "steal_fraction_during_calibration": round(delta.get("steal", 0) / busy, 4),
        "proc_stat": after,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write the profile to this file")
    parser.add_argument("--github-env", action="store_true", help="export the calibration to $GITHUB_ENV")
    args = parser.parse_args(argv)
    result = profile()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json is not None:
        args.json.write_text(text + "\n", encoding="utf-8")
    if args.github_env:
        target = os.environ.get("GITHUB_ENV")
        if not target:
            raise SystemExit("runner_profile: --github-env needs GITHUB_ENV")
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(f"GOROROBA_RUNNER_CALIBRATION_SECONDS={result['calibration_median_wall']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
