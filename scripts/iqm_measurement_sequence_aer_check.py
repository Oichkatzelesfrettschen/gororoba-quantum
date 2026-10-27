"""Cross-check of the pinching case's Bloch model against an Aer density-matrix simulation.

scripts/iqm_measurement_sequence.py predicts every arm's final P0 from a Bloch-vector iteration: a rotation with a
depolarizing prx error, a pinch (measure and settle arms) or coherent evolution (delay and unitary arms), and T1/T2
relaxation over the rotation layer and the measure window, delay or settle idle. This script runs the same circuits
of the case through an independent implementation: scripts/iqm_sim.py's calibration noise model (a depolarizing
channel per prx from the randomized-benchmarking fidelity), thermal relaxation on every wait
(iqm_signed_probe.relaxation, T2 capped at 2 T1), the pinch as the Kraus channel {|0><0|, |1><1|}, per qubit from |0>.
Aer's density-matrix method is deterministic, so no seed enters. The readout and the pre-readout wait lie outside
the comparison: the model predicts the z before the wait, and ro0/ro1 calibrate the wait away.

A gap above the tolerance in any arm, N or qubit means the model's algebra or its time accounting differs from the
simulation's.

Usage: "$PYTHON" scripts/iqm_measurement_sequence_aer_check.py (run CASE_DIR --calibration-dir DIR [--tolerance X]
       | --self-test)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Delay
from qiskit.circuit.library import RGate
from qiskit.quantum_info import Kraus
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_measurement_sequence as case  # noqa: E402
import iqm_signed_probe  # noqa: E402
import iqm_sim  # noqa: E402

from parallel import MIN_PARALLEL_ITEMS, ordered_map  # noqa: E402

PINCH = Kraus([np.array([[1, 0], [0, 0]], dtype=complex), np.array([[0, 0], [0, 1]], dtype=complex)])
TOLERANCE = 1e-9


def p0_of(circuit: dict[str, Any], qubit: str, calibration: iqm_sim.Calibration, simulator: AerSimulator) -> float:
    """P(read 0) of one qubit's marginal of a case circuit, from |0>, up to the pre-readout delay and without
    readout error: each prx followed by the compiled layer time, each mid-circuit measure by the pinch and the
    measure window, each delay by its duration."""
    index = calibration.qubits.index(qubit)
    chain = QuantumCircuit(len(calibration.qubits))
    for o in circuit["instructions"][:-2]:
        if qubit not in o["locus"]:
            continue
        if o["name"] == "prx":
            chain.append(RGate(o["args"]["angle"], o["args"]["phase"]), [index])
            chain.append(Delay(case.PRX_LAYER_SECONDS, "s"), [index])
        elif o["name"] == "measure":
            chain.append(PINCH, [index])
            chain.append(Delay(case.MEASURE_WINDOW_SECONDS, "s"), [index])
        elif o["name"] == "delay":
            chain.append(Delay(o["args"]["duration"], "s"), [index])
    noisy = iqm_signed_probe.relaxation(calibration, {qubit})(chain)
    noisy.save_probabilities([index])
    return float(simulator.run(noisy).result().data()["probabilities"][0])


_SIMULATORS: dict[str, AerSimulator] = {}


def simulator_of(calibration: iqm_sim.Calibration) -> AerSimulator:
    """The density-matrix simulator of a calibration's noise model, built once per process and set."""
    if calibration.set_id not in _SIMULATORS:
        _SIMULATORS[calibration.set_id] = AerSimulator(method="density_matrix", noise_model=calibration.noise_model())
    return _SIMULATORS[calibration.set_id]


def p0_item(item: tuple[dict[str, Any], str, iqm_sim.Calibration]) -> float:
    """p0_of for one (circuit, qubit, calibration) item, with the simulator built inside the worker."""
    circuit, qubit, calibration = item
    return p0_of(circuit, qubit, calibration, simulator_of(calibration))


