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

The file is public device calibration and carries no account or instance
identifier. ``--check FILE`` rebuilds the Target from a retained file,
requires it to reproduce every instruction entry and T1/T2, and runs a
seeded noisy probe; it needs no network.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay, Parameter, Reset
from qiskit.circuit.library import CZGate, IGate, Measure, RZGate, SXGate, XGate
from qiskit.providers import BackendV2, Options, QubitProperties
from qiskit.transpiler import InstructionProperties, Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

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


def describe(name: str, target: Any, props: Any, readout_flips: Any) -> dict[str, Any]:
    """The snapshot of one fetched backend; readout_flips is live_run.readout_flips.

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
        "num_qubits": target.num_qubits,
        "dt": target.dt,
        "qubits": qubits,
        "instructions": {op: _entries(target, op) for op in (*GATES, *NON_GATES)},
        "omitted_operations": sorted(set(target.operation_names) - set(GATES) - set(NON_GATES) - {"delay"}),
    }


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
    """The rebuilt Target reproduces every instruction entry and every T1 and T2 of the snapshot."""
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


# Aer's batched_shots_gpu applies each operation to every shot of a batch in
# one GPU kernel launch. At 7 and 10 active qubits it ran a calibrated noisy
# trajectory batch 2.7 to 3.8 times faster than the unbatched GPU executor,
# and at 14 qubits 2.2 times slower, since one 2**14 statevector already
# fills the device (docs/evidence/aer_gpu_configuration); Aer batches only
# circuits of at most batched_shots_gpu_max_qubits active qubits.
BATCHED_SHOTS_MAX_QUBITS = 10
CONTROL_FLOW = frozenset({"if_else", "while_loop", "for_loop", "switch_case"})


def has_control_flow(circuit: Any) -> bool:
    return isinstance(circuit, QuantumCircuit) and any(
        instruction.operation.name in CONTROL_FLOW for instruction in circuit.data
    )


class SnapshotSimulator(AerSimulator):
    """AerSimulator whose run keeps classical feed-forward off Aer's batched GPU executor.

    The batched executor rejects the jump instruction AerCompiler emits for
    if_else, and when a condition reaches it as a bfunc-gated operation it
    evaluates the condition on the measured outcome before the readout
    channel instead of the recorded bit (the readout toy of
    docs/evidence/aer_gpu_configuration). A batch containing control flow
    therefore runs with batched_shots_gpu off, the per-shot GPU executor,
    which draws the CPU's samples. Every other run is AerSimulator.run.
    """

    def run(self, circuits: Any, parameter_binds: Any = None, **run_options: Any) -> Any:
        options = {**self.options.__dict__, **run_options}
        if options.get("device") == "GPU" and options.get("batched_shots_gpu"):
            batch = circuits if isinstance(circuits, (list, tuple)) else [circuits]
            if any(has_control_flow(circuit) for circuit in batch):
                run_options["batched_shots_gpu"] = False
        return super().run(circuits, parameter_binds=parameter_binds, **run_options)


def noise_simulator(
    snapshot: dict[str, Any],
    device: str = "CPU",
    method: str = "density_matrix",
    batched_shots: bool | None = None,
    custatevec: bool = False,
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

    custatevec sets Aer's cuStateVec_enable on a GPU statevector run, which
    routes gate application and sampling through libcustatevec; an Aer built
    or wheeled without cuQuantum raises at run time. Aer 0.17.2 reports
    cuStateVec_enable False on a run that also sets batched_shots_gpu, so
    custatevec turns the batched default off and raises on an explicit
    batched_shots=True instead of falling back unseen.
    """
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
    snapshot = describe(name, target, props, live_run.readout_flips)
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
