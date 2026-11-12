"""Signed-permutation sweep over the A5 fiber headers.

For every ordered pair of headers (a, b) with the same variable count, including a = b, search coordinate maps
t_i -> s_i t_pi(i) (pi a permutation, s_i = +-1) with span(J_a o sigma) = span(J_b) over F_p, then compare the G spans:
rank G_b, rank G_a o sigma, rank of the union. Permutations are pruned by a per-variable profile of J (monomial total
degree, exponent of the variable, coefficient up to sign); a profile that a span change could alter makes the pruning
heuristic, so an empty result for a multi-generator J is not a proof of absence. Prints one JSON line per hit and a
summary line per pair.
"""

from __future__ import annotations

import functools
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402


def field(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    if m is None:
        raise ValueError(f"header lacks {pattern}")
    return m.group(1)


def load(path: Path) -> tuple[int, list[str], list[dict], list[dict]]:
    t = path.read_text()
    p = int(field(r"ring r=(\d+),", t))
    names = field(r"ring r=\d+,\(([^)]*)\)", t).split(",")

    def parse(text: str) -> dict:
        poly: dict = {}
        for sign, body in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "").replace("\n", "")):
            coef, exps = 1, [0] * len(names)
            for f in body.split("*"):
                if re.fullmatch(r"\d+", f):
                    coef *= int(f)
                else:
                    v, _, e = f.partition("^")
                    exps[names.index(v)] += int(e) if e else 1
            m = tuple(exps)
            poly[m] = (poly.get(m, 0) + (-coef if sign == "-" else coef)) % p
        return {m: c for m, c in poly.items() if c}

    J = [parse(g) for g in field(r"ideal J=([^;]*);", t).split(",")]
    G = [parse(g) for g in field(r"ideal G=([^;]*);", t).split(",")]
    return p, names, J, G


def rank(rows: list[dict], p: int) -> int:
    piv: dict = {}
    for r0 in rows:
        r = dict(r0)
        while r:
            k = max(r)
            if k not in piv:
                inv = pow(r[k], -1, p)
                piv[k] = {m: v * inv % p for m, v in r.items()}
                break
            c = r[k]
            for m, v in piv[k].items():
                x = (r.get(m, 0) - c * v) % p
                if x:
                    r[m] = x
                else:
                    r.pop(m, None)
    return len(piv)


def apply(poly: dict, perm: tuple[int, ...], signs: tuple[int, ...], p: int) -> dict:
    """Substitute t_i -> s_i t_perm[i]: monomial exponent e_i moves to slot perm[i]."""
    out = {}
    for m, c in poly.items():
        new = [0] * len(m)
        sg = 1
        for i, e in enumerate(m):
            new[perm[i]] += e
            if signs[i] < 0 and e % 2:
                sg = -sg
        out[tuple(new)] = c if sg > 0 else (-c) % p
    return out


def profile(J: list[dict], i: int, p: int) -> tuple:
    return tuple(sorted(Counter((sum(m), m[i], min(c, p - c)) for g in J for m, c in g.items()).items()))


Context = tuple[int, list[str], list[dict], list[dict], list[dict], list[dict], int, int]


@functools.cache
def context(a: str, b: str) -> Context | None:
    """The headers of one ordered pair with the ranks of J_b and G_b, or None when the pair is not comparable."""
    p, na, Ja, Ga = load(Path(a))
    pb, nb, Jb, Gb = load(Path(b))
    if p != pb or len(na) != len(nb):
        return None
    return p, nb, Ja, Ga, Jb, Gb, rank(Jb, p), rank(Gb, p)


def permutations(ctx: Context) -> tuple[list[list[int]], list[tuple[int, ...]]]:
    """The profile choices of each variable and the permutations they admit."""
    p, na, Ja, _Ga, Jb, _Gb, _rJb, _rGb = ctx
    n = len(na)
    pa = [profile(Ja, i, p) for i in range(n)]
    pbp = [profile(Jb, i, p) for i in range(n)]
    choices = [[j for j in range(n) if pbp[j] == pa[i]] for i in range(n)]
    return choices, [perm for perm in itertools.product(*choices) if len(set(perm)) == n]


def hits(item: tuple[str, str, tuple[int, ...]]) -> list[str]:
    """The JSON lines of every J-preserving sign vector of one permutation."""
    a, b, perm = item
    ctx = context(a, b)
    if ctx is None:
        raise ValueError("pair is not comparable")
    p, nb, Ja, Ga, Jb, Gb, rJb, rGb = ctx
    n = len(nb)
    out = []
    for signs in itertools.product((1, -1), repeat=n):
        Js = [apply(g, perm, signs, p) for g in Ja]
        if len(Ja) == 1 == len(Jb) and Js[0].keys() != Jb[0].keys():
            continue
        if rank(Jb + Js, p) != rJb or rank(Js, p) != rJb:
            continue
        Gs = [apply(g, perm, signs, p) for g in Ga]
        rGs, rU = rank(Gs, p), rank(Gb + Gs, p)
        out.append(
            json.dumps(
                {
                    "a": Path(a).name,
                    "b": Path(b).name,
                    "perm": [nb[j] for j in perm],
                    "signs": signs,
                    "rank_Gb": rGb,
                    "rank_Ga_moved": rGs,
                    "rank_union": rU,
                    "G_spans_equal": rGb == rGs == rU,
                }
            )
        )
    return out


def main() -> None:
    files = sorted(Path(sys.argv[1]).glob("*.sing"))
    plans = []
    items: list[tuple[str, str, tuple[int, ...]]] = []
    for a in files:
        for b in files:
            ctx = context(str(a), str(b))
            if ctx is None:
                continue
            choices, perms = permutations(ctx)
            plans.append((a, b, choices, len(perms)))
            items += [(str(a), str(b), perm) for perm in perms]
    results = iter(parallel.ordered_map(hits, items, min_items=1))
    for a, b, choices, count in plans:
        found = 0
        for _ in range(count):
            for line in next(results):
                print(line, flush=True)
                found += 1
        print(
            json.dumps(
                {
                    "pair": [a.name, b.name],
                    "profile_choices": [len(c) for c in choices],
                    "permutations_tested": count,
                    "J_preserving_maps": found,
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
