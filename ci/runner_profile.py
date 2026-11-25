"""Profile of the machine a CI job runs on: CPU model, logical CPUs, clock, steal time and a fixed calibration workload.

    "$PYTHON" ci/runner_profile.py [--json PATH] [--github-env]

Hosted runners of one label differ in per-core speed by up to a factor of two: the pull-request suite summed 875 to
1,014 s of test time on AMD EPYC 9V45 runners, 1,262 s on an EPYC 9V74 and about 1,600 s on an EPYC 7763
(gororoba-quantum pull request 1007, 2026-11-25). The workload is fixed single-threaded work, an integer loop and a
NumPy matrix product at one BLAS thread, so its median wall time measures the core the job received: it took 0.50 to
0.55 s on the 9V45 runners, 0.79 s on the 9V74 and 1.09 s on the 7763, in step with the suite. A second pass maps two
copies per worker slot through parallel.ordered_map, whose parallel.workers() allocation (affinity mask bounded by the
cgroup CPU quota and GOROROBA_WORKERS) also sizes the xdist pool, so it loads the CPUs the suite uses; steal time from
/proc/stat separates a slow core from a host that takes CPU away from the guest. `--github-env` exports
GOROROBA_RUNNER_CALIBRATION_SECONDS, the single-copy median, which tests/conftest.py turns into the per-test budget's
speed factor (`speed_factor`).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

REPEATS = 5
# The native thread pools pinned to one thread, as ci/pr_checks.sh pins them for the suite, so the workload measures
# one core: macOS NumPy multiplies through Accelerate, whose pool only VECLIB_MAXIMUM_THREADS bounds.
THREAD_CAPS = {
    name: "1"
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "BLIS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
}
# The single-copy median on the AMD EPYC 9V45 runners that set the 10 s per-test target (pull request 1007).
REFERENCE_SECONDS = 0.55


def speed_factor(calibration: str | None, reference: float = REFERENCE_SECONDS) -> float:
    """How much slower than the reference runner this one is, from GOROROBA_RUNNER_CALIBRATION_SECONDS; never below
    1, so a fast runner keeps the full budget, and 1 where no calibration ran (a local run)."""
    if not calibration:
        return 1.0
    seconds = float(calibration)
    if not seconds > 0:
        raise ValueError(f"calibration seconds must be positive, got {calibration!r}")
    return max(1.0, seconds / reference)


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
    """Aggregate jiffies of /proc/stat: user, nice, system, idle, iowait, irq, softirq and steal; empty off Linux."""
    try:
        fields = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()
    except OSError:
        return {}
    names = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
    return {name: int(value) for name, value in zip(names, fields[1:9], strict=False)}


def cap_threads() -> None:
    """Pin every native thread pool to one thread; effective only before NumPy loads in the process."""
    os.environ.update(THREAD_CAPS)


def workload(scale: float = 1.0) -> float:
    """Wall seconds of one fixed workload, single-threaded once `cap_threads` ran before NumPy loaded; `scale`
    shrinks it for tests."""
    import numpy as np

    n = 320
    a = np.cos(np.arange(n * n, dtype=np.float64).reshape(n, n))
    start = time.perf_counter()
    total = 0
    for i in range(int(9_000_000 * scale)):
        total = (total + i * i) % 1_000_003
    for _ in range(max(1, int(60 * scale))):
        a = np.tanh(a @ a.T / n)
    if total < 0 or not np.isfinite(a).all():
        raise RuntimeError("calibration workload produced an impossible value")
    return time.perf_counter() - start


def profile(scale: float = 1.0, repeats: int = REPEATS) -> dict[str, object]:
    """The runner's identity and calibration. The concurrent pass maps two workloads per parallel.workers() slot
    through the shared pool, one item per chunk; one slot (a test process) runs them inline."""
    copies = parallel.workers()
    before = cpu_ticks()
    single = [workload(scale) for _ in range(repeats)]
    concurrent = parallel.ordered_map(workload, [scale] * (2 * copies), min_items=1)
    after = cpu_ticks()
    delta = {k: after[k] - before[k] for k in before if k in after}
    return {
        "cpu": cpu_identity(),
        "calibration_wall_seconds": [round(s, 4) for s in single],
        "calibration_median_wall": round(statistics.median(single), 4),
        "concurrent_copies": copies,
        "concurrent_median_wall": round(statistics.median(concurrent), 4),
        # None where /proc/stat is absent (macOS): unmeasured, not zero.
        "steal_fraction": round(delta.get("steal", 0) / (sum(delta.values()) or 1), 4) if delta else None,
        "speed_factor": round(speed_factor(str(statistics.median(single))), 3),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--json", type=Path, help="write the profile to this file")
    parser.add_argument("--github-env", action="store_true", help="export the calibration to $GITHUB_ENV")
    args = parser.parse_args(argv)
    cap_threads()
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
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        cpu = result["cpu"]
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(
                f"Runner: {cpu['model']} ({cpu['affinity_cpus']} CPUs);"  # type: ignore[index]
                f" calibration {result['calibration_median_wall']} s single,"
                f" {result['concurrent_median_wall']} s with {result['concurrent_copies']} copies;"
                f" steal {result['steal_fraction']}; per-test budget factor {result['speed_factor']}\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
