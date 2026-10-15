"""Readout, relaxation and Ramsey baseline of six physical qubits, single-qubit gates only.

Seven static circuits act on BASELINE_WIDTH qubits with no two-qubit gate, each
qubit measured into the clbit of its own index, so any six placed qubits
characterize themselves independently:

- ground: measure. Ideal all zero; P(1) per qubit is the |0> assignment error.
- excited: X, measure. Ideal all one; P(0) per qubit is the |1> assignment error.
- relaxation: X, a RELAXATION_DT idle, measure. Ideal all one; the drop of P(1)
  from excited reads energy relaxation over the idle.
- Ramsey: H, an idle of RAMSEY_DT[k], then H (X quadrature) or Sdg and H (Y
  quadrature), measure. Ideal: all zero for X and uniform for Y, so
  <X> = 1 - 2 P(1 | x) and <Y> = 1 - 2 P(1 | y) give each qubit's phase
  atan2(<Y>, <X>) and visibility over the idle; a static detuning delta
  rotates the phase by 2 pi delta t.

Idles are integer dt on every qubit; the returned schedule, not these requests,
times the exposure. The group carries no admission: it is a characterization,
analyzed per physical qubit from the collected distributions.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from experiments import Group, Member

BASELINE_WIDTH = 6
RELAXATION_DT = 12500
RAMSEY_DT = (500, 2500)


def _circuit(name: str) -> QuantumCircuit:
    return QuantumCircuit(BASELINE_WIDTH, BASELINE_WIDTH, name=name)


def _point(outcome: int) -> np.ndarray:
    ideal = np.zeros(1 << BASELINE_WIDTH)
    ideal[outcome] = 1.0
    return ideal


def baseline_circuits() -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    qubits = list(range(BASELINE_WIDTH))
    everything = (1 << BASELINE_WIDTH) - 1
    ground = _circuit("baseline_ground")
    ground.measure(qubits, qubits)
    excited = _circuit("baseline_excited")
    excited.x(qubits)
    excited.measure(qubits, qubits)
    relaxation = _circuit("baseline_relaxation")
    relaxation.x(qubits)
    relaxation.delay(RELAXATION_DT, qubits, unit="dt")
    relaxation.measure(qubits, qubits)
    members = [
        ("baseline_ground", ground, _point(0)),
        ("baseline_excited", excited, _point(everything)),
        ("baseline_relaxation", relaxation, _point(everything)),
    ]
    for delay in RAMSEY_DT:
        for quadrature in ("x", "y"):
            circuit = _circuit(f"baseline_ramsey_{quadrature}_{delay}dt")
            circuit.h(qubits)
            circuit.delay(delay, qubits, unit="dt")
            if quadrature == "y":
                circuit.sdg(qubits)
            circuit.h(qubits)
            circuit.measure(qubits, qubits)
            ideal = _point(0) if quadrature == "x" else np.full(1 << BASELINE_WIDTH, 1.0 / (1 << BASELINE_WIDTH))
            members.append((circuit.name, circuit, ideal))
    return tuple(members)


def bit_one_probability(distribution: np.ndarray, bit: int) -> float:
    return float(sum(p for outcome, p in enumerate(distribution) if outcome >> bit & 1))


def qubit_baseline_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in baseline_circuits())

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for bit in range(BASELINE_WIDTH):
            excited = bit_one_probability(distributions["baseline_excited"], bit)
            relaxed = bit_one_probability(distributions["baseline_relaxation"], bit)
            summary[f"q{bit}_p1_ground"] = bit_one_probability(distributions["baseline_ground"], bit)
            summary[f"q{bit}_p0_excited"] = 1.0 - excited
            summary[f"q{bit}_relaxation_retained"] = relaxed / excited if excited else float("nan")
            for delay in RAMSEY_DT:
                x = 1.0 - 2.0 * bit_one_probability(distributions[f"baseline_ramsey_x_{delay}dt"], bit)
                y = 1.0 - 2.0 * bit_one_probability(distributions[f"baseline_ramsey_y_{delay}dt"], bit)
                summary[f"q{bit}_ramsey_{delay}dt_phase"] = float(np.arctan2(y, x))
                summary[f"q{bit}_ramsey_{delay}dt_visibility"] = float(np.hypot(x, y))
        return summary

    return Group("qubit_baseline", members, summarize)


if __name__ == "__main__":
    from qiskit.quantum_info import Statevector

    for name, circuit, ideal in baseline_circuits():
        probabilities = Statevector(circuit.remove_final_measurements(inplace=False)).probabilities()
        if not np.allclose(probabilities, ideal, atol=1e-12):
            raise SystemExit(f"{name}: statevector law differs from its ideal")
    group = qubit_baseline_group()
    ideal_summary = group.summarize({member.name: member.ideal for member in group.members})
    if any(abs(ideal_summary[f"q{b}_ramsey_{RAMSEY_DT[0]}dt_visibility"] - 1.0) > 1e-12 for b in range(BASELINE_WIDTH)):
        raise SystemExit("ideal Ramsey visibility differs from one")
    print(f"qubit baseline: {len(group.members)} circuits on {BASELINE_WIDTH} qubits match their ideal laws")
