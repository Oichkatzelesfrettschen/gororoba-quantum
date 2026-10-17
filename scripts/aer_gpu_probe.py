"""Aer sampler configurations timed on one machine's CPU and GPUs, with GPU utilization per row.

Each row runs one configuration on one workload in its own process, so an
Aer abort ends only that row. Three workload families run:

- toy: one qubit measured into c0, an X conditioned on c0, and a second
  measurement, under an asymmetric readout channel only (TOY_E10, TOY_E01)
  at TOY_SHOTS shots; each configuration's counts are scored against the
  law toy_expected, in which the condition reads the recorded bit.
- n21 (under retained calibration noise, calibration_snapshot.noise_simulator):
  the N=21 order-finding circuits of scripts/n21_conjugation_noise.py
  under the coset-281 work-register encoding (columns 1, 2, 5, 13, 25) and
  the ibm_fez snapshot, restricted to their 7 active qubits:
  two_round_encoded_ff (one mid-circuit measurement, one reset, one if_else),
  two_round_encoded_noff (the same without the if_else, so its program has
  no control flow), and ten_round_encoded (ten measurements, nine resets,
  45 if_else). Every row runs the shot tiers SHOT_TIERS up to the circuit's
  full count while the fit t = a + b * shots through the measured tiers
  predicts a run within BUDGET_SECONDS; the smallest tier always runs.
- width: scripts/substrate_crossover.py's batch of 8 layered circuits on a
  chain of ibm_kingston qubits at WIDTH_SHOTS shots, static (terminal
  measurement only) and dynamic (one mid-circuit measurement and one
  if_test), on the GPU configurations of WIDTH_CONFIGURATIONS: 7, 10 and 14
  qubits for the density matrix (WIDTHS) and up to 24 for the statevector
  (STATEVECTOR_WIDTHS), whose GPU kernels stay underoccupied at 14 qubits.
  A series stops at the first width whose run exceeds BUDGET_SECONDS.

Configurations (CONFIGURATIONS) name a device, a method and Aer options:
statevector trajectories, shot branching (shot_branching_enable with
shot_branching_sampling_enable), batched_shots_gpu with if_else lowered
into bfunc-conditioned gates (lower_conditionals, a timing path only: the
batched executor evaluates such a condition before the readout channel) and
without it (Aer's own jump program), cuStateVec_enable, the density
matrix, noise_simulator's GPU default through SnapshotSimulator.run
(gpu_statevector_default), and on a machine with two or more GPUs the
batched sampler pinned to one GPU with target_gpus.

Before each row the parent waits, up to IDLE_WAIT_SECONDS, until no GPU
compute process outside the desktop graphics set runs, the 1-minute load is
below the CPU count and other work holds at most FOREIGN_CPU_LIMIT CPUs, then
records that reading and the GPU's utilization and memory as the row's
baseline; during the row it samples the GPU every GPU_SAMPLE_MS, and after
it reads the load again and the CPUs other processes held. A row whose load
exceeded the CPU count at its start or end is contended and runs once more
after the matrix. The parent creates no CUDA context.

``--check FILE`` recomputes every derived value of a retained record (ms
per shot, the per-row fit, utilization summaries, counts identity, speedups
the two-round total variation against cpu_statevector, and each readout-toy
row's z scores and verdict) from its raw timings, samples and counts, and
requires each to equal the stored value. It then replays two CPU contracts:
the default CPU simulator keeps the readout-toy law, and a lowered
feed-forward circuit draws the if_else circuit's seeded counts byte for
byte while flipping or dropping the condition changes them.

Usage:
    "$PYTHON" scripts/aer_gpu_probe.py --out PATH [--workloads toy,n21,width] [--configurations A,B]
    "$PYTHON" scripts/aer_gpu_probe.py --check PATH
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

SCHEMA = "aer-gpu-probe-v2"
N21_SNAPSHOT = "docs/evidence/calibration/history/ibm_fez/20261016T1212520700.json"
WIDTH_SNAPSHOT = "docs/evidence/calibration/ibm_kingston.json"
COLUMNS = (1, 2, 5, 13, 25)
SEED = 20261016
N21_CIRCUITS = {"two_round_encoded_ff": 32768, "two_round_encoded_noff": 32768, "ten_round_encoded": 16384}
SHOT_TIERS = (32, 256, 2048, 16384, 32768)
WIDTHS = (7, 10, 14)
STATEVECTOR_WIDTHS = (7, 10, 14, 20, 24)
WIDTH_SHOTS = 2048
BUDGET_SECONDS = 60.0
# A tier whose first run is shorter than this repeats REPEATS times in all
# and keeps every time; a longer tier runs once.
REPEAT_BELOW_SECONDS = 15.0
REPEATS = 3
ROW_TIMEOUT_SECONDS = 1800
IDLE_WAIT_SECONDS = 30
IDLE_POLL_SECONDS = 10
IDLE_WINDOW_SECONDS = 2.0
GPU_SAMPLE_MS = 200
# Other work above this many CPUs (desktop processes hold about one) makes
# the pre-row reading busy; the parent waits up to IDLE_WAIT_SECONDS for it.
FOREIGN_CPU_LIMIT = 1.5
# Desktop processes that hold a graphics context on a workstation GPU; any
# other compute process is foreign load.
GRAPHICS_PROCESSES = ("kwin_wayland", "plasmashell", "Xwayland", "Xorg", "firefox", "Discord", "chrome", "kded")
METADATA_KEYS = (
    "device",
    "method",
    "batched_shots_optimization",
    "batched_shots_optimization_parallel_gpus",
    "parallel_shots",
    "gpu_parallel_shots_",
    "parallel_state_update",
    "shot_branching_enabled",
    "runtime_noise_sampling_enabled",
    "target_gpus",
    "cuStateVec_enable",
    "noise",
    "measure_sampling",
    "fusion",
)
BRANCHING = {"shot_branching_enable": True, "shot_branching_sampling_enable": True}
# label: (device, method, Aer options, lower if_else, needs two or more GPUs)
CONFIGURATIONS: dict[str, tuple[str, str, dict[str, Any], bool, bool]] = {
    "cpu_statevector": ("CPU", "statevector", {}, False, False),
    "cpu_statevector_branching": ("CPU", "statevector", BRANCHING, False, False),
    "cpu_density_matrix": ("CPU", "density_matrix", {}, False, False),
    "gpu_statevector_unbatched": ("GPU", "statevector", {"batched_shots_gpu": False}, False, False),
    "gpu_statevector_branching": ("GPU", "statevector", {"batched_shots_gpu": False, **BRANCHING}, False, False),
    "gpu_statevector_batched_jump": ("GPU", "statevector", {"batched_shots_gpu": True}, False, False),
    "gpu_statevector_batched": ("GPU", "statevector", {"batched_shots_gpu": True}, True, False),
    "gpu_statevector_batched_gpu0": (
        "GPU",
        "statevector",
        {"batched_shots_gpu": True, "target_gpus": [0]},
        True,
        True,
    ),
    "gpu_statevector_custatevec": (
        "GPU",
        "statevector",
        {"batched_shots_gpu": False, "cuStateVec_enable": True},
        False,
        False,
    ),
    "gpu_density_matrix_unbatched": ("GPU", "density_matrix", {"batched_shots_gpu": False}, False, False),
    "gpu_density_matrix_batched": ("GPU", "density_matrix", {"batched_shots_gpu": True}, True, False),
    "gpu_density_matrix_custatevec": (
        "GPU",
        "density_matrix",
        {"batched_shots_gpu": False, "cuStateVec_enable": True},
        False,
        False,
    ),
    "gpu_statevector_default": ("GPU", "statevector", {"batched_shots_gpu": True}, False, False),
}
# Rows of the readout toy only: shot branching under the density matrix.
TOY_CONFIGURATIONS: dict[str, tuple[str, str, dict[str, Any], bool, bool]] = {
    "cpu_density_matrix_branching": ("CPU", "density_matrix", BRANCHING, False, False),
    "gpu_density_matrix_branching": ("GPU", "density_matrix", {"batched_shots_gpu": False, **BRANCHING}, False, False),
}
WIDTH_CONFIGURATIONS = (
    "gpu_statevector_unbatched",
    "gpu_statevector_batched",
    "gpu_statevector_custatevec",
    "gpu_density_matrix_unbatched",
    "gpu_density_matrix_batched",
    "gpu_density_matrix_custatevec",
)
PACKAGES = (
    "qiskit",
    "qiskit-aer",
    "qiskit-aer-gpu",
    "qiskit-aer-gpu-cu11",
    "cuquantum-cu11",
    "custatevec-cu11",
    "cutensornet-cu11",
    "cutensor-cu11",
    "cuquantum-python-cu11",
    "nvidia-cuda-runtime-cu11",
    "numpy",
)
DERIVED_ROW_KEYS = (
    "expected_counts",
    "z_scores",
    "keeps_readout_law",
    "utilization",
    "fit",
    "ms_per_shot",
    "counts_identical_to_cpu_statevector",
    "speedup_vs_cpu_statevector",
    "speedup_at_shots",
    "tvd_to_cpu_statevector",
    "sampling_scale",
)


# ---------------------------------------------------------------- machine


def run_text(command: list[str]) -> str:
    if shutil.which(command[0]) is None:
        return ""
    return subprocess.run(command, capture_output=True, text=True, check=False).stdout


def gpus() -> list[dict[str, str]]:
    fields = ("index", "name", "driver_version", "memory.total", "compute_cap")
    listing = run_text(["nvidia-smi", f"--query-gpu={','.join(fields)}", "--format=csv,noheader,nounits"])
    return [
        dict(zip(fields, (part.strip() for part in line.split(",")), strict=True))
        for line in listing.splitlines()
        if line.strip()
    ]


def cuda_driver_version() -> str | None:
    # nvidia-smi prints "CUDA Version: X" on older drivers and "CUDA UMD
    # Version: X" on newer ones.
    found = re.search(r"CUDA (?:UMD )?Version:\s*(\S+)", run_text(["nvidia-smi"]))
    return found.group(1) if found else None


def cpu_model() -> str | None:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    arch = run_text(["pacman", "-Q", "python-qiskit-aer-cuda"]).strip()
    versions["arch:python-qiskit-aer-cuda"] = arch.split()[-1] if arch else None
    return versions


def compute_apps() -> list[dict[str, str]]:
    listing = run_text(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"])
    apps = []
    for line in listing.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 3:
            name = parts[1].split()[0].rsplit("/", 1)[-1] if parts[1] else ""
            apps.append({"pid": parts[0], "process": name, "memory": parts[-1]})
    return apps


def foreign(apps: list[dict[str, str]]) -> list[dict[str, str]]:
    return [app for app in apps if not app["process"].startswith(GRAPHICS_PROCESSES)]


def gpu_reading() -> list[dict[str, float]]:
    listing = run_text(["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used", "--format=csv,noheader,nounits"])
    rows = []
    for line in listing.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 3:
            rows.append({"gpu": int(parts[0]), "utilization": float(parts[1]), "memory_mib": float(parts[2])})
    return rows


def foreign_cpus(window: float = IDLE_WINDOW_SECONDS) -> float | None:
    """CPUs held by processes outside this probe over the next window seconds."""
    busy, own = busy_cpu_seconds(), own_cpu_seconds()
    time.sleep(window)
    after = busy_cpu_seconds()
    if busy is None or after is None:
        return None
    return round(((after - busy) - (own_cpu_seconds() - own)) / window, 2)


def wait_idle(cpus: int) -> dict[str, Any]:
    """The reading this row starts from, after waiting up to IDLE_WAIT_SECONDS for foreign load to clear.

    Idle means no GPU compute process outside the desktop graphics set, a
    1-minute load below the CPU count, and at most FOREIGN_CPU_LIMIT CPUs
    of other work over IDLE_WINDOW_SECONDS.
    """
    started = time.monotonic()
    while True:
        apps = compute_apps()
        load = os.getloadavg()[0]
        busy = foreign(apps)
        held = foreign_cpus()
        quiet = not busy and load < cpus and (held is None or held <= FOREIGN_CPU_LIMIT)
        waited = time.monotonic() - started
        if quiet or waited >= IDLE_WAIT_SECONDS:
            return {
                "compute_apps": apps,
                "foreign_compute_apps": busy,
                "load_1min": round(load, 2),
                "foreign_cpus_before_row": held,
                "cpus": cpus,
                "idle": quiet,
                "waited_seconds": round(waited, 1),
                "gpu_baseline": gpu_reading(),
            }
        time.sleep(IDLE_POLL_SECONDS)


def sample_gpu(command: list[str], ngpus: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run command while nvidia-smi samples every GPU each GPU_SAMPLE_MS; the child's outcome and the samples."""
    sampler = None
    if ngpus:
        sampler = subprocess.Popen(
            [
                "nvidia-smi",
                "--query-gpu=timestamp,index,utilization.gpu,memory.used",
                "--format=csv,noheader,nounits",
                f"-lms={GPU_SAMPLE_MS}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    started = time.time()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=ROW_TIMEOUT_SECONDS)
        outcome: dict[str, Any] = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        outcome = {"returncode": None, "stdout": "", "stderr": f"row exceeded {ROW_TIMEOUT_SECONDS} s"}
    outcome["wall_seconds"] = round(time.time() - started, 3)
    samples: list[dict[str, Any]] = []
    if sampler is not None:
        # SIGINT ends nvidia-smi's loop with its buffered samples flushed;
        # SIGTERM discards the unflushed tail of the pipe buffer.
        sampler.send_signal(signal.SIGINT)
        text, _ = sampler.communicate()
        for line in text.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) != 4:
                continue
            try:
                sample = {"time": parts[0], "gpu": int(parts[1]), "utilization": float(parts[2])}
                sample["memory_mib"] = float(parts[3])
            except ValueError:
                continue
            samples.append(sample)
    return outcome, samples


# ---------------------------------------------------------------- derived values


def fit(points: list[tuple[int, float]]) -> dict[str, float] | None:
    """Least-squares t = a + b * shots through (shots, best seconds) points; None below two distinct shot counts."""
    if len({shots for shots, _ in points}) < 2:
        return None
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    sxx = sum((x - mean_x) ** 2 for x, _ in points)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sxx
    return {"fixed_seconds": round(mean_y - slope * mean_x, 4), "ms_per_shot": round(1e3 * slope, 5)}


def predicted(points: list[tuple[int, float]], shots: int) -> float:
    line = fit(points)
    if line is None:
        x, y = points[-1]
        return y * shots / x
    return max(points[-1][1], line["fixed_seconds"] + line["ms_per_shot"] * shots / 1e3)


def utilization_summary(samples: list[dict[str, Any]], baseline: list[dict[str, float]]) -> dict[str, Any]:
    """Per GPU: the baseline reading, the mean and peak utilization over the row, and peak memory above baseline."""
    summary: dict[str, Any] = {}
    for reading in baseline:
        gpu = reading["gpu"]
        mine = [sample for sample in samples if sample["gpu"] == gpu]
        entry: dict[str, Any] = {
            "baseline_utilization": reading["utilization"],
            "baseline_memory_mib": reading["memory_mib"],
            "samples": len(mine),
        }
        if mine:
            mean = sum(sample["utilization"] for sample in mine) / len(mine)
            entry["mean_utilization"] = round(mean, 2)
            entry["peak_utilization"] = max(sample["utilization"] for sample in mine)
            entry["mean_above_baseline"] = round(mean - reading["utilization"], 2)
            entry["peak_memory_above_baseline_mib"] = max(s["memory_mib"] for s in mine) - reading["memory_mib"]
        summary[str(gpu)] = entry
    return summary


def counts_digest(counts: Any) -> str:
    return hashlib.sha256(json.dumps(counts, sort_keys=True).encode()).hexdigest()


def labeled(counts: dict[str, int]) -> list[float]:
    shots = sum(counts.values())
    distribution = [0.0] * 4
    for key, count in counts.items():
        distribution[int(key.replace(" ", ""), 2)] += count / shots
    return distribution


def row_key(row: dict[str, Any]) -> tuple[str, ...]:
    return (row["workload"], row["circuit"], str(row.get("width")))


def derive_toy(row: dict[str, Any]) -> None:
    """Each toy outcome's binomial z score against toy_expected, and whether the row keeps the readout law."""
    row["utilization"] = utilization_summary(row["gpu_samples"], row["environment"]["gpu_baseline"])
    shots = sum(row["counts"].values())
    law = toy_expected(TOY_E10, TOY_E01)
    scores = {}
    for key, p in law.items():
        scores[key] = round((row["counts"].get(key, 0) - shots * p) / math.sqrt(shots * p * (1 - p)), 2)
    row["expected_counts"] = {key: round(shots * p, 1) for key, p in law.items()}
    row["z_scores"] = scores
    row["keeps_readout_law"] = max(abs(z) for z in scores.values()) <= TOY_Z_LIMIT


def derive(record: dict[str, Any]) -> None:
    """Fill every derived field of a record from its raw timings, samples and counts."""
    reference: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in record["rows"]:
        if row["workload"] == "toy" and "counts" in row:
            derive_toy(row)
        if "tiers" not in row:
            continue
        row["utilization"] = utilization_summary(row["gpu_samples"], row["environment"]["gpu_baseline"])
        per_circuit_shots = row.get("batch", 1)
        for tier in row["tiers"]:
            tier["best_seconds"] = min(tier["seconds"])
            tier["ms_per_shot"] = round(1e3 * tier["best_seconds"] / (per_circuit_shots * tier["shots"]), 5)
        if row["workload"] == "n21":
            row["fit"] = fit([(tier["shots"], tier["best_seconds"]) for tier in row["tiers"]])
        else:
            row["ms_per_shot"] = row["tiers"][0]["ms_per_shot"]
        if row["configuration"] == "cpu_statevector":
            reference[row_key(row)] = row
    for row in record["rows"]:
        ref = reference.get(row_key(row)) if "tiers" in row else None
        if ref is None or ref is row:
            continue
        by_shots = {tier["shots"]: tier for tier in ref["tiers"]}
        common = [tier for tier in row["tiers"] if tier["shots"] in by_shots]
        row["counts_identical_to_cpu_statevector"] = {
            str(tier["shots"]): tier["counts_sha256"] == by_shots[tier["shots"]]["counts_sha256"] for tier in common
        }
        if not common:
            continue
        last = common[-1]
        theirs = by_shots[last["shots"]]
        row["speedup_vs_cpu_statevector"] = round(theirs["best_seconds"] / last["best_seconds"], 3)
        row["speedup_at_shots"] = last["shots"]
        if "distribution" in last and "distribution" in theirs:
            pairs = zip(last["distribution"], theirs["distribution"], strict=True)
            row["tvd_to_cpu_statevector"] = round(0.5 * sum(abs(a - b) for a, b in pairs), 6)
            # Four outcomes: two independent samples of n shots differ in
            # total variation on the scale sqrt(2 / n).
            row["sampling_scale"] = round(math.sqrt(2 / last["shots"]), 6)


# ---------------------------------------------------------------- child


def n21_circuit(name: str) -> tuple[Any, dict[str, Any]]:
    from n21_conjugation_noise import _backend, circuits
    from qiskit.transpiler import generate_preset_pass_manager

    import snapshot_laws

    snapshot = json.loads((ROOT / N21_SNAPSHOT).read_text(encoding="utf-8"))
    compiled = generate_preset_pass_manager(
        optimization_level=3, target=_backend(snapshot).target, seed_transpiler=0
    ).run(circuits(COLUMNS, COLUMNS)[name])
    isa, qubits = snapshot_laws.restrict_circuit(compiled)
    return isa, snapshot_laws.restrict(snapshot, qubits)


def simulator_for(snapshot: dict[str, Any], label: str) -> Any:
    import calibration_snapshot
    import parallel

    device, method, options, _, _ = CONFIGURATIONS[label]
    batched = bool(options.get("batched_shots_gpu"))
    custatevec = bool(options.get("cuStateVec_enable"))
    simulator = calibration_snapshot.noise_simulator(
        snapshot, device, method=method, batched_shots=batched, custatevec=custatevec
    )
    extra = {key: value for key, value in options.items() if key not in ("batched_shots_gpu", "cuStateVec_enable")}
    simulator.set_options(max_parallel_threads=parallel.workers(), **extra)
    return simulator


TOY_E10, TOY_E01, TOY_SHOTS = 0.05, 0.10, 200000
# A configuration keeps the toy's readout law when every outcome count lies
# within this many binomial standard deviations of toy_expected.
TOY_Z_LIMIT = 5.0
TOY_LABELS = (
    "cpu_statevector",
    "cpu_statevector_branching",
    "cpu_density_matrix",
    "cpu_density_matrix_branching",
    "gpu_statevector_unbatched",
    "gpu_statevector_branching",
    "gpu_density_matrix_unbatched",
    "gpu_density_matrix_branching",
    "gpu_statevector_batched",
    "gpu_density_matrix_batched",
    "gpu_statevector_default",
)


def lower_conditionals(circuit: Any) -> Any:
    """circuit with every if_else replaced by its true body's gates, each conditioned on the same test.

    AerCompiler inlines an if_else into mark and jump instructions, which
    Aer's batched GPU executor rejects. Aer's assemble_circuit turns an
    operation's ``condition`` (a Clbit or ClassicalRegister and a value)
    into a bfunc register that gates it. A one-level if_else without an else
    body whose true body holds gates only has that form. The result is the
    circuit itself without control flow, and None when an instruction has no
    such form (an else body, an expression condition, a measurement, reset or
    nested control flow inside the body, or a loop or switch).
    """
    from qiskit.circuit import Gate

    import calibration_snapshot

    if not calibration_snapshot.has_control_flow(circuit):
        return circuit
    lowered = circuit.copy_empty_like()
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name not in calibration_snapshot.CONTROL_FLOW:
            lowered.append(instruction)
            continue
        condition = getattr(operation, "condition", None)
        if operation.name != "if_else" or not isinstance(condition, tuple) or operation.params[1] is not None:
            return None
        body = operation.params[0]
        wires = dict(zip(body.qubits, instruction.qubits, strict=True))
        for inner in body.data:
            if not isinstance(inner.operation, Gate) or inner.clbits:
                return None
            gate = inner.operation.to_mutable()
            gate.condition = condition
            lowered.append(gate, [wires[q] for q in inner.qubits])
    return lowered


def execute(simulator: Any, label: str, circuits: Any, shots: int) -> Any:
    """The configuration's run: a lowering configuration submits lower_conditionals' circuits.

    SnapshotSimulator.run turns batching off for circuits with control flow,
    so a configuration that times Aer's own batched program
    (gpu_statevector_batched_jump) calls AerSimulator.run directly.
    """
    from qiskit_aer import AerSimulator

    if {**CONFIGURATIONS, **TOY_CONFIGURATIONS}[label][3]:
        batch = circuits if isinstance(circuits, list) else [circuits]
        lowered = [lower_conditionals(circuit) for circuit in batch]
        if any(circuit is None for circuit in lowered):
            raise RuntimeError("a circuit has no bfunc-conditioned form")
        circuits = lowered if isinstance(circuits, list) else lowered[0]
    if label == "gpu_statevector_default":
        return simulator.run(circuits, shots=shots, seed_simulator=SEED).result()
    run = AerSimulator.run.__get__(simulator)
    return run(circuits, shots=shots, seed_simulator=SEED).result()


def warm_up(simulator: Any, label: str) -> float:
    """One small circuit on the configured device, so CUDA context creation stays out of the timed runs."""
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2, 2)
    circuit.sx(0)
    circuit.cz(0, 1)
    circuit.measure([0, 1], [0, 1])
    started = time.perf_counter()
    execute(simulator, label, circuit, 16)
    return round(time.perf_counter() - started, 3)


