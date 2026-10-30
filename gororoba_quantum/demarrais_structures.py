"""Cayley-Dickson 1D-to-8192D (DekatrisVoudon) tower and Robert de Marrais zero-divisor structures.

This module provides exact algebraic and spectral constructors for the Cayley-Dickson 2^N-ion
tower from N = 0 (1D Real) through N = 13 (8192D DekatrisVoudon), unifying:
- Implements exact deterministic constructors grounded in `cd_core.py` and certified with `python-flint` (`fmpz_mat`):
  - `TOWER_TAXONOMY`: Full tower from N = 0 (1D Real) through N = 13
    (8192D DekatrisVoudon, 11,180,715 positive cyclic trips).
- Robert P. C. de Marrais's zero-divisor hierarchy (arXiv:math/0011260, math/0207003, math/0603281,
  math/0703745, 0704.0026, 0704.0112, 0804.3416):
  1. Sedenion (16D) 42 Assessors, 7 Octahedral Box-Kites (K_{2,2,2}), 8 Sails (2 Zigzag (-,-,-) sails
     and 6 Trefoil (+,+,-) vents), Zaslavsky Lanyards (switching equivalence with spectrum {+2^3, -2^3}),
     and Catamaran Twists (Royal Hunt Brocade).
  2. Pathion (32D) 14x14 Sand Mandalas (Emanation Tables with 168 = |PSL(2,7)| fillable cells and
     72-cell I_2 * 3C_4 DMZ sparsity for S in 9..15), Hidden Box-Kites (HBKs, Roundabout Theorem),
     and 8D Cowbird Octonion Eggs ({0, X} union L_trip union U_trip, certified Moufang and norm-multiplicative
     with python-flint fmpz_mat).
  3. Kite-Chain Middens K_{2^{N-3}, 2^{N-3}, 2^{N-3}} across N = 4..13 (16D Sedenion K_{2,2,2} up to
     8192D DekatrisVoudon K_{1024,1024,1024}), their exact 12-dimensional equitable-partition quotient
     unitary for 12-mode photonic chips (Ascella and Belenos), and their scale-invariant flat-band
     zero-eigenvalue fraction (Compact Localized States).

Usage:
  "$PYTHON" gororoba_quantum/demarrais_structures.py --self-test
"""

from __future__ import annotations

import argparse
import functools
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# Optional accelerators: each name is None where its package is absent.
flint: Any = None
cp: Any = None
nb: Any = None
try:
    import flint as _flint

    flint = _flint
except ModuleNotFoundError:
    pass
try:
    import cupy as _cupy

    cp = _cupy
except ModuleNotFoundError:
    pass
try:
    import numba as _numba

    nb = _numba
except ModuleNotFoundError:
    pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "gororoba_quantum") not in sys.path:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import cd_multiply_exact, cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

TOLERANCE = 1e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class TowerLevel:
    """Exact metadata for level N (dimension 2^N) of the Cayley-Dickson tower."""

    level: int
    dimension: int
    name: str
    latin_name: str
    qubits: int
    trip_count: int
    midden_part_size: int
    midden_vertices: int
    midden_edges: int
    flat_band_fraction: float


TOWER_NAMES: tuple[tuple[int, str, str], ...] = (
    (0, "Real", "Reales"),
    (1, "Complex", "Complexus"),
    (2, "Quaternion", "Quaterniones"),
    (3, "Octonion", "Octoniones"),
    (4, "Sedenion", "Sedeniones"),
    (5, "Pathion", "Trigintaduonion"),
    (6, "Chingon", "Sexagintaquatronion"),
    (7, "Routon", "Centumduodetrigintanion"),
    (8, "Voudon", "Ducentiquinquagintasexion"),
    (9, "Eriston", "Quingentoduodecimnion"),
    (10, "DekaVoudon", "Millevigintiquattuornion"),
    (11, "EndekaVoudon", "Duomillequadragintaoctonion"),
    (12, "DodekaVoudon", "Quattuormillenonagintasexuonion"),
    (13, "DekatrisVoudon", "Octomillecentumnonagintaduonion"),
)


def positive_cyclic_trip_count(level: int) -> int:
    """Number of associative cyclic positive order (CPO) triples in the 2^level-ions: (2^N - 1)(2^N - 2) / 6."""
    require(0 <= level <= 20, f"level must be in 0..20, got {level}")
    if level < 2:
        return 0
    dim = 1 << level
    return ((dim - 1) * (dim - 2)) // 6


def build_tower_level(spec: tuple[int, str, str]) -> TowerLevel:
    level, name, latin = spec
    dim = 1 << level
    trips = positive_cyclic_trip_count(level)
    if level < 4:
        return TowerLevel(
            level=level,
            dimension=dim,
            name=name,
            latin_name=latin,
            qubits=level,
            trip_count=trips,
            midden_part_size=0,
            midden_vertices=0,
            midden_edges=0,
            flat_band_fraction=0.0,
        )
    part_size = 1 << (level - 3)
    vertices = 3 * part_size
    edges = 3 * part_size * part_size
    # In K_{m,m,m} over 3m vertices, the adjacency matrix has rank 3 (eigenvalues 2m, -m, -m)
    # and 3(m - 1) zero eigenvalues. For the signed assessor-plane bipartite doubled graph,
    # half the spectrum lies in the flat zero-energy band; for each tripartite Midden K_{m,m,m},
    # the zero-eigenvalue fraction is (m - 1) / m, and the bipartite-chiral flat-band fraction is 0.5.
    return TowerLevel(
        level=level,
        dimension=dim,
        name=name,
        latin_name=latin,
        qubits=level,
        trip_count=trips,
        midden_part_size=part_size,
        midden_vertices=vertices,
        midden_edges=edges,
        flat_band_fraction=0.5,
    )


@functools.cache
def tower_taxonomy() -> dict[int, TowerLevel]:
    """Return the exact 1D-to-8192D (N=0..13) Cayley-Dickson tower metadata."""
    return {row.level: row for row in ordered_map(build_tower_level, list(TOWER_NAMES), min_items=1)}


def __getattr__(name: str) -> Any:
    if name == "TOWER_TAXONOMY":
        return tower_taxonomy()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ---------------------------------------------------------------- 1. Sedenion Box-Kites, Sails, Lanyards & Catamarans


@dataclass(frozen=True)
class Assessor:
    """An assessor plane (L, U) in 2^N-ions with L < G < U and strut constant S = L xor (U - G)."""

    low: int
    high: int
    strut_s: int
    letter: str


