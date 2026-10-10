"""Semiclassical phase estimation of x -> 2x mod 15 with one recycled control qubit.

Order finding in Shor's algorithm reads the eigenphases s/r of a modular
multiplier through a quantum Fourier transform; the semiclassical form measures
one control qubit per phase bit, resets it, and feeds each outcome forward as a
phase correction on the next round. For a = 2 and N = 15 the multiplier is the
cyclic rotation of four bits (2x = 16 x_3 + (2x mod 16) and 16 = 1 mod 15), the
exact permutation on every residue 1..14, and its order is r = 4. Preparing an
eigenstate |u_s> = (1/2) sum_k exp(-2 pi i s k / 4) |2^k> makes the two-bit
readout deterministic, s itself, which a decohered device cannot imitate; the
|1> input of textbook Shor reads all four phases uniformly, as decoherence
does. The identity multiplier is the null control and reads 0.

The circuits test mid-circuit measurement, reset, and classical feed-forward,
the machinery of the semiclassical QFT in large factoring estimates. They do
not factor anything: multiplication by 2 mod 15 is a rotation, the known easy
case (Smolin, Smith, and Vargo, Nature 499, 163 (2013)).
"""

from __future__ import annotations

import math

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator


def controlled_rotate(qc: QuantumCircuit, ctrl: int, work: list[int], steps: int) -> None:
    """Controlled cyclic left rotation of the work bits by steps, from Fredkin gates.

    Rotation by 1 is SWAP(2,3), SWAP(1,2), SWAP(0,1); rotation by 2 is SWAP(0,2),
    SWAP(1,3). Each SWAP becomes a controlled SWAP on ctrl.
    """
    pairs = {1: [(2, 3), (1, 2), (0, 1)], 2: [(0, 2), (1, 3)]}[steps]
    for a, b in pairs:
        qc.cswap(ctrl, work[a], work[b])


def eigenstate_prep(qc: QuantumCircuit, work: list[int], s: int) -> None:
    """|u_s>: a W state over the one-hot patterns |2^k>, phase -2 pi s k / 4 on qubit k."""
    qc.x(work[0])
    for k, remaining in ((0, 4), (1, 3), (2, 2)):
        qc.cry(2 * math.acos(math.sqrt(1 / remaining)), work[k], work[k + 1])
        qc.cx(work[k + 1], work[k])
    for k in range(1, 4):
        qc.p(-2 * math.pi * s * k / 4, work[k])


def folded_qpe(s: int, identity: bool = False) -> QuantumCircuit:
    """Two-bit semiclassical phase estimation on |u_s>; the outcome integer is s.

    Round one applies U^2 (rotation by 2), whose kickback exp(2 pi i 2 phi)
    carries the low phase bit phi_2 into clbit 0. Round two reuses the reset
    control, applies U, and removes the known 0.0phi_2 part with a phase -pi/2
    conditioned on clbit 0, leaving the high bit phi_1 for clbit 1.
    """
    ctrl = QuantumRegister(1, "c")
    work_reg = QuantumRegister(4, "w")
    bits = ClassicalRegister(2, "c0")
    qc = QuantumCircuit(ctrl, work_reg, bits, name=f"folded_qpe_s{s}" + ("_id" if identity else ""))
    work = [1, 2, 3, 4]
    eigenstate_prep(qc, work, s)
    qc.h(0)
    if not identity:
        controlled_rotate(qc, 0, work, 2)
    qc.h(0)
    qc.measure(0, bits[0])
    qc.reset(0)
    qc.h(0)
    if not identity:
        controlled_rotate(qc, 0, work, 1)
    with qc.if_test((bits[0], 1)):
        qc.p(-math.pi / 2, 0)
    qc.h(0)
    qc.measure(0, bits[1])
    return qc


def _verify() -> None:
    """Multiplier, eigenstates, and readout checked exactly; raises on the first deviation."""
    rot = QuantumCircuit(5)
    controlled_rotate(rot, 0, [1, 2, 3, 4], 1)
    mat = Operator(rot).data
    for x in range(1, 15):
        # control set: index 1 + 2x in the 5-qubit little-endian basis
        out = int(np.argmax(np.abs(mat[:, 1 + 2 * x])))
        if out != 1 + 2 * ((2 * x) % 15):
            raise RuntimeError(f"controlled rotation sends {x} to {(out - 1) // 2}, not {(2 * x) % 15}")
    for s in range(4):
        prep = QuantumCircuit(4)
        eigenstate_prep(prep, [0, 1, 2, 3], s)
        u = QuantumCircuit(5)
        controlled_rotate(u, 0, [1, 2, 3, 4], 1)
        state = Statevector(prep)
        rotated = state.evolve(Operator(u).data[1::2, 1::2])
        overlap = complex(np.vdot(state.data, rotated.data))
        if abs(overlap - np.exp(2j * math.pi * s / 4)) > 1e-12:
            raise RuntimeError(f"|u_{s}> eigenvalue {overlap}")
    sim = AerSimulator()
    for s in range(4):
        for identity in (False, True):
            counts = sim.run(folded_qpe(s, identity), shots=2000, seed_simulator=1).result().get_counts()
            want = 0 if identity else s
            if counts.get(format(want, "02b"), 0) != 2000:
                raise RuntimeError(f"s={s} identity={identity}: counts {counts}, expected all {want}")
    print("order finding: x2 mod 15 exact on residues 1..14; |u_s> eigenvalues i^s; readout s, null 0")


if __name__ == "__main__":
    _verify()