def metadata_of(result: Any) -> dict[str, Any]:
    metadata = result.results[0].metadata
    return {key: metadata[key] for key in METADATA_KEYS if key in metadata}


def timed(simulator: Any, label: str, circuits: Any, shots: int) -> tuple[Any, float]:
    started = time.perf_counter()
    result = execute(simulator, label, circuits, shots)
    seconds = time.perf_counter() - started
    if not result.success:
        raise RuntimeError(str(result.status))
    return result, seconds


def measure_n21(name: str, label: str) -> dict[str, Any]:
    isa, snapshot = n21_circuit(name)
    simulator = simulator_for(snapshot, label)
    row: dict[str, Any] = {"warm_up_seconds": warm_up(simulator, label), "tiers": []}
    points: list[tuple[int, float]] = []
    for shots in (tier for tier in SHOT_TIERS if tier <= N21_CIRCUITS[name]):
        if points and predicted(points, shots) > BUDGET_SECONDS:
            row["stopped_before_shots"] = shots
            break
        result, seconds = timed(simulator, label, isa, shots)
        times = [round(seconds, 4)]
        if seconds < REPEAT_BELOW_SECONDS:
            times += [round(timed(simulator, label, isa, shots)[1], 4) for _ in range(REPEATS - 1)]
        counts = dict(sorted(result.get_counts().items()))
        tier: dict[str, Any] = {"shots": shots, "seconds": times, "counts_sha256": counts_digest(counts)}
        if name.startswith("two_round"):
            tier["counts"] = counts
            tier["distribution"] = labeled(counts)
        row["tiers"].append(tier)
        row.setdefault("metadata", metadata_of(result))
        points.append((shots, min(times)))
    row["routed_cz"] = int(isa.count_ops().get("cz", 0))
    return row


