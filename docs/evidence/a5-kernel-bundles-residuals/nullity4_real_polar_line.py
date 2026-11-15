"""Real points of V(G) minus V(Q): the orbit rank 13 locus and the fiber of the real Gauss map over the polar line.

z = (u; mu; v) in C^15 is a real point when w = conjugate(z) (A5-430). Its kernel plane is P = K(z) n conjugate(z)-perp
with K(z) = ker M(z), and the fiber is L = L_z x conjugate(L_z), L_z = {x : M(x) P = 0, x orthogonal to conjugate(P)}.
By A5-535, dim L > 2 forces P = l_z, the polar line (see "nullity4_polar_line_module.py"), and then L_z is the part of
C(l_z) = {x : M(x) l_z = 0} that is Hermitian-orthogonal to l_z, so dim L = 2 dim L_z.

1. The orbit rank (A5-539). The base action of the 18-dimensional kernel symmetry algebra on the doubly pure y is
   the span of the fourteen derivations of the octonions D (acting by one real matrix on u, on v and on Re and Im of
   each, zero on mu), the phase J = L_(e_16), which multiplies z by i, and the scaling. The tangent rank of the
   orbit at z is 16 minus the dimension of the stabilizer of z in that span. A stabilizer element (D, c) with c a
   complex scalar satisfies D u = -c u and D v = -c v. D is real and skew, so u^T D u = 0 and c u.u = 0, c v.v = 0
   and 2 c u.v = 0. At a point with Delta = (u.u)(v.v) - (u.v)^2 nonzero the Gram matrix is nonzero, so c = 0 and D
   fixes u and v, which is D fixing the real span W of Re u, Im u, Re v, Im v pointwise. The compact G_2 is
   transitive on orthonormal pairs of R^7 with stabilizer SU(2) (the kernel-bundles README, "The connected compact
   stabilizer on N_+ and N_-"; the complex statement is A5-530), whose Lie algebra is spanned by D_1, D_2, D_3 of
   the polar module with D_j D_k = -D_k D_j and D_j^2 = -1 on the four coordinates complementary to span(e_1, e_2,
   e_1 e_2). A real vector c there has |(sum x_k D_k) c|^2 = (sum x_k^2) |c|^2, so an element of the stabilizer of a
   pair that fixes a vector with a nonzero complementary part is zero. Hence the stabilizer of W has dimension 3 if
   W lies in the imaginary part of one quaternion subalgebra and 0 otherwise (dim W is at least 2 because Delta is
   nonzero), and the orbit rank is 13 or 16 at every point of C^15 with Delta nonzero, with no rank 14 or 15. On
   V(G) minus V(Q) and on V(Q) minus V(G), Delta is nonzero (A5-530). Rank 13 is the quaternion position, with W of
   dimension 2 or 3 and closed under the cross product.
2. The fiber (A5-538), split by mu = z_8 at the normal form of A5-530. G_2(C), the 120 degree rotation of the (u_j, v_j)
   planes and the scaling carry a point of the stratum to the normal form; they act by orthogonal matrices M(g t) = g
   M(t) g^T, so l_z, C(l_z) and the kernel move with z. The rotation is unitary and G_2(C) is not, so the statements
   below concern subspaces that the group preserves.
   a. Nullity (argument; the identification of the real kernel vectors with algebra elements is checked at the 66
      fixtures). For a nonzero p with conjugate(p).p nonzero, the bordered matrix A(p, conjugate(p)) has kernel
      {(0, x) : M(p) x = 0, conjugate(p).x = 0}, because conjugate(p) is outside the image of M(p) (its pairing with
      p in the kernel is nonzero), so the real nullity of left multiplication by p is 2 (nullity M(p) - 1). On the polar
      line M has rank 8 (mu nonzero) and 6 (mu = 0), so the real nullity is 12 and 16. The retained exact nullities of
      the real kernel vectors equal 2 (plane nullity - 1) at all 66 fixtures. dim L = 6 forces P = l_z and mu nonzero,
      dim L = 12 forces mu = 0, because dim C(l_z) is 3 and 6 and L_z lies in C(l_z). In
      quaternion position A5-536 gives P = l_z and dim L at least 6, so dim L = 6 at mu nonzero and 12 at mu = 0 (by b):
      A5-539's clause "dim L of 6 or 12" holds there.
   b. mu = 0. At the four lines s = +-i v_1, sigma = +-1 (eps = -sigma sign), the polar line lies in
      E_eps = {(a; 0; eps i a)} and C(l_z) lies in C z_0 + E_(-eps) with zero e_8 component, exact over Q(i) at
      v_1 = 1 and 2. p_sigma, D_k p_sigma and so l_z and C(l_z) are v_1 times constants on a line (A5-537 module), the
      record checks that C(l_z) is the same subspace at v_1 = 1 and 2, and z_0 is affine in v_1 with a nonzero E_eps
      part: its two E_eps coordinates are (1 - eps i v_1)/2 and -eps i (s + sigma)/2, which vanish together only at
      s + sigma = 0, the excluded locus of V(Q). The projection of C(l_z) on E_eps has rank 1 and holds z_0's, so
      C(l_z) lies in C z + E_(-eps) at every point of the line. E_+, E_-, C e_8 are mutually Hermitian-orthogonal and
      preserved by G_2(C), by the rotation (a scalar on each line) and by the scaling, so P = l_z, which says that z is
      Hermitian-orthogonal to l_z, makes C(l_z) Hermitian-orthogonal to l_z: L_z = C(l_z) and dim L = 12. dim L of 8 or
      10 never occurs at mu = 0.
   c. mu nonzero. dim C(l_z) = 3 holds z and two more vectors, so dim L is 2, 4 or 6, as dim L_z = 3 - rank of the
      pairing of C(l_z)/C z with l_z. Computed at the normal form itself (identity transformation) at four of its points
      (two cone points of the form (a, b, c i) with a^2 + b^2 = c^2, two signs sigma): the first-order map from the
      compact g_2 to (conjugate(z).l_z, pairing) has the conjugate(z).l_z part of rank 4, and the pairing on its kernel
      has a four-dimensional real image S in the 2 x 2 complex matrices on which det is i times a definite quadratic
      form. Floating-point witnesses at finite distance have P = l_z and the pairing of rank 1: dim L_z = 2 and
      dim L = 4 (see WITNESSES). The record keeps them as booleans of the singular-value gaps. That is not an exact
      result, and no exact point with dim L = 4 is known. The fiber conditions are linear in the Hermitian form of
      the group element; an exact point needs group elements with Gaussian-rational entries off the quaternion
      position, and an interval Newton certificate needs derivative enclosures of the kernel chart.
      The two-digit singular values of the witnesses are retained in WITNESS_SINGULAR_VALUES.

Evidence classes. Identities and certificates are exact (Q or Q(i), the integer samples named by their labels). The
witnesses are double-precision floating point: each is a z in C^15 whose singular values separate (a kernel of
dimension 3, rank 8 of M on the plane P, a two-dimensional fiber) by a gap of at least 1e-3 above 1e-9, and the two
normal-form calibrations take dim L_z = 3 and 6 through the same function.

Falsifiers. An orbit rank 14 or 15 at a point of nonzero Delta, or rank 13 off the quaternion position; a real point of
V(G) minus V(Q) with mu = 0, P = l_z and dim L of 8 or 10; a nullity of the kernel vectors other than 12 or 16 where
dim L is 6 or 12; an exact point with P = l_z, mu nonzero and dim L = 4 would turn the witnesses into a result, and no
such point at any precision would refute them.

`--write` writes nullity4-real-polar-line-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_line.py --check
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_gauss_image as gauss  # noqa: E402
import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_polar_line_module as polar  # noqa: E402

import parallel  # noqa: E402

symmetry = gauss.symmetry
SCHEMA = "a5-kernel-bundles-residuals-nullity4-real-polar-line-v1"
RECORD = HERE / "nullity4-real-polar-line-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_real_polar_line.py",
    HERE / "nullity4_polar_line_module.py",
    HERE / "nullity4_orbit_normal_forms.py",
    HERE / "nullity4_gauss_image.py",
    gauss.RECORD,
    gauss.FIXTURES,
    HERE.parent / "a5-kernel-bundles" / "kernel_symmetry.py",
    Path(symmetry.equations.__file__).resolve(),
)
FIELD = "Q and Q(i) with integer samples named by label; double precision for the two witnesses"
IDENTITIES = (
    "base_action_is_the_derivations_phase_and_scaling",
    "frame_stabilizer_is_su2_acting_freely_on_the_complement",
    "eigenlines_are_hermitian_orthogonal",
    "rotation_acts_by_scalars_on_the_eigenlines",
    "real_nullity_of_a_kernel_vector",
)
SAMPLE_KINDS = ("generic", "plane", "associative", "nonassociative")
SAMPLES_PER_KIND = 3
SIGMAS = (1, -1)
ZERO_LINES = ((1, 1), (1, -1), (-1, 1), (-1, -1))
CONE_POINTS = ((3, 4, 5), (5, 12, 13))
# The record of the orbit-rank samples: (position, mu zero) -> orbit ranks seen, then the calibration at Delta = 0.
ORBIT_RANKS = {
    "quaternion position": [13],
    "other position": [16],
    "gram zero calibration": [12],
}
# Per line (sigma, sign) at v_1 = 1 and 2 (see expected_mu_zero_lines): dim C(l_z), the sign eps of the line E_eps that
# holds the polar line (eps = -sigma sign), whether C(l_z) lies in C z + E_(-eps) + C e_8, the rank of the e_8
# components of C(l_z), and the ranks of its projections on E_+ and E_-.
FIRST_ORDER = {"rank_of_dF": 4, "dim_of_S": 4, "real_part_of_det_is_zero": True, "imaginary_part_is_definite": True}
# Witnesses: the 15 complex coordinates of z as decimal strings, real and imaginary part in turn. Each was found as
# z = exp(i A) z_0 with A in the compact g_2 and z_0 the normal form (e_1; mu; v_1 e_1 + (s + sigma) e_2), by minimizing
# the residual of the conditions conjugate(z).l_z = 0 and rank 1 of the pairing of C(l_z)/C z with l_z (the search
# script is not retained; the record states what each point is, not how it was found).
WITNESSES = (
    (
        "2.7904767507921733",
        "0.0",
        "-0.00018154625004063778",
        "-2.4554903597048865",
        "-0.27733083767784",
        "0.6458082906041921",
        "0.19363793100972435",
        "-0.24658349453009956",
        "0.39681057164870015",
        "0.42239491131835105",
        "-0.16952096411610848",
        "-0.6278276221247455",
        "-0.20986892495949955",
        "0.22697987891511734",
        "-0.3326091901750603",
        "0.35830718305612513",
        "-0.5612922019059128",
        "2.149546050394434",
        "2.5743648244977635",
        "-0.2922779491584069",
        "-0.5934334209686116",
        "-0.8559110583498674",
        "-0.08227591670004186",
        "0.19226447374680827",
        "-0.07597391327771236",
        "-0.3589870302317131",
        "-0.20426236424421113",
        "-0.3026242845112197",
        "-0.03661305835812234",
        "-0.22345562062412025",
    ),
    (
        "1.3719461624277345",
        "0.0",
        "-0.059454753537186385",
        "-0.20142153937701476",
        "0.03097249494505476",
        "-0.7956030971714037",
        "-0.3630086470615088",
        "0.015421572419688506",
        "0.3169260722251536",
        "-0.3491927902652172",
        "0.020135390823162593",
        "-0.21173153959451316",
        "0.23109565898181292",
        "0.5763678401341469",
        "-0.06111589465535249",
        "0.46568222060936804",
        "-0.06544086069888003",
        "-1.6001328975082925",
        "0.11968405471314086",
        "0.06420141804375457",
        "-0.9009511157323589",
        "0.028553721078797112",
        "0.07259167874823605",
        "0.445805807169948",
        "-0.40175988914308314",
        "-0.162938272354009",
        "-0.17838555805105016",
        "-0.08545775272299602",
        "0.6700986634457711",
        "-0.23716187982335232",
    ),
)
# Calibration: normal forms themselves, where P = l_z by block structure. (s, v_1, mu, sigma) = (3, 4, 5i, 1) has
# dim C(l_z) = 3 and (i, 1, 0, 1) has dim C(l_z) = 6, and the fiber is all of C(l_z).
CALIBRATIONS = (
    (
        "1",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "5",
        "4",
        "0",
        "4",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
    ),
    (
        "1",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "1",
        "0",
        "1",
        "1",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
    ),
)
# What a witness shows, as booleans and small integers so that the record holds no floating-point digits. The kernel
# vectors of P have rank 8 under M, which by A5-534 puts P in the polar line, so P = l_z.
WITNESS_FACTS = {
    "kernel_dimension": 3,
    "kernel_plane_dimension": 2,
    "polar_vector_ranks": [8, 8, 8],
    "fiber_dimension_of_L_z": 2,
    "kernel_singular_values_below_1e-9": True,
    "fiber_gap_above_1e-3": True,
    "mu_modulus_above_0.1": True,
    "norm_square_modulus_above_0.1": True,
}
CALIBRATION_FACTS = (
    {**WITNESS_FACTS, "fiber_dimension_of_L_z": 3},
    {
        **WITNESS_FACTS,
        "polar_vector_ranks": [6, 6, 6],
        "fiber_dimension_of_L_z": 6,
        "mu_modulus_above_0.1": False,
    },
)
# The singular values (two digits, "0" for a value below 1e-9 of the largest) of M(z) and of the system that defines
# L_z at each witness: three zeros for K(z), and two zeros out of fifteen for the fiber, so dim L_z = 2.
WITNESS_SINGULAR_VALUES = (
    {
        "M(z)": ["10", "10", "7.4", "7.4", "5.6", "5.6", "1.8", "1.8", "0.95", "0.95", "0.59", "0.59", "0", "0", "0"],
        "fiber system": [
            "2.5",
            "2.2",
            "2",
            "1.8",
            "1.6",
            "1.4",
            "1.3",
            "1.2",
            "1.2",
            "0.9",
            "0.85",
            "0.59",
            "0.49",
            "0",
            "0",
        ],
    },
    {
        "M(z)": ["5.5", "5.5", "4", "4", "2.8", "2.8", "1.1", "1.1", "0.68", "0.68", "0.25", "0.25", "0", "0", "0"],
        "fiber system": [
            "2.6",
            "2.4",
            "2.1",
            "1.9",
            "1.7",
            "1.5",
            "1.2",
            "1.1",
            "1.1",
            "0.77",
            "0.43",
            "0.36",
            "0.28",
            "0",
            "0",
        ],
    },
)
CLAIMS = {
    "orbit rank": {
        "values_where_delta_is_nonzero": [13, 16],
        "rank_13_exactly_in_quaternion_position": True,
        "fixtures_checked": 64,
        "fixtures_agreeing": 64,
        "fixtures_with_delta_zero": 2,
    },
    "fiber": {
        "nullity_of_kernel_vectors_at_dim_L_6_and_12": [12, 16],
        "mu_zero_with_P_equal_l_z": {"dim_L": 12, "dim_C": 6},
        "mu_nonzero_dim_C": 3,
        "mu_nonzero_dim_L_possible": [2, 4, 6],
        "dim_L_4_exact": False,
        "dim_L_4_floating_point_witnesses": 2,
    },
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _ints(label: str, count: int, low: int, high: int) -> list[int]:
    """count integers in low..high taken from sha256 of the label and a counter."""
    out: list[int] = []
    counter = 0
    while len(out) < count:
        digest = hashlib.sha256(f"{label}:{counter}".encode()).digest()
        out.extend(low + byte % (high - low + 1) for byte in digest)
        counter += 1
    return out[:count]


# --- the orbit rank ---------------------------------------------------------------------------------------------


@cache
def base_matrices() -> tuple[Any, ...]:
    """The base matrices of the solved Lie triples of the kernel symmetry algebra (rank 16)."""
    triples, _, _ = symmetry._solve_lie_triples("")
    return tuple(triple[0] for triple in triples)


def orbit_rank(y: list[int]) -> int:
    """The tangent rank of the orbit of the kernel symmetry algebra at the doubly pure y in Z^32."""
    point = [Fraction(value) for value in y]
    return int(symmetry._rank([symmetry._rational_matrix_vector_product(m, point) for m in base_matrices()]))


def point_from_parts(parts: list[list[int]], mu: tuple[int, int]) -> list[int]:
    """y with Re u, Im u, Re v, Im v given by four vectors of Z^7 (coordinates 1..7) and mu = (Re, Im)."""
    y = [0] * 32
    for k in range(7):
        y[k + 1], y[17 + k], y[9 + k], y[25 + k] = (parts[0][k], parts[1][k], parts[2][k], parts[3][k])
    y[8], y[24] = mu
    return y


def cross(first: list[int], second: list[int]) -> list[int]:
    """The imaginary part of the octonion product of two vectors of Z^7 (coordinates 1..7)."""
    return [
        sum(
            gauss.SIGNS[row][column] * first[(row ^ column) - 1] * second[column - 1]
            for column in range(1, 8)
            if column != row
        )
        for row in range(1, 8)
    ]


def quaternion_position(parts: list[list[int]]) -> bool:
    """Whether the span of the four vectors lies in the imaginary part of one quaternion subalgebra."""
    span = sp.Matrix(parts)
    rank = span.rank()
    if rank != 3:
        return bool(rank < 3)
    basis = [parts[index] for index in span.T.rref()[1]]
    return all(
        sp.Matrix([*basis, cross(basis[first], basis[second])]).rank() == 3
        for first, second in ((0, 1), (0, 2), (1, 2))
    )


def gram_determinant(parts: list[list[int]]) -> Any:
    """Delta = (u.u)(v.v) - (u.v)^2 for u = Re u + i Im u and v likewise."""
    u = [sp.Integer(a) + sp.I * b for a, b in zip(parts[0], parts[1], strict=True)]
    v = [sp.Integer(a) + sp.I * b for a, b in zip(parts[2], parts[3], strict=True)]
    uu, vv, uv = (sum(a * b for a, b in zip(x, y, strict=True)) for x, y in ((u, u), (v, v), (u, v)))
    return sp.expand(uu * vv - uv * uv)


def sample_parts(kind: str, label: str) -> list[list[int]]:
    """Four vectors of Z^7: generic, in a plane, in an associative 3-plane, or in a 3-plane that is not one."""
    raw = _ints(label, 28, -4, 4)
    first, second, third = raw[0:7], raw[7:14], raw[14:21]
    coefficients = _ints(label + ":coefficients", 12, -3, 3)
    if kind == "generic":
        return [raw[0:7], raw[7:14], raw[14:21], raw[21:28]]
    generators = {
        "plane": [first, second],
        "associative": [first, second, cross(first, second)],
        "nonassociative": [first, second, third],
    }[kind]
    return [
        [sum(coefficients[3 * row + g] * generator[k] for g, generator in enumerate(generators)) for k in range(7)]
        for row in range(4)
    ]


def orbit_rank_samples() -> dict[str, list[int]]:
    """Orbit ranks at samples with Delta nonzero, by position, and at planted points with Delta = 0."""
    seen: dict[str, set[int]] = {name: set() for name in ORBIT_RANKS}
    for kind in SAMPLE_KINDS:
        for index in range(SAMPLES_PER_KIND):
            for mu in ((0, 0), (2, -1)):
                for attempt in range(40):
                    label = f"nullity4-real-polar-line:{kind}:{index}:{mu}:{attempt}"
                    parts = sample_parts(kind, label)
                    if gram_determinant(parts) != 0:
                        break
                _require(gram_determinant(parts) != 0, "no sample with Delta nonzero")
                name = "quaternion position" if quaternion_position(parts) else "other position"
                seen[name].add(orbit_rank(point_from_parts(parts, mu)))
    unit = [[1 if column == row else 0 for column in range(7)] for row in range(7)]
    zero = [0] * 7
    seen["gram zero calibration"].add(orbit_rank(point_from_parts([unit[0], unit[1], zero, zero], (0, 0))))
    return {name: sorted(ranks) for name, ranks in seen.items()}


def fixture_agreement() -> dict[str, int]:
    """At the 66 fixtures with Delta nonzero: retained orbit rank 13 against the quaternion position."""
    retained = json.loads(gauss.RECORD.read_text(encoding="utf-8"))["exact_fixture_orbit_ranks"]
    checked = agreeing = gram_zero = 0
    for number, _, split in gauss._fixture_splits():
        z = [value * sp.I ** (unit.bit_count() % 4) for unit, value in zip(range(1, 16), split, strict=True)]
        u, v = z[0:7], z[8:15]
        uu, vv, uv = (sum(a * b for a, b in zip(x, y, strict=True)) for x, y in ((u, u), (v, v), (u, v)))
        if sp.expand(uu * vv - uv * uv) == 0:
            gram_zero += 1
            continue
        checked += 1
        agreeing += (retained[number] == 13) == forms.in_one_quaternion_subalgebra(split)
    return {"checked": checked, "agreeing": agreeing, "gram_zero": gram_zero}


# --- exact identities -------------------------------------------------------------------------------------------


def base_action_is_the_derivations_phase_and_scaling() -> bool:
    """The solved triples have the base span of the 14 derivations, J and the identity; the derivations are skew."""
    solved = [symmetry._flatten_matrix(m) for m in base_matrices()]
    named = [
        symmetry._flatten_matrix(triple[0])
        for name, triple in symmetry._expected_lie_triples("")
        if name not in ("domain_scaling", "vertical_j_phase")
    ]
    ranks = (symmetry._rank(solved), symmetry._rank(named), symmetry._rank(solved + named))
    derivations = [triple[0] for name, triple in symmetry._expected_lie_triples("") if name.startswith("compact_g2")]
    phase = dict(symmetry._expected_lie_triples(""))["base_phase_lift"][0]
    skew = all(m[i][j] == -m[j][i] for m in [*derivations, phase] for i in range(32) for j in range(32))
    pairs = all(
        phase[k][16 + k] == 1 and phase[16 + k][k] == -1 and sum(abs(x) for x in phase[k]) == 1 for k in range(1, 16)
    )
    commute = all(
        sum(m[i][k] * phase[k][j] - phase[i][k] * m[k][j] for k in range(32)) == 0
        for m in derivations
        for i in range(32)
        for j in range(32)
    )
    return ranks == (16, 16, 16) and skew and pairs and commute and len(derivations) == 14


def frame_stabilizer_is_su2_acting_freely_on_the_complement() -> bool:
    """The derivations that kill e_1 and e_2 are D_1, D_2, D_3; |(sum x_k D_k) c|^2 = (sum x_k^2) |c|^2 off e_1..e_3."""
    derivations = [
        sp.Matrix(7, 7, lambda i, j, m=triple[0]: sp.Rational(m[i + 1][j + 1].numerator, m[i + 1][j + 1].denominator))
        for triple in symmetry._octonion_derivation_triples()
    ]
    killing = sp.Matrix.hstack(*[sp.Matrix.vstack(d[:, 0], d[:, 1]) for d in derivations])
    stabilizer = [sum((c[k] * derivations[k] for k in range(14)), sp.zeros(7, 7)) for c in killing.nullspace()]
    given = [matrix[0:7, 0:7] for matrix in polar.derivations()]
    same_span = sp.Matrix([list(m) for m in [*stabilizer, *given]]).rank() == 3
    x = sp.symbols("y1:4", real=True)
    c = sp.Matrix(sp.symbols("c4:8", real=True))
    element = sum((x[k] * given[k] for k in range(3)), sp.zeros(7, 7))
    moved = element * sp.Matrix([0, 0, 0, *c])
    norm_square = sp.expand((moved.T * moved)[0, 0] - sum(v * v for v in x) * sum(v * v for v in c))
    kills = all(given[k][:, axis] == sp.zeros(7, 1) for k in range(3) for axis in (0, 1, 2))
    return len(stabilizer) == 3 and same_span and norm_square == 0 and kills


def eigenlines_are_hermitian_orthogonal() -> bool:
    """E_+ = {(a; 0; i a)}, E_- = {(a; 0; -i a)} and C e_8 are pairwise Hermitian-orthogonal in C^15."""
    a = sp.Matrix(sp.symbols("a1:8"))
    b = sp.Matrix(sp.symbols("b1:8"))
    mu = sp.Symbol("m")

    def vector(first: sp.Matrix, middle: Any, second: sp.Matrix) -> sp.Matrix:
        return sp.Matrix([*first, middle, *second])

    plus = vector(a, 0, sp.I * a)
    minus = vector(b, 0, -sp.I * b)
    middle = vector(sp.zeros(7, 1), mu, sp.zeros(7, 1))
    pairs = ((plus, minus), (plus, middle), (minus, middle))
    return all(sp.expand((x.H * y)[0, 0]) == 0 for x, y in pairs) and sp.expand((plus.H * plus)[0, 0]) != 0


def rotation_acts_by_scalars_on_the_eigenlines() -> bool:
    """The rotation by 120 degrees of each (u_j, v_j) plane multiplies E_+- by c -+ i s with c = -1/2, s = sqrt(3)/2."""
    c, s = sp.Rational(-1, 2), sp.sqrt(3) / 2
    a = sp.Matrix(sp.symbols("a1:8"))
    for sign in (1, -1):
        u, v = a, sign * sp.I * a
        moved_u, moved_v = c * u - s * v, s * u + c * v
        scalar = c - sign * sp.I * s
        if sp.simplify(moved_u - scalar * u) != sp.zeros(7, 1) or sp.simplify(
            moved_v - sign * sp.I * scalar * u
        ) != sp.zeros(7, 1):
            return False
    return bool(sp.simplify(c * c + s * s) == 1)


def _bordered(p: list[Any]) -> sp.Matrix:
    """A(p, conjugate(p)): first row -conjugate(p), first column conjugate(p), lower block M(p)."""
    lower = forms.block(p, forms.ALL, forms.ALL)
    w = [sp.conjugate(entry) for entry in p]
    matrix = sp.zeros(16, 16)
    for index in range(15):
        matrix[0, index + 1], matrix[index + 1, 0] = -w[index], w[index]
    matrix[1:, 1:] = lower
    return matrix


def _nullity(matrix: sp.Matrix) -> int:
    ring = DomainMatrix.from_Matrix(matrix.applyfunc(sp.expand)).convert_to(sp.QQ_I)
    return matrix.shape[1] - int(ring.rank())


def real_nullity_of_a_kernel_vector() -> bool:
    """dim ker A(p, conjugate(p)) = nullity M(p) - 1 at p in the polar line, for mu nonzero and for mu = 0."""
    results = []
    for sigma, (s, v1, mu) in (
        (1, (3, 4, 5 * sp.I)),
        (-1, (5, 12, 13 * sp.I)),
        (1, (sp.I, 1, 0)),
        (-1, (-2 * sp.I, 2, 0)),
    ):
        entries = [
            sp.expand(e.subs({polar.S_VAR: s, polar.V1: v1, polar.MU: mu})) if isinstance(e, sp.Basic) else e
            for e in polar.VECTORS[sigma]
        ]
        base = polar._complement_vector(entries)
        generic = [x + y for x, y in zip(base, list(polar.derivations()[1] * sp.Matrix(base)), strict=True)]
        for p in (base, generic):
            nullity = _nullity(forms.block(p, forms.ALL, forms.ALL))
            results.append((nullity, _nullity(_bordered(p)) == nullity - 1))
    return results == [(7, True)] * 4 + [(9, True)] * 4


CHECKS = {
    "base_action_is_the_derivations_phase_and_scaling": base_action_is_the_derivations_phase_and_scaling,
    "frame_stabilizer_is_su2_acting_freely_on_the_complement": frame_stabilizer_is_su2_acting_freely_on_the_complement,
    "eigenlines_are_hermitian_orthogonal": eigenlines_are_hermitian_orthogonal,
    "rotation_acts_by_scalars_on_the_eigenlines": rotation_acts_by_scalars_on_the_eigenlines,
    "real_nullity_of_a_kernel_vector": real_nullity_of_a_kernel_vector,
}


def identity(name: str) -> bool:
    return CHECKS[name]()


# --- the polar line at mu = 0 -------------------------------------------------------------------------------------


def _rank(rows: list[Any]) -> int:
    return int(DomainMatrix.from_Matrix(sp.Matrix(rows).applyfunc(sp.expand)).convert_to(sp.QQ_I).rank())


def eigenline(sign: int) -> list[list[Any]]:
    """A basis of E_sign = {(a; 0; sign i a)}."""
    rows = []
    for j in range(7):
        vector: list[Any] = [0] * 15
        vector[j], vector[8 + j] = 1, sign * sp.I
        rows.append(vector)
    return rows


def polar_data(sigma: int, s: Any, v1: Any, mu: Any) -> tuple[list[Any], list[list[Any]], list[list[Any]]]:
    """z_0, a basis of the polar line and a basis of C(l_z) at the normal-form point (s, v_1, mu)."""
    values = {polar.S_VAR: s, polar.V1: v1, polar.MU: mu}
    z0 = forms.frame([1, 0, 0], mu, [v1, s + sigma, 0])
    entries = [sp.expand(e.subs(values)) if isinstance(e, sp.Basic) else e for e in polar.VECTORS[sigma]]
    p = polar._complement_vector(entries)
    line: list[list[Any]] = []
    for vector in [p, *[list(matrix * sp.Matrix(p)) for matrix in polar.derivations()]]:
        if _rank([*line, vector]) > len(line):
            line.append(vector)
    stack = sp.Matrix.vstack(*[forms.block(q, forms.ALL, forms.ALL) for q in line])
    kernel = DomainMatrix.from_Matrix(stack.applyfunc(sp.expand)).convert_to(sp.QQ_I).nullspace().to_Matrix().tolist()
    return z0, line, kernel


def mu_zero_line(job: tuple[int, int, int]) -> list[Any]:
    """The record of the line s = sign i v_1, mu = 0 at the given v_1, with the sign eps of E_eps holding l_z."""
    sigma, sign, v1 = job
    z0, line, kernel = polar_data(sigma, sign * sp.I * v1, v1, 0)
    _require(len(line) == 2, "the polar line is not two-dimensional")
    holds = [eps for eps in (1, -1) if all(_rank([*eigenline(eps), vector]) == 7 for vector in line)]
    eps = holds[0] if len(holds) == 1 else None
    opposite = eigenline(-eps if eps else 1)
    e8: list[Any] = [0] * 15
    e8[7] = 1
    contained = eps is not None and _rank([*opposite, z0, e8, *kernel]) == _rank([*opposite, z0, e8])

    def components(x: list[Any], sign_: int) -> list[Any]:
        return [sp.expand((x[j] - sign_ * sp.I * x[8 + j]) / 2) for j in range(7)]

    plus = _rank([components(x, 1) for x in kernel])
    minus = _rank([components(x, -1) for x in kernel])
    e8_rank = _rank([[x[7]] for x in kernel])
    return [len(kernel), eps, contained, e8_rank, plus, minus]


def kernel_independence(job: tuple[int, int]) -> bool:
    """Whether C(l_z) on the line s = sign i v_1 is the same six-dimensional subspace at v_1 = 1 and 2."""
    sigma, sign = job
    first = polar_data(sigma, sign * sp.I, 1, 0)[2]
    second = polar_data(sigma, 2 * sign * sp.I, 2, 0)[2]
    return len(first) == len(second) == 6 and _rank([*first, *second]) == 6


def mu_zero_kernel_independence() -> list[bool]:
    return parallel.ordered_map(kernel_independence, list(ZERO_LINES), min_items=2)


def fixture_kernel_nullities() -> dict[str, int]:
    """At the 66 fixtures: the retained real nullity of the kernel vectors against 2 (plane nullity - 1)."""
    record = json.loads(gauss.RECORD.read_text(encoding="utf-8"))
    pairs = zip(record["exact_fixture_invariants"], record["exact_fixture_kernel_forms"], strict=True)
    agree = sum(row["kernel_vector_nullity"] == 2 * (form["plane_nullity"] - 1) for row, form in pairs)
    return {"fixtures": len(record["exact_fixture_invariants"]), "agree": agree}


def mu_zero_lines() -> list[list[Any]]:
    jobs = [(sigma, sign, v1) for sigma, sign in ZERO_LINES for v1 in (1, 2)]
    return parallel.ordered_map(mu_zero_line, jobs, min_items=2)


def expected_mu_zero_lines() -> list[list[Any]]:
    """C(l_z) projects on E_(-eps) with rank 5 and on E_eps with rank 1 (the line of z), where E_eps holds l_z."""
    rows: list[list[Any]] = []
    for sigma, sign in ZERO_LINES:
        eps = -sigma * sign
        rows.extend([6, eps, True, 0, 5 if eps == -1 else 1, 1 if eps == -1 else 5] for _ in (1, 2))
    return rows


# --- the first-order pairing at mu nonzero ------------------------------------------------------------------------


def _derivations_15() -> list[sp.Matrix]:
    out = []
    for triple in symmetry._octonion_derivation_triples():
        matrix = sp.zeros(15, 15)
        for i in range(1, 8):
            for j in range(1, 8):
                entry = triple[0][i][j]
                matrix[i - 1, j - 1] = matrix[8 + i - 1, 8 + j - 1] = sp.Rational(entry.numerator, entry.denominator)
        out.append(matrix)
    return out


def first_order_pairing(job: tuple[int, int]) -> dict[str, Any]:
    """At the normal form (s, v_1, mu) of a Pythagorean cone point: the first-order map xi -> (F, N) of the pairing."""
    sigma, index = job
    a, b, c = CONE_POINTS[index]
    z0, line, kernel = polar_data(sigma, sp.Integer(a), sp.Integer(b), sp.I * c)
    _require(len(line) == 2 and len(kernel) == 3, "the polar line or C(l_z) has another dimension")
    basis = [sp.Matrix(z0)]
    for vector in kernel:
        if _rank([list(x) for x in basis] + [vector]) > len(basis):
            basis.append(sp.Matrix(vector))
    derivations = _derivations_15()
    table = sp.Matrix(
        [[sp.expand((c_.H * (matrix * sp.Matrix(q)))[0, 0]) for c_ in basis for q in line] for matrix in derivations]
    )
    real, imaginary = table.applyfunc(sp.re), table.applyfunc(sp.im)
    first = sp.Matrix.hstack(real[:, 0:2], imaginary[:, 0:2]).T
    rest = sp.Matrix.hstack(real[:, 2:6], imaginary[:, 2:6]).T
    kernel_of_first = first.nullspace()
    image = sp.Matrix.hstack(*[rest * vector for vector in kernel_of_first])
    columns = image.columnspace()
    matrices = [
        sp.Matrix([[v[0] + sp.I * v[4], v[1] + sp.I * v[5]], [v[2] + sp.I * v[6], v[3] + sp.I * v[7]]]) for v in columns
    ]
    coefficients = sp.symbols(f"a0:{len(matrices)}", real=True)
    determinant = sp.expand(sum((x * m for x, m in zip(coefficients, matrices, strict=True)), sp.zeros(2, 2)).det())
    real_part, imaginary_part = sp.expand(sp.re(determinant)), sp.expand(sp.im(determinant))
    form = sp.hessian(imaginary_part, coefficients) / 2
    definite = all(form[:k, :k].det() > 0 for k in range(1, form.rows + 1)) or all(
        (-1) ** k * form[:k, :k].det() > 0 for k in range(1, form.rows + 1)
    )
    return {
        "rank_of_dF": int(first.rank()),
        "dim_of_S": len(columns),
        "real_part_of_det_is_zero": real_part == 0,
        "imaginary_part_is_definite": bool(definite),
    }


def first_order_pairings() -> list[dict[str, Any]]:
    jobs = [(sigma, index) for sigma in SIGMAS for index in range(len(CONE_POINTS))]
    return parallel.ordered_map(first_order_pairing, jobs, min_items=2)


# --- floating-point witnesses -------------------------------------------------------------------------------------


@cache
def _tables() -> tuple[Any, Any, Any, Any]:
    rows, columns, index, sign = [], [], [], []
    for r in range(1, 16):
        for c in range(1, 16):
            if r != c:
                rows.append(r - 1)
                columns.append(c - 1)
                index.append((r ^ c) - 1)
                sign.append(float(gauss.SIGNS[r][c]))
    return np.array(rows), np.array(columns), np.array(index), np.array(sign)


def lower_block(z: Any) -> Any:
    """M(z) as a complex 15 x 15 array."""
    rows, columns, index, sign = _tables()
    matrix = np.zeros((15, 15), dtype=complex)
    matrix[rows, columns] = sign * z[index]
    return matrix


def _kernel(matrix: Any, tolerance: float = 1e-9) -> tuple[Any, Any]:
    """An orthonormal basis (as columns) of the numerical kernel, and the singular values."""
    _, values, vh = np.linalg.svd(matrix)
    rank = int((values > tolerance * values[0]).sum())
    return vh[rank:].conj().T, values


def _numerical_rank(matrix: Any, tolerance: float = 1e-9) -> int:
    values = np.linalg.svd(matrix, compute_uv=False)
    return int((values > tolerance * values[0]).sum())


def point_from_strings(coordinates: tuple[str, ...]) -> Any:
    """The vector of C^15 whose real and imaginary parts are the decimal strings in turn."""
    return np.array([complex(float(coordinates[2 * k]), float(coordinates[2 * k + 1])) for k in range(15)])


def _two_digits(values: Any, scale: float) -> list[str]:
    """Singular values to two significant digits; "0" below 1e-9 of the scale."""
    return ["0" if value < 1e-9 * scale else f"{value:.2g}" for value in values]


def witness_singular_values(coordinates: tuple[str, ...]) -> dict[str, list[str]]:
    """The singular values of M(z) and of the system that defines L_z, as the evidence for the dimensions."""
    z = point_from_strings(coordinates)
    kernel, values = _kernel(lower_block(z))
    functional = z.conj() @ kernel
    _, _, vh = np.linalg.svd(functional.reshape(1, -1))
    plane = kernel @ vh[1:].conj().T
    units = [lower_block(np.eye(15)[j]) for j in range(15)]
    rows = []
    for k in range(plane.shape[1]):
        p = plane[:, k]
        rows.append(np.stack([unit @ p for unit in units], axis=1))
        rows.append(p.conj().reshape(1, -1))
    fiber = np.linalg.svd(np.vstack(rows), compute_uv=False) if rows else np.zeros(1)
    return {"M(z)": _two_digits(values, values[0]), "fiber system": _two_digits(fiber, fiber[0])}


def witness_facts(coordinates: tuple[str, ...]) -> dict[str, Any]:
    """K(z), P = K(z) n conjugate(z)-perp, the ranks of M on P and L_z from its definition at one point."""
    z = point_from_strings(coordinates)
    kernel, values = _kernel(lower_block(z))
    functional = z.conj() @ kernel
    _, _, vh = np.linalg.svd(functional.reshape(1, -1))
    plane = kernel @ vh[1:].conj().T
    vectors = [plane[:, 0], plane[:, 1], plane[:, 0] + 0.7 * plane[:, 1]] if plane.shape[1] == 2 else []
    units = [lower_block(np.eye(15)[j]) for j in range(15)]
    rows = []
    for k in range(plane.shape[1]):
        p = plane[:, k]
        rows.append(np.stack([unit @ p for unit in units], axis=1))
        rows.append(p.conj().reshape(1, -1))
    if rows:
        fiber, fiber_values = _kernel(np.vstack(rows))
        fiber_dimension = int(fiber.shape[1])
        gap = bool(fiber_values[: 15 - fiber_dimension].min() > 1e-3 * fiber_values[0])
    else:
        fiber_dimension, gap = -1, False
    return {
        "kernel_dimension": int(kernel.shape[1]),
        "kernel_plane_dimension": int(plane.shape[1]),
        "polar_vector_ranks": [_numerical_rank(lower_block(p)) for p in vectors],
        "fiber_dimension_of_L_z": fiber_dimension,
        "kernel_singular_values_below_1e-9": bool(values[-kernel.shape[1] :].max() < 1e-9 * values[0]),
        "fiber_gap_above_1e-3": gap,
        "mu_modulus_above_0.1": bool(abs(z[7]) > 0.1),
        "norm_square_modulus_above_0.1": bool(abs(z @ z) > 0.1),
    }


# --- record -------------------------------------------------------------------------------------------------------


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    lines = mu_zero_lines()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "orbit_rank_samples": orbit_rank_samples(),
        "fixture_agreement": fixture_agreement(),
        "mu_zero_lines": lines,
        "first_order_pairings": first_order_pairings(),
        "witnesses": [witness_facts(coordinates) for coordinates in WITNESSES],
        "witness_singular_values": [witness_singular_values(coordinates) for coordinates in WITNESSES],
        "calibrations": [witness_facts(coordinates) for coordinates in CALIBRATIONS],
        "fixture_kernel_nullities": fixture_kernel_nullities(),
        "mu_zero_kernels_independent_of_v_1": mu_zero_kernel_independence(),
        "claims": copy.deepcopy(CLAIMS),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": dict.fromkeys(IDENTITIES, True),
        "orbit_rank_samples": copy.deepcopy(ORBIT_RANKS),
        "fixture_agreement": {
            "checked": CLAIMS["orbit rank"]["fixtures_checked"],
            "agreeing": CLAIMS["orbit rank"]["fixtures_agreeing"],
            "gram_zero": CLAIMS["orbit rank"]["fixtures_with_delta_zero"],
        },
        "mu_zero_lines": expected_mu_zero_lines(),
        "first_order_pairings": [copy.deepcopy(FIRST_ORDER) for _ in range(len(SIGMAS) * len(CONE_POINTS))],
        "witnesses": [copy.deepcopy(WITNESS_FACTS) for _ in WITNESSES],
        "witness_singular_values": copy.deepcopy(list(WITNESS_SINGULAR_VALUES)),
        "calibrations": copy.deepcopy(list(CALIBRATION_FACTS)),
        "fixture_kernel_nullities": {"fixtures": 66, "agree": 66},
        "mu_zero_kernels_independent_of_v_1": [True] * len(ZERO_LINES),
        "claims": copy.deepcopy(CLAIMS),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "orbit_rank_samples": "an orbit rank differs from 16 minus the dimension of the stabilizer of the span",
        "fixture_agreement": "the retained fixture orbit ranks disagree with the quaternion position",
        "mu_zero_lines": "the polar line or C(l_z) at mu = 0 leaves its eigenline decomposition",
        "first_order_pairings": "the first-order pairing at mu nonzero is not the definite four-dimensional space",
        "witnesses": "a floating-point witness no longer has P = l_z with a two-dimensional fiber",
        "witness_singular_values": "the singular values of a witness differ from the retained two-digit values",
        "calibrations": "a normal-form calibration point leaves its fiber dimension",
        "fixture_kernel_nullities": "a retained kernel-vector nullity differs from 2 (nullity of M on P - 1)",
        "mu_zero_kernels_independent_of_v_1": "C(l_z) at mu = 0 changes with v_1",
        "claims": "the claims differ from the record the constants determine",
    }
    for group, message in messages.items():
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        f"pass: {len(record['identities'])} identities, {len(record['mu_zero_lines'])} lines, "
        f"{len(record['witnesses'])} witnesses, {record['fixture_agreement']['checked']} fixtures"
    )


if __name__ == "__main__":
    main()