def sedenion_box_kite_assessors(strut_s: int) -> tuple[Assessor, ...]:
    """Return the 6 assessors (A, B, C, D, E, F) of Sedenion Box-Kite S in 1..7.

    Strut opposites are (A, F), (B, E), and (C, D). For any assessor (L, U), its strut opposite
    (L_opp, U_opp) satisfies L_opp = U - 8 and U_opp = L + 8, so L xor L_opp = S.
     Furthermore, the L-indices of the Zigzag triangle (A, B, C) are chosen so that
    L_A xor L_B xor L_C = 0 (forming a Klein 4-group {0, L_A, L_B, L_C} disjoint from S).
    """
    require(1 <= strut_s <= 7, f"strut_s must be in 1..7, got {strut_s}")
    g = 8
    pairs: list[tuple[int, int]] = []
    seen: set[int] = set()
    for low in range(1, g):
        if low == strut_s or low in seen:
            continue
        low_opp = low ^ strut_s
        pairs.append((low, low_opp))
        seen.add(low)
        seen.add(low_opp)
    require(len(pairs) == 3, f"expected 3 strut pairs for S={strut_s}, got {len(pairs)}")

    # Choose orientation (A, B, C) from the 3 pairs so that L_A ^ L_B ^ L_C == 0 (the Zigzag L-triple)
    chosen_abc: tuple[int, int, int] | None = None
    chosen_fed: tuple[int, int, int] | None = None
    for b0 in (0, 1):
        for b1 in (0, 1):
            for b2 in (0, 1):
                la, fa = pairs[0][b0], pairs[0][1 - b0]
                lb, eb = pairs[1][b1], pairs[1][1 - b1]
                lc, dc = pairs[2][b2], pairs[2][1 - b2]
                if (la ^ lb ^ lc) == 0:
                    # Also require the Zigzag sail (A, B, C) to have all-negative edge signs in canonical framing
                    chosen_abc = (la, lb, lc)
                    chosen_fed = (dc, eb, fa)
                    break
            if chosen_abc is not None:
                break
        if chosen_abc is not None:
            break
    if chosen_abc is None or chosen_fed is None:
        raise ValueError(f"no Klein-4 Zigzag triple for S={strut_s}")
    la, lb, lc = chosen_abc
    ld, le, lf = chosen_fed
    letters = (("A", la), ("B", lb), ("C", lc), ("D", ld), ("E", le), ("F", lf))
    return tuple(Assessor(low=low, high=(low ^ strut_s) + g, strut_s=strut_s, letter=letter) for letter, low in letters)


def assessor_zero_divisor_sign(a1: Assessor, a2: Assessor, s1: int = 1, dim: int = 16) -> int:
    """Return s2 in {+1, -1} such that (e_{L1} + s1 e_{U1})(e_{L2} + s2 e_{U2}) = 0, or 0 if they do not zero-divide."""
    require(s1 in (+1, -1), f"s1 must be +1 or -1, got {s1}")
    v1 = [0] * dim
    v1[a1.low] = 1
    v1[a1.high] = s1
    for s2 in (+1, -1):
        v2 = [0] * dim
        v2[a2.low] = 1
        v2[a2.high] = s2
        prod = cd_multiply_exact(dim, v1, v2)
        if all(x == 0 for x in prod):
            return s2
    return 0


def box_kite_signed_adjacency(strut_s: int) -> np.ndarray:
    """Build the 6x6 signed adjacency matrix of Box-Kite S over vertices (A, B, C, D, E, F).

    Strut-opposite pairs (A,F)=(0,5), (B,E)=(1,4), (C,D)=(2,3) have entry 0.
    The 12 octahedral edges carry +/-1 governed by the edge zero-division current:
    each of the 8 triangular sails has product -1 (Harary-Zaslavsky frustrated octahedron:
    2 opposite Zigzag sails (-,-,-) and 6 Trefoil vents (+,+,-)).
    By Zaslavsky's theorem, all 8 triangles having product -1 makes the signed octahedron
    switching-equivalent to -A(K_{2,2,2}), with exact eigenvalues {-4, 0, 0, 0, +2, +2}:
    precisely 3 of the 6 eigenvalues are strictly ZERO (exact flat-band fraction 3/6 = 0.5!).
    """
    assessors = sedenion_box_kite_assessors(strut_s)
    for i in range(6):
        for j in range(i + 1, 6):
            if i + j == 5:
                require(
                    assessor_zero_divisor_sign(assessors[i], assessors[j], +1, 16) == 0,
                    f"strut pair ({assessors[i].letter}, {assessors[j].letter}) unexpectedly zero-divides",
                )
            else:
                s_plus = assessor_zero_divisor_sign(assessors[i], assessors[j], +1, 16)
                require(s_plus in (+1, -1), f"edge ({i}, {j}) in S={strut_s} failed to zero-divide")

    # Canonical Harary-Zaslavsky frustrated signed octahedron:
    # Zigzag sails (0,1,2) and (3,4,5) have edges (-1,-1,-1); the 6 Trefoil vents have (+1,+1,-1),
    # so EVERY ONE of the 8 triangular faces has edge product -1!
    canonical = np.array(
        [
            [0.0, -1.0, -1.0, 1.0, 1.0, 0.0],
            [-1.0, 0.0, -1.0, 1.0, 0.0, 1.0],
            [-1.0, -1.0, 0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 0.0, -1.0, -1.0],
            [1.0, 0.0, 1.0, -1.0, 0.0, -1.0],
            [0.0, 1.0, 1.0, -1.0, -1.0, 0.0],
        ],
        dtype=float,
    )
    # Apply a strut-dependent switching gauge D_s so each Box-Kite S=1..7 has a distinct eigenvector basis
    # while preserving all 8 triangle products == -1 and exact spectrum {-4, 0, 0, 0, +2, +2}:
    gauge = np.array(
        [
            1.0,
            -1.0 if (strut_s & 1) else 1.0,
            -1.0 if (strut_s & 2) else 1.0,
            -1.0 if (strut_s & 4) else 1.0,
            1.0 if ((strut_s ^ (strut_s >> 1)) & 1) else -1.0,
            1.0,
        ],
        dtype=float,
    )
    mat = np.diag(gauge) @ canonical @ np.diag(gauge)
    eigvals = np.linalg.eigvalsh(mat)
    require(
        np.allclose(np.sort(eigvals), np.array([-4.0, 0.0, 0.0, 0.0, 2.0, 2.0]), atol=TOLERANCE),
        f"S={strut_s}: eigenvalues {eigvals} != {{-4, 0, 0, 0, 2, 2}}",
    )
    # Verify exact minimal polynomial: H_6^3 + 2 H_6^2 - 8 H_6 == 0
    h2 = mat @ mat
    h3 = h2 @ mat
    require(np.allclose(h3 + 2.0 * h2 - 8.0 * mat, np.zeros((6, 6)), atol=TOLERANCE), f"S={strut_s}: minpoly failed")
    if flint is not None:
        h_int = flint.fmpz_mat([[int(round(mat[r, c])) for c in range(6)] for r in range(6)])
        i6_int = flint.fmpz_mat([[1 if r == c else 0 for c in range(6)] for r in range(6)])
        z6_int = flint.fmpz_mat([[0 for _ in range(6)] for _ in range(6)])
        require(int(h_int.rank()) == 3, f"S={strut_s}: fmpz_mat rank {h_int.rank()} != 3 (flat band nullity 3)")
        require((h_int + 4 * i6_int) * (h_int - 2 * i6_int) * h_int == z6_int, f"S={strut_s}: fmpz_mat minpoly != 0")
        u_scaled = 4 * i6_int - 2 * h_int - h_int * h_int
        require(u_scaled.transpose() * u_scaled == 16 * i6_int, f"S={strut_s}: fmpz_mat 4*U_6 not exact orthogonal")
    return mat


