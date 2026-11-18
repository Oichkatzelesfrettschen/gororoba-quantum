"""Outcome laws of a pulse-and-CZ circuit under elementary coherent errors, one row per parameter value.

The circuit is a list of operations on a register of qubits: ("CZ", None, (a, b)), ("Rz", angle, (q,)) and a
pulse (any other gate name, angle ignored, one qubit), which rotates about x by the qubit's entry in
`pulse_angles` (pi/2 where the qubit has none). Each elementary error is a (candidate, values) pair, and all
pairs act together, value i of every pair in row i:

- ("pulse", axis + order, qubit or None): a rotation by the value about `axis` ("x", "y", "z") before ("b") or
  after ("a") every pulse of the qubit, or of every qubit for None;
- ("cz", coupler or None, None): the value added to the conditional phase pi of every CZ of the coupler (a sorted
  qubit pair), or of every CZ for None;
- ("czz", qubit, coupler or None): Rz(value) on the qubit after each CZ it takes part in, on the coupler or on any;
- ("none", None, None): no error; its values fix the number of rows.

The state starts in |0...0>. The returned law indexes outcomes with `outcome_qubits[0]` as the most significant
bit. Rotations follow R_axis(t) = cos(t/2) 1 - i sin(t/2) sigma_axis, the cQASM convention, so the "czz" error and
an `Rz` instruction of the same angle act alike.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

Operation = tuple[str, float | None, Sequence[int]]
Item = tuple[tuple[str, Any, Any], np.ndarray]

PAULI: dict[str, np.ndarray] = {
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
    "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def rotation(axis: str, angle: float) -> np.ndarray:
    """R_axis(angle) as a 2 x 2 matrix."""
    return np.asarray(math.cos(angle / 2) * np.eye(2, dtype=complex) - 1j * math.sin(angle / 2) * PAULI[axis])


def rotations(axis: str, angles: np.ndarray) -> np.ndarray:
    """R_axis of every angle, shape (len(angles), 2, 2)."""
    return np.asarray(
        np.cos(angles / 2)[:, None, None] * np.eye(2) - 1j * np.sin(angles / 2)[:, None, None] * PAULI[axis]
    )


def error_laws(
    operations: Sequence[Operation],
    region: Sequence[int],
    outcome_qubits: Sequence[int],
    pulse_angles: Mapping[int, float],
    items: Sequence[Item],
) -> np.ndarray:
    """Laws over the outcome index, shape (values, 2 ** len(region))."""
    if not items:
        raise ValueError("at least one (candidate, values) pair fixes the number of rows")
    count = len(items[0][1])
    if any(len(values) != count for _, values in items):
        raise ValueError("every pair carries the same number of values")
    if sorted(outcome_qubits) != sorted(region):
        raise ValueError("outcome_qubits is a permutation of region")
    axis_of = {q: i for i, q in enumerate(region)}
    width = len(region)
    shape = (2,) * width
    trailing = (None,) * width
    psi = np.zeros((count, *shape), complex)
    psi.reshape(count, -1)[:, 0] = 1
    index = np.indices(shape)
    for gate, angle, qubits in operations:
        if gate == "CZ":
            both = index[axis_of[qubits[0]]] * index[axis_of[qubits[1]]]
            coupler = tuple(sorted(qubits))
            phase = np.zeros(count)
            for (kind, first, _second), values in items:
                if kind == "cz" and (first is None or coupler == first):
                    phase = phase + values
            psi = psi * np.where(both[None] == 1, -np.exp(1j * phase)[(slice(None), *trailing)], 1.0)
            for (kind, first, second), values in items:
                if kind == "czz" and first in qubits and (second is None or coupler == second):
                    psi = psi * np.exp(1j * values[(slice(None), *trailing)] * (index[axis_of[first]][None] - 0.5))
            continue
        qubit = qubits[0]
        if gate == "Rz":
            unitary = np.broadcast_to(rotation("z", float(angle or 0.0)), (count, 2, 2))
        else:
            unitary = np.broadcast_to(rotation("x", pulse_angles.get(qubit, math.pi / 2)), (count, 2, 2))
            for (kind, first, second), values in items:
                if kind == "pulse" and (second is None or qubit == second):
                    error = rotations(first[0], values)
                    unitary = unitary @ error if first[1] == "b" else error @ unitary
        moved = np.moveaxis(psi, axis_of[qubit] + 1, -1)
        low, high = moved[..., 0], moved[..., 1]
        u = unitary[(slice(None), slice(None), slice(None), *trailing[:-1])]
        psi = np.moveaxis(
            np.stack([u[:, 0, 0] * low + u[:, 0, 1] * high, u[:, 1, 0] * low + u[:, 1, 1] * high], -1),
            -1,
            axis_of[qubit] + 1,
        )
    probability = np.abs(psi) ** 2
    order = [0, *(axis_of[q] + 1 for q in outcome_qubits)]
    return np.asarray(probability.transpose(order).reshape(count, 2**width))


def damping_kraus(amplitude: float, phase: float) -> list[np.ndarray]:
    """Kraus operators of amplitude damping `amplitude` followed by phase damping `phase` on one qubit.

    The one definition of this channel: gate_noise_histogram_fit imports it for the pulse and CZ damping of its fits.
    """
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    return [p @ a for p in (p0, p1) for a in (a0, a1) if np.any(p @ a)]


def channel_laws(
    operations: Sequence[Operation],
    region: Sequence[int],
    outcome_qubits: Sequence[int],
    pulse_angles: Mapping[int, float],
    items: Sequence[Item],
    pulse_kraus: Sequence[np.ndarray] = (),
    cz_kraus: Sequence[np.ndarray] = (),
) -> np.ndarray:
    """error_laws on a density matrix, with a single-qubit channel after every pulse (`pulse_kraus`) and on each
    qubit of every CZ after it (`cz_kraus`); an empty Kraus list is no channel. Shape (values, 2 ** len(region)).
    The unitaries and error items follow error_laws' rules, so with no channel the two functions agree."""
    if not items:
        raise ValueError("at least one (candidate, values) pair fixes the number of rows")
    count = len(items[0][1])
    if any(len(values) != count for _, values in items):
        raise ValueError("every pair carries the same number of values")
    if sorted(outcome_qubits) != sorted(region):
        raise ValueError("outcome_qubits is a permutation of region")
    axis_of = {q: i for i, q in enumerate(region)}
    n = len(region)
    rho = np.zeros((count, *(2,) * (2 * n)), complex)
    rho.reshape(count, -1)[:, 0] = 1
    index = np.indices((2,) * n)

    def apply_one(rho: np.ndarray, qubit: int, ops: np.ndarray) -> np.ndarray:
        """rho -> sum_k K rho K^dagger on one qubit; `ops` has shape (count or 1, k, 2, 2)."""
        a = axis_of[qubit]
        moved = np.moveaxis(rho, (1 + a, 1 + n + a), (-2, -1))
        k = ops if ops.shape[0] == count else np.broadcast_to(ops, (count, *ops.shape[1:]))
        out = np.einsum("bkij,b...jl,bkml->b...im", k, moved, k.conj())
        return np.moveaxis(out, (-2, -1), (1 + a, 1 + n + a))

    pulse_ops = np.asarray(pulse_kraus, complex)[None] if len(pulse_kraus) else None
    cz_ops = np.asarray(cz_kraus, complex)[None] if len(cz_kraus) else None
    for gate, angle, qubits in operations:
        if gate == "CZ":
            coupler = tuple(sorted(qubits))
            phase = np.zeros(count)
            for (kind, first, _second), values in items:
                if kind == "cz" and (first is None or coupler == first):
                    phase = phase + values
            diag = np.where(index[axis_of[qubits[0]]] * index[axis_of[qubits[1]]] == 1, 1.0, 0.0)
            ket = np.exp(1j * (np.pi + phase))[(slice(None), *(None,) * n)] * diag[None] + (1 - diag[None])
            for (kind, first, second), values in items:
                if kind == "czz" and first in qubits and (second is None or coupler == second):
                    ket = ket * np.exp(1j * values[(slice(None), *(None,) * n)] * (index[axis_of[first]][None] - 0.5))
            rho = rho * ket[(..., *(None,) * n)] * ket.conj()[(slice(None), *(None,) * n, ...)]
            if cz_ops is not None:
                for q in qubits:
                    rho = apply_one(rho, q, cz_ops)
            continue
        qubit = qubits[0]
        if gate == "Rz":
            unitary = np.broadcast_to(rotation("z", float(angle or 0.0)), (count, 2, 2))
        else:
            unitary = np.broadcast_to(rotation("x", pulse_angles.get(qubit, math.pi / 2)), (count, 2, 2))
            for (kind, first, second), values in items:
                if kind == "pulse" and (second is None or qubit == second):
                    error = rotations(first[0], values)
                    unitary = unitary @ error if first[1] == "b" else error @ unitary
        rho = apply_one(rho, qubit, np.asarray(unitary)[:, None])
        if gate != "Rz" and pulse_ops is not None:
            rho = apply_one(rho, qubit, pulse_ops)
    letters = "cdefghijkl"[:n]
    diagonal = np.real(np.einsum(f"z{letters}{letters}->z{letters}", rho))
    order = [0, *(axis_of[q] + 1 for q in outcome_qubits)]
    return np.asarray(diagonal.transpose(order).reshape(count, 2**n))
