"""Arithmetic structure of retained numbers of the A_5 fiber cones: reduced Hilbert numerators, the component
identity of the E8-bar numerator, and the character split of the last jump of the truncated-rank ladders.

    $PYTHON docs/evidence/a5-exceptional-fibers/coefficient-structure/fiber_coefficients.py [OUT.json]

Every input is a retained number: the first Hilbert numerators of docs/evidence/a5-kernel-attachments/
weight-slice-fiber-relations-result.json and the block splits that ledger rows A5-244 and A5-269 record. The script
proves no geometric statement; it checks polynomial and counting identities and exits 1 when one fails.
"""

from __future__ import annotations

import json
import sys
from itertools import product
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = HERE.parents[1] / "a5-kernel-attachments" / "weight-slice-fiber-relations-result.json"
SUCCESSOR = HERE.parents[1] / "a5-kernel-attachments" / "weight-slice-modular-cells-result.json"

Poly = list[int]


def mul(a: Poly, b: Poly) -> Poly:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def add(*polys: Poly) -> Poly:
    out = [0] * max(len(p) for p in polys)
    for p in polys:
        for i, x in enumerate(p):
            out[i] += x
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def scale(c: int, a: Poly) -> Poly:
    return [c * x for x in a]


def power(a: Poly, n: int) -> Poly:
    out = [1]
    for _ in range(n):
        out = mul(out, a)
    return out


def divide_by_one_minus_t(a: Poly, times: int) -> Poly:
    """a / (1 - t)^times, raising ValueError when the division leaves a remainder."""
    for _ in range(times):
        quotient, carry = [], 0
        for x in a:
            carry += x
            quotient.append(carry)
        if quotient[-1] != 0:
            raise ValueError("numerator not divisible by 1 - t")
        a = quotient[:-1]
    return a


ONE_MINUS_T = [1, -1]


def reduced_numerators() -> list[dict[str, object]]:
    rows = []
    cells = json.loads(RECORD.read_text())["cells"] + json.loads(SUCCESSOR.read_text())["cells"]
    for cell in cells:
        hilbert = cell["hilbert"]
        if hilbert is None:
            continue
        generators, dimension = cell["generator_count"], hilbert["affine_dimension"]
        reduced = divide_by_one_minus_t(list(hilbert["first_numerator"]), generators - dimension)
        rows.append(
            {
                "incidence": cell["incidence"],
                "field": cell["field"],
                "generators": generators,
                "codimension": generators - dimension,
                "reduced_numerator": reduced,
                "sum_equals_multiplicity": sum(reduced) == hilbert["multiplicity"],
                "h2_from_relations": comb(generators + 1, 2) - cell["relation_count"],
                "h2_from_numerator": hilbert_function(reduced, dimension, 2),
            }
        )
    return rows


def perturbed_numerator_rejected() -> bool:
    """Known-bad control: a retained numerator with its constant term raised by one no longer divides by 1 - t."""
    cell = next(c for c in json.loads(RECORD.read_text())["cells"] if c["hilbert"] is not None)
    numerator = list(cell["hilbert"]["first_numerator"])
    numerator[0] += 1
    try:
        divide_by_one_minus_t(numerator, 1)
    except ValueError:
        return True
    return False


def hilbert_function(reduced: Poly, dimension: int, degree: int) -> int:
    return sum(c * comb(degree - k + dimension - 1, dimension - 1) for k, c in enumerate(reduced) if k <= degree)


def e8_component_identity(reduced: Poly) -> dict[str, object]:
    """Numerators over (1 - t)^5 of the pieces that rows A5-503, A5-502, A5-501 and A5-454 describe:
    the degree-11 prime (second numerator 1 + 7t + 3t^2), the scroll S(1,1,2) of affine dimension 4, their
    intersection, a linear space of dimension 3, and the nilradical module with the Hilbert function of the
    irrelevant ideal of a quadric of affine dimension 4."""
    prime_11 = [1, 7, 3]
    scroll = mul(ONE_MINUS_T, [1, 3])
    plane = power(ONE_MINUS_T, 2)
    nilradical = mul(ONE_MINUS_T, add([1, 1], scale(-1, power(ONE_MINUS_T, 4))))
    total = add(prime_11, scroll, scale(-1, plane), nilradical)
    return {
        "prime_11": prime_11,
        "scroll": scroll,
        "plane": plane,
        "nilradical": nilradical,
        "sum": total,
        "equals_reduced_numerator": total == reduced,
    }


