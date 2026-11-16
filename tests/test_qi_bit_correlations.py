"""Contract for gororoba_quantum/qi_bit_correlations.py on shot records with known correlations."""

from __future__ import annotations

import math

import numpy as np

import qi_bit_correlations as correlations


def test_bit_array_puts_qubit_zero_at_the_rightmost_character() -> None:
    bits = correlations.bit_array(["100", "001"])
    if bits.tolist() != [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]]:
        raise AssertionError(bits.tolist())


def test_bit_array_rejects_ragged_or_non_binary_shots() -> None:
    for shots in ([], ["01", "1"], ["0a"]):
        try:
            correlations.bit_array(shots)
        except ValueError:
            continue
        raise AssertionError(f"{shots} was accepted")


def records() -> list[str]:
    """Qubits 0 and 1 always agree (one shot in four reads 11); qubit 2 follows a period that is independent of them."""
    shots = []
    for index in range(64):
        pair = "1" if index % 4 == 0 else "0"
        third = "1" if (index // 4) % 2 == 0 else "0"
        shots.append(third + pair + pair)
    return shots


def test_connected_correlation_of_an_agreeing_pair_is_its_variance() -> None:
    bits = correlations.bit_array(records())
    correlation, error = correlations.connected_correlations(bits)
    if abs(correlation[0, 1] - 0.25 * 0.75) > 1e-12 or abs(correlation[0, 2]) > 1e-12 or not error[0, 1] > 0:
        raise AssertionError((correlation[0, 1], correlation[0, 2], error[0, 1]))
    # Var(2 pair + third) = 4 * 3/16 + 1/4 = 1 over the sum of variances 2 * 3/16 + 1/4 = 5/8.
    if abs(correlations.overdispersion(bits) - 1.6) > 1e-12:
        raise AssertionError(correlations.overdispersion(bits))


def test_overdispersion_is_one_for_independent_bits_and_above_one_for_agreement() -> None:
    independent = np.array([[a, b] for a in (0.0, 1.0) for b in (0.0, 1.0)] * 8)
    agreeing = np.array([[a, a] for a in (0.0, 1.0)] * 16)
    if (
        abs(correlations.overdispersion(independent) - 1.0) > 1e-12
        or abs(correlations.overdispersion(agreeing) - 2.0) > 1e-12
    ):
        raise AssertionError((correlations.overdispersion(independent), correlations.overdispersion(agreeing)))


def test_coupled_contrast_finds_correlation_on_the_coupled_pairs_only() -> None:
    counted = np.array([[(i >> k) & 1 for k in range(4)] for i in range(16)] * 4, dtype=float)
    # Qubits 0 and 1 agree, so the coupled pair (0, 1) correlates; every other pair is independent.
    counted[:, 1] = counted[:, 0]
    correlation, error = correlations.connected_correlations(counted)
    contrast = correlations.coupled_contrast(correlation, error, [(0, 1), (2, 3)])
    if contrast["coupled_pairs"] != 2 or contrast["uncoupled_pairs"] != 4:
        raise AssertionError(contrast)
    if not math.isclose(contrast["coupled_mean"], 0.125, abs_tol=1e-12) or abs(contrast["uncoupled_mean"]) > 1e-12:
        raise AssertionError(contrast)
