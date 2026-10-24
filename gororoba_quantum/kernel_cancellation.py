"""Kernel cancellation probe: the zero-divisor sign of the certified sedenion kernel on five qubits.

The certified u = (e4 - e15)/sqrt2 satisfies (L_e1 + L_e10) u = 0 exactly when K = L_e1^T L_e10 maps u
to -u (L_e1 is orthogonal). A Hadamard test whose control branch 0 applies L_e1 or L_e10 under a
selector cos(theta)|e1> + sin(theta)|e10> and whose branch 1 applies L_e1 reads

    <Z_c> = cos^2(theta) <L_e1 u, L_e1 u> + sin^2(theta) <L_e1 u, L_e10 u> = cos(2 theta)

for the kernel vector and 1 for the bright vector (e4 + e15)/sqrt2, the +1 eigenvector of K. Around
the balanced selector theta = pi/4 + phi the kernel reading -sin(2 phi) is odd in phi and changes sign
at the kernel point, so the arms +phi and -phi carry the zero-divisor sign at first order and their
sum holds every offset even in phi. The signed overlap Re<L_e2 u|B(t)|u> does not depend on u lying in
the kernel (scripts/iqm_probe_audit.py); this observable does.

Reduction to five qubits. u lives on {e4, e15}, and L_e1 and L_e10 flip index bits {0, 1} and {1, 3}:
bit 2 stays 1, bit 1 flips under both multipliers alike and always equals bit 0 xor 1, so data bits 0
and 3 carry the whole reachable span as a Bell pair, (|00> - |11>)/sqrt2 for the kernel vector and
(|00> + |11>)/sqrt2 for the bright one. Qubits: 0 = data bit 0, 1 = data bit 3, 2 = selector e1,
3 = selector e10 (one excitation between them), 4 = control. The cd_core signs of L_e1 and L_e10 on
e4 and e15 enter as one diagonal on (data bit 0, selector, control); on the reachable states it reduces
to Z_c Z_s0 CZ(s0, c) up to a global sign, kept here in full so a sign-table mutation changes it.

Run with --check for the exact laws and the mutations that must break them.
"""

from __future__ import annotations

import argparse
import math
import sys

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

from cd_core import cd_sign

DIM = 16
BASE = (4, 15)
E1, E10 = 1, 10
THETA = Parameter("theta")
# RY(BETA) then CX writes (|00> - |11>)/sqrt2 at BETA = -pi/2 (kernel) and (|00> + |11>)/sqrt2 at +pi/2 (bright).
BETA = Parameter("beta")
CHECK_PHI = (-0.3, -0.1, 0.0, 0.1, 0.3)


def diagonal(flip: dict[tuple[int, int], int] | None = None) -> list[float]:
    """cd_core signs over index b + 2 s + 8 c of (data bit 0, selector e1, selector e10, control).

    flip multiplies the sign of (multiplier, basis index) by -1, the mutation of the self-test.
    """

    def sign(m: int, q: int) -> float:
        return float(cd_sign(DIM, m, q) * (flip or {}).get((m, q), 1))

    entries = []
    for c in (0, 1):
        for s in range(4):
            for b in (0, 1):
                q = BASE[b]
                if c:
                    entries.append(sign(E1, q))
                elif s == 1:
                    entries.append(sign(E1, q))
                elif s == 2:
                    entries.append(sign(E10, q))
                else:
                    entries.append(1.0)
    return entries


def cancellation_probe(*, flip: dict[tuple[int, int], int] | None = None) -> QuantumCircuit:
    """One parametrized circuit for the kernel and bright vectors and every theta (values())."""
    circuit = QuantumCircuit(5, 1, name="kernel_cancellation")
    circuit.ry(BETA, 0)
    circuit.cx(0, 1)
    circuit.h(4)
    # cos(theta) on selector e1 (qubit 2), sin(theta) on selector e10 (qubit 3).
    circuit.ry(2 * THETA, 3)
    circuit.x(3)
    circuit.cx(3, 2)
    circuit.x(3)
    circuit.append(DiagonalGate(diagonal(flip)), [0, 2, 3, 4])
    # Branch 0: e1 flips data bit 0, e10 flips data bit 3; branch 1: e1 flips data bit 0.
    circuit.ccx(2, 4, 0, ctrl_state="01")
    circuit.ccx(3, 4, 1, ctrl_state="01")
    circuit.cx(4, 0)
    circuit.h(4)
    circuit.measure(4, 0)
    return circuit


def theta_of(phi: float) -> float:
    return math.pi / 4 + phi


def values(phi: float, bright: bool = False) -> dict[Parameter, float]:
    return {THETA: theta_of(phi), BETA: math.pi / 2 if bright else -math.pi / 2}


def law(phi: float, bright: bool = False) -> float:
    return 1.0 if bright else -math.sin(2 * phi)


def control_z(circuit: QuantumCircuit, phi: float, bright: bool = False) -> float:
    state = Statevector(circuit.assign_parameters(values(phi, bright)).remove_final_measurements(inplace=False))
    p = state.probabilities([4])
    return float(p[0] - p[1])


def check() -> str:
    circuit = cancellation_probe()
    for bright in (False, True):
        for phi in CHECK_PHI:
            z = control_z(circuit, phi, bright)
            if abs(z - law(phi, bright)) > 1e-12:
                raise ValueError(f"{'bright' if bright else 'kernel'} reads {z} at phi = {phi}, not {law(phi, bright)}")
    for q in BASE:
        mutated = cancellation_probe(flip={(E10, q): -1})
        if abs(control_z(mutated, 0.0)) < 0.25:
            raise ValueError(f"flipping the e10 sign at e{q} left the crossing at phi = 0")
    # Negating L_e10 on both support vectors makes u its +1 eigenvector: the kernel reads like the bright one.
    negated = cancellation_probe(flip={(E10, 4): -1, (E10, 15): -1})
    if any(abs(control_z(negated, phi) - 1.0) > 1e-12 for phi in CHECK_PHI):
        raise ValueError("negating L_e10 on the support left a crossing")
    return "kernel cancellation: kernel -sin(2 phi), bright 1; e10 sign flips at e4 and e15 break the crossing"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(check())
    return 0


if __name__ == "__main__":
    sys.exit(main())