def measure_width(dynamic: bool, width: int, label: str) -> dict[str, Any]:
    import substrate_crossover

    snapshot = json.loads((ROOT / WIDTH_SNAPSHOT).read_text(encoding="utf-8"))
    batch = substrate_crossover.circuits(snapshot, width, dynamic)
    simulator = simulator_for(snapshot, label)
    row: dict[str, Any] = {"warm_up_seconds": warm_up(simulator, label), "batch": len(batch)}
    result, seconds = timed(simulator, label, batch, WIDTH_SHOTS)
    counts = [dict(sorted(result.get_counts(k).items())) for k in range(len(batch))]
    row["tiers"] = [{"shots": WIDTH_SHOTS, "seconds": [round(seconds, 4)], "counts_sha256": counts_digest(counts)}]
    row["metadata"] = metadata_of(result)
    return row


def toy_circuit() -> Any:
    """Measure |0> into c0, apply X when c0 reads 1, measure again into c1."""
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    q, c = QuantumRegister(1, "q"), ClassicalRegister(2, "c")
    circuit = QuantumCircuit(q, c)
    circuit.measure(0, c[0])
    with circuit.if_test((c[0], 1)):
        circuit.x(0)
    circuit.measure(0, c[1])
    return circuit


def toy_expected(e10: float, e01: float) -> dict[str, float]:
    """Outcome law of toy_circuit under the readout channel [[1 - e10, e10], [e01, 1 - e01]], keys c1 c0.

    The condition reads the recorded bit: a misread 1 flips the qubit, whose
    second readout then reads 1 unless the channel flips it back.
    """
    return {"00": (1 - e10) ** 2, "10": (1 - e10) * e10, "01": e10 * e01, "11": e10 * (1 - e01)}


