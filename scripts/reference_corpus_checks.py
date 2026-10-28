"""Exact and dimensional checks of a pasted technical-reference corpus on Lie, Jordan and conformal algebra.

The topic note docs/notes/topics/reference-corpus-falsification.md decomposes each claim of the corpus; this
script computes every value that note tags [E] and raises RuntimeError when a stated result fails, so a passing
run certifies the note. It reads no network, draws no random number and submits no job.

Algebra checks compute over the integers, the rationals or sympy's exact field. A rank stated as exact comes
from Gaussian elimination modulo the prime PRIME: a nonzero minor modulo PRIME is nonzero over Q, so the rank
modulo PRIME bounds the rational rank from below, and an explicit independent solution set bounds the nullity
from below. Octonion and sedenion products come from cd_core.cd_sign, the repository's convention authority.

Physical numbers use CODATA constants through scipy.constants and the Planck-unit and vacuum-polarization
helpers of pais_superforce_bounds and pais_claim_bounds; they are order estimates of the corpus's own inputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from functools import cache
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import constants as sc
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import pais_claim_bounds as claim_bounds  # noqa: E402
import pais_superforce_bounds as superforce  # noqa: E402

from cd_core import cd_sign, sedenion_zero_divisor_corpus  # noqa: E402
from hypercomplex_operators import order_interferometer, quaternion_matrix  # noqa: E402
from parallel import ordered_map  # noqa: E402

ALBERT_CHECK = ROOT / "docs/notes/packages/manual/checks/albert_algebra.py"
PRIME = 1_000_003

# Corpus inputs, quoted from the pasted reference conversation (docs/notes/topics/reference-corpus-falsification.md).
CORPUS_FIELD = 1.0e13  # V/m, "E_0 > E_crit ... ~ 10^13 V/m"
CORPUS_AREA = 1.0e-4  # m^2, "for A ~ 1 cm^2"
CORPUS_PEAK_POWER = 1.0e15  # W, "P ~ eps0 E^2 c A ~ 10^15 W"
CORPUS_LASER_INTENSITY = 1.0e22  # W/m^2, "I_laser ~ 10^18 W/cm^2"
CORPUS_LASER_WAIST = 1.0e-5  # m, "w_0 ~ 10 um"
CORPUS_FIELD_ENERGY = 1.0e9  # J/m^3, "E_field ~ 10^13 V/m -> energy density ~ 10^9 J/m^3"
CORPUS_HIGGS_ZPE = 1.0e9  # J/m^3, "Lambda ~ m_Higgs ... -> rho_ZPE ~ 10^9 J/m^3"
CORPUS_P2_SHIFT = 1.0e-12  # J/m^3, claim P2 threshold
CORPUS_P2_FIELD = 1.0e16  # V/m, claim P2 "E_crit ~ 10^16 V/m"
CORPUS_SCALAR_MASS_EV = 1.0e-3
CORPUS_VEV_GEV = 1.0e20
CORPUS_IMMIRZI = 0.2375
CORPUS_LATTICE = 2.7e-35  # m
CORPUS_SOUND_SPEED = 7000.0  # m/s
CORPUS_SPACING = 1.0e-3  # m
HIGGS_MASS_GEV = 125.0  # sets the order of the cutoff only
LIGO_STRAIN = 1.0e-23  # order of the design strain sensitivity near 100 Hz
OPTICAL_WAVELENGTH = 8.0e-7  # m, Ti:sapphire


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def modular_rank(matrix: np.ndarray, prime: int = PRIME) -> int:
    """Rank over Z/prime of an integer matrix by row reduction; a lower bound on the rank over Q."""
    work = np.mod(np.asarray(matrix, dtype=np.int64), prime)
    rows, cols = work.shape
    rank = 0
    for col in range(cols):
        if rank == rows:
            break
        pivots = np.nonzero(work[rank:, col])[0]
        if pivots.size == 0:
            continue
        pivot = rank + int(pivots[0])
        work[[rank, pivot]] = work[[pivot, rank]]
        inverse = pow(int(work[rank, col]), prime - 2, prime)
        work[rank, col:] = (work[rank, col:] * inverse) % prime
        below = work[rank + 1 :, col].copy()
        nonzero = np.nonzero(below)[0]
        if nonzero.size:
            target = rank + 1 + nonzero
            work[target, col:] = (work[target, col:] - np.outer(below[nonzero], work[rank, col:])) % prime
        rank += 1
    return rank


def gram(matrix: sparse.csr_array) -> np.ndarray:
    """Exact A^T A of a sparse integer matrix; scipy's sparse product runs in integer C loops, outside BLAS."""
    return np.asarray((matrix.T @ matrix).toarray(), dtype=np.int64)


# ---------------------------------------------------------------- Lie algebra sl(2) and su(2)


