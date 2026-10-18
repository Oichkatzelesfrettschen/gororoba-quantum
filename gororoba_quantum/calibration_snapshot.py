"""A portable calibration snapshot that rebuilds live_run's Aer noise model offline.

live_run.noise_simulator builds noise from a fresh IBM Target (gate errors,
durations, T1 and T2 through NoiseModel.from_backend with readout off) plus a
per-qubit asymmetric readout channel [[1 - e10, e10], [e01, 1 - e01]] from
the backend properties. A Kaggle kernel holds no IBM credential, so this
module carries those inputs as JSON:

- ``export`` (``--export BACKEND --out FILE``) fetches the backend once, writes
  T1, T2 and frequency per qubit, (e10, e01) per qubit from
  live_run.readout_flips, duration and error for every cz, sx, x, rz, id,
  measure and reset entry, and the Target operations it cannot rebuild
  (``omitted_operations``: measure_2, the measure_reset variants, reset_2,
  xslow and control flow), then builds both noise models (live_run's from the
  live objects, this module's from the round-tripped data) and requires every
  gate, reset and readout channel outside the omitted operations to be equal,
  and the rebuilt model to carry none of the omitted ones, before writing
  anything.
- ``noise_simulator(snapshot, device)`` rebuilds the Target, applies the same
  two noise steps, and returns a density-matrix AerSimulator on CPU or GPU.

The snapshot also records the backend_version its properties report and the
processor_type of the backend configuration. ``backend_identity(snapshot)``
returns the fields a snapshot holds, empty for a snapshot without them, so a
record that names the snapshot carries them through.

The file is public device calibration and carries no account or instance
identifier. ``--check FILE`` rebuilds the Target from a retained file,
requires it to reproduce every instruction entry and T1/T2, and runs a
seeded noisy probe; it needs no network.
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay, Parameter, Reset
from qiskit.circuit.library import CZGate, IGate, Measure, RZGate, SXGate, XGate
from qiskit.providers import BackendV2, Options, QubitProperties
from qiskit.transpiler import InstructionProperties, Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

import aer_resources

SCHEMA = "gororoba-calibration-snapshot-v2"
GATES = {"cz": CZGate(), "sx": SXGate(), "x": XGate(), "rz": RZGate(Parameter("theta")), "id": IGate()}
# Non-gate instructions the snapshot carries; every other Target operation is
# listed in the snapshot's omitted_operations, and a circuit that uses one
# fails transpilation against the rebuilt Target.
NON_GATES = {"measure": Measure(), "reset": Reset()}
PROBE_SHOTS = 2000
PROBE_SEED = 20261015


class SnapshotBackend(BackendV2):
    """A BackendV2 that carries only a Target, the input AerSimulator.from_backend reads."""

    def __init__(self, name: str, target: Target) -> None:
        super().__init__(name=name)
        self._snapshot_target = target

    @property
    def target(self) -> Target:
        return self._snapshot_target

    @property
    def max_circuits(self) -> None:
        return None

    @classmethod
    def _default_options(cls) -> Options:
        return Options()

    def run(self, run_input: Any, **options: Any) -> Any:
        raise NotImplementedError("SnapshotBackend carries a Target for noise modeling only")


def _entries(target: Any, name: str) -> list[dict[str, Any]]:
    if name not in target.operation_names:
        return []
    rows = []
    for qargs, props in target[name].items():
        if qargs is None or props is None:
            continue
        rows.append({"qargs": list(qargs), "duration": props.duration, "error": props.error})
    return sorted(rows, key=lambda row: row["qargs"])


IDENTITY_FIELDS = ("backend_version", "processor_type")


def describe(
    name: str, target: Any, props: Any, readout_flips: Any, processor_type: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """The snapshot of one fetched backend; readout_flips is live_run.readout_flips.

    backend_version comes from the properties, so a historical calibration
    keeps the version reported with it; processor_type is the backend
    configuration's (live_run.backend_identity).

    The Target and the properties must describe one calibration update, the
    condition live_run.take_snapshot enforces through
    check_snapshot_matches_properties: the rebuilt noise model takes gate and
    coherence data from the Target and readout and the calibration identity
    from the properties, so a mixed pair would pass the channel comparison.
    """
    import live_run

    try:
        live_run.check_snapshot_matches_properties(target, props, name)
    except live_run.LiveRunError as error:
        raise SystemExit(f"Target and properties describe different calibrations: {error}") from None
    qubits = []
    for q in range(target.num_qubits):
        qp = target.qubit_properties[q] if target.qubit_properties else None
        e10, e01 = readout_flips(props, q)
        qubits.append(
            {
                "t1": getattr(qp, "t1", None),
                "t2": getattr(qp, "t2", None),
                "frequency": getattr(qp, "frequency", None),
                "e10": e10,
                "e01": e01,
            }
        )
    return {
        "schema": SCHEMA,
        "backend": name,
        "calibration": props.last_update_date.isoformat(),
        "backend_version": str(props.backend_version),
        "processor_type": dict(processor_type) if processor_type is not None else None,
        "num_qubits": target.num_qubits,
        "dt": target.dt,
        "qubits": qubits,
        "instructions": {op: _entries(target, op) for op in (*GATES, *NON_GATES)},
        "omitted_operations": sorted(set(target.operation_names) - set(GATES) - set(NON_GATES) - {"delay"}),
    }


def backend_identity(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """The backend_version and processor_type a snapshot holds; a snapshot without them yields an empty dictionary."""
    return {key: snapshot[key] for key in IDENTITY_FIELDS if key in snapshot}


def check_identity(snapshot: Mapping[str, Any]) -> None:
    """A present backend_version is a nonempty string and a present processor_type a string dictionary."""
    version = snapshot.get("backend_version")
    if "backend_version" in snapshot and not (isinstance(version, str) and version):
        raise ValueError(f"snapshot backend_version {version!r} is not a nonempty string")
    processor = snapshot.get("processor_type")
    if processor is not None and not (
        isinstance(processor, dict)
        and {"family", "revision"} <= set(processor)
        and all(isinstance(value, str) for value in processor.values())
    ):
        raise ValueError(f"snapshot processor_type {processor!r} lacks a string family and revision")


def build_target(snapshot: dict[str, Any]) -> Target:
    if snapshot.get("schema") != SCHEMA:
        raise ValueError(f"calibration snapshot schema must be {SCHEMA}")
    target = Target(
        num_qubits=snapshot["num_qubits"],
        dt=snapshot["dt"],
        qubit_properties=[
            QubitProperties(t1=q["t1"], t2=q["t2"], frequency=q["frequency"]) for q in snapshot["qubits"]
        ],
    )
    for op, gate in GATES.items():
        rows = snapshot["instructions"].get(op, [])
        if rows:
            target.add_instruction(
                gate,
                {tuple(r["qargs"]): InstructionProperties(duration=r["duration"], error=r["error"]) for r in rows},
            )
    for op, instruction in NON_GATES.items():
        rows = snapshot["instructions"].get(op, [])
        if rows:
            target.add_instruction(
                instruction,
                {tuple(r["qargs"]): InstructionProperties(duration=r["duration"], error=r["error"]) for r in rows},
            )
    target.add_instruction(Delay(Parameter("t")), {(q,): None for q in range(snapshot["num_qubits"])})
    return target


def round_trip(snapshot: dict[str, Any]) -> None:
    """The rebuilt Target reproduces every instruction entry and every T1 and T2 of the snapshot.

    A present backend_version or processor_type also passes check_identity.
    """
    check_identity(snapshot)
    target = build_target(snapshot)
    for op in (*GATES, *NON_GATES):
        if _entries(target, op) != snapshot["instructions"].get(op, []):
            raise ValueError(f"rebuilt Target differs from the snapshot on {op}")
    for q, qubit in enumerate(snapshot["qubits"]):
        props = target.qubit_properties[q]
        if (props.t1, props.t2) != (qubit["t1"], qubit["t2"]):
            raise ValueError(f"rebuilt Target differs from the snapshot on qubit {q} T1/T2")


def noise_model(snapshot: dict[str, Any]) -> tuple[SnapshotBackend, NoiseModel]:
    """live_run._noise_model's two steps applied to the rebuilt Target."""
    view = SnapshotBackend(snapshot["backend"], build_target(snapshot))
    noise = NoiseModel.from_backend(view, readout_error=False)
    for q, qubit in enumerate(snapshot["qubits"]):
        e10, e01 = qubit["e10"], qubit["e01"]
        noise.add_readout_error(ReadoutError([[1.0 - e10, e10], [e01, 1.0 - e01]]), [q])
    return view, noise