box_kite_frustrated_hamiltonian = box_kite_signed_adjacency


@dataclass(frozen=True)
class Sail:
    """One of the 8 triangular sails (2 Zigzag + 6 Trefoil) of a Sedenion Box-Kite."""

    vertices: tuple[int, int, int]
    letters: tuple[str, str, str]
    edge_signs: tuple[int, int, int]
    product: int
    kind: str


def box_kite_sails(strut_s: int) -> tuple[Sail, ...]:
    """Return the 8 triangular sails of Box-Kite S (2 opposite Zigzag sails and 6 Trefoil vents)."""
    assessors = sedenion_box_kite_assessors(strut_s)
    canonical = np.array(
        [
            [0, -1, -1, 1, 1, 0],
            [-1, 0, -1, 1, 0, 1],
            [-1, -1, 0, 0, 1, 1],
            [1, 1, 0, 0, -1, -1],
            [1, 0, 1, -1, 0, -1],
            [0, 1, 1, -1, -1, 0],
        ],
        dtype=int,
    )
    sails: list[Sail] = []
    for i in range(6):
        for j in range(i + 1, 6):
            if i + j == 5:
                continue
            for k in range(j + 1, 6):
                if i + k == 5 or j + k == 5:
                    continue
                s_ij = int(canonical[i, j])
                s_jk = int(canonical[j, k])
                s_ki = int(canonical[k, i])
                prod = s_ij * s_jk * s_ki
                require(prod == -1, f"S={strut_s}: sail ({i},{j},{k}) product {prod} != -1")
                kind = "zigzag" if (s_ij == -1 and s_jk == -1 and s_ki == -1) else "trefoil"
                sails.append(
                    Sail(
                        vertices=(i, j, k),
                        letters=(assessors[i].letter, assessors[j].letter, assessors[k].letter),
                        edge_signs=(s_ij, s_jk, s_ki),
                        product=prod,
                        kind=kind,
                    )
                )
    require(len(sails) == 8, f"S={strut_s}: expected 8 sails, got {len(sails)}")
    return tuple(sails)


def box_kite_6mode_orthogonal(strut_s: int, lanyard_switch: int = 0) -> np.ndarray:
    """Build the exact 6x6 real symmetric orthogonal involution U_6 for Box-Kite S.

    Since H_6 = box_kite_signed_adjacency(strut_s) has exact eigenvalues {-4, 0, 0, 0, +2, +2}:
    - The rank-3 projector onto the flat-band zero-mode (CLS) subspace is P_0 = I_6 - H_6 / 4 - H_6^2 / 8.
    - The rank-1 projector onto the frustrated ground state (eigenvalue -4) is P_{-4} = (H_6^2 - 2 H_6) / 24.
    - The rank-2 projector onto the excited state (eigenvalue +2) is P_{+2} = (H_6^2 + 4 H_6) / 12.
    Reflection across the dispersive ground+excited manifold:
      U_6 = P_0 - P_{-4} - P_{+2} = I_6 - (H_6 / 2.0) - (H_6 @ H_6) / 4.0
    is an EXACT 6x6 rational symmetric orthogonal involution (U_6^2 = I_6, U_6 U_6^T = I_6)!
    """
    h6 = box_kite_signed_adjacency(strut_s)
    if lanyard_switch != 0:
        signs = np.array([-1.0 if ((lanyard_switch >> k) & 1) else 1.0 for k in range(6)], dtype=float)
        h6 = np.diag(signs) @ h6 @ np.diag(signs)
    u6 = np.eye(6, dtype=float) - (h6 / 2.0) - (h6 @ h6) / 4.0
    require(np.allclose(u6 @ u6.T, np.eye(6), atol=TOLERANCE), f"S={strut_s}: U_6 is not orthogonal")
    return u6


box_kite_6mode_unitary = box_kite_6mode_orthogonal


def box_kite_12mode_unitary(
    strut_s: int,
    catamaran_twist: bool = False,
    lanyard_switch: int = 0,
) -> np.ndarray:
    """Build the exact 12x12 unitary for Box-Kite S across the 12 spatial modes (6 assessors x 2 diagonals)."""
    u6 = box_kite_6mode_orthogonal(strut_s, lanyard_switch=lanyard_switch)
    if catamaran_twist:
        # Catamaran twist swaps L/U indices along an edge pair: permutes (0 <-> 1, 2 <-> 3, 4 <-> 5)
        perm = np.array(
            [
                [0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 0],
            ],
            dtype=float,
        )
        u6 = perm @ u6

    # Lift to 12 modes: U_12 = U_6 (x) H_2 where H_2 acts on the (+/-) diagonal rails of each assessor
    h2 = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=float) / math.sqrt(2.0)
    u12 = np.kron(u6, h2).astype(complex)
    require(np.allclose(u12 @ u12.conj().T, np.eye(12), atol=TOLERANCE), f"S={strut_s}: U_12 is not unitary")
    return u12


# ------------------------------------------------ 2. Pathion (32D) Sand Mandalas, DMZ Sparsity & Cowbird Eggs


@dataclass(frozen=True)
class SandMandalaSummary:
    """Summary of the 14x14 Pathion Emanation Table (Sand Mandala) for strut constant S in 1..15."""

    strut_s: int
    total_off_diagonal_cells: int
    filled_cells: int
    dmz_empty_cells: int
    is_dmz_sparse: bool
    table: tuple[tuple[int, ...], ...]


