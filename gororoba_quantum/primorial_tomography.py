"""Primorial cover phase-gradient tomography: cost tables, the eight-CNOT parity network, the arms and the fit.

docs/design/primorial-cover-defect-probes.md defines the protocol. For each cube edge (j, x) with x_j = 0 an arm
prepares (|x> + |x ^ 2^j>)/sqrt2, applies exp(-i gamma H) through the parity network on the path 0-1-2 and
reads qubit j in X and Y; the twelve edge phases determine the seven nonconstant Walsh coefficients c_S by least
squares on the cube's incidence matrix. Assignment inversion, null subtraction against the zero-angle arm and
the shot budget of the identification radius 1/16 complete the analysis. scripts/primorial_cover_noise.py,
the live_run campaigns of primorial_campaigns and the probe-case design all read these definitions.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Mapping
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

import primorial_cover as pc

GRADIENT_GAMMA = math.pi / 9


# A coefficient is identified when its estimate lies within half the 1/8 grid.
IDENTIFY_RADIUS = 1.0 / 16.0


# Two-sided z for all seven coefficients of one cost at family-wise level 0.01 (Bonferroni).
SIMULTANEOUS_Z = statistics.NormalDist().inv_cdf(1.0 - 0.01 / (2 * 7))


def cost_table(name: str) -> list[int]:
    if name == "null":
        return [0] * 8
    case, _, repaired = name.partition("_")
    return pc.slice_table(case, repaired=bool(repaired))


def coefficients(table: list[int]) -> dict[str, float]:
    return {key: float(value) for key, value in pc.walsh(table).items() if key}


def parity_network(circuit: QuantumCircuit, angle: Mapping[int, Any]) -> None:
    """The eight-CNOT network on the path 0-1-2 with RZ(angle[mask]) on the wire carrying parity ``mask``.

    ``angle`` maps each nonzero three-bit parity mask to a float or a Parameter, so a parametrized network
    binds to any cost table's angles.
    """
    wires = [1, 2, 4]
    done: set[int] = set()
    for j in range(3):
        circuit.rz(angle[wires[j]], j)
        done.add(wires[j])
    for _ in range(4):
        for control, target in ((0, 1), (1, 2)):
            circuit.cx(control, target)
            wires[target] ^= wires[control]
            if wires[target] not in done:
                circuit.rz(angle[wires[target]], target)
                done.add(wires[target])


def cost_block(circuit: QuantumCircuit, table: list[int], gamma: float) -> None:
    """exp(-i gamma H) up to a global phase, through the eight-CNOT network on the path 0-1-2."""
    c = coefficients(table)
    parity_network(
        circuit, {mask: 2.0 * gamma * c["".join(str(j) for j in range(3) if mask >> j & 1)] for mask in range(1, 8)}
    )


def gradient_arm(table: list[int], j: int, x: int, basis: str) -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)
    for i in range(3):
        if i != j and x >> i & 1:
            circuit.x(i)
    circuit.h(j)
    circuit.barrier()
    cost_block(circuit, table, GRADIENT_GAMMA)
    circuit.barrier()
    if basis == "Y":
        circuit.sdg(j)
    circuit.h(j)
    circuit.measure(range(3), range(3))
    return circuit


def gradient_ideal(table: list[int], j: int, x: int, basis: str) -> float:
    d = table[x ^ (1 << j)] - table[x]
    return math.cos(GRADIENT_GAMMA * d) if basis == "X" else -math.sin(GRADIENT_GAMMA * d)


def edges() -> list[tuple[int, int]]:
    return [(j, x) for j in range(3) for x in range(8) if not x >> j & 1]


def basis_arm(width: int, label: int) -> QuantumCircuit:
    circuit = QuantumCircuit(width, width)
    for q in range(width):
        if label >> q & 1:
            circuit.x(q)
    circuit.measure(range(width), range(width))
    return circuit


def _marginal(law: list[float], bit: int) -> float:
    """<Z> of classical bit ``bit`` under law."""
    return float(sum(p * (1 - 2 * (k >> bit & 1)) for k, p in enumerate(law)))


def incidence() -> np.ndarray:
    """Oriented edge-vertex incidence B: (B E)_e = E(x ^ 2^j) - E(x)."""
    rows = []
    for j, x in edges():
        row = np.zeros(8)
        row[x ^ (1 << j)] += 1.0
        row[x] -= 1.0
        rows.append(row)
    return np.asarray(rows)


def walsh_matrix() -> tuple[list[str], np.ndarray]:
    keys = [k for k in pc.walsh([0] * 8) if k]
    matrix = np.asarray([[(-1) ** sum(x >> int(j) & 1 for j in key) / 8.0 for x in range(8)] for key in keys])
    return keys, matrix


def assignment(rows: list[dict[str, Any]]) -> list[tuple[float, float]]:
    """Per-qubit (p(1|0), p(0|1)) from the three-qubit basis-preparation arms, averaged over the other qubits."""
    reads = [r for r in rows if r["family"] == "readout3"]
    out = []
    for q in range(3):
        flip: dict[int, list[float]] = {0: [], 1: []}
        for r in reads:
            prepared = r["label"] >> q & 1
            flip[prepared].append(sum(p for k, p in enumerate(r["law"]) if (k >> q & 1) != prepared))
        out.append((float(np.mean(flip[0])), float(np.mean(flip[1]))))
    return out


def corrected(z_obs: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """<Z> before an assignment channel with p(1|0) = a, p(0|1) = b: <Z>_obs = (1 - a - b) <Z> + b - a."""
    out: np.ndarray = (z_obs - (b - a)) / (1.0 - a - b)
    return out


def phase_variance(x_mean: np.ndarray, y_mean: np.ndarray, x_var: np.ndarray, y_var: np.ndarray) -> np.ndarray:
    """Delta-method per-shot variance of atan2(y, x) from independent X and Y arms of N shots each."""
    out: np.ndarray = (y_mean**2 * x_var + x_mean**2 * y_var) / np.hypot(x_mean, y_mean) ** 4
    return out


def raw_phase_variance(x_read: np.ndarray, y_read: np.ndarray) -> np.ndarray:
    return phase_variance(x_read, y_read, 1.0 - x_read**2, 1.0 - y_read**2)


def corrected_phase_variance(x_obs: np.ndarray, y_obs: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Phase variance after assignment inversion: each corrected mean has variance (1 - z_obs^2) / (1 - a - b)^2."""
    scale = (1.0 - a - b) ** 2
    return phase_variance(
        corrected(x_obs, a, b), corrected(y_obs, a, b), (1.0 - x_obs**2) / scale, (1.0 - y_obs**2) / scale
    )