AER_DEVICES = ("CPU", "GPU")


def aer_device() -> str:
    """The Aer device GOROROBA_AER_DEVICE names, CPU when it is unset.

    CI runners carry no GPU and keep the CPU; ``ci/run_gates.py --device GPU``
    exports GPU, so a local run computes every exact-law replay on the other
    device. Contracts that compare seeded shot counts keep Aer's CPU sampler,
    whose counts their retained records hold.
    """
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    if device not in AER_DEVICES:
        raise SystemExit(f"GOROROBA_AER_DEVICE={device!r} is not one of {AER_DEVICES}")
    return device


def aer_custatevec() -> bool:
    """Whether GOROROBA_AER_CUSTATEVEC asks noise_simulator for cuStateVec; unset or 0 keeps it off.

    1 sets cuStateVec_enable on every GPU run whose caller leaves custatevec
    unset, so an entry that takes its device from aer_device() runs on
    libcustatevec without an argument of its own; a CPU run ignores it.
    """
    value = os.environ.get("GOROROBA_AER_CUSTATEVEC", "0")
    if value not in ("0", "1"):
        raise SystemExit(f"GOROROBA_AER_CUSTATEVEC={value!r} is not 0 or 1")
    return value == "1"


# Aer's batched_shots_gpu applies each operation to every shot of a batch in
# one GPU kernel launch. At 7 and 10 active qubits it ran a calibrated noisy
# trajectory batch 2.7 to 3.8 times faster than the unbatched GPU executor,
# and at 14 qubits 2.2 times slower, since one 2**14 statevector already
# fills the device (docs/evidence/aer_gpu_configuration); Aer batches only
# circuits of at most batched_shots_gpu_max_qubits active qubits.
BATCHED_SHOTS_MAX_QUBITS = 10
# Aer's blocking_qubits documentation asks that one double-precision chunk,
# 16 * 2**blocking_qubits bytes, stay below a quarter of one GPU's memory;
# a density-matrix chunk of b qubits holds 4**b entries
# (CacheBlocking::set_blocking scales its chunk bits by 2 for a matrix).
BLOCKING_MEMORY_FRACTION = 4
COMPLEX_DOUBLE_BYTES = 16


