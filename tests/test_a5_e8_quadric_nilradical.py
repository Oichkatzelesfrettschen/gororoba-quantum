"""The nilradical of the E8-bar quadric ideal over Q(i): five linear forms of square zero, one embedded component, and a
nilradical module with the Hilbert function of the prime quotient by its annihilator."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import e8_quadric_nilradical as nil  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(nil.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(nil.problems(record), [])
    _same(nil.slice_problems(record), [])
    _same(record["pass"], True)
    _same([cell["orbit"] for cell in record["cells"]], ["N-", "N+"])


def test_the_degrees_of_the_primary_components_sum_to_the_multiplicity_in_top_dimension() -> None:
    """Only the 5-dimensional component enters the multiplicity 11; the embedded one doubles a prime of degree 2."""
    components = nil.EXPECTED["primary_components"]
    top = max(component[0] for component in components)
    _same(sum(component[2] for component in components if component[0] == top), nil.EXPECTED["ideal"][1])
    embedded = [component for component in components if not component[3]]
    _same(embedded, [[4, 2, 4, False]])
    _same(sorted(component[:2] for component in components if component[3]), nil.EXPECTED["minimal_primes"])


def test_the_linear_forms_at_the_two_basepoints_are_conjugate() -> None:
    minus, plus = (cell["linear_forms"] for cell in _record()["cells"])
    _same(sorted(form.replace("(-i)", "(i)") for form in plus), sorted(minus))
    _same(sum("i" in form for form in minus), 1)


def test_the_annihilator_is_prime_and_the_nilradical_module_has_the_hilbert_function_of_its_quotient() -> None:
    for cell in _record()["cells"]:
        _same(cell["annihilator_minimal_primes"], 1)
        _same(cell["annihilator_is_radical"], True)
        _same(cell["annihilator_is_prime"], True)
        functions = cell["hilbert_function"]
        module = [whole - quotient for whole, quotient in zip(functions["ideal"], functions["radical"], strict=True)]
        _same(module, functions["annihilator"])
        _same(cell["nilradical_module_hilbert_function_is_that_of_annihilator_quotient"], True)


def test_the_hilbert_function_of_the_annihilator_is_that_of_a_quadric_hypersurface_in_five_variables() -> None:
    """The annihilator has 16 linear generators and one quadric in the five remaining variables, a hypersurface."""
    hypersurface = [math.comb(degree + 4, 4) - math.comb(degree + 2, 4) for degree in nil.HILBERT_DEGREES]
    _same(nil.EXPECTED["hilbert_function"]["annihilator"], hypersurface)
    for cell in _record()["cells"]:
        _same(cell["hilbert_function"]["annihilator"], hypersurface)
        _same(
            cell["hilbert_numerator"]["annihilator"],
            [1, -16, 119, -544, 1700, -3808, 6188, -7072, 4862, 0, -4862, 7072, -6188, 3808, -1700, 544, -119, 16, -1],
        )


def test_the_nilradical_module_has_the_hilbert_series_of_the_irrelevant_ideal_in_every_degree() -> None:
    for cell in _record()["cells"]:
        numerators = cell["hilbert_numerator"]
        _same(nil.module_series_is_that_of_the_irrelevant_ideal(numerators), True)
        altered = {name: list(values) for name, values in numerators.items()}
        altered["radical"][-1] += 1
        _same(nil.module_series_is_that_of_the_irrelevant_ideal(altered), False)


def test_the_hilbert_function_from_a_numerator_counts_monomials() -> None:
    _same(nil.hilbert_function([1]), [math.comb(degree + 20, 20) for degree in nil.HILBERT_DEGREES])
    _same(nil.hilbert_function([1, -1]), [math.comb(degree + 19, 19) for degree in nil.HILBERT_DEGREES])


def test_the_hilbert_functions_at_the_two_basepoints_agree() -> None:
    minus, plus = (cell["hilbert_function"] for cell in _record()["cells"])
    _same(minus, plus)


def _set(orbit: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        next(cell for cell in record["cells"] if cell["orbit"] == orbit)[key] = value

    return mutate


def _altered(name: str, position: int) -> dict[str, list[int]]:
    functions = copy.deepcopy(_record()["cells"][0]["hilbert_function"])
    functions[name][position] += 1
    return functions


def _altered_numerator(name: str, position: int) -> dict[str, list[int]]:
    numerators = copy.deepcopy(_record()["cells"][0]["hilbert_numerator"])
    numerators[name][position] += 1
    return numerators


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "four linear forms": (_set("N-", "radical_linear_forms", 4), "radical_linear_forms"),
    "a linear form dropped": (_set("N+", "linear_forms", ["y(3)"]), "differ in number"),
    "five copies of one form": (_set("N-", "linear_forms", ["y(1)"] * 5), "differ from the five"),
    "the form of the other basepoint": (
        _set("N+", "linear_forms", ["2*y(12)+(i)*y(13)+(i)*y(17)", "y(7)", "y(6)", "y(5)", "y(3)"]),
        "differ from the five",
    ),
    "radical larger": (_set("N-", "radical_is_ideal_plus_linear_forms", False), "radical_is_ideal_plus"),
    "square not zero": (_set("N+", "radical_square_in_ideal", False), "radical_square_in_ideal"),
    "annihilator changed": (_set("N-", "annihilator", [5, 2]), "annihilator differs"),
    "embedded component radical": (
        _set("N+", "primary_components", [[4, 2, 2, True], [4, 4, 4, True], [5, 11, 11, True]]),
        "primary_components",
    ),
    "annihilator not prime": (_set("N-", "annihilator_is_prime", False), "annihilator_is_prime"),
    "annihilator not radical": (_set("N+", "annihilator_is_radical", False), "annihilator_is_radical"),
    "two minimal primes of the annihilator": (
        _set("N-", "annihilator_minimal_primes", 2),
        "annihilator_minimal_primes",
    ),
    "module flag flipped": (
        _set("N-", "nilradical_module_hilbert_function_is_that_of_annihilator_quotient", False),
        "nilradical_module_hilbert_function_is_that_of_annihilator_quotient",
    ),
    "hilbert value of the annihilator altered": (
        _set("N+", "hilbert_function", _altered("annihilator", 5)),
        "hilbert_function differs",
    ),
    "hilbert value of the radical altered": (
        _set("N-", "hilbert_function", _altered("radical", 11)),
        "hilbert_function differs",
    ),
    "hilbert numerator altered": (_set("N-", "hilbert_numerator", _altered_numerator("ideal", 2)), "numerator"),
    "hilbert data removed": (lambda record: record["cells"][0].pop("hilbert_numerator"), "missing"),
    "minimal primes changed": (_set("N-", "minimal_primes", [[5, 11]]), "minimal_primes"),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-quadric-nilradical/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = nil.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    _same(nil.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(nil.INPUTS))
    for name in nil.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(nil.WEIGHT_SLICE.read_bytes()).hexdigest())