def sl2_brackets() -> dict[str, bool]:
    h = np.array([[1, 0], [0, -1]])
    e = np.array([[0, 1], [0, 0]])
    f = np.array([[0, 0], [1, 0]])

    def br(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return x @ y - y @ x

    out = {
        "[H,E]=2E": bool(np.array_equal(br(h, e), 2 * e)),
        "[H,F]=-2F": bool(np.array_equal(br(h, f), -2 * f)),
        "[E,F]=H": bool(np.array_equal(br(e, f), h)),
    }
    # su(2) as the compact real form: J_k = sigma_k / 2, H = 2 J_3, E = J_1 + i J_2, F = J_1 - i J_2.
    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s2 = np.array([[0, -1j], [1j, 0]])
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)
    out["E=J1+iJ2"] = bool(np.allclose((s1 + 1j * s2) / 2, e))
    out["H=2J3"] = bool(np.allclose(s3, h))
    # The Ascella order interferometer's encoding chi: I = i sigma_3, J = i sigma_2, K = IJ = i sigma_1, so the
    # Chevalley basis is H = -i I, E = (J - i K)/2, F = -(J + i K)/2 and [I, J] = 2K is [H, E] = 2E complexified.
    quat_i = quaternion_matrix([0, 1, 0, 0])
    quat_j = quaternion_matrix([0, 0, 1, 0])
    quat_k = quaternion_matrix([0, 0, 0, 1])
    out["chi(i)=i sigma3"] = bool(np.allclose(quat_i, 1j * s3))
    out["chi(j)=i sigma2"] = bool(np.allclose(quat_j, 1j * s2))
    out["chi(k)=chi(i)chi(j)=i sigma1"] = bool(np.allclose(quat_k, quat_i @ quat_j) and np.allclose(quat_k, 1j * s1))
    out["[I,J]=2K"] = bool(np.allclose(br(quat_i, quat_j), 2 * quat_k))
    out["H,E,F from I,J,K"] = bool(
        np.allclose(-1j * quat_i, h)
        and np.allclose((quat_j - 1j * quat_k) / 2, e)
        and np.allclose(-(quat_j + 1j * quat_k) / 2, f)
    )
    for theta, phi in ((math.pi / 4, math.pi / 4), (0.3, -1.1), (1.2, 0.7)):
        a = math.cos(theta) * np.eye(2) + math.sin(theta) * quat_i
        b = math.cos(phi) * np.eye(2) + math.sin(phi) * quat_j
        dark = float(np.sum(np.abs(order_interferometer(theta, phi)[2:, 0]) ** 2))
        commutator = float(np.linalg.norm(br(a, b)) ** 2 / 8)
        out[f"dark=|[A,B]|^2/8 at {theta:.2f},{phi:.2f}"] = math.isclose(
            dark, commutator, abs_tol=1e-12
        ) and math.isclose(dark, (math.sin(theta) * math.sin(phi)) ** 2, abs_tol=1e-12)
    require(all(out.values()), f"sl(2) brackets fail: {out}")
    return out


# ---------------------------------------------------------------- E8 roots and the Gosset 4_21 polytope


def e8_roots() -> np.ndarray:
    """The 240 roots in the doubled D8-plus-spinor coordinates (entries are twice the coordinates)."""
    integer = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            integer.append(v)
    half = [list(s) for s in itertools.product((1, -1), repeat=8) if s.count(-1) % 2 == 0]
    return np.array(integer + half, dtype=np.int64)


