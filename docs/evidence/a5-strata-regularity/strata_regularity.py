"""Orbit stratification, singular loci and transverse germs of the A_5 rank strata, from cd_core and Singular.

The group H = G_2(C) x SO(2, C) x C^* acts on the doubly pure coordinates z' in C^15 (split coordinates of the
[equations record](../a5-rank-strata-equations/README.md)): G_2 through the 14 derivations of the split octonions on
u' and v' alike, C^* by scaling, and SO(2, C) through the boost (u', v') -> (c u' + s v', s u' + c v'), c^2 - s^2 = 1,
which is the rotation of (u, v) in original coordinates. The reflection mu' -> -mu' also acts. The script decides:

- symmetry: every closure ideal below, and Q and G, is carried into itself by the boost generator and the reflection;
- identities: Q = eta(s, d) - mu'^2 and G = eta(s) eta(d) - 2 mu'^2 eta(s, d) + mu'^4 with s = u' + v', d = u' - v';
- representatives: twelve rational points, one per orbit of nullity at least 8, with the nullity of L_y, the
  membership pattern in the twelve closures and the rank of the 16 H-generators (the orbit dimension);
- planes: for each slice plane (A, B) of Lemma 5 of the strata record, the dimension r_G of the G_2-orbit of the pair
  (A, B) and a basis of the subalgebra s of gl_2 induced by the stabilizer of the plane;
- certificate: on each slice, inside each closure X, the locus of independent pairs where the orbit rank is below
  dim X lies in the closures listed below X, and the independent part of X outside them has a fixed number of
  components;
- iso: the isotropic-pair closure is a complete intersection whose Jacobian drops rank only on V n B9-bar;
- germs: for each closure X (and V(Q), V(G)) and each orbit O inside X, the reduced germ of X in an affine slice
  through the representative of O transverse to O: dimension, multiplicity, embedding dimension, algebraic
  components through the point with their own invariants and pairwise meet dimensions, and the rank of the quadric
  of the tangent cone where the germ is a hypersurface in its embedding;
- nullity4: on every slice, Sing V(G) has the radical of W8 u V, and the points of V(Q) n V(G) where dQ and dG are
  dependent lie in the isotropic closure or in E8-bar.

Every Groebner basis, radical, saturation, decomposition and local standard basis is a Singular computation over Q;
every constant rank is an exact python-flint fmpq_mat rank. The closure ideals, the piece polynomials, the derivations
and the nullity of L_y are those of the equations record script, imported unchanged.

--self-test runs five controls, each of which must fail: the compact rotation (u', v') -> (v', -u') preserving Q,
the representatives of V^a_+ and V^a_- swapped, B9 without u' x v' = 0 at its claimed dimension, the certificate
for the isotropic closure on P4s with B9 dropped from its lower closures, and the germ of V at N_+ with the mu' term
removed from Q keeping its A_1 type.

Usage:
    "$PYTHON" -B -W error docs/evidence/a5-strata-regularity/strata_regularity.py --self-test
    "$PYTHON" -B -W error docs/evidence/a5-strata-regularity/strata_regularity.py \
        --out docs/evidence/a5-strata-regularity/result.json
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import sys
import time
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE.parent / "a5-rank-strata-equations"))

import rederive_strata_equations as eq  # noqa: E402

import parallel  # noqa: E402

GLOBAL_VARS = eq.GLOBAL_VARS

# Closures of the orbits of nullity at least 8, with their complex dimensions. "Iso" is the closure of the
# generic-isotropic orbit, "Xp" and "Xm" those of the mu' = 0 orbits of E8, "VB" that of V n B9 minus N_+-.
DIMS: dict[str, int] = {
    "W8": 12,
    "Ehat": 11,
    "Iso": 11,
    "Xp": 10,
    "Xm": 10,
    "B9": 9,
    "V": 8,
    "VB": 7,
    "Vap": 7,
    "Vam": 7,
    "Np": 6,
    "Nm": 6,
}
NULLITY = {"W8": 8, "Ehat": 8, "Iso": 8, "Xp": 8, "Xm": 8, "B9": 12, "V": 12, "VB": 12, "Vap": 12, "Vam": 12}
HYPERSURFACES = ("VQ", "VG")


def split_point(u: dict[int, int], mu: int, v: dict[int, int]) -> list[int]:
    zp = [0] * 15
    for j, x in u.items():
        zp[j - 1] += x
    zp[7] = mu
    for j, x in v.items():
        zp[7 + j] += x
    return zp


N0 = {1: 1, 3: 1}  # n = e'_1 + e'_3, null
A3 = {2: 1, 3: 1}  # the P3a radical vector, in V_+ of e'_1
K0 = {4: 1, 6: 1}  # n x k = 0: span(n, k) is a special isotropic plane


def lin(*terms: tuple[int, dict[int, int]]) -> dict[int, int]:
    out: dict[int, int] = {}
    for c, vec in terms:
        for j, x in vec.items():
            out[j] = out.get(j, 0) + c * x
    return out


# One representative of the open orbit of each closure.
REPS: dict[str, list[int]] = {
    "W8": split_point({1: 1}, 0, {3: 1}),
    "Ehat": split_point(lin((1, A3), (3, {1: 1})), 4, lin((2, A3), (5, {1: 1}))),
    "Iso": split_point(N0, 0, {2: 1, 5: 1}),
    "Xp": split_point(lin((1, A3), (1, {1: 1})), 0, {1: 1}),
    "Xm": split_point(lin((1, A3), (1, {1: 1})), 0, {1: -1}),
    "B9": split_point(lin((1, N0), (2, K0)), 0, lin((3, N0), (5, K0))),
    "V": split_point({1: 3}, 4, {1: 5}),
    "VB": split_point(N0, 0, {}),
    "Vap": split_point({1: 1}, 0, {1: 1}),
    "Vam": split_point({1: 1}, 0, {1: -1}),
    "Np": split_point(N0, 0, N0),
    "Nm": split_point(N0, 0, lin((-1, N0))),
}


def closure_ideals(mutation: str = "") -> dict[str, list[Any]]:
    """Generators of every closure ideal and of V(Q), V(G) in split coordinates z'_1..z'_15."""
    ctx = eq.global_ctx()
    z = list(ctx.gens())
    pcs = eq.piece_ideals(z)
    u, mu, v = z[0:7], z[7], z[8:15]
    eta = eq.ETA[1:]

    def form(x: Sequence[Any], y: Sequence[Any]) -> Any:
        return sum((eta[j] * x[j] * y[j] for j in range(7)), mu * 0)

    s = [u[j] + v[j] for j in range(7)]
    d = [u[j] - v[j] for j in range(7)]
    minors2 = [u[i] * v[j] - u[j] * v[i] for i, j in itertools.combinations(range(7), 2)]
    q, g = pcs["QG"]
    iso = [mu, form(u, u), form(v, v), form(u, v)]
    out = {
        "W8": pcs["W8"],
        "Ehat": pcs["Ehat"],
        "Iso": iso,
        "Xp": [mu, form(d, d), *pcs["Ehat"]],
        "Xm": [mu, form(s, s), *pcs["Ehat"]],
        "B9": iso if mutation == "b9_no_cross" else pcs["B9"],
        "V": [form(s, d), *minors2] if mutation == "q_without_mu" else pcs["V"],
        "VB": [*iso, *minors2],
        "Vap": [mu, *d],
        "Vam": [mu, *s],
        "Np": pcs["Np"],
        "Nm": pcs["Nm"],
        "VQ": [q],
        "VG": [g],
    }
    return {k: [p for p in gens if p != 0] for k, gens in out.items()}


def member(gens: Sequence[Any], zp: Sequence[int]) -> bool:
    return all(int(p(*zp)) == 0 for p in gens)


DERS = eq.derivations(eq.SPLIT8)


def h_generators(zp: Sequence[Any]) -> list[list[Any]]:
    """The 16 tangent vectors of H at z': 14 derivations, the scaling and the boost u' <-> v'."""
    u = [0, *zp[0:7]]
    v = [0, *zp[8:15]]
    rows = [eq.apply(dm, u)[1:] + [0] + eq.apply(dm, v)[1:] for dm in DERS]
    rows.append(list(zp))
    rows.append(list(zp[8:15]) + [0] + list(zp[0:7]))
    return rows


