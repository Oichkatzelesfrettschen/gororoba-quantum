"""Parse the symbolic limit vectors printed by gen_family.py (Singular string output) and evaluate them mod p."""

from __future__ import annotations

import re
from collections.abc import Iterable

from arc_targets import NGEN
from flint import nmod_mat

VARS = "WRSZE"
SymPoly = dict[tuple[int, ...], int]


def parse_sing_poly(text: str, p: int) -> SymPoly:
    """A Singular polynomial in W, R, S, Z, E as {exponent tuple: coefficient mod p}."""
    text = re.sub(r"\s", "", text)
    text = re.sub(r"(?<!^)-", "+-", text)
    terms: SymPoly = {}
    for t in text.split("+"):
        if not t:
            continue
        found = re.fullmatch(r"(-?)(\d*)((?:[WRSZE]\d*)*)", t)
        if not found:
            raise ValueError(f"cannot parse term {t!r}")
        sign = -1 if found.group(1) else 1
        coef = int(found.group(2)) if found.group(2) else 1
        ex = [0] * len(VARS)
        for v, e in re.findall(r"([WRSZE])(\d*)", found.group(3)):
            ex[VARS.index(v)] += int(e) if e else 1
        key = tuple(ex)
        terms[key] = (terms.get(key, 0) + sign * coef) % p
    return {k: v for k, v in terms.items() if v}


def load_fj(logtext: str, p: int) -> dict[int, SymPoly]:
    """{j: polynomial} from the 'FJ j polynomial' lines of a family log."""
    return {int(m.group(1)): parse_sing_poly(m.group(2), p) for m in re.finditer(r"^FJ (\d+) (.*)$", logtext, re.M)}


def ev(poly: SymPoly, pt: Iterable[int], p: int) -> int:
    tot = 0
    for ex, c in poly.items():
        t = c
        for v, e in zip(pt, ex, strict=True):
            if e:
                t = t * pow(v, e, p) % p
        tot = (tot + t) % p
    return tot


def deriv(poly: SymPoly, i: int, p: int) -> SymPoly:
    out: SymPoly = {}
    for ex, c in poly.items():
        if ex[i]:
            e2 = list(ex)
            e2[i] -= 1
            out[tuple(e2)] = (out.get(tuple(e2), 0) + c * ex[i]) % p
    return {k: v for k, v in out.items() if v}


def vector(fj: dict[int, SymPoly], pt: tuple[int, ...], p: int) -> list[int]:
    """The limit vector F(pt) in y(1..21)."""
    return [ev(fj[j], pt, p) if j in fj else 0 for j in range(1, NGEN + 1)]


def jacobian_rank(fj: dict[int, SymPoly], pt: tuple[int, ...], p: int, cols: Iterable[int] = range(5)) -> int:
    """Rank over F_p of the 21 x len(cols) Jacobian of u -> F(u) at pt."""
    cols = list(cols)
    rows = [[ev(deriv(fj[j], i, p), pt, p) if j in fj else 0 for i in cols] for j in range(1, NGEN + 1)]
    return int(nmod_mat(NGEN, len(cols), [x for r in rows for x in r], p).rank())