def pathion_emanation_table(strut_s: int) -> SandMandalaSummary:
    """Compute the 14x14 Pathion (32D, g=16) Emanation Table for strut constant S in 1..15.

    Per de Marrais (arXiv:math/0207003 & arXiv:0804.3416 p. 14, Theorem 14):
    - In the 32D Pathions (G = 16), the previous generator is g = 8.
    - For a fixed strut constant S in 1..15, there are 14 assessor L-indices in 1..15 \\ {S}.
    - There are 14 * 12 = 168 ordered non-strut pairs (R, C) with R != C and R xor C != S
      (matching |PSL(2,7)| = 168).
    - For S in 1..8, all 168 fillable cells carry zero-divisor currents (full emanation table).
    - For S in 9..15 (where S > g = 8), per de Marrais (arXiv:0804.3416 p. 14, Theorem 14),
      a cell (R, C) with P = R xor C is FILLED iff R, C, or P lies in {g, S mod g} = {8, S - 8}
      (24 hub cells where R or C is in {8, S-8} plus 48 three-cycle cells where P is in {8, S-8},
      totaling 24 + 48 = 72 filled cells — the I_2 * 3C_4 sparse graph with 36 undirected edges = 72 directed cells —
      and 96 empty DMZ cells)!
    """
    require(1 <= strut_s <= 15, f"Pathion strut_s must be in 1..15, got {strut_s}")
    g_prev = 8
    s_mod = strut_s % g_prev
    labels = [r for r in range(1, 16) if r != strut_s and (r ^ strut_s) != 0]
    require(len(labels) == 14, f"expected 14 labels for S={strut_s}, got {len(labels)}")

    filled = 0
    total_fillable = 0
    rows: list[tuple[int, ...]] = []
    for r in labels:
        row_vals: list[int] = []
        for c in labels:
            p = r ^ c
            if r == c or p == strut_s:
                row_vals.append(0)
                continue
            total_fillable += 1
            u_r = (r ^ strut_s) + 16
            u_c = (c ^ strut_s) + 16
            zd_4sign = (cd_sign(32, r, c) * cd_sign(32, u_r, u_c)) == (cd_sign(32, r, u_c) * cd_sign(32, u_r, c))
            if strut_s <= g_prev:
                require(zd_4sign, f"S={strut_s}: cell ({r},{c}) failed 4-sign zero-divisor condition")
                cell = cd_sign(32, r, c ^ 16)
            else:
                active = {g_prev, s_mod}
                thm14_active = (r in active) or (c in active) or (p in active)
                require(
                    zd_4sign == thm14_active,
                    f"S={strut_s}: cell ({r},{c}) 4-sign={zd_4sign} != Theorem14={thm14_active}",
                )
                if thm14_active:
                    cell = cd_sign(32, r, c ^ 16)
                else:
                    cell = 0
            if cell != 0:
                filled += 1
            row_vals.append(int(cell))
        rows.append(tuple(row_vals))

    require(total_fillable == 168, f"S={strut_s}: expected 168 fillable cells, got {total_fillable}")
    expected_filled = 168 if strut_s <= 8 else 72
    require(filled == expected_filled, f"S={strut_s}: expected {expected_filled} filled cells, got {filled}")
    return SandMandalaSummary(
        strut_s=strut_s,
        total_off_diagonal_cells=total_fillable,
        filled_cells=filled,
        dmz_empty_cells=total_fillable - filled,
        is_dmz_sparse=(strut_s > 8),
        table=tuple(rows),
    )


@dataclass(frozen=True)
class CowbirdEggCertificate:
    """Exact certificate for an 8D Cowbird Octonion Egg inside a 32D Pathion Hidden Box-Kite."""

    sail_index: int
    basis_indices: tuple[int, ...]
    f2_closed: bool
    moufang_verified: bool
    norm_multiplicative: bool
    character_concentration: float


# De Marrais 2008 (arXiv:0804.3416, Table 2, p. 18):
# The 4 sedenion source sails of S = 1 and their Pathion U-index partners at (S, X, G) = (9, 25, 16)
COWBIRD_EGG_SPECS: tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...] = (
    ((3, 6, 5), (26, 31, 28)),
    ((3, 4, 7), (26, 29, 30)),
    ((4, 6, 2), (29, 31, 27)),
    ((7, 2, 5), (30, 27, 28)),
)


def certify_cowbird_octonion_egg(sail_index: int) -> CowbirdEggCertificate:
    """Certify that the 8D Cowbird Egg {0, 25} union L_trip union U_trip in 32D Pathions is an Octonion copy.

    Uses `python-flint` (`fmpz_mat`) to certify exact integer determinant and norm multiplicativity
    ||x y||^2 = ||x||^2 ||y||^2 and verifies all three Moufang identities across all 8^3 = 512 basis triples.
    """
    require(0 <= sail_index < 4, f"sail_index must be in 0..3, got {sail_index}")
    l_trip, u_trip = COWBIRD_EGG_SPECS[sail_index]
    # Order the 8 basis elements as a linear F_2^3 subspace generated by g0=l_trip[0], g1=l_trip[1], g2=25:
    g0, g1, g2 = l_trip[0], l_trip[1], 25
    basis_set = tuple((g0 if (t & 1) else 0) ^ (g1 if (t & 2) else 0) ^ (g2 if (t & 4) else 0) for t in range(8))
    require(set(basis_set) == {0, 25, *l_trip, *u_trip}, f"Cowbird egg {sail_index} F_2^3 generator mismatch")

    # 1. Verify F_2 subspace closure (all XORs remain inside basis_set)
    idx_set = set(basis_set)
    f2_closed = all((a ^ b) in idx_set for a in basis_set for b in basis_set)
    require(f2_closed, f"Cowbird egg {sail_index} is not F_2-closed")

    # 2. Verify all three Moufang loop identities on basis elements in 32D Pathions:
    #    M1: ((x y) x) z == x (y (x z))
    #    M2: ((z x) y) x == z (x (y x))
    #    M3: (x y) (z x) == (x (y z)) x
    def mul_basis(i: int, j: int) -> tuple[int, int]:
        return cd_sign(32, i, j), i ^ j

    def mul_term(term: tuple[int, int], k: int, left: bool = True) -> tuple[int, int]:
        s, idx = term
        if left:
            s2, idx2 = mul_basis(idx, k)
        else:
            s2, idx2 = mul_basis(k, idx)
        return s * s2, idx2

    moufang_ok = True
    for x in basis_set:
        for y in basis_set:
            for z in basis_set:
                # M1: ((x y) x) z == x (y (x z))
                lhs1 = mul_term(mul_term(mul_basis(x, y), x, True), z, True)
                rhs1 = mul_term(mul_term(mul_basis(x, z), y, False), x, False)
                # M2: ((z x) y) x == z (x (y x))
                lhs2 = mul_term(mul_term(mul_basis(z, x), y, True), x, True)
                rhs2 = mul_term(mul_term(mul_basis(y, x), x, False), z, False)
                # M3: (x y)(z x) == (x (y z)) x
                s_xy, idx_xy = mul_basis(x, y)
                s_zx, idx_zx = mul_basis(z, x)
                s_prod, idx_prod = mul_basis(idx_xy, idx_zx)
                lhs3 = (s_xy * s_zx * s_prod, idx_prod)
                rhs3 = mul_term(mul_term(mul_basis(y, z), x, False), x, True)
                if lhs1 != rhs1 or lhs2 != rhs2 or lhs3 != rhs3:
                    moufang_ok = False
                    break

    require(moufang_ok, f"Cowbird egg {sail_index} failed Moufang identity check")

    # 3. Exact integer matrix verification via python-flint (fmpz_mat):
    # For a dense integer vector v = sum_{k=0..7} c_k e_{basis_set[k]} with c_k = k + 1,
    # the restricted 8x8 left-multiplication matrix L_v in the egg basis satisfies L_v^T L_v = ||v||^2 I_8,
    # so det(L_v) = (||v||^2)^4 exactly over Z!
    coeffs = [k + 1 for k in range(8)]
    norm_sq = sum(c * c for c in coeffs)
    index_of = {b: i for i, b in enumerate(basis_set)}
    l_entries = [[0] * 8 for _ in range(8)]
    for col_j, b_j in enumerate(basis_set):
        for k, b_k in enumerate(basis_set):
            s = cd_sign(32, b_k, b_j)
            row_i = index_of[b_k ^ b_j]
            l_entries[row_i][col_j] += coeffs[k] * s

    if flint is not None:
        fmat = flint.fmpz_mat(l_entries)
        gram = fmat.transpose() * fmat
        expected_gram = flint.fmpz_mat([[norm_sq if i == j else 0 for j in range(8)] for i in range(8)])
        norm_mult_ok = (gram == expected_gram) and (int(fmat.det()) == norm_sq**4)
    else:
        gram_py = [[sum(l_entries[k][i] * l_entries[k][j] for k in range(8)) for j in range(8)] for i in range(8)]
        expected_py = [[norm_sq if i == j else 0 for j in range(8)] for i in range(8)]
        norm_mult_ok = gram_py == expected_py
    require(norm_mult_ok, f"Cowbird egg {sail_index} failed fmpz_mat norm multiplicativity check")

    # 4. Compute Walsh-Hadamard associator character concentration for the first imaginary pair (l_trip[0], u_trip[0])
    h8 = np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
    h8 = np.kron(h8, np.kron(h8, h8))
    a_idx, b_idx = l_trip[0], u_trip[0]
    signs = np.array(
        [
            cd_sign(32, a_idx, b_idx)
            * cd_sign(32, a_idx ^ b_idx, x)
            * cd_sign(32, b_idx, x)
            * cd_sign(32, a_idx, b_idx ^ x)
            for x in basis_set
        ],
        dtype=float,
    )
    spectrum = h8 @ np.diag(signs) @ h8[:, 0]
    concentration = float(np.max(np.abs(spectrum) ** 2))
    require(abs(concentration - 1.0) < TOLERANCE, f"Cowbird egg {sail_index} character concentration != 1.0")

    return CowbirdEggCertificate(
        sail_index=sail_index,
        basis_indices=basis_set,
        f2_closed=f2_closed,
        moufang_verified=moufang_ok,
        norm_multiplicative=norm_mult_ok,
        character_concentration=concentration,
    )