def measure_toy(label: str) -> dict[str, Any]:
    from qiskit_aer.noise import NoiseModel, ReadoutError

    import calibration_snapshot

    device, method, options, _, _ = {**CONFIGURATIONS, **TOY_CONFIGURATIONS}[label]
    noise = NoiseModel()
    noise.add_readout_error(ReadoutError([[1 - TOY_E10, TOY_E10], [TOY_E01, 1 - TOY_E01]]), [0])
    simulator = calibration_snapshot.SnapshotSimulator(noise_model=noise, method=method, device=device, **options)
    result = execute(simulator, label, toy_circuit(), TOY_SHOTS)
    return {"counts": dict(sorted(result.get_counts().items())), "metadata": metadata_of(result)}


def child(spec: dict[str, Any]) -> dict[str, Any]:
    if spec["workload"] == "toy":
        return measure_toy(spec["configuration"])
    if spec["workload"] == "n21":
        return measure_n21(spec["circuit"], spec["configuration"])
    return measure_width(spec["circuit"] == "dynamic", spec["width"], spec["configuration"])


# ---------------------------------------------------------------- parent


def busy_cpu_seconds() -> float | None:
    """CPU seconds every process on the host has spent outside idle and iowait, from /proc/stat."""
    try:
        fields = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()[1:]
    except OSError:
        return None
    ticks = [int(value) for value in fields[:8]]
    return (sum(ticks) - ticks[3] - ticks[4]) / os.sysconf("SC_CLK_TCK")


