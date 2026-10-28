"""First-principles checks behind the verified results of an LLM-persona corpus, and the run designs they admit.

The corpus mixes a review of a mathematics reference draft (Lie algebras, E8, triality, the Albert algebra,
L-infinity algebras, spectral triples), a speculative "scalar-ZPE / crystalline aether / E8" synthesis, and a
derivation of the Sugawara construction, the Coulomb gas and the Kac determinant. Every number and identity that
docs/notes/topics/persona-corpus-verified-results.md tags [E] comes from a function here, which raises when a
stated identity or inequality fails. ascella_two_photon_associator computes the ideal laws of the Ascella run the
note proposes. existing_note_rechecks and algebra_rechecks recompute, independently of the scripts that own
them, the numbers of the repository's earlier notes (pais-claims-falsification.md,
qpu_vacuum_cd_review_reconciliation.md, octonion_structure_checks.md).

Exact results use integer, rational or FLINT arithmetic: the Albert-algebra symmetry dimensions are integer ranks,
the Kac determinant, Coulomb-gas weights and Sugawara central charge are SymPy identities in the symbols h, m and k.
Physical constants are CODATA values from scipy.constants.

Usage:
    "$PYTHON" scripts/persona_corpus_checks.py [--audit] [--out FILE]

--audit adds the level-5 Kac determinant (about 5 s); the default stops at level 4.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections.abc import Callable
from fractions import Fraction
from functools import cache
from pathlib import Path

import flint
import numpy as np
import sympy as sp
from scipy import constants as sc
from scipy import integrate
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

C = sc.c
G = sc.G
HBAR = sc.hbar
EPS0 = sc.epsilon_0
MU0 = sc.mu_0
ALPHA = sc.fine_structure
E_CHARGE = sc.e
M_E = sc.m_e
EV = sc.electron_volt
GEV = 1e9 * EV
GOLDEN = (1 + math.sqrt(5)) / 2

# Inputs the corpus states, quoted as numbers so each check names what it tests.
CORPUS_FREQUENCY_HZ = 148.0  # "The frequency selection (148Hz)"
CORPUS_CASIMIR_ENHANCEMENT = 1e3  # "amplify Casimir force by factor eta > 10^3"
TOURMALINE_EPSILON = (6.3, 7.1)  # the corpus's eps_33 and eps_11
TOURMALINE_SOUND_M_S = 7000.0
TOURMALINE_SPACING_M = 1e-3
CORPUS_FIELD_V_M = 1e13  # "E_0 > E_crit ... ~ 10^13 V/m"
CORPUS_PEAK_POWER_W = 1e15  # "Peak power: P ~ ... ~ 10^15 W for A ~ 1 cm^2"
CORPUS_AREA_M2 = 1e-4
CORPUS_LASER_W_CM2 = 1e18
CORPUS_VACUUM_FIELD_V_M = 1e16  # "E_crit ~ 10^16 V/m"
CORPUS_VACUUM_DENSITY_BOUND = 1e-12  # "Delta E/V > 10^-12 J/m^3"
CORPUS_VEV_GEV = 1e20  # "v ~ Planck mass/alpha_EM ~ 10^20 GeV"
CORPUS_SCALAR_MASS_EV = 1e-3
CORPUS_QUARTIC = (0.1, 1.0)  # "lambda ... ~ 0.1 - 1.0"
CORPUS_ZPE_DENSITY = 1e9  # "rho_ZPE ~ 10^9 J/m^3 (check) CONSISTENT"
CORPUS_FIELD_ENERGY_J_M3 = 1e9  # "E_field ~ 10^13 V/m -> energy density ~ 10^9 J/m^3"
HIGGS_GEV = 125.0
IMMIRZI = 0.2375
CORPUS_LATTICE_M = 2.7e-35  # "a_lattice = l_Planck sqrt(8 pi gamma) ~ 2.7 x 10^-35 m"
# Planck 2018 VI abstract: H0 = 67.4 km/s/Mpc and Omega_m = 0.315 in the flat fit (Omega_K = 0.001 +- 0.002).
H0_KM_S_MPC = 67.4
OMEGA_M = 0.315


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def close(value: float, stated: float, rel: float) -> bool:
    return abs(value - stated) <= rel * abs(stated)


# ---------------------------------------------------------------- algebra


def sl2_brackets() -> dict[str, object]:
    """[H, E] = 2E, [H, F] = -2F, [E, F] = H for the 2 x 2 traceless basis, in integer matrices."""
    h = np.array([[1, 0], [0, -1]])
    e = np.array([[0, 1], [0, 0]])
    f = np.array([[0, 0], [1, 0]])

    def br(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return x @ y - y @ x

    require(np.array_equal(br(h, e), 2 * e), "[H, E] != 2E")
    require(np.array_equal(br(h, f), -2 * f), "[H, F] != -2F")
    require(np.array_equal(br(e, f), h), "[E, F] != H")
    # The same brackets hold in every spin-j representation, here j = 1 (3 x 3), so they describe all spins.
    h3 = np.diag([2, 0, -2])
    e3 = np.array([[0, 2, 0], [0, 0, 1], [0, 0, 0]])
    f3 = np.array([[0, 0, 0], [1, 0, 0], [0, 2, 0]])
    spin_one = np.array_equal(br(h3, e3), 2 * e3) and np.array_equal(br(h3, f3), -2 * f3)
    spin_one = spin_one and np.array_equal(br(e3, f3), h3)
    require(spin_one, "the spin-1 representation breaks the sl(2) brackets")
    return {"structure_constants": {"c_HE^E": 2, "c_HF^F": -2, "c_EF^H": 1}, "spin_one_representation": True}


def e8_roots() -> np.ndarray:
    """The 240 E8 roots in doubled integer coordinates (2x): 112 of type +-2e_i +-2e_j, 128 of (+-1)^8 even minus."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            roots.append(v)
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(list(signs))
    return np.array(roots, dtype=np.int64)