def e8_structure() -> dict[str, object]:
    roots = e8_roots()
    require(len(roots) == 240 and len({tuple(r) for r in roots}) == 240, "E8 root count")
    gramm = roots @ roots.T  # four times the inner products
    require(bool(np.all(np.diag(gramm) == 8)), "roots have norm 2")
    values, counts = np.unique(gramm[0], return_counts=True)
    distribution = {str(int(v) // 4): int(c) for v, c in zip(values, counts, strict=True)}
    require(all(np.array_equal(np.unique(row, return_counts=True)[1], counts) for row in gramm), "row profile")
    require(distribution == {"-2": 1, "-1": 56, "0": 126, "1": 56, "2": 1}, f"inner products {distribution}")
    # Reflection closure s_a(b) = b - <a, b> a over all 57600 ordered pairs.
    index = {tuple(r): k for k, r in enumerate(roots)}
    reflected = roots[None, :, :] - (gramm[:, :, None] // 4) * roots[:, None, :]
    closed = all(tuple(v) in index for v in reflected.reshape(-1, 8))
    require(closed, "E8 roots not closed under reflections")
    rank = modular_rank(roots)
    require(rank == 8, f"root span has rank {rank}")
    edges = int(np.count_nonzero(gramm == 4)) // 2
    require(edges == 6720, f"4_21 has {edges} edges")
    return {
        "roots": 240,
        "inner_product_distribution_from_one_root": distribution,
        "reflection_pairs_checked": 240 * 240,
        "span_rank": rank,
        "gosset_421_vertices": 240,
        "gosset_421_edges": edges,
        "gosset_421_dimension": 4 + 2 + 1 + 1,
    }


def e8_branchings() -> dict[str, int]:
    so16 = 120 + 128
    su5su5 = 24 + 24 + 4 * (10 * 5)
    so8so8_adj = 28 + 28 + 64
    so8so8_spin = 64 + 64
    require(so16 == 248 and su5su5 == 248, "E8 branching dimensions")
    require(so8so8_adj == 120 and so8so8_spin == 128, "Spin(8)^2 branching of Spin(16)")
    return {"so16_adjoint_plus_spinor": so16, "su5_su5": su5su5, "so8_so8_in_120": so8so8_adj}


def su5_assignments() -> dict[str, object]:
    """Dimension and hypercharge-trace tests of the SU(5) grouping, Y normalized so that Q = T3 + Y/2."""

    def content(states: list[tuple[int, int, Fraction]]) -> tuple[int, Fraction, Fraction]:
        dim = sum(c * w for c, w, _ in states)
        tr = sum((c * w * y for c, w, y in states), Fraction(0))
        tr3 = sum((c * w * y**3 for c, w, y in states), Fraction(0))
        return dim, tr, tr3

    standard_ten = [(3, 2, Fraction(1, 3)), (3, 1, Fraction(-4, 3)), (1, 1, Fraction(2))]
    standard_five_bar = [(3, 1, Fraction(2, 3)), (1, 2, Fraction(-1))]
    corpus_ten = [(3, 2, Fraction(1, 3)), (1, 2, Fraction(-1))]
    corpus_five_bar = [(3, 1, Fraction(-4, 3)), (3, 1, Fraction(2, 3)), (1, 1, Fraction(2))]
    st, sf, ct, cf = (content(x) for x in (standard_ten, standard_five_bar, corpus_ten, corpus_five_bar))
    require(st[:2] == (10, 0) and sf[:2] == (5, 0), "standard SU(5) grouping fails its own dimension or trace")
    require(ct[0] == 8 and cf[0] == 7, "corpus grouping dimensions")
    require(st[2] + sf[2] == ct[2] + cf[2] == 0, "one generation's Y^3 anomaly")
    return {
        "standard": {"10": st[0], "5bar": sf[0]},
        "corpus": {"10": ct[0], "5bar": cf[0]},
        "same_state_set": sorted(standard_ten + standard_five_bar) == sorted(corpus_ten + corpus_five_bar),
        "generation_Y3_trace": str(st[2] + sf[2]),
    }


# ---------------------------------------------------------------- Octonions, Spin(8) and triality


def left_matrices(dim: int) -> np.ndarray:
    """L[a][r, q] = coefficient of e_r in e_a e_q under cd_core."""
    out = np.zeros((dim, dim, dim), dtype=np.int64)
    for a, q in itertools.product(range(dim), repeat=2):
        out[a, a ^ q, q] = cd_sign(dim, a, q)
    return out


def clifford_from_left_multiplication(dim: int) -> dict[str, int]:
    """Gamma_a = [[0, L_a], [L_conj(a), 0]]; the Clifford relation needs L_a L_conj(b) + L_b L_conj(a) = 2 delta."""
    lm = left_matrices(dim)
    conj = np.array([lm[0]] + [-lm[a] for a in range(1, dim)])
    zero = np.zeros((dim, dim), dtype=np.int64)
    gammas = np.array([np.block([[zero, lm[a]], [conj[a], zero]]) for a in range(dim)])
    anti = np.einsum("aij,bjk->abik", gammas, gammas) + np.einsum("bij,ajk->abik", gammas, gammas)
    ident = np.eye(2 * dim, dtype=np.int64)
    failing_pairs = {
        (a, b)
        for a, b in itertools.combinations_with_replacement(range(dim), 2)
        if not np.array_equal(anti[a, b], 2 * ident * (a == b))
    }
    failing = len(failing_pairs)
    result = {"dimension": dim, "pairs_failing_clifford": failing}
    if dim == 16:
        # The failing pairs are the index pairs of the zero-divisor corpus: (e_i + t e_j) annihilates a nonzero
        # element only when L_i and L_j fail to anticommute.
        divisor_pairs = {(i, j) for i, j, *_ in sedenion_zero_divisor_corpus()}
        require(failing_pairs == divisor_pairs, "Clifford failures differ from the zero-divisor index pairs")
        result["equals_zero_divisor_index_pairs"] = 1
    if dim == 8:
        chirality = np.linalg.multi_dot(list(gammas))
        sign = int(chirality[0, 0])
        expected = np.block([[sign * np.eye(8, dtype=np.int64), zero], [zero, -sign * np.eye(8, dtype=np.int64)]])
        require(failing == 0 and np.array_equal(chirality, expected), "octonion gammas fail Cl(8)")
        result["chirality_sign_on_first_block"] = sign
    return result


def clifford_sign(a: int, b: int) -> int:
    """Sign of e_A e_B in Cl(0,3) with blades indexed by bit masks: reordering swaps times -1 per shared generator."""
    swaps = sum(bin(a >> (i + 1)).count("1") for i in range(3) if b >> i & 1)
    return (-1) ** (swaps + bin(a & b).count("1"))


def associator_characters() -> dict[str, object]:
    """Column signs s(x) with (e_a e_b) e_x = s(x) e_a (e_b e_x) over the 8 basis columns x.

    For the octonions every pair of distinct imaginary units gives a nontrivial character of F_2^3 whose kernel is
    the quaternion subalgebra {0, a, b, a^b}; the associative Cl(0,3) sign table on the same index set, and a = b
    under alternativity, give the trivial character. These are the ideal arm and mutation arms of a sign
    interferometer on eight modes.
    """

    def signs(sign: Callable[[int, int], int], a: int, b: int) -> list[int]:
        return [sign(a, b) * sign(a ^ b, x) * sign(b, x) * sign(a, b ^ x) for x in range(8)]

    def octonion(p: int, q: int) -> int:
        return cd_sign(8, p, q)

    nontrivial = 0
    for a, b in itertools.combinations(range(1, 8), 2):
        s = signs(octonion, a, b)
        character = all(s[x] * s[y] == s[x ^ y] for x in range(8) for y in range(8))
        kernel = {x for x in range(8) if s[x] == 1}
        require(character and kernel == {0, a, b, a ^ b}, f"octonion pair {(a, b)} column signs {s}")
        nontrivial += 1
    clifford_trivial = all(signs(clifford_sign, a, b) == [1] * 8 for a, b in itertools.product(range(8), repeat=2))
    alternative_trivial = all(signs(octonion, a, a) == [1] * 8 for a in range(8))
    require(clifford_trivial and alternative_trivial, "a mutation arm carries a nontrivial associator character")
    return {
        "octonion_pairs_nontrivial": nontrivial,
        "cl03_trivial": clifford_trivial,
        "a_equals_b_trivial": alternative_trivial,
    }


def d4_diagram_symmetries() -> int:
    cartan = np.array([[2, -1, 0, 0], [-1, 2, -1, -1], [0, -1, 2, 0], [0, -1, 0, 2]])
    count = sum(np.array_equal(cartan[np.ix_(p, p)], cartan) for p in itertools.permutations(range(4)))
    require(count == 6, f"D4 diagram has {count} symmetries")
    return int(count)


# ---------------------------------------------------------------- The Albert algebra H3(O)

OFFDIAG = ((0, 1), (0, 2), (1, 2))  # slots x, y, z of albert_algebra.py: entries 12, 13, 23


def albert_basis() -> np.ndarray:
    """27 Hermitian octonion matrices, shape (27, 3, 3, 8), in the order of albert_algebra.py."""
    basis = np.zeros((27, 3, 3, 8), dtype=np.int64)
    for i in range(3):
        basis[i, i, i, 0] = 1
    for slot, (i, j) in enumerate(OFFDIAG):
        for u in range(8):
            k = 3 + 8 * slot + u
            basis[k, i, j, u] = 1
            basis[k, j, i, u] = 1 if u == 0 else -1
    return basis


def albert_coordinates(matrices: np.ndarray) -> np.ndarray:
    """Coordinates of Hermitian matrices (..., 3, 3, 8); raises when an input is not Hermitian."""
    diag_imag = np.stack([matrices[..., i, i, 1:] for i in range(3)], axis=-1)
    require(not np.any(diag_imag), "diagonal entry is not real")
    for i, j in OFFDIAG:
        upper, lower = matrices[..., i, j, :], matrices[..., j, i, :]
        require(
            np.array_equal(lower[..., 0], upper[..., 0]) and np.array_equal(lower[..., 1:], -upper[..., 1:]),
            "not Hermitian",
        )
    parts = [matrices[..., i, i, 0][..., None] for i in range(3)]
    parts += [matrices[..., i, j, :] for i, j in OFFDIAG]
    return np.concatenate(parts, axis=-1)


def albert_doubled_product() -> np.ndarray:
    """J2[i, j, k]: coordinate k of 2 (B_i o B_j) = B_i B_j + B_j B_i."""
    structure = np.zeros((8, 8, 8), dtype=np.int64)
    for p, q in itertools.product(range(8), repeat=2):
        structure[p, q, p ^ q] = cd_sign(8, p, q)
    basis = albert_basis()
    product = np.einsum("aijp,bjkq,pqr->abikr", basis, basis, structure)
    return albert_coordinates(product + product.transpose(1, 0, 2, 3, 4))


def _albert_pair(pair: tuple[int, int]) -> list[Fraction]:
    spec = importlib.util.spec_from_file_location("albert_algebra_check", ALBERT_CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ALBERT_CHECK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    i, j = pair
    return [2 * v for v in module.flatten(module.jordan(8, module.basis_element(i), module.basis_element(j)))]


def albert_cross_check(doubled: np.ndarray) -> int:
    """Compare the vectorized table with albert_algebra.py's Fraction product, which is checked against SageMath."""
    pairs = list(itertools.product(range(27), repeat=2))
    reference = ordered_map(_albert_pair, pairs)
    mismatches = sum(
        any(Fraction(int(x)) != y for x, y in zip(doubled[i, j], ref, strict=True))
        for (i, j), ref in zip(pairs, reference, strict=True)
    )
    require(mismatches == 0, f"{mismatches} Jordan products differ from albert_algebra.py")
    return len(pairs)


def derivation_constraints(doubled: np.ndarray, block: int = 54) -> sparse.csr_array:
    """Rows of D(x o y) = D(x) o y + x o D(y) on basis pairs i <= j, linear in the 729 entries D[a, b]."""
    eye = np.eye(27, dtype=np.int64)
    first, second = np.triu_indices(27)
    blocks = []
    for start in range(0, len(first), block):
        pi, pj = first[start : start + block], second[start : start + block]
        rows = np.einsum("ak,nb->nkab", eye, doubled[pi, pj])
        rows -= np.einsum("nb,ank->nkab", eye[pi], doubled[:, pj, :])
        rows -= np.einsum("nb,nak->nkab", eye[pj], doubled[pi, :, :])
        blocks.append(sparse.csr_array(rows.reshape(-1, 729)))
    return sparse.csr_array(sparse.vstack(blocks, format="csr"))


def norm_trilinear(doubled: np.ndarray) -> np.ndarray:
    """72 t(e_i, e_j, e_k) for the cubic norm N(X) = t(X, X, X) of the degree-3 Jordan algebra."""
    tau = np.array([1, 1, 1] + [0] * 24, dtype=np.int64)
    g2 = doubled @ tau  # 2 T(e_i o e_j)
    h2 = np.einsum("ijm,mk->ijk", doubled, g2)  # 4 T((e_i o e_j) o e_k)
    require(
        all(np.array_equal(h2, h2.transpose(p)) for p in itertools.permutations(range(3))), "trace form not symmetric"
    )
    ttt = np.einsum("i,j,k->ijk", tau, tau, tau)
    mixed = np.einsum("i,jk->ijk", tau, g2) + np.einsum("j,ik->ijk", tau, g2) + np.einsum("k,ij->ijk", tau, g2)
    return 12 * ttt - 6 * mixed + 6 * h2


def norm_value(trilinear72: np.ndarray, x: Sequence[int]) -> Fraction:
    v = np.array(x, dtype=object)
    return Fraction(int(np.einsum("ijk,i,j,k->", trilinear72.astype(object), v, v, v)), 72)


def structure_constraints(trilinear72: np.ndarray) -> sparse.csr_array:
    """Rows of t(TX, Y, Z) + t(X, TY, Z) + t(X, Y, TZ) = 0 on basis triples i <= j <= k."""
    eye = np.eye(27, dtype=np.int64)
    triples = np.array(list(itertools.combinations_with_replacement(range(27), 3)))
    ti, tj, tk = triples.T
    t = trilinear72
    first = np.einsum("nb,na->nab", eye[ti], t[:, tj, tk].T)
    second = np.einsum("nb,na->nab", eye[tj], t[ti, :, tk])
    third = np.einsum("nb,na->nab", eye[tk], t[ti, tj, :])
    return sparse.csr_array((first + second + third).reshape(len(triples), 729))


def characteristic_discriminant(trilinear72: np.ndarray, doubled: np.ndarray, x: Sequence[int]) -> Fraction:
    """Discriminant of lambda^3 - T lambda^2 + S lambda - N for X; non-negative means three real roots."""
    v = np.array(x, dtype=object)
    trace = Fraction(int(v[0] + v[1] + v[2]))
    square_trace = Fraction(
        int(np.einsum("ijk,i,j,k->", doubled.astype(object), v, v, np.array([1, 1, 1] + [0] * 24, dtype=object))), 2
    )
    s = (trace**2 - square_trace) / 2
    n = norm_value(trilinear72, x)
    b, c, d = -trace, s, -n
    return 18 * b * c * d - 4 * b**3 * d + b**2 * c**2 - 4 * c**3 - 27 * d**2


def albert_algebra(cross_check: bool) -> dict[str, object]:
    doubled = albert_doubled_product()
    require(np.array_equal(doubled, doubled.transpose(1, 0, 2)), "Jordan product not commutative")
    checked_pairs = albert_cross_check(doubled) if cross_check else 0

    derivation = derivation_constraints(doubled)
    der_rank = modular_rank(gram(derivation))
    require(der_rank == 729 - 52, f"derivation constraints have rank {der_rank} mod {PRIME}")
    left = doubled.transpose(0, 2, 1)  # left[i][k, j] = coordinate k of 2 e_i o e_j
    inner = np.array([left[i] @ left[j] - left[j] @ left[i] for i, j in itertools.combinations(range(27), 2)])
    flat_inner = inner.reshape(len(inner), 729)
    require(not np.any(derivation @ flat_inner.T), "an inner derivation [L_x, L_y] fails the derivation rule")
    inner_rank = modular_rank(flat_inner)
    require(inner_rank == 52, f"inner derivations span rank {inner_rank}")

    trilinear = norm_trilinear(doubled)
    identity = [1, 1, 1] + [0] * 24
    require(norm_value(trilinear, identity) == 1, "N(I) != 1")
    require(norm_value(trilinear, [2, 3, 5] + [0] * 24) == 30, "N(diag(2, 3, 5)) != 30")
    constraints = structure_constraints(trilinear)
    str_rank = modular_rank(gram(constraints))
    require(str_rank == 729 - 78, f"reduced structure constraints have rank {str_rank} mod {PRIME}")
    traceless = [left[0] - left[1], left[1] - left[2]] + [left[k] for k in range(3, 27)]
    candidates = np.concatenate([flat_inner, np.array(traceless).reshape(26, 729)])
    require(not np.any(constraints @ candidates.T), "candidate fails norm invariance")
    str_explicit = modular_rank(candidates)
    require(str_explicit == 78, f"explicit reduced structure elements span {str_explicit}")
    scaling = np.eye(27, dtype=np.int64).reshape(729)
    require(bool(np.any(constraints @ scaling)), "the identity map preserves N")

    samples = [
        [1, 2, 3] + [((7 * k) % 5) - 2 for k in range(24)],
        [0, 0, 0] + [1] * 24,
        [4, -1, 2] + [k % 3 for k in range(24)],
    ]
    discriminants = [characteristic_discriminant(trilinear, doubled, x) for x in samples]
    require(all(d >= 0 for d in discriminants), f"a characteristic cubic has complex roots: {discriminants}")
    return {
        "dimension": 27,
        "pairs_cross_checked_with_albert_algebra_py": checked_pairs,
        "der_dimension": 52,
        "der_constraint_rank_mod_p": der_rank,
        "inner_derivation_rank_mod_p": inner_rank,
        "reduced_structure_dimension": 78,
        "structure_constraint_rank_mod_p": str_rank,
        "identity_scales_norm": True,
        "characteristic_discriminants": [str(d) for d in discriminants],
    }


# ---------------------------------------------------------------- L-infinity identities


def linfinity_counterexample() -> dict[str, object]:
    """l1 = l3 = 0 and a skew bracket failing Jacobi: the corpus's n = 3 identity holds, the true one fails.

    Every term of the corpus's identity contains l1 or l3, so it vanishes identically here; the n = 3 identity of
    an L-infinity algebra with l1 = l3 = 0 is the Jacobi identity of l2.
    """
    structure = {(0, 1): 1, (1, 2): 0}  # [e0, e1] = e1, [e1, e2] = e0; the Jacobiator of (e0, e1, e2) is e0

    def bracket(x: Sequence[int], y: Sequence[int]) -> list[int]:
        out = [0, 0, 0]
        for (i, j), k in structure.items():
            out[k] += x[i] * y[j] - x[j] * y[i]
        return out

    e = [[int(i == j) for j in range(3)] for i in range(3)]
    cyclic = (
        bracket(bracket(e[0], e[1]), e[2]),
        bracket(bracket(e[1], e[2]), e[0]),
        bracket(bracket(e[2], e[0]), e[1]),
    )
    jacobiator = [sum(t) for t in zip(*cyclic, strict=True)]
    require(any(jacobiator), "the counterexample bracket satisfies Jacobi")
    return {"corpus_n3_residual": 0, "jacobiator_e0_e1_e2": jacobiator}


def virasoro_cocycle(window: int = 8) -> int:
    """The central term of the Virasoro bracket satisfies the cocycle (Jacobi) identity on a window of modes."""
    c = sp.Symbol("c")

    def omega(m: int, n: int) -> sp.Expr:
        return c / 12 * (m**3 - m) * (1 if m + n == 0 else 0)

    checked = 0
    for m, n, p in itertools.product(range(-window, window + 1), repeat=3):
        total = (m - n) * omega(m + n, p) + (n - p) * omega(n + p, m) + (p - m) * omega(p + m, n)
        require(sp.simplify(total) == 0, f"Virasoro cocycle fails at {(m, n, p)}")
        checked += 1
    return checked


# ---------------------------------------------------------------- mode-algebra vacuum engine

Mode = tuple[int, int]  # (generator index, mode number)
Word = tuple[Mode, ...]
Terms = list[tuple[sp.Expr, Word]]


class ModeAlgebra:
    """Vacuum expectation values <0| word |0> for a Lie algebra of modes with a highest-weight vacuum.

    The rightmost mode that is not a creation operator moves right through creation operators by its
    commutator; at the right end an annihilator gives zero and a zero mode gives its vacuum eigenvalue.
    A word of creation operators alone pairs to zero with <0|, and the empty word to one.
    """

    def __init__(self, bracket: Callable[[Mode, Mode], Terms], zero_mode_value: Callable[[int], sp.Expr | None]):
        self.bracket = bracket
        self.zero_mode_value = zero_mode_value
        self.cache: dict[Word, sp.Expr] = {}

    def vev(self, word: Word) -> sp.Expr:
        if word in self.cache:
            return self.cache[word]
        movers = [i for i, (_, n) in enumerate(word) if n >= 0]
        if not movers:
            value: sp.Expr = sp.Integer(1 if not word else 0)
        else:
            i = movers[-1]
            mode = word[i]
            if i == len(word) - 1:
                eigen = self.zero_mode_value(mode[0]) if mode[1] == 0 else None
                value = sp.Integer(0) if eigen is None else sp.expand(eigen * self.vev(word[:-1]))
            else:
                nxt = word[i + 1]
                value = self.vev(word[:i] + (nxt, mode) + word[i + 2 :])
                for coef, inserted in self.bracket(mode, nxt):
                    value += coef * self.vev(word[:i] + inserted + word[i + 2 :])
                value = sp.expand(value)
        self.cache[word] = value
        return value

    def pair(self, left: Terms, right: Terms) -> sp.Expr:
        return sp.expand(sum((a * b * self.vev(u + v) for a, u in left for b, v in right), sp.Integer(0)))


def normal_ordered(n: int, generators: Sequence[int], cutoff: int, scale: sp.Expr) -> Terms:
    """scale * sum_a sum_{|p| <= cutoff} :J^a_p J^a_(n-p):, the larger mode index on the right."""
    terms: Terms = []
    for a in generators:
        for p in range(-cutoff, cutoff + 1):
            q = n - p
            if abs(q) > cutoff:
                continue
            terms.append((scale, ((a, p), (a, q)) if p <= q else ((a, q), (a, p))))
    return terms


def sugawara_su2(cutoff: int = 4) -> dict[str, object]:
    """su(2) currents in the corpus's first convention, f^abc = i eps^abc, so sum f^abc f^acd = +2 delta^bd."""
    level = sp.Symbol("K")
    eps = {p: int(sp.LeviCivita(*p)) for p in itertools.product(range(3), repeat=3)}
    f = {p: sp.I * v for p, v in eps.items()}
    contraction = {
        (b, d): sp.expand(sum(f[(a, b, c)] * f[(a, c, d)] for a in range(3) for c in range(3)))
        for b in range(3)
        for d in range(3)
    }
    require(all(contraction[(b, d)] == (2 if b == d else 0) for b, d in contraction), "sum f f != 2 delta")
    dual = sp.Integer(1)  # 2 h_dual = 2 in this normalization

    def bracket(x: Mode, y: Mode) -> Terms:
        (a, m), (b, n) = x, y
        out: Terms = [(f[(a, b, c)], ((c, m + n),)) for c in range(3) if f[(a, b, c)] != 0]
        if a == b and m + n == 0 and m != 0:
            out.append((level * m, ()))
        return out

    algebra = ModeAlgebra(bracket, lambda _a: None)  # J^a_0 annihilates the singlet vacuum
    scale = 1 / (2 * (level + dual))
    central = {}
    for cut in (cutoff - 1, cutoff):
        two = algebra.pair(normal_ordered(2, range(3), cut, scale), normal_ordered(-2, range(3), cut, scale))
        central[cut] = sp.simplify(2 * two)
    require(sp.simplify(central[cutoff] - central[cutoff - 1]) == 0, "c depends on the mode cutoff")
    expected = sp.simplify(3 * level / (level + dual))
    require(sp.simplify(central[cutoff] - expected) == 0, f"c = {central[cutoff]}")
    three = algebra.pair(
        normal_ordered(3, range(3), cutoff + 1, scale), normal_ordered(-3, range(3), cutoff + 1, scale)
    )
    require(sp.simplify(three - 2 * expected) == 0, "<L3 L-3> != 2c")

    s0 = normal_ordered(0, range(3), cutoff, sp.Rational(1, 2))
    weight_matrix = sp.expand(sum(c * algebra.vev(((0, 1),) + w + ((0, -1),)) for c, w in s0))
    norm = algebra.vev(((0, 1), (0, -1)))
    require(sp.simplify(weight_matrix - (level + dual) * norm) == 0, "[S0, J_-1]|0> != (K + h) J_-1|0>")

    # The linear map J^a_n -> J^a_-n is no anti-automorphism: pairing the state J^2_0 J^0_-1 |0> = f^{201} J^1_-1 |0>
    # with J^1_-1 |0> gives different values from the word and from the reduced state.
    from_word = algebra.vev(((0, 1), (2, 0), (1, -1)))
    from_state = sp.expand(f[(2, 0, 1)] * algebra.vev(((1, 1), (1, -1))))
    hermitian_state = sp.expand(sp.conjugate(f[(2, 0, 1)]) * algebra.vev(((1, 1), (1, -1))))
    require(sp.simplify(from_word + from_state) == 0 and from_state != 0, "bilinear-form sign contradiction absent")
    require(sp.simplify(from_word - hermitian_state) == 0, "the sesquilinear form is inconsistent")
    return {
        "central_charge": str(expected),
        "central_charge_su2_level_k": "3k/(k+2) with K = k/2",
        "cutoffs_agree": [cutoff - 1, cutoff],
        "L3_check": "2c",
        "current_weight_denominator": "K + h_dual",
        "bilinear_pairing_word_vs_state": [str(from_word), str(from_state)],
    }


def coulomb_gas(cutoff: int = 5) -> dict[str, str]:
    """Feigin-Fuchs modes L_n = 1/2 sum :a a: + beta (n+1) a_n on the Fock vacuum of momentum alpha."""
    alpha, beta = sp.symbols("alpha beta")

    def bracket(x: Mode, y: Mode) -> Terms:
        (_, m), (_, n) = x, y
        return [(sp.Integer(m), ())] if m + n == 0 and m != 0 else []

    algebra = ModeAlgebra(bracket, lambda _g: alpha)

    def virasoro(n: int) -> Terms:
        terms = normal_ordered(n, [0], cutoff, sp.Rational(1, 2))
        return terms + [(beta * (n + 1), ((0, n),))]

    weight = algebra.pair([(sp.Integer(1), ())], virasoro(0))
    two = algebra.pair(virasoro(2), virasoro(-2))
    central = sp.expand(2 * (two - 4 * weight))
    three = algebra.pair(virasoro(3), virasoro(-3))
    require(sp.expand(three - 6 * weight - 2 * central) == 0, "<L3 L-3> != 6h + 2c")
    q = sp.Symbol("Q")
    require(sp.expand(central.subs(beta, -q) - (1 - 12 * q**2)) == 0, f"c = {central}")
    require(sp.expand(weight.subs(beta, -q) - (alpha**2 / 2 - q * alpha)) == 0, f"h = {weight}")

    m, r, s = sp.symbols("m r s", positive=True)
    qq = 1 / sp.sqrt(2 * m * (m + 1))
    root = (2 * m + 1) / sp.sqrt(2 * m * (m + 1))  # the positive square root of Q^2 + 2
    require(sp.simplify(root**2 - (qq**2 + 2)) == 0, "sqrt(Q^2 + 2) != (2m + 1)/sqrt(2m(m + 1))")
    a = qq + root
    b = qq - root
    require(sp.simplify(a * b + 2) == 0 and sp.simplify(a**2 - 2 * (m + 1) / m) == 0, "screening momenta")
    a_rs = (1 - r) * a / 2 + (1 - s) * b / 2
    h_rs = sp.simplify(a_rs * (a_rs - 2 * qq) / 2)
    kac = ((r * (m + 1) - s * m) ** 2 - 1) / (4 * m * (m + 1))
    require(sp.simplify(h_rs - kac) == 0, "h_rs differs from the Kac table formula")
    return {"c": "1 - 12 Q^2", "h_alpha": "alpha^2/2 - Q alpha", "h_rs": "((r(m+1) - s m)^2 - 1)/(4 m (m+1))"}


@cache
def partitions(n: int, largest: int | None = None) -> tuple[tuple[int, ...], ...]:
    largest = n if largest is None else largest
    if n == 0:
        return ((),)
    out: list[tuple[int, ...]] = []
    for k in range(min(n, largest), 0, -1):
        out.extend((k, *rest) for rest in partitions(n - k, k))
    return tuple(out)


def partition_count(n: int) -> int:
    return len(partitions(n)) if n >= 0 else 0


def kac_constant(level: int) -> int:
    """K_N = prod over rs <= N of ((2r)^s s!)^(p(N - rs) - p(N - r(s + 1)))."""
    value = Fraction(1)
    for r in range(1, level + 1):
        for s in range(1, level // r + 1):
            exponent = partition_count(level - r * s) - partition_count(level - r * (s + 1))
            value *= Fraction((2 * r) ** s * math.factorial(s)) ** exponent
    require(value.denominator == 1, "K_N not an integer")
    return int(value)


def virasoro_gram(level: int) -> tuple[sp.Matrix, sp.Symbol, sp.Symbol]:
    h, c = sp.symbols("h c")

    def bracket(x: Mode, y: Mode) -> Terms:
        (_, m), (_, n) = x, y
        out: Terms = []
        if m != n:
            out.append((sp.Integer(m - n), ((0, m + n),)))
        if m + n == 0 and m**3 != m:
            out.append((c * (m**3 - m) / 12, ()))
        return out

    algebra = ModeAlgebra(bracket, lambda _g: h)
    states = partitions(level)
    words = [tuple((0, -k) for k in lam) for lam in states]
    adjoints = [tuple((0, k) for k in reversed(lam)) for lam in states]
    matrix = sp.Matrix(len(states), len(states), lambda i, j: algebra.vev(adjoints[i] + words[j]))
    return matrix, h, c


def kac_determinant(level: int) -> dict[str, object]:
    matrix, h, c = virasoro_gram(level)
    det = sp.expand(matrix.det(method="berkowitz"))
    t = sp.Symbol("t")
    on_curve = det.subs(c, 13 - 6 * t - 6 / t)
    product = sp.Integer(kac_constant(level))
    for r in range(1, level + 1):
        for s in range(1, level // r + 1):
            h_rs = sp.Rational(r * r - 1, 4) * t + sp.Rational(s * s - 1, 4) / t + sp.Rational(1 - r * s, 2)
            product *= (h - h_rs) ** partition_count(level - r * s)
    require(sp.cancel(on_curve - product) == 0, f"level {level} Gram determinant differs from the Kac product")
    degree = sp.Poly(det, h).degree()
    parts = sum(len(lam) for lam in partitions(level))
    divisor_sum = sum(partition_count(level - r * s) for r in range(1, level + 1) for s in range(1, level // r + 1))
    require(degree == parts == divisor_sum, "degree in h differs from the zero count")
    guessed = math.prod((2 * n) ** partition_count(level - n) for n in range(1, level + 1))
    return {
        "level": level,
        "dimension": len(partitions(level)),
        "K_N": kac_constant(level),
        "guessed_K_N": guessed,
        "degree_in_h": degree,
    }


def level_two_ising() -> dict[str, str]:
    matrix, h, c = virasoro_gram(2)  # basis L_-2 |h>, L_-1^2 |h>
    require(matrix == sp.Matrix([[4 * h + c / 2, 6 * h], [6 * h, 8 * h**2 + 4 * h]]), f"level-2 Gram matrix {matrix}")
    roots = sp.solve(sp.expand(matrix.det()).subs(c, sp.Rational(1, 2)), h)
    require(set(roots) == {0, sp.Rational(1, 2), sp.Rational(1, 16)}, f"Ising roots {roots}")
    return {"gram_L-2_L-1^2": "[[4h + c/2, 6h], [6h, 8h^2 + 4h]]", "roots_at_c_half": "0, 1/2, 1/16"}


# ---------------------------------------------------------------- physical orders of magnitude


def physics() -> dict[str, float]:
    eps0, c, hbar = sc.epsilon_0, sc.c, sc.hbar
    out: dict[str, float] = {}
    out["peak_power_W"] = eps0 * CORPUS_FIELD**2 * c * CORPUS_AREA
    out["peak_power_over_corpus"] = out["peak_power_W"] / CORPUS_PEAK_POWER
    out["field_energy_J_m3"] = eps0 * CORPUS_FIELD**2 / 2
    out["field_energy_over_corpus"] = out["field_energy_J_m3"] / CORPUS_FIELD_ENERGY
    out["laser_field_V_m"] = math.sqrt(2 * CORPUS_LASER_INTENSITY / (eps0 * c))
    out["magnetic_field_T"] = CORPUS_FIELD / c
    out["e_crit_from_corpus_rho_V_m"] = math.sqrt(2 * CORPUS_HIGGS_ZPE / eps0)

    def zpe(cutoff: float) -> float:
        return hbar * cutoff**4 / (8 * math.pi**2 * c**3)

    higgs = HIGGS_MASS_GEV * 1e9 * sc.e / hbar
    planck = 1 / math.sqrt(hbar * sc.G / c**5)
    out["zpe_higgs_cutoff_J_m3"] = zpe(higgs)
    out["zpe_higgs_over_corpus"] = zpe(higgs) / CORPUS_HIGGS_ZPE
    out["zpe_planck_cutoff_J_m3"] = zpe(planck)
    out["corpus_prefactor_over_correct"] = (1 / (16 * math.pi**2)) / (1 / (8 * math.pi**2))
    out["coherence_length_m"] = hbar * c / (CORPUS_SCALAR_MASS_EV * sc.e)
    planck_mass_gev = superforce.planck_mass() * c**2 / sc.e / 1e9
    out["vev_planck_over_alpha_GeV"] = planck_mass_gev / sc.fine_structure
    out["vev_over_corpus"] = out["vev_planck_over_alpha_GeV"] / CORPUS_VEV_GEV
    lp = superforce.planck_length()
    out["lqg_scale_m"] = lp * math.sqrt(8 * math.pi * CORPUS_IMMIRZI)
    out["lqg_scale_over_corpus"] = out["lqg_scale_m"] / CORPUS_LATTICE
    out["lqg_area_gap_root_m"] = lp * math.sqrt(4 * math.sqrt(3) * math.pi * CORPUS_IMMIRZI)
    out["casimir_periods_per_nm"] = 1e-9 / CORPUS_LATTICE
    k_optical = 2 * math.pi / OPTICAL_WAVELENGTH
    out["dispersion_factor"] = (out["laser_field_V_m"] / claim_bounds.schwinger_field()) ** 2 * (k_optical * lp) ** 2
    out["tourmaline_frequency_Hz"] = CORPUS_SOUND_SPEED / (2 * CORPUS_SPACING)
    f_planck = 1 / superforce.planck_length() * c
    for name, target in (("148Hz", 148.0), ("3.5MHz", 3.5e6)):
        out[f"golden_exponent_{name}"] = math.log(target * sc.fine_structure / f_planck) / math.log(
            (1 + math.sqrt(5)) / 2
        )
    out["schwinger_field_V_m"] = claim_bounds.schwinger_field()
    # P1: a field's energy density curves spacetime through 8 pi G / c^4 = 8 pi / (c^4 / G).
    u_laser = CORPUS_LASER_INTENSITY / c
    out["p1_ricci_scale_per_m2"] = 8 * math.pi * u_laser / superforce.planck_force()
    out["p1_strain_over_waist"] = out["p1_ricci_scale_per_m2"] * CORPUS_LASER_WAIST**2
    out["p1_strain_over_ligo"] = out["p1_strain_over_waist"] / LIGO_STRAIN
    # P2: the Euler-Heisenberg energy shift of a static field.
    out["p2_shift_at_1e16_J_m3"] = (
        claim_bounds.euler_heisenberg_fraction(CORPUS_P2_FIELD) * eps0 * CORPUS_P2_FIELD**2 / 2
    )
    coefficient = claim_bounds.euler_heisenberg_fraction(1.0) * eps0 / 2  # shift = coefficient * E^4
    out["p2_field_for_1e-12_J_m3_V_m"] = (CORPUS_P2_SHIFT / coefficient) ** 0.25

    require(out["peak_power_over_corpus"] > 1e4, "peak power no longer exceeds the corpus by four orders")
    require(out["field_energy_over_corpus"] > 1e5, "field energy no longer exceeds the corpus by five orders")
    require(1e12 < out["laser_field_V_m"] < 1e13, "laser field outside the corpus's order")
    require(out["zpe_higgs_over_corpus"] > 1e30, "Higgs-cutoff ZPE within 30 orders of the corpus")
    require(1.9e-4 < out["coherence_length_m"] < 2.0e-4, "Compton length of 1 meV")
    require(1.3 < out["lqg_scale_over_corpus"] < 1.6, "LQG scale ratio")
    require(out["dispersion_factor"] < 1e-60, "strong-field dispersion factor reaches 1e-60")
    require(out["p1_strain_over_ligo"] < 1e-15, "laser-curvature strain within 15 orders of LIGO")
    require(out["p2_shift_at_1e16_J_m3"] > CORPUS_P2_SHIFT, "Euler-Heisenberg shift below the P2 threshold")
    require(out["p2_field_for_1e-12_J_m3_V_m"] < CORPUS_P2_FIELD, "P2 threshold field exceeds 1e16 V/m")
    return out


def checks(cross_check: bool, kac_levels: Sequence[int]) -> dict[str, object]:
    return {
        "sl2": sl2_brackets(),
        "e8": e8_structure(),
        "e8_branchings": e8_branchings(),
        "su5": su5_assignments(),
        "clifford_octonion": clifford_from_left_multiplication(8),
        "clifford_sedenion": clifford_from_left_multiplication(16),
        "d4_symmetries": d4_diagram_symmetries(),
        "associator_characters": associator_characters(),
        "albert": albert_algebra(cross_check),
        "linfinity": linfinity_counterexample(),
        "virasoro_cocycle_triples": virasoro_cocycle(),
        "sugawara": sugawara_su2(),
        "coulomb_gas": coulomb_gas(),
        "kac_level_two": level_two_ising(),
        "kac": ordered_map(kac_determinant, list(kac_levels), min_items=1),
        "physics": physics(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--kac-levels", type=int, default=5, help="highest Verma level whose Gram determinant is checked"
    )
    parser.add_argument(
        "--skip-cross-check", action="store_true", help="skip the 729-pair comparison with albert_algebra.py"
    )
    parser.add_argument("--json", action="store_true", help="print every computed value as JSON")
    args = parser.parse_args(argv)
    result = checks(not args.skip_cross_check, range(1, args.kac_levels + 1))
    print(json.dumps(result, indent=2, default=str) if args.json else "reference_corpus_checks_pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
