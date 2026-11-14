"""Quadrics on the Gauss image: polarization, the Plucker family, the product on K, the sandwich, the record rules."""

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
from nullity4_gauss_image import IMAGINARY, PRIME, STRATA, Points, _block  # noqa: E402


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

    def swap_names(found: dict[str, Any]) -> None:
        found["families"][2]["name"], found["families"][3]["name"] = (
            found["families"][3]["name"],
            found["families"][2]["name"],
        )

    top: dict[str, Mutation] = {
        "field": ("headed otherwise", lambda r: r.update(field="GF(2)")),
        "inputs": ("input digests", lambda r: r.update(inputs={})),
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
        "strata dropped": ("other strata", lambda r: r["strata"].pop(STRATA[2])),
    }
    changes = {
        **top,
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

    def move_outside(found: dict[str, Any]) -> None:
        found["characters"][1][2] -= 1
        found["characters"][9][2] += 1

    changes.update(_per_stratum("character of the outside quadrics", "fall in other characters", move_outside))
    changes.update(
        _per_stratum("character list", "sixteen characters", lambda found: found["characters"].pop()),
    )
    changes["quadric is the norm"] = ("sum of the squares", lambda r: r.update(quadric_is_norm=1))
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
