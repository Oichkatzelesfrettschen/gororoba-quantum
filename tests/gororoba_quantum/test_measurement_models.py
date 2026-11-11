"""Measurement identities with deterministic finite-dimensional counterexamples."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from measurement_models import (
    Instrument,
    density_matrix,
    dephasing_channel,
    entropy_bits,
    mutual_information_bits,
    partial_trace,
    trace_distance,
    z_measurement,
)

PLUS = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)


def _close(actual: Any, expected: Any) -> None:
    if not np.allclose(actual, expected, atol=1e-12, rtol=0):
        raise AssertionError(f"{actual} differs from {expected}")


def test_instrument_and_dilation_have_identical_system_laws() -> None:
    measurement = z_measurement()
    coherent = measurement.coherent_record_state(PLUS)
    classical = measurement.classical_record_state(PLUS)
    _close(partial_trace(coherent, (2, 2), (1,)), np.eye(2) / 2)
    _close(partial_trace(classical, (2, 2), (1,)), np.eye(2) / 2)
    _close(measurement.nonselective_state(PLUS), np.eye(2) / 2)
    _close(trace_distance(coherent, classical), 0.5)
    _close(entropy_bits(coherent), 0)
    _close(entropy_bits(classical), 1)
    v = measurement.quantum_isometry()
    _close(v.conj().T @ v, np.eye(2))


def test_coherent_record_can_be_uncomputed_but_a_classical_record_cannot() -> None:
    # Environment is first, system second; flip environment conditioned on system.
    undo = np.eye(4)[[0, 3, 2, 1]]
    measurement = z_measurement()
    coherent = undo @ measurement.coherent_record_state(PLUS) @ undo.T
    classical = undo @ measurement.classical_record_state(PLUS) @ undo.T
    recovered = partial_trace(coherent, (2, 2), (1,))
    unrecovered = partial_trace(classical, (2, 2), (1,))
    _close(np.trace(PLUS @ recovered), 1)
    _close(np.trace(PLUS @ unrecovered), 0.5)


@pytest.mark.parametrize("strength", [0.0, 0.25, 0.5, 1.0])
def test_dephasing_echo_and_dilation_equivalence(strength: float) -> None:
    channel = dephasing_channel(strength)
    output = channel.nonselective_state(PLUS)
    _close(np.trace(PLUS @ output), 1 - strength / 2)
    _close(partial_trace(channel.coherent_record_state(PLUS), (3, 2), (1,)), output)
    _close(channel.classical_record_state(PLUS), output)


def test_arbitrary_subsystem_not_maximum_index_cut() -> None:
    # |0> on factor 0 tensor a Bell pair on factors 1 and 2.
    psi = np.zeros(8)
    psi[[0, 3]] = 1 / np.sqrt(2)
    rho = np.outer(psi, psi)
    _close(entropy_bits(partial_trace(rho, (2, 2, 2), (0,))), 0)
    _close(entropy_bits(partial_trace(rho, (2, 2, 2), (1,))), 1)
    _close(entropy_bits(partial_trace(rho, (2, 2, 2), (0, 2))), 1)
    _close(entropy_bits(partial_trace(rho, (2, 2, 2), (1, 2))), 0)
    _close(mutual_information_bits(rho, (2, 2, 2), (1,), (2,)), 2)
    _close(partial_trace(rho, (2, 2, 2), ()), [[1]])


def test_keep_order_and_mixed_radix_factors() -> None:
    rho = np.zeros((6, 6))
    rho[5, 5] = 1  # |1> tensor |2>
    _close(partial_trace(rho, (2, 3), (0,)), [[0, 0], [0, 1]])
    _close(partial_trace(rho, (2, 3), (1,)), np.diag([0, 0, 1]))
    _close(partial_trace(rho, (2, 3), (1, 0)), rho)
    rho[5, 5], rho[1, 1] = 0, 1  # |0> tensor |1> becomes |1> tensor |0>
    reordered = np.zeros((6, 6))
    reordered[2, 2] = 1
    _close(partial_trace(rho, (2, 3), (1, 0)), reordered)


def test_redundant_ghz_records_are_not_independent_worlds() -> None:
    psi = np.zeros(8)
    psi[[0, 7]] = 1 / np.sqrt(2)
    rho = np.outer(psi, psi)
    _close(mutual_information_bits(rho, (2, 2, 2), (0,), (1,)), 1)
    _close(mutual_information_bits(rho, (2, 2, 2), (0,), (1, 2)), 2)


def test_impossible_outcome_stays_subnormalized_zero() -> None:
    branches = z_measurement().outcome_states(np.diag([1, 0]))
    _close(branches[1], np.zeros((2, 2)))
    _close(np.trace(branches.sum(axis=0)), 1)


def test_rectangular_isometry_and_multiple_kraus_per_outcome() -> None:
    embedding = np.array([[[1, 0], [0, 1], [0, 0]]], dtype=np.complex128)
    instrument = Instrument(embedding, (0,))
    _close(instrument.nonselective_state(PLUS), np.pad(PLUS, ((0, 1), (0, 1))))
    embedding[:] = 0  # ownership: caller mutations do not change the instrument
    _close(np.trace(instrument.nonselective_state(PLUS)), 1)


@pytest.mark.parametrize("state", [np.diag([1.1, -0.1]), np.eye(2), [[1, 1], [0, 0]], [[np.nan]]])
def test_invalid_density_is_refused(state: object) -> None:
    with pytest.raises(ValueError):
        density_matrix(state)  # type: ignore[arg-type]


@pytest.mark.parametrize("keep", [(1, 1), (2,), (-1,), (True,)])
def test_invalid_subsystem_is_refused(keep: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        partial_trace(np.eye(4) / 4, (2, 2), keep)


def test_instrument_requires_completeness_and_valid_labels() -> None:
    with pytest.raises(ValueError, match="trace preserving"):
        Instrument(np.eye(2)[None] * 2, (0,))
    with pytest.raises(ValueError, match="consecutive"):
        Instrument(np.eye(2)[None], (1,))
    with pytest.raises(ValueError):
        dephasing_channel(float("nan"))
    with pytest.raises(ValueError):
        mutual_information_bits(np.eye(4) / 4, (2, 2), (0,), (0,))


def test_huge_outcome_label_is_refused_before_allocating() -> None:
    with pytest.raises(ValueError, match="consecutive"):
        Instrument(np.eye(2)[None, :, :], (10**100,))
