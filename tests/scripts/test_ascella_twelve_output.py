"""Contracts of the Ascella twelve-output likelihood: the profiled background weight, the chip-stage families'
reduction to the bare mesh and the output stage's unitarity."""

from __future__ import annotations

import math
from typing import Any

import ascella_twelve_output as twelve
import numpy as np


def data() -> dict[str, Any]:
    """A rectangular 12-mode mesh of two-coupler cells with one heater after each coupler, three configurations."""
    arch: list[tuple[str, int, Any]] = []
    for column in range(6):
        for m in range(column % 2, twelve.MODES - 1, 2):
            for k in range(2):
                arch.append(("bs", m, (1.45 + 0.01 * math.sin(column + m + k), 0.0, 0.0, 0.0, 0.0)))
                arch.append(("ps", m + 1, 0.0))
    heaters = sum(1 for kind, _, _ in arch if kind == "ps")
    phases = np.array(
        [[(1.7 * c + 0.9 * h + math.sin(c * h)) % (2 * math.pi) for h in range(heaters)] for c in range(3)]
    )
    couplers = np.array([value[0] for kind, _, value in arch if kind == "bs"])
    return {"arch": arch, "couplers": couplers, "phases": phases, "sources": np.array([0, 3, 0])}


def test_profiled_weight_maximizes_the_iteration_likelihood() -> None:
    model = np.array([[0.9, 0.05, 0.0, 0.03] + [0.0025] * 8, [0.25] * 4 + [0.0] * 8])
    dark = np.array([1, 2, 3, 1, 5, 8, 2, 9, 30, 25, 10, 4], dtype=float)
    dark = dark / dark.sum()
    counts = np.array([[880, 52, 6, 35] + [9, 11, 3, 12, 40, 35, 14, 6], [100, 98, 97, 101] + [0] * 8], dtype=float)
    w = twelve.profile_background(counts, model, dark)
    grid = np.linspace(0, 1, 20001)
    for row in range(len(counts)):
        pi = (1 - grid)[:, None] * np.maximum(model[row], twelve.LIGHT_FLOOR) + grid[:, None] * dark[None, :]
        best = grid[np.argmax((counts[row] * np.log(pi)).sum(axis=1))]
        if abs(w[row] - best) > 1e-4:
            raise AssertionError((row, w[row], best))


def test_zero_stages_are_the_bare_mesh() -> None:
    d = data()
    unitary = twelve.unitaries(d)
    p, _ = twelve.models.pure_jacobians(d["couplers"], d["arch"], d["phases"], d["sources"])
    for family in twelve.FAMILIES:
        out = twelve.light(family, unitary, d["sources"], np.zeros(twelve.parameter_count(family)))
        if not np.allclose(out, p / p.sum(axis=1, keepdims=True), atol=1e-13):
            raise AssertionError(family)


def test_output_stage_is_unitary_and_couples_neighbors() -> None:
    beta = np.array([0.03 * (k + 1) * np.exp(1j * k) for k in range(twelve.MODES - 1)])
    stage = twelve.output_stage(beta)
    if not np.allclose(stage.conj().T @ stage, np.eye(twelve.MODES), atol=1e-13):
        raise AssertionError("the output stage is not unitary")
    small = twelve.output_stage(1e-6 * np.eye(1, twelve.MODES - 1, 4)[0].astype(complex))
    if abs(small[4, 5] - 1e-6j) > 1e-11 or abs(small[0, 5]) > 1e-11:
        raise AssertionError("the coupling does not act on its own neighbor pair")
