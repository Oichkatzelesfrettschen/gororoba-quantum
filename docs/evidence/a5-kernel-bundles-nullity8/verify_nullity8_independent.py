"""Independent verification of the compact-orbit, stabilizer, boundary and class statements on the A_5 nullity-8 strata.

Every multiplication comes from gororoba_quantum/cd_core.py: L_y from left_mult_matrix_exact(32, y) and the compact
octonion signs from cd_sign(8, p, q), both reached through the compact-algebra helpers of the earlier independent
verifier docs/evidence/a5-kernel-bundles/verify_kernel_bundles_independent.py (compact g_2 lifted blockwise to A_5, the
base phase, its domain lift, stabilizer solves, Casimir multiplicities, primitive circle generators, the representation
ring quotient). Split-coordinate data (representatives REPS, orbit dimensions DIMS, closure memberships, the H-tangent
vectors, nilpotent split derivations, G_2 and boost actions) come from
docs/evidence/a5-strata-regularity/verify_regularity_independent.py, and y_from_split, nullspace from
docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py. Nothing is imported from
docs/evidence/a5-kernel-bundles-nullity8/.

Coordinates. Split z'_k and original z_k = i^popcount(k) z'_k, k = 1..15; z_k = y_k + i y_(16+k); u = z_1..z_7,
mu = z_8, v = z_9..z_15. K = compact G_2 x U(1) phase acts on y; K_H = K x SO(2), where the SO(2) generator ROT sends
(u, v) to (v, -u) in original coordinates and equals i times the split boost generator. H = G_2(C) x SO(2, C) x C^*.

Test points. Each representative is moved by Gaussian-rational unipotents exp(c N) of split G_2(C) and complex or real
boosts that are listed in MOVES; the sequences differ from those of the earlier verifier. Special points are built
explicitly: su(2)-fixed points from the fixed subspace of the representative's stabilizer, coassociative isotropic
pairs for the Iso circle, and polynomial curves for the boundary limits. No random value enters.

Weights. A primitive circle generator Z has integer weights of gcd one on the base (Z = w Phi on the weight-w base
space) and a positive phase coefficient t; a native kernel weight w means Z = w J on that kernel subspace,
J = L_(e_16). The converted weight is -(w + t), the convention change R_(e_16) = -(Y_Phi + J) established by the
earlier verifier.

Usage:
    GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
        docs/evidence/a5-kernel-bundles-nullity8/verify_nullity8_independent.py \
        --out docs/evidence/a5-kernel-bundles-nullity8/verification.json
    ... verify_nullity8_independent.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter
from collections.abc import Sequence
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles"))

import verify_kernel_bundles_independent as vk  # noqa: E402

import parallel  # noqa: E402

vr = vk.vr
Gq = vr.Gq
Mat = list[list[Fraction]]
Vec = list[Fraction]

ORBITS = ("W8", "E8bar", "Iso", "X+", "X-")
REP_RANK_CLAIM = {"W8": 12, "E8bar": 12, "Iso": 15, "X+": 12, "X-": 12}
HSTAB_CLAIM = {"W8": 4, "E8bar": 5, "Iso": 5, "X+": 6, "X-": 6}
CORE_CLAIM = {"W8": ("V_2(R^7) x S^1", 12), "E8bar": ("V_2(R^7) x T^2", 13), "Iso": ("G_2", 14)}
CORE_CLAIM.update({"X+": ("V_2(R^7) x S^1", 12), "X-": ("V_2(R^7) x S^1", 12)})

# Mutation switches read by the self-test; the production run leaves every entry False.
MUTATION: dict[str, bool] = {
    "unmoved_points": False,
    "flip_j": False,
    "false_seven_branching": False,
    "same_normal_direction": False,
    "non_coassociative_pair": False,
    "radical_as_unipotent": False,
    "drop_leibniz_term": False,
}


def zero_mat(n: int, m: int | None = None) -> Mat:
    return [[Fraction(0)] * (n if m is None else m) for _ in range(n)]


# ---------------------------------------------------------------------------------------------------------------------
# Points


def cb(w: Any) -> tuple[str, Any, Any]:
    """Boost (c, s) = ((w + 1/w)/2, (w - 1/w)/2) for a Gaussian rational w; c^2 - s^2 = 1."""
    w = Gq.of(w)
    winv = Gq(1) / w
    return ("b", (w + winv) * Fraction(1, 2), (w - winv) * Fraction(1, 2))


MOVES: dict[str, list[tuple[Any, ...]]] = {
    "g1": [("u", 3, Gq(1, 2)), ("u", 25, Gq(-1, Fraction(1, 2))), cb(Gq(2, 1)), ("u", 41, Gq(0, 3))],
    "g2": [
        ("u", 17, Gq(2, -1)),
        ("u", 9, Fraction(1, 3)),
        ("b", Fraction(17, 8), Fraction(15, 8)),
        ("u", 50, Gq(1, 1)),
    ],
    "g3": [("u", 55, Gq(Fraction(1, 2), -1)), cb(Gq(1, -2)), ("u", 12, Gq(3, 1)), ("u", 36, Gq(0, -1)), ("u", 1, 2)],
}
# Fixed non-compact element moving every boundary curve and its endpoint off the recorded special points.
CURVE_MOVE: list[tuple[Any, ...]] = [("u", 7, Gq(1, 1)), cb(Gq(3, 1)), ("u", 44, Gq(0, Fraction(1, 2))), ("u", 21, -1)]


def moved(name: str, key: str) -> list[Any]:
    base = list(vr.REPS[name])
    if key == "rep" or MUTATION["unmoved_points"]:
        return base
    return vk.move(base, MOVES[key])


def split_to_y(zs: Sequence[Any]) -> Vec:
    return vk.y_of(list(zs))


def y_to_split(y: Sequence[Fraction]) -> list[Any]:
    return vk.original_to_split([Gq(y[k], y[16 + k]) for k in range(1, 16)])


def original_to_y(u: Sequence[Any], mu: Any, v: Sequence[Any]) -> Vec:
    z = [Gq.of(x) for x in [*u, mu, *v]]
    y = [Fraction(0)] * 32
    for k in range(15):
        y[k + 1] = z[k].re
        y[16 + k + 1] = z[k].im
    return y


def nullity(y: Sequence[Fraction]) -> int:
    return 32 - vk.rank(vk.l_of(list(y)))


def classify(zs: Sequence[Any]) -> str:
    """Orbit name whose closure pattern, H-orbit dimension and L_y nullity all match, else '?'."""
    pat = vr.pattern(list(zs))
    odim = vr.orbit_dim(list(zs))
    nul = nullity(split_to_y(zs))
    for name, (epat, edim, enul) in vr.EXPECTED.items():
        if pat == epat and odim == edim and nul == enul:
            return str(name)
    return "?"


def classify_y(y: Sequence[Fraction]) -> str:
    return classify(y_to_split(y))


def herm_invariants(y: Sequence[Fraction]) -> list[str]:
    """K-invariant Hermitian data (u*u, v*v, u*v, |mu|^2) over |y|^2."""
    u, mu, v = vk.z_parts(list(y))
    tot = sum((x * x for x in y), Fraction(0))
    uv = vk.hdot(u, v)
    vals = [vk.hdot(u, u).re, vk.hdot(v, v).re, uv.re, uv.im, (mu.conj() * mu).re]
    return [str(x / tot) for x in vals]


# ---------------------------------------------------------------------------------------------------------------------
# Compact stabilizer analysis


def su2_data(dstab: Sequence[Vec], kb: Sequence[Vec]) -> dict[str, Any]:
    rep = [vk.restrict(vk.kernel_lift(x), kb) for x in dstab]
    seven = [vk.lin(list(x[:14]), vk.D7) for x in dstab]
    ads = []
    for x in dstab:
        cols = [vk.bracket(x, [*vk.unit(14, b), Fraction(0)])[:14] for b in range(14)]
        ads.append(vk.transpose(cols))
    return {
        "su2_on_kernel": vk.su2_multiplicities(dstab, rep, 2),
        "su2_on_7": vk.su2_multiplicities(dstab, seven, 1),
        "su2_on_14": vk.su2_multiplicities(dstab, ads, 1),
    }


def j_matrix() -> Mat:
    return [[-x for x in r] for r in vk.J32] if MUTATION["flip_j"] else vk.J32


def circle_weights(zgen: Vec, kb: Sequence[Vec]) -> list[Fraction]:
    mz = vk.restrict(vk.kernel_lift(zgen), kb)
    mj = vk.restrict(j_matrix(), kb)
    w = [[-x for x in r] for r in vk.matmul(mj, mz)]
    cnt = Counter(vk.rational_roots(w))
    if any(c % 2 for c in cnt.values()):
        raise RuntimeError("odd real multiplicity of a kernel weight")
    return sorted(Fraction(r) for r, c in cnt.items() for _ in range(c // 2))


def compact_point(job: tuple[str, str, Vec]) -> dict[str, Any]:
    """Nullity, orbit, compact tangent rank and the connected compact stabilizer with its kernel representation."""
    label, expect, y = job
    zs = y_to_split(y)
    kb = vk.kernel(vk.l_of(y))
    stab = vk.stabilizer(y)
    res: dict[str, Any] = {"label": label, "orbit": classify(zs), "expected_orbit": expect, "nullity": len(kb)}
    res["H_orbit_complex_dim"] = vr.orbit_dim(zs)
    res["compact_tangent_rank"] = 15 - len(stab)
    res["stabilizer_dim"] = len(stab)
    res["hermitian_invariants"] = herm_invariants(y) if any(y) else []
    if res["orbit"] != expect:
        return res
    vk.restrict(vk.J32, kb)
    if stab:
        dstab = vk.derived(stab)
        cent = vk.center(stab)
        res["derived_dim"] = len(dstab)
        res["center_dim"] = len(cent)
        if len(dstab) == 3:
            res["derived_killing_negative_definite"] = vk.negative_definite(vk.killing(dstab))
            res.update(su2_data(dstab, kb))
        if len(stab) == 1:
            zgen, base_w = vk.primitive_central(stab[0])
            t = zgen[14]
            native = circle_weights(zgen, kb)
            res["circle_generator"] = [str(x) for x in zgen]
            res["circle_phase_coefficient_t"] = str(t)
            res["circle_base_weights"] = [str(w) for w in base_w]
            res["kernel_weights_native"] = [str(w) for w in native]
            res["kernel_weights_converted_-(w+t)"] = [str(w) for w in sorted(-(w + t) for w in native)]
            g2w = sorted(
                set(vk.rational_roots([[-x for x in r] for r in vk.matmul(*([vk.lin(zgen[:14], vk.D7)] * 2))]))
            )
            res["circle_g2_part_squared_weights"] = [str(w) for w in g2w]
    return res


# ---------------------------------------------------------------------------------------------------------------------
# Associative three-form and the coassociative circle locus


def phi3(x: Sequence[Fraction], y: Sequence[Fraction], z: Sequence[Fraction]) -> Fraction:
    """<x cross y, z> with the compact octonion cross product of cd_sign(8, ., .)."""
    acc = Fraction(0)
    for p in range(1, 8):
        for q in range(1, 8):
            k = p ^ q
            if k and x[p - 1] and y[q - 1]:
                acc += vk.oct_sign(p, q) * x[p - 1] * y[q - 1] * z[k - 1]
    return acc


def three_form_values(y: Sequence[Fraction]) -> list[str]:
    a, b = list(y[1:8]), list(y[17:24])
    c, d = list(y[9:16]), list(y[25:32])
    frame = [a, b, c, d]
    return [str(phi3(frame[i], frame[j], frame[k])) for i, j, k in itertools.combinations(range(4), 3)]


def coassociative_indices() -> tuple[list[int], list[int]]:
    """An associative triple {1, 2, 1^2} of cd_sign(8) units and its complement, checked through phi3."""
    e7 = [[Fraction(int(i == k)) for i in range(7)] for k in range(7)]
    assoc = [1, 2, 3]
    co = [4, 5, 6, 7]
    if phi3(e7[0], e7[1], e7[2]) == 0:
        raise RuntimeError("e1, e2, e3 are not associative")
    for i, j, k in itertools.combinations(co, 3):
        if phi3(e7[i - 1], e7[j - 1], e7[k - 1]) != 0:
            raise RuntimeError("complement is not coassociative")
    return assoc, co


def ovec(spec: dict[int, Any]) -> list[Any]:
    return [Gq.of(spec.get(k, 0)) for k in range(1, 8)]


def iso_circle_points() -> dict[str, Vec]:
    """Isotropic pairs (u, v) inside the complexified coassociative 4-plane spanned by the complement of {1, 2, 3}.

    The isotropic 2-planes of that C^4 form two rulings: span(e4 + i e5, e6 + i e7) (alpha) and
    span(e4 + i e5, e6 - i e7) (beta). Pairs from both rulings are listed; classification decides their orbit.
    """
    _assoc, co = coassociative_indices()
    a4, a5, a6, a7 = co
    i = Gq(0, 1)
    p45 = ovec({a4: 1, a5: i})
    p67 = ovec({a6: 1, a7: i})
    m67 = ovec({a6: 1, a7: -i})
    m45 = ovec({a4: 1, a5: -i})

    def comb(a: Any, x: Sequence[Any], b: Any, w: Sequence[Any]) -> list[Any]:
        return [a * p + b * q for p, q in zip(x, w, strict=True)]

    zero = Gq(0)
    pts = {
        "beta_basis": original_to_y(p45, zero, m67),
        "beta_mixed": original_to_y(comb(1, p45, 1, m67), zero, comb(Gq(1, 1), p45, -2, m67)),
        "beta_conjugate_basis": original_to_y(m45, zero, p67),
        "beta_swapped_scaled": original_to_y(comb(3, m67, 0, p45), zero, comb(Gq(0, 2), p45, Gq(1, -1), m67)),
        "alpha_basis": original_to_y(p45, zero, p67),
        "alpha_mixed": original_to_y(comb(1, p45, 2, p67), zero, comb(3, p45, -1, p67)),
    }
    if MUTATION["non_coassociative_pair"]:
        # isotropic pair whose real frame spans e1..e4, on which phi(e1, e2, e3) is nonzero
        pts = {"beta_basis": original_to_y(ovec({1: 1, 2: i}), zero, ovec({3: 1, 4: i}))}
    return pts


# ---------------------------------------------------------------------------------------------------------------------
# su(2) points away from the representatives and the compact-core points


def rot_cs(w: Any) -> tuple[Any, Any]:
    """(c, s) = ((w + 1/w)/2, (w - 1/w)/(2i)) with c^2 + s^2 = 1 for a Gaussian rational w."""
    w = Gq.of(w)
    winv = Gq(1) / w
    return (w + winv) * Fraction(1, 2), (w - winv) / Gq(0, 2)


def rotate_associative(y: Sequence[Fraction], i: int, j: int, w: Any) -> Vec:
    """Complex rotation of original coordinates i, j (0-based, inside the associative span(e1, e2, e3)) in u and v.

    On points whose u and v lie in span(e1, e2, e3) this is the action of an element of the complexified SU(2)' in
    G_2(C) that acts on span(e1, e2, e3) by SO(3, C) and commutes with the stabilizer SU(2).
    """
    c, s_ = rot_cs(w)
    u, mu, v = vk.z_parts(list(y))
    for vec in (u, v):
        a, b = vec[i], vec[j]
        vec[i], vec[j] = c * a - s_ * b, s_ * a + c * b
    return original_to_y(u, mu, v)


def boost_y(y: Sequence[Fraction], op: tuple[Any, ...]) -> Vec:
    return split_to_y(vk.move(y_to_split(y), [op]))


def _offrep_pair(name: str) -> list[tuple[str, str, Vec]]:
    y0 = split_to_y(vr.REPS[name])
    ya = boost_y(rotate_associative(rotate_associative(y0, 0, 1, Gq(2, 1)), 1, 2, Gq(1, -3)), cb(Gq(2, 1)))
    yb = rotate_associative(boost_y(y0, ("b", Fraction(17, 8), Fraction(15, 8))), 0, 2, Gq(Fraction(1, 2), 2))
    return [(f"{name}/so3_boost_a", name, ya), (f"{name}/so3_boost_b", name, yb)]


def su2_offrep_points() -> list[tuple[str, str, Vec]]:
    """Representatives moved by SO(3, C) on the associative 3-plane and by boosts, both commuting with SU(2)."""
    pairs = parallel.ordered_map(_offrep_pair, ["W8", "E8bar", "X+", "X-"], min_items=1)
    return [job for pair in pairs for job in pair]


def core_points() -> dict[str, Vec]:
    """Points where the K_H stabilizer has the dimension of the reductive quotient of H_z.

    X_+ and X_- use weight vectors of a circle in su(2)' + phase + rotation: m = e1 - i e2 and e3 in span(e1, e2, e3),
    paired with the rotation eigenvectors (1, -i) and (1, i) of (u, v).
    """
    i = Gq(0, 1)
    m = ovec({1: 1, 2: -i})
    e3 = ovec({3: 1})
    zero = Gq(0)
    beta = iso_circle_points()["beta_basis"]
    return {
        "W8": split_to_y(vr.REPS["W8"]),
        "E8bar": split_to_y(vr.REPS["E8bar"]),
        "Iso": beta,
        "X+": original_to_y(
            [a + b for a, b in zip(m, e3, strict=True)], zero, [-i * a + i * b for a, b in zip(m, e3, strict=True)]
        ),
        "X-": original_to_y(
            [a + b for a, b in zip(m, e3, strict=True)], zero, [i * a - i * b for a, b in zip(m, e3, strict=True)]
        ),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Boundary curves and Jordan-chain limits


def svec(spec: dict[int, Any]) -> list[Any]:
    return [spec.get(k, Fraction(0)) for k in range(1, 8)]


def cross_eigvecs(u0: Sequence[Fraction], lam: int) -> list[Vec]:
    cm = [vr.cross(list(u0), vr.e(j + 1)) for j in range(7)]  # column j
    mat = [[cm[j][i] - (lam if i == j else 0) for j in range(7)] for i in range(7)]
    return vk.kernel(mat)


def add7(*terms: tuple[Any, Sequence[Any]]) -> list[Any]:
    out: list[Any] = [Fraction(0)] * 7
    for c, w in terms:
        out = [a + c * b for a, b in zip(out, w, strict=True)]
    return out


def curve(u: Sequence[Sequence[Any]], mu: Sequence[Any], v: Sequence[Sequence[Any]]) -> list[list[Any]]:
    """Coefficient vectors z'_k of t^k for a split polynomial curve given by coefficient lists of u, mu, v."""
    deg = max(len(u), len(mu), len(v))
    out = []
    for k in range(deg):
        uk = list(u[k]) if k < len(u) else [Fraction(0)] * 7
        vk_ = list(v[k]) if k < len(v) else [Fraction(0)] * 7
        mk = mu[k] if k < len(mu) else Fraction(0)
        out.append(vr.join_z(uk, mk, vk_))
    return out


