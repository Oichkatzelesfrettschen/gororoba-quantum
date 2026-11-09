"""The SELECT sign of select_lcu has algebraic degree 4 on every pair of distinct imaginary sedenion units.

g(a, x) = f_i(x) ^ a (f_i(x) ^ f_j(x)) with f_m(x) = [cd_sign(16, m, x) = -1]: each f_m of an imaginary unit has
degree 3 in the four bits of x, and the ancilla bit a raises the joint sign to degree 4, so the Reed-Muller route
needs a controlled-controlled-controlled-Z for every pair and never more.
"""

from __future__ import annotations

from itertools import combinations

from boolean_anf import anf_degree
from cd_core import cd_sign
from select_lcu import joint_select_signs

SEDENION = 16


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _bits(signs: list[float]) -> list[int]:
    return [1 if s < 0 else 0 for s in signs]


def test_each_imaginary_unit_sign_has_degree_three() -> None:
    for m in range(1, SEDENION):
        degree = anf_degree([1 if cd_sign(SEDENION, m, x) < 0 else 0 for x in range(SEDENION)])
        _check(degree == 3, f"f_{m} has degree {degree}")


def test_the_joint_select_sign_has_degree_four_on_all_105_pairs() -> None:
    pairs = list(combinations(range(1, SEDENION), 2))
    _check(len(pairs) == 105, f"{len(pairs)} pairs")
    for i, j in pairs:
        degree = anf_degree(_bits(joint_select_signs(SEDENION, i, j)))
        _check(degree == 4, f"pair ({i}, {j}) has degree {degree}")
