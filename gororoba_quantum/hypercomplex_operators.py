"""Faithful quaternion operators and convention-certified octonion envelopes.

Complex channels encode quaternion coefficients in adjacent pairs. Only the
sum within each pair is a quaternion-ray position observable. Octonion left
operators compose associatively without making their encoding a homomorphism.
"""

from __future__ import annotations

import math
from itertools import combinations
from typing import Any

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from cd_core import cd_sign
from parallel import ordered_map

ComplexMatrix = NDArray[np.complex128]
RealMatrix = NDArray[np.float64]


def quaternion_matrix(coefficients: list[float]) -> ComplexMatrix:
    """Return chi(a+b*i+c*j+d*k), with q=z+w*j and chi(q)=[[z,w],[-w*,z*]]."""
    if len(coefficients) != 4 or not np.isfinite(coefficients).all():
        raise ValueError("a quaternion needs four finite real coefficients")
    real, imaginary_i, imaginary_j, imaginary_k = coefficients
    diagonal = complex(real, imaginary_i)
    off_diagonal = complex(imaginary_j, imaginary_k)
    return np.array([[diagonal, off_diagonal], [-off_diagonal.conjugate(), diagonal.conjugate()]])


def _size(sites: int) -> None:
    if type(sites) is not int or sites < 4 or sites & (sites - 1):
        raise ValueError("sites must be a power of two of at least four")


def _finite(*values: float) -> None:
    if not all(math.isfinite(value) for value in values):
        raise ValueError("parameters must be finite")