def phase_fit(table: list[int], x_read: np.ndarray, y_read: np.ndarray, phase_var: np.ndarray) -> dict[str, Any]:
    """Least-squares cube potential from edge readings, recovered c_S, cycle residual and shot price.

    ``phase_var`` is each edge phase's per-shot variance, X and Y arms each taking N shots; the analysis that
    produced the readings (assignment inversion, null subtraction) determines it.
    """
    exact = coefficients(table)
    visibility = np.hypot(x_read, y_read)
    d_hat = -np.arctan2(y_read, x_read) / GRADIENT_GAMMA
    b = incidence()
    potential, *_ = np.linalg.lstsq(b, d_hat, rcond=None)
    residual = d_hat - b @ potential
    keys, w = walsh_matrix()
    projector = w @ np.linalg.pinv(b)
    recovered = dict(zip(keys, (projector @ d_hat).tolist(), strict=True))
    bias = max(abs(recovered[k] - exact[k]) for k in keys)
    coeff_var = (projector**2) @ (phase_var / GRADIENT_GAMMA**2)
    margin = IDENTIFY_RADIUS - bias
    return {
        "visibility": visibility.tolist(),
        "d_estimate": d_hat.tolist(),
        "cycle_residual_rms": float(math.sqrt(float(np.mean(residual**2)))),
        "recovered_coefficients": recovered,
        "max_coefficient_bias": bias,
        "per_shot_coefficient_variance": dict(zip(keys, coeff_var.tolist(), strict=True)),
        "shots_identify_all": math.ceil(SIMULTANEOUS_Z**2 * float(coeff_var.max()) / margin**2) if margin > 0 else None,
    }


def gradient_readings(rows: list[dict[str, Any]], name: str) -> tuple[np.ndarray, np.ndarray]:
    got = {
        (r["j"], r["x"], r["basis"]): _marginal(r["law"], r["j"])
        for r in rows
        if r["family"] == "gradient" and r["cost"] == name
    }
    return (
        np.asarray([got[(j, x, "X")] for j, x in edges()]),
        np.asarray([got[(j, x, "Y")] for j, x in edges()]),
    )


def null_subtracted(
    table: list[int],
    x_read: np.ndarray,
    y_read: np.ndarray,
    null: tuple[np.ndarray, np.ndarray],
    phase_var: np.ndarray,
    null_phase_var: np.ndarray,
) -> dict[str, Any]:
    """Phase fit after rotating each edge reading by minus the null arm's phase on the same edge.

    The null arm takes N shots per setting of its own, so the subtracted phase's variance is the sum of both.
    """
    rotation = np.exp(-1j * np.arctan2(null[1], null[0]))
    turned = (x_read + 1j * y_read) * rotation
    return phase_fit(table, turned.real, turned.imag, phase_var + null_phase_var)


def gradient_analysis(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    """Raw, assignment-corrected and null-subtracted phase fits.

    The corrected bias is the incoherent model's floor; the null-subtracted fit removes every diagonal error the
    zero-angle block shares with the cost block.
    """
    table = cost_table(name)
    x_read, y_read = gradient_readings(rows, name)
    flips = assignment(rows)
    a = np.asarray([flips[j][0] for j, _ in edges()])
    b = np.asarray([flips[j][1] for j, _ in edges()])
    null_x, null_y = gradient_readings(rows, "null")
    corrected_var = corrected_phase_variance(x_read, y_read, a, b)
    return {
        "exact_coefficients": coefficients(table),
        "d_true": (incidence() @ np.asarray(table, dtype=float)).tolist(),
        "raw": phase_fit(table, x_read, y_read, raw_phase_variance(x_read, y_read)),
        "assignment_corrected": phase_fit(table, corrected(x_read, a, b), corrected(y_read, a, b), corrected_var),
        "null_subtracted": null_subtracted(
            table,
            corrected(x_read, a, b),
            corrected(y_read, a, b),
            (corrected(null_x, a, b), corrected(null_y, a, b)),
            corrected_var,
            corrected_phase_variance(null_x, null_y, a, b),
        ),
    }
