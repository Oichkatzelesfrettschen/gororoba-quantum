"""Independent matrix interpretation of emitted circuits and reference preservation.

These are ideal protocol fixtures, not a live-output acquisition or a native
compiler check. The interpreter accepts only the emitted logical gate set.
"""

from __future__ import annotations

import math
import re
import unittest

import numpy as np

from teleportation_contract import STATES, circuit, decode

H = np.array([[1, 1], [1, -1]], complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
I2 = np.eye(2, dtype=complex)
GATES = {"H": H, "X": X, "S": np.diag([1, 1j]), "Sdag": np.diag([1, -1j])}


def interpret(text: str, initial: np.ndarray) -> np.ndarray:
    state = initial.copy()
    for line in text.splitlines():
        if not line or line.startswith(("version", "qubit[", "bit[", "barrier", "b =")):
            continue
        match = re.fullmatch(r"(\w+) q\[(\d+)\](?:, q\[(\d+)\])?", line)
        if match is None:
            raise ValueError(f"unsupported reference instruction: {line}")
        gate, first, second = match.groups()
        q = int(first)
        out = np.zeros_like(state)
        if second is None:
            matrix = GATES[gate]
            for index, amplitude in enumerate(state):
                for target in (0, 1):
                    dest = (index & ~(1 << q)) | (target << q)
                    out[dest] += matrix[target, (index >> q) & 1] * amplitude
        else:
            r = int(second)
            for index, amplitude in enumerate(state):
                if gate == "CNOT":
                    dest = index ^ ((1 << r) if (index >> q) & 1 else 0)
                elif gate == "SWAP":
                    differ = ((index >> q) ^ (index >> r)) & 1
                    dest = index ^ (((1 << q) | (1 << r)) if differ else 0)
                else:
                    raise ValueError(f"unsupported reference gate: {gate}")
                out[dest] += amplitude
        state = out
    return state


class EmitterTests(unittest.TestCase):
    def test_emitted_circuit_on_permuted_routes(self) -> None:
        initial = np.zeros(16, complex)
        initial[0] = 1
        for route in ((0, 1, 2, 3), (3, 1, 0, 2)):
            for spec in STATES:
                state = interpret(circuit(4, route, spec.label), initial)
                self.assertAlmostEqual(float(np.vdot(state, state).real), 1)
                correct = 0.0
                for index, probability in enumerate(abs(state) ** 2):
                    a, b, d = ((index >> q) & 1 for q in (route[0], route[1], route[3]))
                    correct += probability * (decode(spec.basis, d, a, b) == spec.expected)
                self.assertAlmostEqual(float(correct), 1)

    def test_ideal_reference_and_downstream_gate_not_a_hardware_claim(self) -> None:
        # R is qubit 4; I is qubit 0. The emitted |0> case has no input gate
        # or destination basis gate, so its core can act on an entangled input.
        initial = np.zeros(32, complex)
        initial[[0, 17]] = 1 / math.sqrt(2)
        state = interpret(circuit(4, [0, 1, 2, 3], "0"), initial)
        target = np.array([1, 0, 0, 1], complex) / math.sqrt(2)
        mixed = np.zeros((4, 4), complex)
        t = np.diag([1, np.exp(1j * math.pi / 4)])
        for a in (0, 1):
            for b in (0, 1):
                branch = np.array([state[a + 2 * b + 8 * d + 16 * r] for r in (0, 1) for d in (0, 1)])
                self.assertAlmostEqual(float(np.vdot(branch, branch).real), 0.25)
                mixed += np.outer(branch, branch.conj())
                correction = np.linalg.matrix_power(Z, a) @ np.linalg.matrix_power(X, b)
                corrected = np.kron(I2, correction) @ (2 * branch)
                self.assertAlmostEqual(float(abs(np.vdot(target, corrected)) ** 2), 1)
                # T on D and T-dagger on the untouched reference cancel on
                # the Bell pair. This checks an ideal downstream operation.
                downstream = np.kron(t.conj().T, t) @ corrected
                self.assertAlmostEqual(float(abs(np.vdot(target, downstream)) ** 2), 1)
        np.testing.assert_allclose(mixed, np.eye(4) / 4, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
