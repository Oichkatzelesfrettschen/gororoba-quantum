"""Quadrics on the Gauss image: polarization, the families, the product on K, the sandwiches, the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import gauss_image_quadrics as quadrics  # noqa: E402
from nullity4_gauss_image import (  # noqa: E402
    IMAGINARY,
    PRIME,
    STRATA,
    Points,
    _block,
    _fixture_splits,
    _nullspace,
    _polynomials,
    _rank,
)

import cd_core  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _random_vectors(label: str, count: int) -> np.ndarray:
    points = Points(label)
    return np.array([points.vector() for _ in range(count)], dtype=np.int64)


def _random_bivectors(label: str, count: int) -> np.ndarray:
    """General vectors of the 105-dimensional space of bivectors, which are mostly not decomposable."""
    points = Points(label)
    return np.array([[points.value() for _ in range(quadrics.BIVECTORS)] for _ in range(count)], dtype=np.int64)


def test_polar_rows_pair_with_a_quadric_to_its_polar_form() -> None:
    # Q(x + y) - Q(x) - Q(y) for Q = sum of c_ab x_a x_b over a <= b equals the coefficients paired with the polar row.
    points = Points("test:polar")
    coefficients = [points.value() for _ in range(quadrics.SYMMETRIC_COEFFICIENTS)]
    first, second = _random_vectors("test:polar:vectors", 2)

    def form(vector: np.ndarray) -> int:
        return sum(
            c * int(vector[a]) * int(vector[b])
            for c, (a, b) in zip(coefficients, quadrics.SYMMETRIC_MONOMIALS, strict=True)
        )

    row = quadrics.polar_rows(first, second, quadrics.SYMMETRIC_FIRST, quadrics.SYMMETRIC_SECOND)
    paired = sum(c * int(value) for c, value in zip(coefficients, row, strict=True)) % PRIME
    _same(paired, (form((first + second) % PRIME) - form(first) - form(second)) % PRIME)


def test_quadric_coefficients_recover_the_coefficients_of_quadratic_functions() -> None:
    def function(bivectors: np.ndarray) -> np.ndarray:
        return (
            np.stack(
                [bivectors[:, 0] * bivectors[:, 1] + 3 * bivectors[:, 2] ** 2, bivectors[:, 5] * bivectors[:, 5]],
                axis=1,
            )
            % PRIME
        )

    coefficients = quadrics.quadric_coefficients(function, 2)
    monomials = {monomial: index for index, monomial in enumerate(quadrics.QUADRIC_MONOMIALS)}
    nonzero = [{monomial for monomial, index in monomials.items() if row[index]} for row in coefficients]
    _same(nonzero, [{(0, 1), (2, 2)}, {(5, 5)}])
    _same((int(coefficients[0, monomials[0, 1]]), int(coefficients[0, monomials[2, 2]])), (1, 3))


def test_quadric_coefficients_reject_a_function_that_is_not_quadratic() -> None:
    def function(bivectors: np.ndarray) -> np.ndarray:
        return (bivectors[:, :1] ** 3) % PRIME

    with pytest.raises(RuntimeError):
        quadrics.quadric_coefficients(function, 1)


def test_plucker_relations_vanish_on_decomposable_bivectors_and_not_on_general_ones() -> None:
    first, second = _random_vectors("test:plucker", 2)
    decomposable = quadrics.wedge(first[None, :], second[None, :])
    _same(bool(quadrics.plucker_relations(decomposable).any()), False)
    general = _random_bivectors("test:plucker:general", 1)
    _same(bool(quadrics.plucker_relations(general).any()), True)
    _same(quadrics.plucker_relations(general).shape[1], quadrics.PLUCKER_QUADRICS)


def test_mu_extends_the_block_product_linearly_to_the_exterior_square() -> None:
    first, second = _random_vectors("test:mu", 2)
    block = np.array(_block([int(value) for value in first]), dtype=np.int64)
    expected = block @ second % PRIME
    found = quadrics.MU @ quadrics.wedge(first, second) % PRIME
    _same(found.tolist(), expected.tolist())


def test_block_product_is_the_imaginary_part_of_the_cayley_dickson_product() -> None:
    # For imaginary t and v of the 16-dimensional algebra, t v = -<t, v> + M(t) v.
    for number in range(4):
        first, second = _random_vectors(f"test:cayley-dickson:{number}", 2)
        product = cd_core.cd_multiply_exact(16, [0, *map(int, first)], [0, *map(int, second)])
        block = np.array(_block([int(value) for value in first]), dtype=np.int64)
        _same([int(value) % PRIME for value in product[1:]], (block @ second % PRIME).tolist())
        _same(int(product[0]) % PRIME, int(-(first * second).sum()) % PRIME)


def test_commutant_of_a_null_imaginary_octonion_is_a_heisenberg_algebra_with_that_center() -> None:
    # The octonion counterpart of the product type on V(Q) minus V(G): for a null imaginary octonion z the imaginary
    # elements commuting with z form a null three-plane whose products are multiples of z.
    points = Points("test:octonion")
    found = 0
    while found < 8:
        head = [points.value() for _ in range(6)]
        square = -sum(value * value for value in head) % PRIME
        root = pow(square, (PRIME + 1) // 4, PRIME)
        if root * root % PRIME != square or not root:
            continue
        found += 1
        null = [*head, root]
        columns = [
            [int(v) % PRIME for v in cd_core.cd_multiply_exact(8, [0, *null], [0, *unit])[1:]]
            for unit in np.eye(7, dtype=np.int64).tolist()
        ]
        kernel = _nullspace([list(row) for row in zip(*columns, strict=True)])
        _same(len(kernel), 3)
        _same(any(sum(a * b for a, b in zip(u, v, strict=True)) % PRIME for u in kernel for v in kernel), False)
        products = [
            [int(v) % PRIME for v in cd_core.cd_multiply_exact(8, [0, *kernel[a]], [0, *kernel[b]])]
            for a, b in ((0, 1), (0, 2), (1, 2))
        ]
        _same([row[0] for row in products], [0, 0, 0])
        nonzero = [row[1:] for row in products if any(row)]
        _same((_rank(nonzero), _rank([*nonzero, null])), (1, 1))


def test_sign_changes_of_the_coordinates_preserve_the_block_and_both_hypersurfaces() -> None:
    # M is linear in t, so M(D e_j) = D M(e_j) D on the 15 frame vectors gives M(D t) = D M(t) D for every t; a
    # polynomial is invariant under every sign change exactly when each monomial has trivial character, the xor of
    # the 1-based indices that carry an odd exponent.
    for character in quadrics.CHARACTERS:
        signs = np.array([1 - 2 * ((character & index).bit_count() % 2) for index in range(1, IMAGINARY + 1)])
        for index, block in enumerate(quadrics.BLOCKS):
            twisted = signs[index] * block % PRIME
            _same((signs[:, None] * block * signs[None, :] % PRIME).tolist(), twisted.tolist())
    for name, terms in (("Q", 15), ("G", 141)):
        polynomial = _polynomials()[name]
        weights = set()
        for exponents in polynomial.monoms():
            weight = 0
            for index, exponent in enumerate(exponents, start=1):
                if int(exponent) % 2:
                    weight ^= index
            weights.add(weight)
        _same((len(polynomial), weights), (terms, {0}))


def test_quadric_is_the_sum_of_squares_of_the_frame_coordinates_over_the_integers() -> None:
    # Q = sum of (-1)^popcount(k) t'_k^2 in the split coordinates, and t'_k^2 = (-1)^popcount(k) t_k^2 in the frame
    # t_k = i^popcount(k) t'_k, so Q is the sum of the squares of the frame coordinates in characteristic 0.
    polynomial = _polynomials()["Q"]
    expected = {}
    for index in range(1, IMAGINARY + 1):
        exponents = [0] * IMAGINARY
        exponents[index - 1] = 2
        expected[tuple(exponents)] = (-1) ** index.bit_count()
    found = {
        tuple(int(e) for e in exponents): int(coefficient)
        for exponents, coefficient in zip(polynomial.monoms(), polynomial.coeffs(), strict=True)
    }
    _same(found, expected)


def test_combination_of_a_sandwich_is_minus_the_mixed_discriminant_on_the_plane() -> None:
    # trace(c Pi(p) D Pi(p)) = 2 c(u, v) D(u, v) - c(u, u) D(v, v) - c(v, v) D(u, u) for p = u ^ v.
    first, second = _random_vectors("test:mixed", 2)
    forms = []
    for label in ("test:mixed:c", "test:mixed:d"):
        half = _random_vectors(label, IMAGINARY)
        forms.append((half + half.T) % PRIME)
    c, d = forms
    matrix = quadrics.skew_matrices(quadrics.wedge(first[None, :], second[None, :]))[0]
    found = int(np.trace(c @ (matrix @ d % PRIME @ matrix % PRIME) % PRIME)) % PRIME

    def pair(form: np.ndarray, left: np.ndarray, right: np.ndarray) -> int:
        return int(left @ form % PRIME @ right) % PRIME

    expected = (
        2 * pair(c, first, second) * pair(d, first, second)
        - pair(c, first, first) * pair(d, second, second)
        - pair(c, second, second) * pair(d, first, first)
    ) % PRIME
    _same(found, expected)


def test_rank_one_form_on_a_three_plane_yields_the_quadrics_of_the_forms_vanishing_on_its_kernel_plane() -> None:
    # D = l^2 on K: the combination with c vanishes on Lambda^2 K exactly when c vanishes on K n ker l. Here K is
    # the span of e_1, e_2, e_3 and l the first coordinate, so K n ker l is the span of e_2 and e_3.
    kernel = np.eye(IMAGINARY, dtype=np.int64)[:3]
    bivectors = quadrics.wedge(kernel[[0, 0, 1]], kernel[[1, 2, 2]])
    general = quadrics.wedge(*_random_vectors("test:rank-one", 2) @ np.eye(IMAGINARY, dtype=np.int64)[:, :3] @ kernel)
    matrices = quadrics.skew_matrices(np.array([*bivectors, general]))
    d = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
    d[0, 0] = 1
    sandwich = np.matmul(np.matmul(matrices, d) % PRIME, matrices) % PRIME
    vanishing_on_plane = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
    vanishing_on_plane[0, 0], vanishing_on_plane[0, 1], vanishing_on_plane[1, 0] = 5, 7, 7
    nonzero_on_plane = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
    nonzero_on_plane[1, 2] = nonzero_on_plane[2, 1] = 1
    _same([int(np.trace(vanishing_on_plane @ s)) % PRIME for s in sandwich], [0, 0, 0, 0])
    _same(any(int(np.trace(nonzero_on_plane @ s)) % PRIME for s in sandwich), True)


def test_doubling_forms_have_rank_at_most_one_on_the_kernels_inside_the_quartic_hypersurface() -> None:
    _same(np.sum(quadrics.DOUBLING_FORMS, axis=0).tolist(), np.eye(IMAGINARY, dtype=np.int64).tolist())
    _same(quadrics.three_plane((STRATA[0], 1))[2], [0, 3, 1, 3])
    _same(quadrics.three_plane((STRATA[1], 1))[2], [1, 1, 1, 1])
    _same(quadrics.three_plane((STRATA[2], 1))[2], [0, 1, 1, 1])


def test_fixture_class_is_exact_and_agrees_with_the_modular_class_of_its_stratum() -> None:
    first: dict[str, tuple[int, str, list[int]]] = {}
    for job in _fixture_splits():
        first.setdefault(job[1], job)
    for stratum, job in first.items():
        found = quadrics.fixture_class(job)
        _same(found[:2], [stratum, 3])
        _same(found[2:6], quadrics.PRODUCT_CLASSES[stratum][0][:4])
        if stratum != STRATA[0]:
            _same(max(found[7:]) <= 1, True)


def test_independent_rows_give_the_rank_of_every_prefix() -> None:
    rows = np.array([[1, 2, 3], [2, 4, 6], [0, 1, 1], [1, 3, 4], [0, 0, 5]], dtype=np.int64)
    pivots = quadrics.independent_rows(rows)
    _same(pivots, [0, 2, 4])
    _same([quadrics.prefix_rank(pivots, count) for count in range(6)], [0, 1, 1, 2, 2, 3])
    _same(quadrics.matrix_rank(rows), 3)
    _same(quadrics.independent_rows(rows[:0]), [])


def test_product_mod_prime_matches_integer_arithmetic() -> None:
    left, right = _random_vectors("test:product:left", 4), _random_vectors("test:product:right", 3)
    found = quadrics.product_mod_prime(left, right.T)
    expected = [
        [sum(int(a) * int(b) for a, b in zip(row, column, strict=True)) % PRIME for column in right] for row in left
    ]
    _same(found.tolist(), expected)
    with pytest.raises(RuntimeError):
        quadrics.product_mod_prime(left - PRIME, right.T)


def test_three_planes_carry_the_product_class_of_their_stratum() -> None:
    # Heisenberg product on V(Q) minus V(G): M(k) k' is a multiple of z; the product vanishes on V(Q) n V(G).
    _same(quadrics.three_plane((STRATA[0], 0))[1], [1, 3, True, 1])
    _same(quadrics.three_plane((STRATA[1], 0))[1], [1, 4, False, 2])
    _same(quadrics.three_plane((STRATA[2], 0))[1], [0, 3, True, 0])


def test_sandwich_of_a_form_vanishing_on_the_kernels_kills_their_exterior_square() -> None:
    # Pi(p) beta Pi(p) = 0 for p = u ^ v in Lambda^2 K when beta vanishes on K: every entry is a multiple of
    # beta(u, u), beta(u, v) or beta(v, v). The form comes from a sample of planes, the check runs on its planes.
    kernels = np.array([quadrics.three_plane((STRATA[0], number))[0] for number in range(40)], dtype=np.int64)
    betas = quadrics.symmetric_forms_vanishing(kernels)
    _same(len(betas), 1)
    bivectors = quadrics.wedge(kernels[:, [0, 0, 1]], kernels[:, [1, 2, 2]]).reshape(-1, quadrics.BIVECTORS)
    matrices = quadrics.skew_matrices(bivectors)
    sandwich = np.matmul(np.matmul(matrices, betas[0]) % PRIME, matrices) % PRIME
    _same(bool(sandwich.any()), False)
    # A form that does not vanish on the planes (the square of the first coordinate) leaves a nonzero sandwich.
    coordinate = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
    coordinate[0, 0] = 1
    _same(bool((np.matmul(np.matmul(matrices, coordinate) % PRIME, matrices) % PRIME).any()), True)


def test_linear_forms_times_coordinates_vanish_where_the_form_does() -> None:
    form = np.zeros((1, quadrics.BIVECTORS), dtype=np.int64)
    form[0, 0] = 1
    function = quadrics.linear_forms_times_coordinates(form)
    bivectors = _random_bivectors("test:linear", 3)
    bivectors[:, 0] = 0
    _same(bool(function(bivectors).any()), False)
    bivectors[:, 0] = 1
    _same(bool(function(bivectors).any()), True)


Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _per_stratum(name: str, fragment: str, change: Callable[[dict[str, Any]], Any]) -> dict[str, Mutation]:
    """One mutation of `change` on the row of each stratum, with the fragment of the message that must follow."""

    def on_stratum(stratum: str) -> Callable[[dict[str, Any]], Any]:
        return lambda record: change(record["strata"][stratum])

    return {f"{name} on {stratum}": (fragment, on_stratum(stratum)) for stratum in STRATA}


def test_retained_record_passes_its_rules_and_each_mutation_fails_them(monkeypatch: pytest.MonkeyPatch) -> None:
    record = json.loads(quadrics.RECORD.read_text(encoding="utf-8"))
    # The digests of the live source files are compared by the on-demand replay gate; here the rule that compares
    # them is exercised against a fixed copy, so an edit of an input file leaves the required test lane green.
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(quadrics, "_inputs", lambda: dict(retained_inputs))
    _same((record["pass"], quadrics.verdict(record)), (True, []))
    _same(sorted(record["strata"]), sorted(STRATA))

    def family(index: int, **fields: int) -> Callable[[dict[str, Any]], Any]:
        return lambda found: found["families"][index].update(fields)

    def bump(field: str, delta: int) -> Callable[[dict[str, Any]], Any]:
        return lambda found: found["quadric_rank"].update({field: found["quadric_rank"][field] + delta})

    def set_plane_count(found: dict[str, Any]) -> None:
        found["planes"] = 759

    def set_spans(found: dict[str, Any]) -> None:
        found["spans"]["bivectors"] -= 1

    def set_product_class(found: dict[str, Any]) -> None:
        found["product_classes"][0][3] += 1

    def set_symmetric_forms(found: dict[str, Any]) -> None:
        found["symmetric_forms"] += 1

    def set_mu_span(found: dict[str, Any]) -> None:
        found["forms_and_mu_rank"] += 1

    def set_cumulative_decrease(found: dict[str, Any]) -> None:
        found["families"][3]["cumulative"] = found["families"][2]["cumulative"] - 1

    def set_unexplained(found: dict[str, Any]) -> None:
        found["unexplained"] += 1

    def set_cumulative_end(found: dict[str, Any]) -> None:
        found["families"][-1]["cumulative"] += 1

    def set_form_ranks(found: dict[str, Any]) -> None:
        found["doubling_form_ranks"][0][1] += 1

    def shift_between_characters(found: dict[str, Any]) -> None:
        # Sums and differences of the columns stay as they are; only the pinned rows see the change.
        for column in range(1, 4):
            found["characters"][0][column] += 1
            found["characters"][1][column] -= 1

    def shift_monomials(found: dict[str, Any]) -> None:
        found["characters"][0][0] -= 1
        found["characters"][1][0] += 1

    def swap_names(found: dict[str, Any]) -> None:
        found["families"][2]["name"], found["families"][3]["name"] = (
            found["families"][3]["name"],
            found["families"][2]["name"],
        )

    top: dict[str, Mutation] = {
        "field": ("headed otherwise", lambda r: r.update(field="GF(2)")),
        "one input digest": ("input digests", lambda r: r["inputs"].update({next(iter(r["inputs"])): "0" * 64})),
        "stated failure": ("states that it fails", lambda r: r.update({"pass": False})),
        "mu rank": ("another rank than 15", lambda r: r.update(mu_rank=14)),
        "general square rank": ("Plucker quadrics", lambda r: r["calibration"].update(square_rank=4199)),
        "general annihilator": ("Plucker quadrics", lambda r: r["calibration"].update(annihilator=1364)),
        "plucker family rank": ("Plucker quadrics", lambda r: r["calibration"].update(plucker_family_rank=1364)),
        "plucker family annihilates": (
            "Plucker quadrics",
            lambda r: r["calibration"].update(plucker_family_annihilates=False),
        ),
        "norm family rank": ("other ranks", lambda r: r["family_ranks"].update(plucker_with_norm_family=1484)),
        "block product family rank": (
            "other ranks",
            lambda r: r["family_ranks"].update(plucker_with_block_product_and_norm_families=1677),
        ),
        "fixture count": ("exact fixtures have other classes", lambda r: r["fixtures"][0].__setitem__(-1, 5)),
        "fixture form rank": ("exact fixtures have other classes", lambda r: r["fixtures"][-1].__setitem__(7, 1)),
        "quadric is the norm": ("sum of the squares", lambda r: r.update(quadric_is_norm=False)),
        "any pinned value": ("differs from the record the constants determine", lambda r: r.update(mu_rank=14)),
    }
    # A record with other fields or value types ends the verdict before a rule reads it: True == 1 and 15.0 == 15
    # under ==, and a missing or mistyped field would raise inside a rule.
    shape = "other fields or value types"
    first = STRATA[0]
    shapes: dict[str, Mutation] = {
        "inputs emptied": (shape, lambda r: r.update(inputs={})),
        "pass dropped": (shape, lambda r: r.pop("pass")),
        "added field": (shape, lambda r: r.update(note="")),
        "strata dropped": (shape, lambda r: r["strata"].pop(STRATA[2])),
        "strata as a list": (shape, lambda r: r.update(strata=list(r["strata"].values()))),
        "integer for a boolean in the calibration": (
            shape,
            lambda r: r["calibration"].update(plucker_family_annihilates=1),
        ),
        "integer for a boolean in a product class": (
            shape,
            lambda r: r["strata"][first]["product_classes"][0].__setitem__(2, 1),
        ),
        "integer for the norm flag": (shape, lambda r: r.update(quadric_is_norm=1)),
        "float for an integer": (shape, lambda r: r.update(mu_rank=15.0)),
        "boolean for a count": (shape, lambda r: r["strata"][first].update(symmetric_forms=True)),
        "boolean for a rank": (shape, lambda r: r["strata"][first].update(forms_with_quadric_rank=True)),
        "added family field": (shape, lambda r: r["strata"][first]["families"][0].update(note=0)),
        "family field dropped": (shape, lambda r: r["strata"][first]["families"][2].pop("vanishing")),
        "family field emptied": (shape, lambda r: r["strata"][first]["families"][2].update(vanishing=None)),
        "character row as text": (shape, lambda r: r["strata"][first]["characters"].__setitem__(0, "abcd")),
        "character dropped": (shape, lambda r: r["strata"][first]["characters"].pop()),
    }
    changes = {
        **top,
        **shapes,
        **_per_stratum("form ranks", "doubling forms on K differ", set_form_ranks),
        **_per_stratum("fixture planes", "exact fixtures do not lie", bump("fixture_planes", 1)),
        **_per_stratum("rank with fixtures", "exact fixtures do not lie", bump("rank_with_fixtures", 1)),
        **_per_stratum("shift between characters", "fall in other characters", shift_between_characters),
        **_per_stratum("shift of monomials", "fall in other characters", shift_monomials),
        **_per_stratum("plane count", "three-planes", set_plane_count),
        **_per_stratum("spans", "spans of K", set_spans),
        **_per_stratum("product class", "classes of the product", set_product_class),
        **_per_stratum("symmetric forms", "counts of linear and symmetric forms", set_symmetric_forms),
        **_per_stratum("linear forms and mu", "span the rows of mu", set_mu_span),
        **_per_stratum("product vectors", "six per three-plane", bump("vectors", 6)),
        **_per_stratum("quadric rank", "quadric rank differs", bump("rank", 1)),
        **_per_stratum("annihilator", "annihilator dimension", bump("annihilator", -1)),
        **_per_stratum("saturation count", "saturation reads", bump("planes_below", 1)),
        **_per_stratum("saturation below", "less general", bump("rank_below", -1)),
        **_per_stratum("saturation above", "less general", bump("rank_above", -1)),
        **_per_stratum("retained planes", "count of planes", bump("retained_planes", 1)),
        **_per_stratum("retained rank", "do not span the same quadrics", bump("retained_rank", 1)),
        **_per_stratum("retained first planes", "do not span the same quadrics", bump("retained_rank_first", -1)),
        **_per_stratum("retained stacked", "do not span the same quadrics", bump("retained_rank_stacked", 1)),
        **_per_stratum("family names", "stated list", swap_names),
        **_per_stratum("family written", "family tallies differ", family(2, written=454)),
        **_per_stratum("family rank", "family tallies differ", family(3, rank=119)),
        **_per_stratum("family intersection", "more than its rank", family(3, vanishing=121)),
        **_per_stratum("plucker intersection", "Plucker quadrics do not all vanish", family(0, vanishing=1364)),
        **_per_stratum("cumulative decrease", "cumulative rank decreases", set_cumulative_decrease),
        **_per_stratum("unexplained", "unexplained quadrics differs", set_unexplained),
        **_per_stratum("cumulative end", "unexplained quadrics differs", set_cumulative_end),
    }
    # Families that vanish by construction fail the rule that states it where the family has rank.
    changes["always vanishing form sandwich on V(Q) minus V(G)"] = (
        "vanishes on every three-plane does not",
        lambda r: r["strata"][STRATA[0]]["families"][6].update(vanishing=119),
    )
    changes["always vanishing linear products on V(Q) n V(G)"] = (
        "vanishes on every three-plane does not",
        lambda r: r["strata"][STRATA[2]]["families"][1].update(vanishing=1469),
    )
    changes.update(
        _per_stratum(
            "form against the quadric",
            "not a multiple of the polar form",
            lambda found: found.update(forms_with_quadric_rank=found["forms_with_quadric_rank"] + 1),
        )
    )
    changes.update(
        _per_stratum(
            "character sums",
            "do not split by the characters",
            lambda found: found["characters"][0].__setitem__(0, found["characters"][0][0] + 1),
        )
    )

    def beyond_annihilator(found: dict[str, Any]) -> None:
        found["families"][-1]["cumulative"] = found["quadric_rank"]["annihilator"] + 1

    changes.update(_per_stratum("cumulative beyond the annihilator", "explain more quadrics", beyond_annihilator))
    for name, (fragment, change) in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        problems = quadrics.verdict(mutated)
        if not any(fragment in problem for problem in problems):
            raise AssertionError(f"a record mutated at {name} does not fail on {fragment!r}: {problems}")


def test_replay_comparison_separates_a_boolean_from_an_integer() -> None:
    # True == 1 in Python, so a comparison of parsed records accepts either; the replay compares the retained text.
    _same({"unit": True} == {"unit": 1}, True)
    _same(quadrics._serialized({"unit": True}) == quadrics._serialized({"unit": 1}), False)
