"""Algebra boundary and exact-certificate regression cases."""

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import cd_core


@pytest.mark.parametrize("dimension", [0, -1, 3, True, 8.0])
def test_invalid_dimensions(dimension: Any) -> None:
    with pytest.raises(ValueError):
        cd_core.cd_sign(dimension, 0, 0)


@pytest.mark.parametrize("index", [-1, 8, True, 1.0])
def test_invalid_indices(index: Any) -> None:
    for operation in (lambda: cd_core.cd_sign(8, index, 0), lambda: cd_core.basis(8, index)):
        with pytest.raises(ValueError):
            operation()


def test_real_algebra_and_last_basis_unit() -> None:
    if cd_core.cd_sign(1, 0, 0) != 1 or cd_core.basis(1, 0) != [1.0]:
        raise AssertionError("dimension one must implement real multiplication")
    if cd_core.cd_sign(8, 7, 7) != -1 or cd_core.basis(8, 7)[7] != 1.0:
        raise AssertionError("the final valid basis index must remain admitted")


def test_exact_index_protocol() -> None:
    import sympy

    if cd_core.cd_sign(8, sympy.Integer(1), sympy.Integer(2)) != 1:
        raise AssertionError("exact symbolic matrix indices must retain their integer meaning")


def test_index_protocol_normalization() -> None:
    class BasisIndex:
        def __index__(self) -> int:
            return 1

    index: Any = BasisIndex()
    if cd_core.cd_sign(8, index, 2) != 1 or cd_core.triple_sign(8, index, 2, 4) != (1, -1):
        raise AssertionError("basis arithmetic must normalize the integer-index protocol")
    if cd_core.fano_completion(index, 2) != 3:
        raise AssertionError("Fano completion must normalize its basis indices")
    if cd_core.left_mult_matrix_check(index, 2) != cd_core.left_mult_matrix_check(1, 2):
        raise AssertionError("basis matrices must normalize their indices")


@pytest.mark.parametrize("length", [1, 3])
def test_vector_lengths(length: int) -> None:
    invalid = [1.0] * length
    valid = [1.0, 0.0]
    operations = (
        lambda: cd_core.cd_multiply(2, invalid, valid),
        lambda: cd_core.cd_multiply(2, valid, invalid),
        lambda: cd_core.left_mult_matrix(2, invalid),
        lambda: cd_core.associator(2, valid, valid, invalid),
    )
    for operation in operations:
        with pytest.raises(ValueError):
            operation()


@pytest.mark.parametrize("pair", [(1, 1), (0, 1), (-1, 2), (1, 8)])
def test_invalid_fano_pair(pair: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        cd_core.fano_completion(*pair)


def test_fano_boundary_pairs() -> None:
    if cd_core.fano_completion(1, 7) != 6 or cd_core.fano_completion(6, 7) != 1:
        raise AssertionError("distinct imaginary units must complete their Fano line")


def test_exact_cancellation() -> None:
    first = [2**27 + 1, 2**27]
    second = [2**27 - 1, 2**27]
    exact = cd_core.cd_multiply_exact(2, first, second)
    if exact != (Fraction(-1), Fraction(2**55)):
        raise AssertionError(f"exact complex product lost its integer coordinate: {exact}")
    if cd_core.cd_multiply(2, first, second)[0] != 0.0:
        raise AssertionError("the numerical regression fixture changed its binary64 behavior")


@pytest.mark.parametrize("coordinate", [True, 1.0])
def test_exact_scalar_rejection(coordinate: Any) -> None:
    for operation in (
        lambda: cd_core.cd_multiply_exact(1, [coordinate], [1]),
        lambda: cd_core.left_mult_matrix_exact(1, [coordinate]),
        lambda: cd_core.left_mult_determinant_exact(1, [coordinate]),
    ):
        with pytest.raises(ValueError):
            operation()


def test_exact_determinants_and_counterexample_types() -> None:
    for indices, expected in (((0, 9), 256), ((1, 9), 256), ((1, 10), 0)):
        vector = [int(index in indices) for index in range(16)]
        determinant = cd_core.left_mult_determinant_exact(16, vector)
        if determinant != expected or not isinstance(determinant, Fraction):
            raise AssertionError(f"incorrect exact determinant for {indices}: {determinant}")
    facts = cd_core.sedenion_counterexamples()
    if facts["e0+e9"] != {"det": Fraction(256), "square_is_scalar": False, "square_scale": None}:
        raise AssertionError("the non-scalar control must carry an optional scale")
    if facts["e1+e9"] != {"det": Fraction(256), "square_is_scalar": True, "square_scale": Fraction(-2)}:
        raise AssertionError("the parallel imaginary halves must square to minus twice the identity")
    if type(facts["e1+e9"]["square_is_scalar"]) is not bool:
        raise AssertionError("scalar-square status must be a Boolean")


def test_corpus_matches_retained_independent_integer_rows() -> None:
    from verify import _corpus

    root = Path(__file__).resolve().parents[2]
    tables = json.loads((root / "docs/evidence/algebra_packages/tables.json").read_text())
    signs = tables["packages"]["hypercomplex"]["tables"]["16"]["signs"]
    independent = _corpus(lambda dimension, first, second: int(signs[first][second]))
    corpus = cd_core.sedenion_zero_divisor_corpus()
    if len(corpus) != 336 or set(corpus) != independent:
        raise AssertionError("the signed two-support corpus differs from the independent table enumeration")
    ordered = sorted(corpus, key=lambda row: (row[0], row[1], -row[2], row[3], row[4], -row[5]))
    if corpus != ordered:
        raise AssertionError("the corpus changed its operand and relative-sign iteration order")


@pytest.mark.parametrize("dimension", [0, -2, 3])
def test_exact_invalid_dimensions(dimension: int) -> None:
    for operation in (
        lambda: cd_core.cd_multiply_exact(dimension, [], []),
        lambda: cd_core.left_mult_matrix_exact(dimension, []),
        lambda: cd_core.left_mult_determinant_exact(dimension, []),
    ):
        with pytest.raises(ValueError):
            operation()


@pytest.mark.parametrize("length", [1, 3])
def test_exact_lengths(length: int) -> None:
    for operation in (
        lambda: cd_core.cd_multiply_exact(2, [1] * length, [0, 1]),
        lambda: cd_core.cd_multiply_exact(2, [0, 1], [1] * length),
        lambda: cd_core.left_mult_matrix_exact(2, [1] * length),
    ):
        with pytest.raises(ValueError):
            operation()


def test_rational_matrix_and_real_product() -> None:
    if cd_core.cd_multiply_exact(1, [Fraction(2, 3)], [Fraction(3, 5)]) != (Fraction(2, 5),):
        raise AssertionError("exact real products must preserve rational coefficients")
    matrix = cd_core.left_mult_matrix_exact(2, [Fraction(1, 2), Fraction(2, 3)])
    if matrix != ((Fraction(1, 2), Fraction(-2, 3)), (Fraction(2, 3), Fraction(1, 2))):
        raise AssertionError("left multiplication columns changed their complex orientation")
