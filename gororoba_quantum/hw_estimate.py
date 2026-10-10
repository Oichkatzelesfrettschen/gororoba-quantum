"""Compile each circuit once for a real backend, then count and simulate that object.

transpile() against the backend Target fixes layout, routing, and the ISA gate
set under SEED_TRANSPILER. The CZ count, depth, and noisy distribution all
describe that one ISA circuit: AerSimulator.from_backend runs it unchanged under
the noise model built from the backend calibration, with SEED_SIMULATOR fixing
shot sampling. A control compiles from its experiment's initial layout, so the
two compare one patch of the device against itself. Reading backend metadata
uses the network; nothing submits a QPU job. --out archives the ISA circuits as
QPY beside a JSON record of versions, seeds, calibration timestamp, layout, and
results, so the counted and simulated circuit is the one a later submission runs.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

import predict
from cd_core import sedenion_zero_divisors
from designs import (
    SPECTRUM_EXEMPLARS,
    SWEEP_PHASES,
    design_a_associator,
    design_b_zero_divisor,
    design_c_associator_spectrum,
    design_d_phase_sweep,
)

BACKEND = "ibm_fez"
SHOTS = 4096
OPT_LEVEL = 3
SEED_TRANSPILER = 20261010
SEED_SIMULATOR = 20261011


def _physical(isa: QuantumCircuit, names: set[str] | None = None) -> list[int]:
    """Physical qubits touched by isa, or only by the named operations."""
    touched = {
        isa.find_bit(q).index
        for inst in isa.data
        if inst.operation.name != "barrier" and (names is None or inst.operation.name in names)
        for q in inst.qubits
    }
    return sorted(touched)


def _distribution(counts: dict[str, int], clbits: int) -> np.ndarray:
    dist = np.zeros(2**clbits)
    for key, c in counts.items():
        dist[int(key.replace(" ", ""), 2)] += c
    return np.asarray(dist / dist.sum())


def _tvd(p: np.ndarray, q: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(p - q)))


def readout_corrected_p0(p0_measured: float, props: Any, qubit: int) -> float:
    """P(0) before readout error, inverting P0_meas = P0 (1 - e10) + (1 - P0) e01.

    e10 = prob_meas1_prep0 and e01 = prob_meas0_prep1 belong to the physical
    qubit that measured the ancilla. Routing can end the dark and bright
    circuits on different qubits, so each term of the suppression ratio is
    corrected with the calibration of its own readout qubit.
    """
    e10 = props.qubit_property(qubit, "prob_meas1_prep0")[0]
    e01 = props.qubit_property(qubit, "prob_meas0_prep1")[0]
    return float((p0_measured - e01) / (1.0 - e10 - e01))


def run_case(
    name: str,
    qc: QuantumCircuit,
    ideal: np.ndarray,
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
    noisy = _distribution(counts, qc.num_clbits)
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
        "ideal": [round(float(p), 12) for p in ideal],
        "noisy": [round(float(p), 6) for p in noisy],
        "tvd_to_ideal": _tvd(noisy, ideal),
        "counts": dict(sorted(counts.items())),
    }


def fit_fringe(phases: list[float], p0: list[float]) -> dict[str, float]:
    """Least-squares P0 = o + A cos(phi) + B sin(phi): offset, visibility, phase.

    Visibility is 2 sqrt(A^2 + B^2) and the fringe phase is atan2(B, A); the
    ideal (1 - s cos phi)/2 has offset 1/2, visibility 1, and phase 0 for s = -1.
    """
    basis = np.column_stack([np.ones(len(phases)), np.cos(phases), np.sin(phases)])
    (o, a, b), *_ = np.linalg.lstsq(basis, np.array(p0), rcond=None)
    return {"offset": float(o), "visibility": float(2 * math.hypot(a, b)), "phase": float(math.atan2(b, a))}


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
    cases: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    def run(name: str, qc: QuantumCircuit, ideal: np.ndarray, layout: list[int] | None = None) -> dict[str, Any]:
        case = run_case(name, qc, ideal, backend, sim, layout)
        cases.append(case)
        print(
            f"{name}: depth={case['depth']} cz={case['cz']} qubits={case['physical_qubits']} "
            f"tvd_to_ideal={case['tvd_to_ideal']:.4f}"
        )
        return case

    run("design_a_1_2", design_a_associator(1, 2)[0], np.array([0.0, 1.0]))

    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    tag = f"{i}_{j}_{k}_{el}"
    dark_p0 = predict.zero_divisor_p0((i, j), (k, el), s)
    bright_p0 = predict.zero_divisor_p0((i, j), (k, el), -s)
    dark = run(f"design_b_dark_{tag}", design_b_zero_divisor((i, j), (k, el), s), np.array([dark_p0, 1 - dark_p0]))
    layout = dark["initial_virtual_to_physical"]
    bright = run(
        f"design_b_bright_{tag}",
        design_b_zero_divisor((i, j), (k, el), -s),
        np.array([bright_p0, 1 - bright_p0]),
        layout,
    )
    props = backend.properties()
    q_dark, q_bright = dark["measured_physical_qubits"][0], bright["measured_physical_qubits"][0]
    c_dark = readout_corrected_p0(dark["noisy"][0], props, q_dark)
    c_bright = readout_corrected_p0(bright["noisy"][0], props, q_bright)
    summary["design_b"] = {
        "readout_qubits": [q_dark, q_bright],
        "p0_dark": dark["noisy"][0],
        "p0_bright": bright["noisy"][0],
        "ratio": dark["noisy"][0] / bright["noisy"][0],
        "p0_dark_readout_corrected": c_dark,
        "p0_bright_readout_corrected": c_bright,
        "ratio_readout_corrected": c_dark / c_bright,
    }

    sweep = []
    for phase in SWEEP_PHASES:
        want = predict.phase_sweep_p0((i, j), (k, el), phase)
        case = run(
            f"design_d_{tag}_phase_{phase:.4f}",
            design_d_phase_sweep((i, j), (k, el), phase),
            np.array([want, 1 - want]),
            layout,
        )
        sweep.append(case["noisy"][0])
    summary["design_d_fit"] = fit_fringe(SWEEP_PHASES, sweep)

    summary["design_c"] = []
    for dim, ci, cj in SPECTRUM_EXEMPLARS:
        omega = predict.associator_phase(dim, ci, cj)
        ideal = predict.walsh_distribution(omega)
        flipped = predict.walsh_distribution([w * (-1 if x == 0 else 1) for x, w in enumerate(omega)])
        true = run(f"design_c_{dim}_{ci}_{cj}", design_c_associator_spectrum(dim, ci, cj), ideal)
        flip = run(
            f"design_c_{dim}_{ci}_{cj}_flip",
            design_c_associator_spectrum(dim, ci, cj, flip=cj),
            flipped,
            true["initial_virtual_to_physical"],
        )
        hn = np.array([[(-1) ** bin(x & y).count("1") for x in range(dim)] for y in range(dim)]) / math.sqrt(dim)
        plus = np.full(dim, 1.0 / math.sqrt(dim))
        omitted = np.abs(hn @ predict.left_mult_matrix(dim, ci) @ predict.left_mult_matrix(dim, cj) @ plus) ** 2
        omit = run(
            f"design_c_{dim}_{ci}_{cj}_omit",
            design_c_associator_spectrum(dim, ci, cj, omit_adjoint=True),
            omitted,
            true["initial_virtual_to_physical"],
        )
        noisy = np.array(true["noisy"])
        summary["design_c"].append(
            {
                "dim": dim,
                "pair": [ci, cj],
                "tvd_noisy_to_ideal": _tvd(noisy, ideal),
                "tvd_noisy_to_flip_prediction": _tvd(noisy, flipped),
                "tvd_noisy_to_omit_prediction": _tvd(noisy, omitted),
                "tvd_flip_noisy_to_flip_prediction": flip["tvd_to_ideal"],
                "tvd_omit_noisy_to_omit_prediction": omit["tvd_to_ideal"],
            }
        )

    print(f"\ndesign B P(anc=0): {summary['design_b']}")
    print(f"design D fringe fit (ideal offset 0.5, visibility 1, phase 0): {summary['design_d_fit']}")
    for entry in summary["design_c"]:
        print(f"design C {entry}")

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
            "summary": summary,
            "cases": [{key: val for key, val in case.items() if key != "isa"} for case in cases],
        }
        (args.out / f"{backend.name}_record.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"\narchived {len(cases)} ISA circuits and the record under {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