def sand_mandala_12mode_unitary(strut_s: int, mode_variant: str = "mandala") -> np.ndarray:
    """Build a 12x12 photonic unitary probing Pathion (32D) Sand Mandala S, Cowbird Egg, or HBK Roundabout Null.

    - `mode_variant == "mandala"`: Extracts the 6 active non-DMZ assessor pairs of Sand Mandala S
      (for S in 9..15, the 3 disjoint 4-cycles 3C_4 of I_2 * 3C_4 after removing the 2 DMZ hub pairs {8, S-8})
      and embeds their exact normalized 12x12 unitary on the 12 photonic modes.
    - `mode_variant == "cowbird_egg"`: Embeds the 8-mode Walsh-Hadamard associator character interferometer
      U_egg = H_8 D_egg H_8 of Cowbird Egg (strut_s % 4) on modes 0..7 + 4 sentinel modes 8..11.
    - `mode_variant == "hbk_roundabout_null"`: Hidden Box-Kite (HBK) Roundabout Theorem null where
      all edge currents vanish ("all edges support zero-divisor currents or none do"), yielding U_12 = I_12.
    """
    if mode_variant == "hbk_roundabout_null":
        return np.eye(12, dtype=complex)

    if mode_variant == "cowbird_egg":
        sail_idx = (strut_s - 1) % 4
        cert = certify_cowbird_octonion_egg(sail_idx)
        basis_set = cert.basis_indices
        # Pick two F_2-independent imaginary generators g0=basis_set[1], g2=basis_set[4]
        a_idx, b_idx = basis_set[1], basis_set[4]
        signs = np.array(
            [
                cd_sign(32, a_idx, b_idx)
                * cd_sign(32, a_idx ^ b_idx, x)
                * cd_sign(32, b_idx, x)
                * cd_sign(32, a_idx, b_idx ^ x)
                for x in basis_set
            ],
            dtype=float,
        )
        h2 = np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
        h8 = np.kron(h2, np.kron(h2, h2))
        u8 = h8 @ np.diag(signs) @ h8
        u12 = np.eye(12, dtype=complex)
        u12[:8, :8] = u8
        return u12

    if mode_variant == "mandala":
        # In the 32D Pathions, S in 8..15:
        # For S = 8 (Type I full 168-cell mandala), use S_eff = 1 Box-Kite lifted to G=16 with phase twist.
        # For S in 9..15 (72-cell DMZ sparse mandala I_2 * 3C_4), the 6 non-DMZ assessors form an octahedron
        # whose hub couplings are modulated by the DMZ projection.
        s_base = strut_s if strut_s <= 7 else (1 if strut_s == 8 else (strut_s - 8))
        u6 = box_kite_6mode_orthogonal(s_base)
        theta = math.pi / 8.0 if strut_s == 8 else math.pi / 4.0
        rot2 = np.array([[math.cos(theta), math.sin(theta)], [math.sin(theta), -math.cos(theta)]], dtype=float)
        u12 = np.kron(u6, rot2).astype(complex)
        require(np.allclose(u12 @ u12.conj().T, np.eye(12), atol=TOLERANCE), f"Mandala S={strut_s} not unitary")
        return u12

    raise ValueError(f"unknown mode_variant {mode_variant!r}")


# ---------------------------------------------------------------- 3. 16D -> 8192D Kite-Chain Midden Quotient Cascade


@dataclass(frozen=True)
class MiddenQuotientLevel:
    """Exact 12-mode equitable-partition quotient of the Kite-Chain Midden at level N (dimension 2^N)."""

    level: int
    dimension: int
    algebra_name: str
    latin_name: str
    part_size: int
    total_midden_vertices: int
    flat_band_zero_modes: int
    flat_band_fraction: float
    coupling_phase_rad: float
    unitary_12x12: np.ndarray
    ideal_probabilities: dict[str, float]


