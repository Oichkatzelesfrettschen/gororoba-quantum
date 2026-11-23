"""Plane model of the line-native Grover retention: the model-anchored plane family, its fits and its predictions.

The exact density-matrix model of grover_plane_sim (the model of iqm_grover_line.predicted) has, in the logical frame,
the iteration channels Lambda_j and, on the plane of the marked state, the affine maps v' = M v + w (1 - n). The family
that carries the retained data is anchored to that model and adds three excess parameters:

    a    the plane vector entering the first iteration contracts toward the maximally mixed point by a;
    s    every iteration contracts the plane vector toward that point by a further factor s;
    eps  every iteration rotates the Bloch vector about the y axis by a further angle eps (radians).

(a, s, eps) = (1, 1, 0) is the model, eps = 0 is the geometric excess loss rho_k = a s^k to first order, and eps != 0 is
a coherent rotation error. The marked probability at depth k reads the plane vector through the circuit's own tail
and readout: P_k = e_k . v_k + (1 - n_k) h_k, with e_k and h_k the model's probability of the marked outcome from
the plane
basis operators and from the normalized complement through the tail of the depth-k circuit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

import grover_plane_sim as sim

CENTER = np.array([0.25, 0.0, 0.0, 0.0])


@dataclass(frozen=True)
class Arm:
    """One depth-k circuit of a mark under a calibration: the model's plane maps and tail functional."""

    k: int
    marked_index: int
    maps: list[tuple[np.ndarray, np.ndarray]]
    reader: np.ndarray
    reader_complement: float
    model_probability: float
    ideal_probability: float


def ideal_probability(k: int) -> float:
    return math.sin((2 * k + 1) * sim.THETA) ** 2


def marked_index(marked: str) -> int:
    return sum(int(c) << q for q, c in enumerate(marked))


def arm_of(circuit: dict[str, Any], calibration: Any, path: list[str], marked: str, k: int, noisy: bool = True) -> Arm:
    frame = sim.logical_frame(circuit, calibration, path, marked, k, noisy)
    index = marked_index(marked)
    maps = [sim.plane_map(lam, index) for lam in frame["lambda"]]
    basis, complement = sim.plane_operators(index)
    rotate = sim.conjugation(frame["frames"][k])

    def read(op: np.ndarray) -> float:
        out = sim.unvec(frame["tail"] @ (rotate @ sim.vec(op)))
        return float(sim.outcome_distribution(out, frame["measured"], path, calibration, readout=False)[index])

    reader = np.array([read(b) for b in basis])
    rho = sim.vec(np.diag([1.0] + [0.0] * 7).astype(complex))
    state = frame["frames"][0].conj().T @ sim.unvec(rho) @ frame["frames"][0]
    rho = sim.vec(state)
    for lam in frame["lambda"]:
        rho = lam @ rho
    final = sim.unvec(frame["tail"] @ (rotate @ rho))
    model = float(sim.outcome_distribution(final, frame["measured"], path, calibration, readout=False)[index])
    return Arm(k, index, maps, reader, read(complement), model, ideal_probability(k))


def contract(v: np.ndarray, factor: float) -> np.ndarray:
    return CENTER + factor * (v - CENTER)


def rotate(v: np.ndarray, eps: float) -> np.ndarray:
    c, s = math.cos(eps), math.sin(eps)
    return np.array([v[0], c * v[1] - s * v[3], v[2], s * v[1] + c * v[3]])


def vector(arm: Arm, a: float, s: float, eps: float) -> np.ndarray:
    v = contract(sim.initial_vector(), a)
    for m, w in arm.maps:
        v = contract(rotate(sim.step_affine(m, w, v), eps), s)
    return v


def probability(arm: Arm, a: float, s: float, eps: float) -> float:
    v = vector(arm, a, s, eps)
    return float(arm.reader @ v + (1 - v[0]) * arm.reader_complement)


def retention(arm: Arm, p: float) -> float:
    return (p - 1 / 8) / (arm.ideal_probability - 1 / 8)
