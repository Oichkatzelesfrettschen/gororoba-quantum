"""Certify an arc family against a component of sqrt(K2) with an independent exact numeric implementation.

The symbolic limit vector printed by gen_family.py (Singular) is compared, on a deterministic parameter grid, with the
limit of the same arc built by exact truncated series over F_p (laurent.py, python-flint). Each grid point checks the
order of G(x(s)), the limit vector, containment in the target prime, the other prime and K2, and every J generator on
the first six arcs. The Jacobian rank of the symbolic map is taken at five fixed points.

usage: certify.py TARGET P1|P2 [OUT.json]    (reads families/ of the target directory)
"""

from __future__ import annotations

import dataclasses
import itertools
import json
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import arclib as A
import laurent as Lm
import symfam as SF
from arc_targets import TARGETS, Target, load_primes, ordered_map
from gen_family import P1_FAMILY, P2_FAMILY, Family

GRID = (
    [1, 3, 7],  # W
    [2, 5, 13],  # R
    [1, 6, 19],  # S
    [4, 11],  # Z
    [2, 3, 5, 10, 23],  # E, or E1 for the near family
)
RANK_POINTS = [(3, 5, 7, 11, 2), (1, 2, 3, 4, 5), (7, 13, 1, 11, 10), (2, 9, 4, 6, 3), (5, 3, 8, 1, 7)]
TOP = 80
J_CHECKED_ARCS = 6
FAILURE_KEYS = ("not_regular", "off_origin", "J_nonzero", "order", "symbolic", "not_target", "not_K2", "in_other")


def grid_points() -> list[tuple[int, ...]]:
    return list(itertools.product(*GRID))


def family_arc(target: Target, fam: Family, pt: Sequence[int]) -> list[Lm.L]:
    """The arc x(s) = Phi(...) of the family at the parameter point (W, R, S, Z, E)."""
    p = target.prime
    big_w, big_r, big_s, big_z, big_e = pt
    w = Lm.L.mono(big_w, fam.a, TOP, p)
    zeta = Lm.L.mono(big_z, fam.d, TOP, p)
    if fam.coords == "pq":
        half = pow(2, -1, p)
        rho = (Lm.L.mono(big_r, fam.b, TOP, p) + Lm.L.mono(big_s, fam.c, TOP, p)) * half
        sig = (Lm.L.mono(big_r, fam.b, TOP, p) - Lm.L.mono(big_s, fam.c, TOP, p)) * half
    else:
        rho = Lm.L.mono(big_r, fam.b, TOP, p)
        sig = Lm.L.mono(big_s, fam.c, TOP, p)
    if fam.etype[0] == "k":
        e = Lm.L.mono(big_e, fam.etype[1], TOP, p)
    else:
        e = Lm.L.const(fam.etype[1], TOP, p) + Lm.L.mono(big_e, fam.etype[2], TOP, p)
    return Lm.phi_laurent(target, w, rho, sig, e, zeta)


def parse_family_log(text: str, p: int) -> tuple[int, dict[int, SF.SymPoly]]:
    """(nu, nonzero symbolic coordinates) of a family log."""
    found = re.search(r"NU (\d+)", text)
    if found is None:
        raise ValueError("the family log has no order NU")
    return int(found.group(1)), SF.load_fj(text, p)


