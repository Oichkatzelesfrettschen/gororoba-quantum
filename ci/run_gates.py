"""Run the repository gates listed in ci/gates.json, or in the manifest --manifest names, keep-going.

ci/gates.json lists what every pull request runs; ci/replays.json lists the replays and long checks that run on
demand with ``--manifest ci/replays.json`` (ci/manifest.py is the only reader of both files).

Each gate declares a shell command, working directory and measured duration.
Execution shares detected affinity/cgroup CPU slots across concurrent gates:
ordinary gates reserve one, and gates marked workers: all reserve the available
allocation for their inner pool. Explicit caller caps bound every inner pool.
Native library threads default to one. Every gate runs despite earlier failures;
completions and failure tails print immediately, resource/timing records name
the actual allocation, and any failed gate makes the run exit nonzero.

``--device GPU`` exports GOROROBA_AER_DEVICE=GPU to every gate, so the
replays that simulate run on the local GPU while CI's runners, which carry
no GPU, keep the CPU. A gate that passes on one device and fails on the
other exposes a device-dependent result.

``--max-seconds S`` keeps the gates whose measured seconds are at most S,
the fast gates ci/premerge_gates.py runs on a merge result.

A gate's optional ``requires`` list names the toolchains its live path
needs beyond the repository interpreter; ``qi`` is the Quantum Inspire stack
under $QI_PYTHON (gororoba_quantum/qi_stack.py) and ``singular`` is Singular
4.4 on PATH. Every run includes such a gate, which replays its retained record
(qi) or skips (singular, by its GOROROBA_SINGULAR_REQUIRED guard) where the
toolchain is absent. A caller that exports the variable REQUIREMENTS names for
the toolchain (GOROROBA_QI_REQUIRED=1 or GOROROBA_SINGULAR_REQUIRED=1) makes
each such gate take its live path or fail.

A gate without a ``runtime`` runs under $PYTHON, which pins.resolve_current
chooses: an explicit $PYTHON as named, else the running interpreter when it
holds every pin of requirements.txt and ci/requirements-ci.txt, else the
host environment ci/build_host_envs.sh builds. A gate's ``runtime`` names a
historical producer environment; its command runs under that runtime's
interpreter (pins.REPLAY_RUNTIMES). The interpreter comes from
``--replay-python PATH``, else REPLAY_PYTHON, and must hold every pin of
ci/requirements-replay.txt. With neither, the running interpreter serves
when it holds every pin, then the runtime's host environment, unless
GOROROBA_PINS_REQUIRED=1, which CI sets. One line per runtime before the
first gate names the choice, and a selection with an unresolved runtime
runs no gate and exits 2 with that reason, since its gates would fail on
the interpreter rather than on the tree.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import manifest
import pins

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

TAIL_LINES = 40
# Each named toolchain and the variable that makes its absence a gate failure when the caller exports it.
REQUIREMENTS = {"qi": "GOROROBA_QI_REQUIRED", "singular": "GOROROBA_SINGULAR_REQUIRED"}
OPENBLAS_CORETYPE = "Haswell"
# numpy's dispatched loops above x86-64-v3 (AVX-512 on the runners' Intel
# CPUs) round differently from the AVX2 loops; every runner and build host
# supports x86-64-v3, so capping dispatch there gives all of them one path.
NUMPY_DISABLED_FEATURES = "X86_V4 AVX512_ICL AVX512_SPR"
REPLAY_INTERPRETERS = {runtime: variable for runtime, (variable, _pins) in pins.REPLAY_RUNTIMES.items()}
# The numeric stack a gate's interpreter loads under the gate environment: the CPU model, numpy's enabled dispatch
# targets, and each OpenBLAS that numpy and scipy.linalg load with the core it selected, which shows whether
# OPENBLAS_CORETYPE and NPY_DISABLE_CPU_FEATURES took effect on the runner.
NUMERIC_STACK_PROBE = """
import json, os, numpy, scipy.linalg, threadpoolctl
from numpy._core._multiarray_umath import __cpu_dispatch__, __cpu_features__
try:
    with open("/proc/cpuinfo") as handle:
        info = handle.read().splitlines()
except OSError:
    info = []