def orbit_rank(zp: Sequence[int]) -> int:
    return eq.qrank([[Fraction(x) for x in r] for r in h_generators(zp)])


# ---------------------------------------------------------------------------------------------------------------
# Singular helpers


def gens_text(gens: Sequence[Any]) -> str:
    return ",".join(str(p) for p in gens) if gens else "0"


def head(names: Sequence[str] = GLOBAL_VARS) -> str:
    return 'LIB "primdec.lib";\nLIB "sing.lib";\n' + eq.ring_text(names) + "\n"


def run(script: str) -> dict[str, str]:
    start = time.perf_counter()
    res = eq.run_singular(script)
    res["seconds"] = f"{time.perf_counter() - start:.1f}"
    return res


# ---------------------------------------------------------------------------------------------------------------
# Symmetry and identities


def symmetry_job(mutation: str = "") -> dict[str, Any]:
    """X f lies in the ideal for every generator f, X the boost generator; the reflection maps the ideal into itself."""
    ideals = closure_ideals()
    if mutation == "compact":
        xder = "+".join(f"z{9 + k}*diff(f,z{1 + k})-z{1 + k}*diff(f,z{9 + k})" for k in range(7))
    else:
        xder = "+".join(f"z{9 + k}*diff(f,z{1 + k})+z{1 + k}*diff(f,z{9 + k})" for k in range(7))
    refl = ",".join([*GLOBAL_VARS[:7], "-z8", *GLOBAL_VARS[8:]])
    lines = [head(), f"proc X(poly f) {{ return({xder}); }}", f"map sg = r, {refl};"]
    for name, gens in ideals.items():
        lines += [
            f"ideal I = {gens_text(gens)}; ideal S = std(I); int ok = 1;",
            "for (int i = 1; i <= size(I); i++) { if (reduce(X(I[i]), S) != 0) { ok = 0; } }",
            f'"RESULT boost_{name}", ok;',
            f'"RESULT reflection_{name}", size(reduce(sg(I), S)) == 0;',
            "kill I, S, ok, i;",
        ]
    lines.append("quit;")
    res = run("\n".join(lines))
    names = list(ideals)
    ok = all(res.get(f"boost_{n}") == "1" and res.get(f"reflection_{n}") == "1" for n in names)
    return {"pass": ok and "singular_error" not in res, "mutation": mutation, **res}


