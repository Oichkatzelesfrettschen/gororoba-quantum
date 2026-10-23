"""Local Aer prediction of an IQM circuit case from the retained calibration of one quantum computer.

The free mock twins (garnet:mock, emerald:mock) run the server pipeline and return its runtime
estimate, but their measurement data are random bits, so a physics prediction needs a noise model.
This one is built from the retained snapshot (docs/evidence/iqm/qc/QC/calibration/): per-qubit
single-shot readout (metrics.ssro.measure.constant.QBn.error_0_to_1 and error_1_to_0, the
unheralded values, which include the initialization error), per-qubit PRX randomized benchmarking
fidelity and per-coupler CZ interleaved benchmarking fidelity, with the CZ loci of the dynamic
quantum architecture. A depolarizing channel of average fidelity F has p = 2(1 - F) on one qubit
and p = 4(1 - F)/3 on two. Idle decoherence is not modeled, so a case with delays is out of scope.

Circuits are the case's own JSON (iqm.station_control.Circuit): prx(angle, phase) is
RGate(angle, phase), cz is CZ on a calibrated coupler, and measure reads its locus into one bit per
qubit under its key. The prediction for each circuit is P(1) per measured qubit, sampled at the
case's shots with a fixed seed, beside the exact single-qubit value where the circuit is one prx
and a measure.

Usage: "$PYTHON" scripts/iqm_sim.py run CASE_DIR [--qc garnet] [--seed N]
       "$PYTHON" scripts/iqm_sim.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import RGate
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "docs/evidence/iqm/qc"
PRX_FIELD = "metrics.rb.prx.drag_crf_sx.{q}.fidelity:par=d2"
READOUT_FIELD = "metrics.ssro.measure.constant.{q}.{kind}"
# Error rates conditioned on an all-zeros herald measurement, the readout a heralded job's kept shots see.
HERALD_SUFFIX = ":herald=measure.constant"


class Calibration:
    def __init__(self, qc: str, evidence: Path = EVIDENCE) -> None:
        self.load(evidence / qc.replace(":", "_") / "calibration")

    @classmethod
    def from_directory(cls, folder: Path) -> Calibration:
        """A calibration read from a folder holding metrics.json and dynamic-quantum-architecture.json."""
        calibration = cls.__new__(cls)
        calibration.load(folder)
        return calibration

    def load(self, folder: Path) -> None:
        metrics = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
        self.values = {o["dut_field"]: o["value"] for o in metrics["observations"] if not o.get("invalid")}
        self.metrics_id = metrics.get("observation_set_id")
        architecture = json.loads((folder / "dynamic-quantum-architecture.json").read_text(encoding="utf-8"))
        self.qubits: list[str] = architecture["qubits"]
        self.set_id: str = architecture["calibration_set_id"]
        cz = architecture["gates"]["cz"]
        self.cz: dict[frozenset[str], float] = {}
        for implementation, spec in cz["implementations"].items():
            for a, b in spec["loci"]:
                fidelity = self.values.get(f"metrics.irb.cz.{implementation}.{a}__{b}.fidelity:par=d2")
                if fidelity is None:
                    fidelity = self.values.get(f"metrics.irb.cz.{implementation}.{b}__{a}.fidelity:par=d2")
                if fidelity is not None:
                    self.cz[frozenset((a, b))] = fidelity

    def readout(self, qubit: str, heralded: bool = False) -> tuple[float, float]:
        """(P(read 1 | 0), P(read 0 | 1)), unheralded or conditioned on an all-zeros herald."""
        suffix = HERALD_SUFFIX if heralded else ""
        return (
            self.values[READOUT_FIELD.format(q=qubit, kind="error_0_to_1") + suffix],
            self.values[READOUT_FIELD.format(q=qubit, kind="error_1_to_0") + suffix],
        )

    def prx_p(self, qubit: str) -> float:
        return 2 * (1 - self.values[PRX_FIELD.format(q=qubit)])

    def noise_model(self, heralded: bool = False) -> NoiseModel:
        """Depolarizing PRX and CZ and readout error; heralded selects the herald-conditioned readout."""
        model = NoiseModel(basis_gates=["r", "cz"])
        for n, qubit in enumerate(self.qubits):
            if PRX_FIELD.format(q=qubit) in self.values:
                model.add_quantum_error(depolarizing_error(self.prx_p(qubit), 1), "r", [n])
            if READOUT_FIELD.format(q=qubit, kind="error_0_to_1") in self.values:
                e01, e10 = self.readout(qubit, heralded)
                model.add_readout_error(ReadoutError([[1 - e01, e01], [e10, 1 - e10]]), [n])
        for pair, fidelity in self.cz.items():
            a, b = sorted(pair, key=self.qubits.index)
            p = 4 * (1 - fidelity) / 3
            error = depolarizing_error(p, 2)
            model.add_quantum_error(error, "cz", [self.qubits.index(a), self.qubits.index(b)])
            model.add_quantum_error(error, "cz", [self.qubits.index(b), self.qubits.index(a)])
        return model


def to_qiskit(circuit: dict[str, Any], calibration: Calibration) -> tuple[QuantumCircuit, list[tuple[str, str]]]:
    """The circuit on the QC's qubit order and the (key, qubit) of each classical bit."""
    quantum = QuantumRegister(len(calibration.qubits), "q")
    bits: list[tuple[str, str]] = [
        (op["args"]["key"], q) for op in circuit["instructions"] if op["name"] == "measure" for q in op["locus"]
    ]
    classical = ClassicalRegister(max(len(bits), 1), "c")
    out = QuantumCircuit(quantum, classical, name=circuit["name"])
    index = {q: n for n, q in enumerate(calibration.qubits)}
    bit = 0
    for op in circuit["instructions"]:
        locus = [index[q] for q in op["locus"]]
        if op["name"] == "prx":
            out.append(RGate(op["args"]["angle"], op["args"]["phase"]), locus)
        elif op["name"] == "cz":
            if frozenset(op["locus"]) not in calibration.cz:
                raise ValueError(f"{circuit['name']}: cz on {op['locus']} has no calibrated coupler")
            out.cz(*locus)
        elif op["name"] == "measure":
            for q in locus:
                out.measure(q, bit)
                bit += 1
        else:
            raise ValueError(f"{circuit['name']}: {op['name']} has no local model")
    return out, bits