model = next((line.split(":", 1)[1].strip() for line in info if line.startswith("model name")), "unknown")
flags = next((line.split(":", 1)[1].split() for line in info if line.startswith("flags")), [])
blas = [
    {"library": os.path.basename(item["filepath"]), "version": item.get("version"), "core": item.get("architecture")}
    for item in threadpoolctl.threadpool_info()
    if item.get("internal_api") == "openblas"
]
print(json.dumps({
    "cpu": model,
    "avx512f": "avx512f" in flags,
    "numpy_dispatch": [name for name in __cpu_dispatch__ if __cpu_features__.get(name)],
    "openblas": blas,
}, sort_keys=True))
"""
# Each collector owns exactly one shell tree, so parallel gates cannot mix
# their RUSAGE_CHILDREN counters. POSIX Python supplies the platform binding.
RESOURCE_COLLECTOR = """
import json
import resource
import subprocess
import sys
from pathlib import Path

completed = subprocess.run(sys.argv[2:], check=False)
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
rss_kib = usage.ru_maxrss / 1024 if sys.platform == "darwin" else usage.ru_maxrss
Path(sys.argv[1]).write_text(json.dumps({
    "user_seconds": usage.ru_utime,
    "system_seconds": usage.ru_stime,
    "max_rss_kib": int(rss_kib),
}))
sys.exit(completed.returncode if completed.returncode >= 0 else 128 - completed.returncode)
"""


def _cpus() -> int:
    return parallel.available_cpus()


def _run(gate: dict[str, Any], environment: dict[str, str], root: Path) -> tuple[dict[str, Any], int, float, str]:
    start = time.monotonic()
    environment = dict(environment)
    environment.setdefault("GOROROBA_WORKERS", "1")
    if runtime := gate.get("runtime"):
        variable = REPLAY_INTERPRETERS[runtime]
        if not environment.get(variable):
            return gate, 127, 0.0, f"historical runtime {runtime} requires {variable}"
        environment = dict(environment, PYTHON=environment[variable])
    try:
        with TemporaryDirectory(prefix="ci-gate-resources-") as temporary:
            resource_file = Path(temporary) / "usage.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    RESOURCE_COLLECTOR,
                    str(resource_file),
                    "sh",
                    "-c",
                    f"set -eu\n{gate['cmd']}",
                ],
                cwd=root / gate["cwd"],
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            resources = json.loads(resource_file.read_text())
            resources["workers"] = int(environment["GOROROBA_WORKERS"])
            measured = dict(gate, resources=resources)
    except OSError as error:
        return gate, 127, time.monotonic() - start, f"gate could not start: {error}"
    except ValueError as error:
        return gate, 127, time.monotonic() - start, f"gate resource record is invalid: {error}"
    return measured, completed.returncode, time.monotonic() - start, completed.stdout


def allocated_workers(gate: dict[str, Any], capacity: int, caller_cap: str | None = None) -> int:
    """Bound inner concurrency by detected slots and the caller's explicit cap."""
    limit = min(capacity, int(caller_cap)) if caller_cap is not None else capacity
    requested = gate.get("workers", caller_cap or "1")
    workers = limit if requested == "all" else min(limit, int(requested))
    if workers < 1:
        raise ValueError(f"{gate['name']}: workers must be positive")
    return workers


def select(
    root: Path,
    tier: str,
    max_seconds: float | None = None,
    listing: str = manifest.GATES,
) -> list[dict[str, Any]]:
    """The gates of the tree at root in the file order of the manifest listing, limited to tier and measured seconds."""
    gates = manifest.gates(root, listing)
    for gate in gates:
        if gate.get("runtime") is not None and gate["runtime"] not in REPLAY_INTERPRETERS:
            raise SystemExit(f"{gate['name']}: unregistered historical runtime")
        workers = gate.get("workers", 1)
        if workers != "all" and (isinstance(workers, bool) or not isinstance(workers, int) or workers < 1):
            raise SystemExit(f"{gate['name']}: workers must be a positive integer or all")
        if "requires" not in gate:
            continue
        named = gate["requires"]
        valid = isinstance(named, list) and all(isinstance(name, str) for name in named)
        if not valid or not named or set(named) - REQUIREMENTS.keys() or len(set(named)) < len(named):
            raise SystemExit(f"{gate['name']}: requires must be a nonempty list of distinct {sorted(REQUIREMENTS)}")
    if tier == "pr":
        gates = [gate for gate in gates if gate.get("tier", "pr") == "pr"]
    if max_seconds is not None:
        gates = [gate for gate in gates if float(gate.get("seconds", 10.0)) <= max_seconds]
    return gates


