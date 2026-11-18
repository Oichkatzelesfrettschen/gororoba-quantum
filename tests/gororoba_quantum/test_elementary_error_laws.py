"""Hand-derived two-qubit circuits fix the conventions of the elementary-error laws."""

from __future__ import annotations

import math

import numpy as np
import pytest

from elementary_error_laws import channel_laws, damping_kraus, error_laws, rotation

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


def test_the_density_matrix_without_channels_equals_the_state_vector() -> None:
    operations = [X90, ("X90", None, (1,)), ("CZ", None, (0, 1)), ("Rz", 0.4, (1,)), ("X90", None, (1,))]
    values = np.array([-0.3, 0.0, 0.25])
    for item in [("pulse", "zb", 1), ("cz", (0, 1), None), ("czz", 0, (0, 1))]:
        pure = error_laws(operations, (0, 1), (1, 0), {0: 1.9}, [(item, values)])
        mixed = channel_laws(operations, (0, 1), (1, 0), {0: 1.9}, [(item, values)])
        np.testing.assert_allclose(mixed, pure, atol=1e-12)


def test_amplitude_damping_after_a_pulse_moves_its_excitation() -> None:
    law = channel_laws([X90], (0,), (0,), {}, [(("none", None, None), ZERO)], pulse_kraus=damping_kraus(0.2, 0.0))
    np.testing.assert_allclose(law[0], [0.6, 0.4], atol=1e-12)
    pure_dephasing = channel_laws(
        [X90, X90], (0,), (0,), {}, [(("none", None, None), ZERO)], pulse_kraus=damping_kraus(0.0, 1.0)
    )
    np.testing.assert_allclose(pure_dephasing[0], [0.5, 0.5], atol=1e-12)


def test_cz_damping_acts_on_both_qubits_of_the_gate() -> None:
    operations = [X90, ("X90", None, (1,)), ("CZ", None, (0, 1))]
    law = channel_laws(operations, (0, 1), (0, 1), {}, [(("none", None, None), ZERO)], cz_kraus=damping_kraus(1.0, 0))
    np.testing.assert_allclose(law[0], [1.0, 0.0, 0.0, 0.0], atol=1e-12)


def _closed_form(amplitude: float, phase: float) -> list[np.ndarray]:
    """P_j A_i for A = amplitude damping and P = phase damping, written out entry by entry; P_1 A_1 is zero."""
    root_a, root_p = math.sqrt(amplitude), math.sqrt(phase)
    keep = math.sqrt((1 - amplitude) * (1 - phase))
    return [
        np.array([[1, 0], [0, keep]], dtype=complex),
        np.array([[0, root_a], [0, 0]], dtype=complex),
        np.array([[0, 0], [0, math.sqrt(1 - amplitude) * root_p]], dtype=complex),
    ]


def _matches_law(ops: list[np.ndarray], amplitude: float, phase: float) -> bool:
    """Operators equal the closed form, sum K^dagger K is the identity, and the matrix units map as the law states."""
    want = _closed_form(amplitude, phase)
    if len(ops) != len(want) or any(not np.allclose(k, w, rtol=0, atol=1e-15) for k, w in zip(ops, want, strict=True)):
        return False
    if not np.allclose(sum(k.conj().T @ k for k in ops), np.eye(2), rtol=0, atol=1e-15):
        return False
    keep = math.sqrt((1 - amplitude) * (1 - phase))
    images = {
        (0, 0): np.array([[1, 0], [0, 0]], dtype=complex),
        (1, 1): np.array([[amplitude, 0], [0, 1 - amplitude]], dtype=complex),
        (0, 1): np.array([[0, keep], [0, 0]], dtype=complex),
        (1, 0): np.array([[0, 0], [keep, 0]], dtype=complex),
    }
    for (row, col), image in images.items():
        unit = np.zeros((2, 2), dtype=complex)
        unit[row, col] = 1
        if not np.allclose(sum(k @ unit @ k.conj().T for k in ops), image, rtol=0, atol=1e-15):
            return False
    return True


GRID = [(a, p) for a in (0.0, 0.05, 0.3, 0.9) for p in (0.0, 0.1, 0.5, 0.97)]


def test_damping_kraus_is_amplitude_then_phase_damping_in_closed_form() -> None:
    for amplitude, phase in GRID:
        ops = damping_kraus(amplitude, phase)
        want = _closed_form(amplitude, phase)
        kept = [w for w in want if np.any(w)]
        check(len(ops) == len(kept), f"operator count at {amplitude}, {phase}")
        for k, w in zip(ops, kept, strict=True):
            np.testing.assert_allclose(k, w, rtol=0, atol=1e-15)
        completeness = sum(k.conj().T @ k for k in ops)
        np.testing.assert_allclose(completeness, np.eye(2), rtol=0, atol=1e-15)
    check(_matches_law(damping_kraus(0.3, 0.5), 0.3, 0.5), "the shared law fails its own closed form")


def test_the_closed_form_check_rejects_a_swapped_order_and_a_wrong_off_diagonal() -> None:
    amplitude, phase = 0.3, 0.5
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    swapped = [a @ p for a in (a0, a1) for p in (p0, p1) if np.any(a @ p)]
    check(not _matches_law(swapped, amplitude, phase), "a swapped composition order passed")
    wrong = [k.copy() for k in damping_kraus(amplitude, phase)]
    wrong[0][1, 1] = (1 - amplitude) * (1 - phase)
    check(not _matches_law(wrong, amplitude, phase), "a wrong off-diagonal factor passed")
