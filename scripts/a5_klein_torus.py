"""The Klein sign group of the N- base point is the 2-torsion of a rank-2 torus of its stabilizer in H (A5-254).

H = G_2(C) x SO(2, C) x C^* acts on the split coordinates z' in C^15 of the strata record: its 16 tangent generators
are strata_regularity.h_generators (the 14 split-octonion derivations on u' and v', the scaling and the boost), here
turned into 15 x 15 matrices A_1..A_16 by applying them to the standard basis. The N- base point p is
strata_regularity.REPS["Nm"] (support {1, 3, 9, 11}). The Klein group is the stabilizer of p among the diagonal maps
z'_k -> epsilon chi_s(k) z'_k, chi_s(k) = (-1)^popcount(s AND k), with (s, epsilon) = (1, -1), (4, 1), (5, -1)
(cd-tower report, section 3.1); the split substitution z_k = i^popcount(k) z'_k is diagonal, so these are the same
maps in either coordinate system.

Every step is exact over Q (SymPy Rational matrices). The record decides, with a require behind each item:

- the stabilizer algebra s = {X in span(A_k) : X p = 0} has dimension 10, and each Klein matrix fixes p;
- the centralizer c of the three Klein matrices in s has dimension 3 and is abelian; its boost-free part
  c' = c n span(A_1..A_15) has dimension 2;
- c and c' act diagonalizably on C^15 (the joint eigenspaces of a basis span C^15), with rational weights, so the
  Zariski closures T_K = exp(c) and T'_K = exp(c') are algebraic tori of ranks 3 and 2, every element semisimple and
  the nilpotent part of every Jordan decomposition zero;
- with the weight lattice M of the torus (Hermite normal form of the 15 weights) and its dual cocharacter lattice N,
  the 2-torsion T[2] = exp(2 pi i N / 2) acts by (-1)^(w . lambda) on the weight spaces: for T'_K this set of four
  matrices equals {1, K_1, K_2, K_3}; for T_K the eight matrices contain the Klein group;
- the generalized zero space of ad(x) at one integer point x of s' = s n span(A_1..A_15) (and of s) has dimension
  2 (and 3), an upper bound for the rank, so T'_K (T_K) is a maximal torus of the boost-free (full) stabilizer.

Controls (--self-test; each baseline holds and its mutant fails): the character s = 2 in place of s = 1 does not fix
p; with the scaling generator removed the boost-free torus has rank 1, whose 2-torsion misses the Klein elements
with epsilon = -1; and the Klein matrices multiplied by the reflection mu' -> -mu', which lies outside G_2 x C^*,
differ from the 2-torsion of the boost-free torus (the rank-3 torus with the boost contains them, since its 2-torsion
acts on mu' by the weight of the scaling plus boost). Every sign is an integer (-1)^k computed by parity, never a
power with a negative exponent, which Python returns as a float. No random draw enters.

Usage:
    "$PYTHON" -B -W error scripts/a5_klein_torus.py --self-test
    "$PYTHON" -B -W error scripts/a5_klein_torus.py --out docs/evidence/a5-klein-torus/result.json
    "$PYTHON" -B -W error scripts/a5_klein_torus.py --check docs/evidence/a5-klein-torus/result.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from math import gcd
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-strata-regularity"))

import strata_regularity as sr  # noqa: E402

KLEIN = ((1, -1), (4, 1), (5, -1))
DIM = 15
BOOST = 15
SCALING = 14


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def chi(s: int, k: int) -> int:
    return -1 if bin(s & k).count("1") % 2 else 1


def klein_matrix(s: int, eps: int, reflect: bool = False) -> sp.Matrix:
    diag = [eps * chi(s, k) for k in range(1, DIM + 1)]
    if reflect:
        diag[7] = -diag[7]
    return sp.diag(*diag)


def generator_matrices() -> list[sp.Matrix]:
    """A_k[r][j] = (generator k applied to e_j)_r for the 16 tangent generators of H."""
    cols = []
    for j in range(DIM):
        e = [0] * DIM
        e[j] = 1
        cols.append(sr.h_generators(e))
    return [sp.Matrix(DIM, DIM, lambda r, j, k=k: sp.Rational(cols[j][k][r])) for k in range(16)]


def combine(mats: list[sp.Matrix], coeffs: list[Any]) -> sp.Matrix:
    out = sp.zeros(DIM, DIM)
    for c, m in zip(coeffs, mats, strict=True):
        if c != 0:
            out += c * m
    return out


def coefficient_space(
    mats: list[sp.Matrix], point: sp.Matrix, commute_with: list[sp.Matrix], zero_coeffs: tuple[int, ...]
) -> list[list[sp.Rational]]:
    """Reduced basis of {c : (sum c_k A_k) p = 0, [sum c_k A_k, K] = 0, c_i = 0 for i in zero_coeffs}."""
    n = len(mats)
    rows: list[list[Any]] = []
    for r in range(DIM):
        rows.append([(m * point)[r] for m in mats])
    for k in commute_with:
        comms = [m * k - k * m for m in mats]
        for r in range(DIM):
            for c in range(DIM):
                rows.append([cm[r, c] for cm in comms])
    for i in zero_coeffs:
        rows.append([1 if j == i else 0 for j in range(n)])
    null = sp.Matrix(rows).nullspace()
    if not null:
        return []
    basis = sp.Matrix.hstack(*null).T.rref()[0]
    return [[basis[i, j] for j in range(n)] for i in range(basis.rows) if any(basis[i, j] != 0 for j in range(n))]


def joint_eigenspaces(elems: list[sp.Matrix]) -> list[tuple[tuple[sp.Rational, ...], sp.Matrix]]:
    """Joint eigenspaces of commuting matrices with rational eigenvalues, as (weight, column basis)."""
    eigs = []
    for x in elems:
        vals = list(x.eigenvals())
        require(all(v.is_rational for v in vals), "an eigenvalue is irrational")
        eigs.append(sorted(vals))
    out = []
    for combo in itertools.product(*eigs):
        stacked = sp.Matrix.vstack(*[x - v * sp.eye(DIM) for x, v in zip(elems, combo, strict=True)])
        null = stacked.nullspace()
        if null:
            out.append((tuple(combo), sp.Matrix.hstack(*null)))
    return out


def integer_hnf(rows: list[list[int]]) -> list[list[int]]:
    """Row Hermite normal form (nonzero rows) of an integer matrix by gcd elimination."""
    mat = [list(r) for r in rows]
    ncols = len(mat[0])
    out: list[list[int]] = []
    for col in range(ncols):
        while True:
            live = [r for r in mat if r[col] != 0]
            if len(live) <= 1:
                break
            live.sort(key=lambda r: abs(r[col]))
            pivot = live[0]
            for r in live[1:]:
                q = r[col] // pivot[col]
                for j in range(ncols):
                    r[j] -= q * pivot[j]
        live = [r for r in mat if r[col] != 0]
        if live:
            pivot = live[0]
            if pivot[col] < 0:
                for j in range(ncols):
                    pivot[j] = -pivot[j]
            out.append(pivot)
            mat = [r for r in mat if r is not pivot]
    return out


def torus_data(elems: list[sp.Matrix]) -> dict[str, Any]:
    """Weights, lattice and 2-torsion matrices of the torus exp(span elems)."""
    rank = len(elems)
    if rank == 0:
        return {"rank": 0, "diagonalizable": True, "lattice_rank": 0, "weights": [], "two_torsion": [sp.eye(DIM)]}
    spaces = joint_eigenspaces(elems)
    total = sum(b.cols for _, b in spaces)
    weights = []
    for w, b in spaces:
        weights.extend([w] * b.cols)
    den = 1
    for w in weights:
        for x in w:
            den = den * sp.Rational(x).q // gcd(den, sp.Rational(x).q)
    scaled = [[int(x * den) for x in w] for w in weights]
    hnf = integer_hnf(scaled)
    lattice_rank = len(hnf)
    data: dict[str, Any] = {
        "rank": rank,
        "diagonalizable": total == DIM,
        "lattice_rank": lattice_rank,
        "weights": sorted([[str(x) for x in w], b.cols] for w, b in spaces),
    }
    if total != DIM or lattice_rank != rank:
        data["two_torsion"] = []
        return data
    basis_m = sp.Matrix(hnf) / den  # rows: a basis of M
    cochar = basis_m.inv()  # columns: the dual basis of N
    p_mat = sp.Matrix.hstack(*[b for _, b in spaces])
    p_inv = p_mat.inv()
    torsion = []
    for eps in itertools.product((0, 1), repeat=rank):
        lam = cochar * sp.Matrix(eps)
        signs = []
        for w, b in spaces:
            pair = sum((w[i] * lam[i] for i in range(rank)), sp.Integer(0))
            require(pair.is_integer, "a weight pairs non-integrally with a cocharacter")
            signs.extend([1 if int(pair) % 2 == 0 else -1] * b.cols)
        torsion.append(p_mat * sp.diag(*signs) * p_inv)
    data["cocharacters"] = [[str(cochar[i, j]) for i in range(rank)] for j in range(rank)]
    data["two_torsion"] = torsion
    return data


def ad_zero_dimension(mats: list[sp.Matrix], basis: list[list[sp.Rational]]) -> int:
    """Generalized zero-space dimension of ad(x), x = sum (i + 1) Y_i over the given basis of a Lie algebra."""
    ys = [combine(mats, c) for c in basis]
    flat = sp.Matrix.hstack(*[y.reshape(DIM * DIM, 1) for y in ys])
    x = combine(ys, [sp.Integer(i + 1) for i in range(len(ys))])
    cols = []
    for y in ys:
        br = (x * y - y * x).reshape(DIM * DIM, 1)
        sol, params = flat.gauss_jordan_solve(br)
        require(not params, "the basis is dependent")
        cols.append(sol)
    ad = sp.Matrix.hstack(*cols)
    lam = sp.Symbol("lam")
    poly = sp.Poly(ad.charpoly(lam).as_expr(), lam)
    k = 0
    while poly.eval(0) == 0:
        poly = sp.Poly(sp.cancel(poly.as_expr() / lam), lam)
        k += 1
    return k


def is_abelian(elems: list[sp.Matrix]) -> bool:
    return all((a * b - b * a).is_zero_matrix for a in elems for b in elems)


def analyse(drop_scaling: bool = False, klein_s1: int = 1, reflect: bool = False) -> dict[str, Any]:
    mats = generator_matrices()
    point = sp.Matrix(sr.REPS["Nm"])
    klein = [klein_matrix(s if s != 1 else klein_s1, eps, reflect) for s, eps in KLEIN]
    zero_bf = (BOOST, SCALING) if drop_scaling else (BOOST,)
    stab = coefficient_space(mats, point, [], ())
    stab_bf = coefficient_space(mats, point, [], zero_bf)
    cent = coefficient_space(mats, point, klein, ())
    cent_bf = coefficient_space(mats, point, klein, zero_bf)
    c_full = [combine(mats, c) for c in cent]
    c_bf = [combine(mats, c) for c in cent_bf]
    t_full = torus_data(c_full)
    t_bf = torus_data(c_bf)
    group = {tuple(k) for k in [sp.eye(DIM), *klein]}
    bf_set = {tuple(m) for m in t_bf["two_torsion"]}
    full_set = {tuple(m) for m in t_full["two_torsion"]}
    return {
        "klein_fix_point": [bool((k * point - point).is_zero_matrix) for k in klein],
        "stabilizer_dim": len(stab),
        "stabilizer_boost_free_dim": len(stab_bf),
        "centralizer_dim": len(cent),
        "centralizer_boost_free_dim": len(cent_bf),
        "centralizer_abelian": is_abelian(c_full),
        "centralizer_coefficients": [[str(x) for x in c] for c in cent],
        "centralizer_boost_free_coefficients": [[str(x) for x in c] for c in cent_bf],
        "torus_full": {k: v for k, v in t_full.items() if k != "two_torsion"},
        "torus_boost_free": {k: v for k, v in t_bf.items() if k != "two_torsion"},
        "boost_free_two_torsion_equals_klein": bf_set == group,
        "full_two_torsion_order": len(full_set),
        "full_two_torsion_contains_klein": group <= full_set,
        "ad_zero_dim_stabilizer": ad_zero_dimension(mats, stab) if stab else 0,
        "ad_zero_dim_stabilizer_boost_free": ad_zero_dimension(mats, stab_bf) if stab_bf else 0,
    }


def compute() -> dict[str, Any]:
    return {
        "claim": "the Klein sign group of the N- base point equals T'_K[2] for the rank-2 torus T'_K = exp(c'), c' the "
        "boost-free centralizer of the Klein group in the stabilizer algebra of N- in H",
        "base_point": [int(x) for x in sr.REPS["Nm"]],
        "klein": [list(k) for k in KLEIN],
        "result": analyse(),
        "sympy": sp.__version__,
    }


def validate(result: dict[str, Any]) -> None:
    r = result["result"]
    require(all(r["klein_fix_point"]), "a Klein matrix moves the base point")
    require(r["stabilizer_dim"] == 10, f"stabilizer dimension {r['stabilizer_dim']}")
    require(r["stabilizer_boost_free_dim"] == 9, f"boost-free stabilizer dimension {r['stabilizer_boost_free_dim']}")
    require(r["centralizer_dim"] == 3 and r["centralizer_abelian"], "the Klein centralizer is not abelian of dim 3")
    require(r["centralizer_boost_free_dim"] == 2, "the boost-free centralizer is not 2-dimensional")
    for key, rank in (("torus_full", 3), ("torus_boost_free", 2)):
        t = r[key]
        require(t["diagonalizable"], f"{key}: not diagonalizable (a nilpotent Jordan part)")
        require(t["lattice_rank"] == rank and t["rank"] == rank, f"{key}: weight lattice rank {t['lattice_rank']}")
        require(sum(m for _, m in t["weights"]) == DIM, f"{key}: weight multiplicities")
    require(r["boost_free_two_torsion_equals_klein"], "T'_K[2] differs from the Klein group")
    require(r["full_two_torsion_order"] == 8 and r["full_two_torsion_contains_klein"], "T_K[2] misses Klein")
    require(r["ad_zero_dim_stabilizer"] == 3, f"rank bound of the stabilizer {r['ad_zero_dim_stabilizer']}")
    require(r["ad_zero_dim_stabilizer_boost_free"] == 2, "rank bound of the boost-free stabilizer")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    base = analyse()
    wrong_char = analyse(klein_s1=2)
    control(all(base["klein_fix_point"]), all(wrong_char["klein_fix_point"]), "character s = 2 fixes p")
    no_scaling = analyse(drop_scaling=True)
    control(
        base["boost_free_two_torsion_equals_klein"],
        no_scaling["boost_free_two_torsion_equals_klein"],
        "torus without the scaling",
    )
    reflected = analyse(reflect=True)
    control(
        base["boost_free_two_torsion_equals_klein"],
        reflected["boost_free_two_torsion_equals_klein"],
        "Klein times the reflection mu' -> -mu'",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 3 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