def environment_for(device: str | None) -> dict[str, str]:
    environment = dict(os.environ)
    if device:
        environment["GOROROBA_AER_DEVICE"] = device
    environment.setdefault("PYTHON", sys.executable)
    retained_tunables = []
    tls_capacity = 4096
    for entry in environment.get("GLIBC_TUNABLES", "").split(":"):
        name, separator, value = entry.partition("=")
        if name == "glibc.rtld.optional_static_tls" and separator:
            try:
                tls_capacity = max(tls_capacity, int(value))
            except ValueError:
                pass
        elif entry:
            retained_tunables.append(entry)
    retained_tunables.append(f"glibc.rtld.optional_static_tls={tls_capacity}")
    environment["GLIBC_TUNABLES"] = ":".join(retained_tunables)
    for variable in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "BLIS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "RAYON_NUM_THREADS",
        "QISKIT_NUM_PROCS",
    ):
        environment.setdefault(variable, "1")
    # OpenBLAS and numpy select kernels by the running CPU, and kernels differ
    # in rounding; one named x86-64 AVX2 kernel set for each gives every
    # x86-64-v3 CPU one rounding path. libm and the Python build follow the
    # host image, so records are written in the runner's (ci/runner_image.sh).
    environment.setdefault("OPENBLAS_CORETYPE", OPENBLAS_CORETYPE)
    environment.setdefault("NPY_DISABLE_CPU_FEATURES", NUMPY_DISABLED_FEATURES)
    return environment