def identity_checks() -> dict[str, Any]:
    """Q and G in the light-cone vectors s = u' + v', d = u' - v', over Z[z']."""
    ctx = eq.global_ctx()
    z = list(ctx.gens())
    q, g = eq.piece_ideals(z)["QG"]
    u, mu, v = z[0:7], z[7], z[8:15]
    eta = eq.ETA[1:]

    def form(x: Sequence[Any], y: Sequence[Any]) -> Any:
        return sum((eta[j] * x[j] * y[j] for j in range(7)), mu * 0)

    s = [u[j] + v[j] for j in range(7)]
    d = [u[j] - v[j] for j in range(7)]
    q_sd = form(s, d) - mu * mu
    g_sd = form(s, s) * form(d, d) - 2 * mu * mu * form(s, d) + mu**4
    # piece_ideals fixes Q and G up to sign (the unit divided out); the identities fix the sign.
    q_sign = 1 if q == q_sd else (-1 if q == -q_sd else 0)
    g_sign = 1 if g == g_sd else (-1 if g == -g_sd else 0)
    return {"pass": q_sign != 0 and g_sign != 0, "Q_sign": q_sign, "G_sign": g_sign}


# ---------------------------------------------------------------------------------------------------------------
# Representatives


# The closure order: the closures strictly inside each closure.
EXPECTED_LOWER: dict[str, list[str]] = {
    "W8": ["Iso", "B9", "VB", "Np", "Nm"],
    "Ehat": ["Xp", "Xm", "B9", "V", "VB", "Vap", "Vam", "Np", "Nm"],
    "Iso": ["B9", "VB", "Np", "Nm"],
    "Xp": ["B9", "VB", "Vap", "Np", "Nm"],
    "Xm": ["B9", "VB", "Vam", "Np", "Nm"],
    "B9": ["VB", "Np", "Nm"],
    "V": ["VB", "Vap", "Vam", "Np", "Nm"],
    "VB": ["Np", "Nm"],
    "Vap": ["Np"],
    "Vam": ["Nm"],
    "Np": [],
    "Nm": [],
}


def representatives(swap: bool = False) -> dict[str, Any]:
    ideals = closure_ideals()
    reps = dict(REPS)
    if swap:
        reps["Vap"], reps["Vam"] = reps["Vam"], reps["Vap"]
    names = list(DIMS)
    nullities = parallel.ordered_map(eq.point_nullity, [reps[n] for n in names], min_items=1)
    ranks = parallel.ordered_map(orbit_rank, [reps[n] for n in names], min_items=1)
    rows = []
    for name, nul, rank in zip(names, nullities, ranks, strict=True):
        pattern = [x for x in names if member(ideals[x], reps[name])]
        rows.append(
            {
                "closure": name,
                "point": reps[name],
                "nullity": nul,
                "orbit_rank": rank,
                "pattern": pattern,
                "in_VQ": member(ideals["VQ"], reps[name]),
                "in_VG": member(ideals["VG"], reps[name]),
            }
        )
    # Y lies below X when the representative of Y lies in X.
    lower = {x: [r["closure"] for r in rows if r["closure"] != x and x in r["pattern"]] for x in names}
    ok = True
    for r in rows:
        name = r["closure"]
        expect_nul = NULLITY.get(name, 16)
        ok = ok and r["nullity"] == expect_nul and r["orbit_rank"] == DIMS[name] and name in r["pattern"]
        # every closure strictly below has smaller dimension
        ok = ok and all(DIMS[y] < DIMS[name] for y in lower[name])
    patterns = [tuple(r["pattern"]) for r in rows]
    ok = ok and len(set(patterns)) == len(patterns) and lower == EXPECTED_LOWER
    # Every orbit of R_8 lies in V(Q) n V(G) except the open orbit of W8, which lies in V(G) only.
    ok = ok and all((r["in_VQ"], r["in_VG"]) == (r["closure"] != "W8", True) for r in rows)
    return {"pass": ok, "rows": rows, "lower": lower}


def lower_sets() -> dict[str, list[str]]:
    """Y is below X when the open-orbit representative of Y lies in X."""
    ideals = closure_ideals()
    return {x: [y for y in DIMS if y != x and member(ideals[x], REPS[y])] for x in DIMS}


# ---------------------------------------------------------------------------------------------------------------
# Planes and the orbit-rank certificate


def plane_data(name: str) -> dict[str, Any]:
    """r_G = dim G_2 (A, B) and a basis of the induced subalgebra s of gl_2 for the slice plane (A, B)."""
    first, second = eq.SLICE_PLANES[name]
    a = [Fraction(first.get(j, 0)) for j in range(8)]
    b = [Fraction(second.get(j, 0)) for j in range(8)]
    r_g = eq.qrank([eq.apply(dm, a)[1:] + eq.apply(dm, b)[1:] for dm in DERS])
    # sum x_k D_k a = n11 a + n12 b and sum x_k D_k b = n21 a + n22 b; the N-parts of the solutions span s.
    rows = []
    for comp in range(1, 8):
        rows.append([eq.apply(dm, a)[comp] for dm in DERS] + [-a[comp], -b[comp], Fraction(0), Fraction(0)])
        rows.append([eq.apply(dm, b)[comp] for dm in DERS] + [Fraction(0), Fraction(0), -a[comp], -b[comp]])
    basis: list[list[Fraction]] = []
    for vec in eq.nullspace(rows):
        cand = vec[14:]
        if any(cand) and eq.qrank([*basis, cand]) > len(basis):
            basis.append(cand)
    return {"plane": name, "r_G": r_g, "s_dim": len(basis), "s_basis": [[str(x) for x in r] for r in basis]}


