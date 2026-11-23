"""Full-outcome response of the plane family with a nonuniform fixed point of the excess contraction.

grover_plane_sim.Response keeps one number per depth, the marked probability, and contracts the excess loss toward
the maximally mixed state I/8: the leaked weight returns as the uniform state. This module keeps all eight outcome
probabilities of every depth under the same calibrated noisy path and plane rotation, and lets the contraction
rho -> s rho + (1 - s) tr(rho) Sigma end at a diagonal state Sigma that need not be uniform. Sigma comes in three
forms: the uniform state (the plane family unchanged), the three weights of the S3-invariant sector of the marked
vertex (the marked state and the Hamming shells of distance 1, 2 and 3, the sector the six cube symmetries that fix the
marked vertex leave invariant: four orbits), and a product of per-qubit populations. The eight outcome probabilities
are 1/8 + a (D - 1/8), the depth-independent factor a of the plane family applied to every cell.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import grover_plane_sim as sim

SHELLS = ("marked", "d1", "d2", "d3")


def shell_of(index: int, marked: int) -> int:
    """0 for the marked outcome, otherwise the Hamming distance to it."""
    return bin(index ^ marked).count("1")


def sigma_uniform() -> np.ndarray:
    return np.full(8, 1 / 8)


def sigma_shells(weights: tuple[float, float, float], marked: int) -> np.ndarray:
    """Diagonal state with the weights u_marked, u_d1, u_d2 (and u_d3 = 1 - the sum) spread evenly inside each shell."""
    u = [*weights, 1.0 - sum(weights)]
    size = [1, 3, 3, 1]
    return np.array([u[shell_of(i, marked)] / size[shell_of(i, marked)] for i in range(8)])


def sigma_qubits(populations: tuple[float, float, float]) -> np.ndarray:
    """Product state diag(prod_q (1 - b_q, b_q)) with b_q the population of bit q."""
    return np.array([np.prod([b if (i >> q) & 1 else 1 - b for q, b in enumerate(populations)]) for i in range(8)])


class FullResponse:
    """The eight outcome probabilities of every depth for (a, s, eps, Sigma), with the circuits and calibration of one
    mark exactly as sim.Response builds them (readout=False: the state's own distribution)."""

    def __init__(self, circuits: dict[int, dict[str, Any]], calibration: Any, path: list[str], marked: str) -> None:
        self.depths = sorted(circuits)
        self.marked = sum(int(c) << q for q, c in enumerate(marked))
        frames = {k: sim.logical_frame(circuits[k], calibration, path, marked, k, True) for k in self.depths}
        top = frames[self.depths[-1]]
        self.lambdas = top["lambda"]
        start = top["frames"][0]
        self.start = sim.vec(start.conj().T @ np.diag([1.0] + [0.0] * 7).astype(complex) @ start)
        self.readers: dict[int, np.ndarray] = {}
        for k in self.depths:
            rows = np.zeros((8, 64))
            for i in range(8):
                basis = np.zeros((8, 8), dtype=complex)
                basis[i, i] = 1
                dist = sim.outcome_distribution(basis, frames[k]["measured"], path, calibration, readout=False)
                for o in range(8):
                    rows[o, i * 8 + i] = dist[o]
            self.readers[k] = rows @ frames[k]["tail"] @ sim.conjugation(frames[k]["frames"][k])

    def distributions(self, s: float, eps: float, sigma: np.ndarray, a: float = 1.0) -> dict[int, np.ndarray]:
        u = sim.plane_rotation_unitary(eps, self.marked)
        ud = u.conj().T
        target = np.diag(sigma).astype(complex)
        rho = self.start
        out: dict[int, np.ndarray] = {}
        for j, lam in enumerate(self.lambdas, start=1):
            r = (lam @ rho).reshape(8, 8)
            r = u @ r @ ud
            r = s * r + (1 - s) * np.trace(r) * target
            rho = r.reshape(64)
            if j in self.readers:
                out[j] = 1 / 8 + a * (np.real(self.readers[j] @ rho) - 1 / 8)
        return out
