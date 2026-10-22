"""Synthetic model regressions; inputs are analytic laws, counts and likelihoods, never run reports."""

from __future__ import annotations

import math

import n21_orbit_rca as orbit
import n21_q143_beat_model as beat
import n21_q143_segmented_sweep as segmented
import n21_spectator_ramsey as ramsey
import numpy as np
import pytest


def quadrature_counts(expectation: float, shots: int = 4000) -> np.ndarray:
    """Two equally populated control branches with the prescribed spectator expectation."""
    return shots * np.array([1 + expectation, 1 + expectation, 1 - expectation, 1 - expectation]) / 4


@pytest.mark.parametrize(("measured", "expected"), [(0.2, "pass"), (0.9, "fail")])
def test_spectator_coherence_contract_and_missing_control(measured: float, expected: str) -> None:
    counts = {
        "measured": {"x": quadrature_counts(measured), "y": quadrature_counts(0)},
        "reset_only": {"x": quadrature_counts(0.9), "y": quadrature_counts(0)},
    }
    found = orbit.spectator_contract(counts, 0.01)
    if found["status"] != expected or not math.isclose(found["statistic"], measured - 0.9, abs_tol=1e-14):
        raise AssertionError(found)
    if orbit.spectator_contract(None, 0.01)["status"] != "not_evaluable":
        raise AssertionError("a missing spectator control entered inference")
    guarded = orbit.spectator_contract(counts, 0.01, margin=1.0)
    if guarded["status"] != "fail":
        raise AssertionError("the herald uncertainty margin failed to guard a coherence claim")


@pytest.mark.parametrize("phase", [0.0, math.pi / 4, math.pi / 2])
@pytest.mark.parametrize("coherence", [0.0, 0.8])
def test_contrast_magnitude_removes_work_phase(phase: float, coherence: float) -> None:
    arms = {}
    for name, contrast in (
        ("feedback", coherence * math.sin(phase) / 4),
        ("no_feedback", -coherence * math.cos(phase) / 4),
    ):
        arms[name] = 4000 * np.array([0.25, 0.25 + contrast / 2, 0.25, 0.25 - contrast / 2])
    magnitude, variance = orbit.contrast_magnitude(arms)
    if not math.isclose(magnitude, coherence / 4, abs_tol=1e-14) or not math.isfinite(variance) or variance <= 0:
        raise AssertionError((magnitude, variance))
    if coherence == 0 and not math.isclose(variance, 1 / 4000, abs_tol=1e-14):
        raise AssertionError("the zero-coherence variance lost both independent arms")


def test_ramsey_quadratures_and_unidentified_decisions() -> None:
    times = np.arange(4, dtype=float)
    parameters = np.array([0.8, 10.0, 1.0, 0.25, 0.0, 0.1])
    expected = 0.1 + 0.8 * np.array([1, math.exp(-0.1), -math.exp(-0.2), -math.exp(-0.3)])
    found = ramsey.mean_expectation(parameters, times, np.array([0, 1, 0, 1]))
    np.testing.assert_allclose(found, expected, rtol=0, atol=1e-14)
    free = {
        "estimates": {"detuning_mhz": 0.1, "beta": 1.0, "t2_star_us": 10.0},
        "standard_errors": {"detuning_mhz": None, "beta": None, "t2_star_us": None},
        "alias_bound_mhz": 1.0,
    }
    decision = ramsey.decisions(free)
    if any(decision[name]["status"] != "not_evaluable" for name in ("detuning", "decay_shape")):
        raise AssertionError(decision)


def test_beat_kernel_and_uncoupled_tls_analytic_limits() -> None:
    times = np.array([0.0, 0.3, 1.0, 2.0])
    weight, frequency, splitting = 0.7, 0.17, 0.11
    static = weight * np.exp(2j * math.pi * frequency * times)
    static += (1 - weight) * np.exp(2j * math.pi * (frequency + splitting) * times)
    np.testing.assert_allclose(
        beat.telegraph_kernel(weight, frequency, splitting, 0, times), static, rtol=0, atol=1e-13
    )
    expected = np.exp(-times / 30 - 2j * math.pi * frequency * times)
    found = beat.tls_signal(frequency, 0.21, 0.0, 30.0, 40.0, 0.0, 0.3, times)
    np.testing.assert_allclose(found, expected, rtol=0, atol=1e-12)


def test_segment_design_geometry_and_shot_cost_scaling() -> None:
    points = segmented.design_points(6, 128)
    if len({point.name for point in points}) != len(points):
        raise AssertionError("the prospective geometry repeats a member")
    if any(len(point.bases) != 6 or len(point.gaps_dt) != 5 for point in points):
        raise AssertionError("the six-segment design lost a read or an inter-segment gap")
    if not any(point.pre_dt for point in points):
        raise AssertionError("the design lost its herald-backaction controls")
    low, high = segmented.design_cost(points, 128), segmented.design_cost(points, 256)
    if not math.isclose(high["execution_s"], 2 * low["execution_s"], rel_tol=1e-14):
        raise AssertionError((low, high))
    if not math.isclose(high["charge_estimate_s"] - high["execution_s"], segmented.CHARGE_OFFSET_S, abs_tol=1e-14):
        raise AssertionError("the charge estimate changed its declared fixed offset")


@pytest.mark.parametrize(("gap", "expected"), [(0.0, "unresolved"), (10.0, "resolved")])
def test_segment_alias_resolution_threshold(gap: float, expected: str) -> None:
    cells = {
        cell: (100.0 + gap + abs(cell), [0.8, 50.0, 0.0, 0.01, 0.02, 100.0, 0.7, 0.12, 0.2]) for cell in segmented.CELLS
    }
    cells[0] = (100.0, [0.8, 50.0, 0.0, 0.01, 0.02, 100.0, 0.7, 0.12, 0.2])
    cells[1] = (100.0 + gap, [0.8, 50.0, 0.0, 0.01, 0.02, 100.0, 0.7, 0.12, 0.2])
    decision = segmented.alias_resolution(cells, 0.01)
    if decision["status"] != expected or decision["cell"] != 0:
        raise AssertionError(decision)


@pytest.mark.parametrize(("tls_nll", "expected"), [(80.0, "tls"), (100.0, "undecided"), (120.0, "line_mixture")])
def test_segment_model_choice_and_missing_degrees_of_freedom(tls_nll: float, expected: str) -> None:
    fits: dict[str, tuple[float, list[float]]] = {
        model: (nll, [])
        for model, nll in (("single", 130.0), ("static", 100.0), ("telegraph", 105.0), ("tls", tls_nll))
    }
    if segmented.model_decision(fits, 0.01)["status"] != expected:
        raise AssertionError("the model decision lost its likelihood threshold or direction")
    if segmented.verdict("null", "alternative", 1000.0, 0, 0.01)["status"] != "not_evaluable":
        raise AssertionError("an unobserved comparison entered a chi-square decision")