class PointCheck:
    """Callable checking one grid point; the worker pool pickles it once, and its inputs load on the first call."""

    def __init__(self, target: Target, fam: Family, comp: str, log_text: str) -> None:
        self.target = target
        self.fam = fam
        self.comp = comp
        self.log_text = log_text
        self.state: tuple[Any, ...] | None = None

    def load(self) -> tuple[Any, ...]:
        if self.state is None:
            p = self.target.prime
            nu_sym, fj = parse_family_log(self.log_text, p)
            _, g_gens = A.load_slice(self.target)
            p1_text, p2_text, k2_text = load_primes(self.target)
            p1, p2, k2 = (A.load_yideal(t, p) for t in (p1_text, p2_text, k2_text))
            tgt, oth = (p1, p2) if self.comp == "P1" else (p2, p1)
            self.state = (nu_sym, fj, g_gens, tgt, oth, k2)
        return self.state

    def __call__(self, pt: tuple[int, ...]) -> dict[str, int]:
        """Failure flags of one grid point, keyed as in the certificate."""
        nu_sym, fj, g_gens, tgt, oth, k2 = self.load()
        p = self.target.prime
        bad = dict.fromkeys(FAILURE_KEYS, 0)
        n_prec = nu_sym + 4
        try:
            xs = [x.to_series(n_prec) for x in family_arc(self.target, self.fam, pt)]
        except (ValueError, ZeroDivisionError):
            bad["not_regular"] = 1
            return bad
        if any(x.coeff(0) for x in xs):
            bad["off_origin"] = 1
            return bad
        nu, vec, _ = A.leading_vector(g_gens, xs, n_prec)
        if nu != nu_sym or vec is None:
            bad["order"] = 1
            return bad
        if self.fam.etype[0] == "k":
            vec = [x * pow(pt[4], self.fam.n, p) % p for x in vec]
        bad["symbolic"] = int(vec != SF.vector(fj, pt, p))
        bad["not_target"] = int(not A.inside(tgt, vec, p))
        bad["not_K2"] = int(not A.inside(k2, vec, p))
        bad["in_other"] = int(A.inside(oth, vec, p))
        return bad


@dataclasses.dataclass(frozen=True)
class RankAt:
    """Rank of the symbolic limit map's Jacobian at one parameter point."""

    fj: Any
    p: int

    def __call__(self, pt: tuple[int, ...]) -> int:
        return int(SF.jacobian_rank(self.fj, pt, self.p))


def certify(
    target: Target,
    fam: Family,
    comp: str,
    log_text: str,
    points: Iterable[tuple[int, ...]] | None = None,
    log_name: str | None = None,
) -> dict[str, object]:
    """Numeric certificate of one family for the component `comp` (P1 or P2) of sqrt(K2).

    The order of G(x(s)) is read off the family log; every J generator is checked on the first six regular arcs.
    """
    p = target.prime
    checker = PointCheck(target, fam, comp, log_text)
    nu_sym, fj, *_ = checker.load()
    j_gens, _ = A.load_slice(target)
    n_prec = nu_sym + 4
    pts = list(points) if points is not None else grid_points()
    bad = dict.fromkeys(FAILURE_KEYS, 0)
    j_checked = 0
    for pt in pts:
        try:
            xs = [x.to_series(n_prec) for x in family_arc(target, fam, pt)]
        except (ValueError, ZeroDivisionError):
            continue
        if j_checked >= J_CHECKED_ARCS:
            break
        j_checked += 1
        if not any(x.coeff(0) for x in xs):
            bad["J_nonzero"] += sum(1 for g in j_gens if A.eval_poly(g, xs, n_prec).val() is not None)
    flags = ordered_map(checker, pts)
    for flag in flags:
        for key, value in flag.items():
            bad[key] += value
    ranks = {str(pt): rank for pt, rank in zip(RANK_POINTS, ordered_map(RankAt(fj, p), RANK_POINTS), strict=True)}
    return {
        "family_log": log_name,
        "component": comp,
        "order_nu": nu_sym,
        "points_checked": len(pts) - bad["not_regular"],
        "grid_size": len(pts),
        "failures": bad,
        "jacobian_rank": ranks,
        "nonzero_coordinates": sorted(fj),
    }


COMPONENTS = {"P2": (P2_FAMILY, "numeric_P2.json"), "P1": (P1_FAMILY, "numeric_P1.json")}


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    fam, default_out = COMPONENTS[argv[2]]
    log = target.directory / "families" / f"fam_{fam.tag}.log"
    res = certify(target, fam, argv[2], log.read_text(), log_name=f"families/{log.name}")
    out = Path(argv[3]) if len(argv) > 3 else target.directory / default_out
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