Character = tuple[int, int]
CHI = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
BLOCK = {v: k for k, v in CHI.items()}


def nodal_conic_characters(degree: int, node: tuple[Character, Character]) -> list[int]:
    """Characters of the degree-d monomials of k[a, b, c] / (b c): a of character 0, b and c of the characters node."""
    counts = [0, 0, 0, 0]
    counts[0] += 1  # a^d
    for j in range(1, degree + 1):
        for ch in node:
            counts[BLOCK[(ch[0] * j % 2, ch[1] * j % 2)]] += 1
    return counts


def tensor(left: list[int], right: list[int]) -> list[int]:
    counts = [0, 0, 0, 0]
    for (i, x), (j, y) in product(enumerate(left), enumerate(right)):
        a, b = CHI[i], CHI[j]
        counts[BLOCK[((a[0] + b[0]) % 2, (a[1] + b[1]) % 2)]] += x * y
    return counts


def closed_form_two_rulings(d: int) -> list[int]:
    block0 = (d + 1) ** 2 if d % 2 == 0 else d * d
    block1 = d * (d + 1)
    rest = (2 * d + 1) ** 2 - block0 - block1
    return [block0, block1, rest // 2, rest // 2]


def closed_form_one_ruling(d: int) -> list[int]:
    return [d + 1, d, 0, 0] if d % 2 == 0 else [d, d + 1, 0, 0]


# (ledger row, fiber, degree, measured split of the last jump by character block)
MEASURED = [
    ("A5-244", "X-", 2, [9, 6, 5, 5]),
    ("A5-244", "X-", 3, [9, 12, 14, 14]),
    ("A5-244", "X-", 4, [25, 20, 18, 18]),
    ("A5-244", "X-", 6, [49, 42, 39, 39]),
    ("A5-244", "Iso", 6, [49, 42, 39, 39]),
    ("A5-269", "E8-bar -> VB", 4, [5, 4, 0, 0]),
    ("A5-269", "E8-bar -> VB", 5, [5, 6, 0, 0]),
    ("A5-269", "E8-bar -> VB", 6, [7, 6, 0, 0]),
    ("A5-269", "E8-bar -> VB", 7, [7, 8, 0, 0]),
]


def add_characters(a: Character, b: Character) -> Character:
    return ((a[0] + b[0]) % 2, (a[1] + b[1]) % 2)


def polynomial_characters(degree: int, variables: tuple[Character, ...]) -> list[int]:
    """Characters of the monomials of the given degree in variables of the given characters."""
    counts = [0, 0, 0, 0]
    if degree < 0:
        return counts
    for exponents in product(range(degree + 1), repeat=len(variables)):
        if sum(exponents) != degree:
            continue
        total: Character = (0, 0)
        for exponent, ch in zip(exponents, variables, strict=True):
            if exponent % 2:
                total = add_characters(total, ch)
        counts[BLOCK[total]] += 1
    return counts


def quadric_quotient_characters(degree: int, variables: tuple[Character, ...], relation: Character) -> list[int]:
    """Characters of degree-d forms modulo one quadric of the given character that is a nonzero divisor."""
    whole = polynomial_characters(degree, variables)
    lower = polynomial_characters(degree - 2, variables)
    out = list(whole)
    for block, count in enumerate(lower):
        out[BLOCK[add_characters(CHI[block], relation)]] -= count
    return out


def veronese_characters(degree: int, parameters: tuple[Character, Character]) -> list[int]:
    """Characters of the degree-d part of k[u^2, u v, v^2], the smooth conic with the action linear on (u, v)."""
    return polynomial_characters(2 * degree, parameters)


def character_model(max_degree: int) -> dict[str, object]:
    first = (CHI[1], CHI[1])
    second = (CHI[2], CHI[3])
    r1 = (CHI[0], CHI[1], CHI[1])
    r2 = (CHI[0], CHI[2], CHI[3])
    degrees = []
    ok = True
    for d in range(1, max_degree + 1):
        one = nodal_conic_characters(d, first)
        other = nodal_conic_characters(d, second)
        two = tensor(one, other)
        match = (
            one == closed_form_one_ruling(d)
            and two == closed_form_two_rulings(d)
            # any quadric of trivial character in (a, b, c) gives the character of R1, the smooth a^2 - b c included
            and one == quadric_quotient_characters(d, r1, CHI[0])
            # the relation of R2 has character chi_1, and x y is the one quadratic monomial of that character
            and other == quadric_quotient_characters(d, r2, CHI[1])
        )
        ok = ok and match
        degrees.append({"degree": d, "one_conic": one, "two_conics": two, "equals_closed_forms": match})
    measured = []
    for row, fiber, d, split in MEASURED:
        model = (
            nodal_conic_characters(d, first)
            if "VB" in fiber
            else tensor(nodal_conic_characters(d, first), nodal_conic_characters(d, second))
        )
        measured.append(
            {"ledger": row, "fiber": fiber, "degree": d, "measured": split, "model": model, "equal": model == split}
        )
        ok = ok and model == split
    chi1_quadrics = sum(1 for i in range(3) for j in range(i, 3) if add_characters(r2[i], r2[j]) == CHI[1])
    # known-bad control: the smooth conic with the action linear on its parameters misses the measured odd degrees
    control = [
        {"degree": d, "veronese": veronese_characters(d, (CHI[0], CHI[1])), "measured": split}
        for row, fiber, d, split in MEASURED
        if "VB" in fiber and d % 2
    ]
    rejected = bool(control) and all(c["veronese"] != c["measured"] for c in control)
    return {
        "degrees": degrees,
        "measured": measured,
        "all_equal": ok,
        "quadratic_monomials_of_character_chi_1_in_r2": chi1_quadrics,
        "control_veronese_linear_action": control,
        "control_rejected": rejected,
    }


def main() -> int:
    numerators = reduced_numerators()
    e8 = next(r for r in numerators if r["incidence"] == "E8bar->N-" and r["field"] == "Q(i)")
    identity = e8_component_identity(list(e8["reduced_numerator"]))  # type: ignore[call-overload]
    characters = character_model(12)
    record: dict[str, object] = {
        "reduced_numerators": numerators,
        "e8_component_identity": identity,
        "last_jump_characters": characters,
    }
    good = (
        all(r["sum_equals_multiplicity"] and r["h2_from_relations"] == r["h2_from_numerator"] for r in numerators)
        and bool(identity["equals_reduced_numerator"])
        and bool(characters["all_equal"])
        and bool(characters["control_rejected"])
        and characters["quadratic_monomials_of_character_chi_1_in_r2"] == 1
        and perturbed_numerator_rejected()
    )
    record["control_perturbed_numerator_rejected"] = perturbed_numerator_rejected()
    record["pass"] = good
    text = json.dumps(record, indent=1) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text)
    print("CELLS with Hilbert data", len(numerators))
    seen: set[tuple[str, str]] = set()
    for r in numerators:
        key = (str(r["incidence"]).split("->")[0], str(r["reduced_numerator"]))
        if key not in seen:
            seen.add(key)
            print(
                "NUMERATOR",
                key[0],
                "codimension",
                r["codimension"],
                "reduced",
                r["reduced_numerator"],
                "h2",
                r["h2_from_relations"],
            )
    print("E8 COMPONENT IDENTITY", identity["sum"], "equal", identity["equals_reduced_numerator"])
    print("CHARACTERS degrees 1..12 equal", characters["all_equal"], "measured rows", len(MEASURED))
    print("verdict:", "PASS" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
