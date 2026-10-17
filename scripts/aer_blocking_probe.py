"""Aer cache blocking on the GPUs of one host: which wide states run, where their chunks live, what ends the rest.

Each trial runs one circuit in its own child process, so a state the host
or the driver cannot hold ends that trial only. The parent records:

- the outcome: ``ok`` when every count lands on the circuit's expected
  outcomes, Aer's error text, or the signal that ended the child;
- the child's peak resident set from ``os.wait4``, the lowest host
  MemAvailable while it ran, and the cgroup's ``oom_kill`` count before and
  after (``memory.events``), which separates a host or cgroup kill from a
  driver failure;
- each GPU's peak memory.used from nvidia-smi samples;
- Aer's metadata: device, method, ``cacheblocking`` (enabled, block_bits,
  chunk_parallel_gpus), ``gpu_blocking`` and target_gpus.

Configurations (CONFIGURATIONS):

- ``auto``: AerSimulator's defaults. Aer blocks a state on its own when it
  needs more than one GPU's share of the summed device memory
  (ParallelStateExecutor::multiple_chunk_required), with the widest chunk
  that fits one whole device (CacheBlocking::set_blocking);
- ``blocked``: ``blocking_enable`` with ``blocking_qubits`` from
  ``calibration_snapshot.blocking_qubits_for``, a chunk of at most a quarter
  of one device, as Aer's option documentation asks, and
  ``max_parallel_shots=1``: Executor::set_parallelization sizes parallel
  shots of a circuit that measurement sampling cannot serve (a dynamic
  circuit) against the whole state and raises "a circuit requires more
  memory than max_memory_mb" when it exceeds the summed GPU memory;
- ``blocked_parallel_shots``: ``blocked`` without ``max_parallel_shots``;
- ``blocked_custatevec``: ``blocked`` with ``cuStateVec_enable``;
- ``blocked_gpu0``: ``blocked`` on GPU 0 alone (``target_gpus=[0]``, which
  Aer takes only as a run option); chunks past that device's memory live in
  host memory (ChunkManager::Allocate).

Circuits: ``ghz`` (H, a CX chain, every qubit measured; outcomes all zeros
or all ones) and ``dynamic`` (the same GHZ, qubit 0 measured mid-circuit and
an if_else that flips every qubit on a one, so every final readout is all
zeros), and ``dynamic_lowered`` (that circuit through
``aer_gpu_probe.lower_conditionals``: each body gate conditioned on the
measured bit, with no jump or mark). AerCompiler inlines an if_else into
jump and mark operations, and the cache-blocking pass splits the operation
list into per-chunk blocks, so a jump whose mark lies in a later block finds
no destination (State::apply_ops raises "Invalid jump destination"). A
dynamic circuit evolves shot by shot, so it runs DYNAMIC_SHOTS.

``--trials`` names a TRIALS subset; ``--check RECORD`` re-derives every
trial's ``ok`` and ``ended_by`` from its retained counts and exit fields.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import aer_gpu_probe  # noqa: E402

import calibration_snapshot  # noqa: E402

SCHEMA = "aer-blocking-probe-v1"
SHOTS = 256
DYNAMIC_SHOTS = 2
SEED = 20261017
TRIAL_TIMEOUT_SECONDS = 600
MEMINFO_POLL_SECONDS = 0.5
CONFIGURATIONS: dict[str, dict[str, Any]] = {
    "auto": {},
    "blocked": {"blocking": True, "max_parallel_shots": 1},
    "blocked_parallel_shots": {"blocking": True},
    "blocked_custatevec": {"blocking": True, "max_parallel_shots": 1, "cuStateVec_enable": True},
    "blocked_gpu0": {"blocking": True, "max_parallel_shots": 1, "target_gpus": [0]},
}
RUN_OPTIONS = frozenset({"target_gpus"})
# (method, width, circuit, configuration): one GPU's limit and one past it
# for each method, the configurations at the width past it, and the dynamic
# circuit blocked across every GPU.
TRIALS: tuple[tuple[str, int, str, str], ...] = (
    ("density_matrix", 14, "ghz", "auto"),
    ("density_matrix", 14, "ghz", "blocked"),
    ("density_matrix", 15, "ghz", "auto"),
    ("density_matrix", 15, "ghz", "blocked"),
    ("density_matrix", 15, "ghz", "blocked_custatevec"),
    ("density_matrix", 15, "ghz", "blocked_gpu0"),
    ("density_matrix", 15, "dynamic", "blocked"),
    ("density_matrix", 15, "dynamic", "blocked_parallel_shots"),
    ("density_matrix", 15, "dynamic_lowered", "blocked"),
    ("statevector", 29, "ghz", "auto"),
    ("statevector", 29, "ghz", "blocked"),
    ("statevector", 30, "ghz", "auto"),
    ("statevector", 30, "ghz", "blocked"),
    ("statevector", 30, "ghz", "blocked_custatevec"),
    ("statevector", 30, "ghz", "blocked_gpu0"),
    ("statevector", 30, "dynamic", "blocked"),
    ("statevector", 30, "dynamic_lowered", "blocked"),
)
METADATA_KEYS = (
    "device",
    "method",
    "num_qubits",
    "cacheblocking",
    "gpu_blocking",
    "target_gpus",
    "cuStateVec_enable",
    "parallel_shots",
    "parallel_state_update",
)


def trial_name(trial: tuple[str, int, str, str]) -> str:
    method, width, circuit, configuration = trial
    return f"{method}-{width}-{circuit}-{configuration}"


def circuit_for(kind: str, width: int) -> Any:
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    if kind == "dynamic_lowered":
        return aer_gpu_probe.lower_conditionals(circuit_for("dynamic", width))

    qubits = QuantumRegister(width, "q")
    out = ClassicalRegister(width, "out")
    circuit = QuantumCircuit(qubits, out)
    circuit.h(0)
    for q in range(width - 1):
        circuit.cx(q, q + 1)
    if kind == "dynamic":
        mid = ClassicalRegister(1, "mid")
        circuit.add_register(mid)
        circuit.measure(0, mid[0])
        with circuit.if_test((mid[0], 1)):
            circuit.x(range(width))
    circuit.measure(qubits, out)
    return circuit


def expected(kind: str, width: int) -> set[str]:
    """Every outcome register the circuit can read without noise."""
    if kind != "ghz":
        return {"0" * width}
    return {"0" * width, "1" * width}


def options_for(method: str, configuration: str, gpu_memory_mib: int) -> dict[str, Any]:
    spec = dict(CONFIGURATIONS[configuration])
    options: dict[str, Any] = {}
    if spec.pop("blocking", False):
        options["blocking_enable"] = True
        options["blocking_qubits"] = calibration_snapshot.blocking_qubits_for(method, gpu_memory_mib)
    options.update(spec)
    return options


def run_one(spec: dict[str, Any]) -> dict[str, Any]:
    """The child: one circuit on the GPU, its counts and metadata."""
    from qiskit_aer import AerSimulator

    circuit = circuit_for(spec["circuit"], spec["width"])
    constructed = {key: value for key, value in spec["options"].items() if key not in RUN_OPTIONS}
    extra = {key: value for key, value in spec["options"].items() if key in RUN_OPTIONS}
    simulator = AerSimulator(method=spec["method"], device="GPU", **constructed)
    shots = SHOTS if spec["circuit"] == "ghz" else DYNAMIC_SHOTS
    started = time.perf_counter()
    result = simulator.run(circuit, shots=shots, seed_simulator=SEED, **extra).result()
    seconds = time.perf_counter() - started
    if not result.success:
        return {"aer_error": str(result.status)[:400], "simulate_seconds": round(seconds, 3)}
    metadata = result.results[0].metadata
    return {
        "simulate_seconds": round(seconds, 3),
        "shots": shots,
        "counts": dict(sorted(result.get_counts().items())),
        "metadata": {key: metadata[key] for key in METADATA_KEYS if key in metadata},
    }


def cgroup_file(name: str) -> Path | None:
    """The process's cgroup v2 file NAME, or None where it is unreadable."""
    try:
        entry = Path("/proc/self/cgroup").read_text(encoding="utf-8").strip().splitlines()[-1]
    except OSError:
        return None
    path = Path("/sys/fs/cgroup") / entry.split(":", 2)[2].lstrip("/") / name
    return path if path.is_file() else None


