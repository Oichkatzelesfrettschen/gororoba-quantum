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
``calibration_snapshot.lower_conditionals``: each body gate conditioned on the
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
import math
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
        return calibration_snapshot.lower_conditionals(circuit_for("dynamic", width))

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
            except IndexError, ValueError:
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
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.one:
        print(json.dumps(run_one(json.loads(args.one))), flush=True)
        return 0
    names = {trial_name(t): t for t in TRIALS}
    chosen = list(TRIALS) if not args.trials else [names[name] for name in args.trials.split(",")]
    if args.check:
        return check(args.check, [trial_name(trial) for trial in chosen])
    if args.self_test:
        print(f"aer_blocking_probe: {self_test()}")
        return 0
    if args.out is None:
        parser.error("--out is required")
    devices = aer_gpu_probe.gpus()
    if not devices:
        raise SystemExit(aer_gpu_probe.NO_GPU)
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
        # Written before the first trial, so a record cut off mid-run keeps
        # the trials it was meant to hold and --check names the missing ones.
        "planned": [trial_name(trial) for trial in chosen],
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


def check(path: Path, requested: list[str]) -> int:
    """Re-derive every trial's ok and ended_by and the record's chunk sizes; exit 1 on any difference.

    The trials must be the record's planned list; a collected record made
    before the probe wrote one checks against requested, the trials of the
    --trials argument (every TRIALS entry by default), while its
    collect.json sha256 pins its bytes.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    planned = record.get("planned", requested)
    found = [row["name"] for row in record["trials"]]
    if found != planned:
        missing = [name for name in planned if name not in found]
        problems.append(f"{len(found)} of {len(planned)} planned trials; missing {missing[:3]}")
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


TOY_WIDTH, TOY_CHUNK, TOY_SHOTS, TOY_E10, TOY_E01 = 6, 3, 4000, 0.05, 0.10


def readout_toy(flip: bool = False) -> Any:
    """Qubit 0's recorded bit, read through a readout channel, conditions an X on the top qubit outside a chunk.

    Qubit 0 stays in |0>, so its recorded bit reads 1 only through the
    readout channel; a condition evaluated before that channel never flips
    the top qubit, and a correct one flips it in exactly the shots that
    recorded a 1. flip tests the opposite value, the negative control.
    """
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    qubits = QuantumRegister(TOY_WIDTH, "q")
    mid, out = ClassicalRegister(1, "mid"), ClassicalRegister(TOY_WIDTH, "out")
    circuit = QuantumCircuit(qubits, mid, out)
    circuit.h(1)
    circuit.cx(1, TOY_WIDTH - 2)
    circuit.measure(0, mid[0])
    with circuit.if_test((mid[0], 0 if flip else 1)):
        circuit.x(TOY_WIDTH - 1)
    circuit.measure(qubits, out)
    return circuit


def toy_counts(circuit: Any, method: str, device: str, options: dict[str, Any]) -> dict[str, int]:
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, ReadoutError

    noise = NoiseModel()
    noise.add_readout_error(ReadoutError([[1 - TOY_E10, TOY_E10], [TOY_E01, 1 - TOY_E01]]), [0])
    simulator = AerSimulator(method=method, device=device, noise_model=noise, **options)
    result = simulator.run(circuit, shots=TOY_SHOTS, seed_simulator=SEED).result()
    if options and result.results[0].metadata.get("cacheblocking", {}).get("block_bits") != options["blocking_qubits"]:
        raise SystemExit(f"aer_blocking_probe: the {device} {method} toy ran without its {TOY_CHUNK}-qubit chunks")
    return dict(sorted(result.get_counts().items()))


def else_toy(width: int) -> Any:
    """An if_else with an else body on width qubits, which has no conditioned-gate form."""
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(width, 2, name=f"else{width}")
    circuit.h(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)) as orelse:
        circuit.x(1)
    with orelse:
        circuit.x(width - 1)
    circuit.measure(1, 1)
    return circuit


def toy_contract(method: str, device: str) -> None:
    """The lowered toy under blocking: on a GPU the if_else toy's counts, on the CPU a condition off its bit.

    Aer's GPU chunk executor applies a bfunc-conditioned gate after the
    readout channel on the recorded bit, so the blocked lowered toy draws the
    if_else toy's seeded counts. Its CPU executor under the same blocking
    draws outcomes whose top qubit disagrees with the recorded bit, which is
    why SnapshotSimulator.run applies blocking_options on a GPU device only.
    """
    forced = {"blocking_enable": True, "blocking_qubits": TOY_CHUNK, "max_parallel_shots": 1}
    # A device of 0 MiB puts every width past one GPU, so blocked_batch takes
    # its blocking path on the six-qubit toy.
    lowered, blocking = calibration_snapshot.blocked_batch([readout_toy()], method, 0)
    if not blocking or calibration_snapshot.has_control_flow(lowered[0]):
        raise SystemExit("aer_blocking_probe: blocked_batch left the toy unlowered")
    blocked = toy_counts(lowered[0], method, device, forced)
    # Keys read "out mid"; out's leftmost character is the conditioned top qubit.
    on_bit = all(key.split()[0][0] == key.split()[1] for key in blocked)
    if device == "CPU":
        if on_bit:
            raise SystemExit("aer_blocking_probe: CPU cache blocking keeps the condition; revisit the GPU-only rule")
        return
    if blocked != toy_counts(readout_toy(), method, device, {}) or not on_bit:
        raise SystemExit(f"aer_blocking_probe: the blocked {device} {method} toy differs from the if_else toy")
    ones = sum(value for key, value in blocked.items() if key.split()[1] == "1")
    if abs(ones - TOY_E10 * TOY_SHOTS) > 5 * math.sqrt(TOY_SHOTS * TOY_E10 * (1 - TOY_E10)):
        raise SystemExit(f"aer_blocking_probe: {ones} recorded ones is off the readout channel's {TOY_E10}")
    flipped = calibration_snapshot.lower_conditionals(readout_toy(flip=True))
    if toy_counts(flipped, method, device, forced) == blocked:
        raise SystemExit("aer_blocking_probe: the toy's condition does not reach its outcome")


def run_contract() -> None:
    """SnapshotSimulator.run blocks a GPU batch past its chunk, lowers its if_else, and keeps the seeded counts.

    blocking_options is replaced by the toy's forced chunk, so the six-qubit
    toy takes the path a state wider than one GPU takes. The batch also holds
    an else-body if_else as wide as the chunk, which Aer runs whole: it keeps
    its control flow and draws its unblocked counts.
    """
    from qiskit_aer.noise import NoiseModel, ReadoutError

    noise = NoiseModel()
    noise.add_readout_error(ReadoutError([[1 - TOY_E10, TOY_E10], [TOY_E01, 1 - TOY_E01]]), [0])

    def counts() -> tuple[list[dict[str, int]], list[Any]]:
        simulator = calibration_snapshot.SnapshotSimulator(method="statevector", device="GPU", noise_model=noise)
        batch = [readout_toy(), else_toy(TOY_CHUNK)]
        result = simulator.run(batch, shots=TOY_SHOTS, seed_simulator=SEED).result()
        return (
            [dict(sorted(result.get_counts(index).items())) for index in range(len(batch))],
            [experiment.metadata.get("cacheblocking") for experiment in result.results],
        )

    plain, unblocked = counts()
    original = calibration_snapshot.blocking_options
    calibration_snapshot.blocking_options = lambda method, width, memory: {  # type: ignore[assignment]
        "blocking_enable": True,
        "blocking_qubits": TOY_CHUNK,
        "max_parallel_shots": 1,
    }
    try:
        blocked, metadata = counts()
    finally:
        calibration_snapshot.blocking_options = original
    if any(unblocked) or (metadata[0] or {}).get("block_bits") != TOY_CHUNK or metadata[1] or blocked != plain:
        raise SystemExit(f"aer_blocking_probe: SnapshotSimulator.run chunks {metadata}, counts kept {blocked == plain}")


def self_test() -> str:
    """Chunk sizes, the blocking trigger, active width, refusal, and the readout toy under blocking."""
    from qiskit import ClassicalRegister, QuantumCircuit

    sizes = {
        (method, memory): calibration_snapshot.blocking_qubits_for(method, memory)
        for method in ("statevector", "density_matrix")
        for memory in (15360, 12282)
    }
    if set(sizes.values()) != {27, 13} or any(
        calibration_snapshot.state_bytes(method, bits) > (memory << 20) // 4
        or calibration_snapshot.state_bytes(method, bits + 1) <= (memory << 20) // 4
        for (method, memory), bits in sizes.items()
    ):
        raise SystemExit(f"aer_blocking_probe: blocking_qubits_for gave {sizes}")
    t4 = 15360
    decisions = {
        (method, width): bool(calibration_snapshot.blocking_options(method, width, t4))
        for method, width in (("statevector", 29), ("statevector", 30), ("density_matrix", 14), ("density_matrix", 15))
    }
    if decisions != {
        ("statevector", 29): False,
        ("statevector", 30): True,
        ("density_matrix", 14): False,
        ("density_matrix", 15): True,
    }:
        raise SystemExit(f"aer_blocking_probe: blocking_options decided {decisions} on a T4")
    if calibration_snapshot.blocking_options("statevector", 40, None) or calibration_snapshot.blocking_options(
        "matrix_product_state", 40, t4
    ):
        raise SystemExit("aer_blocking_probe: blocking_options blocked without a GPU or for an unchunked method")
    wide = QuantumCircuit(156, 7)
    wide.h(3)
    for a, b in ((3, 4), (4, 5), (5, 16), (16, 23), (23, 24), (24, 25)):
        wide.cx(a, b)
    wide.barrier()
    wide.measure([3, 4, 5, 16, 23, 24, 25], range(7))
    sized = calibration_snapshot.blocked_batch([wide], "statevector", t4)[1]
    if calibration_snapshot.active_qubits(wide) != 7 or sized:
        raise SystemExit(
            "aer_blocking_probe: a barriered 156-qubit circuit with 7 active qubits was sized by its register"
        )
    with_else = QuantumCircuit(TOY_WIDTH, 1)
    with_else.measure(0, 0)
    with with_else.if_test((with_else.clbits[0], 1)) as orelse:
        with_else.x(1)
    with orelse:
        with_else.x(2)
    with_else.add_register(ClassicalRegister(1, "extra"))
    try:
        calibration_snapshot.blocked_batch([with_else], "statevector", 0)
    except ValueError:
        pass
    else:
        raise SystemExit("aer_blocking_probe: blocked_batch accepted an if_else with an else body")
    # On a T4 the 30-qubit statevector blocks at 27-qubit chunks, so only a
    # circuit wider than 27 active qubits loses its if_else.
    thirty = QuantumCircuit(30)
    thirty.h(range(30))
    narrow = else_toy(TOY_WIDTH)
    mixed, mixed_blocking = calibration_snapshot.blocked_batch([thirty, narrow], "statevector", t4)
    if not mixed_blocking or mixed[1] is not narrow:
        raise SystemExit("aer_blocking_probe: blocked_batch lowered a circuit narrower than its chunk")
    wide_else = else_toy(28)
    wide_else.h(range(28))
    try:
        calibration_snapshot.blocked_batch([thirty, wide_else], "statevector", t4)
    except ValueError:
        pass
    else:
        raise SystemExit("aer_blocking_probe: blocked_batch accepted an else body wider than its chunk")
    toy_contract("statevector", "CPU")
    from qiskit_aer import AerSimulator

    gpu = "no GPU or no GPU Aer build here, so the GPU toy did not run"
    # Aer's GPU builds list GPU whether or not a device exists, and its CPU
    # build lists CPU only, so both readings gate the GPU contracts.
    if aer_gpu_probe.gpus() and "GPU" in AerSimulator().available_devices():
        for method in ("statevector", "density_matrix"):
            toy_contract(method, "GPU")
        run_contract()
        gpu = (
            "on the GPU it draws the if_else counts, the condition on the recorded bit (statevector, density "
            "matrix), and SnapshotSimulator.run blocks and lowers the if_else toy and runs a chunk-wide else body "
            "whole, both with their counts unchanged"
        )
    return (
        f"chunks {sorted(set(sizes.values()))}; a T4 blocks statevector 30 and density matrix 15, not 29 or 14; "
        f"a 156-qubit circuit counts its 7 active qubits; an else body wider than the chunk is refused and one "
        f"within it kept; under {TOY_CHUNK}-qubit chunks "
        f"the CPU's lowered readout toy leaves its condition's bit; {gpu}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
