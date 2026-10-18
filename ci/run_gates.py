"""Run the repository gates listed in ci/gates.json, sharded and keep-going.

Each gate is one shell command with a repository-relative working directory
and the seconds it took on the last measured CI run. Shards come from a
longest-first assignment of those durations, so the slowest gates land on
separate shards. A shard runs its gates on a thread pool sized to the CPUs
available to the process, each gate's own process pool limited to one worker
and native-library threads default to one; every gate runs regardless
of earlier failures, completions print immediately, and the exit status is nonzero when any gate fails,
listing each failure with its output tail.

``--device GPU`` exports GOROROBA_AER_DEVICE=GPU to every gate, so the
replays that simulate run on the local GPU while CI's runners, which carry
no GPU, keep the CPU. A gate that passes on one device and fails on the
other exposes a device-dependent result.

``--max-seconds S`` keeps the gates whose measured seconds are at most S,
the record and replay checks ci/premerge_gates.py runs on a merge result.

A gate's optional ``requires`` list names the toolchains its live path
needs beyond the repository interpreter; ``qi`` is the Quantum Inspire stack
under $QI_PYTHON (gororoba_quantum/qi_stack.py). Every run includes such a
gate, which replays its retained record where the toolchain is absent.
``--requires qi`` keeps only the gates that name it and exports
GOROROBA_QI_REQUIRED=1, so each must take its live path or fail; the
qi-stack job of .github/workflows/ci.yml runs that selection.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import gate_inputs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

TAIL_LINES = 40
# Each named toolchain and the variable that makes its absence a gate failure.
REQUIREMENTS = {"qi": "GOROROBA_QI_REQUIRED"}


def _cpus() -> int:
    return parallel.available_cpus()


def _run(gate: dict[str, Any], environment: dict[str, str], root: Path) -> tuple[dict[str, Any], int, float, str]:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            ["sh", "-c", f"set -eu\n{gate['cmd']}"],
            cwd=root / gate["cwd"],
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


def select(
    root: Path,
    tier: str,
    max_seconds: float | None = None,
    requires: str | None = None,
    changed: list[str] | None = None,
) -> list[dict[str, Any]]:
    """The gates of the tree at root in its ci/gates.json order, limited to tier, measured seconds and toolchain."""
    gates: list[dict[str, Any]] = json.loads((root / "ci" / "gates.json").read_text())["gates"]
    for gate in gates:
        if "requires" not in gate:
            continue
        named = gate["requires"]
        valid = isinstance(named, list) and all(isinstance(name, str) for name in named)
        if not valid or not named or set(named) - REQUIREMENTS.keys() or len(set(named)) < len(named):
            raise SystemExit(f"{gate['name']}: requires must be a nonempty list of distinct {sorted(REQUIREMENTS)}")
    if changed is not None:
        affected = gate_inputs.affected_full(root, gates, changed)
        gates = [gate for gate in gates if gate.get("tier", "pr") == "pr" or gate["name"] in affected]
    elif tier == "pr":
        gates = [gate for gate in gates if gate.get("tier", "pr") == "pr"]
    if requires is not None:
        gates = [gate for gate in gates if requires in gate.get("requires", [])]
    if max_seconds is not None:
        gates = [gate for gate in gates if float(gate.get("seconds", 10.0)) <= max_seconds]
    return gates


def environment_for(device: str | None, requires: str | None = None) -> dict[str, str]:
    environment = dict(os.environ)
    if device:
        environment["GOROROBA_AER_DEVICE"] = device
    if requires is not None:
        environment[REQUIREMENTS[requires]] = "1"
    environment.setdefault("PYTHON", sys.executable)
    environment.setdefault("GOROROBA_WORKERS", "1")
    for variable in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "BLIS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        environment.setdefault(variable, "1")
    return environment


def run_all(
    gates: list[dict[str, Any]], environment: dict[str, str], root: Path
) -> Iterator[tuple[dict[str, Any], int, float, str]]:
    """Every gate on the CPU pool, reporting each completion immediately."""
    with ThreadPoolExecutor(max_workers=_cpus()) as pool:
        futures = [pool.submit(_run, gate, environment, root) for gate in gates]
        for future in as_completed(futures):
            yield future.result()


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
    parser.add_argument(
        "--device",
        choices=("CPU", "GPU"),
        help="Aer device for every gate (GOROROBA_AER_DEVICE); unset keeps the environment's, CPU by default",
    )
    parser.add_argument("--max-seconds", type=float, help="only gates whose measured seconds are at most this")
    parser.add_argument(
        "--requires",
        choices=sorted(REQUIREMENTS),
        help="only gates whose live path needs this toolchain, each required to take that path",
    )
    parser.add_argument(
        "--changed-files", type=Path, help="NUL-delimited git paths; fast gates plus affected full gates"
    )
    parser.add_argument("--timings", type=Path, help="write measured gate durations and shard wall time as JSON")
    arguments = parser.parse_args(argv)
    shard, count = (int(part) for part in arguments.shard.split("/"))
    if not 0 <= shard < count:
        parser.error("shard must satisfy 0 <= SHARD < COUNT")
    changed = None
    if arguments.changed_files is not None:
        changed = arguments.changed_files.read_bytes().decode("utf-8").split("\0")
        changed = [path for path in changed if path]
    selected = assign(select(ROOT, arguments.tier, arguments.max_seconds, arguments.requires, changed), count)[shard]
    if arguments.list:
        for gate in selected:
            print(f"{gate['name']}\t{gate['cwd']}\t{gate['cmd']}")
        return 0
    environment = environment_for(arguments.device, arguments.requires)
    failures = []
    started = time.monotonic()
    timings = []
    for gate, status, seconds, output in run_all(selected, environment, ROOT):
        timings.append(
            {"name": gate["name"], "status": status, "seconds": seconds, "estimated_seconds": gate.get("seconds")}
        )
        verdict = "PASS" if status == 0 else "FAIL"
        print(f"{verdict} {gate['name']} {seconds:7.1f}s  {gate['cmd'][:100]}", flush=True)
        if status != 0:
            failures.append((gate, status, output))
    for gate, status, output in failures:
        tail = "\n".join(output.splitlines()[-TAIL_LINES:])
        print(f"\n=== {gate['name']} exit {status} in {gate['cwd']}\n{gate['cmd']}\n{tail}")
    if arguments.timings is not None:
        arguments.timings.parent.mkdir(parents=True, exist_ok=True)
        arguments.timings.write_text(
            json.dumps(
                {
                    "schema": "gororoba-gate-timings-v1",
                    "shard": arguments.shard,
                    "wall_seconds": time.monotonic() - started,
                    "gates": sorted(timings, key=lambda row: str(row["name"])),
                },
                indent=2,
            )
            + "\n"
        )
    passed = len(selected) - len(failures)
    device = environment.get("GOROROBA_AER_DEVICE", "CPU")
    print(f"\n{passed} passed, {len(failures)} failed of {len(selected)} gates in shard {shard}/{count} on {device}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