def slice_subs(name: str) -> list[str]:
    first, second = eq.SLICE_PLANES[name]
    u = [f"({first.get(j, 0)})*a+({second.get(j, 0)})*b" for j in range(1, 8)]
    v = [f"({first.get(j, 0)})*c+({second.get(j, 0)})*d" for j in range(1, 8)]
    return [*u, "m", *v]


def certificate_job(job: tuple[str, str, str]) -> dict[str, Any]:
    """Orbit-rank drop locus of independent pairs in X on one slice, against the closures below X.

    On a slice point with Mc = [[a, b], [c, d]] invertible, the H-orbit tangent space is Mc applied to the G_2
    tangent space of the pair (A, B) plus the scaling and the boost. The G_2 part has rank r_G and meets the pairs in
    span(A, B) exactly in s (A, B); the scaling is independent through its mu' entry when m != 0, and the boost is
    the pair Mc^-1 J Mc (A, B), J the row swap. So the orbit rank is r_G + [m != 0] + the rank of
    {N_b, [m = 0] I} modulo s, N_b = adj(Mc) J Mc up to the unit det Mc.
    """
    name, closure, mutation = job
    pd = plane_data(name)
    lower = lower_sets()[closure]
    if mutation == "drop_b9":
        lower = [y for y in lower if y != "B9"]
    ideals = closure_ideals()
    r_g, ds = pd["r_G"], pd["s_dim"]
    dim_x = DIMS[closure]
    lines = [head()]
    for y in [closure, *lower]:
        lines.append(f"ideal G_{y} = {gens_text(ideals[y])};")
    lines += [
        "ring rs = 0, (a, b, c, d, m), dp;",
        f"map phi = r, {', '.join(slice_subs(name))};",
    ]
    for y in [closure, *lower]:
        lines.append(f"ideal I_{y} = std(radical(phi(G_{y})));")
    srows = ",".join(x for r in pd["s_basis"] for x in r)
    rows0 = (srows + "," if srows else "") + "NB[1,1],NB[1,2],NB[2,1],NB[2,2],del,0,0,del"
    rows1 = (srows + "," if srows else "") + "NB[1,1],NB[1,2],NB[2,1],NB[2,2]"
    t0 = dim_x - r_g + ds
    t1 = dim_x - r_g - 1 + ds

    def fit(mat: str, nrows: int, t: int) -> str:
        if t <= 0:
            return "ideal(1)"  # rank below t is impossible: no drop
        if t > min(nrows, 4):
            return "ideal(0)"  # rank below t everywhere
        return f"minor({mat}, {t})"

    test = " && ".join(f"size(reduce(I_{y}, Pi)) != 0" for y in lower) or "1"
    lines += [
        "poly del = a*d - b*c;",
        "matrix Ad[2][2] = d, -b, -c, a; matrix JM[2][2] = c, d, a, b; matrix NB = Ad * JM;",
        f"matrix K0[{ds + 2}][4] = {rows0};",
        f"matrix K1[{ds + 1}][4] = {rows1};",
        "proc escapes(list P) { int bad = 0; for (int i = 1; i <= size(P); i++) { ideal Pi = std(P[i]);"
        f" if (Pi[1] != 1) {{ if (reduce(del, Pi) != 0 && {test}) {{ bad++; }} }} }} return(bad); }}",
        f"ideal J0 = I_{closure} + ideal(m) + {fit('K0', ds + 2, t0)};",
        f"ideal J1 = sat(I_{closure} + {fit('K1', ds + 1, t1)}, ideal(m))[1];",
        '"RESULT drop_escapes", escapes(minAssGTZ(J0)) + escapes(minAssGTZ(J1));',
        f"ideal O = sat(I_{closure}, del)[1];",
        '"RESULT open_components", escapes(minAssGTZ(O));',
        "quit;",
    ]
    res = run("\n".join(lines))
    ok = res.get("drop_escapes") == "0" and "singular_error" not in res
    return {"slice": name, "closure": closure, "mutation": mutation, "lower": lower, "pass": ok, **res}


# Slices that carry the independent open part of each closure; every other pair (slice, closure) has none.
OPEN_SLICES = {
    "W8": ("P2",),
    "Ehat": ("P3a", "P3b"),
    "Xp": ("P3a", "P3b"),
    "Xm": ("P3a", "P3b"),
    "B9": ("P4s",),
    "Iso": ("P4g",),
}


# r_G and dim s of each slice plane.
PLANE_TABLE = {"P2": (11, 1), "P3a": (9, 2), "P3b": (9, 2), "P3c": (11, 2), "P4s": (9, 4), "P4g": (11, 4)}