def own_cpu_seconds() -> float:
    """CPU seconds of this process and of every child it has reaped, the GPU sampler included."""
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def attempt(spec: dict[str, Any], cpus: int, ngpus: int) -> dict[str, Any]:
    device, method, options, lower, _ = {**CONFIGURATIONS, **TOY_CONFIGURATIONS}[spec["configuration"]]
    row: dict[str, Any] = {
        **spec,
        "device": device,
        "method": method,
        "options": options,
        "lowered_if_else": lower,
        "environment": wait_idle(cpus),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    busy, own = busy_cpu_seconds(), own_cpu_seconds()
    outcome, samples = sample_gpu([sys.executable, "-B", __file__, "--one", json.dumps(spec)], ngpus)
    busy_after, own_after = busy_cpu_seconds(), own_cpu_seconds()
    row["environment"]["load_1min_end"] = round(os.getloadavg()[0], 2)
    if busy is not None and busy_after is not None:
        # Host CPU time outside this probe's process tree, averaged over the
        # row: the CPUs other work held while the row ran.
        foreign_seconds = (busy_after - busy) - (own_after - own)
        row["environment"]["foreign_cpus_during_row"] = round(foreign_seconds / max(outcome["wall_seconds"], 1e-9), 2)
    row["gpu_samples"] = samples
    row["process_wall_seconds"] = outcome["wall_seconds"]
    if outcome["returncode"] == 0:
        row.update(json.loads(outcome["stdout"].strip().splitlines()[-1]))
    else:
        row["failed"] = outcome["returncode"]
        row["stderr_tail"] = outcome["stderr"].strip().splitlines()[-3:]
    return row


def contended(row: dict[str, Any]) -> bool:
    """A 1-minute load above the CPU count at the row's start or end."""
    environment = row["environment"]
    return bool(environment["load_1min"] > environment["cpus"] or environment["load_1min_end"] > environment["cpus"])


def run_row(spec: dict[str, Any], cpus: int, ngpus: int) -> dict[str, Any]:
    row = attempt(spec, cpus, ngpus)
    row["contended"] = contended(row)
    return row


def skip_reason(label: str, ngpus: int) -> str | None:
    device, _, _, _, two = {**CONFIGURATIONS, **TOY_CONFIGURATIONS}[label]
    if device == "GPU" and ngpus == 0:
        return "no GPU on this machine"
    if two and ngpus < 2:
        return "needs two or more GPUs"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--workloads", default="toy,n21,width")
    parser.add_argument("--configurations", default=",".join(CONFIGURATIONS))
    parser.add_argument("--one", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.one:
        print(json.dumps(child(json.loads(args.one))), flush=True)
        return 0
    if args.check:
        return check(args.check)
    if args.out is None:
        parser.error("--out or --check is required")
    import parallel

    workloads = args.workloads.split(",")
    labels = args.configurations.split(",")
    unknown = sorted(set(labels) - set(CONFIGURATIONS))
    if unknown:
        parser.error(f"unknown configurations {unknown}")
    cpus = parallel.available_cpus()
    devices = gpus()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "machine": {
            "cpu": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "available_cpus": cpus,
            "workers": parallel.workers(),
            # A niced probe yields the CPU to other work, which lengthens its rows.
            "niceness": os.nice(0),
            "gpus": devices,
            "cuda_driver_version": cuda_driver_version(),
            "python": platform.python_version(),
            "packages": package_versions(),
        },
        "n21_snapshot": N21_SNAPSHOT,
        "width_snapshot": WIDTH_SNAPSHOT,
        "columns": list(COLUMNS),
        "seed": SEED,
        "shot_tiers": list(SHOT_TIERS),
        "width_shots": WIDTH_SHOTS,
        "budget_seconds": BUDGET_SECONDS,
        "gpu_sample_ms": GPU_SAMPLE_MS,
        "readout_toy": {"e10": TOY_E10, "e01": TOY_E01, "shots": TOY_SHOTS, "z_limit": TOY_Z_LIMIT},
        "rows": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)

    def emit(row: dict[str, Any]) -> None:
        record["rows"].append(row)
        derive(record)
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        brief = {key: row.get(key) for key in ("workload", "circuit", "width", "configuration", "failed", "skipped")}
        brief["ms_per_shot"] = [tier.get("ms_per_shot") for tier in row.get("tiers", [])]
        print(json.dumps(brief), flush=True)

    if "toy" in workloads:
        for label in TOY_LABELS:
            spec: dict[str, Any] = {"workload": "toy", "circuit": "readout_toy", "configuration": label}
            reason = skip_reason(label, len(devices))
            emit({**spec, "skipped": reason} if reason else run_row(spec, cpus, len(devices)))
    if "n21" in workloads:
        for name in N21_CIRCUITS:
            for label in labels:
                spec = {"workload": "n21", "circuit": name, "configuration": label}
                reason = skip_reason(label, len(devices))
                emit({**spec, "skipped": reason} if reason else run_row(spec, cpus, len(devices)))
    if "width" in workloads:
        for circuit in ("static", "dynamic"):
            for label in (label for label in WIDTH_CONFIGURATIONS if label in labels):
                stop = skip_reason(label, len(devices))
                widths = STATEVECTOR_WIDTHS if CONFIGURATIONS[label][1] == "statevector" else WIDTHS
                for width in widths:
                    spec = {"workload": "width", "circuit": circuit, "width": width, "configuration": label}
                    if stop is not None:
                        emit({**spec, "skipped": stop})
                        continue
                    row = run_row(spec, cpus, len(devices))
                    emit(row)
                    if "failed" in row:
                        stop = f"width {width} failed"
                    elif min(row["tiers"][0]["seconds"]) > BUDGET_SECONDS:
                        stop = f"width {width} exceeded {BUDGET_SECONDS} s"
    # Each contended row runs once more; the record keeps the attempt that
    # ran under the lower starting load and the other attempt's reading.
    for index, row in enumerate(record["rows"]):
        if not row.get("contended"):
            continue
        spec = {key: row[key] for key in ("workload", "circuit", "width", "configuration") if key in row}
        again = run_row(spec, cpus, len(devices))
        keep, other = (
            (again, row) if again["environment"]["load_1min"] < row["environment"]["load_1min"] else (row, again)
        )
        keep["other_attempt"] = {
            "environment": {key: value for key, value in other["environment"].items() if key != "compute_apps"},
            "process_wall_seconds": other["process_wall_seconds"],
            "best_seconds": [min(tier["seconds"]) for tier in other.get("tiers", [])],
        }
        record["rows"][index] = keep
        derive(record)
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({"rerun": spec, "kept_load": keep["environment"]["load_1min"]}), flush=True)
    return 0


