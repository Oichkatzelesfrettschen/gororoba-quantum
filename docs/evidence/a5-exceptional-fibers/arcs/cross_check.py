"""Ties of an E8-bar -> N+ target to the E8-bar -> N- target at the same prime.

compare: are the minimal primes and the K2 ideal of the N+ target the same ideals as those of the N- target?
cross_control: limits of the N+ certified families against the primes and K2 of both targets. The N+ limits satisfy the
N+ ideals (certify.py); failing the N- P1 and K2 shows that the membership test separates the two slices.
"""

from __future__ import annotations

import itertools
import json
from typing import Any

import arclib as A
from arc_targets import Target, load_primes, ordered_map
from certify import GRID, family_arc
from gen_family import P1_FAMILY, P2_FAMILY, Family

IDEALS = ("P1", "P2", "K2")


class CrossPoint:
    """Callable returning the membership flags of the limit at one grid point of a family; loads on the first call."""

    def __init__(self, plus: Target, minus: Target, fam: Family) -> None:
        self.plus = plus
        self.minus = minus
        self.fam = fam
        self.state: tuple[Any, ...] | None = None

    def load(self) -> tuple[Any, ...]:
        if self.state is None:
            p = self.plus.prime
            _, g_gens = A.load_slice(self.plus)
            own = dict(zip(IDEALS, (A.load_yideal(t, p) for t in load_primes(self.plus)), strict=True))
            oth = dict(zip(IDEALS, (A.load_yideal(t, p) for t in load_primes(self.minus)), strict=True))
            self.state = (g_gens, own, oth)
        return self.state

    def __call__(self, pt: tuple[int, ...]) -> list[str]:
        g_gens, own, oth = self.load()
        p = self.plus.prime
        nu_want = self.fam.n
        n_prec = nu_want + 4
        xs = [x.to_series(n_prec) for x in family_arc(self.plus, self.fam, pt)]
        nu, vec, _ = A.leading_vector(g_gens, xs, n_prec)
        if nu != nu_want or vec is None:
            raise RuntimeError(f"{self.fam.tag}: order {nu} at {pt}, expected {nu_want}")
        return [
            f"in_{tag}_{k}" for tag, ids in (("own", own), ("other", oth)) for k in IDEALS if A.inside(ids[k], vec, p)
        ]


def cross_control(plus: Target, minus: Target) -> dict[str, dict[str, int]]:
    """Counts over the 270 grid points of the P1 and P2 families of the N+ target."""
    res: dict[str, dict[str, int]] = {}
    for name, fam in (("P1_near_e-1", P1_FAMILY), ("P2_first_order", P2_FAMILY)):
        cnt = {"points": 0}
        for tag in ("own", "other"):
            for k in IDEALS:
                cnt[f"in_{tag}_{k}"] = 0
        for hits in ordered_map(CrossPoint(plus, minus, fam), list(itertools.product(*GRID))):
            cnt["points"] += 1
            for key in hits:
                cnt[key] += 1
        res[name] = cnt
    return res


def dump(res: dict[str, dict[str, int]]) -> str:
    return json.dumps(res, indent=1) + "\n"
