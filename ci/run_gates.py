"""Run the repository gates listed in ci/gates.json, sharded and keep-going.

Each gate declares a shell command, working directory and measured duration.
Shards balance estimated CPU-slot seconds under a stable planning profile.
Execution shares detected affinity/cgroup CPU slots across concurrent gates:
ordinary gates reserve one, and gates marked workers: all reserve the available
allocation for their inner pool. Explicit caller caps bound every inner pool.
Native library threads default to one. Every gate runs despite earlier failures;
completions and failure tails print immediately, resource/timing records name
the actual allocation, and any failed gate makes the shard exit nonzero.

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
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import gate_inputs
import gate_ledger
import host_identity
import pins

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

# Stable across shards, matching the retained hosted four-CPU timing profile.
DEFAULT_SHARD_CPUS = 4
TAIL_LINES = 40
# Each named toolchain and the variable that makes its absence a gate failure.
REQUIREMENTS = {"qi": "GOROROBA_QI_REQUIRED"}
REPLAY_INTERPRETERS = {runtime: variable for runtime, (variable, _pins) in pins.REPLAY_RUNTIMES.items()}
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


def _run(
    gate: dict[str, Any], environment: dict[str, str], root: Path, trace: Path | None = None
) -> tuple[dict[str, Any], int, float, str]:
    start = time.monotonic()
    environment = dict(environment)
    environment.setdefault("GOROROBA_WORKERS", "1")
    if runtime := gate.get("runtime"):
        variable = REPLAY_INTERPRETERS[runtime]
        if not environment.get(variable):
            return gate, 127, 0.0, f"historical runtime {runtime} requires {variable}"
        environment = dict(environment, PYTHON=environment[variable])
    if trace is not None:
        trace.mkdir(parents=True)
        pythons = [environment.get("PYTHON", ""), *(environment.get(name, "") for name in REPLAY_INTERPRETERS.values())]
        resolved = [os.path.realpath(found) for found in map(_which, pythons) if found]
        environment = gate_ledger.trace_environment(environment, trace, root, resolved)
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


def _which(name: str) -> str | None:
    import shutil

    return shutil.which(name) if name else None


def allocated_workers(gate: dict[str, Any], capacity: int, caller_cap: str | None = None) -> int:
    """Bound inner concurrency by detected slots and the caller's explicit cap."""
    limit = min(capacity, int(caller_cap)) if caller_cap is not None else capacity
    requested = gate.get("workers", caller_cap or "1")
    workers = limit if requested == "all" else min(limit, int(requested))
    if workers < 1:
        raise ValueError(f"{gate['name']}: workers must be positive")
    return workers


def measured_seconds(root: Path) -> dict[str, float]:
    """Measured wall seconds per gate from ci/gate_timings.json (ci/merge_gate_timings.py), empty when absent."""
    path = root / "ci" / "gate_timings.json"
    if not path.is_file():
        return {}
    gates = json.loads(path.read_text())["gates"]
    return {name: float(entry["wall_seconds"]) for name, entry in gates.items()}


def assign(
    gates: list[dict[str, Any]],
    count: int,
    capacity: int = 1,
    caller_cap: str | None = None,
    measured: dict[str, float] | None = None,
) -> list[list[dict[str, Any]]]:
    """Longest-first allocation by occupied CPU-slot seconds, measured where recorded, else estimated."""
    shards: list[list[dict[str, Any]]] = [[] for _ in range(count)]
    loads = [0.0] * count
    measured = measured or {}
    costs = {
        gate["name"]: measured.get(gate["name"], float(gate.get("seconds", 10.0)))
        * allocated_workers(gate, capacity, caller_cap)
        for gate in gates
    }
    for gate in sorted(gates, key=lambda gate: (-costs[gate["name"]], gate["name"])):
        target = min(range(count), key=lambda index: (loads[index], index))
        shards[target].append(gate)
        loads[target] += costs[gate["name"]]
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
    return environment


