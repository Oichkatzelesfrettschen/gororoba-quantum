"""The phase-slope search interval of scripts/n21_orbit_rca.py: an exposure ratio p / q makes the summed
profile periodic in the nominal phase with period 2 pi q exactly, so the search covers one period when the
exposure bound reaches past it and the bound otherwise.
"""

from __future__ import annotations

import math
from fractions import Fraction

import n21_orbit_rca as rca


def expect(found: object, wanted: object) -> None:
    if found != wanted:
        raise AssertionError(f"{found!r} != {wanted!r}")


def test_integer_ratio_searches_one_turn() -> None:
    expect(rca.slope_search_interval(10.38, Fraction(519, 519)), (-math.pi, math.pi, True))


def test_rational_ratio_period_spans_q_turns() -> None:
    expect(rca.slope_search_interval(20.0, Fraction(17, 10)), (-20.0, 20.0, False))
    expect(rca.slope_search_interval(40.0, Fraction(3, 2)), (-2 * math.pi, 2 * math.pi, True))


def test_period_is_exact_for_the_ratio() -> None:
    # The window_delay phase advances p turns while the nominal phase advances q turns.
    ratio = Fraction(-1415, -1000)
    low, high, _periodic = rca.slope_search_interval(1e4, ratio)
    turns = Fraction(round((high - low) / (2 * math.pi)))
    expect(turns, ratio.denominator)
    expect(ratio * turns, ratio.numerator)
