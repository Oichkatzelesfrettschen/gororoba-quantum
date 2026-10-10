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

Summary = Callable[[dict[str, np.ndarray]], dict[str, float]]


@dataclass(frozen=True)
class Member:
    """One circuit of a group. mirror asks the compiler for a calibration twin.

    The twin is cut from the member's compiled ISA circuit, so it runs on the
    same physical qubits with the same two-qubit content (live_run.mirror_isa);
    summaries find its distribution under the member's name plus MIRROR_SUFFIX.
    """

    name: str
    circuit: QuantumCircuit
    ideal: np.ndarray
    mirror: bool = False


MIRROR_SUFFIX = "_mirror"


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


def z_expectation(dist: np.ndarray) -> float:
    """<Z> of a one-bit distribution: P(0) - P(1)."""
    return float(dist[0] - dist[1])


def odr_p1(dist: np.ndarray, mirror: np.ndarray) -> float:
    """P(1) after dividing <Z> by the mirror circuit's attenuation.

    The value is left unclipped: a result outside [0, 1] means the mirror
    attenuates less than the witness does, which is itself the diagnostic.
    """
    att = z_expectation(mirror)
    corrected = z_expectation(dist) / att if att > 0 else math.nan
    return float((1.0 - corrected) / 2.0)


def _uniform(clbits: int) -> np.ndarray:
    return np.full(2**clbits, 1.0 / 2**clbits)


def _design_a() -> Group:
    qc = design_a_associator(1, 2)[0]

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        got = dist["design_a_1_2"]
        return {
            "p1": float(got[1]),
            "p1_odr": odr_p1(got, dist["design_a_1_2" + MIRROR_SUFFIX]),
            "mirror_z": z_expectation(dist["design_a_1_2" + MIRROR_SUFFIX]),
            "tvd_to_uniform": tvd(got, _uniform(1)),
        }

    return Group("design_a", (Member("design_a_1_2", qc, _two_outcome(1.0), mirror=True),), summarize)


def _zero_divisor_fringe() -> Group:
    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    tag = f"{i}_{j}_{k}_{el}"
    dark_p0 = predict.zero_divisor_p0((i, j), (k, el), s)
    bright_p0 = predict.zero_divisor_p0((i, j), (k, el), -s)
    dark_qc = design_b_zero_divisor((i, j), (k, el), s)
    bright_qc = design_b_zero_divisor((i, j), (k, el), -s)
    dark_name, bright_name = f"design_b_dark_{tag}", f"design_b_bright_{tag}"
    members = [
        # Each witness gets its own mirror; the sweep points share the dark one,
        # since they differ from it only by the preparation phase gate.
        Member(dark_name, dark_qc, _two_outcome(1 - dark_p0), mirror=True),
        Member(bright_name, bright_qc, _two_outcome(1 - bright_p0), mirror=True),
    ]
    sweep_names = []
    for n, phase in enumerate(SWEEP_PHASES):
        want = predict.phase_sweep_p0((i, j), (k, el), phase)
        name = f"design_d_{tag}_phase_{n}of8"
        sweep_names.append(name)
        members.append(Member(name, design_d_phase_sweep((i, j), (k, el), phase), _two_outcome(1 - want)))

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        dark, bright = float(dist[dark_name][0]), float(dist[bright_name][0])
        dark_odr = 1.0 - odr_p1(dist[dark_name], dist[dark_name + MIRROR_SUFFIX])
        bright_odr = 1.0 - odr_p1(dist[bright_name], dist[bright_name + MIRROR_SUFFIX])
        fit = fit_fringe(SWEEP_PHASES, [float(dist[name][0]) for name in sweep_names])
        odr_sweep = [1.0 - odr_p1(dist[name], dist[dark_name + MIRROR_SUFFIX]) for name in sweep_names]
        fit_odr = {f"{k}_odr": v for k, v in fit_fringe(SWEEP_PHASES, odr_sweep).items()}
        return (
            {
                "p0_dark": dark,
                "p0_bright": bright,
                "ratio": dark / bright if bright else math.nan,
                "p0_dark_odr": dark_odr,
                "p0_bright_odr": bright_odr,
                "ratio_odr": dark_odr / bright_odr if bright_odr else math.nan,
                "mirror_z_dark": z_expectation(dist[dark_name + MIRROR_SUFFIX]),
                "mirror_z_bright": z_expectation(dist[bright_name + MIRROR_SUFFIX]),
            }
            | fit
            | fit_odr
        )

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
            "tvd_to_uniform": tvd(got, _uniform(n)),
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
