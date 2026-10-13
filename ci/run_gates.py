"""Run the repository gates listed in ci/gates.json, sharded and keep-going.

Each gate is one shell command with a repository-relative working directory
and the seconds it took on the last measured CI run. Shards come from a
longest-first assignment of those durations, so the slowest gates land on
separate shards. A shard uses the shared half-CPU default for its outer pool.
Child process pools and BLAS/OpenMP threads default to one; explicit environment
overrides remain authoritative. Every gate runs regardless
of earlier failures, and the exit status is nonzero when any gate fails,
listing each failure with its output tail.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TAIL_LINES = 40


def _cpus() -> int:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    from parallel import default_threads

    return default_threads()


def _run(gate: dict[str, Any], environment: dict[str, str]) -> tuple[dict[str, Any], int, float, str]:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            ["sh", "-c", f"set -eu\n{gate['cmd']}"],
            cwd=ROOT / gate["cwd"],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError as error:
        return gate, 127, time.monotonic() - start, f"gate could not start: {error}"
    return gate, completed.returncode, time.monotonic() - start, completed.stdout


def assign(gates: list[dict[str, Any]], count: int) -> list[list[dict[str, Any]]]:
    """Longest-first assignment: each gate joins the shard with the least total seconds."""
    shards: list[list[dict[str, Any]]] = [[] for _ in range(count)]
    loads = [0.0] * count
    for gate in sorted(gates, key=lambda gate: (-float(gate.get("seconds", 10.0)), gate["name"])):
        target = min(range(count), key=lambda index: (loads[index], index))
        shards[target].append(gate)
        loads[target] += float(gate.get("seconds", 10.0))
    return shards


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", default="0/1", help="SHARD/COUNT, zero-based")
    parser.add_argument("--list", action="store_true", help="print this shard's gates without running them")
    parser.add_argument(
        "--tier",
        choices=("pr", "full"),
        default="full",
        help="pr runs the gates that fit pull-request CI; full adds the long simulation contracts",
    )
    arguments = parser.parse_args(argv)
    shard, count = (int(part) for part in arguments.shard.split("/"))
    if not 0 <= shard < count:
        parser.error("shard must satisfy 0 <= SHARD < COUNT")
    gates = json.loads((ROOT / "ci" / "gates.json").read_text())["gates"]
    if arguments.tier == "pr":
        gates = [gate for gate in gates if gate.get("tier", "pr") == "pr"]
    selected = assign(gates, count)[shard]
    if arguments.list:
        for gate in selected:
            print(f"{gate['name']}\t{gate['cwd']}\t{gate['cmd']}")
        return 0
    environment = dict(os.environ)
    environment.setdefault("PYTHON", sys.executable)
    environment.setdefault("GOROROBA_WORKERS", "1")
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        environment.setdefault(variable, "1")
    failures = []
    with ThreadPoolExecutor(max_workers=_cpus()) as pool:
        for gate, status, seconds, output in pool.map(lambda gate: _run(gate, environment), selected):
            verdict = "PASS" if status == 0 else "FAIL"
            print(f"{verdict} {gate['name']} {seconds:7.1f}s  {gate['cmd'][:100]}", flush=True)
            if status != 0:
                failures.append((gate, status, output))
    for gate, status, output in failures:
        tail = "\n".join(output.splitlines()[-TAIL_LINES:])
        print(f"\n=== {gate['name']} exit {status} in {gate['cwd']}\n{gate['cmd']}\n{tail}")
    passed = len(selected) - len(failures)
    print(f"\n{passed} passed, {len(failures)} failed of {len(selected)} gates in shard {shard}/{count}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
