"""Compile each circuit once for a real backend, then count and simulate that object.

transpile() against the backend Target fixes layout, routing, and the ISA gate
set under SEED_TRANSPILER. The CZ count, depth, and noisy probabilities all
describe that one ISA circuit: AerSimulator.from_backend runs it unchanged under
the noise model built from the backend calibration, with SEED_SIMULATOR fixing
shot sampling. Reading backend metadata uses the network; nothing submits a QPU
job. --out archives the ISA circuits as QPY beside a JSON record of versions,
seeds, calibration timestamp, layout, and results, so the counted and simulated
circuit is the one a later submission runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qpy, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

from cd_core import sedenion_zero_divisors
from designs import design_a_associator, design_b_zero_divisor

BACKEND = "ibm_fez"
SHOTS = 4096
OPT_LEVEL = 3
SEED_TRANSPILER = 20261010
SEED_SIMULATOR = 20261011


def _p_one(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return sum(c for k, c in counts.items() if k.replace(" ", "")[-1] == "1") / total


def _physical(isa: QuantumCircuit, names: set[str] | None = None) -> list[int]:
    """Physical qubits touched by isa, or only by the named operations."""
    touched = {
        isa.find_bit(q).index
        for inst in isa.data
        if inst.operation.name != "barrier" and (names is None or inst.operation.name in names)
        for q in inst.qubits
    }
    return sorted(touched)


def run_case(
    name: str,
    qc: QuantumCircuit,
    ideal_p1: float,
    backend: Any,
    sim: AerSimulator,
    initial_layout: list[int] | None = None,
) -> dict[str, Any]:
    isa = transpile(
        qc,
        backend=backend,
        optimization_level=OPT_LEVEL,
        seed_transpiler=SEED_TRANSPILER,
        initial_layout=initial_layout,
    )
    isa.name = name
    counts = sim.run(isa, shots=SHOTS, seed_simulator=SEED_SIMULATOR).result().get_counts()
    layout = isa.layout
    return {
        "name": name,
        "isa": isa,
        "depth": isa.depth(),
        "cz": isa.count_ops().get("cz", 0),
        "ops": dict(isa.count_ops()),
        "initial_virtual_to_physical": layout.initial_index_layout(filter_ancillas=True) if layout else None,
        "physical_qubits": _physical(isa),
        "measured_physical_qubits": _physical(isa, {"measure"}),
        "ideal_p1": ideal_p1,
        "noisy_p1": _p_one(counts),
        "counts": dict(sorted(counts.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backend", default=BACKEND)
    parser.add_argument("--out", type=Path, help="directory for the QPY archive and JSON record")
    args = parser.parse_args(argv)

    service = QiskitRuntimeService()
    backend = service.backend(args.backend)
    calibrated = backend.properties().last_update_date
    usage = service.usage()
    print(f"backend {backend.name}: {backend.num_qubits} qubits, calibration {calibrated.isoformat()}")
    print(f"QPU budget: {usage['usage_remaining_seconds']} s remaining of {usage['usage_limit_seconds']} s\n")

    sim = AerSimulator.from_backend(backend)
    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    # Design B measures the ancilla; P1 = 1 - P(anc=0), ideal 1 dark and 0 bright.
    # The bright control starts on the dark circuit's physical qubits, so the
    # suppression ratio compares one patch of the device against itself.
    tag = f"{i}_{j}_{k}_{el}"
    dark = run_case(f"design_b_dark_{tag}", design_b_zero_divisor((i, j), (k, el), s), 1.0, backend, sim)
    bright = run_case(
        f"design_b_bright_{tag}",
        design_b_zero_divisor((i, j), (k, el), -s),
        0.0,
        backend,
        sim,
        initial_layout=dark["initial_virtual_to_physical"],
    )
    cases = [run_case("design_a_1_2", design_a_associator(1, 2)[0], 1.0, backend, sim), dark, bright]
    for case in cases:
        print(
            f"{case['name']}: depth={case['depth']} cz={case['cz']} qubits={case['physical_qubits']} "
            f"measured={case['measured_physical_qubits']} ideal P1={case['ideal_p1']:.0f} "
            f"noisy P1={case['noisy_p1']:.4f}"
        )
    p_dark, p_bright = 1.0 - dark["noisy_p1"], 1.0 - bright["noisy_p1"]
    print(f"design B P(anc=0): dark={p_dark:.4f} bright={p_bright:.4f} ratio={p_dark / p_bright:.4f}")

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        with open(args.out / f"{backend.name}_isa.qpy", "wb") as handle:
            qpy.dump([case["isa"] for case in cases], handle)
        record = {
            "backend": backend.name,
            "calibration_last_update": calibrated.isoformat(),
            "versions": {pkg: version(pkg) for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
            "optimization_level": OPT_LEVEL,
            "seed_transpiler": SEED_TRANSPILER,
            "seed_simulator": SEED_SIMULATOR,
            "shots": SHOTS,
            "qpu_executed": False,
            "cases": [{key: val for key, val in case.items() if key != "isa"} for case in cases],
        }
        (args.out / f"{backend.name}_record.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"\narchived {len(cases)} ISA circuits and the record under {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