def cold_tables(inputs: dict[str, float]) -> dict[str, Any]:
    """One qubit's model P0 tables at q = 1 (a cold start) with its calibrated T1, T2 and prx error."""
    return case.model_tables(inputs["t1_s"], inputs["t2_s"], 1.0, case.MEASURE_WINDOW_SECONDS, inputs["prx_p"])


def compare(
    circuits: dict[str, dict[str, Any]],
    qubits: dict[str, dict[str, float]],
    calibration: iqm_sim.Calibration,
    min_items: int = MIN_PARALLEL_ITEMS,
) -> list[dict[str, Any]]:
    """Per qubit, arm and N: the simulation's P0 over the four signed circuits against the Bloch model at q = 1
    (a cold start), with the calibration's prx error. The qubit x arm x N x sign simulations are independent and run
    through parallel.ordered_map; the sums keep the serial order, so the rows match a serial run bit for bit."""
    keys = [(qubit, arm, n) for qubit in qubits for arm, n in case.group_keys()]
    items = [(circuits[name], qubit, calibration) for qubit, arm, n in keys for name in case.group_names(arm, n)]
    values = iter(ordered_map(p0_item, items, min_items))
    names = list(qubits)
    model = dict(zip(names, ordered_map(cold_tables, [qubits[q] for q in names], min_items), strict=True))
    rows = []
    for qubit, arm, n in keys:
        tables = model[qubit]
        names = case.group_names(arm, n)
        simulated = sum(next(values) for _ in names) / len(names)
        rows.append(
            {
                "qubit": qubit,
                "arm": arm,
                "n": n,
                "simulated": simulated,
                "model": tables[arm][str(n)],
                "gap": simulated - tables[arm][str(n)],
            }
        )
    return rows


def run(case_dir: Path, calibration_dir: Path, tolerance: float) -> list[dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    prediction = case.load_json(case_dir / "prediction.json")
    if calibration.set_id != prediction["calibration_set"]:
        raise ValueError(f"{calibration_dir} is set {calibration.set_id}, the case is {prediction['calibration_set']}")
    circuits = {p.stem: case.load_json(p) for p in sorted((case_dir / "circuits").glob("*.json"))}
    rows = compare(circuits, {q: row["inputs"] for q, row in prediction["qubits"].items()}, calibration)
    worst = max(abs(r["gap"]) for r in rows)
    if worst > tolerance:
        raise RuntimeError(
            f"the Bloch model and the Aer simulation differ by {worst:.3e} in P0 (tolerance {tolerance})"
        )
    return rows


def self_test() -> str:
    """One qubit of the retained calibration through the case's own circuit builder, in every arm."""
    calibration = iqm_sim.Calibration.from_directory(case.CALIBRATION_DIR)
    qubit = "QB1"
    circuits = {}
    for arm, n in case.group_keys():
        for name, sign in zip(case.group_names(arm, n), case.SIGNS, strict=True):
            circuits[name] = case.circuit(name, [qubit], arm, n, sign)
    inputs = {
        "t1_s": calibration.values[f"characterization.model.{qubit}.t1_time"],
        "t2_s": calibration.values[f"characterization.model.{qubit}.t2_time"],
        "prx_p": calibration.prx_p(qubit),
    }
    rows = compare(circuits, {qubit: inputs}, calibration)
    worst = max(abs(r["gap"]) for r in rows)
    if worst > TOLERANCE:
        raise RuntimeError(f"the Bloch model and the Aer simulation differ by {worst:.3e}")
    return f"pinching Aer check: {len(rows)} arm and N points of {qubit} agree to {worst:.1e} in P0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    r = sub.add_parser("run")
    r.add_argument("case_dir", type=Path)
    r.add_argument("--calibration-dir", type=Path, required=True)
    r.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "run":
        rows = run(args.case_dir, args.calibration_dir, args.tolerance)
        print(json.dumps(rows, indent=1, sort_keys=True))
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