def certificate() -> dict[str, Any]:
    jobs = [(name, x, "") for name in eq.SLICE_PLANES for x in DIMS]
    rows = parallel.ordered_map(certificate_job, jobs, min_items=1)
    ok = all(r["pass"] for r in rows)
    for r in rows:
        expect = 1 if r["slice"] in OPEN_SLICES.get(r["closure"], ()) else 0
        ok = ok and r.get("open_components") == str(expect)
    planes = [plane_data(name) for name in eq.SLICE_PLANES]
    ok = ok and {p["plane"]: (p["r_G"], p["s_dim"]) for p in planes} == PLANE_TABLE
    return {"pass": ok, "planes": planes, "rows": rows}


# ---------------------------------------------------------------------------------------------------------------
# The isotropic closure is a normal complete intersection


def iso_job(name: str) -> dict[str, Any]:
    """On a slice, the 4 x 4 minors of the Jacobian of the Iso generators vanish only on VB-bar."""
    ideals = closure_ideals()
    lines = [
        head(),
        f"ideal G = {gens_text(ideals['Iso'])};",
        f"ideal H = {gens_text(ideals['VB'])};",
        "ideal S = G + minor(jacob(G), 4);",
        '"RESULT global_dim", dim(std(G));',
        "ring rs = 0, (a, b, c, d, m), dp;",
        f"map phi = r, {', '.join(slice_subs(name))};",
        "ideal J = phi(S); ideal Hs = std(radical(phi(H)));",
        "list P = minAssGTZ(J); int bad = 0;",
        "for (int i = 1; i <= size(P); i++) { if (size(reduce(Hs, std(P[i]))) != 0) { bad++; } }",
        '"RESULT escapes", bad;',
        "quit;",
    ]
    res = run("\n".join(lines))
    ok = res.get("escapes") == "0" and res.get("global_dim") == "11" and "singular_error" not in res
    return {
        "slice": name,
        "pass": ok,
        "global_dim": res.get("global_dim"),
        "escapes": res.get("escapes"),
        "seconds": res.get("seconds"),
        **({"singular_error": res["singular_error"]} if "singular_error" in res else {}),
    }


def iso_checks() -> dict[str, Any]:
    rows = parallel.ordered_map(iso_job, list(eq.SLICE_PLANES), min_items=1)
    return {"pass": all(r["pass"] for r in rows), "rows": rows}


# ---------------------------------------------------------------------------------------------------------------
# Transverse germs


# Every complement of the orbit tangent space gives an isomorphic transverse germ. At VB the greedy order tries the
# z3 direction before z1: on the z1 slice the primary decomposition of the E8-bar ideal does not finish.
COLUMN_ORDER: dict[str, tuple[int, ...]] = {"VB": (2, 0, 1, *range(3, 15))}


def transverse_columns(zp: Sequence[int], order: Sequence[int] = range(15)) -> list[int]:
    """Coordinate directions completing the H-orbit tangent space at z' to C^15 (greedy, in the given order)."""
    basis = [[Fraction(x) for x in r] for r in h_generators(zp)]
    cols = []
    for c in order:
        e = [Fraction(int(j == c)) for j in range(15)]
        if eq.qrank([*basis, e]) > eq.qrank(basis):
            basis.append(e)
            cols.append(c)
    return sorted(cols)


