"""Portable scalar arithmetic for retained native operators and optical meshes.

Rx/Ry/Rz/CZ use their standard matrix definitions. Trigonometric constants
are rounded from a private fifty-decimal mpmath context; matrix rows then
update in a fixed scalar binary64 order, without BLAS dispatch. The reported
phase-aligned Frobenius residual is explicitly distinct from a spectral norm.
The exact mathematical Frobenius norm bounds the spectral norm; these values
remain numerical conformance diagnostics rather than interval certificates.
"""

from __future__ import annotations

import math
from typing import Any

import mpmath
import numpy as np
from numpy.typing import NDArray

DECIMAL_PRECISION = 50
ComplexMatrix = NDArray[np.complex128]


def _context() -> Any:
    context = mpmath.mp.clone()
    context.dps = DECIMAL_PRECISION
    return context


def _complex(value: Any) -> complex:
    return complex(float(value.real), float(value.imag))


def _magnitude(context: Any, value: complex) -> Any:
    return context.sqrt(context.mpf(value.real) ** 2 + context.mpf(value.imag) ** 2)


def _finite(matrix: ComplexMatrix) -> None:
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.isfinite(matrix).all():
        raise ValueError("operator arithmetic requires a finite square matrix")


def native_operator(circuit: Any, row_order: list[int]) -> ComplexMatrix:
    """Reconstruct a complete lowered circuit, including its recorded global phase and layout."""
    context = _context()
    size = 1 << circuit.num_qubits
    if sorted(row_order) != list(range(size)):
        raise ValueError("native operator row order must be a complete permutation")
    rows = [[complex(row == column) for column in range(size)] for row in range(size)]
    blocks = {}
    for instruction in circuit.data:
        operation = instruction.operation
        operands = [circuit.find_bit(qubit).index for qubit in instruction.qubits]
        if operation.name == "barrier":
            continue
        if operation.name == "cz":
            first, second = operands
            for row in range(size):
                if row & (1 << first) and row & (1 << second):
                    rows[row] = [-value for value in rows[row]]
            continue
        if operation.name not in {"rx", "ry", "rz"} or len(operands) != 1:
            raise ValueError(f"unsupported native operator gate {operation.name!r}")
        angle = float(operation.params[0])
        if not math.isfinite(angle):
            raise ValueError("native gate angles must be finite")
        key = (operation.name, angle)
        if key not in blocks:
            half = context.mpf(angle) / 2
            cosine, sine = float(context.cos(half)), float(context.sin(half))
            if operation.name == "rx":
                block = ((complex(cosine), -1j * sine), (-1j * sine, complex(cosine)))
            elif operation.name == "ry":
                block = ((complex(cosine), complex(-sine)), (complex(sine), complex(cosine)))
            else:
                block = ((_complex(context.exp(-1j * half)), 0j), (0j, _complex(context.exp(1j * half))))
            blocks[key] = block
        block = blocks[key]
        bit = 1 << operands[0]
        for row in range(size):
            if row & bit:
                continue
            paired = row | bit
            first_values, second_values = rows[row], rows[paired]
            rows[row] = [
                block[0][0] * first + block[0][1] * second
                for first, second in zip(first_values, second_values, strict=True)
            ]
            rows[paired] = [
                block[1][0] * first + block[1][1] * second
                for first, second in zip(first_values, second_values, strict=True)
            ]
    phase = float(circuit.global_phase)
    if not math.isfinite(phase):
        raise ValueError("native global phase must be finite")
    factor = _complex(context.exp(1j * context.mpf(phase)))
    return np.asarray([[factor * value for value in rows[row]] for row in row_order], dtype=np.complex128)


def probabilities(matrix: ComplexMatrix) -> list[float]:
    """Interpret the first column through fixed real-square-plus-imaginary-square arithmetic."""
    _finite(matrix)
    return [float(value.real) * float(value.real) + float(value.imag) * float(value.imag) for value in matrix[:, 0]]


def frobenius_residual(left: ComplexMatrix, right: ComplexMatrix) -> float:
    """Return the phase-aligned numerical Frobenius residual in a fixed accumulation order."""
    _finite(left)
    _finite(right)
    if left.shape != right.shape:
        raise ValueError("operator residual matrices must have the same shape")
    context = _context()
    products = [
        complex(first).conjugate() * complex(second) for first, second in zip(left.flat, right.flat, strict=True)
    ]
    overlap = complex(math.fsum(value.real for value in products), math.fsum(value.imag for value in products))
    magnitude = _magnitude(context, overlap)
    phase = _complex(context.mpc(overlap) / magnitude) if magnitude else 1 + 0j
    differences = [
        complex(second) - phase * complex(first) for first, second in zip(left.flat, right.flat, strict=True)
    ]
    squares = [context.mpf(value.real) ** 2 + context.mpf(value.imag) ** 2 for value in differences]
    return float(context.sqrt(context.fsum(squares)))


def photonic_template(matrix: ComplexMatrix) -> tuple[dict[str, Any], dict[str, float]]:
    """Factor the complete optical operator with fixed scalar Givens updates and phase conventions."""
    _finite(matrix)
    size = len(matrix)
    if not np.allclose(matrix.conj().T @ matrix, np.eye(size), atol=1e-12, rtol=0):
        raise ValueError("the photonic operator must be unitary")
    context = _context()
    remaining = [[complex(value) for value in row] for row in matrix]
    eliminations = []
    for column in range(size - 1):
        for bottom in range(size - 1, column, -1):
            top = bottom - 1
            first, second = remaining[top][column], remaining[bottom][column]
            radius = float(context.sqrt(_magnitude(context, first) ** 2 + _magnitude(context, second) ** 2))
            givens = (
                ((first.conjugate() / radius, second.conjugate() / radius), (-second / radius, first / radius))
                if radius > 1e-15
                else ((1 + 0j, 0j), (0j, 1 + 0j))
            )
            top_values, bottom_values = remaining[top], remaining[bottom]
            remaining[top] = [
                givens[0][0] * upper + givens[0][1] * lower
                for upper, lower in zip(top_values, bottom_values, strict=True)
            ]
            remaining[bottom] = [
                givens[1][0] * upper + givens[1][1] * lower
                for upper, lower in zip(top_values, bottom_values, strict=True)
            ]
            eliminations.append((top, givens))
    operations: list[list[Any]] = []
    parameters: dict[str, float] = {}

    def add(kind: str, mode: int, value: float) -> None:
        index = len(parameters)
        operations.append([kind, mode, index])
        parameters[f"x{index}"] = value

    for mode in range(size):
        add("PS", mode, float(context.arg(remaining[mode][mode])))
    for mode, givens in reversed(eliminations):
        diagonal, off_diagonal = givens[0][0].conjugate(), givens[1][0].conjugate()
        diagonal_phase = float(context.arg(diagonal))
        off_phase = float(context.arg(off_diagonal) - context.pi / 2)
        alpha, beta = (diagonal_phase + off_phase) / 2, (diagonal_phase - off_phase) / 2
        theta = float(2 * context.atan2(_magnitude(context, off_diagonal), _magnitude(context, diagonal)))
        add("PS", mode, beta)
        add("PS", mode + 1, -beta)
        add("BS", mode, theta)
        add("PS", mode, alpha)
        add("PS", mode + 1, -alpha)
    return {
        "schema": "qd-template-circuit-v1",
        "modes": size,
        "input_state": [1] + [0] * (size - 1),
        "parameters": len(parameters),
        "ops": operations,
    }, parameters
