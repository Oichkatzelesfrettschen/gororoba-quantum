"""Contracts of the Ascella response-geometry reading: gain relations, weighted fits and the background split."""

from __future__ import annotations

import ascella_response_geometry as geometry
import numpy as np


def endpoint(name: str, value: float, radius: float) -> dict[str, object]:
    return {"name": name, "value": value, "interval": [value - radius, value + radius]}


def gain_endpoints(gain: complex, radius: float) -> list[dict[str, object]]:
    """Sign-odd coefficients of g C(theta), C(theta) = (1 - exp(-2i theta))/2."""
    values = {
        "X_odd constant": gain.real / 2,
        "X_odd cos(2 theta)": -gain.real / 2,
        "X_odd sin(2 theta)": -gain.imag / 2,
        "Y_odd constant": gain.imag / 2,
        "Y_odd cos(2 theta)": -gain.imag / 2,
        "Y_odd sin(2 theta)": gain.real / 2,
    }
    return [endpoint(name, value, radius) for name, value in values.items()]


def test_uniform_gain_satisfies_every_relation() -> None:
    for relation in geometry.gain_relations(gain_endpoints(0.97 * np.exp(0.1j), 0.01)):
        if abs(relation["value"]) > 1e-12 or relation["excludes_zero"]:
            raise AssertionError(relation)


def test_offset_on_x_constant_breaks_only_its_relations() -> None:
    rows = gain_endpoints(0.97 + 0j, 0.005)
    for row in rows:
        if row["name"] == "X_odd constant":
            row["value"] = 0.485 - 0.03
            row["interval"] = [0.455 - 0.005, 0.455 + 0.005]
    excluded = {r["relation"] for r in geometry.gain_relations(rows) if r["excludes_zero"]}
    if excluded != {"X0 + Xc2", "X0 - Ys2"}:
        raise AssertionError(excluded)


def test_projected_interval_takes_the_far_bound_of_a_subtracted_term() -> None:
    rows = gain_endpoints(1 + 0j, 0.0)
    for row in rows:
        if row["name"] == "Y_odd sin(2 theta)":
            row["interval"] = [0.4, 0.7]
    relation = {r["relation"]: r for r in geometry.gain_relations(rows)}["X0 - Ys2"]
    if not np.allclose(relation["interval"], [0.5 - 0.7, 0.5 - 0.4]):
        raise AssertionError(relation)


def test_weighted_fit_of_an_exact_line_leaves_no_residual() -> None:
    x = np.linspace(-1, 1, 12)
    result = geometry.weighted_fit(np.column_stack([x, np.ones_like(x)]), 0.97 * x - 0.01, np.full(12, 1e-4))
    if not np.allclose(result["coefficients"], [0.97, -0.01]) or result["statistic"] > 1e-12 or result["dof"] != 10:
        raise AssertionError(result)


def test_background_fit_recovers_a_two_component_mixture() -> None:
    dark = np.array([1.0, 1, 1, 1, 30, 40, 50, 6, 1, 1, 1, 1])
    catalogue = dark[geometry.LOGICAL :] / dark[geometry.LOGICAL :].sum()
    flat = np.array([0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.05, 0.05])
    floor = np.full(64, 400.0)
    swing = np.where(np.arange(64) % 2 == 0, 20000.0, 2000.0)
    counts = np.zeros((64, 12))
    counts[:, geometry.LOGICAL :] = np.outer(floor, flat) + np.outer(swing, catalogue)
    result = geometry.background_components(counts, dark)
    if result["deviance"] > 1e-3:
        raise AssertionError(result["deviance"])
    low, high = result["admissible_dark_totals"]
    if not low - 1e-6 * swing.sum() <= swing.sum() <= high + 1e-6 * swing.sum():
        raise AssertionError((low, swing.sum(), high))
    if max(result["admissible_dark_lag1"]) > -0.9:
        raise AssertionError(result["admissible_dark_lag1"])


def test_background_fit_is_pinned_by_an_iteration_without_dark_component() -> None:
    dark = np.array([1.0, 1, 1, 1, 30, 40, 50, 6, 1, 1, 1, 1])
    catalogue = dark[geometry.LOGICAL :] / dark[geometry.LOGICAL :].sum()
    flat = np.array([0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.0, 0.1])
    swing = np.where(np.arange(64) % 2 == 0, 20000.0, 2000.0)
    swing[5] = 0.0
    counts = np.zeros((64, 12))
    counts[:, geometry.LOGICAL :] = np.outer(np.full(64, 400.0), flat) + np.outer(swing, catalogue)
    low, high = geometry.background_components(counts, dark)["admissible_dark_totals"]
    if not np.allclose([low, high], swing.sum(), rtol=1e-3):
        raise AssertionError((low, swing.sum(), high))