def exact_single(circuit: dict[str, Any], calibration: Calibration) -> float | None:
    """P(read 1) of one prx then measure on one qubit under the same model, or None for any other shape."""
    ops = circuit["instructions"]
    if len(ops) != 2 or ops[0]["name"] != "prx" or ops[1]["name"] != "measure" or ops[0]["locus"] != ops[1]["locus"]:
        return None
    qubit = ops[0]["locus"][0]
    ideal = math.sin(ops[0]["args"]["angle"] / 2) ** 2
    p = calibration.prx_p(qubit)
    excited = (1 - p) * ideal + p / 2
    e01, e10 = calibration.readout(qubit)
    return excited * (1 - e10) + (1 - excited) * e01


def simulate_circuit(item: tuple[str, str, int, int, str, str, bool]) -> dict[str, Any]:
    """One circuit of a case: sampled P(1) per measured qubit and the exact single-qubit value."""
    case_dir, qc, seed, shots, job, file, heralded = item
    calibration = Calibration(qc)
    circuit = json.loads((Path(case_dir) / file).read_text(encoding="utf-8"))
    qiskit_circuit, bits = to_qiskit(circuit, calibration)
    simulator = AerSimulator(noise_model=calibration.noise_model(heralded), seed_simulator=seed)
    counts = simulator.run(qiskit_circuit, shots=shots).result().get_counts()
    p1 = {}
    for n, (key, qubit) in enumerate(bits):
        ones = sum(c for s, c in counts.items() if s[::-1][n] == "1")
        p1[f"{key}:{qubit}"] = ones / shots
    return {
        "job": job,
        "circuit": circuit["name"],
        "shots": shots,
        "p1": p1,
        "exact_p1": exact_single(circuit, calibration),
    }


def run_case(case_dir: Path, qc: str, seed: int) -> list[dict[str, Any]]:
    """Every circuit of a case, in the case's order, each with its own simulator at the given seed; a
    heralded job reads the herald-conditioned readout."""
    case = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    items = [
        (
            str(case_dir),
            qc,
            seed,
            job["shots"],
            job["job"],
            entry["file"],
            job["options"].get("heralding_mode") == "zeros",
        )
        for job in case["jobs"]
        for entry in job["circuits"]
    ]
    return ordered_map(simulate_circuit, items)


def self_test() -> str:
    calibration = Calibration("garnet")
    x = {
        "name": "x",
        "instructions": [
            {"name": "prx", "locus": ["QB1"], "args": {"angle": math.pi, "phase": 0.0}},
            {"name": "measure", "locus": ["QB1"], "args": {"key": "m"}},
        ],
    }
    exact = exact_single(x, calibration)
    if exact is None or not 0.9 < exact < 1.0:
        raise RuntimeError(f"exact P(1) of X on QB1 is {exact}")
    simulator = AerSimulator(noise_model=calibration.noise_model(), seed_simulator=7)
    shots = 200000
    counts = simulator.run(to_qiskit(x, calibration)[0], shots=shots).result().get_counts()
    sampled = counts.get("1", 0) / shots
    if abs(sampled - exact) > 5 * math.sqrt(exact * (1 - exact) / shots):
        raise RuntimeError(f"sampled P(1) {sampled} departs from the exact {exact}")
    zero = {"name": "zero", "instructions": [{"name": "measure", "locus": ["QB1"], "args": {"key": "m"}}]}
    counts = simulator.run(to_qiskit(zero, calibration)[0], shots=shots).result().get_counts()
    e01 = calibration.readout("QB1")[0]
    if abs(counts.get("1", 0) / shots - e01) > 5 * math.sqrt(e01 * (1 - e01) / shots) + 1e-9:
        raise RuntimeError("a bare measure does not read the calibrated P(1 | 0)")
    if calibration.readout("QB1", heralded=True) == calibration.readout("QB1"):
        raise RuntimeError("the herald-conditioned readout of QB1 equals the unheralded one")
    far = sorted(calibration.qubits, key=lambda q: -int(q[2:]))[0]
    if frozenset(("QB1", far)) in calibration.cz:
        raise RuntimeError("the test pair is a coupler")
    bad = {"name": "bad", "instructions": [{"name": "cz", "locus": ["QB1", far], "args": {}}]}
    try:
        to_qiskit(bad, calibration)
    except ValueError:
        pass
    else:
        raise RuntimeError("a cz off the coupler graph was accepted")
    return (
        f"iqm sim: {len(calibration.qubits)} qubits, {len(calibration.cz)} CZ couplers; "
        f"X on QB1 exact P(1) {exact:.4f}, sampled {sampled:.4f}; off-graph cz refused"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument("case_dir", type=Path)
    run.add_argument("--qc", default="garnet")
    run.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "run":
        print(json.dumps(run_case(args.case_dir, args.qc, args.seed), indent=1))
    else:
        parser.error("choose run or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