def e8_structure() -> dict[str, object]:
    """Root count, inner products, the 4_21 vertex figure and dimension, and the D4 x D4 and SU(5)^2 branchings."""
    roots = e8_roots()
    gram = roots @ roots.T  # four times the inner product
    require(len(roots) == 240 and set(np.diag(gram)) == {8}, "E8 roots are not 240 vectors of norm 2")
    products = sorted({int(v) // 4 for v in gram.ravel()})
    require(products == [-2, -1, 0, 1, 2], f"root inner products {products}")
    opposite = {int(gram[i, j]) // 4 for i in range(240) for j in range(240) if np.array_equal(roots[i], -roots[j])}
    require(opposite == {-2}, "<alpha, -alpha> is not -2")
    neighbours = {int(v) for v in (gram == 4).sum(axis=1)}
    require(neighbours == {56}, f"vertex degrees {neighbours}")
    edges = int((gram == 4).sum()) // 2
    affine_rank = int(flint.fmpz_mat((roots[1:] - roots[0]).tolist()).rank())  # dimension of the affine hull
    require(edges == 6720 and affine_rank == 8, "4_21 is not an 8-dimensional polytope with 6720 edges")
    # D4 x D4 on coordinates 0-3 and 4-7: roots inside one block, mixed vector-vector, and the two spinor pairs.
    inside_first = inside_second = mixed = spinor_even = spinor_odd = 0
    for v in roots:
        first, second = v[:4], v[4:]
        if np.all(np.abs(v) <= 1):
            if int((first < 0).sum()) % 2 == 0:
                spinor_even += 1
            else:
                spinor_odd += 1
        elif not second.any():
            inside_first += 1
        elif not first.any():
            inside_second += 1
        else:
            mixed += 1
    split = [inside_first, inside_second, mixed, spinor_even, spinor_odd]
    require(split == [24, 24, 64, 64, 64], f"D4 x D4 root split {split}")
    # 248 = (28,1) + (1,28) + (8v,8v) + (8s,8s) + (8c,8c): 24 + 4 Cartan per D4, three triality-related 64s.
    require(28 + 28 + 3 * 64 == 248, "Spin(8)^2 branching does not sum to 248")
    require(24 + 24 + 2 * 10 * 5 + 2 * 5 * 10 == 248, "SU(5)^2 branching does not sum to 248")
    require(78 + 1 + 27 + 27 == 133, "E7 > E6 x U(1) branching does not sum to 133")
    require(120 + 128 == 248, "Spin(16) branching does not sum to 248")
    return {
        "roots": 240,
        "inner_products": products,
        "inner_product_with_negative": -2,
        "neighbours_per_vertex": 56,
        "edges_4_21": edges,
        "affine_dimension_4_21": affine_rank,
        "d4xd4_root_split": split,
        "branchings": {
            "spin8xspin8": "28+28+64+64+64",
            "su5xsu5": "24+24+50+50+50+50",
            "e7_e6xu1": "78+1+27+27",
            "spin16": "120+128",
        },
    }


def cd_table(dim: int) -> np.ndarray:
    """Integer structure constants T[p, q, r]: e_p e_q = T[p, q, r] e_r under cd_core."""
    table = np.zeros((dim, dim, dim), dtype=np.int64)
    for p in range(dim):
        for q in range(dim):
            table[p, q, p ^ q] = cd_sign(dim, p, q)
    return table


ALBERT_SLOTS = ((0, 1), (1, 2), (2, 0))
# Freudenthal magic square, first two rows: Der(H3(A)) = so(3), su(3), sp(3), f4 and the norm-preserving
# (reduced structure) algebras sl(3,R), sl(3,C), sl(3,H), e6, for A = R, C, H, O.
MAGIC_SQUARE = {1: (3, 8), 2: (8, 16), 4: (21, 35), 8: (52, 78)}


def jordan_double_product(dim: int) -> np.ndarray:
    """2 X o Y = XY + YX on H3(A), A the cd_core algebra of dimension dim (1, 2, 4, 8).

    Coordinates: the three real diagonal entries, then the A-valued entries at (0,1), (1,2), (2,0).
    """
    algebra = cd_table(dim)
    conj = np.array([1] + [-1] * (dim - 1), dtype=np.int64)
    size = 3 + 3 * dim

    def matrix(index: int) -> np.ndarray:
        m = np.zeros((3, 3, dim), dtype=np.int64)
        if index < 3:
            m[index, index, 0] = 1
            return m
        slot, unit = divmod(index - 3, dim)
        i, j = ALBERT_SLOTS[slot]
        m[i, j, unit] = 1
        m[j, i, unit] = conj[unit]
        return m

    def coordinates(m: np.ndarray) -> np.ndarray:
        for i in range(3):
            require(not m[i, i, 1:].any(), "Jordan product has a non-real diagonal")
            for j in range(3):
                require(np.array_equal(m[j, i], m[i, j] * conj), "Jordan product is not Hermitian")
        v = [m[i, i, 0] for i in range(3)]
        for i, j in ALBERT_SLOTS:
            v.extend(m[i, j])
        return np.array(v, dtype=np.int64)

    mats = [matrix(a) for a in range(size)]
    table = np.zeros((size, size, size), dtype=np.int64)
    for a in range(size):
        for b in range(size):
            xy = np.einsum("ijp,jkq,pqr->ikr", mats[a], mats[b], algebra)
            yx = np.einsum("ijp,jkq,pqr->ikr", mats[b], mats[a], algebra)
            table[a, b] = coordinates(xy + yx)
    return table


def integer_rank(matrix: np.ndarray) -> int:
    rows = np.unique(matrix[np.any(matrix != 0, axis=1)], axis=0)
    return int(flint.fmpz_mat(rows.tolist()).rank())


def jordan_symmetry_dimensions(dim: int) -> dict[str, int]:
    """dim Der(H3(A)) and dim of the Lie algebra preserving the cubic norm, as exact integer ranks.

    Derivations solve D(X o Y) = DX o Y + X o DY. The generic norm of a degree-3 Jordan algebra is
    N(X) = T(X^3)/3 - T(X) T(X^2)/2 + T(X)^3/6 (Newton's identity on the generic minimal polynomial); a linear map
    preserves N to first order when the symmetrized trilinear form satisfies N(Xa,b,c) + N(a,Xb,c) + N(a,b,Xc) = 0.
    """
    p2 = jordan_double_product(dim)
    n = len(p2)
    eye = np.eye(n, dtype=np.int64)
    der = np.einsum("gr,abs->abgrs", eye, p2) - np.einsum("rbg,sa->abgrs", p2, eye)
    der -= np.einsum("arg,sb->abgrs", p2, eye)
    upper = np.triu_indices(n)
    der_dim = n * n - integer_rank(der[upper[0], upper[1]].reshape(-1, n * n))
    trace = np.zeros(n, dtype=np.int64)
    trace[:3] = 1
    tau2 = np.einsum("jkm,m->jk", p2, trace)  # 2 T(e_j o e_k)
    theta4 = np.einsum("ijm,mkn,n->ijk", p2, p2, trace)  # 4 T((e_i o e_j) o e_k)
    coef12 = theta4 - 3 * np.einsum("i,jk->ijk", trace, tau2) + 2 * np.einsum("i,j,k->ijk", trace, trace, trace)
    norm72 = sum(coef12.transpose(perm) for perm in itertools.permutations(range(3)))  # 72 N_ijk
    diag = np.zeros(n, dtype=np.int64)
    diag[:3] = (2, 3, 5)
    require(int(np.einsum("ijk,i,j,k->", norm72, diag, diag, diag)) == 72 * 30, "N(diag(2,3,5)) != 30")
    require(int(np.einsum("ijk,i,j,k->", norm72, trace, trace, trace)) == 72, "N(identity) != 1")
    preserve = np.einsum("rjk,si->ijkrs", norm72, eye) + np.einsum("irk,sj->ijkrs", norm72, eye)
    preserve += np.einsum("ijr,sk->ijkrs", norm72, eye)
    triples = np.array(list(itertools.combinations_with_replacement(range(n), 3)))
    rows = preserve[triples[:, 0], triples[:, 1], triples[:, 2]].reshape(len(triples), n * n)
    norm_dim = n * n - integer_rank(rows)
    require((der_dim, norm_dim) == MAGIC_SQUARE[dim], f"H3 over dimension {dim}: {(der_dim, norm_dim)}")
    return {"jordan_dimension": n, "derivation_dimension": der_dim, "norm_preserving_dimension": norm_dim}


def albert_symmetry_dimensions(dims: tuple[int, ...] = (1, 2, 4, 8)) -> dict[str, object]:
    """The magic-square rows for A = R, C, H, O; at O the dimensions are 52 (f4) and 78 (e6).

    E6 is therefore not Aut(H3(O)), whose Lie algebra is the 52-dimensional derivation algebra, and 52 + 1 != 78.
    """
    rows = dict(zip((str(d) for d in dims), parallel.ordered_map(jordan_symmetry_dimensions, list(dims)), strict=True))
    out: dict[str, object] = {"by_algebra_dimension": rows}
    if "8" in rows:
        octonion = rows["8"]
        out["e6_equals_aut"] = octonion["norm_preserving_dimension"] == octonion["derivation_dimension"]
        out["e6_equals_aut_plus_u1"] = octonion["norm_preserving_dimension"] == octonion["derivation_dimension"] + 1
    return out


def batched_product(table: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.einsum("np,nq,pqr->nr", a, b, table)


def moufang_split() -> dict[str, object]:
    """a(xy)a = (ax)(ya), the Moufang form of the triality triple (L_a R_a, L_a, R_a), on O and on S.

    Tested for every a = e_i + e_j (0 < i < j) and every basis x, y. The identity holds in every alternative algebra,
    so the octonion count must be zero; the sedenions are not alternative.
    """
    out: dict[str, object] = {}
    for dim, name in ((8, "octonions"), (16, "sedenions")):
        table = cd_table(dim)
        eye = np.eye(dim, dtype=np.int64)
        pairs = list(itertools.combinations(range(1, dim), 2))
        cases = [(i, j, x, y) for i, j in pairs for x in range(dim) for y in range(dim)]
        a = np.array([eye[i] + eye[j] for i, j, _, _ in cases])
        x = np.array([eye[c[2]] for c in cases])
        y = np.array([eye[c[3]] for c in cases])
        lhs = batched_product(table, batched_product(table, a, batched_product(table, x, y)), a)
        rhs = batched_product(table, batched_product(table, a, x), batched_product(table, y, a))
        bad = np.flatnonzero(np.any(lhs != rhs, axis=1))
        entry: dict[str, object] = {"cases": len(cases), "failures": int(len(bad))}
        if len(bad):
            i, j, xi, yi = cases[int(bad[0])]
            entry["first_witness"] = {
                "a": f"e{i} + e{j}",
                "x": f"e{xi}",
                "y": f"e{yi}",
                "a(xy)a": lhs[bad[0]].tolist(),
                "(ax)(ya)": rhs[bad[0]].tolist(),
            }
        out[name] = entry
    require(out["octonions"]["failures"] == 0, "the octonions fail the Moufang identity")  # type: ignore[index]
    require(out["sedenions"]["failures"] > 0, "the sedenions satisfy the Moufang identity")  # type: ignore[index]
    return out


# ------------------------------------------------------- Virasoro and Kac

H_SYM, C_SYM, M_SYM = sp.symbols("h c m")


def partitions(total: int, largest: int | None = None) -> list[tuple[int, ...]]:
    largest = total if largest is None else largest
    if total == 0:
        return [()]
    return [(first,) + rest for first in range(min(total, largest), 0, -1) for rest in partitions(total - first, first)]


def _accumulate(acc: dict[tuple[int, ...], sp.Expr], state: dict[tuple[int, ...], sp.Expr], factor: sp.Expr) -> None:
    for key, value in state.items():
        acc[key] = acc.get(key, sp.Integer(0)) + factor * value


@cache
def _virasoro_apply(n: int, mono: tuple[int, ...]) -> dict[tuple[int, ...], sp.Expr]:
    """L_n on L_{-mono[0]} ... L_{-mono[-1]} |h>, mono nonincreasing, as a PBW combination."""
    if n == 0:
        return {mono: H_SYM + sum(mono)}
    if not mono:
        return {} if n > 0 else {(-n,): sp.Integer(1)}
    first, rest = mono[0], mono[1:]
    out: dict[tuple[int, ...], sp.Expr] = {}
    if n < 0:
        if -n >= first:
            return {(-n,) + mono: sp.Integer(1)}
        _accumulate(out, {(first,) + key: value for key, value in _virasoro_apply(n, rest).items()}, sp.Integer(1))
        _accumulate(out, _virasoro_apply(n - first, rest), sp.Integer(first + n))
        return out
    for key, value in _virasoro_apply(n, rest).items():
        _accumulate(out, _virasoro_apply(-first, key), value)
    _accumulate(out, _virasoro_apply(n - first, rest), sp.Integer(n + first))
    if n == first:
        _accumulate(out, {rest: sp.Integer(1)}, C_SYM * sp.Rational(n**3 - n, 12))
    return out


def virasoro_gram(level: int) -> sp.Matrix:
    """Shapovalov matrix <h| L_{lam_k} ... L_{lam_1} L_{-mu_1} ... |h> on the PBW basis of the level."""
    basis = partitions(level)
    gram = sp.zeros(len(basis))
    for i, lam in enumerate(basis):
        for j, mu in enumerate(basis):
            state: dict[tuple[int, ...], sp.Expr] = {mu: sp.Integer(1)}
            for part in lam:
                new: dict[tuple[int, ...], sp.Expr] = {}
                for key, value in state.items():
                    _accumulate(new, _virasoro_apply(part, key), value)
                state = new
            gram[i, j] = sp.expand(state.get((), sp.Integer(0)))
    return gram


def kac_weight(r: int, s: int) -> sp.Expr:
    """h_{r,s} = ([(m+1) r - m s]^2 - 1) / (4 m (m+1)) at c = 1 - 6/(m(m+1))."""
    return (((M_SYM + 1) * r - M_SYM * s) ** 2 - 1) / (4 * M_SYM * (M_SYM + 1))


def kac_level(level: int) -> dict[str, object]:
    """det M_N = K_N prod_{rs <= N} (h - h_{r,s})^{p(N - rs)}, K_N = prod ((2r)^s s!)^{m(r,s)}, as an identity in h, m.

    m(r, s) counts the partitions of N in which r appears exactly s times. The h-degree of the determinant equals
    sum p(N - rs), which makes each zero's order exactly p(N - rs) once every factor divides the determinant.
    """
    gram = virasoro_gram(level)
    domain = DomainMatrix.from_Matrix(gram).convert_to(sp.QQ[H_SYM, C_SYM])
    det = domain.domain.to_sympy(domain.det())
    constant = sp.Integer(1)
    product = sp.Integer(1)
    degree = 0
    for r in range(1, level + 1):
        for s in range(1, level // r + 1):
            count = sum(1 for lam in partitions(level) if lam.count(r) == s)
            constant *= (sp.Integer(2 * r) ** s * sp.factorial(s)) ** count
            exponent = len(partitions(level - r * s))
            product *= (H_SYM - kac_weight(r, s)) ** exponent
            degree += exponent
    difference = det.subs(C_SYM, 1 - sp.Integer(6) / (M_SYM * (M_SYM + 1))) - constant * product
    numerator, _ = sp.fraction(sp.together(difference))
    require(sp.expand(numerator) == 0, f"Kac determinant fails at level {level}")
    require(sp.Poly(det, H_SYM).degree() == degree, f"h-degree differs from sum p(N - rs) at level {level}")
    return {"level": level, "dimension": len(partitions(level)), "constant": int(constant), "h_degree": degree}


def kac_determinant(max_level: int) -> dict[str, object]:
    levels = parallel.ordered_map(kac_level, list(range(1, max_level + 1)), min_items=2)
    by_level = {str(item["level"]): item for item in levels}
    require(by_level["2"]["constant"] == 32, "K_2 != 32")
    gram2 = virasoro_gram(2)  # basis (L_-2, L_-1^2); the corpus orders it (L_-1^2, L_-2)
    expected = sp.Matrix([[4 * H_SYM + C_SYM / 2, 6 * H_SYM], [6 * H_SYM, 8 * H_SYM**2 + 4 * H_SYM]])
    require(sp.simplify(gram2 - expected) == sp.zeros(2), "level-2 Gram matrix differs from the corpus")
    det2 = sp.expand(gram2.det())
    require(sp.expand(det2 - 2 * H_SYM * (16 * H_SYM**2 + (2 * C_SYM - 10) * H_SYM + C_SYM)) == 0, "level-2 det")
    ising = sorted(sp.solve(det2.subs(C_SYM, sp.Rational(1, 2)) / H_SYM, H_SYM))
    require(ising == [sp.Rational(1, 16), sp.Rational(1, 2)], f"c = 1/2 roots {ising}")
    rejected_guess = math.prod((2 * n) ** len(partitions(2 - n)) for n in (1, 2))
    return {
        "levels": by_level,
        "level2_ising_roots": [str(v) for v in ising],
        "corpus_rejected_constant_guess_at_level2": rejected_guess,
    }


def coulomb_gas() -> dict[str, object]:
    """c = 1 - 12 Q^2, h_alpha = alpha(alpha - 2Q)/2, screening a, b and alpha_{r,s} give the Kac weights."""
    m = sp.symbols("m", positive=True)
    q = 1 / sp.sqrt(2 * m * (m + 1))
    require(sp.simplify(1 - 12 * q**2 - (1 - sp.Integer(6) / (m * (m + 1)))) == 0, "c(Q) != c(m)")
    # sqrt(Q^2 + 2) = (2m + 1)/sqrt(2m(m + 1)) for m > 0: the square matches and both sides are positive.
    root = (2 * m + 1) / sp.sqrt(2 * m * (m + 1))
    require(sp.simplify(root**2 - (q**2 + 2)) == 0, "sqrt(Q^2 + 2) closed form")
    a = q + root
    b = q - root
    require(sp.simplify(a * b + 2) == 0 and sp.simplify(a + b - 2 * q) == 0, "screening roots")
    for alpha in (a, b):
        require(sp.simplify(alpha * (alpha - 2 * q) / 2 - 1) == 0, "screening charge weight != 1")
    require(sp.simplify(a**2 - 2 * (m + 1) / m) == 0 and sp.simplify(b**2 - 2 * m / (m + 1)) == 0, "a^2, b^2")
    checked = 0
    for r in range(1, 5):
        for s in range(1, 5):
            alpha = (1 - r) * a / 2 + (1 - s) * b / 2
            weight = alpha * (alpha - 2 * q) / 2
            target = kac_weight(r, s).subs(M_SYM, m)
            require(sp.simplify(sp.expand(weight - target)) == 0, f"h_({r},{s}) differs from the Kac formula")
            checked += 1
    ising = {f"{r},{s}": str(kac_weight(r, s).subs(M_SYM, 3)) for r, s in ((2, 1), (1, 2), (1, 1))}
    require(ising == {"2,1": "1/2", "1,2": "1/16", "1,1": "0"}, f"m = 3 weights {ising}")
    return {"weights_checked": checked, "ising_m3": ising}


K_SYM = sp.symbols("k")
SL2_DUAL = {"e": ("f", sp.Integer(1)), "f": ("e", sp.Integer(1)), "h": ("h", sp.Rational(1, 2))}
SL2_ADJOINT = {"e": "f", "f": "e", "h": "h"}
SL2_FORM = {("e", "f"): 1, ("f", "e"): 1, ("h", "h"): 2}
SL2_BRACKET = {
    ("h", "e"): (2, "e"),
    ("h", "f"): (-2, "f"),
    ("e", "h"): (-2, "e"),
    ("f", "h"): (2, "f"),
    ("e", "f"): (1, "h"),
    ("f", "e"): (-1, "h"),
}
Mode = tuple[str, int]


@cache
def affine_vev(word: tuple[Mode, ...]) -> sp.Expr:
    """<0| x1_m1 ... xn_mn |0> for affine sl(2) at level k (Chevalley basis, (h|h) = 2, (e|f) = 1)."""
    if not word:
        return sp.Integer(1)
    if word[-1][1] >= 0 or word[0][1] <= 0:
        return sp.Integer(0)
    i = max(j for j, (_, mode) in enumerate(word) if mode > 0)
    x, mx = word[i]
    total = sp.Integer(0)
    for j in range(i + 1, len(word)):
        y, my = word[j]
        base, tail = word[:i] + word[i + 1 : j], word[j + 1 :]
        if (x, y) in SL2_BRACKET:
            coef, z = SL2_BRACKET[(x, y)]
            total += coef * affine_vev(base + ((z, mx + my),) + tail)
        if mx + my == 0 and (x, y) in SL2_FORM:
            total += K_SYM * mx * SL2_FORM[(x, y)] * affine_vev(base + tail)
    return sp.expand(total)


def sugawara_terms(n: int, low: int = -6, high: int = 8) -> list[tuple[sp.Expr, tuple[Mode, Mode], int]]:
    """S_n = (1/2) sum_a sum_p :J^a_p J_a,n-p:, larger mode on the right; each term carries its p."""
    terms = []
    for a, (b, weight) in SL2_DUAL.items():
        for p in range(low, high + 1):
            q = n - p
            pair = ((a, p), (b, q)) if p <= q else ((b, q), (a, p))
            terms.append((sp.Rational(1, 2) * weight, pair, p))
    return terms


def sugawara_sl2() -> dict[str, object]:
    """S_0 J_{-1}|0> = (k + h^v) J_{-1}|0> and <0|L_2 L_{-2}|0> = c/2 with c = 3k/(k + 2) for affine sl(2)."""

    def adjoint(word: tuple[Mode, ...]) -> tuple[Mode, ...]:
        return tuple((SL2_ADJOINT[x], -mode) for x, mode in reversed(word))

    for x in "efh":
        for y in "efh":
            bra = adjoint(((x, -1),))
            lhs = sum(coef * affine_vev(bra + pair + ((y, -1),)) for coef, pair, _ in sugawara_terms(0))
            rhs = (K_SYM + 2) * affine_vev(bra + ((y, -1),))
            require(sp.simplify(lhs - rhs) == 0, f"S_0 on {y}_-1|0> paired with {x}_-1|0>")
    contributions: dict[int, sp.Expr] = {}
    for coef, pair, p in sugawara_terms(2):
        value = sum(c2 * affine_vev(pair + w2) for c2, w2, _ in sugawara_terms(-2))
        contributions[p] = sp.expand(contributions.get(p, sp.Integer(0)) + coef * value)
    total = sum(contributions.values()) / (K_SYM + 2) ** 2
    central = 3 * K_SYM / (K_SYM + 2)
    require(sp.simplify(total - central / 2) == 0, "<0|L_2 L_-2|0> != c/2")
    nonzero = sorted(p for p, value in contributions.items() if sp.simplify(value) != 0)
    require(nonzero == [1], f"L_2 terms with nonzero contribution: {nonzero}")
    # Real totally antisymmetric structure constants with a positive form contract negatively: sum eps eps = -2 delta.
    eps = np.zeros((3, 3, 3), dtype=np.int64)
    for (i, j, k), sign in (((0, 1, 2), 1), ((1, 2, 0), 1), ((2, 0, 1), 1)):
        eps[i, j, k], eps[j, i, k] = sign, -sign
    contraction = np.einsum("abc,ace->be", eps, eps)
    require(np.array_equal(contraction, -2 * np.eye(3, dtype=np.int64)), "sum eps^abc eps^ace != -2 delta")
    return {
        "dual_coxeter": 2,
        "weight_one_eigenvalue": "k + 2",
        "central_charge": "3k/(k + 2)",
        "nonzero_L2_terms_p": nonzero,
        "real_antisymmetric_contraction": -2,
    }


def l_infinity_and_affine() -> dict[str, object]:
    """Counterexamples to the corpus's n = 3 L-infinity identity and to its Kac-Moody bracket.

    A degree-0 bracket with l1 = l3 = 0 satisfies the corpus's displayed identity (every term vanishes) while its
    Jacobiator is nonzero, so that identity cannot be the n = 3 relation, which reduces to Jacobi there. The central
    term m delta_{m+n,0} K without the invariant form is not bilinear; m delta (x|y) K with (x|y) = tr(xy) is a
    2-cocycle on the sl(2) loop algebra.
    """
    bracket = np.zeros((3, 3, 3), dtype=np.int64)  # [e1,e2] = e1, [e2,e3] = e2, [e3,e1] = e3
    for i, j, k in ((0, 1, 0), (1, 2, 1), (2, 0, 2)):
        bracket[i, j, k], bracket[j, i, k] = 1, -1
    eye = np.eye(3, dtype=np.int64)

    def br(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        return np.einsum("i,j,ijk->k", u, v, bracket)

    jacobiator = br(eye[0], br(eye[1], eye[2])) + br(eye[1], br(eye[2], eye[0])) + br(eye[2], br(eye[0], eye[1]))
    require(jacobiator.any(), "the counterexample bracket satisfies Jacobi")
    sl2 = [np.array([[1, 0], [0, -1]]), np.array([[0, 1], [0, 0]]), np.array([[0, 0], [1, 0]])]

    def form(x: np.ndarray, y: np.ndarray) -> int:
        return int(np.trace(x @ y))

    def omega(x: np.ndarray, m: int, y: np.ndarray, n: int) -> int:
        return m * form(x, y) if m + n == 0 else 0

    # The cocycle identity omega([x,y] t^(m+n), z t^p) + cyclic = 0 for p = -m-n, with omega(u t^p, v t^q) =
    # p delta_{p+q,0} tr(uv), evaluated for every basis triple and mode pair at once; T2 and T3 are the cyclic
    # relabellings tr([x_b, x_c] x_a) and tr([x_c, x_a] x_b) indexed by (a, b, c).
    basis = np.array(sl2)
    commutator = np.einsum("aij,bjk->abik", basis, basis) - np.einsum("bij,ajk->abik", basis, basis)
    triple = np.einsum("abij,cji->abc", commutator, basis)  # tr([x_a, x_b] x_c)
    modes = np.arange(-3, 4)
    ma, mb = np.meshgrid(modes, modes, indexing="ij")
    mc = -ma - mb
    total = (
        (ma + mb)[None, None, None] * triple[..., None, None]
        + (mb + mc)[None, None, None] * triple.transpose(2, 0, 1)[..., None, None]
        + (mc + ma)[None, None, None] * triple.transpose(1, 2, 0)[..., None, None]
    )
    failures = int(np.count_nonzero(total))
    require(failures == 0, "m delta (x|y) is not a 2-cocycle on the loop algebra")
    x, y = sl2[1], sl2[2]
    corpus_central = 1  # m delta_{m+n,0} at m = 1, the same for (x, y) and (2x, y)
    bilinear = [omega(x, 1, y, -1), omega(2 * x, 1, y, -1)]
    require(bilinear[1] == 2 * bilinear[0] != 0, "the corrected central term is not bilinear")
    return {
        "counterexample_jacobiator": jacobiator.tolist(),
        "corpus_identity_holds_on_counterexample": True,
        "corrected_cocycle_failures": failures,
        "corpus_central_term_at_x_and_2x": [corpus_central, corpus_central],
        "bilinear_central_term_at_x_and_2x": bilinear,
    }


def scalar_equation_of_motion() -> dict[str, object]:
    """The Euler-Lagrange equation of the corpus scalar sector against its printed equation, in both box conventions.

    The physical Lagrangian (1/2)(phi_t^2 - phi_x^2) - (1/2) m^2 phi^2 - lam phi^4/4! + xi R phi^2 + kappa T phi
    (R, T constant) has one equation of motion. Written with box = d_t^2 - d_x^2 or with box = -d_t^2 + d_x^2, the
    printed box phi - m^2 phi - lam phi^3/6 - xi R phi - kappa T = 0 differs from it by an overall factor in
    neither convention; the residual names the terms that disagree.
    """
    t, x = sp.symbols("t x")
    mass, lam, xi, ricci, kappa, trace = sp.symbols("m lambda xi R kappa T")
    phi = sp.Function("phi")(t, x)
    lagrangian = (sp.diff(phi, t) ** 2 - sp.diff(phi, x) ** 2) / 2 - mass**2 * phi**2 / 2
    lagrangian += -lam * phi**4 / 24 + xi * ricci * phi**2 + kappa * trace * phi
    euler = sp.expand(-sp.euler_equations(lagrangian, [phi], [t, x])[0].lhs)  # phi_tt - phi_xx + ... = 0
    wave = sp.diff(phi, t, 2) - sp.diff(phi, x, 2)
    results: dict[str, object] = {"euler_lagrange": str(euler)}
    for sign, name in ((1, "box_mostly_minus"), (-1, "box_mostly_plus")):
        printed = sign * wave - mass**2 * phi - lam * phi**3 / 6 - xi * ricci * phi - kappa * trace
        residual = sp.expand(printed - sign * euler)  # zero when the printed equation is sign x the true one
        require(residual != 0, f"the printed EOM follows from the Lagrangian with {name}")
        results[name] = {"printed_minus_true": str(residual)}
    return results


# --------------------------------------------------------------- physics


def planck() -> dict[str, float]:
    return {
        "length_m": math.sqrt(HBAR * G / C**3),
        "frequency_Hz": math.sqrt(C**5 / (HBAR * G)),
        "mass_GeV": math.sqrt(HBAR * C / G) * C**2 / GEV,
        "energy_density_J_m3": C**7 / (HBAR * G**2),
    }


def frequency_numerology() -> dict[str, float]:
    """f_n = f_P alpha^-1 phi^n: the n that reaches 148 Hz, and the grid spacing that makes every target reachable."""
    base = planck()["frequency_Hz"] / ALPHA
    n_real = math.log(CORPUS_FREQUENCY_HZ / base) / math.log(GOLDEN)
    nearest = round(n_real)
    worst_miss = math.sqrt(GOLDEN)  # any frequency lies within phi^(1/2) of some f_n
    require(abs(n_real - nearest) <= 0.5 and worst_miss < 1.28, "phi grid spacing")
    return {
        "f_n0_Hz": base,
        "n_for_148Hz": n_real,
        "nearest_integer_n": nearest,
        "f_nearest_Hz": base * GOLDEN**nearest,
        "max_ratio_to_nearest_grid_point": worst_miss,
    }


def _polylog4(x: float, terms: int = 4000) -> float:
    n = np.arange(1, terms + 1, dtype=float)
    return float(np.sum(x**n / n**4))


def lifshitz_ratio(epsilon: float) -> float:
    """E/E_ideal for two identical nondispersive dielectric half-spaces at T = 0.

    With s = zeta/kappa, E = -(hbar c / (16 pi^2 d^3)) sum_p int_0^1 Li_4(r_p(s)^2) ds, and perfect mirrors give
    2 zeta(4), so the ratio is (45/pi^4) sum_p int_0^1 Li_4(r_p^2) ds; |r_p| <= 1 bounds it by one.
    """

    def integrand(s: float, polarization: str) -> float:
        root = math.sqrt(1 + (epsilon - 1) * s * s)
        r = (1 - root) / (1 + root) if polarization == "TE" else (epsilon - root) / (epsilon + root)
        return _polylog4(r * r)

    total = sum(integrate.quad(integrand, 0, 1, args=(pol,), limit=200)[0] for pol in ("TE", "TM"))
    return 45 / math.pi**4 * total


def casimir() -> dict[str, object]:
    ratios = {str(eps): lifshitz_ratio(eps) for eps in (*TOURMALINE_EPSILON, 1e4)}
    require(all(0 < v < 1 for v in ratios.values()), "a passive dielectric exceeds the ideal Casimir energy")
    largest = max(ratios[str(eps)] for eps in TOURMALINE_EPSILON)
    return {
        "lifshitz_ratio_by_epsilon": ratios,
        "corpus_enhancement": CORPUS_CASIMIR_ENHANCEMENT,
        "shortfall_factor": CORPUS_CASIMIR_ENHANCEMENT / largest,
    }


def fields_and_powers() -> dict[str, float]:
    """The corpus's tourmaline, field, power and laser figures recomputed."""
    intensity = C * EPS0 * CORPUS_FIELD_V_M**2 / 2
    laser = math.sqrt(2 * CORPUS_LASER_W_CM2 * 1e4 / (C * EPS0))
    frequency = TOURMALINE_SOUND_M_S / (2 * TOURMALINE_SPACING_M)
    e_crit_own = math.sqrt(2 * CORPUS_ZPE_DENSITY / EPS0)
    e_crit_planck = math.sqrt(2 * planck()["energy_density_J_m3"] / EPS0)
    power = intensity * CORPUS_AREA_M2
    require(close(frequency, 3.5e6, 1e-9), "tourmaline frequency")
    require(power / CORPUS_PEAK_POWER_W > 1e3, "the stated peak power is within three decades of I A")
    require(1e12 < laser < 1e13, "laser field outside the stated order")
    return {
        "tourmaline_frequency_Hz": frequency,
        "e_crit_from_corpus_density_V_m": e_crit_own,
        "e_crit_from_planck_density_V_m": e_crit_planck,
        "b0_T": CORPUS_FIELD_V_M / C,
        "peak_power_W": power,
        "peak_power_over_corpus": power / CORPUS_PEAK_POWER_W,
        "laser_field_V_m": laser,
    }


def euler_heisenberg() -> dict[str, float]:
    """Delta u = 3 xi E^4, xi = 2 alpha^2 eps0^2 hbar^3 / (45 m_e^4 c^5), at the corpus's 1e16 V/m."""
    xi = 2 * ALPHA**2 * EPS0**2 * HBAR**3 / (45 * M_E**4 * C**5)
    delta = 3 * xi * CORPUS_VACUUM_FIELD_V_M**4
    schwinger = M_E**2 * C**3 / (E_CHARGE * HBAR)
    require(delta > CORPUS_VACUUM_DENSITY_BOUND, "standard QED misses the corpus's bound")
    return {
        "schwinger_field_V_m": schwinger,
        "corpus_field_over_schwinger": CORPUS_VACUUM_FIELD_V_M / schwinger,
        "euler_heisenberg_delta_u_J_m3": delta,
        "fraction_of_field_energy": delta / (EPS0 * CORPUS_VACUUM_FIELD_V_M**2 / 2),
    }


def gravity_of_field() -> dict[str, float]:
    """Metric perturbation 2 G u L^2 / c^4 of the corpus's 1e13 V/m field energy over one metre."""
    density = EPS0 * CORPUS_FIELD_V_M**2 / 2
    strain = 2 * G * density / C**4
    require(strain < 1e-25, "the field's metric perturbation reaches 1e-25 over a metre")
    return {"field_energy_density_J_m3": density, "metric_perturbation_over_1m": strain}


def scalar_potential() -> dict[str, float]:
    """v = M_P/alpha, the Compton length of 1e-3 eV, and the radial mass sqrt(lambda v^2/3 - 2 m^2) of V(phi)."""
    vev = planck()["mass_GeV"] / ALPHA
    compton = HBAR * C / (CORPUS_SCALAR_MASS_EV * EV)
    radial = [math.sqrt(lam / 3) * CORPUS_VEV_GEV for lam in CORPUS_QUARTIC]
    needed = 3 * (CORPUS_SCALAR_MASS_EV * 1e-9 / CORPUS_VEV_GEV) ** 2
    require(close(compton, 1.97e-4, 0.01), "Compton length of 1e-3 eV")
    require(min(radial) > 1e18, "radial mass is not Planckian")
    return {
        "m_planck_over_alpha_GeV": vev,
        "compton_length_m": compton,
        "compton_over_array_spacing": compton / TOURMALINE_SPACING_M,
        "radial_mass_GeV_lambda_0.1": radial[0],
        "radial_mass_GeV_lambda_1": radial[1],
        "quartic_needed_for_1meV": needed,
    }


def zero_point() -> dict[str, float]:
    """rho(Lambda) = Lambda^4 / (8 pi^2 (hbar c)^3) at a Higgs cutoff, the Planck density, the observed rho_Lambda."""
    omega = sp.symbols("omega", positive=True)
    cutoff = sp.symbols("Lambda", positive=True)
    integral = sp.integrate(omega**3 / (2 * sp.pi**2), (omega, 0, cutoff))
    require(sp.simplify(integral - cutoff**4 / (8 * sp.pi**2)) == 0, "zero-point integral")
    energy = HIGGS_GEV * GEV
    rho = energy**4 / (8 * math.pi**2 * (HBAR * C) ** 3)
    hubble = H0_KM_S_MPC * 1e3 / (sc.parsec * 1e6)
    rho_lambda = (1 - OMEGA_M) * 3 * hubble**2 * C**2 / (8 * math.pi * G)
    require(rho / CORPUS_ZPE_DENSITY > 1e30, "Higgs-cutoff density within 30 decades of 1e9")
    return {
        "integral_prefactor": "1/(8 pi^2)",
        "corpus_prefactor": "1/(16 pi^2)",
        "higgs_cutoff_density_J_m3": rho,
        "higgs_cutoff_over_corpus": rho / CORPUS_ZPE_DENSITY,
        "planck_density_J_m3": planck()["energy_density_J_m3"],
        "observed_dark_energy_J_m3": rho_lambda,
        "higgs_cutoff_over_observed": rho / rho_lambda,
    }


def loop_quantum_gravity() -> dict[str, float]:
    """l_P sqrt(8 pi gamma) and the area of two j = 1/2 punctures in units of 8 pi gamma l_P^2, both forms."""
    lattice = planck()["length_m"] * math.sqrt(8 * math.pi * IMMIRZI)
    spins = (0.5, 0.5)
    sum_of_roots = sum(math.sqrt(j * (j + 1)) for j in spins)
    root_of_sum = math.sqrt(sum(j * (j + 1) for j in spins))
    require(abs(lattice / CORPUS_LATTICE_M - 1) > 0.3, "the corpus lattice length agrees")
    return {
        "lattice_length_m": lattice,
        "lattice_over_corpus": lattice / CORPUS_LATTICE_M,
        "area_two_half_punctures_sum_of_roots": sum_of_roots,
        "area_two_half_punctures_corpus_form": root_of_sum,
    }


def prediction_sizes() -> dict[str, float]:
    """The corpus's three signatures at a = l_P sqrt(8 pi gamma): Casimir modulation, photon and GW dispersion."""
    lattice = loop_quantum_gravity()["lattice_length_m"]
    roughness = 1e-10
    log10_suppression = -2 * math.pi**2 * (roughness / lattice) ** 2 / math.log(10)
    optical_k = 2 * math.pi / 500e-9
    gw_k = 2 * math.pi * 100.0 / C
    return {
        "casimir_periods_per_nm": 1e-9 / lattice,
        "log10_modulation_after_0.1nm_averaging": log10_suppression,
        "photon_shift_at_500nm_max": (optical_k * planck()["length_m"]) ** 2,
        "gw_shift_at_100Hz": (gw_k * lattice) ** 2,
    }


def su5_assignments() -> dict[str, object]:
    """Lambda^2 5 and 5bar of SU(5) in Q = T3 + Y, against the corpus's multiplets (Y doubled there)."""
    five = [("3", "1", Fraction(-1, 3))] * 3 + [("1", "2", Fraction(1, 2))] * 2
    content: dict[tuple[str, str, Fraction], int] = {}
    for (c1, w1, y1), (c2, w2, y2) in itertools.combinations(five, 2):
        colour = "3bar" if c1 == c2 == "3" else ("3" if "3" in (c1, c2) else "1")
        weak = "1" if w1 == w2 == "2" else ("2" if "2" in (w1, w2) else "1")
        key = (colour, weak, y1 + y2)
        content[key] = content.get(key, 0) + 1
    ten = {f"({c},{w})_{y}": n for (c, w, y), n in sorted(content.items(), key=str)}
    require(ten == {"(1,1)_1": 1, "(3,2)_1/6": 6, "(3bar,1)_-2/3": 3}, f"Lambda^2 5 = {ten}")  # e^c, Q, u^c
    require(sum(n * y for (_, _, y), n in content.items()) == 0, "Tr Y != 0 on the 10")
    corpus_ten = 6 + 2  # Q and L
    corpus_five_bar = 3 + 3 + 1  # u^c, d^c, e^c
    return {
        "ten": ten,
        "five_bar": {"(3bar,1)_1/3": 3, "(1,2)_-1/2": 2},
        "corpus_ten_dimension": corpus_ten,
        "corpus_five_bar_dimension": corpus_five_bar,
    }


# ---------------------------------------------------- repository rechecks


def qet_model(h: float = 1.0, k: float = 1.0) -> dict[str, float]:
    """Hotta's minimal QET model rebuilt from its Hamiltonian, independently of scripts/qet_*.py.

    H_A = h Z_A + h^2/r, H_B = h Z_B + h^2/r, V = 2k X_A X_B + 2k^2/r with r = sqrt(h^2 + k^2): ground energy 0.
    Alice measures X_A; Bob rotates by exp(-i sign theta Y_B) with sign her outcome. L(theta) = <H_B + V> after.
    """
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    y = np.array([[0, -1j], [1j, 0]])
    z = np.diag([1.0, -1.0]).astype(complex)
    one = np.eye(2)
    r = math.hypot(h, k)
    h_a = h * np.kron(z, one) + h * h / r * np.eye(4)
    h_b = h * np.kron(one, z) + h * h / r * np.eye(4)
    v = 2 * k * np.kron(x, x) + 2 * k * k / r * np.eye(4)
    total = h_a + h_b + v
    values, vectors = np.linalg.eigh(total)
    require(abs(values[0]) < 1e-12, f"ground energy {values[0]}")
    ground = vectors[:, 0]
    rho = np.outer(ground, ground.conj())
    local = h_b + v

    def bob_energy(theta: float) -> float:
        out = np.zeros((4, 4), dtype=complex)
        for sign in (1, -1):
            proj = np.kron((one + sign * x) / 2, one)
            rotation = np.kron(one, math.cos(theta) * one - 1j * sign * math.sin(theta) * y)
            branch = rotation @ proj
            out += branch @ rho @ branch.conj().T
        return float(np.real(np.trace(out @ local)))

    # L(theta) = A + B cos 2 theta + D sin 2 theta, since the rotation enters through cos^2, sin^2 and sin cos.
    at_zero, at_plus, at_minus = bob_energy(0.0), bob_energy(math.pi / 4), bob_energy(-math.pi / 4)
    mean = (at_plus + at_minus) / 2
    cos_part, sin_part = at_zero - mean, (at_plus - at_minus) / 2
    best = math.atan2(-sin_part, -cos_part) / 2
    e_m = mean - math.hypot(cos_part, sin_part)
    require(
        abs(bob_energy(best) - e_m) < 1e-12
        and abs(bob_energy(0.3) - (mean + cos_part * math.cos(0.6) + sin_part * math.sin(0.6))) < 1e-12,
        "Bob's energy is not a first harmonic in 2 theta",
    )
    e_x = bob_energy(-best)
    injected = float(
        np.real(
            np.trace(
                sum(np.kron((one + s * x) / 2, one) @ rho @ np.kron((one + s * x) / 2, one) for s in (1, -1)) @ h_a
            )
        )
    )
    closed_form = math.sqrt(h * h + 4 * k * k) - (h * h + 2 * k * k) / r
    require(abs(-e_m - closed_form) < 1e-6, "E_B differs from sqrt(h^2+4k^2) - (h^2+2k^2)/r")
    return {
        "extracted_E_B": -e_m,
        "closed_form_E_B": closed_form,
        "reversed_raise_E_x": e_x,
        "half_contrast": (e_x - e_m) / 2,
        "record_flip_zero": -e_m / (e_x - e_m),
        "alice_injected": injected,
    }


def existing_note_rechecks() -> list[dict[str, object]]:
    """Numbers printed in the repository's falsification notes, recomputed from CODATA without their scripts."""
    rows: list[dict[str, object]] = []

    def row(note: str, statement: str, computed: float, stated: float, rel: float) -> None:
        rows.append(
            {
                "note": note,
                "statement": statement,
                "computed": computed,
                "stated": stated,
                "agrees": close(computed, stated, rel),
            }
        )

    pais = "pais-claims-falsification.md"
    omega = 3.0e4 * 2 * math.pi / 60
    sigma, radius = 5.0e4, 2.0
    charge = sigma * 4 * math.pi * radius**2
    row(pais, "Eq. 1 at 50000 C/m^2, 2 m, 30000 RPM (W/m^2)", sigma**2 / EPS0 * radius * omega, 1.77e24, 0.01)
    row(pais, "surface field sigma/eps0 (V/m)", sigma / EPS0, 5.6e15, 0.02)
    row(pais, "electrostatic pressure sigma^2/(2 eps0) (Pa)", sigma**2 / (2 * EPS0), 1.4e20, 0.02)
    row(pais, "largest charge under 1e9 V/m (C/m^2)", EPS0 * 1e9, 8.9e-3, 0.01)
    row(pais, "Eq. 1 at that charge (W/m^2)", (EPS0 * 1e9) ** 2 / EPS0 * radius * omega, 5.6e10, 0.01)
    row(pais, "1 C on a 2 m sphere (V/m)", 1 / (4 * math.pi * EPS0 * radius**2), 2.2e9, 0.03)
    row(pais, "radius keeping 1 C under 1e9 V/m (m)", math.sqrt(1 / (4 * math.pi * EPS0 * 1e9)), 3.0, 0.01)
    field_energy = charge**2 / (8 * math.pi * EPS0 * radius)
    row(pais, "exterior field energy of the worked example (J)", field_energy, 1.4e22, 0.02)
    row(pais, "its inertia (kg)", field_energy / C**2, 1.6e5, 0.02)
    schwinger = M_E**2 * C**3 / (E_CHARGE * HBAR)
    field = sigma / EPS0
    log_rate = math.log10(
        E_CHARGE**2 * field**2 / (4 * math.pi**3 * HBAR**2 * C)
    ) - math.pi * schwinger / field / math.log(10)
    row(pais, "log10 Schwinger rate at 5.6e15 V/m (per m^3 s)", log_rate, -268.0, 0.005)
    xi = 2 * ALPHA**2 * EPS0**2 * HBAR**3 / (45 * M_E**4 * C**5)
    row(pais, "Euler-Heisenberg fraction at 5.6e15 V/m", 6 * xi * field**2 / EPS0, 2.8e-9, 0.02)
    row(pais, "Euler-Heisenberg fraction at 1e9 V/m", 6 * xi * 1e18 / EPS0, 8.8e-23, 0.02)
    cutoff = (1e24 / C * 8 * math.pi**2 * C**3 / HBAR) ** 0.25
    row(pais, "Eq. 4 angular cutoff at 1e24 W/m^2 (1/s)", cutoff, 1.6e19, 0.02)
    row(pais, "its photon energy (keV)", HBAR * cutoff / EV / 1e3, 10.6, 0.01)
    row(pais, "Ford-Roman bound sampled over 1 ns (J/m^3)", 3 * HBAR / (32 * math.pi**2 * C**3 * 1e-36), 3.7e-26, 0.01)
    row(pais, "orders short over 1 ns", math.log10(9e16 / (3 * HBAR / (32 * math.pi**2 * C**3 * 1e-36))), 42.4, 0.002)
    gap = (math.pi**2 * HBAR * C / (720 * 9.0e16)) ** 0.25
    row(pais, "ideal-plate gap for -9e16 J/m^3 (m)", gap, 8.3e-12, 0.01)
    row(pais, "in Bohr radii", gap / sc.physical_constants["Bohr radius"][0], 0.16, 0.03)
    row(pais, "10 T over 1 m graviton conversion", 4 * math.pi * G * 100 / (MU0 * C**4), 8.3e-36, 0.01)
    path = math.sqrt(1e10 / (4 * math.pi * G * 1e20 / (MU0 * C**4) * 1e33))
    row(pais, "path for 1e10 W from 1e33 W/m^2 at 1e10 T (m)", path, 1.1e-3, 0.03)
    row(pais, "1e33 W/m^2 over the Schwinger intensity", 1e33 / (C * EPS0 * schwinger**2 / 2), 0.43, 0.01)
    moment_ddot = charge * radius**2 * omega / 3
    row(
        pais,
        "spin-up radiation, scale estimate Q R^2 omega/(3 tau^2) (W)",
        MU0 * moment_ddot**2 / (6 * math.pi * C**3),
        2.7e-13,
        0.02,
    )
    superforce = "pais-claims-falsification.md (Superforce)"
    electron_over_c4g = G * M_E**2 / (2 * HBAR * C)
    row(superforce, "electron Schrodinger step over c^4/G", electron_over_c4g, 8.8e-46, 0.01)
    row(
        superforce,
        "electron Schrodinger step over c^4/(2G), the sentence's referent",
        2 * electron_over_c4g,
        8.8e-46,
        0.01,
    )
    row(superforce, "Kreuzer bound / 4 (index match)", 5e-5 / 4, 1.25e-5, 1e-9)
    proton_radius = sc.physical_constants["proton rms charge radius"][0]
    proton_density = sc.m_p * C**2 / (4 * math.pi * proton_radius**3 / 3)
    row(superforce, "1e35 Pa over m_p c^2 / V_p", 1e35 / proton_density, 1.66, 0.01)
    row(superforce, "1e35 Pa times the proton cross-section (N)", 1e35 * math.pi * proton_radius**2, 2.2e5, 0.02)
    vacuum = "qpu_vacuum_cd_review_reconciliation.md"
    row(
        vacuum,
        "100 nm ideal Casimir mass equivalent (kg/m^3)",
        math.pi**2 * HBAR * C / (720 * 1e-28) / C**2,
        4.82e-17,
        0.002,
    )
    row(vacuum, "uniform-triple associator sign at D = 16", 1 - 2 * 1848 / 4096, 25 / 256, 1e-12)
    qet = qet_model()
    row(pais, "QET E_B at h = k = 1", qet["extracted_E_B"], 0.114748, 1e-4)
    row(pais, "QET reversed-feedback raise", qet["reversed_raise_E_x"], 0.332, 0.002)
    row(pais, "QET binned half-contrast (E_m - E_x)/2 magnitude", qet["half_contrast"], 0.223607, 1e-4)
    row(pais, "QET record-flip zero q*", qet["record_flip_zero"], 0.2566, 1e-3)
    row(pais, "QET Alice injection = record-steered floor magnitude", qet["alice_injected"], 0.707107, 1e-5)
    return rows


def spin_up_profiles(tau: float = 1.0) -> dict[str, float]:
    """Magnetic-dipole power of the worked-example shell for two spin-up profiles reaching 30000 RPM in tau.

    A uniform ramp has m'' = 0 between its ends (impulses at t = 0 and tau); omega(t) = omega_f sin^2(pi t/(2 tau))
    has |omega''| up to pi^2 omega_f / (2 tau^2), so its peak power is (pi^2/2)^2 = 24.4 times the scale estimate.
    """
    omega = 3.0e4 * 2 * math.pi / 60
    charge = 5.0e4 * 4 * math.pi * 4.0
    scale = MU0 * (charge * 4.0 * omega / (3 * tau**2)) ** 2 / (6 * math.pi * C**3)
    peak = scale * (math.pi**2 / 2) ** 2
    require(peak < 1e-10, "smooth spin-up radiation reaches 1e-10 W")
    return {
        "scale_estimate_W": scale,
        "uniform_ramp_interior_W": 0.0,
        "sin2_ramp_peak_W": peak,
        "sin2_ramp_mean_W": peak / 2,
    }


def algebra_rechecks() -> dict[str, object]:
    """Basis non-associativity counts N(D), the D = 16 witnesses, anticommuting pairs and Construction A on RM(1,3)."""
    counts = {}
    for dim in (8, 16, 32):
        signs = np.array([[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)], dtype=np.int64)
        idx = np.arange(dim)
        i, j, k = np.meshgrid(idx, idx, idx, indexing="ij")
        left = signs[i, j] * signs[i ^ j, k]
        right = signs[j, k] * signs[i, j ^ k]
        counts[str(dim)] = int((left != right).sum())
        require(counts[str(dim)] == (dim - 2) * (dim - 4) * (dim + 6) // 2, f"N({dim}) differs from the closed form")
    table = cd_table(16)
    eye = np.eye(16, dtype=np.int64)

    def product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return np.einsum("p,q,pqr->r", a, b, table)

    dark = product(eye[1] + eye[10], eye[4] - eye[15])
    bright = product(eye[1] + eye[10], eye[2] - eye[13])
    require(not dark.any(), "(e1 + e10)(e4 - e15) != 0")
    require(bright.tolist() == (eye[3] + eye[7] + eye[8] - eye[12]).tolist(), "(e1 + e10)(e2 - e13)")
    left = np.array([product(eye[1] + eye[10], eye[q]) for q in range(16)]).T
    rank = int(flint.fmpz_mat(left.tolist()).rank())
    require(rank == 12, f"rank L_(e1+e10) = {rank}")
    mats = [np.array([product(eye[m], eye[q]) for q in range(16)]).T for m in range(16)]
    anticommuting = sum(
        1 for p, q in itertools.combinations(range(1, 16), 2) if not (mats[p] @ mats[q] + mats[q] @ mats[p]).any()
    )
    require(anticommuting == 63, f"{anticommuting} anticommuting pairs")
    code = {
        tuple((c0 + sum(ci * ((v >> b) & 1) for b, ci in enumerate(cs))) % 2 for v in range(8))
        for c0 in (0, 1)
        for cs in itertools.product((0, 1), repeat=3)
    }
    require(len(code) == 16, "RM(1,3) does not have 16 words")
    # Integer vectors of squared length 4 are +-2 e_i or four entries +-1; Construction A keeps those whose
    # reduction mod 2 is a codeword, and x.x = 4 is norm 2 after the 1/sqrt2 scaling.
    candidates = [tuple(2 * s if b == i else 0 for b in range(8)) for i in range(8) for s in (1, -1)]
    for support in itertools.combinations(range(8), 4):
        for pattern in itertools.product((1, -1), repeat=4):
            entries = dict(zip(support, pattern, strict=True))
            candidates.append(tuple(entries.get(b, 0) for b in range(8)))
    norm4 = sum(1 for vector in candidates if tuple(v % 2 for v in vector) in code)
    require(norm4 == 240, f"Construction A gives {norm4} norm-2 vectors")
    return {
        "nonassociating_basis_triples": counts,
        "rank_L_e1_plus_e10": rank,
        "anticommuting_imaginary_pairs_of_105": anticommuting,
        "construction_a_norm2_vectors": norm4,
    }


# Ascella HOM visibility at the two calibration reads of docs/notes/quandela/calibration.md (87.46 % and 88.8 %).
ASCELLA_HOM_VISIBILITY = 0.875
ASSOCIATOR_PAIR = ((6, 7), (5, 7))  # a = (e6 + e7)/sqrt2, b = (e5 + e7)/sqrt2
ASSOCIATIVE_PAIR = ((1, 2), (1, 3))  # both inside the quaternions spanned by e0..e3
PHOTON_INPUTS = (2, 3)


def octonion_left(vector: np.ndarray) -> np.ndarray:
    """L_v as a matrix, columns indexed by the input basis vector."""
    return np.einsum("p,pqr->rq", vector, cd_table(8).astype(float))


def two_click_law(unitary: np.ndarray, inputs: tuple[int, int], visibility: float) -> dict[str, float]:
    """Two-click probabilities of two photons through a real unitary, threshold detectors, partial indistinguishability.

    The photon pair is the mixture visibility x (indistinguishable) + (1 - visibility) x (distinguishable); an
    indistinguishable pair exits (o1, o2), o1 != o2, with |U_o1x U_o2y + U_o1y U_o2x|^2, a distinguishable one with
    |U_o1x U_o2y|^2 + |U_o1y U_o2x|^2. Bunched outcomes give one click and are dropped; the law is unnormalized.
    """
    x, y = inputs
    law = {}
    for o1, o2 in itertools.combinations(range(len(unitary)), 2):
        direct, exchange = unitary[o1, x] * unitary[o2, y], unitary[o1, y] * unitary[o2, x]
        quantum = (direct + exchange) ** 2
        classical = direct**2 + exchange**2
        value = visibility * quantum + (1 - visibility) * classical
        if value > 1e-12:
            law[f"{o1}{o2}"] = float(value)
    return law


def ascella_two_photon_associator(visibility: float = ASCELLA_HOM_VISIBILITY) -> dict[str, object]:
    """Two photons through L_a L_b against L_(ab): the associator is visible only through two-photon interference.

    With a = (e6 + e7)/sqrt2, b = (e5 + e7)/sqrt2 and photons in modes 2 and 3, both maps keep span(e0..e3), so the
    run needs a 4-mode interferometer. Indistinguishable photons exit on pairs {03, 12} after L_a L_b and on
    {02, 13} after L_(ab); distinguishable photons give the same uniform law after both. The endpoint is
    D = P({03, 12} | two clicks) - P({02, 13} | two clicks). The associative control takes a, b inside the
    quaternions, where L_a L_b = L_(ab) and the two routes cannot differ.
    """
    eye = np.eye(8)
    table = cd_table(8).astype(float)
    out: dict[str, object] = {"visibility": visibility, "inputs": list(PHOTON_INPUTS)}
    for label, ((i, j), (k, m)) in (("associator", ASSOCIATOR_PAIR), ("associative_control", ASSOCIATIVE_PAIR)):
        a = (eye[i] + eye[j]) / math.sqrt(2)
        b = (eye[k] + eye[m]) / math.sqrt(2)
        product = np.einsum("p,q,pqr->r", a, b, table)
        routes = {"LaLb": octonion_left(a) @ octonion_left(b), "Lab": octonion_left(product)}
        arm: dict[str, object] = {"a": f"(e{i} + e{j})/sqrt2", "b": f"(e{k} + e{m})/sqrt2"}
        for name, unitary in routes.items():
            require(np.allclose(unitary.T @ unitary, eye), f"{name} is not orthogonal")
            require(not np.abs(unitary[4:, :4]).max() > 1e-12, f"{name} leaves span(e0..e3)")
            for v_label, v in (("ideal", 1.0), ("calibrated", visibility), ("distinguishable", 0.0)):
                law = two_click_law(unitary[:4, :4], PHOTON_INPUTS, v)
                total = sum(law.values())
                endpoint = (law.get("03", 0) + law.get("12", 0) - law.get("02", 0) - law.get("13", 0)) / total
                arm[f"{name}_{v_label}"] = {"two_click_mass": total, "D": endpoint, "law": law}
        out[label] = arm
    assoc = out["associator"]
    control = out["associative_control"]
    if not isinstance(assoc, dict) or not isinstance(control, dict):
        raise RuntimeError("arms missing")
    require(abs(assoc["LaLb_ideal"]["D"] - 1) < 1e-12 and abs(assoc["Lab_ideal"]["D"] + 1) < 1e-12, "ideal D != +-1")
    require(abs(assoc["LaLb_distinguishable"]["D"]) < 1e-12, "distinguishable photons see the associator")
    require(control["LaLb_ideal"]["law"] == control["Lab_ideal"]["law"], "the associative control separates routes")
    calibrated = assoc["LaLb_calibrated"]["D"]
    # D is a difference of multinomial frequencies with values +-1 or 0 per event: var(D) = (q - D^2)/n, q the
    # probability mass on the four counted pairs; n two-click events give standard error 0.01 at the calibrated law.
    counted = sum(assoc["LaLb_calibrated"]["law"].get(k, 0) for k in ("03", "12", "02", "13"))
    q = counted / assoc["LaLb_calibrated"]["two_click_mass"]
    out["route_difference_ideal"] = assoc["LaLb_ideal"]["D"] - assoc["Lab_ideal"]["D"]
    out["route_difference_control"] = control["LaLb_ideal"]["D"] - control["Lab_ideal"]["D"]
    out["two_click_events_for_0.01_standard_error"] = math.ceil((q - calibrated**2) / 1e-4)
    return out


def corpus_pairing_sign() -> dict[str, object]:
    """The corpus's linear pairing (J^a_n u, v) = (u, J^a_-n v) is not well defined; the Hermitian adjoint is.

    In the Chevalley basis the corpus's rule sends e_n to e_-n. The state h_0 e_-1|0> equals 2 e_-1|0>, yet pairing
    it with f_-1|0> through the word gives <0|e_1 h_0 f_-1|0> = -2k while the reduced state gives +2k: the map is
    no anti-automorphism. The adjoint e <-> f, which sugawara_sl2 uses, agrees on both routes.
    """
    word = affine_vev((("e", 1), ("h", 0), ("f", -1)))
    state = 2 * affine_vev((("e", 1), ("f", -1)))
    require(sp.simplify(word + state) == 0 and state != 0, "the linear pairing no longer contradicts itself")
    hermitian_word = affine_vev((("f", 1), ("h", 0), ("f", -1)))
    hermitian_state = 2 * affine_vev((("f", 1), ("f", -1)))
    require(sp.simplify(hermitian_word - hermitian_state) == 0, "the Hermitian pairing is inconsistent")
    return {"linear_word": str(word), "linear_state": str(state), "hermitian_agrees": True}


def quaternion_order_bridge() -> dict[str, object]:
    """The quaternion encoding of the Ascella order interferometer carries the corpus's sl(2) bracket.

    hypercomplex_operators.quaternion_matrix sends i, j, k to I = i sigma_3, J = i sigma_2 and K = IJ = i sigma_1, so
    H = -iI, E = (J - iK)/2, F = -(J + iK)/2, and [I, J] = 2K is [H, E] = 2E in the compact real form. The
    interferometer's dark probability is ||[A, B]||_F^2 / 8 = sin^2(theta) sin^2(phi), the squared bracket coefficient.
    """
    from hypercomplex_operators import order_interferometer, quaternion_matrix

    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s2 = np.array([[0, -1j], [1j, 0]])
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)
    h, e, f = s3, np.array([[0, 1], [0, 0]], dtype=complex), np.array([[0, 0], [1, 0]], dtype=complex)
    qi, qj, qk = (quaternion_matrix(v) for v in ([0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]))
    require(np.allclose(qi, 1j * s3) and np.allclose(qj, 1j * s2) and np.allclose(qk, 1j * s1), "chi(i, j, k)")
    require(np.allclose(qi @ qj - qj @ qi, 2 * qk), "[I, J] != 2K")
    chevalley = np.allclose(-1j * qi, h) and np.allclose((qj - 1j * qk) / 2, e) and np.allclose(-(qj + 1j * qk) / 2, f)
    require(chevalley, "H, E, F are not the stated combinations of I, J, K")
    for theta, phi in ((math.pi / 4, math.pi / 4), (0.3, -1.1), (1.2, 0.7)):
        a = math.cos(theta) * np.eye(2) + math.sin(theta) * qi
        b = math.cos(phi) * np.eye(2) + math.sin(phi) * qj
        dark = float(np.sum(np.abs(order_interferometer(theta, phi)[2:, 0]) ** 2))
        bracket = float(np.linalg.norm(a @ b - b @ a) ** 2 / 8)
        require(abs(dark - bracket) < 1e-12 and abs(dark - (math.sin(theta) * math.sin(phi)) ** 2) < 1e-12, "dark law")
    return {"I, J, K": "i sigma_3, i sigma_2, i sigma_1", "dark": "||[A, B]||^2 / 8", "angle_pairs_checked": 3}


def octonion_clifford() -> dict[str, object]:
    """Gamma_a = [[0, L_a], [L_conj(a), 0]] generates Cl(8) on the octonions; at 16 dimensions it fails on 42 pairs.

    The relation needs L_a L_conj(b) + L_b L_conj(a) = 2 delta_ab, which alternativity gives at 8 dimensions. On the
    sedenions the failing index pairs are exactly those of cd_core.sedenion_zero_divisor_corpus.
    """
    from cd_core import sedenion_zero_divisor_corpus

    out: dict[str, object] = {}
    for dim in (8, 16):
        left = cd_table(dim).transpose(0, 2, 1)  # left[a][r, q] = coefficient of e_r in e_a e_q
        conj = np.array([left[0]] + [-left[a] for a in range(1, dim)])
        zero = np.zeros((dim, dim), dtype=np.int64)
        gammas = np.array([np.block([[zero, left[a]], [conj[a], zero]]) for a in range(dim)])
        anti = np.einsum("aij,bjk->abik", gammas, gammas) + np.einsum("bij,ajk->abik", gammas, gammas)
        ident = np.eye(2 * dim, dtype=np.int64)
        failing = {
            (a, b)
            for a, b in itertools.combinations_with_replacement(range(dim), 2)
            if not np.array_equal(anti[a, b], 2 * ident * (a == b))
        }
        out[str(dim)] = len(failing)
        if dim == 8:
            chirality = np.linalg.multi_dot(list(gammas))
            sign = int(chirality[0, 0])
            split = np.block([[sign * np.eye(8, dtype=np.int64), zero], [zero, -sign * np.eye(8, dtype=np.int64)]])
            require(not failing and np.array_equal(chirality, split), "octonion gammas fail Cl(8) or 16 = 8_s + 8_c")
        else:
            divisors = {(i, j) for i, j, *_ in sedenion_zero_divisor_corpus()}
            require(failing == divisors, "sedenion Clifford failures differ from the zero-divisor index pairs")
    return {"failing_pairs_by_dimension": out, "sedenion_failures_are_zero_divisor_pairs": True}


def _clifford_sign(a: int, b: int) -> int:
    """Sign of e_A e_B in Cl(0,3), blades indexed by bit masks: reordering swaps, times -1 per shared generator."""
    swaps = sum(bin(a >> (i + 1)).count("1") for i in range(3) if b >> i & 1)
    return (-1) ** (swaps + bin(a & b).count("1"))


def associator_characters() -> dict[str, object]:
    """Column signs s(x) with (e_a e_b) e_x = s(x) e_a (e_b e_x) over the eight octonion basis columns.

    Every pair of distinct imaginary units gives a nontrivial character of F_2^3 whose kernel is the quaternion
    subalgebra {0, a, b, a ^ b}. The associative Cl(0,3) sign table on the same index set and a = b (alternativity)
    give the trivial character, so they are mutation arms of a sign interferometer on eight modes; no quaternionic
    pair can be one, because two distinct units generate a quaternion subalgebra that four columns leave.
    """

    def octonion(p: int, q: int) -> int:
        return cd_sign(8, p, q)

    def signs(sign: Callable[[int, int], int], a: int, b: int) -> list[int]:
        return [sign(a, b) * sign(a ^ b, x) * sign(b, x) * sign(a, b ^ x) for x in range(8)]

    for a, b in itertools.combinations(range(1, 8), 2):
        s = signs(octonion, a, b)
        character = all(s[x] * s[y] == s[x ^ y] for x in range(8) for y in range(8))
        require(character and {x for x in range(8) if s[x] == 1} == {0, a, b, a ^ b}, f"pair {(a, b)}: {s}")
    clifford = all(signs(_clifford_sign, a, b) == [1] * 8 for a, b in itertools.product(range(8), repeat=2))
    alternative = all(signs(octonion, a, a) == [1] * 8 for a in range(8))
    require(clifford and alternative, "a mutation arm carries a nontrivial associator character")
    return {"octonion_pairs_nontrivial": 21, "cl03_trivial": True, "a_equals_b_trivial": True}


ALBERT_CHECK = ROOT / "docs/notes/packages/manual/checks/albert_algebra.py"


def _albert_reference_pair(pair: tuple[int, int]) -> list[Fraction]:
    """2 B_i o B_j from albert_algebra.py's Fraction product, which is checked against SageMath."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("albert_algebra_check", ALBERT_CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ALBERT_CHECK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    i, j = pair
    return [2 * v for v in module.flatten(module.jordan(8, module.basis_element(i), module.basis_element(j)))]


def albert_table_cross_check() -> dict[str, int]:
    """jordan_double_product(8) against albert_algebra.py on all 729 basis pairs, through the signed slot map.

    albert_algebra.py stores (alpha, beta, gamma, x, y, z) with x at (0,1), y at (0,2) and z at (1,2); here the slots
    are (0,1), (1,2) and (2,0). So slot (1,2) is z, and slot (2,0) holds w with y = conj(w).
    """
    table = jordan_double_product(8)
    # Basis element k here is sign[k] times albert_algebra.py's element target[k].
    target = list(range(11)) + list(range(19, 27)) + list(range(11, 19))
    sign = [1] * 19 + [1] + [-1] * 7
    pairs = list(itertools.product(range(27), repeat=2))
    reference = dict(zip(pairs, parallel.ordered_map(_albert_reference_pair, pairs), strict=True))
    mismatches = 0
    for a, b in pairs:
        here = [Fraction(0)] * 27
        for r in range(27):
            here[target[r]] = Fraction(sign[r] * int(table[a, b, r]))
        expected = [sign[a] * sign[b] * v for v in reference[(target[a], target[b])]]
        mismatches += here != expected
    require(mismatches == 0, f"{mismatches} Jordan products differ from albert_algebra.py")
    return {"pairs_checked": len(pairs)}


LIGO_STRAIN = 1e-23  # order of the design strain sensitivity near 100 Hz


def decomposition_reconciliation() -> dict[str, object]:
    """Quantities that two independent decompositions of the corpus first stated with different definitions.

    Each is recomputed from its definition here, so the note can state which definition gives which number.
    - Peak power: a wave of field amplitude E carries the instantaneous peak flux c eps0 E^2 and the cycle average
      half of it; the corpus's own formula eps0 E^2 c A is the instantaneous peak.
    - Field gravity: linearised GR with the traceless electromagnetic stress gives the active density
      (u + p_1 + p_2 + p_3)/c^2 = 2u/c^2. A uniform sphere of radius R then has
      Phi(0) - Phi(R) = -(2 pi/3) G (2u/c^2) R^2, so h_00 differs between centre and surface by (8 pi/3) G u R^2/c^4.
      The coefficients 2 and 8 pi of the earlier order estimates bracket it.
    - Casimir modulation: the corpus names three lattice spacings; Gaussian surface roughness sigma multiplies
      cos(2 pi d/a) by exp(-2 pi^2 sigma^2/a^2) at every one of them.
    - Strong-field dispersion: (k l_P)^2 bounds the corpus's term when its alpha and E/E_S are at most 1; at the
      corpus's own laser field the factor (E/E_S)^2 lowers it further.
    """
    fields = fields_and_powers()
    instantaneous = EPS0 * CORPUS_FIELD_V_M**2 * C * CORPUS_AREA_M2
    require(close(instantaneous, 2 * fields["peak_power_W"], 1e-12), "instantaneous peak != twice the cycle average")

    def sphere_strain(density: float, radius: float) -> float:
        return 8 * math.pi / 3 * G * density * radius**2 / C**4

    field_density = EPS0 * CORPUS_FIELD_V_M**2 / 2
    derived = sphere_strain(field_density, 1.0)
    lower, upper = 2 * G * field_density / C**4, 8 * math.pi * G * field_density / C**4
    require(lower < derived < upper, "the derived gravity coefficient leaves the two estimates' bracket")
    laser_density = CORPUS_LASER_W_CM2 * 1e4 / C
    laser_strain = sphere_strain(laser_density, 1e-5)
    require(laser_strain / LIGO_STRAIN < 1e-15, "laser-focus strain within 15 decades of LIGO")

    planck_length = planck()["length_m"]
    spacings = {
        "planck_length": planck_length,
        "corpus_2.7e-35": CORPUS_LATTICE_M,
        "l_P_sqrt(8_pi_gamma)": loop_quantum_gravity()["lattice_length_m"],
    }
    roughness = 1e-10
    casimir = {
        name: {
            "periods_per_nm": 1e-9 / a,
            "log10_modulation_after_0.1nm_roughness": -2 * math.pi**2 * (roughness / a) ** 2 / math.log(10),
        }
        for name, a in spacings.items()
    }
    require(all(v["log10_modulation_after_0.1nm_roughness"] < -1e49 for v in casimir.values()), "Casimir modulation")

    laser = fields["laser_field_V_m"]
    schwinger = M_E**2 * C**3 / (E_CHARGE * HBAR)
    bound = (2 * math.pi / 500e-9 * planck_length) ** 2
    at_laser = ALPHA * (laser / schwinger) ** 2 * bound
    require(at_laser < bound < 1e-55, "dispersion bound ordering")

    planck_gev = math.sqrt(HBAR * C / G) * C**2 / GEV
    vev = planck_gev / ALPHA
    field_energy_ratio = field_density / CORPUS_FIELD_ENERGY_J_M3
    shift_coefficient = 3 * ALPHA / (45 * math.pi) / schwinger**2 * EPS0 / 2  # Euler-Heisenberg shift = coef E^4
    threshold = (CORPUS_VACUUM_DENSITY_BOUND / shift_coefficient) ** 0.25
    require(threshold < CORPUS_VACUUM_FIELD_V_M, "the stated threshold is not above the Euler-Heisenberg crossing")
    return {
        "peak_power_instantaneous_W": instantaneous,
        "peak_power_cycle_average_W": fields["peak_power_W"],
        "field_gravity_derived_over_1m": derived,
        "field_gravity_estimates_over_1m": [lower, upper],
        "laser_focus_strain": laser_strain,
        "laser_focus_strain_over_ligo": laser_strain / LIGO_STRAIN,
        "casimir_by_spacing": casimir,
        "dispersion_bound_500nm": bound,
        "dispersion_at_corpus_laser_500nm": at_laser,
        "vev_planck_mass_over_alpha_GeV": vev,
        "vev_over_corpus": vev / CORPUS_VEV_GEV,
        "field_energy_over_corpus": field_energy_ratio,
        "euler_heisenberg_field_for_corpus_bound_V_m": threshold,
    }


SECTIONS: dict[str, Callable[..., object]] = {
    "sl2": sl2_brackets,
    "e8": e8_structure,
    "albert": albert_symmetry_dimensions,
    "moufang": moufang_split,
    "kac": kac_determinant,
    "coulomb_gas": coulomb_gas,
    "sugawara": sugawara_sl2,
    "l_infinity_and_affine": l_infinity_and_affine,
    "scalar_eom": scalar_equation_of_motion,
    "numerology": frequency_numerology,
    "casimir": casimir,
    "fields": fields_and_powers,
    "euler_heisenberg": euler_heisenberg,
    "field_gravity": gravity_of_field,
    "scalar_potential": scalar_potential,
    "zero_point": zero_point,
    "lqg": loop_quantum_gravity,
    "predictions": prediction_sizes,
    "su5": su5_assignments,
    "existing_notes": existing_note_rechecks,
    "spin_up_profiles": spin_up_profiles,
    "algebra_rechecks": algebra_rechecks,
    "ascella_two_photon_associator": ascella_two_photon_associator,
    "corpus_pairing_sign": corpus_pairing_sign,
    "quaternion_order_bridge": quaternion_order_bridge,
    "octonion_clifford": octonion_clifford,
    "associator_characters": associator_characters,
    "albert_table_cross_check": albert_table_cross_check,
    "decomposition_reconciliation": decomposition_reconciliation,
}


def run_section(item: tuple[str, int]) -> object:
    """One independent section by name; the Kac section takes the highest level."""
    name, max_kac_level = item
    return kac_determinant(max_kac_level) if name == "kac" else SECTIONS[name]()


def run(max_kac_level: int) -> dict[str, object]:
    """Every section through the order-preserving process pool; nested maps inside a worker run in its slot."""
    names = list(SECTIONS)
    results = parallel.ordered_map(run_section, [(name, max_kac_level) for name in names], min_items=2)
    return dict(zip(names, results, strict=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--audit", action="store_true", help="add the level-5 Kac determinant")
    parser.add_argument("--out", type=Path, help="write the JSON here instead of standard output")
    args = parser.parse_args()
    result = run(5 if args.audit else 4)
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