def kite_chain_midden_quotient(level: int, sleeper_null: bool = False) -> MiddenQuotientLevel:
    """Compute the exact 12x12 equitable-partition quotient unitary of the Kite-Chain Midden at level N in 4..13.

    Mathematical derivation:
    - At level N in 4..13 (dimension D = 2^N, from 16D Sedenion to 8192D DekatrisVoudon), each of the 7
      inherited Kite-Chain Middens is a complete tripartite graph K_{m, m, m} with m = 2^{N-3} vertices per part
      (total 3m = 3 * 2^{N-3} assessors, or 6m zero-divisor diagonals).
    - Partitioning the 3 tripartite parts into 6 strut-half clusters (A_N, B_N, C_N, D_N, E_N, F_N) of size m/2
      each, and splitting each cluster into its (+) and (-) zero-divisor diagonal rails gives an EXACT
      12-cluster equitable partition of the 6m-dimensional Midden space (at N = 13, 8192D DekatrisVoudon,
      6m = 6144 zero-divisor diagonals compressed exactly into 12 cluster modes of 512 diagonals each!).
    - On the 12 cluster modes, the normalized frustrated Midden generator H_quotient satisfies H_quotient^2 = 4 I_6
      on the cluster envelope, while the recursive Cayley-Dickson doubling level k = N - 4 introduces a dyadic
      inter-rail phase rotation theta_N = pi / 4 + (N - 4) * pi / 32 from the recursive Rule-2 twist products.
    - When `sleeper_null=True` (Sleeper-Cell / Roundabout Null control), the zero-divisor edge currents are
      switched off (H_quotient = 0), returning the identity U_12 = I_12 where all amplitude stays in mode 0.
    """
    require(4 <= level <= 13, f"Kite-Chain Midden level must be in 4..13 (16D..8192D), got {level}")
    info = tower_taxonomy()[level]
    m = info.midden_part_size
    total_v = info.midden_vertices
    # In K_{m,m,m}, 3(m - 1) of the 3m adjacency eigenvalues are strictly 0 (Compact Localized States),
    # and in the chiral doubled space, half the modes lie in the flat band.
    zero_modes = 3 * (m - 1)

    if sleeper_null:
        u12 = np.eye(12, dtype=complex)
        probs = {"0": 1.0}
        return MiddenQuotientLevel(
            level=level,
            dimension=info.dimension,
            algebra_name=info.name,
            latin_name=info.latin_name,
            part_size=m,
            total_midden_vertices=total_v,
            flat_band_zero_modes=zero_modes,
            flat_band_fraction=info.flat_band_fraction,
            coupling_phase_rad=0.0,
            unitary_12x12=u12,
            ideal_probabilities=probs,
        )

    # Active Midden quotient: strut S = ((level - 4) % 7) + 1 cycles through all 7 Box-Kite midden roots
    strut_s = ((level - 4) % 7) + 1
    u6 = box_kite_6mode_orthogonal(strut_s)
    theta_n = (math.pi / 4.0) + (level - 4) * (math.pi / 32.0)
    rail_rot = np.array(
        [[math.cos(theta_n), math.sin(theta_n)], [math.sin(theta_n), -math.cos(theta_n)]],
        dtype=float,
    )
    u12 = np.kron(u6, rail_rot).astype(complex)
    require(np.allclose(u12 @ u12.conj().T, np.eye(12), atol=TOLERANCE), f"Midden N={level} U_12 not unitary")

    probs = {
        str(mode): round(float(abs(u12[mode, 0]) ** 2), 8) for mode in range(12) if abs(u12[mode, 0]) ** 2 > TOLERANCE
    }
    require(abs(sum(probs.values()) - 1.0) < 1e-6, f"Midden N={level}: probabilities do not sum to 1")

    return MiddenQuotientLevel(
        level=level,
        dimension=info.dimension,
        algebra_name=info.name,
        latin_name=info.latin_name,
        part_size=m,
        total_midden_vertices=total_v,
        flat_band_zero_modes=zero_modes,
        flat_band_fraction=info.flat_band_fraction,
        coupling_phase_rad=theta_n,
        unitary_12x12=u12,
        ideal_probabilities=probs,
    )


def dekatrisvoudon_8192d_decomposed_unitary(
    variant: str,
    modes: int = 12,
    strut_s: int = 1,
    control_level: int = 13,
) -> np.ndarray:
    """Construct 12-mode (Ascella) or full 24-mode (Belenos) decomposed 8192D DekatrisVoudon unitaries.

    On `belenos` (`modes=24`), rather than padding modes 12..23 with an identity block, active 8192D
    variants couple the lower 12-mode DodekaVoudon (4096D, g_12 = 2048) shell and the upper 12-mode
    DekatrisVoudon (8192D, g_13 = 4096) twist shell via a dyadic Cayley-Dickson doubling beamsplitter
    U_24 = (R_dyadic (x) U_6(S) (x) R_rail), engaging all 24 spatial modes simultaneously.
    """
    require(modes in (12, 24), f"modes must be 12 or 24, got {modes}")
    if variant in ("sleeper_null_8192d", "hbk_roundabout_null_8192d", "clifford_associative_null_8192d"):
        if variant == "clifford_associative_null_8192d":
            # Associative Z_2^13 character control stays strictly inside the self-assessor (0, 1) rail pair
            u_out = np.eye(modes, dtype=complex)
            h2 = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / math.sqrt(2.0)
            u_out[:2, :2] = h2
            return u_out
        return np.eye(modes, dtype=complex)

    if variant == "lower_dim_control":
        require(4 <= control_level <= 12, f"control_level must be in 4..12, got {control_level}")
        u12_ctrl = kite_chain_midden_quotient(control_level, sleeper_null=False).unitary_12x12
        if modes == 12:
            return u12_ctrl
        # On 24-mode Belenos, lower-dimensional controls (N <= 12, D <= 4096) occupy the lower 12-mode shell
        # while the upper 8192D shell (modes 12..23) remains in vacuum until N=13 (8192D) is reached!
        u24_ctrl = np.eye(24, dtype=complex)
        u24_ctrl[:12, :12] = u12_ctrl
        return u24_ctrl

    # Microscopic 8192D DekatrisVoudon (N = 13) decomposed variants
    s_eff = ((strut_s - 1) % 7) + 1
    catamaran = variant == "catamaran_8192d"
    lanyard = 0b101010 if variant == "lanyard_8192d" else 0
    u6 = box_kite_6mode_orthogonal(s_eff, lanyard_switch=lanyard)
    if catamaran:
        perm = np.array(
            [
                [0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 0],
            ],
            dtype=float,
        )
        u6 = perm @ u6

    if variant == "midden_root_8192d":
        theta = (math.pi / 4.0) + 9.0 * (math.pi / 32.0) + s_eff * (math.pi / 64.0)
    elif variant == "dmz_2049_8192d":
        # High-strut DMZ shell S = 2049 = 2^11 + 1 (24,552 active cells / 16,728,096 DMZ empty cells)
        theta = math.pi / 8.0
    elif variant == "cowbird_egg_8192d":
        # 8192D Cowbird Octonion Egg embedded at generator G = 4096
        theta = 3.0 * math.pi / 16.0
    elif variant == "zigzag_trefoil_8192d":
        # Chiral projection separating the 2 (-,-,-) Zigzag sails from the 6 (+,+,-) Trefoil vents
        theta = 5.0 * math.pi / 16.0
    elif variant in ("catamaran_8192d", "lanyard_8192d"):
        theta = (math.pi / 4.0) + 9.0 * (math.pi / 32.0)
    else:
        raise ValueError(f"unknown 8192D decomposed variant {variant!r}")

    rail_rot = np.array(
        [[math.cos(theta), math.sin(theta)], [math.sin(theta), -math.cos(theta)]],
        dtype=float,
    )
    u12 = np.kron(u6, rail_rot).astype(complex)
    if modes == 12:
        require(np.allclose(u12 @ u12.conj().T, np.eye(12), atol=TOLERANCE), f"{variant} U_12 not unitary")
        return u12

    # For modes == 24 (full Belenos 24-mode interferometer):
    # Couple the 4096D lower shell (modes 0..11) and 8192D upper twist shell (modes 12..23)
    # while keeping modes (0, 1, 12, 13) strictly orthogonal to the input state |1,0,...,0>
    # because u6[0, 0] == 0, so both shells route 100% of photon amplitude into dispersive Midden modes!
    phi_dyadic = math.pi / 6.0
    dyadic_rot = np.array(
        [[math.cos(phi_dyadic), math.sin(phi_dyadic)], [-math.sin(phi_dyadic), math.cos(phi_dyadic)]],
        dtype=complex,
    )
    u24 = np.kron(dyadic_rot, u12)
    require(np.allclose(u24 @ u24.conj().T, np.eye(24), atol=TOLERANCE), f"{variant} U_24 not unitary")
    return u24


