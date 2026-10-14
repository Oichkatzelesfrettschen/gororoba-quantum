"""Pfaffian volume coordinates on complete complex annihilator charts.

The determinant line is trivial on each constant-rank locus. Its polynomial
multivector vanishes when rank decreases, so the construction alone does not
specify frontier kernel inclusions or trivialize the full kernel bundle.
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations

import sympy as sp

from complex_skew import ComplexKernelChart, chart_transition, complex_operator, pfaffian, verify_kernel_chart


def _require_chart(chart: ComplexKernelChart) -> None:
    if not verify_kernel_chart(chart):
        raise ValueError("determinant coordinates require an intact complete kernel chart")


def _order_sign(indices: tuple[int, ...]) -> int:
    return (-1) ** sum(first > second for position, first in enumerate(indices) for second in indices[position + 1 :])


def kernel_volume(chart: ComplexKernelChart) -> sp.Expr:
    """Evaluate the canonical kernel covolume on the chart's ordered frame.

    The quotient skew form and fixed ambient volume define this functional.
    The empty kernel is included; its covolume need not equal one.
    """
    _require_chart(chart)
    return sp.cancel(_order_sign(chart.pivot_indices + chart.free_indices) / chart.pivot_pfaffian)


def determinant_transition(source: ComplexKernelChart, target: ComplexKernelChart) -> sp.Expr:
    """Certify det(T_target_source)=volume(source)/volume(target)."""
    transport = chart_transition(source, target)
    expected = sp.cancel(kernel_volume(source) / kernel_volume(target))
    observed = transport.det(method="domain-ge")
    if sp.cancel(observed - expected) != 0:
        raise RuntimeError("Pfaffian determinant transition fails")
    return expected


def unit_volume_frame(chart: ComplexKernelChart) -> sp.ImmutableMatrix:
    """Rescale one column to obtain determinant-one overlap maps.

    A zero-column frame cannot absorb a nonunit scalar; the rank-zero bundle
    uses its canonical empty frame instead of this positive-rank interface.
    """
    volume = kernel_volume(chart)
    if chart.frame.cols == 0:
        raise ValueError("unit-volume frames require positive kernel dimension")
    scale = sp.eye(chart.frame.cols)
    scale[0, 0] = 1 / volume
    return sp.ImmutableMatrix((chart.frame * scale).applyfunc(sp.cancel))


def kernel_plucker_coordinates(chart: ComplexKernelChart) -> Iterator[tuple[tuple[int, ...], sp.Expr]]:
    """Yield every coordinate of the polynomial kernel determinant section.

    For each increasing free tuple J, its coefficient is sign(I,J)*Pf(K_I),
    where I is the increasing complement. Enumeration is complete and lazy.
    Each coefficient is checked against the independent frame minor identity.
    """
    _require_chart(chart)
    operator = complex_operator(chart.coordinates)
    dimension = operator.rows
    amplitude = 1 / kernel_volume(chart)
    for free in combinations(range(dimension), chart.frame.cols):
        pivot = tuple(index for index in range(dimension) if index not in free)
        coefficient = _order_sign(pivot + free) * pfaffian(operator.extract(pivot, pivot))
        minor = chart.frame.extract(free, range(chart.frame.cols)).det(method="domain-ge")
        if sp.cancel(coefficient - amplitude * minor) != 0:
            raise RuntimeError("complementary Pfaffian and kernel frame minor differ")
        yield free, coefficient