def grouped_probabilities(state: ComplexMatrix) -> RealMatrix:
    """Measure adjacent quaternion-ray channels of a normalized complex vector."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or not vector.size or vector.size % 2 or not np.isfinite(vector).all():
        raise ValueError("a state needs a finite vector of paired complex channels")
    if not np.isclose(np.vdot(vector, vector).real, 1, atol=1e-12, rtol=0):
        raise ValueError("the state must be normalized")
    return np.asarray((np.abs(vector) ** 2).reshape(-1, 2).sum(axis=1), dtype=np.float64)


def order_interferometer(theta: float, phi: float) -> ComplexMatrix:
    """Compare AB and BA in two paths; dark probability is sin(theta)^2 sin(phi)^2."""
    _finite(theta, phi)
    imaginary_i = quaternion_matrix([0, 1, 0, 0])
    imaginary_j = quaternion_matrix([0, 0, 1, 0])
    first = math.cos(theta) * np.eye(2) + math.sin(theta) * imaginary_i
    second = math.cos(phi) * np.eye(2) + math.sin(phi) * imaginary_j
    paths = np.zeros((4, 4), dtype=complex)
    paths[:2, :2], paths[2:, 2:] = first @ second, second @ first
    splitter = np.kron(np.array([[1, 1], [1, -1]]) / math.sqrt(2), np.eye(2))
    return np.asarray(splitter @ paths @ splitter, dtype=np.complex128)


def periodic_generator(sites: int, coupling: float) -> ComplexMatrix:
    """Discretize L_i*d_xx+g*L_j*cos(x)+(g/2)*L_k*sin(x) on a periodic grid."""
    _size(sites)
    _finite(coupling)
    positions = 2 * np.pi * np.arange(sites) / sites
    frequencies = np.fft.fftfreq(sites, d=1 / sites)
    fourier = np.fft.fft(np.eye(sites), axis=0) / math.sqrt(sites)
    laplacian = (fourier.conj().T @ np.diag(-(frequencies**2)) @ fourier).real
    return np.asarray(
        np.kron(laplacian, quaternion_matrix([0, 1, 0, 0]))
        + coupling * np.kron(np.diag(np.cos(positions)), quaternion_matrix([0, 0, 1, 0]))
        + coupling / 2 * np.kron(np.diag(np.sin(positions)), quaternion_matrix([0, 0, 0, 1])),
        dtype=np.complex128,
    )


def split_evolve(state: ComplexMatrix, coupling: float, time: float, steps: int) -> ComplexMatrix:
    """Apply symmetric unitary Fourier/potential splitting without normalizing errors away."""
    grouped_probabilities(state)
    sites = state.size // 2
    _size(sites)
    _finite(coupling, time)
    if type(steps) is not int or steps < 1:
        raise ValueError("steps must be a positive integer")
    delta = time / steps
    positions = 2 * np.pi * np.arange(sites) / sites
    frequencies = np.fft.fftfreq(sites, d=1 / sites)
    phase = np.exp(-0.5j * frequencies**2 * delta)
    kinetic = np.column_stack((phase, phase.conj()))
    potential = coupling * np.cos(positions)[:, None, None] * quaternion_matrix([0, 0, 1, 0])
    potential += coupling / 2 * np.sin(positions)[:, None, None] * quaternion_matrix([0, 0, 0, 1])
    radius = abs(coupling) * np.sqrt(np.cos(positions) ** 2 + 0.25 * np.sin(positions) ** 2)
    local = np.asarray(np.cos(delta * radius)[:, None, None] * np.eye(2), dtype=complex)
    local += (delta * np.sinc(delta * radius / np.pi))[:, None, None] * potential
    evolved = np.asarray(state, dtype=complex).reshape(sites, 2).copy()
    for _ in range(steps):
        evolved = np.fft.ifft(np.fft.fft(evolved, axis=0) * kinetic, axis=0)
        evolved = np.einsum("nij,nj->ni", local, evolved)
        evolved = np.fft.ifft(np.fft.fft(evolved, axis=0) * kinetic, axis=0)
    return evolved.reshape(-1)


def left_fourier(sites: int) -> ComplexMatrix:
    """Encode the normalized left-i Fourier transform as two conjugate channels."""
    _size(sites)
    frequencies, positions = np.indices((sites, sites))
    phases = np.exp(-2j * np.pi * frequencies * positions / sites) / math.sqrt(sites)
    result = np.zeros((2 * sites, 2 * sites), dtype=complex)
    result[0::2, 0::2], result[1::2, 1::2] = phases, phases.conj()
    return result


def right_fourier_real(sites: int) -> RealMatrix:
    """Return a real-coordinate right-j transform; its dimension is 4*sites."""
    _size(sites)
    right_j = np.array([[cd_sign(4, column, 2) if row == column ^ 2 else 0 for column in range(4)] for row in range(4)])
    frequencies, positions = np.indices((sites, sites))
    angles = -2 * np.pi * frequencies * positions / sites
    blocks = np.cos(angles)[:, :, None, None] * np.eye(4) + np.sin(angles)[:, :, None, None] * right_j
    return np.asarray(blocks.transpose(0, 2, 1, 3).reshape(4 * sites, 4 * sites) / math.sqrt(sites))


def _left(unit: int) -> Any:
    return sp.Matrix(8, 8, lambda row, column: cd_sign(8, unit, column) if row == unit ^ column else 0)


def _right(unit: int) -> Any:
    return sp.Matrix(8, 8, lambda row, column: cd_sign(8, column, unit) if row == unit ^ column else 0)


def _commutator(first: Any, second: Any) -> Any:
    return first * second - second * first


def _derivation(pair: tuple[int, int]) -> Any:
    first, second = pair
    return (
        _commutator(_left(first), _left(second))
        + _commutator(_left(first), _right(second))
        + _commutator(_right(first), _right(second))
    ).reshape(64, 1)


def _clifford_word(mask: int) -> Any:
    product = sp.eye(8)
    for index in range(6):
        if mask & (1 << index):
            product *= _left(index + 1)
    return product.reshape(64, 1)


def _clifford_failures(dimension: int) -> int:
    operators = [
        sp.Matrix(
            dimension,
            dimension,
            lambda row, column, unit=unit: cd_sign(dimension, unit, column) if row == unit ^ column else 0,
        )
        for unit in range(1, dimension)
    ]
    return (
        sum(
            first * second + second * first != sp.zeros(dimension)
            for index, first in enumerate(operators)
            for second in operators[index + 1 :]
        )
        * 2
    )


def algebra_certificate() -> dict[str, Any]:
    """Certify the finite color/ladder convention using exact integer and rational matrices."""
    columns = ordered_map(_derivation, list(combinations(range(1, 8), 2)))
    derivations = [column.reshape(8, 8) for column in sp.Matrix.hstack(*columns).columnspace()]
    coefficients = sp.Matrix.hstack(*(derivation[:, 7] for derivation in derivations)).nullspace()
    stabilizer = [
        sum(
            (coefficient * derivation for coefficient, derivation in zip(vector, derivations, strict=True)), sp.zeros(8)
        )
        for vector in coefficients
    ]
    aligned = [(-_left(unit) + sp.I * cd_sign(8, 7, unit) * _left(7 ^ unit)) / 2 for unit in (1, 2, 3)]
    draft = [(-_left(unit) + sp.I * _left(unit + 3)) / 2 for unit in (1, 2, 3)]
    number = sum((operator.conjugate().T * operator for operator in aligned), sp.zeros(8))
    draft_number = sum((operator.conjugate().T * operator for operator in draft), sp.zeros(8))
    car = all(
        aligned[first] * aligned[second].conjugate().T + aligned[second].conjugate().T * aligned[first]
        == (sp.eye(8) if first == second else sp.zeros(8))
        for first in range(3)
        for second in range(3)
    )
    return {
        "schema": "hypercomplex-algebra-certificate-v1",
        "g2_dimension": len(derivations),
        "e7_stabilizer_dimension": len(stabilizer),
        "canonical_anticommutation": car,
        "occupation_dimensions": [len((number - level * sp.eye(8)).nullspace()) for level in range(4)],
        "aligned_commutators_failed": sum(_commutator(number, generator) != sp.zeros(8) for generator in stabilizer),
        "draft_commutators_failed": sum(
            _commutator(draft_number, generator) != sp.zeros(8) for generator in stabilizer
        ),
        "clifford_image_rank": int(sp.Matrix.hstack(*ordered_map(_clifford_word, list(range(64)))).rank()),
        "operator_homomorphism": _left(1) * _left(2) == cd_sign(8, 1, 2) * _left(3),
        "higher_dimensional_clifford_failures": dict(
            zip(("16", "32"), ordered_map(_clifford_failures, [16, 32]), strict=True)
        ),
        "evidence_kind": "exact finite algebra; no physical particle identification",
    }
