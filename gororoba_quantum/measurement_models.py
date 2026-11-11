"""Finite quantum instruments and coherent apparatus dilations.

A Kraus index is a quantum environment coordinate. An outcome label is a
classical record. Equality after tracing an environment is not evidence for
an interpretation of quantum mechanics. These deterministic finite-matrix
routines test model identities; they neither submit circuits nor adjudicate
hardware or objective-collapse models.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

TOLERANCE = 1e-10


def density_matrix(state: np.ndarray, *, tolerance: float = TOLERANCE) -> np.ndarray:
    """Validate a normalized density matrix without silently repairing it."""
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be positive and finite")
    rho = np.asarray(state, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] == 0 or rho.shape[0] != rho.shape[1]:
        raise ValueError("state must be a nonempty square density matrix")
    if not np.isfinite(rho).all():
        raise ValueError("state contains nonfinite entries")
    if not np.allclose(rho, rho.conj().T, atol=tolerance, rtol=0):
        raise ValueError("state is not Hermitian")
    if abs(np.trace(rho) - 1) > tolerance:
        raise ValueError("state does not have unit trace")
    if np.linalg.eigvalsh(rho).min() < -tolerance:
        raise ValueError("state is not positive semidefinite")
    return rho


def partial_trace(state: np.ndarray, dimensions: Sequence[int], keep: Sequence[int]) -> np.ndarray:
    """Trace out complementary tensor factors, preserving the order of keep.

    Factor zero is the leftmost tensor factor (most significant mixed-radix
    coordinate). Empty keep returns a 1-by-1 trace. Repeated or invalid
    factor indices are errors, not aliases for contiguous cuts.
    """
    dims = tuple(dimensions)
    selected = tuple(keep)
    if not dims or any(type(d) is not int or d <= 0 for d in dims):
        raise ValueError("dimensions must be positive integers")
    if any(type(i) is not int or not 0 <= i < len(dims) for i in selected):
        raise ValueError("keep contains an invalid tensor factor")
    if len(set(selected)) != len(selected):
        raise ValueError("keep contains repeated tensor factors")
    rho = density_matrix(state)
    if rho.shape[0] != math.prod(dims):
        raise ValueError("tensor dimensions do not match state")
    discarded = tuple(i for i in range(len(dims)) if i not in selected)
    axes = selected + discarded
    order = axes + tuple(i + len(dims) for i in axes)
    kept_size = math.prod(dims[i] for i in selected)
    discarded_size = math.prod(dims[i] for i in discarded)
    tensor = rho.reshape(dims + dims).transpose(order)
    tensor = tensor.reshape(kept_size, discarded_size, kept_size, discarded_size)
    return np.trace(tensor, axis1=1, axis2=3)


def entropy_bits(state: np.ndarray) -> float:
    """Von Neumann entropy in bits of a normalized density matrix."""
    rho = density_matrix(state)
    # Only eigenvalues inside the validated roundoff tolerance are clipped.
    values = np.clip(np.linalg.eigvalsh(rho), 0.0, 1.0)
    positive = values[values > 0]
    return float(-np.sum(positive * np.log2(positive)))


def mutual_information_bits(
    state: np.ndarray, dimensions: Sequence[int], first: Sequence[int], second: Sequence[int]
) -> float:
    """I(A:B) for disjoint factors, with no claim about accessible classical information."""
    a, b = tuple(first), tuple(second)
    if set(a) & set(b):
        raise ValueError("mutual-information factors must be disjoint")
    return (
        entropy_bits(partial_trace(state, dimensions, a))
        + entropy_bits(partial_trace(state, dimensions, b))
        - entropy_bits(partial_trace(state, dimensions, a + b))
    )


def trace_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Half the trace norm of two density matrices' difference."""
    a, b = density_matrix(first), density_matrix(second)
    if a.shape != b.shape:
        raise ValueError("states have different dimensions")
    return float(np.abs(np.linalg.eigvalsh(a - b)).sum() / 2)