# ---------------------------------------------------------------- check


def strip_derived(record: dict[str, Any]) -> dict[str, Any]:
    fresh: dict[str, Any] = json.loads(json.dumps(record))
    for row in fresh["rows"]:
        for key in DERIVED_ROW_KEYS:
            row.pop(key, None)
        for tier in row.get("tiers", []):
            tier.pop("best_seconds", None)
            tier.pop("ms_per_shot", None)
    return fresh


def lowering_contract() -> str:
    """Seeded CPU counts of a feed-forward circuit equal its lowered form's; a flipped or dropped condition differs."""
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile

    import calibration_snapshot
    import snapshot_laws

    snapshot = json.loads((ROOT / N21_SNAPSHOT).read_text(encoding="utf-8"))
    pair = calibration_snapshot.probe_qubits(snapshot)[:2]
    simulator = calibration_snapshot.noise_simulator(
        snapshot_laws.restrict(snapshot, pair), "CPU", method="statevector"
    )
    q, flag, out = QuantumRegister(2, "q"), ClassicalRegister(1, "flag"), ClassicalRegister(2, "out")
    source = QuantumCircuit(q, flag, out)
    source.h(0)
    source.cx(0, 1)
    source.measure(0, flag[0])
    with source.if_test((flag[0], 1)):
        source.x(1)
        source.rz(0.3, 0)
    source.h(0)
    source.measure([0, 1], out)
    basis = ["cz", "sx", "x", "rz", "measure", "if_else"]
    circuit = transpile(source, basis_gates=basis, optimization_level=0, seed_transpiler=0)
    lowered = lower_conditionals(circuit)
    if lowered is None or any(instruction.operation.name == "if_else" for instruction in lowered.data):
        raise SystemExit("aer_gpu_probe: lower_conditionals left an if_else in a lowerable circuit")
    flipped, dropped = lowered.copy_empty_like(), lowered.copy_empty_like()
    for instruction in lowered.data:
        condition = getattr(instruction.operation, "condition", None)
        if condition is None:
            flipped.append(instruction)
            dropped.append(instruction)
            continue
        gate = instruction.operation.to_mutable()
        gate.condition = (condition[0], not condition[1])
        flipped.append(gate, instruction.qubits)
        dropped.append(instruction.operation.base_class(*instruction.operation.params), instruction.qubits)

    def counts(c: Any) -> dict[str, int]:
        return dict(sorted(simulator.run(c, shots=4096, seed_simulator=SEED).result().get_counts().items()))

    reference = counts(circuit)
    if counts(lowered) != reference:
        raise SystemExit("aer_gpu_probe: lowered counts differ from the if_else circuit's on the CPU")
    if counts(flipped) == reference or counts(dropped) == reference:
        raise SystemExit("aer_gpu_probe: the lowered condition does not reach the outcome")
    with_else = QuantumCircuit(q, flag, out)
    with_else.measure(0, flag[0])
    with with_else.if_test((flag[0], 1)) as orelse:
        with_else.x(1)
    with orelse:
        with_else.x(0)
    if lower_conditionals(with_else) is not None:
        raise SystemExit("aer_gpu_probe: lower_conditionals accepted an else body")
    return "lowered counts equal the if_else counts; flipped and dropped conditions differ; else bodies stay unlowered"