def blocking_qubits_for(method: str, gpu_memory_mib: int) -> int:
    """The widest Aer chunk whose double-precision state fits a quarter of one GPU's memory."""
    if method not in ("statevector", "density_matrix"):
        raise ValueError(f"Aer cache blocking supports statevector and density_matrix, not {method}")
    scale = 2 if method == "density_matrix" else 1
    limit = (gpu_memory_mib << 20) // BLOCKING_MEMORY_FRACTION
    bits = 1
    while COMPLEX_DOUBLE_BYTES << (scale * (bits + 1)) <= limit:
        bits += 1
    return bits


CONTROL_FLOW = frozenset({"if_else", "while_loop", "for_loop", "switch_case"})


def has_control_flow(circuit: Any) -> bool:
    return isinstance(circuit, QuantumCircuit) and any(
        instruction.operation.name in CONTROL_FLOW for instruction in circuit.data
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

    if not has_control_flow(circuit):
        return circuit
    lowered = circuit.copy_empty_like()
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name not in CONTROL_FLOW:
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


def active_qubits(circuit: Any) -> int:
    """The width Aer simulates once it truncates idle qubits: every wire an instruction other than a barrier acts on.

    Aer leaves barriers out of the wires it keeps (Circuit::check_result_ancestor,
    which Circuit::set_params applies when it truncates), so a device-wide
    barrier on an ISA circuit adds no width.
    """
    return aer_resources.active_support(circuit)


# Aer stores a double-precision state in 16 * 2**n bytes, 16 * 4**n for a
# density matrix.
def state_bytes(method: str, width: int) -> int:
    return COMPLEX_DOUBLE_BYTES << ((2 if method == "density_matrix" else 1) * width)


@functools.cache
def gpu_memory_mib() -> int | None:
    """The smallest memory.total nvidia-smi reports across the host's GPUs, or None without one."""
    if shutil.which("nvidia-smi") is None:
        return None
    listing = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    return min(int(value) for value in listing) if listing else None


def blocking_options(method: str, width: int, memory_mib: int | None) -> dict[str, Any]:
    """Aer cache-blocking options for a state of width qubits, empty while it fits one GPU.

    Aer blocks a state on its own once it exceeds one GPU's share of the
    device memory (ParallelStateExecutor::multiple_chunk_required), with a
    chunk as wide as one whole device; on the T4 x2 that choice placed a
    15-qubit density matrix and a 30-qubit statevector entirely in host
    memory, which the OOM killer ended, while chunks from blocking_qubits_for
    ran both across the two GPUs (docs/evidence/aer_gpu_configuration). So
    the trigger is Aer's own and only the chunk size changes: a run that
    fits one GPU keeps its unblocked executor and its seeded counts.
    max_parallel_shots=1 keeps Executor::set_parallelization from sizing
    parallel shots of a dynamic circuit against the whole state, which
    raises "a circuit requires more memory than max_memory_mb".
    """
    if memory_mib is None or method not in ("statevector", "density_matrix"):
        return {}
    if state_bytes(method, width) <= memory_mib << 20:
        return {}
    return {
        "blocking_enable": True,
        "blocking_qubits": blocking_qubits_for(method, memory_mib),
        "max_parallel_shots": 1,
    }


class SnapshotSimulator(AerSimulator):
    """AerSimulator whose run keeps classical feed-forward off Aer's batched GPU executor.

    The batched executor rejects the jump instruction AerCompiler emits for
    if_else, and when a condition reaches it as a bfunc-gated operation it
    evaluates the condition on the measured outcome before the readout
    channel instead of the recorded bit (the readout toy of
    docs/evidence/aer_gpu_configuration). A batch containing control flow
    therefore runs with batched_shots_gpu off, the per-shot GPU executor,
    which draws the CPU's samples.

    A GPU state wider than one device runs under blocking_options. Aer's
    cache-blocking pass splits the operation list into per-chunk blocks, so
    an if_else, which AerCompiler inlines into jump and mark, aborts the
    process when its mark lands in another block ("Invalid jump
    destination", raised past every handler); a circuit wider than the
    chunk runs in its lower_conditionals form, whose seeded counts equal the
    if_else circuit's under blocking with the readout channel ahead of the
    condition (scripts/aer_blocking_probe.py --self-test), and one with no
    such form raises ValueError. Run options that set blocking_enable keep the
    caller's choice. Every other run is AerSimulator.run.
    """

    def run(self, circuits: Any, parameter_binds: Any = None, **run_options: Any) -> Any:
        options = {**self.options.__dict__, **run_options}
        batch = list(circuits) if isinstance(circuits, (list, tuple)) else [circuits]
        if options.get("device") == "GPU" and options.get("batched_shots_gpu"):
            if any(has_control_flow(circuit) for circuit in batch):
                run_options["batched_shots_gpu"] = False
        if options.get("device") == "GPU" and "blocking_enable" not in run_options:
            lowered, blocking = blocked_batch(batch, str(options.get("method")), gpu_memory_mib())
            if blocking:
                circuits = lowered if isinstance(circuits, (list, tuple)) else lowered[0]
                run_options = {**run_options, **blocking}
        return super().run(circuits, parameter_binds=parameter_binds, **run_options)


def blocked_batch(batch: list[Any], method: str, memory_mib: int | None) -> tuple[list[Any], dict[str, Any]]:
    """The batch and its blocking options; under blocking a circuit wider than the chunk runs in conditioned-gate form.

    Aer's cache-blocking pass splits only a circuit wider than
    blocking_qubits; a circuit at or below the chunk width runs whole, so its
    if_else stays intact and draws the unblocked batch's seeded counts
    (scripts/aer_blocking_probe.py --self-test).
    """
    width = max((active_qubits(c) for c in batch if isinstance(c, QuantumCircuit)), default=0)
    blocking = blocking_options(method, width, memory_mib)
    if not blocking:
        return batch, {}
    lowered = []
    for circuit in batch:
        split = isinstance(circuit, QuantumCircuit) and active_qubits(circuit) > blocking["blocking_qubits"]
        form = lower_conditionals(circuit) if split and has_control_flow(circuit) else circuit
        if form is None:
            raise ValueError(
                f"{getattr(circuit, 'name', circuit)}: a {active_qubits(circuit)}-qubit {method} needs Aer cache "
                "blocking, which aborts on if_else, and its control flow has no conditioned-gate form (an else "
                "body, an expression condition, a measurement, reset or nested control flow in the body, or a loop)"
            )
        lowered.append(form)
    return lowered, blocking


def noise_simulator(
    snapshot: dict[str, Any],
    device: str = "CPU",
    method: str = "density_matrix",
    batched_shots: bool | None = None,
    custatevec: bool | None = None,
) -> AerSimulator:
    """AerSimulator with live_run.noise_simulator's noise, rebuilt from the snapshot.

    method "density_matrix" evolves the channel exactly per shot; "statevector"
    samples trajectories of the same channel. On a GPU device batched_shots
    (default on; False opts out) enables Aer's batched_shots_gpu up to
    BATCHED_SHOTS_MAX_QUBITS active qubits: the unbatched GPU executor runs
    one shot at a time and pays a kernel launch per operation per shot, which
    a narrow state cannot amortize. Circuits with control flow run unbatched
    (SnapshotSimulator.run). For statevector trajectories of circuits
    without control flow the batched, unbatched GPU and CPU executors drew
    identical seeded counts in the retained measurement; a record still
    names the sampler that produced its counts. On the CPU batched_shots is
    ignored and the simulator carries Aer's default CPU options. Shot
    branching is never enabled: Aer 0.17.2's shot branching drops the
    readout channel of a mid-circuit measurement.

    custatevec sets Aer's cuStateVec_enable on a GPU run, statevector or
    density matrix, which routes gate application and sampling through
    libcustatevec; an Aer built or wheeled without cuQuantum raises at run
    time. Left unset it follows aer_custatevec(). Aer 0.17.2 reports
    cuStateVec_enable False on a run that also sets batched_shots_gpu, so
    custatevec turns the batched default off and raises on an explicit
    batched_shots=True instead of falling back unseen.
    """
    if custatevec is None:
        custatevec = aer_custatevec()
    if custatevec and batched_shots:
        raise ValueError("custatevec and batched_shots are exclusive Aer GPU options")
    view, noise = noise_model(snapshot)
    options: dict[str, Any] = {}
    if device == "GPU" and custatevec:
        options = {"cuStateVec_enable": True}
    elif device == "GPU" and batched_shots is not False:
        options = {"batched_shots_gpu": True, "batched_shots_gpu_max_qubits": BATCHED_SHOTS_MAX_QUBITS}
    return SnapshotSimulator.from_backend(view, noise_model=noise, method=method, device=device, **options)


def channel_table(noise: NoiseModel) -> dict[str, Any]:
    """Every local quantum error and every readout error of a noise model, keyed by name and qubits."""
    table: dict[str, Any] = {}
    for name, by_qubits in noise._local_quantum_errors.items():
        for qubits, error in by_qubits.items():
            table[f"{name}{list(qubits)}"] = error
    for qubits, error in noise._local_readout_errors.items():
        table[f"readout{list(qubits)}"] = error
    return table


def probe_counts(simulator: AerSimulator, qubits: list[int]) -> dict[str, int]:
    """Seeded noisy counts of a GHZ, idle and X probe on the named physical qubits."""
    n = len(qubits)
    circuit = QuantumCircuit(n, n)
    circuit.h(0)
    for k in range(n - 1):
        circuit.cx(k, k + 1)
    circuit.delay(2000, 0, unit="dt")
    circuit.x(n - 1)
    circuit.measure(range(n), range(n))
    compiled = transpile(circuit, simulator, initial_layout=qubits, optimization_level=1, seed_transpiler=PROBE_SEED)
    result = simulator.run(compiled, shots=PROBE_SHOTS, seed_simulator=PROBE_SEED).result()
    return dict(sorted(result.get_counts().items()))


def probe_qubits(snapshot: dict[str, Any]) -> list[int]:
    """The first cz edge's qubits plus a neighbor, a connected three-qubit probe."""
    edges = [tuple(r["qargs"]) for r in snapshot["instructions"]["cz"]]
    a, b = edges[0]
    for u, v in edges:
        if u == b and v != a:
            return [a, b, v]
    return [a, b]


def export(name: str, out: Path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from qiskit_ibm_runtime import QiskitRuntimeService

    import live_run

    backend = QiskitRuntimeService().backend(name)
    backend.refresh()
    props = backend.properties()
    target = backend.target
    processor_type = live_run.backend_identity(backend)["processor_type"]
    snapshot = describe(name, target, props, live_run.readout_flips, processor_type)
    snapshot = json.loads(json.dumps(snapshot))
    omitted = tuple(snapshot["omitted_operations"])
    live_all = channel_table(live_run._noise_model(name, live_run.TargetView(name, target), target, props))
    live = {key: error for key, error in live_all.items() if not key.startswith(tuple(f"{op}[" for op in omitted))}
    rebuilt = channel_table(noise_model(snapshot)[1])
    if any(key.startswith(tuple(f"{op}[" for op in omitted)) for key in rebuilt):
        raise SystemExit("the rebuilt noise model carries an operation the snapshot omits")
    shared = live.keys() & rebuilt.keys()
    differing = sorted((live.keys() ^ rebuilt.keys()) | {key for key in shared if not live[key] == rebuilt[key]})
    if differing:
        raise SystemExit(f"rebuilt noise differs from live_run's on {len(differing)} channels, first {differing[:3]}")
    check_identity(snapshot)
    out.write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {out}: calibration {snapshot['calibration']}, {len(live)} channels equal to live_run's, "
        f"omitted {', '.join(omitted) or 'none'}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--export", metavar="BACKEND")
    mode.add_argument("--check", metavar="FILE", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.export:
        if args.out is None:
            parser.error("--export needs --out")
        export(args.export, args.out)
        return 0
    snapshot = json.loads(args.check.read_text(encoding="utf-8"))
    round_trip(snapshot)
    qubits = probe_qubits(snapshot)
    counts = probe_counts(noise_simulator(snapshot, aer_device()), qubits)
    print(f"{args.check}: {snapshot['backend']} calibration {snapshot['calibration']}, probe on {qubits}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