def null_vectors(perp_to: Sequence[Fraction], count: int, avoid: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    """First null split vectors with entries in {-1, 0, 1}, eta-orthogonal to perp_to, independent of avoid."""
    found: list[list[Fraction]] = []
    for ent in itertools.product((0, 1, -1), repeat=7):
        x = [Fraction(e) for e in ent]
        if not any(x) or vr.eta2(x, x) != 0 or vr.eta2(x, list(perp_to)) != 0:
            continue
        if vk.rank([*avoid, *found, x]) > len(avoid) + len(found):
            found.append(x)
            if len(found) == count:
                return found
    raise RuntimeError("not enough null vectors")


def incidence_curves() -> dict[str, dict[str, Any]]:
    """Per incidence: the open orbit, the boundary orbit and named curves (unmoved split coefficient lists)."""
    e1 = vr.e(1)
    fr = Fraction
    lam = fr(5, 3)
    mu0 = fr(4, 3)  # mu0^2 = (1 - lam^2) eta(e1, e1), eta(e1, e1) = -1
    plus = cross_eigvecs(e1, 1)
    minus = cross_eigvecs(e1, -1)
    n_p1, n_p2, n_m1 = plus[0], plus[1], minus[0]
    lam_e1 = [lam * x for x in e1]
    e8v = {
        "sheet+_v_moves_n1": curve([e1], [mu0], [lam_e1, n_p1]),
        "sheet+_v_moves_n2": curve([e1], [mu0], [lam_e1, n_p2]),
        "sheet+_u_moves_n1": curve([e1, n_p1], [mu0], [lam_e1]),
        "sheet+_mixed": curve([e1, add7((1, n_p1), (2, n_p2))], [mu0], [lam_e1, add7((3, n_p1), (6, n_p2))]),
        "sheet-_v_moves_n1": curve([e1], [mu0], [lam_e1, n_m1]),
    }
    i = Gq(0, 1)
    zero7 = [fr(0)] * 7
    me1 = [-x for x in e1]
    # u = (1 + t^2) e1 + t g n, mu = 2 r t with r^2 = eta(e1, e1) = -1, v = (1 - t^2) e1 + t d n
    e8va = {
        "sheet+_u_linear": curve([e1, n_p1, e1], [fr(0), 2 * i], [e1, zero7, me1]),
        "sheet+_v_linear": curve([e1, zero7, e1], [fr(0), 2 * i], [e1, n_p1, me1]),
        "sheet+_mixed_n2": curve([e1, n_p2, e1], [fr(0), 2 * i], [e1, [2 * x for x in n_p2], me1]),
        "sheet+_opposite_mu": curve([e1, n_p1, e1], [fr(0), -2 * i], [e1, zero7, me1]),
        "sheet-_v_linear": curve([e1, zero7, e1], [fr(0), 2 * i], [e1, n_m1, me1]),
        "sheet-_u_linear": curve([e1, n_m1, e1], [fr(0), 2 * i], [e1, zero7, me1]),
    }
    nn = svec({1: 1, 3: 1})  # B9 representative plane span(N, K), N = e1 + e3, K = e4 + e6
    kk = svec({4: 1, 6: 1})
    # S = {x : eta(x, N) = 0, cross(x, N) = lambda N}; unknowns (x, lambda)
    rows = [[vr.eta2(vr.e(j + 1), nn) for j in range(7)] + [fr(0)]]
    cmat = [vr.cross(vr.e(j + 1), nn) for j in range(7)]
    for r in range(7):
        rows.append([cmat[j][r] for j in range(7)] + [-nn[r]])
    sol = vk.kernel(rows)
    with_lam = [s[:7] for s in sol if s[7]]
    no_lam = [s[:7] for s in sol if not s[7] and vk.rank([nn, kk, s[:7]]) == 3]
    if not with_lam or not no_lam:
        raise RuntimeError("X+ boundary directions missing")
    w_dir, m_dir = with_lam[0], no_lam[0]  # cross(w_dir, N) = lambda N with lambda != 0; cross(m_dir, N) = 0

    def xplus(s_terms: Sequence[Sequence[Any]], sign: int = 1) -> list[list[Any]]:
        """X_+ (sign 1): s = u + v moves, d = u - v = N fixed and null; X_- (sign -1): d moves, s = N fixed."""
        moving = [list(kk), *[list(s) for s in s_terms]]
        half = fr(1, 2)
        if sign == 1:
            u = [[(a + b) * half for a, b in zip(moving[0], nn, strict=True)]] + [
                [a * half for a in s] for s in moving[1:]
            ]
            v = [[(a - b) * half for a, b in zip(moving[0], nn, strict=True)]] + [
                [a * half for a in s] for s in moving[1:]
            ]
        else:
            u = [[(b + a) * half for a, b in zip(moving[0], nn, strict=True)]] + [
                [a * half for a in s] for s in moving[1:]
            ]
            v = [[(b - a) * half for a, b in zip(moving[0], nn, strict=True)]] + [
                [-a * half for a in s] for s in moving[1:]
            ]
        return curve(u, [fr(0)], v)

    xp = {
        "s_linear_w": xplus([w_dir]),
        "s_linear_w_plus_2m": xplus([add7((1, w_dir), (2, m_dir))]),
        "s_linear_i_w": xplus([[i * x for x in w_dir]]),
        "s_linear_w_plus_n": xplus([add7((1, w_dir), (1, nn))]),
        "s_quadratic_w_then_m": xplus([w_dir, m_dir]),
        # first-order term tangent to B9 (m_dir keeps s null with cross(s, N) = 0); the normal w_dir enters at t^2
        "s_tangent_then_w": xplus([m_dir, w_dir]),
        "s_tangent_then_i_w": xplus([m_dir, [i * x for x in w_dir]]),
    }
    s_null = null_vectors(kk, 2, [kk, nn])
    d_null = null_vectors(nn, 2, [kk, nn])

    def w8(s1: Sequence[Any], d1: Sequence[Any]) -> list[list[Any]]:
        u = [
            [(a + b) * fr(1, 2) for a, b in zip(kk, nn, strict=True)],
            [(a + b) * fr(1, 2) for a, b in zip(s1, d1, strict=True)],
        ]
        v = [
            [(a - b) * fr(1, 2) for a, b in zip(kk, nn, strict=True)],
            [(a - b) * fr(1, 2) for a, b in zip(s1, d1, strict=True)],
        ]
        return curve(u, [fr(0)], v)

    xm = {
        "d_linear_w": xplus([w_dir], -1),
        "d_linear_i_w": xplus([[i * x for x in w_dir]], -1),
        "d_linear_w_plus_2m": xplus([add7((1, w_dir), (2, m_dir))], -1),
        "d_quadratic_w_then_m": xplus([w_dir, m_dir], -1),
        "d_tangent_then_w": xplus([m_dir, w_dir], -1),
    }
    w8b = {
        "d_only_a": w8(zero7, d_null[0]),
        "d_only_b": w8(zero7, d_null[1]),
        "s_and_d_a": w8(s_null[0], d_null[0]),
        "s_and_d_b": w8(s_null[1], d_null[1]),
        "s_a_d_b": w8(s_null[0], d_null[1]),
    }
    out: dict[str, dict[str, Any]] = {
        "E8bar->V": {"open": "E8bar", "boundary": "V", "curves": e8v},
        "E8bar->Va+": {"open": "E8bar", "boundary": "Va+", "curves": e8va},
        "X+->B9": {"open": "X+", "boundary": "B9", "curves": xp},
        "X-->B9": {"open": "X-", "boundary": "B9", "curves": xm},
        "W8->B9": {"open": "W8", "boundary": "B9", "curves": w8b},
    }
    if MUTATION["same_normal_direction"]:
        for inc in out.values():
            first = next(iter(inc["curves"].values()))
            inc["curves"] = {k: first for k in inc["curves"]}
    return out


def eval_curve(coeffs: Sequence[Sequence[Any]], t: Fraction) -> list[Any]:
    out: list[Any] = [Fraction(0)] * 15
    for k, w in enumerate(coeffs):
        out = [a + (t**k) * b for a, b in zip(out, w, strict=True)]
    return out


SAMPLE_T = [Fraction(k, 3) for k in range(1, 20)]
GENERIC_T = (Fraction(1, 2), Fraction(1, 3))


def limit_plane(ys: Sequence[Vec], target: int, max_order: int = 12) -> tuple[list[Vec], int]:
    """Leading terms x_0 of Jordan chains sum_j L_(y_j) x_(i-j) = 0 (i <= order) once their span has dim target."""
    mats = [vk.l_of(list(y)) for y in ys]
    deg = len(mats) - 1
    for order in range(max_order + 1):
        size = 32 * (order + 1)
        big = [[Fraction(0)] * size for _ in range(size)]
        for i in range(order + 1):
            for j in range(order + 1):
                k = i - j
                if 0 <= k <= deg:
                    m = mats[k]
                    for r in range(32):
                        row = big[32 * i + r]
                        for c in range(32):
                            if m[r][c]:
                                row[32 * j + c] = m[r][c]
        sols = vk.kernel(big)
        lead = vk.kernel_complement_basis([s[:32] for s in sols if any(s[:32])])
        if len(lead) == target:
            return lead, order
        if len(lead) < target:
            raise RuntimeError("leading space below the generic nullity")
    raise RuntimeError("Jordan-chain order limit reached")


def curve_job(job: tuple[str, str, str, str, list[list[Any]]]) -> dict[str, Any]:
    inc, cname, open_orb, bnd, coeffs = job
    mc = [vk.move(list(w), CURVE_MOVE) for w in coeffs]
    deg = len(mc) - 1
    bound = 4 * deg  # closure generators have degree <= 4
    closure_ok = all(vr.membership(eval_curve(mc, t))[open_orb] for t in SAMPLE_T[: bound + 1])
    gen_orbit = [classify(eval_curve(mc, t)) for t in GENERIC_T]
    end_orbit = classify(mc[0])
    ys = [split_to_y(w) for w in mc]
    head = {
        "incidence": inc,
        "curve": cname,
        "degree": deg,
        "closure_identity_samples": bound + 1,
        "closure_identity_ok": closure_ok,
        "generic_orbit_at_t=1/2,1/3": gen_orbit,
        "endpoint_orbit": end_orbit,
        "endpoint_y": [str(x) for x in ys[0]],
    }
    if gen_orbit != [open_orb] * 2 or end_orbit != bnd:
        return {**head, "valid": False}
    lead, order = limit_plane(ys, 8)
    k0 = vk.kernel(vk.l_of(ys[0]))
    contained = vk.rank([*k0, *lead]) == len(k0)
    try:
        vk.restrict(vk.J32, lead)
        j_inv = True
    except RuntimeError:
        j_inv = False
    stab0 = vk.stabilizer(ys[0])
    inv = []
    for x in stab0:
        try:
            vk.restrict(vk.kernel_lift(x), lead)
            inv.append(True)
        except RuntimeError:
            inv.append(False)
    return {
        **head,
        "valid": True,
        "boundary_kernel_dim": len(k0),
        "chain_order": order,
        "limit_dim": len(lead),
        "limit_in_boundary_kernel": contained,
        "limit_J_invariant": j_inv,
        "endpoint_compact_stabilizer_dim": len(stab0),
        "limit_invariant_under_endpoint_stabilizer": inv,
        "_lead": [[str(x) for x in v] for v in lead],
    }


def _iso_three_forms(key: str) -> Any:
    """Three-form values at the Iso representative moved by the named non-compact element."""
    return three_form_values(split_to_y(moved("Iso", key)))


def compare_limits(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    leads = [[[Fraction(x) for x in v] for v in r["_lead"]] for r in rows]
    names = [r["curve"] for r in rows]
    classes: list[list[int]] = []
    for idx, lead in enumerate(leads):
        for cl in classes:
            if vk.rank([*leads[cl[0]], *lead]) == 8:
                cl.append(idx)
                break
        else:
            classes.append([idx])
    pair = {
        f"{names[a]}|{names[b]}": vk.rank([*leads[a], *leads[b]]) - 8
        for a, b in itertools.combinations(range(len(leads)), 2)
    }
    return {
        "distinct_limits": len(classes),
        "classes": [[names[i] for i in cl] for cl in classes],
        "pairwise_extra_dims": pair,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Complex point stabilizer in H and its reductive quotient


def realify(m: Sequence[Sequence[Any]]) -> Mat:
    n = len(m)
    out = zero_mat(2 * n)
    for i in range(n):
        for j in range(n):
            g = Gq.of(m[i][j])
            out[i][j], out[i][n + j] = g.re, -g.im
            out[n + i][j], out[n + i][n + j] = g.im, g.re
    return out


def h_generators() -> list[Mat]:
    """Realified 30 x 30 matrices of a real basis of h = g_2(C) + so(2, C) + C acting on split C^15."""
    comp: list[list[list[Any]]] = []
    for d in vr.DERS:
        t = [[Fraction(0)] * 15 for _ in range(15)]
        for a in range(7):
            for b in range(7):
                t[a][b] = d[a][b]
                t[8 + a][8 + b] = d[a][b]
        comp.append(t)
    comp.append([[Fraction(int(a == b)) for b in range(15)] for a in range(15)])
    boost = [[Fraction(0)] * 15 for _ in range(15)]
    for a in range(7):
        boost[a][8 + a] = Fraction(1)
        boost[8 + a][a] = Fraction(1)
    comp.append(boost)
    out = []
    for t in comp:
        out.append(realify(t))
        out.append(realify([[Gq(0, 1) * x for x in r] for r in t]))
    return out


HGEN = h_generators()


def flat(m: Mat) -> Vec:
    return [x for r in m for x in r]


def fmat(m: Mat) -> Any:
    return vk.fm(m)


def mtrace(m: Any) -> Fraction:
    return sum((Fraction(int(m[i, i].p), int(m[i, i].q)) for i in range(m.nrows())), Fraction(0))


def mzero(m: Any) -> bool:
    return all(m[i, j] == 0 for i in range(m.nrows()) for j in range(m.ncols()))


def levi_analysis(job: tuple[str, list[Any]]) -> dict[str, Any]:
    """dim_C h_z, its radical (Killing complement of the derived algebra) and the nilpotent part of the radical."""
    label, zs = job
    zr = [Gq.of(x).re for x in zs] + [Gq.of(x).im for x in zs]
    cols = [vk.matvec(g, zr) for g in HGEN]
    sols = vk.kernel(vk.transpose(cols))
    mats = [vk.lin(s, HGEN) for s in sols]
    n = len(mats)
    fl = [flat(m) for m in mats]
    fms = [fmat(m) for m in mats]

    def coords(m: Any) -> Vec:
        c = vk.coords_in_span(fl, flat(vk.to_rows(m)))
        if c is None:
            raise RuntimeError("stabilizer not closed")
        return c

    brk = [[coords(fms[a] * fms[b] - fms[b] * fms[a]) for b in range(n)] for a in range(n)]
    ad = [vk.transpose([brk[a][b] for b in range(n)]) for a in range(n)]
    kill = [[sum((vk.matmul(ad[a], ad[b])[i][i] for i in range(n)), Fraction(0)) for b in range(n)] for a in range(n)]
    derived = vk.kernel_complement_basis([brk[a][b] for a in range(n) for b in range(n) if any(brk[a][b])])
    rad = vk.kernel([vk.matvec(kill, w) for w in derived]) if derived else [vk.unit(n, k) for k in range(n)]
    rad_m = [fmat(vk.lin(c, mats)) for c in rad]
    # Unipotent radical: the radical of the trace form tr(XY) on rad. On an algebraic torus the trace form of a
    # faithful representation is positive definite on the rational cocharacter span, and nilpotent elements of a
    # solvable linear algebra have zero diagonal in a common triangular basis, so the form's radical is exactly the
    # set of nilpotent elements.
    if MUTATION["radical_as_unipotent"]:
        nil = rad
    else:
        rows = [[mtrace(a * b) for b in rad_m] for a in rad_m]
        rows_q = [list(r) for r in rows]
        sol = vk.kernel(rows_q) if rows_q else []
        nil = [[sum((s_[i] * rad[i][k] for i in range(len(rad))), Fraction(0)) for k in range(n)] for s_ in sol]
    nil_m = [fmat(vk.lin(c, mats)) for c in nil]
    nilpotent = all(mzero(m**30) for m in nil_m)
    ideal = True
    for m in fms:
        for q in nil_m:
            c = coords(m * q - q * m)
            if nil and vk.rank([*nil, c]) > len(nil):
                ideal = False
    rad_mod_nil_abelian = all(
        vk.rank([*nil, coords(a * b - b * a)]) == len(nil) if nil else mzero(a * b - b * a)
        for a, b in itertools.combinations(rad_m, 2)
    )
    if n % 2 or len(nil) % 2:
        raise RuntimeError("realified dimensions must be even")
    return {
        "label": label,
        "h_z_complex_dim": n // 2,
        "radical_complex_dim": len(rad) // 2,
        "unipotent_radical_complex_dim": len(nil) // 2,
        "unipotent_part_nilpotent": nilpotent,
        "unipotent_part_ideal": ideal,
        "radical_mod_unipotent_abelian": rad_mod_nil_abelian,
        "reductive_quotient_complex_dim": (n - len(nil)) // 2,
    }


ROT = zero_mat(32)
for _k in range(1, 8):
    ROT[_k][8 + _k] = Fraction(1)
    ROT[8 + _k][_k] = Fraction(-1)
    ROT[16 + _k][24 + _k] = Fraction(1)
    ROT[24 + _k][16 + _k] = Fraction(-1)


def kh_stabilizer(job: tuple[str, Vec]) -> dict[str, Any]:
    """Stabilizer of y in K_H = G_2 x U(1) phase x SO(2) rotation; derived part, central projection, core dims."""
    label, y = job
    cols = [vk.matvec(vk.D32[a], y) for a in range(14)] + [vk.matvec(vk.PHASE, y), vk.matvec(ROT, y)]
    sols = vk.kernel(vk.transpose(cols))
    kstab = vk.stabilizer(y)
    res: dict[str, Any] = {"label": label, "KH_stabilizer_dim": len(sols), "K_stabilizer_dim": len(kstab)}
    res["central_projection_rank_(phase,rot)"] = vk.rank([[s[14], s[15]] for s in sols]) if sols else 0
    der = vk.derived([s[:15] for s in sols]) if sols else []
    res["derived_dim"] = len(der)
    if len(der) == 3:
        res["derived_killing_negative_definite"] = vk.negative_definite(vk.killing(der))
        res["derived_on_7"] = vk.su2_multiplicities(der, [vk.lin(list(x[:14]), vk.D7) for x in der], 1)
    res["K_H_orbit_dim"] = 16 - len(sols)
    res["K_orbit_dim"] = 15 - len(kstab)
    return res


def ring_from_point(row: dict[str, Any]) -> tuple[dict[int, int], dict[int, int], dict[str, Any]]:
    """Measured SU(2) restrictions of 7 and 14 and the quotient Z[V_1]/(rho_7 - 7, rho_14 - 14)."""
    seven = vk.measured_multiplicities(row["su2_on_7"])
    fourteen = vk.measured_multiplicities(row["su2_on_14"])
    if MUTATION["false_seven_branching"]:
        seven = {0: 5, 1: 1}  # rank-preserving false branching 5 + t
    return seven, fourteen, vk.ring_quotient(seven, fourteen)


# ---------------------------------------------------------------------------------------------------------------------
# Run


def _stage_point(job: tuple[str, str]) -> tuple[str, str, Vec]:
    name, key = job
    return (f"{name}/{key}", name, split_to_y(moved(name, key)))


def stage_points() -> list[tuple[str, str, Vec]]:
    keys = [(name, key) for name in ORBITS for key in ("rep", "g1", "g2", "g3")]
    return parallel.ordered_map(_stage_point, keys, min_items=1)


def run_all() -> dict[str, Any]:
    t0 = time.time()
    result: dict[str, Any] = {}
    ders = vk.compact_derivations()
    result["compact_g2_dimension"] = len(ders)
    if len(ders) != 14:
        raise RuntimeError(f"compact derivation space has dimension {len(ders)}")
    rot_skew = all(ROT[i][j] == -ROT[j][i] for i in range(32) for j in range(32))
    rot_central = vk.comm(ROT, vk.PHASE) == zero_mat(32) and all(vk.comm(ROT, d) == zero_mat(32) for d in vk.D32)
    # ROT = i (split boost generator) at a moved point: compare y-images
    zt = moved("W8", "g1")
    btan = vr.h_tangent(zt)[15]
    rot_is_i_boost = vk.matvec(ROT, split_to_y(zt)) == split_to_y([Gq(0, 1) * Gq.of(x) for x in btan])
    result["rotation_generator"] = {
        "skew": rot_skew,
        "central_in_K_H": rot_central,
        "equals_i_times_split_boost": rot_is_i_boost,
    }

    # Statement 1
    pts = stage_points()
    rows = parallel.ordered_map(compact_point, pts, min_items=1)
    by = {r["label"]: r for r in rows}
    rep_ranks = {n: by[f"{n}/rep"]["compact_tangent_rank"] for n in ORBITS}
    in_orbit = all(r["orbit"] == r["expected_orbit"] and r["nullity"] == 8 for r in rows)
    generic = {n: max(by[f"{n}/{k}"]["compact_tangent_rank"] for k in ("g1", "g2", "g3")) for n in ORBITS}
    s1 = in_orbit and rep_ranks == REP_RANK_CLAIM and all(v == 15 for v in generic.values())
    result["statement_1"] = {
        "points": {
            r["label"]: {k: r[k] for k in ("orbit", "nullity", "H_orbit_complex_dim", "compact_tangent_rank")}
            for r in rows
        },
        "rep_ranks": rep_ranks,
        "claimed_rep_ranks": REP_RANK_CLAIM,
        "max_moved_rank": generic,
        "all_points_in_their_orbit_nullity_8": in_orbit,
        "generic_argument": (
            "rank 15 at one point of the connected complex orbit makes rank 15 an open nonempty real-analytic "
            "condition, hence generic; stabilizer 0 makes the kernel representation 4 V_0"
        ),
        "verdict": "confirmed" if s1 else "refuted",
    }

    # Statement 2
    off_jobs = su2_offrep_points()
    cores = core_points()
    core_jobs = [(f"{n}/core", n, cores[n]) for n in ("X+", "X-")]
    circle = iso_circle_points()
    circle_jobs = [(f"Iso/{k}", "Iso", y) for k, y in circle.items()]
    all_jobs = off_jobs + core_jobs + circle_jobs
    s2_rows = parallel.ordered_map(compact_point, all_jobs, min_items=1)
    ymap = {lab: y for lab, _e, y in all_jobs}
    forms = parallel.ordered_map(three_form_values, [ymap[r["label"]] for r in s2_rows], min_items=1)
    for r, values in zip(s2_rows, forms, strict=True):
        r["three_form_values"] = values
    s2_by = {r["label"]: r for r in s2_rows}
    iso_keys = ("rep", "g1", "g2", "g3")
    iso_forms = parallel.ordered_map(_iso_three_forms, list(iso_keys), min_items=1)
    iso_neg = [
        {
            "label": by[f"Iso/{key}"]["label"],
            "three_form_values": values,
            "stabilizer_dim": by[f"Iso/{key}"]["stabilizer_dim"],
        }
        for key, values in zip(iso_keys, iso_forms, strict=True)
    ]
    expect_kernel = {
        "W8": {"V_1": 2},
        "E8bar": {"V_0": 2, "V_1": 1},
        "X+": {"V_0": 2, "V_1": 1},
        "X-": {"V_0": 2, "V_1": 1},
    }
    su2_keys = ("stabilizer_dim", "derived_killing_negative_definite", "su2_on_kernel", "su2_on_7", "su2_on_14")
    su2_ok = True
    su2_summary: dict[str, Any] = {}
    for name in ("W8", "E8bar", "X+", "X-"):
        rep = by[f"{name}/rep"]
        others = [r for r in s2_rows if r["label"].startswith(name + "/") and r["expected_orbit"] == name]
        distinct = [r for r in others if r["hermitian_invariants"] != rep["hermitian_invariants"]]
        good = all(
            r["orbit"] == name
            and r["stabilizer_dim"] == 3
            and r.get("derived_killing_negative_definite")
            and r.get("su2_on_kernel") == expect_kernel[name]
            and r.get("su2_on_7") == {"V_0": 3, "V_1": 2}
            for r in [rep, *others]
        )
        su2_summary[name] = {
            "rep": {k: rep.get(k) for k in su2_keys},
            "off_rep_points": {
                r["label"]: {k: r.get(k) for k in ("orbit", *su2_keys, "hermitian_invariants")} for r in others
            },
            "off_rep_points_outside_K_R+_orbit_of_rep": len(distinct),
            "claimed_kernel": expect_kernel[name],
            "ok": bool(good and len(distinct) >= 2),
        }
        su2_ok = su2_ok and su2_summary[name]["ok"]
    iso_rows = [r for r in s2_rows if r["label"].startswith("Iso/") and r["orbit"] == "Iso"]
    other_ruling = {r["label"]: r["orbit"] for r in s2_rows if r["label"].startswith("Iso/") and r["orbit"] != "Iso"}
    claim_circle = sorted(Fraction(x) for x in (0, -3, -3, -2))
    circ_ok = len(iso_rows) >= 3 and all(
        all(v == "0" for v in r["three_form_values"])
        and r["stabilizer_dim"] == 1
        and [Fraction(x) for x in r["kernel_weights_converted_-(w+t)"]] == claim_circle
        for r in iso_rows
    )
    neg_ok = all(any(v != "0" for v in r["three_form_values"]) and r["stabilizer_dim"] == 0 for r in iso_neg)
    circle_keys = (
        "orbit",
        "three_form_values",
        "stabilizer_dim",
        "circle_phase_coefficient_t",
        "circle_base_weights",
        "kernel_weights_native",
        "kernel_weights_converted_-(w+t)",
        "circle_g2_part_squared_weights",
    )
    result["statement_2"] = {
        "su2_strata": su2_summary,
        "iso_coassociative_points_in_Iso": {r["label"]: {k: r.get(k) for k in circle_keys} for r in iso_rows},
        "coassociative_pairs_outside_Iso": other_ruling,
        "iso_nonvanishing_points": iso_neg,
        "claimed_circle_weights_converted": [str(x) for x in claim_circle],
        "weight_normalization": (
            "primitive circle generator Z, integer base weights of gcd 1, positive phase coefficient t; native kernel "
            "weight w means Z = w J; converted weight -(w + t)"
        ),
        "verdict": "confirmed" if (su2_ok and circ_ok and neg_ok) else "refuted",
    }

    # Statement 3
    incs = incidence_curves()
    cjobs = [(inc, cname, d["open"], d["boundary"], c) for inc, d in incs.items() for cname, c in d["curves"].items()]
    crow = parallel.ordered_map(curve_job, cjobs, min_items=1)
    s3: dict[str, Any] = {}
    s3_ok = True
    rows_by_inc = {inc: [r for r in crow if r["incidence"] == inc] for inc in incs}
    valid_by_inc = {inc: [r for r in rows if r["valid"]] for inc, rows in rows_by_inc.items()}
    cmps = dict(
        zip(incs, parallel.ordered_map(compare_limits, [valid_by_inc[inc] for inc in incs], min_items=1), strict=True)
    )
    for inc, d in incs.items():
        rr_all = rows_by_inc[inc]
        rr = valid_by_inc[inc]
        cmp = cmps[inc]
        same_end = len({json.dumps(r["endpoint_y"]) for r in rr}) == 1
        valid = all(
            r["closure_identity_ok"]
            and r["generic_orbit_at_t=1/2,1/3"] == [d["open"]] * 2
            and r["endpoint_orbit"] == d["boundary"]
            and r["limit_in_boundary_kernel"]
            and r["limit_J_invariant"]
            and r["boundary_kernel_dim"] == 12
            for r in rr
        )
        s3[inc] = {
            "curves": [{k: v for k, v in r.items() if k not in ("_lead", "endpoint_y")} for r in rr_all],
            "valid_curves": len(rr),
            "common_endpoint": same_end,
            "all_curves_valid": valid,
            **cmp,
        }
        s3_ok = s3_ok and valid and same_end
    enough = all(v["valid_curves"] >= 3 for v in s3.values())
    canonical = all(s3[k]["distinct_limits"] == 1 for k in ("X+->B9", "X-->B9"))
    dependent = [inc for inc in s3 if not inc.startswith("X") and s3[inc]["distinct_limits"] > 1]
    s3_verdict = "confirmed" if (s3_ok and enough and canonical and len(dependent) == 3) else "refuted"
    if s3_ok and enough and canonical and 0 < len(dependent) < 3:
        s3_verdict = "partly confirmed"
    result["statement_3"] = {
        "incidences": s3,
        "path_dependent_incidences": dependent,
        "X+-->B9_single_limit": canonical,
        "every_incidence_has_3_valid_curves": enough,
        "containment_note": "containment of every limit in the boundary kernel is automatic (L_(y_0) x_0 = 0)",
        "canonical_note": "finite tests can only falsify canonicity: no counterexample among the listed X+ approaches",
        "verdict": s3_verdict,
    }

    # Statement 4
    ljobs = [(f"{n}/{k}", moved(n, k)) for n in ORBITS for k in ("rep", "g1")]
    lev = parallel.ordered_map(levi_analysis, ljobs, min_items=1)
    lby = {r["label"]: r for r in lev}
    khjobs = [(f"{n}/rep", split_to_y(vr.REPS[n])) for n in ORBITS] + [(f"{n}/core", cores[n]) for n in ORBITS]
    kh = parallel.ordered_map(kh_stabilizer, khjobs, min_items=1)
    khby = {r["label"]: r for r in kh}
    core_orbit = dict(
        zip(ORBITS, parallel.ordered_map(classify_y, [cores[n] for n in ORBITS], min_items=1), strict=True)
    )
    s4_rows = {}
    s4_ok = True
    for n in ORBITS:
        hz = [lby[f"{n}/{k}"]["h_z_complex_dim"] for k in ("rep", "g1")]
        red = [lby[f"{n}/{k}"]["reductive_quotient_complex_dim"] for k in ("rep", "g1")]
        khr = khby[f"{n}/core"]
        core_dim = 16 - red[0]
        ok = (
            hz == [HSTAB_CLAIM[n]] * 2
            and red[0] == red[1]
            and core_dim == CORE_CLAIM[n][1]
            and khr["KH_stabilizer_dim"] == red[0]
            and core_orbit[n] == n
            and all(
                lby[f"{n}/{k}"]["unipotent_part_nilpotent"] and lby[f"{n}/{k}"]["unipotent_part_ideal"]
                for k in ("rep", "g1")
            )
        )
        s4_rows[n] = {
            "h_z_complex_dim_rep_moved": hz,
            "claimed_h_z_dim": HSTAB_CLAIM[n],
            "reductive_quotient_dim_rep_moved": red,
            "core_dim_16_minus_reductive": core_dim,
            "claimed_core": CORE_CLAIM[n],
            "K_H_stabilizer_at_core_point": khr,
            "K_H_stabilizer_at_rep": khby[f"{n}/rep"],
            "core_point_orbit": core_orbit[n],
            "ok": ok,
        }
        s4_ok = s4_ok and ok
    v2_dim = vk.g2_orbit_dim([vk.unit(7, 0), vk.unit(7, 1)])
    result["statement_4"] = {
        "orbits": s4_rows,
        "levi_rows": lev,
        "dim_V2_R7_from_g2_orbit_of_orthonormal_pair": v2_dim,
        "dim_G2": len(ders),
        "core_dims_from_claims": {"V_2 x S^1": v2_dim + 1, "V_2 x T^2": v2_dim + 2, "G_2": len(ders)},
        "verdict": "confirmed (dimensions computed; homotopy steps are arguments)" if s4_ok else "refuted",
    }

    # Statement 5
    seven = {}
    fourteen = {}
    rings = {}
    for n in ("W8", "E8bar", "X+", "X-"):
        seven[n], fourteen[n], rings[n] = ring_from_point(by[f"{n}/rep"])
    ring_ok = all(r["reduced_quotient"] == "Z/2" and r["rho7_minus_7_in_x"] == [0, 2] for r in rings.values())
    # classes in Z[x]/(2x, x^2): reduced class = (number of V_1 copies) x mod 2
    classes = {}
    core_fiber = {"W8": by["W8/rep"], "E8bar": by["E8bar/rep"], "X+": s2_by["X+/core"], "X-": s2_by["X-/core"]}
    for n, row in core_fiber.items():
        k1 = row["su2_on_kernel"].get("V_1", 0) if row.get("su2_on_kernel") else -1
        k0 = row["su2_on_kernel"].get("V_0", 0) if row.get("su2_on_kernel") else -1
        classes[n] = {"core_point": row["label"], "bundle": f"C^{k0} + {k1} xi", "reduced_class": f"{k1 % 2} x"}
    # E8-bar core: rotated representative is outside the K-orbit but has the same K-stabilizer and fiber
    y0 = split_to_y(vr.REPS["E8bar"])
    c, s = Fraction(3, 5), Fraction(4, 5)
    proj = [Fraction(int(i not in (0, 8, 16, 24))) for i in range(32)]
    rot = [[(1 + (c - 1) * proj[i] if i == j else 0) + s * ROT[i][j] for j in range(32)] for i in range(32)]
    norm_ok = vk.matmul(vk.transpose(rot), rot) == vk.identity(32)
    yr = vk.matvec(rot, y0)
    rot_row = compact_point(("E8bar/rotated", "E8bar", yr))
    same_stab = vk.rank([*vk.stabilizer(y0), *vk.stabilizer(yr)]) == 3
    e8_core = {
        "rotation_orthogonal": norm_ok,
        "rotated_orbit": rot_row["orbit"],
        "rotated_hermitian_invariants": rot_row["hermitian_invariants"],
        "rep_hermitian_invariants": by["E8bar/rep"]["hermitian_invariants"],
        "rotated_outside_K_orbit": rot_row["hermitian_invariants"] != by["E8bar/rep"]["hermitian_invariants"],
        "same_K_stabilizer_subalgebra": same_stab,
        "rotated_fiber": rot_row.get("su2_on_kernel"),
    }
    iso_core = khby["Iso/core"]
    circ_first = s2_by["Iso/beta_basis"]
    t_iso = Fraction(circ_first.get("circle_phase_coefficient_t", "0"))
    g2sq = [Fraction(x) for x in circ_first.get("circle_g2_part_squared_weights", [])]
    g2_weights = sorted({Fraction(isqrt(w.numerator), isqrt(w.denominator)) for w in g2sq if w >= 0})
    perfect = bool(g2sq) and all(w * w == x for w, x in zip(g2_weights, sorted(set(g2sq)), strict=True))
    finite_trivial = perfect and t_iso != 0 and all((w / t_iso).denominator == 1 for w in g2_weights)
    s5_ok = (
        ring_ok
        and classes["W8"]["reduced_class"] == "0 x"
        and all(classes[n]["reduced_class"] == "1 x" for n in ("E8bar", "X+", "X-"))
        and all(
            s4_rows[n]["K_H_stabilizer_at_core_point"]["K_orbit_dim"]
            == s4_rows[n]["K_H_stabilizer_at_core_point"]["K_H_orbit_dim"]
            for n in ("W8", "X+", "X-", "Iso")
        )
        and e8_core["rotated_outside_K_orbit"]
        and e8_core["same_K_stabilizer_subalgebra"]
        and e8_core["rotated_fiber"] == {"V_0": 2, "V_1": 1}
        and finite_trivial
        and iso_core["central_projection_rank_(phase,rot)"] == 2
    )
    result["statement_5"] = {
        "measured_restrictions_7": {n: seven[n] for n in seven},
        "measured_restrictions_14": {n: fourteen[n] for n in fourteen},
        "rings": rings,
        "classes_from_core_fibers": classes,
        "E8bar_full_core": e8_core,
        "Iso_core": {
            "phase_coefficient_t": str(t_iso),
            "g2_part_weights_on_R7": [str(w) for w in g2_weights],
            "circle_meets_G2_trivially": finite_trivial,
            "K_H_stabilizer": iso_core,
        },
        "W8_note": (
            "2 xi has reduced class 2x = 0, so it is stably trivial; rank 4 over a 12-dimensional core lies outside "
            "the stable range, so actual triviality is undecided"
        ),
        "verdict": "confirmed (fibers and K-bookkeeping computed; bundle identifications are arguments)"
        if s5_ok
        else "refuted",
    }
    return {"result": result, "seconds": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------------------------------------------------
# Self-test


def control(name: str) -> str | None:
    """Run the mutated property; return a description when the downstream value changes, None when uncaught."""
    for k in MUTATION:
        MUTATION[k] = k == name
    try:
        if name == "unmoved_points":
            r = compact_point(("W8/g1", "W8", split_to_y(moved("W8", "g1"))))
            return f"W8 moved rank {r['compact_tangent_rank']}" if r["compact_tangent_rank"] != 15 else None
        if name == "flip_j":
            y = next(iter(iso_circle_points().values()))
            w = compact_point(("Iso/c", "Iso", y))["kernel_weights_converted_-(w+t)"]
            claim = [str(x) for x in sorted(Fraction(v) for v in (0, -3, -3, -2))]
            return f"Iso weights {w}" if w != claim else None
        if name == "false_seven_branching":
            row = compact_point(("W8/rep", "W8", split_to_y(vr.REPS["W8"])))
            ring = ring_from_point(row)[2]
            return f"ring {ring['reduced_quotient']}" if ring["reduced_quotient"] != "Z/2" else None
        if name == "same_normal_direction":
            d = incidence_curves()["E8bar->V"]
            rows = [curve_job(("E8bar->V", k, d["open"], d["boundary"], c)) for k, c in d["curves"].items()]
            n = compare_limits(rows)["distinct_limits"]
            return f"E8bar->V distinct limits {n}" if n == 1 else None
        if name == "non_coassociative_pair":
            y = next(iter(iso_circle_points().values()))
            r = compact_point(("Iso/c", "Iso", y))
            return f"stabilizer {r['stabilizer_dim']}, orbit {r['orbit']}" if r["stabilizer_dim"] != 1 else None
        if name == "radical_as_unipotent":
            r = levi_analysis(("W8/rep", list(vr.REPS["W8"])))
            red = r["reductive_quotient_complex_dim"]
            return f"W8 reductive dim {red}, nilpotent {r['unipotent_part_nilpotent']}" if red != 4 else None
        if name == "drop_leibniz_term":
            vk.MUTATION["drop_leibniz_term"] = True
            dim = len(vk.compact_derivations())
            return f"derivation dimension {dim}" if dim != 14 else None
        raise ValueError(name)
    finally:
        for k in MUTATION:
            MUTATION[k] = False
        vk.MUTATION["drop_leibniz_term"] = False


def self_test() -> int:
    names = list(MUTATION)
    report = dict(zip(names, parallel.ordered_map(control, names, min_items=1), strict=True))
    print(json.dumps({"controls": report}, indent=1))
    failures = [n for n, msg in report.items() if msg is None]
    if failures:
        print(f"uncaught mutations: {failures}")
        return 1
    print("self-test: every mutation caught")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        ap.error("--out is required without --self-test")
    start = time.time()
    run = run_all()
    out = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {"python": platform.python_version(), "python_flint": flint.__version__},
        "workers": parallel.workers(),
        **run["result"],
        "total_s": round(time.time() - start, 1),
    }
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"total_s={out['total_s']}")
    print(json.dumps({k: out[k]["verdict"] for k in out if k.startswith("statement_")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
