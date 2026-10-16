"""A portable calibration snapshot that rebuilds live_run's Aer noise model offline.

live_run.noise_simulator builds noise from a fresh IBM Target (gate errors,
durations, T1 and T2 through NoiseModel.from_backend with readout off) plus a
per-qubit asymmetric readout channel [[1 - e10, e10], [e01, 1 - e01]] from
the backend properties. A Kaggle kernel holds no IBM credential, so this
module carries those inputs as JSON:

- ``export`` (``--export BACKEND --out FILE``) fetches the backend once, writes
  T1, T2 and frequency per qubit, (e10, e01) per qubit from
  live_run.readout_flips, and duration and error for every cz, sx, x, rz,
  id and measure entry, then builds both simulators (live_run's from the
  live objects, this module's from the round-tripped data) and requires
  every gate and readout channel to be equal before writing anything.
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
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay, Parameter
from qiskit.circuit.library import CZGate, IGate, Measure, RZGate, SXGate, XGate
from qiskit.providers import BackendV2, Options, QubitProperties
from qiskit.transpiler import InstructionProperties, Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

SCHEMA = "gororoba-calibration-snapshot-v1"
GATES = {"cz": CZGate(), "sx": SXGate(), "x": XGate(), "rz": RZGate(Parameter("theta")), "id": IGate()}
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
    """The snapshot of one fetched backend; readout_flips is live_run.readout_flips."""
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
        "instructions": {op: _entries(target, op) for op in (*GATES, "measure")},
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
    measure = snapshot["instructions"]["measure"]
    target.add_instruction(
        Measure(), {tuple(r["qargs"]): InstructionProperties(duration=r["duration"], error=r["error"]) for r in measure}
    )
    target.add_instruction(Delay(Parameter("t")), {(q,): None for q in range(snapshot["num_qubits"])})
    return target


def round_trip(snapshot: dict[str, Any]) -> None:
    """The rebuilt Target reproduces every instruction entry and every T1 and T2 of the snapshot."""
    target = build_target(snapshot)
    for op in (*GATES, "measure"):
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


def noise_simulator(snapshot: dict[str, Any], device: str = "CPU") -> AerSimulator:
    """Density-matrix AerSimulator with live_run.noise_simulator's noise, rebuilt from the snapshot."""
    view, noise = noise_model(snapshot)
    return AerSimulator.from_backend(view, noise_model=noise, method="density_matrix", device=device)


def channel_table(noise: NoiseModel) -> dict[str, Any]:
    """Every local quantum error on the snapshot's instructions and every readout error, keyed by name and qubits."""
    table: dict[str, Any] = {}
    for name, by_qubits in noise._local_quantum_errors.items():
        if name in GATES:
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
    live = channel_table(live_run._noise_model(name, live_run.TargetView(name, target), target, props))
    rebuilt = channel_table(noise_model(snapshot)[1])
    shared = live.keys() & rebuilt.keys()
    differing = sorted((live.keys() ^ rebuilt.keys()) | {key for key in shared if not live[key] == rebuilt[key]})
    if differing:
        raise SystemExit(f"rebuilt noise differs from live_run's on {len(differing)} channels, first {differing[:3]}")
    out.write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}: calibration {snapshot['calibration']}, {len(live)} channels equal to live_run's")


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
    counts = probe_counts(noise_simulator(snapshot), qubits)
    print(f"{args.check}: {snapshot['backend']} calibration {snapshot['calibration']}, probe on {qubits}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
