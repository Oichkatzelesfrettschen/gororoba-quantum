"""Arc certificate that the reduced exceptional fiber over the base point is all of P^2, for one incidence at one prime.

usage: xarc_certify.py PRIME SLUG     (SLUG is xp-nm for X+ -> N- or xm-np for X- -> N+)

Reads the slice (J, G) of the header of SLUG at PRIME, the symbolic limit map written by sing/pPRIME/SLUG_limit.sing
(logs/pPRIME/SLUG_limit.log), and the symbolic identity J(Phi) = 0 of logs/pPRIME/SLUG_phi.log. Rebuilds every arc with
exact truncated series over F_PRIME in python-flint, a code path separate from Singular, and writes
records/pPRIME/SLUG/result.json and details.json. The prime and the root of -1 come from the header.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy
import xarc_series as SR
from xarc_common import FLIPPED_GENERATOR, HERE, INCIDENCES, SIGN9, T9_KEY, Header, Poly, inv, load_headers, prime_dir

sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))
import parallel  # noqa: E402

TOP = 12
GRID = ([1, 3, 7, 11, 19], [2, 5, 13, 21, 34], [1, 6], [0, 4])  # W, R, S, K: 5*5*2*2 = 100 points
RANK_POINTS = [(3, 5, 7, 11), (4, 9, 2, 6), (7, 13, 1, 11), (5, 3, 8, 2), (6, 10, 4, 9)]
PHI_POINTS = list(itertools.product([0, 1, 5], [0, 2, 9], [0, 3], [0, 4, 10]))  # 36 parameter points of Phi
HIT_TARGETS = list(itertools.product(range(10), range(10)))  # 100 projective targets (1 : a : b)
G2_SQUARE = (0, 2, 0, 0, 0, 0, 0)  # exponent vector of t2^2
# The loops below have 5 to 100 items that each cost milliseconds to seconds: map them from 5 items on.
MIN_ITEMS = 5
W_, R_, S_, K_ = sympy.symbols("W R S K")


@dataclass(frozen=True)
class Slice:
    """The data of one incidence at one prime that every arc replay needs."""

    prime: int
    sgn: int
    j: tuple[Poly, ...]
    g: tuple[Poly, ...]


def slice_of(h: Header) -> Slice:
    return Slice(h.prime, SIGN9[h.slug], h.j, h.g)


def parse_limit_log(path: Path) -> dict[int, list[sympy.Expr]]:
    """{j: [coefficient of s^0..s^3 of G_j(x(s)) as a polynomial in W, R, S, K]} from the Singular log."""
    return parse_limit_text(path.read_text())


def parse_limit_text(text: str) -> dict[int, list[sympy.Expr]]:
    out: dict[int, list[sympy.Expr]] = {}
    cur = None
    for line in text.splitlines():
        head = re.match(r"G (\d) \(x\(s\)\) coefficients", line)
        if head:
            cur = int(head.group(1))
            out[cur] = []
            continue
        term = re.match(r"\s+s\^ (\d) :(.*)", line)
        if term and cur is not None:
            expr = term.group(2).strip().replace("^", "**").replace("Rr", "R")
            out[cur].append(sympy.sympify(expr, locals={"W": W_, "R": R_, "S": S_, "K": K_}))
    if sorted(out) != [1, 2, 3] or any(len(v) != 4 for v in out.values()):
        raise ValueError("limit log is incomplete")
    return out


def mod_poly(expr: sympy.Expr, p: int) -> sympy.Poly:
    return sympy.Poly(expr, W_, R_, S_, K_, modulus=p)


def rank_mod(rows: list[list[int]], p: int) -> int:
    a = [[x % p for x in r] for r in rows]
    rank = 0
    ncol = len(a[0]) if a else 0
    for c in range(ncol):
        piv = next((i for i in range(rank, len(a)) if a[i][c]), None)
        if piv is None:
            continue
        a[rank], a[piv] = a[piv], a[rank]
        ic = inv(a[rank][c], p)
        a[rank] = [x * ic % p for x in a[rank]]
        for i in range(len(a)):
            if i != rank and a[i][c]:
                f = a[i][c]
                a[i] = [(x - f * y) % p for x, y in zip(a[i], a[rank], strict=True)]
        rank += 1
    return rank


def limit_numeric(sl: Slice, pt: tuple[int, ...]) -> dict[str, Any]:
    """Exact series replay of one arc: J residues, order of G(x(s)), coefficient vectors at s^0..s^3."""
    xs = SR.arc(sl.sgn, sl.prime, pt[0], pt[1], pt[2], pt[3], TOP)
    x0 = all(x.coeff(0) == 0 for x in xs)
    jres = sum(1 for j in sl.j if SR.eval_poly(j, xs, TOP).val() is not None)
    vals = [SR.eval_poly(g, xs, TOP) for g in sl.g]
    vs = [v.val() for v in vals]
    finite = [v for v in vs if v is not None]
    nu = min(finite) if finite else None
    vec = [v.coeff(nu) for v in vals] if nu is not None else None
    coeffs = [[v.coeff(k) for k in range(4)] for v in vals]
    return {"x0": x0, "j_nonzero": jres, "nu": nu, "F": vec, "coeffs": coeffs}


class PointCheck:
    """Callable for one grid point; compares the replayed series with the symbolic coefficients (no J or G of the
    unperturbed slice enters a control except through `symbolic`)."""

    def __init__(self, sl: Slice, symbolic: dict[int, list[sympy.Poly]]) -> None:
        self.sl = sl
        self.symbolic = symbolic  # {j: [Poly objects of coefficients s^0..s^3]}

    def __call__(self, pt: tuple[int, ...]) -> dict[str, Any]:
        p = self.sl.prime
        res = limit_numeric(self.sl, pt)
        values = {W_: pt[0], R_: pt[1], S_: pt[2], K_: pt[3]}
        sym = [[int(c.eval(values)) % p for c in self.symbolic[j]] for j in (1, 2, 3)]
        reasons = []
        if not res["x0"]:
            reasons.append("x(0) != 0")
        if res["j_nonzero"]:
            reasons.append("J(x(s)) != 0")
        if res["nu"] != 2:
            reasons.append("order != 2")
        if res["coeffs"] != sym:
            reasons.append("series != symbolic")
        res["reasons"] = reasons
        res["point"] = pt
        res.pop("coeffs")
        return res


class HitCheck:
    """Callable for one target projective point (1 : a : b); builds the arc that the limit map sends there."""

    def __init__(self, sl: Slice, coef: tuple[int, int, int]) -> None:
        self.sl, self.coef = sl, coef

    def __call__(self, ab: tuple[int, int]) -> dict[str, Any]:
        p = self.sl.prime
        a1, a2, a3 = self.coef
        ta, tb = ab
        half = inv(2, p)
        ssum = a1 * ta * inv(a2, p) % p  # R + S
        sdif = a1 * tb * inv(a3, p) % p  # R - S
        R = (ssum + sdif) * half % p
        S = (ssum - sdif) * half % p
        pt = (1, R, S, 7)
        res = limit_numeric(self.sl, pt)
        want = [a1 % p, a1 * ta % p, a1 * tb % p]
        ok = res["nu"] == 2 and res["F"] == want and res["j_nonzero"] == 0
        return {"target": [1, ta, tb], "point": pt, "F": res["F"], "ok": ok}


class JacobianRows:
    """Callable for one point: Jacobian of the order-2 limit map by central differences of exact replays; exact when
    the map has degree <= 2."""

    def __init__(self, sl: Slice) -> None:
        self.sl = sl

    def __call__(self, pt: tuple[int, ...]) -> list[list[int]]:
        p = self.sl.prime
        rows = [[0] * 4 for _ in range(3)]
        half = inv(2, p)
        for i in range(4):
            fp = list(pt)
            fm = list(pt)
            fp[i] += 1
            fm[i] -= 1
            vp = limit_numeric(self.sl, tuple(fp))
            vm = limit_numeric(self.sl, tuple(fm))
            if vp["nu"] != 2 or vm["nu"] != 2:
                raise ValueError("order changed under the difference")
            for j in range(3):
                rows[j][i] = (vp["F"][j] - vm["F"][j]) * half % p
        return rows


class DphiRank:
    """Callable for one parameter point: rank of the 7 x 4 Jacobian of Phi by dual numbers."""

    def __init__(self, prime: int, sgn: int) -> None:
        self.prime, self.sgn = prime, sgn

    def __call__(self, pt: tuple[int, int, int, int]) -> int:
        cols = []
        for i in range(4):
            args = [SR.Dual(pt[k], 1 if k == i else 0, self.prime) for k in range(4)]
            xs = SR.phi(self.sgn, self.prime, *args)
            cols.append([x.d for x in xs])
        return rank_mod([[cols[i][j] for i in range(4)] for j in range(7)], self.prime)


class PhiResidue:
    """Callable for one parameter point: number of generators of J that Phi leaves nonzero there."""

    def __init__(self, sl: Slice) -> None:
        self.sl = sl

    def __call__(self, pt: tuple[int, ...]) -> int:
        xs = SR.phi(self.sl.sgn, self.sl.prime, *[SR.Series([c], 1, self.sl.prime) for c in pt])
        return sum(1 for j in self.sl.j if SR.eval_poly(j, xs, 1).val() is not None)


def run_map(function: Any, items: list[Any]) -> list[Any]:
    return list(parallel.ordered_map(function, items, min_items=MIN_ITEMS))


def with_flipped_t9(sl: Slice) -> Slice:
    """The slice with the sign of the t9 term of J[12] reversed (the control that must leave V(J))."""
    j = [dict(x) for x in sl.j]
    if T9_KEY not in j[FLIPPED_GENERATOR]:
        raise ValueError("J[12] has no t9 term")
    j[FLIPPED_GENERATOR][T9_KEY] = (-j[FLIPPED_GENERATOR][T9_KEY]) % sl.prime
    return Slice(sl.prime, sl.sgn, tuple(j), sl.g)


def with_perturbed_g2(sl: Slice) -> Slice:
    """The slice with G_2 replaced by G_2 + t2^2."""
    g = [dict(x) for x in sl.g]
    g[1][G2_SQUARE] = (g[1].get(G2_SQUARE, 0) + 1) % sl.prime
    return Slice(sl.prime, sl.sgn, sl.j, tuple(g))


def with_duplicated_g(sl: Slice) -> Slice:
    """The slice with G_3 replaced by a copy of G_2."""
    return Slice(sl.prime, sl.sgn, sl.j, (sl.g[0], sl.g[1], dict(sl.g[1])))


def certify(h: Header, limit_log: str, phi_log: str, ctl_log: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """The result record and the details record of one incidence at one prime."""
    p = h.prime
    sl = slice_of(h)
    sym_raw = parse_limit_text(limit_log)
    symbolic = {j: [mod_poly(e, p) for e in sym_raw[j]] for j in sym_raw}

    # Symbolic limit vector at order 2 and its structure
    f2 = [sym_raw[j][2] for j in (1, 2, 3)]
    for j in (1, 2, 3):
        if any(not mod_poly(sym_raw[j][k], p).is_zero for k in (0, 1)):
            raise ValueError("G_j(x(s)) has a nonzero coefficient below s^2")
    a1 = int(sympy.Poly(f2[0], W_, modulus=p).coeff_monomial(W_**2)) % p
    a2 = int(sympy.Poly(f2[1], W_, R_, S_, modulus=p).coeff_monomial(W_ * R_)) % p
    a3 = int(sympy.Poly(f2[2], W_, R_, S_, modulus=p).coeff_monomial(W_ * R_)) % p
    structure_ok = (
        mod_poly(f2[0] - a1 * W_**2, p).is_zero
        and mod_poly(f2[1] - a2 * W_ * (R_ + S_), p).is_zero
        and mod_poly(f2[2] - a3 * W_ * (R_ - S_), p).is_zero
    )
    jac_sym = sympy.Matrix(f2).jacobian([W_, R_, S_, K_])
    det_wrs = sympy.factor(jac_sym[:, :3].det(), modulus=p)
    rank_sym = []
    for pt in RANK_POINTS:
        m = jac_sym.subs({W_: pt[0], R_: pt[1], S_: pt[2], K_: pt[3]})
        rank_sym.append(rank_mod([[int(x) % p for x in m.row(i)] for i in range(3)], p))
    num_jac = run_map(JacobianRows(sl), RANK_POINTS)
    num_rank = [rank_mod(rows, p) for rows in num_jac]
    # dPhi rank and J(Phi) = 0 at parameter points
    dphi_ranks = run_map(DphiRank(p, sl.sgn), [(0, 0, 0, 0), (3, 5, 7, 11)])
    dphi = {"origin": dphi_ranks[0], "generic": dphi_ranks[1]}
    phi_fail = sum(run_map(PhiResidue(sl), PHI_POINTS))

    # Grid replay
    points = list(itertools.product(*GRID))
    grid = run_map(PointCheck(sl, symbolic), points)
    failures = [g for g in grid if g["reasons"]]

    hits = run_map(HitCheck(sl, (a1, a2, a3)), HIT_TARGETS)
    hit_fail = [x for x in hits if not x["ok"]]

    # Negative controls
    controls: dict[str, dict[str, Any]] = {}
    cj = run_map(PointCheck(with_flipped_t9(sl), symbolic), points)
    controls["j_sign_flip"] = {
        "perturbation": "sign of the t9 term of J[12] flipped",
        "failing_check": "J(x(s)) = 0",
        "points": len(cj),
        "points_failing_J": sum(1 for g in cj if "J(x(s)) != 0" in g["reasons"]),
        "must_fail": True,
        "failed_as_intended": all("J(x(s)) != 0" in g["reasons"] for g in cj),
    }
    cg = run_map(PointCheck(with_perturbed_g2(sl), symbolic), points)
    controls["generator_perturbation"] = {
        "perturbation": "G_2 replaced by G_2 + t2^2",
        "failing_check": "replayed series equals the symbolic series of the unperturbed G",
        "points": len(cg),
        "points_failing_series": sum(1 for g in cg if "series != symbolic" in g["reasons"]),
        "must_fail": True,
        "failed_as_intended": all("series != symbolic" in g["reasons"] for g in cg),
    }
    rk = [rank_mod(rows, p) for rows in run_map(JacobianRows(with_duplicated_g(sl)), RANK_POINTS)]
    controls["rank_collapse"] = {
        "perturbation": "G_3 replaced by a copy of G_2",
        "failing_check": "Jacobian rank of the limit map is 3",
        "ranks": rk,
        "must_fail": True,
        "failed_as_intended": all(r < 3 for r in rk),
    }
    sym_ok = "nonzero numerators of J(Phi): 0" in phi_log
    ctl_match = re.search(r"must be > 0\): (\d+)", ctl_log)
    if ctl_match is None:
        raise ValueError("control log has no numerator count")
    controls["j_sign_flip"]["symbolic_nonzero_numerators"] = int(ctl_match.group(1))

    certified = (
        sym_ok
        and structure_ok
        and not failures
        and not hit_fail
        and not phi_fail
        and all(r == 3 for r in rank_sym)
        and all(r == 3 for r in num_rank)
        and all(v == 4 for v in dphi.values())
        and all(c["failed_as_intended"] for c in controls.values())
        and controls["j_sign_flip"]["symbolic_nonzero_numerators"] > 0
    )
    family = "x(s) = Phi(w = W s, rho = R s, sigma = S s, t1 = K s): linear arcs through the origin of V(J)"
    result = {
        "incidence": INCIDENCES[h.slug],
        "certified_P2": bool(certified),
        "family": family,
        "jacobian_rank": min(rank_sym + num_rank),
        "points": len(points),
        "grid_failures": len(failures),
        "controls": controls,
        "prime": p,
        "root_of_minus_one": h.root,
        "limit_order": 2,
        "limit_map": {
            "F1": f"{a1} W^2",
            "F2": f"{a2} W (R + S)",
            "F3": f"{a3} W (R - S)",
            "jacobian_det_in_W_R_S": str(det_wrs),
        },
        "targets_hit": len(hits) - len(hit_fail),
        "targets": len(hits),
        "dphi_rank": dphi,
        "phi_points_with_J_nonzero": phi_fail,
        "symbolic_J_of_Phi_vanishes": sym_ok,
        "jacobian_rank_symbolic_at_points": rank_sym,
        "jacobian_rank_replay_at_points": num_rank,
        "input_sha256": hashlib.sha256(h.path.read_bytes()).hexdigest(),
    }
    details = {
        "grid_first_failures": failures[:5],
        "grid_limit_vectors": [{"point": g["point"], "F": g["F"]} for g in grid],
        "hits": hits,
        "rank_points": RANK_POINTS,
        "replay_jacobians": num_jac,
        "symbolic_jacobian_f2": [[str(x) for x in jac_sym.row(i)] for i in range(3)],
    }
    return result, details


def main(prime: int, slug: str) -> None:
    h = load_headers(prime)[slug]
    logs = prime_dir("logs", prime)
    result, details = certify(
        h,
        (logs / f"{slug}_limit.log").read_text(),
        (logs / f"{slug}_phi.log").read_text(),
        (logs / f"{slug}_ctl.log").read_text(),
    )
    out_dir = prime_dir("records", prime) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out_dir / "details.json").write_text(json.dumps(details, indent=1) + "\n")
    print(
        slug,
        "certified_P2",
        result["certified_P2"],
        "rank",
        result["jacobian_rank"],
        "failures",
        result["grid_failures"],
        "hits",
        result["targets_hit"],
    )


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2])
