"""Hand-derived two-qubit circuits fix the conventions of the elementary-error laws."""

from __future__ import annotations

import math

import numpy as np
import pytest

from elementary_error_laws import error_laws, rotation

X90 = ("X90", None, (0,))
ZERO = np.zeros(1)


def check(condition: bool, message: str = "check failed") -> None:
    if not condition:
        raise AssertionError(message)


def _law(operations: list, items: list, pulse_angles: dict[int, float] | None = None, region: tuple = (0, 1)):
    return error_laws(operations, region, region, pulse_angles or {}, items)[0]


def test_two_pulses_flip_the_qubit_and_one_pulse_splits_it() -> None:
    none = [(("none", None, None), ZERO)]
    np.testing.assert_allclose(_law([X90], none), [0.5, 0.0, 0.5, 0.0], atol=1e-12)
    np.testing.assert_allclose(_law([X90, X90], none), [0.0, 0.0, 1.0, 0.0], atol=1e-12)


def test_the_outcome_order_puts_the_first_listed_qubit_in_the_high_bit() -> None:
    flip_one = [("X90", None, (1,)), ("X90", None, (1,))]
    none = [(("none", None, None), ZERO)]
    np.testing.assert_allclose(error_laws(flip_one, (0, 1), (0, 1), {}, none)[0], [0, 1, 0, 0], atol=1e-12)
    np.testing.assert_allclose(error_laws(flip_one, (0, 1), (1, 0), {}, none)[0], [0, 0, 1, 0], atol=1e-12)


def test_an_injected_pulse_angle_and_a_pulse_x_error_add() -> None:
    delta = 0.3
    by_angle = _law([X90, X90], [(("none", None, None), ZERO)], {0: math.pi / 2 + delta})
    by_error = _law([X90, X90], [(("pulse", "xb", 0), np.array([delta]))])
    expected = math.sin((math.pi + 2 * delta) / 2) ** 2
    check(abs(by_angle[2] - (expected)) < 1e-12)
    np.testing.assert_allclose(by_angle, by_error, atol=1e-12)


def test_a_phase_between_two_pulses_reads_as_a_ramsey_fringe_with_either_order() -> None:
    phi = 0.7
    before = _law([X90, X90], [(("pulse", "zb", 0), np.array([phi]))])
    after = _law([X90, X90], [(("pulse", "za", 0), np.array([phi]))])
    by_gate = _law([X90, ("Rz", phi, (0,)), X90], [(("none", None, None), ZERO)])
    expected = math.cos(phi / 2) ** 2
    for law in (before, after, by_gate):
        check(abs(law[2] - (expected)) < 1e-12)


def test_a_conditional_phase_error_shows_in_a_controlled_ramsey_and_only_on_its_coupler() -> None:
    delta = 0.4
    circuit = [("X90", None, (1,)), ("X90", None, (1,)), X90, ("CZ", None, (0, 1)), X90]
    exact = _law(circuit, [(("none", None, None), ZERO)])
    shifted = _law(circuit, [(("cz", (0, 1), None), np.array([delta]))])
    elsewhere = _law(circuit, [(("cz", (1, 2), None), np.array([delta]))])
    # Qubit 1 is |1>, so qubit 0 sees Rz(pi + delta) up to a global phase between its two pulses.
    check(abs(exact[1] - (1.0)) < 1e-12)
    check(abs(shifted[1] - (math.cos(delta / 2) ** 2)) < 1e-12)
    np.testing.assert_allclose(elsewhere, exact, atol=1e-12)


def test_the_czz_error_is_an_rz_after_the_cz() -> None:
    phi = 0.25
    flip = [("X90", None, (1,)), ("X90", None, (1,))]
    circuit = [*flip, X90, ("CZ", None, (0, 1)), X90]
    with_gate = [*flip, X90, ("CZ", None, (0, 1)), ("Rz", phi, (0,)), X90]
    by_error = _law(circuit, [(("czz", 0, (0, 1)), np.array([phi]))])
    by_gate = _law(with_gate, [(("none", None, None), ZERO)])
    np.testing.assert_allclose(by_error, by_gate, atol=1e-12)
    check(abs(by_error[1] - (math.cos(phi / 2) ** 2)) < 1e-12)


def test_rows_follow_the_values_and_two_errors_act_together() -> None:
    values = np.array([0.0, 0.2, -0.2])
    table = error_laws([X90, X90], (0,), (0,), {}, [(("pulse", "xb", 0), values), (("pulse", "xb", 0), values)])
    check(table.shape == (3, 2))
    np.testing.assert_allclose(table.sum(1), 1.0, atol=1e-12)
    check(abs(table[1, 1] - (math.sin((math.pi + 4 * 0.2) / 2) ** 2)) < 1e-12)
    np.testing.assert_allclose(table[1], table[2], atol=1e-12)


def test_malformed_inputs_are_refused() -> None:
    with pytest.raises(ValueError, match="at least one"):
        error_laws([X90], (0,), (0,), {}, [])
    with pytest.raises(ValueError, match="same number"):
        error_laws([X90], (0,), (0,), {}, [(("none", None, None), ZERO), (("cz", None, None), np.zeros(2))])
    with pytest.raises(ValueError, match="permutation"):
        error_laws([X90], (0, 1), (0, 0), {}, [(("none", None, None), ZERO)])


def test_rotation_follows_the_cqasm_convention() -> None:
    np.testing.assert_allclose(rotation("z", 0.6), np.diag([np.exp(-0.3j), np.exp(0.3j)]), atol=1e-12)
