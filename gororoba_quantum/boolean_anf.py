"""Algebraic normal form for Boolean truth tables.

The in-place Moebius transform maps a truth table on F_2^n to the masks of
its nonzero algebraic-normal-form monomials. Cayley-Dickson sign functions use
the masks as phase-polynomial coefficients. Reversible modular arithmetic uses
the same representation as a compiler IR for output bits.
"""

from __future__ import annotations

from collections import Counter


def anf_coefficients(truth_table: list[int]) -> tuple[int, ...]:
    """Return the monomial masks with coefficient one in the Boolean ANF."""
    size = len(truth_table)
    if size == 0 or size & (size - 1):
        raise ValueError(f"truth-table length must be a positive power of two, got {size}")
    if any(value not in (0, 1) for value in truth_table):
        raise ValueError("truth-table entries must be zero or one")

    transformed = list(truth_table)
    variable_count = size.bit_length() - 1
    for bit_index in range(variable_count):
        bit_mask = 1 << bit_index
        for input_value in range(size):
            if input_value & bit_mask:
                transformed[input_value] ^= transformed[input_value ^ bit_mask]
    return tuple(mask for mask, coefficient in enumerate(transformed) if coefficient)


def anf_degree_from_coefficients(coefficients: tuple[int, ...]) -> int:
    """Return the largest monomial degree in an ANF coefficient tuple."""
    return max((mask.bit_count() for mask in coefficients), default=0)


def anf_degree(truth_table: list[int]) -> int:
    """Return the algebraic degree of a Boolean truth table."""
    return anf_degree_from_coefficients(anf_coefficients(truth_table))


def anf_degree_histogram(coefficients: tuple[int, ...]) -> dict[int, int]:
    """Count nonzero ANF coefficients by monomial degree."""
    return dict(sorted(Counter(mask.bit_count() for mask in coefficients).items()))


def evaluate_anf(coefficients: tuple[int, ...], input_value: int) -> int:
    """Evaluate an ANF represented by monomial masks at one packed input."""
    output = 0
    for mask in coefficients:
        if input_value & mask == mask:
            output ^= 1
    return output