def germ_job(job: tuple[str, str, str]) -> dict[str, Any]:
    """Reduced germ at the representative of orbit O of closure X in the slice z' = p + sum t_j e_(c_j)."""
    closure, orbit, mutation = job
    ideals = closure_ideals("q_without_mu" if mutation == "q_without_mu" else "")
    zp = REPS[orbit]
    cols = transverse_columns(zp, COLUMN_ORDER.get(orbit, range(15)))
    k = len(cols)
    tv = [f"t{j + 1}" for j in range(k)]
    subs = [f"({zp[c]}+{tv[cols.index(c)]})" if c in cols else str(zp[c]) for c in range(15)]
    zero = ",".join(["0"] * k)
    lines = [
        head(),
        f"ideal G = {gens_text(ideals[closure])};",
        f"ring r1 = 0, ({', '.join(tv)}), dp;",
        f"map phi = r, {', '.join(subs)};",
        # The reduced germ at p is the intersection of the minimal primes through p; primes away from p drop out.
        "list L = minAssGTZ(phi(G)); list C; int nc = 0;",
        "for (int i = 1; i <= size(L); i++) { if (size(reduce(L[i], std(maxideal(1)))) == 0) { nc++; C[nc] = L[i]; } }",
        "ideal J = C[1]; for (int i = 2; i <= nc; i++) { J = intersect(J, C[i]); }",
        f"ring r2 = 0, ({', '.join(tv)}, h), dp;",
        f"map psi = r1, {', '.join('h*' + v for v in tv)};",
        "setring r1;",
        f"map z0 = r1, {zero};",
        "list A = J; for (int i = 1; i <= nc; i++) { A[i + 1] = C[i]; }",
        # Deformation to the normal cone: the tangent cone at 0 is (X(h t) : h^infinity) at h = 0, a homogeneous
        # ideal whose degree is the multiplicity and whose linear part cuts out the Zariski tangent space.
        "for (int a = 1; a <= size(A); a++) {",
        '  setring r1; ideal X = A[a]; string tag = "germ"; if (a > 1) { tag = "comp" + string(a - 1); }',
        "  int dX = dim(std(X)); matrix MJ = jacob(X); matrix M0 = z0(MJ); int e = nvars(r1) - rank(M0);",
        "  setring r2; ideal Y = sat(psi(X), h); Y = subst(Y, h, 0);",
        "  setring r1; ideal T = std(imap(r2, Y)); int m = mult(T);",
        "  ideal lin; for (int k = 1; k <= size(T); k++) { if (deg(T[k]) == 1) { lin = lin + T[k]; } }",
        "  ideal Rd = simplify(interred(reduce(T, std(lin))), 2);",
        '  string qr = "-1";',
        "  if (e == dX + 1 && m == 2 && size(Rd) == 1) {",
        "    if (deg(Rd[1]) == 2) { qr = string(rank(jacob(jacob(Rd[1])))); } }",
        '  "RESULT " + tag, string(dX) + " " + string(m) + " " + string(e) + " " + qr;',
        "  kill X, tag, dX, MJ, M0, e, T, m, lin, Rd, qr; setring r2; kill Y; setring r1;",
        "}",
        '"RESULT components", nc;',
        # The meet of two sheets at p is the largest minimal prime of their sum through p.
        "for (int i = 1; i <= nc; i++) { for (int j = i + 1; j <= nc; j++) {",
        "  list M = minAssGTZ(C[i] + C[j]); int md = -1;",
        "  for (int k = 1; k <= size(M); k++) { if (size(reduce(M[k], std(maxideal(1)))) == 0) {",
        "    if (dim(std(M[k])) > md) { md = dim(std(M[k])); } } }",
        '  "RESULT meet" + string(i) + string(j), md; kill M, md; } }',
        "quit;",
    ]
    res = run("\n".join(lines))

    def parse(key: str) -> dict[str, int] | None:
        if key not in res:
            return None
        dim, mult, emb, qr = (int(x) for x in res[key].split())
        return {"dim": dim, "mult": mult, "embdim": emb, "quadric_rank": qr}

    ncomp = int(res.get("components", "0"))
    comps = [parse(f"comp{i}") for i in range(1, ncomp + 1)]
    meets = {
        f"{i}{j}": int(res[f"meet{i}{j}"])
        for i in range(1, ncomp + 1)
        for j in range(i + 1, ncomp + 1)
        if f"meet{i}{j}" in res
    }
    out = {
        "closure": closure,
        "orbit": orbit,
        "mutation": mutation,
        "slice_dim": k,
        "germ": parse("germ"),
        "components": comps,
        "meets": meets,
        "seconds": res.get("seconds"),
    }
    if "singular_error" in res:
        out["singular_error"] = res["singular_error"]
    return out


# The germ table: (closure, orbit) -> (dim, mult, embdim, quadric rank or -1, sheets through p, meet dimension of
# the two sheets or None). Every pair (X, O) with O inside X appears.
EXPECTED_GERMS: dict[tuple[str, str], tuple[int, int, int, int, int, int | None]] = {
    ("W8", "Iso"): (1, 1, 1, -1, 1, None),
    ("W8", "B9"): (3, 1, 3, -1, 1, None),
    ("W8", "VB"): (5, 1, 5, -1, 1, None),
    ("W8", "Np"): (6, 2, 7, 7, 1, None),
    ("W8", "Nm"): (6, 2, 7, 7, 1, None),
    ("Ehat", "Xp"): (1, 1, 1, -1, 1, None),
    ("Ehat", "Xm"): (1, 1, 1, -1, 1, None),
    ("Ehat", "B9"): (2, 2, 3, 3, 1, None),
    ("Ehat", "V"): (3, 2, 6, -1, 2, 0),
    ("Ehat", "VB"): (4, 2, 7, -1, 1, None),
    ("Ehat", "Vap"): (4, 2, 7, -1, 2, 1),
    ("Ehat", "Vam"): (4, 2, 7, -1, 2, 1),
    ("Ehat", "Np"): (5, 3, 8, -1, 1, None),
    ("Ehat", "Nm"): (5, 3, 8, -1, 1, None),
    ("Iso", "B9"): (2, 1, 2, -1, 1, None),
    ("Iso", "VB"): (4, 2, 5, 5, 1, None),
    ("Iso", "Np"): (5, 2, 6, 5, 1, None),
    ("Iso", "Nm"): (5, 2, 6, 5, 1, None),
    ("Xp", "B9"): (1, 1, 1, -1, 1, None),
    ("Xp", "VB"): (3, 1, 3, -1, 1, None),
    ("Xp", "Vap"): (3, 2, 6, -1, 2, 0),
    ("Xp", "Np"): (4, 2, 7, -1, 1, None),
    ("Xp", "Nm"): (4, 1, 4, -1, 1, None),
    ("Xm", "B9"): (1, 1, 1, -1, 1, None),
    ("Xm", "VB"): (3, 1, 3, -1, 1, None),
    ("Xm", "Vam"): (3, 2, 6, -1, 2, 0),
    ("Xm", "Np"): (4, 1, 4, -1, 1, None),
    ("Xm", "Nm"): (4, 2, 7, -1, 1, None),
    ("B9", "VB"): (2, 1, 2, -1, 1, None),
    ("B9", "Np"): (3, 1, 3, -1, 1, None),
    ("B9", "Nm"): (3, 1, 3, -1, 1, None),
    ("V", "VB"): (1, 1, 1, -1, 1, None),
    ("V", "Vap"): (1, 1, 1, -1, 1, None),
    ("V", "Vam"): (1, 1, 1, -1, 1, None),
    ("V", "Np"): (2, 2, 3, 3, 1, None),
    ("V", "Nm"): (2, 2, 3, 3, 1, None),
    ("VB", "Np"): (1, 1, 1, -1, 1, None),
    ("VB", "Nm"): (1, 1, 1, -1, 1, None),
    ("Vap", "Np"): (1, 1, 1, -1, 1, None),
    ("Vam", "Nm"): (1, 1, 1, -1, 1, None),
    ("VQ", "Ehat"): (3, 1, 3, -1, 1, None),
    ("VQ", "Iso"): (3, 1, 3, -1, 1, None),
    ("VQ", "Xp"): (4, 1, 4, -1, 1, None),
    ("VQ", "Xm"): (4, 1, 4, -1, 1, None),
    ("VQ", "B9"): (5, 1, 5, -1, 1, None),
    ("VQ", "V"): (6, 1, 6, -1, 1, None),
    ("VQ", "VB"): (7, 1, 7, -1, 1, None),
    ("VQ", "Vap"): (7, 1, 7, -1, 1, None),
    ("VQ", "Vam"): (7, 1, 7, -1, 1, None),
    ("VQ", "Np"): (8, 1, 8, -1, 1, None),
    ("VQ", "Nm"): (8, 1, 8, -1, 1, None),
    ("VG", "W8"): (2, 2, 3, 3, 1, None),
    ("VG", "Ehat"): (3, 1, 3, -1, 1, None),
    ("VG", "Iso"): (3, 2, 4, 2, 1, None),
    ("VG", "Xp"): (4, 1, 4, -1, 1, None),
    ("VG", "Xm"): (4, 1, 4, -1, 1, None),
    ("VG", "B9"): (5, 2, 6, 2, 1, None),
    ("VG", "V"): (6, 2, 7, 7, 1, None),
    ("VG", "VB"): (7, 2, 8, 2, 1, None),
    ("VG", "Vap"): (7, 2, 8, 7, 1, None),
    ("VG", "Vam"): (7, 2, 8, 7, 1, None),
    ("VG", "Np"): (8, 3, 9, -1, 1, None),
    ("VG", "Nm"): (8, 3, 9, -1, 1, None),
}