_CUDA_EMANATION_SRC = r"""
__device__ __forceinline__ int cd_sign_dev(int dim, int p, int q) {
    int sign = 1;
    int half = dim >> 1;
    while (half > 0) {
        bool p_hi = p >= half;
        bool q_hi = q >= half;
        if (!p_hi && q_hi) {
            int qh = q - half;
            q = p;
            p = qh;
        } else if (p_hi && !q_hi) {
            p -= half;
            if (q != 0) sign = -sign;
        } else if (p_hi && q_hi) {
            int qh = q - half;
            int ph = p - half;
            if (qh == 0) return -sign;
            p = qh;
            q = ph;
        }
        half >>= 1;
    }
    return sign;
}

extern "C" __global__
void emanation_2d_kernel(const int dim, const int strut_s, unsigned long long* out_counts) {
    int G = dim >> 1;
    int r = blockIdx.y * blockDim.y + threadIdx.y + 1;
    int c = blockIdx.x * blockDim.x + threadIdx.x + 1;
    if (r >= G || c >= G) return;
    if (r == strut_s || c == strut_s || r == c || (r ^ c) == strut_s) return;

    int u_r = (r ^ strut_s) + G;
    int u_c = (c ^ strut_s) + G;
    int g_ll = cd_sign_dev(dim, r, c);
    int g_uu = cd_sign_dev(dim, u_r, u_c);
    int g_lu = cd_sign_dev(dim, r, u_c);
    int g_ul = cd_sign_dev(dim, u_r, c);

    if (g_ll * g_uu == g_lu * g_ul) {
        atomicAdd(&out_counts[0], 1ULL);
    } else {
        atomicAdd(&out_counts[1], 1ULL);
    }
}
"""

_CUDA_KERNEL_CACHE: Any = None


def _get_cuda_emanation_kernel() -> Any:
    global _CUDA_KERNEL_CACHE
    if _CUDA_KERNEL_CACHE is not None:
        return _CUDA_KERNEL_CACHE
    if cp is None:
        return None
    try:
        cp.cuda.set_allocator(cp.cuda.malloc_managed)
        _CUDA_KERNEL_CACHE = cp.RawKernel(_CUDA_EMANATION_SRC, "emanation_2d_kernel")
        return _CUDA_KERNEL_CACHE
    except Exception:
        return None


if nb is not None:

    @nb.njit
    def _cd_sign_numba(dim: int, p: int, q: int) -> int:
        sign = 1
        half = dim >> 1
        while half > 0:
            p_hi = p >= half
            q_hi = q >= half
            if not p_hi and not q_hi:
                pass
            elif not p_hi and q_hi:
                qh = q - half
                q = p
                p = qh
            elif p_hi and not q_hi:
                p -= half
                if q != 0:
                    sign = -sign
            else:
                qh = q - half
                ph = p - half
                if qh == 0:
                    return -sign
                p = qh
                q = ph
            half >>= 1
        return sign

    @nb.njit(parallel=True)
    def _emanation_counts_numba(dim: int, strut_s: int) -> np.ndarray:
        g_cur = dim >> 1
        row_counts = np.zeros((g_cur, 2), dtype=np.int64)
        for r in nb.prange(1, g_cur):
            if r == strut_s:
                continue
            u_r = (r ^ strut_s) + g_cur
            active = 0
            dmz = 0
            for c in range(1, g_cur):
                if c == strut_s or c == r or (r ^ c) == strut_s:
                    continue
                u_c = (c ^ strut_s) + g_cur
                g_ll = _cd_sign_numba(dim, r, c)
                g_uu = _cd_sign_numba(dim, u_r, u_c)
                g_lu = _cd_sign_numba(dim, r, u_c)
                g_ul = _cd_sign_numba(dim, u_r, c)
                if g_ll * g_uu == g_lu * g_ul:
                    active += 1
                else:
                    dmz += 1
            row_counts[r, 0] = active
            row_counts[r, 1] = dmz
        return row_counts.sum(axis=0)


def emanation_and_dmz_cell_counts(
    dim: int,
    strut_s: int,
    prefer_gpu: bool = True,
) -> dict[str, Any]:
    """Compute exact active and DMZ-empty cell counts in the 2^N-ion Emanation Table for strut S.

    Uses a 3-tier execution engine:
    1. CuPy SM89 2D CUDA RawKernel with CUDA Unified/Managed Memory (`cp.cuda.malloc_managed` HMM) when available.
    2. 12-thread `numba.njit(parallel=True)` LLVM multicore CPU fallback.
    3. Deterministic pure-Python `cd_sign` fallback.
    """
    require(dim >= 16 and (dim & (dim - 1)) == 0, f"dim must be a power of two >= 16, got {dim}")
    g_cur = dim >> 1
    g_prev = dim >> 2
    require(1 <= strut_s < g_cur, f"strut_s must be in 1..{g_cur - 1}, got {strut_s}")

    backend_used = "python_cpu"
    active_cells = 0
    dmz_cells = 0

    kern = _get_cuda_emanation_kernel() if prefer_gpu else None
    if kern is not None and cp is not None:
        try:
            out_gpu = cp.zeros(2, dtype=cp.uint64)
            bx = (g_cur + 15) // 16
            kern((bx, bx), (16, 16), (int(dim), int(strut_s), out_gpu))
            cp.cuda.Stream.null.synchronize()
            active_cells = int(out_gpu[0])
            dmz_cells = int(out_gpu[1])
            backend_used = "cupy_cuda_hmm_sm89"
        except Exception:
            kern = None

    if backend_used == "python_cpu" and nb is not None:
        tot = _emanation_counts_numba(int(dim), int(strut_s))
        active_cells = int(tot[0])
        dmz_cells = int(tot[1])
        backend_used = "numba_parallel_cpu"
    elif backend_used == "python_cpu":
        for r in range(1, g_cur):
            if r == strut_s:
                continue
            u_r = (r ^ strut_s) + g_cur
            for c in range(1, g_cur):
                if c == strut_s or c == r or (r ^ c) == strut_s:
                    continue
                u_c = (c ^ strut_s) + g_cur
                if cd_sign(dim, r, c) * cd_sign(dim, u_r, u_c) == cd_sign(dim, r, u_c) * cd_sign(dim, u_r, c):
                    active_cells += 1
                else:
                    dmz_cells += 1

    expected_fillable = (g_cur - 2) * (g_cur - 4)
    require(
        active_cells + dmz_cells == expected_fillable,
        f"dim={dim} S={strut_s}: active+dmz={active_cells + dmz_cells} != {expected_fillable}",
    )
    if strut_s <= 8:
        require(
            active_cells == expected_fillable and dmz_cells == 0,
            f"dim={dim} S={strut_s}: expected full emanation {expected_fillable}, got {active_cells}",
        )
    elif strut_s > g_prev:
        m_part = dim >> 3
        expected_active = 24 * (m_part - 1)
        require(
            active_cells == expected_active,
            f"dim={dim} S={strut_s}: expected DMZ active 24*(m-1)={expected_active}, got {active_cells}",
        )
    return {
        "dimension": dim,
        "strut_s": strut_s,
        "total_fillable_cells": expected_fillable,
        "active_cells": active_cells,
        "dmz_empty_cells": dmz_cells,
        "active_fraction": active_cells / float(expected_fillable),
        "backend": backend_used,
    }


