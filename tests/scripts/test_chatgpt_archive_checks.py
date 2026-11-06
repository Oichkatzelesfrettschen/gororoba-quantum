"""Contracts of the exact checks behind the ChatGPT-archive verified results."""

from __future__ import annotations

import chatgpt_archive_checks as claims


def test_j_coefficients_and_mckay_decompositions() -> None:
    qj = claims.j_coefficients()["q_j"]
    if not isinstance(qj, list) or qj[:4] != [1, 744, 196884, 21493760]:
        raise AssertionError(f"j coefficients {qj}")


def test_e8_character_is_the_cube_root_of_j() -> None:
    if claims.e8_character_cube_root()["cube_equals_qj"] is not True:
        raise AssertionError("E4/eta^8 cubed differs from j")


def test_j_at_i_is_1728() -> None:
    if abs(claims.j_at_i() - 1728) > 1e-6:
        raise AssertionError("j(i)")


def test_e8_root_split_under_a_fixed_root() -> None:
    if claims.e8_root_split()["0"] != 126:
        raise AssertionError("E7 root count")


def test_ising_level_two_singular_vectors() -> None:
    if claims.ising_level_two() != {"1/2": "-3/4", "1/16": "-4/3"}:
        raise AssertionError("Ising coefficients")


def test_sugawara_contraction_normalizations() -> None:
    if claims.sugawara_contraction()["epsilon"] != -2:
        raise AssertionError("epsilon contraction")


def test_doubling_formulas_and_sedenion_zero_divisor() -> None:
    if claims.norm_failures()["conversation_dim8"] != [8, 4]:
        raise AssertionError("conversation doubling witness")


def test_jacobiator_vanishes_exactly_on_xor_lines() -> None:
    if claims.jacobiator_zero_set((8, 16)) != {"8": [7, 35], "16": [35, 455]}:
        raise AssertionError("XOR-line counts")


def test_power_associative_and_not_associative() -> None:
    if claims.power_associativity((8, 16)) != {"8": True, "16": True}:
        raise AssertionError("power associativity")


def test_fractal_doping_is_scalar() -> None:
    if claims.fractal_doping() != "x + phi x = phi^2 x":
        raise AssertionError("fractal doping")
