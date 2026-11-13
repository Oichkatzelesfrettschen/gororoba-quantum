"""Arc certificate of the E8-bar fiber components over Q(i): parsing, ranks, spans, reduction and the record rules."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-char0-transfer"))

import e8_fiber_components_qi as components  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _pair(real: int, imaginary: int = 0) -> tuple[Fraction, Fraction]:
    return Fraction(real), Fraction(imaginary)


def test_singular_output_parses_to_gaussian_coefficients() -> None:
    poly = components.parse_polynomial("(2*I-2)*pW*pR*pE^3+(-1/2*I)*pW^2-4*pZ")
    expected = {
        (1, 1, 0, 0, 3): (Fraction(-2), Fraction(2)),
        (2, 0, 0, 0, 0): (Fraction(0), Fraction(-1, 2)),
        (0, 0, 0, 1, 0): (Fraction(-4), Fraction(0)),
    }
    _same(components.coefficients(poly), expected)
    _same(components.parse_polynomial("0").is_zero, True)


def test_rank_over_the_gaussian_field_sees_dependence_that_needs_i() -> None:
    dependent = [[_pair(1), _pair(0, 1)], [_pair(0, 1), _pair(-1)]]
    independent = [[_pair(1), _pair(0, 1)], [_pair(1), _pair(0, -1)]]
    _same(
        [components.complex_rank(dependent), components.complex_rank(independent), components.complex_rank([])],
        [1, 2, 0],
    )


def test_cone_rank_and_span_of_a_veronese_surface_and_of_a_line() -> None:
    # (W^2, W R, R^2, 0, ...) is the cone over a conic: dimension 2, span 3. (W, W, 0, ...) is a line: 1 and 1.
    conic = [components.parse_polynomial(text) for text in ("pW^2", "pW*pR", "pR^2", "0")]
    line = [components.parse_polynomial(text) for text in ("pW", "pW", "0", "0")]
    point = (3, 5, 7, 11, 2)
    _same((components.cone_rank(conic, point), components.complex_rank(components.span_rows(conic))), (2, 3))
    _same((components.cone_rank(line, point), components.complex_rank(components.span_rows(line))), (1, 1))
    joint = components.complex_rank(components.span_rows(conic) + components.span_rows(line))
    _same(joint, 3)


def test_reduction_sends_i_to_the_root_and_drops_vanishing_terms() -> None:
    poly = components.parse_polynomial("(2*I)*pW^2+(32009)*pR+(1/2)*pE")
    reduced = components.reduce_polynomial(poly, 32009, 10754)
    _same(reduced, {(2, 0, 0, 0, 0): 21508, (0, 0, 0, 0, 1): 16005})


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    record = json.loads(components.RECORD.read_text(encoding="utf-8"))
    _same(
        (record["pass"], components.verdict(record), [t["slug"] for t in record["targets"]]),
        (True, [], ["e8-nm", "e8-np"]),
    )

    def family(target: dict, name: str) -> dict:
        return next(row for row in target["families"] if row["family"] == name)

    changes = (
        lambda t: family(t, "order_five").update(cone_ranks=[4, 4]),
        lambda t: family(t, "first_order").update(order=1),
        lambda t: t.update(joint_span_dimension=family(t, "order_five")["span_dimension"]),
        lambda t: family(t, "first_order")["reduction"][0].update(coordinates_that_differ=[1]),
        lambda t: t["phi_identity"]["arc"].update(nonzero=1),
        lambda t: t.update(quadric_ideal_minimal_primes=[[5, 11, 9]]),
        lambda t: family(t, "order_five_recentered_at_2").update(order=5, cone_ranks=[5, 5]),
    )
    for change in changes:
        mutated = json.loads(json.dumps(record))
        change(mutated["targets"][0])
        if components.verdict(mutated) == []:
            raise AssertionError("a mutated record passes")
