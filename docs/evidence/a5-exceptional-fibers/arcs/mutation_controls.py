"""Negative controls: the certificate checks must fail on corrupted inputs.

The baseline is the order-5 arc of the P1 family at (W, R, S, Z, E1) = (3, 5, 7, 11, 2). Three corruptions follow:
t9 plus s^3 (the arc leaves V(J)), the lowest-degree coefficient of G_11 plus one (the limit leaves V(P1)), and the
conic point e0 = 2 in place of -1 (the limit leaves V(P1) for V(P2)).
"""

from __future__ import annotations

import json
import sys

import arclib as A
import laurent as Lm
from arc_targets import TARGETS, Target, load_primes

TOP = 80
N = 9
POINT = (3, 5, 7, 11, 2)
CORRUPT_GENERATOR = 10  # G_11, zero-based


def mutation_controls(target: Target) -> dict[str, dict[str, object]]:
    p = target.prime
    half = pow(2, -1, p)
    j_gens, g_gens = A.load_slice(target)
    p1, p2, k2 = (A.load_yideal(t, p) for t in load_primes(target))
    big_w, big_r, big_s, big_z, big_e1 = POINT
    w = Lm.L.mono(big_w, 2, TOP, p)
    zeta = Lm.L.mono(big_z, 1, TOP, p)
    rho = (Lm.L.mono(big_r, 1, TOP, p) + Lm.L.mono(big_s, 1, TOP, p)) * half
    sig = (Lm.L.mono(big_r, 1, TOP, p) - Lm.L.mono(big_s, 1, TOP, p)) * half
    e = Lm.L.const(-1, TOP, p) + Lm.L.mono(big_e1, 2, TOP, p)
    xs = [x.to_series(N) for x in Lm.phi_laurent(target, w, rho, sig, e, zeta)]

    def j_residues(arc: list[A.Series]) -> int:
        return sum(1 for q in j_gens if A.eval_poly(q, arc, N).val() is not None)

    out: dict[str, dict[str, object]] = {}
    nu, vec, _ = A.leading_vector(g_gens, xs, N)
    if vec is None:
        raise RuntimeError("the baseline arc has no order")
    out["baseline"] = {
        "nu": nu,
        "inP1": A.inside(p1, vec, p),
        "inP2": A.inside(p2, vec, p),
        "inK2": A.inside(k2, vec, p),
        "J_residues": j_residues(xs),
    }
    xs_a = list(xs)
    xs_a[8] = xs_a[8] + A.Series.mono(1, 3, N, p)
    out["mutate_t9"] = {"J_residues": j_residues(xs_a)}
    g_b = [dict(g) for g in g_gens]
    low = min(g_b[CORRUPT_GENERATOR], key=lambda ex: sum(ex))
    g_b[CORRUPT_GENERATOR][low] = (g_b[CORRUPT_GENERATOR][low] + 1) % p
    nu_b, vec_b, _ = A.leading_vector(g_b, xs, N)
    out["mutate_G11"] = {
        "nu": nu_b,
        "inP1": A.inside(p1, vec_b, p) if vec_b else None,
        "inK2": A.inside(k2, vec_b, p) if vec_b else None,
    }
    e2 = Lm.L.const(2, TOP, p) + Lm.L.mono(big_e1, 2, TOP, p)
    xs_c = [x.to_series(N) for x in Lm.phi_laurent(target, w, rho, sig, e2, zeta)]
    nu_c, vec_c, _ = A.leading_vector(g_gens, xs_c, N)
    if vec_c is None:
        raise RuntimeError("the e0 = 2 arc has no order")
    out["E_base_2"] = {
        "nu": nu_c,
        "inP1": A.inside(p1, vec_c, p),
        "inP2": A.inside(p2, vec_c, p),
        "inK2": A.inside(k2, vec_c, p),
    }
    return out


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    res = mutation_controls(target)
    (target.directory / "mutation_controls.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
