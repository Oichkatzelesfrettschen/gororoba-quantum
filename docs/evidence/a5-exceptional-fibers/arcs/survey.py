"""Deterministic survey of arcs x(s) = Phi(w, rho, sigma, E, zeta) in V(J) through points of the slice.

Each arc is built from monomial parameter data with small integer coefficients (no random draws). For each arc the
leading coefficient vector F of (G_j(x(s))) at the minimal order is classified against V(P1), V(P2) and V(K2), and the
record keeps the base point x(0) so that the arcs sort by where they start.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from typing import Any

import arclib as A
import laurent as Lm
from arc_targets import TARGETS, Target, load_primes, ordered_map

TOP = 60
N = 16
COEFS = [(3, 5, 7, 11), (2, 3, -5, 7)]  # (W, R, S, Z)
E0 = 2


Job = tuple[int, int, int, int, int, tuple[int, int, int, int]]


class SurveyArc:
    """Callable classifying one monomial arc; the worker pool pickles it once, and its inputs load on the first call."""

    def __init__(self, target: Target) -> None:
        self.target = target
        self.state: tuple[Any, ...] | None = None

    def load(self) -> tuple[Any, ...]:
        if self.state is None:
            p = self.target.prime
            _, g_gens = A.load_slice(self.target)
            p1, p2, k2 = (A.load_yideal(t, p) for t in load_primes(self.target))
            self.state = (g_gens, p1, p2, k2)
        return self.state

    def __call__(self, job: Job) -> dict[str, object]:
        g_gens, p1, p2, k2 = self.load()
        p = self.target.prime
        a, b, c, d, k, (big_w, big_r, big_s, big_z) = job

        def mono(coef: int, val: int) -> Lm.L:
            return Lm.L.mono(coef, val, TOP, p) if val > 0 else Lm.L.const(coef, TOP, p)

        tag = {"w": (big_w, a), "rho": (big_r, b), "sig": (big_s, c), "zeta": (big_z, d), "E": (E0, k)}
        params = (Lm.L.mono(big_w, a, TOP, p), mono(big_r, b), mono(big_s, c), Lm.L.mono(E0, k, TOP, p), mono(big_z, d))
        try:
            xs = [x.to_series(N) for x in Lm.phi_laurent(self.target, *params)]
        except (ValueError, ZeroDivisionError) as exc:
            return {"tag": tag, "status": f"not-regular: {exc}"}
        base = [x.coeff(0) for x in xs]
        nu, vec, _ = A.leading_vector(g_gens, xs, N)
        if vec is None:
            return {"tag": tag, "status": f"G(x(s)) zero to order {N}", "base": base}
        if nu == 0:
            return {"tag": tag, "status": "base point off V(G)", "base": base}
        return {
            "tag": tag,
            "status": "ok",
            "base": base,
            "nu": nu,
            "F": vec,
            "P1": A.inside(p1, vec, p),
            "P2": A.inside(p2, vec, p),
            "K2": A.inside(k2, vec, p),
        }


def survey(target: Target) -> list[dict[str, object]]:
    """The 540 arcs: valuations a in {1,2}, b, c, d in {0,1,2}, k in {-2..2} and two coefficient sets."""
    jobs: list[Job] = [
        (a, b, c, d, k, coefs)
        for a, b, c, d, k in itertools.product([1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [-2, -1, 0, 1, 2])
        for coefs in COEFS
    ]
    return list(ordered_map(SurveyArc(target), jobs))


def tally(rows: list[dict[str, object]]) -> Counter[str]:
    cnt: Counter[str] = Counter()
    for r in rows:
        if r["status"] != "ok":
            cnt[str(r["status"])[:30]] += 1
        else:
            cnt[("P1" if r["P1"] else "-") + ("P2" if r["P2"] else "-") + ("K2" if r["K2"] else "notK2")] += 1
    return cnt


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    rows = survey(target)
    (target.directory / "survey.json").write_text(json.dumps(rows) + "\n")
    print(sum(tally(rows).values()), dict(tally(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