@dataclass(frozen=True)
class Instrument:
    """Trace-preserving instrument with an outcome label for each Kraus map.

    operators has shape (K, output_dimension, input_dimension). Labels are
    consecutive nonnegative integers, with repetition for unobserved Kraus
    alternatives within an outcome. Arrays are copied and made read-only.
    The coherent dilation retains K orthogonal environment coordinates;
    those coordinates are not classical outcome branches.
    """

    operators: np.ndarray
    labels: tuple[int, ...]

    def __post_init__(self) -> None:
        operators = np.array(self.operators, dtype=np.complex128, copy=True)
        labels = tuple(self.labels)
        if operators.ndim != 3 or min(operators.shape) < 1 or not np.isfinite(operators).all():
            raise ValueError("operators need finite nonempty (K, output, input) shape")
        if len(labels) != operators.shape[0] or any(type(i) is not int or i < 0 for i in labels):
            raise ValueError("every Kraus map needs a nonnegative integer outcome label")
        if max(labels) >= len(labels) or set(labels) != set(range(max(labels) + 1)):
            raise ValueError("outcome labels must be consecutive starting at zero")
        completeness = np.einsum("kai,kaj->ij", operators.conj(), operators)
        if not np.allclose(completeness, np.eye(operators.shape[2]), atol=TOLERANCE, rtol=0):
            raise ValueError("Kraus maps are not trace preserving")
        operators.setflags(write=False)
        object.__setattr__(self, "operators", operators)
        object.__setattr__(self, "labels", labels)

    def _input(self, state: np.ndarray) -> np.ndarray:
        rho = density_matrix(state)
        if rho.shape[0] != self.operators.shape[2]:
            raise ValueError("instrument input dimension does not match state")
        return rho

    def quantum_isometry(self) -> np.ndarray:
        """V = sum_k |k> tensor K_k; V*V=I, environment factor first."""
        count, output, source = self.operators.shape
        return self.operators.reshape(count * output, source).copy()

    def coherent_record_state(self, state: np.ndarray) -> np.ndarray:
        """Retain off-diagonal environment blocks in V rho V*."""
        rho = self._input(state)
        isometry = self.quantum_isometry()
        return isometry @ rho @ isometry.conj().T

    def outcome_states(self, state: np.ndarray) -> np.ndarray:
        """Subnormalized conditional states, one per classical outcome.

        Their traces are outcome probabilities. Zero-probability states stay
        zero rather than being normalized or assigned an invented state.
        """
        rho = self._input(state)
        terms = np.einsum("kai,ij,kbj->kab", self.operators, rho, self.operators.conj())
        output = self.operators.shape[1]
        branches = np.zeros((max(self.labels) + 1, output, output), dtype=np.complex128)
        np.add.at(branches, np.asarray(self.labels), terms)
        return branches

    def nonselective_state(self, state: np.ndarray) -> np.ndarray:
        """Discard the classical outcome while retaining its quantum disturbance."""
        return self.outcome_states(state).sum(axis=0)

    def classical_record_state(self, state: np.ndarray) -> np.ndarray:
        """Block-diagonal classical-outcome/quantum-system state."""
        branches = self.outcome_states(state)
        outcomes, output, _ = branches.shape
        blocks = np.zeros((outcomes, output, outcomes, output), dtype=np.complex128)
        index = np.arange(outcomes)
        blocks[index, :, index, :] = branches
        return blocks.reshape(outcomes * output, outcomes * output)


def z_measurement() -> Instrument:
    """Ideal nonselective Z measurement when its outcome is discarded."""
    operators = np.array([[[1, 0], [0, 0]], [[0, 0], [0, 1]]], dtype=np.complex128)
    return Instrument(operators, (0, 1))


def dephasing_channel(strength: float) -> Instrument:
    """(1-p) rho + p diag(rho), modeled as an instrument with one outcome.

    p is a channel parameter, not a measured fundamental-collapse rate.
    Ordinary uncontrolled environmental interactions realize this channel.
    """
    if not math.isfinite(strength) or not 0 <= strength <= 1:
        raise ValueError("dephasing strength must be in [0, 1]")
    operators = np.concatenate(
        (np.sqrt(1 - strength) * np.eye(2)[None, :, :], np.sqrt(strength) * z_measurement().operators)
    )
    return Instrument(operators, (0, 0, 0))