def run_all(
    gates: list[dict[str, Any]], environment: dict[str, str], root: Path, traces: Path | None = None
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
                trace = None if traces is None else traces / gate["name"]
                arguments = (gate, child_environment, root) if trace is None else (gate, child_environment, root, trace)
                active[pool.submit(_run, *arguments)] = workers
                available -= workers
                pending.remove(gate)
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                available += active.pop(future)
                yield future.result()


@dataclass
class GateResult:
    """One gate's verdict: PASS or FAIL from a run, SKIP from a matching ledger entry."""

    gate: dict[str, Any]
    status: int
    seconds: float
    output: str
    verdict: str
    untraceable: list[str] = field(default_factory=list)


def execute(
    gates: list[dict[str, Any]],
    environment: dict[str, str],
    root: Path,
    ledger: Path | None = None,
    ledger_out: Path | None = None,
    audit: Path | None = None,
) -> Iterator[GateResult]:
    """Run gates, skipping those whose ledger key matches, and record traceable passes.

    With ``audit`` every gate runs; a gate the ledger at that path would
    have skipped and that fails now yields verdict FAIL with ``untraceable``
    naming the audit, so the caller reports the ledger miss.
    """
    tracing = ledger_out is not None or audit is not None
    stored = gate_ledger.load(ledger if audit is None else audit)
    if not tracing and ledger is None:
        for gate, status, seconds, output in run_all(gates, environment, root):
            yield GateResult(gate, status, seconds, output, "PASS" if status == 0 else "FAIL")
        return
    replay = {variable: environment[variable] for variable in REPLAY_INTERPRETERS.values() if environment.get(variable)}
    host = gate_ledger.host_digest(host_identity.identity(environment, environment["PYTHON"], replay))
    content = gate_ledger.Content(root)
    capacity = _cpus()
    cap = environment.get("GOROROBA_WORKERS")

    def key(gate: dict[str, Any], reads: dict[str, list[Any]]) -> str:
        return gate_ledger.gate_key(gate, allocated_workers(gate, capacity, cap), host, reads, content)

    matching = {
        gate["name"]
        for gate in gates
        if gate["name"] in stored and stored[gate["name"]]["key"] == key(gate, stored[gate["name"]]["reads"])
    }
    entries = dict(gate_ledger.load(ledger)) if ledger_out is not None else {}
    to_run = gates if audit is not None else [gate for gate in gates if gate["name"] not in matching]
    if audit is None:
        for gate in gates:
            if gate["name"] in matching:
                yield GateResult(gate, 0, 0.0, "", "SKIP")
    with TemporaryDirectory(prefix="ci-read-trace-") as temporary:
        traces = Path(temporary) if tracing else None
        for gate, status, seconds, output in run_all(to_run, environment, root, traces):
            reasons: list[str] = []
            verdict = "PASS" if status == 0 else "FAIL"
            if traces is None:
                pass
            elif status == 0:
                shell = gate_ledger.shell_untraceable(gate["cmd"])
                reads, reasons = gate_ledger.read_trace(traces / gate["name"])
                if shell is not None:
                    reasons = [shell, *reasons]
                if reads is not None and not reasons:
                    # Another gate of the shard may have rewritten a file
                    # since an earlier key read it, so each key hashes the
                    # bytes on disk when its gate ends.
                    content.forget()
                    entries[gate["name"]] = {"key": key(gate, reads), "reads": reads}
                else:
                    entries.pop(gate["name"], None)
            else:
                entries.pop(gate["name"], None)
                if audit is not None and gate["name"] in matching:
                    reasons = [f"ledger {audit} would have skipped this failing gate"]
            yield GateResult(gate, status, seconds, output, verdict, reasons)
    if ledger_out is not None:
        gate_ledger.write(ledger_out, entries, [gate["name"] for gate in gates])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", default="0/1", help="SHARD/COUNT, zero-based")
    parser.add_argument(
        "--shard-cpus",
        type=int,
        default=DEFAULT_SHARD_CPUS,
        help="stable CPU profile for shard estimates; execution concurrency is detected per runner",
    )
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
    parser.add_argument(
        "--gates",
        help="comma-separated gate names; a registered case gate matches by its own or its parent's name",
    )
    parser.add_argument("--timings", type=Path, help="write measured gate durations and shard wall time as JSON")
    parser.add_argument("--plan", type=Path, help="write the selected shard and historical environments, then exit")
    parser.add_argument("--github-output", type=Path, help="append historical=true/false for a --plan step")
    parser.add_argument(
        "--replay-python",
        help="interpreter for historical-runtime gates; it must hold every pin of ci/requirements-replay.txt",
    )
    parser.add_argument("--ledger", type=Path, help="skip gates whose ledger key in this file is unchanged")
    parser.add_argument("--ledger-out", type=Path, help="trace every gate and write the merged ledger of this run")
    parser.add_argument(
        "--ledger-audit",
        type=Path,
        help="run every gate and fail on each one this ledger would have skipped that fails now",
    )
    arguments = parser.parse_args(argv)
    if arguments.ledger_audit is not None and arguments.ledger is not None:
        parser.error("--ledger-audit runs every gate; it excludes --ledger")
    if arguments.shard_cpus < 1:
        parser.error("--shard-cpus must be positive")
    shard, count = (int(part) for part in arguments.shard.split("/"))
    if not 0 <= shard < count:
        parser.error("shard must satisfy 0 <= SHARD < COUNT")
    changed = None
    if arguments.changed_files is not None:
        changed = arguments.changed_files.read_bytes().decode("utf-8").split("\0")
        changed = [path for path in changed if path]
    candidates = gate_inputs.expand_cases(
        ROOT, select(ROOT, arguments.tier, arguments.max_seconds, arguments.requires, changed)
    )
    if arguments.gates is not None:
        named = {name for name in arguments.gates.split(",") if name}
        candidates = [gate for gate in candidates if gate["name"] in named or gate.get("parent") in named]
    selected = assign(candidates, count, arguments.shard_cpus, measured=measured_seconds(ROOT))[shard]
    if arguments.plan is not None:
        environments = sorted({gate["runtime"] for gate in selected if gate.get("runtime")})
        arguments.plan.write_text(
            json.dumps(
                {
                    "schema": "gororoba-gate-plan-v1",
                    "gates": selected,
                    "environments": environments,
                    "shard_cpus": arguments.shard_cpus,
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
    primary, reason = pins.resolve_current(os.environ, sys.executable, ROOT)
    print(f"current runtime: {reason}", flush=True)
    if primary is None:
        return 2
    environment = environment_for(arguments.device, arguments.requires)
    environment["PYTHON"] = primary
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
    skipped = []
    audit_misses = []
    started = time.monotonic()
    timings = []
    outcomes = execute(selected, environment, ROOT, arguments.ledger, arguments.ledger_out, arguments.ledger_audit)
    for result in outcomes:
        gate, status, seconds, output = result.gate, result.status, result.seconds, result.output
        if result.verdict == "SKIP":
            skipped.append(gate["name"])
            print(f"SKIP {gate['name']}  ledger key unchanged", flush=True)
            continue
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
        print(f"{result.verdict} {gate['name']} {seconds:7.1f}s  {gate['cmd'][:100]}", flush=True)
        if arguments.ledger_out is not None and status == 0 and result.untraceable:
            print(f"  untraceable {gate['name']}: {'; '.join(result.untraceable[:3])}", flush=True)
        if status != 0:
            failures.append((gate, status, output))
            if arguments.ledger_audit is not None and result.untraceable:
                audit_misses.append(gate["name"])
            tail = "\n".join(output.splitlines()[-TAIL_LINES:])
            print(f"\n=== {gate['name']} exit {status} in {gate['cwd']}\n{gate['cmd']}\n{tail}", flush=True)
    if arguments.timings is not None:
        arguments.timings.parent.mkdir(parents=True, exist_ok=True)
        arguments.timings.write_text(
            json.dumps(
                {
                    "schema": "gororoba-gate-timings-v1",
                    "shard": arguments.shard,
                    "wall_seconds": time.monotonic() - started,
                    "cpu_capacity": _cpus(),
                    "shard_cpus": arguments.shard_cpus,
                    "gates": sorted(timings, key=lambda row: str(row["name"])),
                    "skipped": sorted(skipped),
                    "ledger_audit_misses": sorted(audit_misses),
                },
                indent=2,
            )
            + "\n"
        )
    passed = len(selected) - len(failures) - len(skipped)
    device = environment.get("GOROROBA_AER_DEVICE", "CPU")
    cached = f", {len(skipped)} skipped" if skipped else ""
    summary = f"{passed} passed, {len(failures)} failed{cached} of {len(selected)} gates"
    print(f"\n{summary} in shard {shard}/{count} on {device}")
    if audit_misses:
        print(f"ledger audit: the ledger would have skipped failing gates {', '.join(audit_misses)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
