"""The gate-noise forward model and fits on two-qubit circuits whose laws follow by hand."""

from __future__ import annotations

import math

import numpy as np
import pytest

import gate_noise_histogram_fit as gnf

PULSE = ("X90", None, (0,))
OTHER = ("X90", None, (1,))
STEP = 0.1


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _experiment(ops: tuple[gnf.Operation, ...]) -> gnf.Experiment:
    return gnf.Experiment(
        ops=ops,
        region=(0, 1),
        roles={"a": 0, "b": 1},
        keys=("a", "b"),
        arms={"exact": ("X90", None, 0), "turned": ("Rx", "all", 2)},
        scopes={"all": (0, 1)},
        step=STEP,
        selector="b",
        flip_bit="a",
        flip_state=1,
    )


def test_the_law_of_one_and_two_pulses_follows_the_outcome_bit_order() -> None:
    one = gnf.law(_experiment((PULSE,)), "exact", {})
    np.testing.assert_allclose(one, [0.5, 0.5, 0.0, 0.0], atol=1e-12)
    two = gnf.law(_experiment((OTHER, OTHER)), "exact", {})
    np.testing.assert_allclose(two, [0.0, 0.0, 1.0, 0.0], atol=1e-12)


def test_an_injected_step_turns_the_pulse_beyond_the_quarter_turn() -> None:
    law = gnf.law(_experiment((PULSE, PULSE)), "turned", {})
    inject = 2 * STEP
    np.testing.assert_allclose(law[1], math.cos(inject) ** 2, atol=1e-12)
    np.testing.assert_allclose(law[0], math.sin(inject) ** 2, atol=1e-12)


def test_the_selector_flip_moves_the_stated_fraction_of_the_flip_state() -> None:
    matrix = gnf.flip_matrix(_experiment((PULSE,)), 0.1)
    np.testing.assert_allclose(matrix[:, 1], [0.0, 0.9, 0.0, 0.1], atol=1e-15)
    np.testing.assert_allclose(matrix[:, 0], [1.0, 0.0, 0.0, 0.0], atol=1e-15)
    np.testing.assert_allclose(matrix.sum(axis=0), 1.0, atol=1e-15)


def test_arm_laws_equal_the_laws_of_each_arm_in_input_order() -> None:
    experiment = _experiment((PULSE, OTHER, PULSE))
    values = {"pa": 0.02, "pp": 0.01}
    arms = ["turned", "exact"]
    laws = gnf.arm_laws(experiment, arms, values)
    _expect(list(laws) == arms, f"arm_laws returned {list(laws)}")
    for arm in arms:
        np.testing.assert_array_equal(laws[arm], gnf.law(experiment, arm, values))
        np.testing.assert_allclose(laws[arm].sum(), 1.0, atol=1e-12)


def test_a_planted_pulse_damping_is_recovered_by_the_fit() -> None:
    experiment = _experiment((PULSE, PULSE))
    planted = {"pa": 0.05}
    shots = 1_000_000
    found = [
        {
            "batch": "planted",
            "kind": "planted",
            "arm": arm,
            "counts": shots * gnf.law(experiment, arm, planted),
            "matrix": np.eye(4),
        }
        for arm in ("exact", "turned")
    ]
    spec = gnf.FitSpec("planted", ("pa",), (0.01,), (0.0,), (0.3,), (0.03,))
    _, fitted = gnf.fit_item((experiment, spec, found))
    _expect(abs(fitted["values"]["pa"] - 0.05) < 1e-4, f"pa recovered as {fitted['values']['pa']}")
    _expect(fitted["histogram_chi2"] < 1.0, f"the planted fit leaves chi-square {fitted['histogram_chi2']}")


def test_a_channel_without_operators_is_refused() -> None:
    with pytest.raises(ValueError, match="at least one Kraus operator"):
        gnf.channel(np.zeros((2, 2, 2, 2), dtype=complex), [], 0, 2)