SMOOTH = "smooth"


def germ_pairs() -> list[tuple[str, str]]:
    ideals = closure_ideals()
    pairs = []
    for x in [*DIMS, *HYPERSURFACES]:
        for orbit, zp in REPS.items():
            if orbit != x and member(ideals[x], zp):
                pairs.append((x, orbit))
    return pairs


def classify_germ(row: dict[str, Any]) -> str:
    """smooth, A1 (quadric cone of full rank in its embedding), two smooth sheets, or singular."""
    g = row["germ"]
    if g is None:
        return "not run"
    if g["mult"] == 1 and g["embdim"] == g["dim"]:
        return SMOOTH
    comps = row["components"]
    if g["mult"] == 2 and g["embdim"] == g["dim"] + 1 and g["quadric_rank"] == g["embdim"]:
        return "A1"
    if (
        len(comps) == 2
        and all(c is not None and c["mult"] == 1 and c["embdim"] == c["dim"] for c in comps)
        and g["mult"] == 2
    ):
        return f"two smooth sheets meeting in dimension {row['meets'].get('12')}"
    if g["mult"] == 2 and g["embdim"] == g["dim"] + 1:
        return f"corank {g['embdim'] - g['quadric_rank']} quadric tangent cone"
    return "singular"


def germs() -> dict[str, Any]:
    pairs = germ_pairs()
    rows = parallel.ordered_map(germ_job, [(x, o, "") for x, o in pairs], min_items=1)
    for r in rows:
        r["type"] = classify_germ(r)
    ok = set(pairs) == set(EXPECTED_GERMS)
    for r in rows:
        g, comps = r["germ"], r["components"]
        if "singular_error" in r or g is None or any(c is None for c in comps):
            ok = False
            continue
        observed = (g["dim"], g["mult"], g["embdim"], g["quadric_rank"], len(comps), r["meets"].get("12"))
        r["expected"] = EXPECTED_GERMS.get((r["closure"], r["orbit"]))
        ok = ok and observed == r["expected"] and g["dim"] == expected_germ_dim(r["closure"], r["orbit"])
        # Every sheet through p has the full dimension, so no component of the closure ideal hides in a lower orbit.
        ok = ok and all(c["dim"] == g["dim"] for c in comps)
    return {"pass": ok, "rows": rows}


def expected_germ_dim(closure: str, orbit: str) -> int:
    top = {"VQ": 14, "VG": 14}.get(closure, DIMS.get(closure, 0))
    return top - DIMS[orbit]


# ---------------------------------------------------------------------------------------------------------------
# Nullity 4: Sing V(G) and the transversality of V(Q) and V(G)