def check(path: Path) -> int:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA:
        raise SystemExit(f"aer_gpu_probe: {path} schema is not {SCHEMA}")
    fresh = strip_derived(record)
    derive(fresh)
    if fresh != record:
        bad = [
            (row.get("circuit"), row.get("width"), row.get("configuration"))
            for row, again in zip(record["rows"], fresh["rows"], strict=True)
            if row != again
        ]
        raise SystemExit(f"aer_gpu_probe: derived values differ from the record on {len(bad)} rows, first {bad[:3]}")
    timed_rows = sum("tiers" in row for row in record["rows"])
    toy = [row for row in record["rows"] if row["workload"] == "toy" and "counts" in row]
    kept = sorted(row["configuration"] for row in toy if row["keeps_readout_law"])
    # The CPU default noise_simulator configuration keeps the toy's readout
    # law, recomputed here; the record's GPU rows were measured on a GPU.
    cpu = {
        "workload": "toy",
        "configuration": "cpu_statevector",
        "gpu_samples": [],
        "environment": {"gpu_baseline": []},
    }
    cpu.update(measure_toy("cpu_statevector"))
    derive_toy(cpu)
    if not cpu["keeps_readout_law"]:
        raise SystemExit(f"aer_gpu_probe: the CPU default breaks the readout toy law: {cpu['z_scores']}")
    print(
        f"{path}: {timed_rows} timed rows and {len(toy)} readout-toy rows reproduce their derived values; "
        f"readout law kept by {', '.join(kept)}; the CPU default keeps it on replay; {lowering_contract()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
