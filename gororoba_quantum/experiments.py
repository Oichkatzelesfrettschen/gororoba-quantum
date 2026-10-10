"""Experiment groups: each a primary circuit, its controls, and their ideal distributions.

A group runs on one backend from one initial layout: the primary circuit picks
the layout and every control compiles onto it, so a control compares one patch
of the device against itself. Ideals come from predict.py; summaries reduce the
noisy or measured distributions to each design's observable.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

import predict
from cd_core import sedenion_zero_divisors
from designs import (
    SPECTRUM_EXEMPLARS,
    SWEEP_PHASES,
    design_a_associator,
    design_c_associator_spectrum,
    design_d_phase_sweep,
)

Summary = Callable[[dict[str, np.ndarray]], dict[str, float]]


@dataclass(frozen=True)
class Member:
    """One circuit of a group; binding assigns the parameters of a shared circuit.

    Members whose circuit is the same parametrized object as the group's
    primary compile once and differ only by bound angles, so they share routing
    and readout qubits (live_run.select).
    """

    name: str
    circuit: QuantumCircuit
    ideal: np.ndarray
    binding: dict[Parameter, float] | None = None


@dataclass(frozen=True)
class Group:
    name: str
    members: tuple[Member, ...]
    summarize: Summary


def tvd(p: np.ndarray, q: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(np.asarray(p) - np.asarray(q))))


def fit_fringe(phases: list[float], p0: list[float]) -> dict[str, float]:
    """Least-squares P0 = o + A cos(phi) + B sin(phi): offset, visibility, phase.

    Visibility is 2 sqrt(A^2 + B^2) and the fringe phase is atan2(B, A); the
    ideal (1 - s cos phi)/2 has offset 1/2, visibility 1, and phase 0 for s = -1.
    """
    basis = np.column_stack([np.ones(len(phases)), np.cos(phases), np.sin(phases)])
    (o, a, b), *_ = np.linalg.lstsq(basis, np.array(p0), rcond=None)
    return {"offset": float(o), "visibility": float(2 * math.hypot(a, b)), "phase": float(math.atan2(b, a))}


def _two_outcome(p1: float) -> np.ndarray:
    return np.array([1.0 - p1, p1])


def _design_a() -> Group:
    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        return {"p1": float(dist["design_a_1_2"][1])}

    member = Member("design_a_1_2", design_a_associator(1, 2)[0], _two_outcome(1.0))
    return Group("design_a", (member,), summarize)


def _zero_divisor_fringe() -> Group:
    """Design B dark and bright and the design D sweep as bindings of one circuit.

    b = (e_k + e^{i phi} e_l)/sqrt2 covers all of them: phi = pi for s = -1 is
    the zero divisor, phi = 0 its sign-flipped control, and the sweep phases
    the fringe. One parametrized circuit gives every member the same compiled
    routing and readout qubit, so the suppression ratio and the fringe compare
    one set of physical qubits.
    """
    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    tag = f"{i}_{j}_{k}_{el}"
    phi = Parameter("phi")
    template = design_d_phase_sweep((i, j), (k, el), phi)
    dark_phase, bright_phase = (0.0, math.pi) if s > 0 else (math.pi, 0.0)
    dark_p0 = predict.zero_divisor_p0((i, j), (k, el), s)
    bright_p0 = predict.zero_divisor_p0((i, j), (k, el), -s)
    members = [
        Member(f"design_b_dark_{tag}", template, _two_outcome(1 - dark_p0), {phi: dark_phase}),
        Member(f"design_b_bright_{tag}", template, _two_outcome(1 - bright_p0), {phi: bright_phase}),
    ]
    sweep_names = []
    for n, phase in enumerate(SWEEP_PHASES):
        want = predict.phase_sweep_p0((i, j), (k, el), phase)
        name = f"design_d_{tag}_phase_{n}of8"
        sweep_names.append(name)
        members.append(Member(name, template, _two_outcome(1 - want), {phi: phase}))

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        dark, bright = float(dist[members[0].name][0]), float(dist[members[1].name][0])
        fit = fit_fringe(SWEEP_PHASES, [float(dist[name][0]) for name in sweep_names])
        return {"p0_dark": dark, "p0_bright": bright, "ratio": dark / bright if bright else math.nan} | fit

    return Group("zero_divisor_fringe", tuple(members), summarize)


def _associator_spectrum(dim: int, i: int, j: int) -> Group:
    n = dim.bit_length() - 1
    omega = predict.associator_phase(dim, i, j)
    true = predict.walsh_distribution(omega)
    flipped = predict.walsh_distribution([w * (-1 if x == 0 else 1) for x, w in enumerate(omega)])
    hn = np.array([[(-1) ** bin(x & y).count("1") for x in range(dim)] for y in range(dim)]) / math.sqrt(dim)
    plus = np.full(dim, 1.0 / math.sqrt(dim))
    omitted = np.abs(hn @ predict.left_mult_matrix(dim, i) @ predict.left_mult_matrix(dim, j) @ plus) ** 2
    base = f"design_c_{dim}_{i}_{j}"
    members = (
        Member(base, design_c_associator_spectrum(dim, i, j), true),
        # flip=j negates L_{e_i}'s sign on input j, which the block sees at x = 0.
        Member(f"{base}_flip", design_c_associator_spectrum(dim, i, j, flip=j), flipped),
        Member(f"{base}_omit", design_c_associator_spectrum(dim, i, j, omit_adjoint=True), omitted),
    )

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        got = dist[base]
        return {
            "qubits": float(n),
            "tvd_to_true": tvd(got, true),
            "tvd_to_flip_prediction": tvd(got, flipped),
            "tvd_to_omit_prediction": tvd(got, omitted),
            "flip_control_tvd_to_own": tvd(dist[f"{base}_flip"], flipped),
            "omit_control_tvd_to_own": tvd(dist[f"{base}_omit"], omitted),
        }

    return Group(base, members, summarize)


def experiment_groups() -> list[Group]:
    return [
        _design_a(),
        _zero_divisor_fringe(),
        *(_associator_spectrum(dim, i, j) for dim, i, j in SPECTRUM_EXEMPLARS),
    ]