def numeric_stack(interpreter: str, environment: dict[str, str]) -> str:
    """One JSON line describing the CPU and the numpy and OpenBLAS paths the interpreter loads under environment."""
    try:
        done = subprocess.run(
            [interpreter, "-B", "-c", NUMERIC_STACK_PROBE],
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable ({exc})"
    if done.returncode != 0:
        tail = (done.stderr.strip().splitlines() or ["no output"])[-1]
        return f"unavailable (exit {done.returncode}: {tail})"
    return done.stdout.strip()


def run_all(
    gates: list[dict[str, Any]], environment: dict[str, str], root: Path
) -> Iterator[tuple[dict[str, Any], int, float, str]]:
    """Share detected CPU slots across independent gates and their process pools."""
    capacity = _cpus()
    pending = list(gates)
    active: dict[Future[tuple[dict[str, Any], int, float, str]], int] = {}
    available = capacity
    with ThreadPoolExecutor(max_workers=capacity) as pool:
        while pending or active:
            for gate in list(pending):
                workers = allocated_workers(gate, capacity, environment.get("GOROROBA_WORKERS"))
                if workers > available:
                    continue
                child_environment = dict(environment, GOROROBA_WORKERS=str(workers))
                active[pool.submit(_run, gate, child_environment, root)] = workers
                available -= workers
                pending.remove(gate)
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                available += active.pop(future)
                yield future.result()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        choices=manifest.MANIFESTS,
        default=manifest.GATES,
        help="the gate list to run: ci/gates.json (every pull request) or ci/replays.json (on demand)",
    )
    parser.add_argument("--list", action="store_true", help="print the selected gates without running them")
    parser.add_argument(
        "--tier",
        choices=("pr", "full"),
        default="full",
        help="pr keeps the pr-tier gates, the set ci/premerge_gates.py runs; full keeps every gate",
    )
    parser.add_argument(
        "--device",
        choices=("CPU", "GPU"),
        help="Aer device for every gate (GOROROBA_AER_DEVICE); unset keeps the environment's, CPU by default",
    )
    parser.add_argument("--max-seconds", type=float, help="only gates whose measured seconds are at most this")
    parser.add_argument(
        "--gates",
        help="comma-separated gate names; a registered case gate matches by its own or its parent's name",
    )
    parser.add_argument("--timings", type=Path, help="write measured gate durations and run wall time as JSON")
    parser.add_argument("--plan", type=Path, help="write the selected gates and historical environments, then exit")
    parser.add_argument("--github-output", type=Path, help="append historical=true/false for a --plan step")
    parser.add_argument(
        "--replay-python",
        help="interpreter for historical-runtime gates; it must hold every pin of ci/requirements-replay.txt",
    )
    arguments = parser.parse_args(argv)
    gates = select(ROOT, arguments.tier, arguments.max_seconds, arguments.manifest)
    selected = manifest.expand_cases(ROOT, gates)
    if arguments.gates is not None:
        named = {name for name in arguments.gates.split(",") if name}
        selected = [gate for gate in selected if gate["name"] in named or gate.get("parent") in named]
    if arguments.plan is not None:
        environments = sorted({gate["runtime"] for gate in selected if gate.get("runtime")})
        arguments.plan.write_text(
            json.dumps(
                {
                    "schema": "gororoba-gate-plan-v1",
                    "gates": selected,
                    "environments": environments,
                },
                indent=2,
            )
            + "\n"
        )
        if arguments.github_output is not None:
            with arguments.github_output.open("a") as output:
                print(f"historical={str(bool(environments)).lower()}", file=output)
        return 0
    if arguments.github_output is not None:
        parser.error("--github-output requires --plan")
    if arguments.list:
        for gate in selected:
            print(f"{gate['name']}\t{gate['cwd']}\t{gate['cmd']}")
        return 0
    # _run gives each historical gate its runtime's interpreter as $PYTHON, so the current runtime
    # resolves only when a selected gate runs under it.
    primary = sys.executable
    # The shared host-environment lock spans interpreter resolution and every gate, so a rebuild of the host
    # environments cannot swap packages under the verdict; the descriptor stays open until the process exits.
    pins.hold_host_envs(os.environ)
    if any(not gate.get("runtime") for gate in selected):
        resolved, reason = pins.resolve_current(os.environ, sys.executable, ROOT)
        print(f"current runtime: {reason}", flush=True)
        if resolved is None:
            return 2
        primary = resolved
    environment = environment_for(arguments.device)
    environment["PYTHON"] = primary
    print(f"numeric stack: {numeric_stack(primary, environment)}", flush=True)
    unresolved = []
    for runtime in sorted({gate["runtime"] for gate in selected if gate.get("runtime")}):
        interpreter, reason = pins.resolve_replay(runtime, arguments.replay_python, environment, primary)
        print(f"historical runtime {runtime}: {reason}", flush=True)
        variable = REPLAY_INTERPRETERS[runtime]
        if interpreter is None:
            unresolved.append(runtime)
        else:
            environment[variable] = interpreter
    if unresolved:
        return 2
    failures = []
    started = time.monotonic()
    timings = []
    for gate, status, seconds, output in run_all(selected, environment, ROOT):
        timings.append(
            {
                "name": gate["name"],
                "status": status,
                "seconds": seconds,
                "estimated_seconds": gate.get("seconds"),
                "resources": gate.get("resources"),
                "runtime": gate.get("runtime", "current"),
            }
        )
        print(f"{'PASS' if status == 0 else 'FAIL'} {gate['name']} {seconds:7.1f}s  {gate['cmd'][:100]}", flush=True)
        if status != 0:
            failures.append((gate, status, output))
            tail = "\n".join(output.splitlines()[-TAIL_LINES:])
            print(f"\n=== {gate['name']} exit {status} in {gate['cwd']}\n{gate['cmd']}\n{tail}", flush=True)
    if arguments.timings is not None:
        arguments.timings.parent.mkdir(parents=True, exist_ok=True)
        arguments.timings.write_text(
            json.dumps(
                {
                    "schema": "gororoba-gate-timings-v1",
                    "wall_seconds": time.monotonic() - started,
                    "cpu_capacity": _cpus(),
                    "gates": sorted(timings, key=lambda row: str(row["name"])),
                },
                indent=2,
            )
            + "\n"
        )
    passed = len(selected) - len(failures)
    device = environment.get("GOROROBA_AER_DEVICE", "CPU")
    summary = f"{passed} passed, {len(failures)} failed of {len(selected)} gates"
    print(f"\n{summary} on {device}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
