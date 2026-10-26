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


def scrambled_unitary() -> np.ndarray:
    """A dense 12-mode unitary from the QR factor of a deterministic complex matrix."""
    index = np.arange(twelve.MODES)
    matrix = np.cos(1.3 * index[:, None] + 0.7 * index[None, :]) + 1j * np.sin(0.9 * np.outer(index, index) + 0.4)
    unitary: np.ndarray = np.linalg.qr(matrix)[0]
    return unitary


def test_bunching_term_matches_perceval_noise_model_clicks() -> None:
    import perceval as pcvl
    from perceval.utils import Matrix, NoiseModel

    unitary = scrambled_unitary()
    for g2 in (0.02, 0.2):
        gamma = twelve.bunching_weight(g2)
        model = twelve.light(twelve.Family(bunching=gamma), unitary[None], np.array([0]), np.zeros(0))[0]
        processor = pcvl.Processor("SLOS", pcvl.Unitary(Matrix(unitary)), noise=NoiseModel(g2=g2))
        processor.with_input(pcvl.BasicState([1] + [0] * (twelve.MODES - 1)))
        clicks = np.zeros(twelve.MODES)
        for state, probability in processor.probs()["results"].items():
            occupied = [mode for mode, count in enumerate(state) if count > 0]
            if len(occupied) == 1:
                clicks[occupied[0]] += float(probability)
        deviation = float(np.abs(model - clicks / clicks.sum()).max())
        if deviation > 1e-9:
            raise AssertionError(f"g2 {g2}: the bunching term departs from Perceval's clicks by {deviation:.2e}")


def test_efficiencies_scale_outputs_relative_to_mode_zero_and_stage_families_keep_their_light() -> None:
    unitary = scrambled_unitary()[None]
    sources = np.array([0])
    bare = twelve.light("nominal", unitary, sources, np.zeros(0))[0]
    if not np.array_equal(bare, twelve.light(twelve.Family(), unitary, sources, np.zeros(0))[0]):
        raise AssertionError("a Family without stages changes the nominal light")
    logs = np.linspace(-0.3, 0.3, twelve.MODES - 1)
    scaled = twelve.light(twelve.Family(efficiency=True), unitary, sources, logs)[0]
    expected = bare * np.exp(np.concatenate(([0.0], logs)))
    if float(np.abs(scaled - expected / expected.sum()).max()) > 1e-15:
        raise AssertionError("efficiencies do not scale each output relative to mode 0")
    if twelve.parameter_count(twelve.Family(efficiency=True, bunching="free")) != twelve.MODES:
        raise AssertionError("eleven log-efficiencies and one bunching root make twelve parameters")