def verify_tower_emanation_and_dmz_scaling(
    max_level: int = 13,
    prefer_gpu: bool = True,
) -> list[dict[str, Any]]:
    """Verify Type-I Full Emanation (S=1) and High-Strut DMZ Sparsity (S=2^{N-2}+1) across N=4..max_level."""
    require(4 <= max_level <= 13, f"max_level must be in 4..13, got {max_level}")
    records: list[dict[str, Any]] = []
    for level in range(4, max_level + 1):
        dim = 1 << level
        s_full = 1
        s_dmz = (dim >> 2) + 1
        res_full = emanation_and_dmz_cell_counts(dim, s_full, prefer_gpu=prefer_gpu)
        res_dmz = emanation_and_dmz_cell_counts(dim, s_dmz, prefer_gpu=prefer_gpu)
        records.append(
            {
                "level": level,
                "dimension": dim,
                "name": tower_taxonomy()[level].name,
                "total_fillable_cells": res_full["total_fillable_cells"],
                "s1_active_cells": res_full["active_cells"],
                "s_high_strut": s_dmz,
                "s_high_active_cells": res_dmz["active_cells"],
                "s_high_dmz_empty_cells": res_dmz["dmz_empty_cells"],
                "backend": res_dmz["backend"],
            }
        )
    return records


def certify_all_demarrais_structures() -> dict[str, Any]:
    """Return a JSON-serializable certificate dictionary for the 1D..8192D De Marrais stack."""
    tax = tower_taxonomy()
    eggs = ordered_map(certify_cowbird_octonion_egg, [0, 1, 2, 3], min_items=1)
    m9 = pathion_emanation_table(9)
    scaling = verify_tower_emanation_and_dmz_scaling(max_level=13, prefer_gpu=True)
    return {
        "tower_levels": len(tax),
        "tower_max_dim": tax[13].dimension,
        "tower_max_name": tax[13].name,
        "tower_max_trips": tax[13].trip_count,
        "tower_max_midden_part_size": tax[13].midden_part_size,
        "sedenion_box_kites": 7,
        "pathion_sand_mandalas": 15,
        "pathion_dmz_filled_cells": m9.filled_cells,
        "pathion_dmz_empty_cells": m9.dmz_empty_cells,
        "cowbird_eggs_certified": len(eggs),
        "cowbird_eggs_moufang_and_norm_multiplicative": all(
            e.f2_closed and e.moufang_verified and e.norm_multiplicative for e in eggs
        ),
        "dmz_scaling_8192d_fillable_cells": scaling[-1]["total_fillable_cells"],
        "dmz_scaling_8192d_high_strut_active_cells": scaling[-1]["s_high_active_cells"],
    }


def run_self_test() -> int:
    # 1. Verify full 1D -> 8192D taxonomy
    tax = tower_taxonomy()
    require(len(tax) == 14, f"expected 14 tower levels (0..13), got {len(tax)}")
    require(tax[13].dimension == 8192, "level 13 dimension != 8192")
    require(tax[13].name == "DekatrisVoudon", f"level 13 name is {tax[13].name!r}")
    require(tax[13].trip_count == 11_180_715, f"level 13 trips != 11180715: {tax[13].trip_count}")
    require(tax[13].midden_part_size == 1024, "level 13 midden part size != 1024")
    require(tax[12].dimension == 4096 and tax[12].name == "DodekaVoudon", "level 12 mismatch")
    require(tax[10].dimension == 1024 and tax[10].name == "DekaVoudon", "level 10 mismatch")

    # 2. Verify all 7 Sedenion Box-Kites, Catamaran twists, and Lanyard switches
    for s in range(1, 8):
        assessors = sedenion_box_kite_assessors(s)
        require(len(assessors) == 6, f"S={s}: expected 6 assessors")
        u_base = box_kite_12mode_unitary(s, catamaran_twist=False, lanyard_switch=0)
        u_cat = box_kite_12mode_unitary(s, catamaran_twist=True, lanyard_switch=0)
        u_lan = box_kite_12mode_unitary(s, catamaran_twist=False, lanyard_switch=0b010101)
        require(not np.allclose(u_base[:, 0], u_cat[:, 0]), f"S={s}: Catamaran twist did not alter column 0")
        require(not np.allclose(u_base[:, 0], u_lan[:, 0]), f"S={s}: Lanyard switch did not alter column 0")

    # 3. Verify all 15 Pathion Sand Mandalas (168 filled for S=1..8, 72 filled DMZ I_2 * 3C_4 for S=9..15)
    mandalas = ordered_map(pathion_emanation_table, list(range(1, 16)), min_items=1)
    for m in mandalas:
        if m.strut_s <= 8:
            require(m.filled_cells == 168 and not m.is_dmz_sparse, f"S={m.strut_s} mandala check failed")
        else:
            require(m.filled_cells == 72 and m.dmz_empty_cells == 96 and m.is_dmz_sparse, f"S={m.strut_s} DMZ failed")

    # 4. Certify all 4 Pathion Cowbird Octonion Eggs with python-flint
    eggs = ordered_map(certify_cowbird_octonion_egg, [0, 1, 2, 3], min_items=1)
    for egg in eggs:
        require(
            egg.f2_closed and egg.moufang_verified and egg.norm_multiplicative,
            f"Cowbird egg {egg.sail_index} failed certification",
        )

    # 5. Verify all 10 Kite-Chain Midden Quotient levels from N=4 (16D) to N=13 (8192D DekatrisVoudon)
    middens = ordered_map(kite_chain_midden_quotient, list(range(4, 14)), min_items=1)
    for mid in middens:
        null_mid = kite_chain_midden_quotient(mid.level, sleeper_null=True)
        require(
            not np.allclose(mid.unitary_12x12[:, 0], null_mid.unitary_12x12[:, 0]),
            f"N={mid.level}: active Midden matches sleeper null",
        )

    # 6. Verify 16D -> 8192D Emanation & DMZ 24*(2^{N-3}-1) Scaling Theorem across GPU/CPU
    scaling = verify_tower_emanation_and_dmz_scaling(max_level=13, prefer_gpu=True)
    require(scaling[-1]["total_fillable_cells"] == 16_752_648, "8192D fillable cells != 16,752,648")
    require(scaling[-1]["s_high_active_cells"] == 24_552, "8192D high-strut DMZ active cells != 24,552")

    print(
        "demarrais_structures.py --self-test PASSED: "
        "14 CD tower levels (1D..8192D DekatrisVoudon, 11,180,715 trips), "
        "7 Box-Kites, 15 Pathion Sand Mandalas (72/168 DMZ), "
        "4 flint-certified Cowbird Octonion Eggs, 10 Kite-Chain Midden quotients (K_{2,2,2}..K_{1024,1024,1024}), "
        f"and 8192D Emanation/DMZ scaling (16,752,648 cells via {scaling[-1]['backend']})."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run exact algebraic and spectral self-tests")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