def nullity4_job(name: str) -> dict[str, Any]:
    ideals = closure_ideals()
    g = ideals["VG"][0]
    q = ideals["VQ"][0]
    lines = [
        head(),
        f"poly G = {g}; poly Q = {q};",
        "ideal SG = G, jacob(G);",
        "matrix JQG[2][15] = jacob(Q), jacob(G);",
        "ideal T = Q, G, minor(JQG, 2);",
        f"ideal W = {gens_text(ideals['W8'])}; ideal VV = {gens_text(ideals['V'])};",
        f"ideal I = {gens_text(ideals['Iso'])}; ideal E = {gens_text(ideals['Ehat'])};",
        "ring rs = 0, (a, b, c, d, m), dp;",
        f"map phi = r, {', '.join(slice_subs(name))};",
        "ideal S1 = std(radical(phi(SG)));",
        "ideal U = std(radical(intersect(phi(W), phi(VV))));",
        '"RESULT sing_vg_equals_w8_u_v", size(reduce(S1, U)) == 0 && size(reduce(U, S1)) == 0;',
        "ideal Ts = radical(phi(T)); ideal Is = std(radical(phi(I))); ideal Es = std(radical(phi(E)));",
        "list P = minAssGTZ(Ts); int bad = 0;",
        "for (int i = 1; i <= size(P); i++) { ideal Pi = std(P[i]);"
        " if (size(reduce(Is, Pi)) != 0 && size(reduce(Es, Pi)) != 0) { bad++; } }",
        '"RESULT dependent_escapes", bad;',
        "quit;",
    ]
    res = run("\n".join(lines))
    ok = res.get("sing_vg_equals_w8_u_v") == "1" and res.get("dependent_escapes") == "0"
    return {"slice": name, "pass": ok and "singular_error" not in res, **res}


def nullity4() -> dict[str, Any]:
    rows = parallel.ordered_map(nullity4_job, list(eq.SLICE_PLANES), min_items=1)
    return {"pass": all(r["pass"] for r in rows), "rows": rows}


# ---------------------------------------------------------------------------------------------------------------
# Closure dimensions


def dims_job(job: tuple[str, str]) -> dict[str, Any]:
    name, mutation = job
    ideals = closure_ideals(mutation)
    res = run(head() + f"ideal G = {gens_text(ideals[name])};\n" + '"RESULT dim", dim(std(G));\nquit;\n')
    return {"closure": name, "mutation": mutation, "dim": res.get("dim"), "pass": res.get("dim") == str(DIMS[name])}


def closure_dims() -> dict[str, Any]:
    rows = parallel.ordered_map(dims_job, [(x, "") for x in DIMS], min_items=1)
    return {"pass": all(r["pass"] for r in rows), "rows": rows}


# ---------------------------------------------------------------------------------------------------------------
# Driver


def run_control(name: str) -> str | None:
    """One mutation control; returns the failure message when the control does not behave as required."""
    if name == "compact_rotation":
        if symmetry_job("compact")["pass"]:
            return "the compact rotation (u', v') -> (v', -u') preserved every closure ideal and Q"
    elif name == "swapped_representatives":
        if representatives(swap=True)["pass"]:
            return "the representatives of V^a_+ and V^a_- passed when swapped"
    elif name == "b9_no_cross":
        if dims_job(("B9", "b9_no_cross"))["pass"]:
            return "B9 without u' x v' = 0 kept dimension 9"
    elif name == "certificate_drops_b9":
        if certificate_job(("P4s", "Iso", "drop_b9"))["pass"]:
            return "the Iso certificate on P4s passed with B9 removed from its lower closures"
    elif name == "q_without_mu":
        row = germ_job(("V", "Np", "q_without_mu"))
        if classify_germ(row) == "A1":
            return "V with the mu' term removed from Q kept the A1 germ at N_+"
    else:
        return f"unknown control {name}"
    return None


CONTROLS = ("compact_rotation", "swapped_representatives", "b9_no_cross", "certificate_drops_b9", "q_without_mu")


def self_test() -> list[str]:
    return [msg for msg in parallel.ordered_map(run_control, list(CONTROLS), min_items=1) if msg is not None]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if shutil.which(eq.SINGULAR) is None:
        print("Singular is not on PATH")
        return 2
    if args.self_test:
        failures = self_test()
        for line in failures:
            print("FAIL", line)
        print(
            f"strata_regularity self-test: {len(CONTROLS) - len(failures)} of {len(CONTROLS)} controls behaved as"
            " required"
        )
        return 1 if failures else 0
    t0 = time.perf_counter()
    report: dict[str, Any] = {}
    timings: dict[str, float] = {}

    def step(key: str, fn: Callable[[], Any]) -> None:
        start = time.perf_counter()
        report[key] = fn()
        timings[key] = round(time.perf_counter() - start, 2)
        print(f"{key:16s} pass={report[key].get('pass')} {timings[key]:8.2f} s", flush=True)

    step("identities", identity_checks)
    step("symmetry", symmetry_job)
    step("representatives", representatives)
    step("closure_dims", closure_dims)
    step("certificate", certificate)
    step("iso", iso_checks)
    step("nullity4", nullity4)
    step("germs", germs)
    report["timings_s"] = timings
    report["total_s"] = round(time.perf_counter() - t0, 2)
    report["workers"] = parallel.workers()
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["versions"] = {
        "python": sys.version.split()[0],
        "python-flint": flint.__version__,
        "singular": eq.singular_version(),
    }
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str) + "\n", encoding="utf-8")
    failed = [k for k, v in report.items() if isinstance(v, dict) and v.get("pass") is False]
    print(f"total {report['total_s']} s; failed: {', '.join(failed) or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