def oom_kills() -> int | None:
    path = cgroup_file("memory.events")
    if path is None:
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition(" ")
        if key == "oom_kill":
            return int(value)
    return None


def mem_available_mib() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) >> 10
    except OSError:
        return None
    return None


def host_memory() -> dict[str, Any]:
    limit = cgroup_file("memory.max")
    total = None
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                total = int(line.split()[1]) >> 10
    except OSError:
        pass
    return {
        "mem_total_mib": total,
        "cgroup_memory_max": limit.read_text(encoding="utf-8").strip() if limit else None,
    }


def sampled(command: list[str], ngpus: int) -> dict[str, Any]:
    """Run command while nvidia-smi samples every GPU and a thread polls MemAvailable."""
    sampler = None
    if ngpus:
        sampler = subprocess.Popen(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.used",
                "--format=csv,noheader,nounits",
                f"-lms={aer_gpu_probe.GPU_SAMPLE_MS}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    lowest: list[int] = []
    done = threading.Event()

    def poll() -> None:
        while not done.is_set():
            value = mem_available_mib()
            if value is not None:
                lowest.append(value)
            done.wait(MEMINFO_POLL_SECONDS)

    poller = threading.Thread(target=poll, daemon=True)
    poller.start()
    kills = oom_kills()
    started = time.time()
    with tempfile.TemporaryFile("w+") as out, tempfile.TemporaryFile("w+") as err:
        # The child raises its own oom_score_adj to the maximum before it
        # execs, so a state the host cannot hold ends the trial and leaves the
        # probe and the kernel that runs it alive (proc(5), oom_score_adj).
        child = subprocess.Popen(
            ["sh", "-c", 'echo 1000 > /proc/self/oom_score_adj && exec "$0" "$@"', *command],
            stdout=out,
            stderr=err,
            text=True,
        )
        timer = threading.Timer(TRIAL_TIMEOUT_SECONDS, child.kill)
        timer.start()
        # wait4 reaps the child with its own rusage, whose ru_maxrss is that
        # child's peak resident set in KiB; Popen.wait would discard it.
        _, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
        timed_out = not timer.is_alive()
        timer.cancel()
        out.seek(0)
        err.seek(0)
        stdout, stderr = out.read(), err.read()
    outcome: dict[str, Any] = {
        "wall_seconds": round(time.time() - started, 3),
        "returncode": child.returncode,
        "peak_rss_mib": usage.ru_maxrss >> 10,
        "timed_out": timed_out,
    }
    done.set()
    poller.join()
    after = oom_kills()
    outcome["oom_kills"] = None if kills is None or after is None else after - kills
    outcome["min_mem_available_mib"] = min(lowest) if lowest else None
    peaks: dict[int, float] = {}
    if sampler is not None:
        sampler.send_signal(signal.SIGINT)
        text, _ = sampler.communicate()
        for line in text.splitlines():
            parts = [part.strip() for part in line.split(",")]
            try:
                index, used = int(parts[0]), float(parts[1])
            except (IndexError, ValueError):
                continue
            peaks[index] = max(peaks.get(index, 0.0), used)
    outcome["gpu_peak_memory_mib"] = {str(k): v for k, v in sorted(peaks.items())}
    outcome["stdout"] = stdout
    outcome["stderr_tail"] = stderr.strip().splitlines()[-4:]
    return outcome


def ended_by(trial: dict[str, Any]) -> str:
    """ok, aer_error, timeout, oom_kill, signal N, or exit N."""
    if trial.get("timed_out"):
        return "timeout"
    code = trial["returncode"]
    if code == 0:
        return "aer_error" if "aer_error" in trial else ("ok" if trial["ok"] else "wrong_counts")
    if code < 0:
        return "oom_kill" if trial.get("oom_kills") else f"signal {-code}"
    return f"exit {code}"


def classify(trial: dict[str, Any]) -> None:
    # Outcome keys read "mid out" with a mid register; the final readout is
    # the last space-separated field.
    finals = {key.split()[-1] for key in trial.get("counts", {})}
    trial["ok"] = "counts" in trial and finals <= expected(trial["circuit"], trial["width"])
    trial["ended_by"] = ended_by(trial)


def run_trial(trial: tuple[str, int, str, str], gpu_memory_mib: int, ngpus: int) -> dict[str, Any]:
    method, width, circuit, configuration = trial
    spec = {
        "name": trial_name(trial),
        "method": method,
        "width": width,
        "circuit": circuit,
        "configuration": configuration,
        "options": options_for(method, configuration, gpu_memory_mib),
    }
    outcome = sampled([sys.executable, "-B", __file__, "--one", json.dumps(spec)], ngpus)
    stdout = outcome.pop("stdout").strip().splitlines()
    row = {**spec, **outcome}
    if outcome["returncode"] == 0 and stdout:
        row.update(json.loads(stdout[-1]))
    classify(row)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--trials", help="comma-separated trial names (default: every TRIALS entry)")
    parser.add_argument("--one", help=argparse.SUPPRESS)
    parser.add_argument("--check", type=Path, metavar="RECORD")
    args = parser.parse_args()
    if args.one:
        print(json.dumps(run_one(json.loads(args.one))), flush=True)
        return 0
    if args.check:
        return check(args.check)
    if args.out is None:
        parser.error("--out is required")
    devices = aer_gpu_probe.gpus()
    if not devices:
        raise SystemExit(aer_gpu_probe.NO_GPU)
    names = {trial_name(t): t for t in TRIALS}
    chosen = list(TRIALS) if not args.trials else [names[name] for name in args.trials.split(",")]
    gpu_memory_mib = min(int(device["memory.total"]) for device in devices)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "machine": {
            "gpus": devices,
            "cuda_driver": aer_gpu_probe.cuda_driver_version(),
            "cpu": aer_gpu_probe.cpu_model(),
            "cpus": os.cpu_count(),
            "host_memory": host_memory(),
            "packages": aer_gpu_probe.package_versions(),
            "qiskit_aer": aer_gpu_probe.aer_module(),
        },
        "gpu_memory_mib": gpu_memory_mib,
        "blocking_qubits": {
            method: calibration_snapshot.blocking_qubits_for(method, gpu_memory_mib)
            for method in ("statevector", "density_matrix")
        },
        "seed": SEED,
        "trials": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for trial in chosen:
        row = run_trial(trial, gpu_memory_mib, len(devices))
        record["trials"].append(row)
        print(json.dumps({k: row.get(k) for k in ("name", "ended_by", "wall_seconds", "peak_rss_mib")}), flush=True)
        # Rewritten after every trial, so a cut-off kernel keeps every finished one.
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return 0


def check(path: Path) -> int:
    """Re-derive every trial's ok and ended_by and the record's chunk sizes; exit 1 on any difference."""
    record = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    if record.get("schema") != SCHEMA:
        problems.append(f"schema {record.get('schema')!r} is not {SCHEMA}")
    for method, bits in record["blocking_qubits"].items():
        if calibration_snapshot.blocking_qubits_for(method, record["gpu_memory_mib"]) != bits:
            problems.append(f"blocking_qubits[{method}] {bits} differs from blocking_qubits_for")
    for row in record["trials"]:
        retained = (row["ok"], row["ended_by"])
        classify(row)
        if (row["ok"], row["ended_by"]) != retained:
            problems.append(f"{row['name']}: retained {retained}, derived {(row['ok'], row['ended_by'])}")
        if row["ended_by"] == "ok" and row.get("metadata", {}).get("device") != "GPU":
            problems.append(f"{row['name']}: ran on {row['metadata'].get('device')!r}")
        blocking = row.get("metadata", {}).get("cacheblocking", {})
        requested = row["options"].get("blocking_qubits")
        if row["ended_by"] == "ok" and requested is not None and blocking.get("block_bits") != requested:
            problems.append(f"{row['name']}: block_bits {blocking.get('block_bits')} is not the requested chunk")
    for problem in problems:
        print(problem)
    print(f"{path}: {len(record['trials'])} trials, {len(problems)} differences")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
