"""Algebraic normal form for Boolean truth tables.

The in-place Moebius transform maps a truth table on F_2^n to the masks of
its nonzero algebraic-normal-form monomials. Cayley-Dickson sign functions use
the masks as phase-polynomial coefficients. Reversible modular arithmetic uses
the same representation as a compiler IR for output bits.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping


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


def partial_anf_coefficients(
    samples: Mapping[int, int], variable_count: int, maximum_degree: int
) -> tuple[int, ...] | None:
    """Return one bounded-degree ANF matching partial samples, or None.

    The equations use every square-free monomial of degree at most
    ``maximum_degree`` and Gaussian elimination over GF(2). Free coefficients
    are set to zero, which gives a deterministic witness. This is the finite
    interpolation problem for a punctured Reed-Muller code.
    """
    if variable_count < 0:
        raise ValueError(f"variable count must be nonnegative, got {variable_count}")
    if not 0 <= maximum_degree <= variable_count:
        raise ValueError(f"maximum degree must lie in [0, {variable_count}], got {maximum_degree}")
    if not samples:
        raise ValueError("partial ANF interpolation needs at least one sample")

    domain_size = 1 << variable_count
    ordered_samples: list[tuple[int, int]] = []
    for input_value, output_value in sorted(samples.items()):
        if not 0 <= input_value < domain_size:
            raise ValueError(f"sample input {input_value} lies outside {variable_count}-variable domain")
        if output_value not in (0, 1):
            raise ValueError(f"sample output at {input_value} must be zero or one")
        ordered_samples.append((input_value, output_value))

    monomial_masks = tuple(mask for mask in range(domain_size) if mask.bit_count() <= maximum_degree)
    coefficient_count = len(monomial_masks)
    right_hand_side_mask = 1 << coefficient_count
    coefficient_bits_mask = right_hand_side_mask - 1
    packed_rows = []
    for input_value, output_value in ordered_samples:
        coefficient_bits = sum(
            1 << coefficient_index
            for coefficient_index, monomial_mask in enumerate(monomial_masks)
            if input_value & monomial_mask == monomial_mask
        )
        packed_rows.append(coefficient_bits | output_value * right_hand_side_mask)

    pivot_columns: list[int] = []
    pivot_row_index = 0
    for coefficient_index in range(coefficient_count):
        column_mask = 1 << coefficient_index
        matching_row_index = next(
            (
                row_index
                for row_index in range(pivot_row_index, len(packed_rows))
                if packed_rows[row_index] & column_mask
            ),
            None,
        )
        if matching_row_index is None:
            continue
        packed_rows[pivot_row_index], packed_rows[matching_row_index] = (
            packed_rows[matching_row_index],
            packed_rows[pivot_row_index],
        )
        pivot_row = packed_rows[pivot_row_index]
        for row_index in range(len(packed_rows)):
            if row_index != pivot_row_index and packed_rows[row_index] & column_mask:
                packed_rows[row_index] ^= pivot_row
        pivot_columns.append(coefficient_index)
        pivot_row_index += 1
        if pivot_row_index == len(packed_rows):
            break

    for packed_row in packed_rows:
        if packed_row & coefficient_bits_mask == 0 and packed_row & right_hand_side_mask:
            return None

    return tuple(
        monomial_masks[coefficient_index]
        for row_index, coefficient_index in enumerate(pivot_columns)
        if packed_rows[row_index] & right_hand_side_mask
    )


def minimum_partial_anf_degree(samples: Mapping[int, int], variable_count: int) -> tuple[int, tuple[int, ...]]:
    """Return the minimum degree and a deterministic ANF matching samples."""
    for maximum_degree in range(variable_count + 1):
        coefficients = partial_anf_coefficients(samples, variable_count, maximum_degree)
        if coefficients is not None:
            return maximum_degree, coefficients
    raise RuntimeError("full-degree Boolean interpolation unexpectedly failed")


def _gf2_rank(packed_rows: list[int], column_count: int) -> int:
    """Return the GF(2) rank of bit-packed matrix rows."""
    reduced_rows = list(packed_rows)
    rank = 0
    for column_index in range(column_count):
        column_mask = 1 << column_index
        pivot_index = next(
            (row_index for row_index in range(rank, len(reduced_rows)) if reduced_rows[row_index] & column_mask),
            None,
        )
        if pivot_index is None:
            continue
        reduced_rows[rank], reduced_rows[pivot_index] = (
            reduced_rows[pivot_index],
            reduced_rows[rank],
        )
        pivot_row = reduced_rows[rank]
        for row_index in range(len(reduced_rows)):
            if row_index != rank and reduced_rows[row_index] & column_mask:
                reduced_rows[row_index] ^= pivot_row
        rank += 1
    return rank


def quadratic_polar_rank(coefficients: tuple[int, ...], variable_count: int) -> int:
    """Return the GF(2) rank of a quadratic ANF's alternating polar form.

    Linear and constant monomials vanish under polarization. A coefficient of
    ``x_r x_s`` contributes symmetric off-diagonal entries at ``(r, s)`` and
    ``(s, r)``. Inputs above degree two are outside this function's contract.
    """
    if variable_count < 0:
        raise ValueError(f"variable count must be nonnegative, got {variable_count}")
    if len(set(coefficients)) != len(coefficients):
        raise ValueError("ANF coefficient masks must be unique")
    domain_size = 1 << variable_count
    polar_rows = [0] * variable_count
    for monomial_mask in coefficients:
        if not 0 <= monomial_mask < domain_size:
            raise ValueError(f"monomial mask {monomial_mask} lies outside {variable_count}-variable domain")
        degree = monomial_mask.bit_count()
        if degree > 2:
            raise ValueError(f"monomial mask {monomial_mask} has degree {degree}, expected at most two")
        if degree == 2:
            first_bit = (monomial_mask & -monomial_mask).bit_length() - 1
            second_bit = (monomial_mask ^ (1 << first_bit)).bit_length() - 1
            polar_rows[first_bit] ^= 1 << second_bit
            polar_rows[second_bit] ^= 1 << first_bit
    return _gf2_rank(polar_rows, variable_count)
