"""A real point of V(G) minus V(Q) with mu nonzero, kernel plane l_z and dim L = 4, certified by an interval Newton box.

z = (u; mu; v) in C^15 is a real point when w = conjugate(z) (A5-430). Its kernel plane is P = K(z) n conjugate(z)-perp
with K(z) = ker M(z), and the fiber is L = L_z x conjugate(L_z) with L_z = {x : M(x) P = 0, x Hermitian-orthogonal to
P} (nullity4_real_polar_line.py, items 2a to 2c). The record certifies that dim L = 4 occurs at mu nonzero.

Reduction to a system in the Hermitian form. The 14 derivations D_k of the octonions act on C^15 by the real skew
matrices diag(D_k, 0, D_k) (zero on the mu coordinate), and M(D x) = D M(x) + M(x) D^T on every basis vector; the
identity is linear in D, so for H = i sum xi_k D_k and Theta = exp(H) it integrates to M(Theta x) = Theta M(x) Theta^T,
and Theta^T Theta = 1 because H^T = -H. The group element Theta = exp(H) is Hermitian, so Theta^* Theta = Pi =
exp(2 H). Fix the normal-form point z_0 = (e_1; mu; v_1 e_1 + (s + sigma) e_2) with s^2 + v_1^2 + mu^2 = 0, a line
l = span(l_1, l_2) in K(z_0), and C = {x : M(l_1) x = M(l_2) x = 0} = span(z_0, c_2, c_3) of dimension 3, all exact
over Q(i) (nullity4_real_polar_line.polar_data). For z = Theta z_0:

- Q(z) = Q(z_0), mu(z) = mu(z_0) and G(z) = G(z_0) = 0, because Theta acts on u and v by one complex orthogonal 7 x 7
  block and fixes mu, so u.u, u.v, v.v and mu are invariants. Q(z_0) and mu(z_0) are nonzero, so z lies in V(G) minus
  V(Q) with mu nonzero.
- rank M(z) = rank M(z_0) = 12 and K(z) = Theta K(z_0) has dimension 3.
- l_z = Theta l lies in K(z). z lies in K(z) (M(z) z = 0 by antisymmetry) and conjugate(z).z is positive, so K(z) n
  conjugate(z)-perp has dimension 2, and l_z lies in it exactly when conjugate(z).l_z = 0, which is z_0^* Pi l = 0 (the
  row F of the system). Then P = l_z.
- C(l_z) = {x : M(x) l_z = 0} = Theta C, which has dimension 3 and holds z, so L_z is the kernel of x -> l_z^* x on
  C(l_z), and dim L_z = 3 - rank N with the 2 x 2 matrix N = [c_2, c_3]^* Pi l (the row of z_0 is F = 0).
- dim L = 2 dim L_z. It equals 4 exactly when det N = 0 and N is nonzero.

The unknown is xi in R^14. The system f(xi) = (Re F_1, Im F_1, Re F_2, Im F_2, Re det N, Im det N) consists of 6 real
equations, so 6 of the 14 coordinates (SLICE_FREE) are unknown and the other 8 are dyadic constants (FIXED_NUMERATORS);
no equation is dropped. The Krawczyk operator K(X) = x* - C f(x*) + (I - C J(X)) (X - x*) of the box X = x* + [-r, r]^6
(C the inverse of the midpoint of J(x*)) uses J(X), an arb enclosure of the Jacobian over X: for each free k the
upper right block of exp([[2H, 2 i D_k], [0, 2H]]) is d Pi / d xi_k (the derivative of the matrix exponential),
evaluated on ball matrices; the derivative of det N
is the polynomial N_11 dN_22 + dN_11 N_22 - N_12 dN_21 - dN_12 N_21. K(X) inside the interior of X proves that f
has exactly one zero in X. At that zero F = 0 and det N = 0, and the bound on one entry of N over the whole box proves
N nonzero, so rank N = 1, dim L_z = 2 and dim L = 4. The rank and dimension facts at z_0 are exact over Q(i) and
constant on the orbit of Theta, so the box needs no rank enclosures.

Evidence classes. The identities and ranks at z_0 are exact over Q(i). The existence of the real zero of f in the box
(and its uniqueness there) is a certified interval statement at 200 bits; the point is not an exact point and no
exact algebraic point is known. The double-precision cross-check evaluates the dimensions from the definition at the
midpoint of the box through nullity4_real_polar_line.witness_facts and is a measurement.

Falsifiers. A failed identity or rank at z_0; K(X) not inside X; an entry of N whose ball contains 0; a
double-precision midpoint whose K(z), P or L_z dimension differs from 3, 2 and 2.

`--write` writes nullity4-real-polar-fiber-four-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_fiber_four.py --check
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp
from flint import acb, acb_mat, arb, arb_mat, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_real_polar_line as real_line  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-real-polar-fiber-four-v1"
RECORD = HERE / "nullity4-real-polar-fiber-four-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_real_polar_fiber_four.py",
    HERE / "nullity4_real_polar_line.py",
    HERE / "nullity4_polar_line_module.py",
    HERE / "nullity4_orbit_normal_forms.py",
    HERE / "nullity4_gauss_image.py",
    HERE.parent / "a5-kernel-bundles" / "kernel_symmetry.py",
    ROOT / "docs" / "evidence" / "a5-rank-strata-equations" / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)
PRECISION = 200
FIELD = f"Q(i) for the normal form; arb balls at {PRECISION} bits for the zero in the box; double precision"
# The normal-form point (s, v_1, mu) = (4, 3, 5 i) on the cone s^2 + v_1^2 + mu^2 = 0 with sigma = 1.
SIGMA = 1
CONE_POINT = (4, 3, 5)
# The slice of xi in R^14: the free coordinates, and the others as numerators over 2^FIXED_BITS.
SLICE_FREE = (0, 1, 2, 4, 9, 11)
FIXED_BITS = 10
FIXED_NUMERATORS = {3: 149, 5: 98, 6: -23, 7: -70, 8: 44, 10: 2, 12: 120, 13: 275}
# The midpoint of the box as numerators over 2^MIDPOINT_BITS, in the order of SLICE_FREE, and its radius 2^-RADIUS_BITS.
MIDPOINT_BITS = 60
MIDPOINT = (
    38994581117443500,
    53842321344079524,
    -230017735920244814,
    -23016549000837857,
    -44883851846891566,
    -79270953292811649,
)
RADIUS_BITS = 24
# The rounded outcome of the interval evaluation: K(X) lies within 2^-CONTRACTION_BITS of the radius from the midpoint,
# and the entry PAIRING_ENTRY of N exceeds 2^PAIRING_BOUND_BITS in modulus on the whole box.
CONTRACTION_BITS = 13
PAIRING_ENTRY = (1, 1)
PAIRING_BOUND_BITS = 36
IDENTITIES = (
    "derivations_are_skew_block_equivariant",
    "unit_products_anticommute",
    "normal_form_on_V_G_off_V_Q",
    "rank_of_M_at_the_normal_form_is_12",
    "polar_line_in_the_kernel_with_dim_C_3",
    "rank_8_on_the_polar_line",
)
POINT_FACTS = {"Q": 10, "G": 0, "mu": "5*I", "cone": 0}
EXACT_FACTS = {"rank_M_z0": 12, "stack_rank": 12, "dim_C": 3, "polar_line_ranks": [8, 8, 8, 8, 8]}
DOUBLE_FACTS = {
    "kernel_dimension": 3,
    "kernel_plane_dimension": 2,
    "polar_vector_ranks": [8, 8, 8],
    "fiber_dimension_of_L_z": 2,
    "kernel_singular_values_below_1e-9": True,
    "fiber_gap_above_1e-3": True,
    "mu_modulus_above_0.1": True,
    "norm_square_modulus_above_0.1": True,
}
CLAIMS = {
    "dim_L": 4,
    "dim_L_z": 2,
    "rank_of_pairing": 1,
    "kernel_plane_is_polar_line": True,
    "mu_nonzero": True,
    "interval_certificate": True,
    "exact_point": False,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# --- exact data at the normal form --------------------------------------------------------------------------------


@functools.cache
def _exact() -> tuple[list[Any], list[list[Any]], list[list[Any]]]:
    """z_0, a basis of l and a basis (z_0, c_2, c_3) of C, over Q(i)."""
    s, v1, modulus = CONE_POINT
    z0, line, kernel = real_line.polar_data(SIGMA, sp.Integer(s), sp.Integer(v1), sp.I * modulus)
    basis = [list(z0)]
    for vector in kernel:
        if real_line._rank([*basis, vector]) > len(basis):
            basis.append(list(vector))
    _require(len(line) == 2 and len(basis) == 3, "the polar line or C has another dimension")
    return list(z0), [list(x) for x in line], basis


@functools.cache
def _units() -> list[sp.Matrix]:
    """M(e_a) for the 15 basis vectors."""
    return [forms.block([1 if j == a else 0 for j in range(15)], forms.ALL, forms.ALL) for a in range(15)]


@functools.cache
def _derivations() -> list[sp.Matrix]:
    return real_line._derivations_15()


def derivation_identity(index: int) -> bool:
    """D is skew with the block form diag(R, 0, R) and M(D e_a) = D M(e_a) + M(e_a) D^T for the 15 vectors e_a."""
    matrix = _derivations()[index]
    units = _units()
    skew = matrix + matrix.T == sp.zeros(15, 15)
    blocks = (
        matrix[0:7, 0:7] == matrix[8:15, 8:15]
        and matrix[0:7, 8:15] == sp.zeros(7, 7)
        and matrix[8:15, 0:7] == sp.zeros(7, 7)
        and matrix[7, :] == sp.zeros(1, 15)
        and matrix[:, 7] == sp.zeros(15, 1)
    )
    equivariant = all(
        sum((matrix[b, a] * units[b] for b in range(15)), sp.zeros(15, 15)) == matrix * units[a] + units[a] * matrix.T
        for a in range(15)
    )
    return bool(skew and blocks and equivariant)


def _block(vector: list[Any]) -> sp.Matrix:
    return forms.block(vector, forms.ALL, forms.ALL).applyfunc(sp.expand)


def unit_products_anticommute() -> bool:
    units = _units()
    return all(units[a][:, b] + units[b][:, a] == sp.zeros(15, 1) for a in range(15) for b in range(15))


def normal_form_facts() -> dict[str, Any]:
    z0, _, _ = _exact()
    u, mu, v = z0[:7], z0[7], z0[8:]
    dot = sum(a * a for a in u)
    cross = sum(a * b for a, b in zip(u, v, strict=True))
    q = sp.expand(dot + mu * mu + sum(b * b for b in v))
    g = sp.expand(q * q - 4 * (dot * sum(b * b for b in v) - cross * cross))
    s, v1, modulus = CONE_POINT
    return {"Q": int(q), "G": int(g), "mu": str(sp.nsimplify(mu)), "cone": s * s + v1 * v1 - modulus * modulus}


def rank_of_M_at_the_normal_form() -> int:
    z0, _, _ = _exact()
    return int(real_line._rank(_block(z0).tolist()))


def polar_line_facts() -> dict[str, Any]:
    """M(z_0) l = 0, the rank of the stack (so dim C), z_0 in C, and the ranks of M on five vectors of l."""
    z0, line, basis = _exact()
    in_kernel = all(_block(z0) * sp.Matrix(p) == sp.zeros(15, 1) for p in line)
    stack = sp.Matrix.vstack(*[_block(p) for p in line])
    stack_rank = int(real_line._rank(stack.tolist()))
    z0_in_c = all(_block(p) * sp.Matrix(z0) == sp.zeros(15, 1) for p in line)
    first, second = sp.Matrix(line[0]), sp.Matrix(line[1])
    vectors = [first, second, first + second, first + 3 * second, first + sp.I * second]
    ranks = [int(real_line._rank(_block(list(p)).tolist())) for p in vectors]
    return {"in_kernel": in_kernel, "stack_rank": stack_rank, "z0_in_C": z0_in_c, "ranks": ranks}


def exact_job(job: tuple[str, int]) -> Any:
    name, index = job
    if name == "derivation":
        return derivation_identity(index)
    if name == "unit_products_anticommute":
        return unit_products_anticommute()
    if name == "normal_form":
        return normal_form_facts()
    if name == "rank_M":
        return rank_of_M_at_the_normal_form()
    return polar_line_facts()


def exact_facts() -> tuple[dict[str, bool], dict[str, Any], dict[str, Any]]:
    """The identities, the point facts and the exact ranks, from independent jobs."""
    jobs: list[tuple[str, int]] = [("derivation", k) for k in range(14)]
    jobs += [("unit_products_anticommute", 0), ("normal_form", 0), ("rank_M", 0), ("polar_line", 0)]
    rows = parallel.ordered_map(exact_job, jobs, min_items=2)
    derivations, products, normal, rank, line = rows[:14], rows[14], rows[15], rows[16], rows[17]
    point = {"Q": normal["Q"], "G": normal["G"], "mu": normal["mu"], "cone": normal["cone"]}
    identities = {
        IDENTITIES[0]: all(derivations),
        IDENTITIES[1]: products,
        IDENTITIES[2]: normal["G"] == 0 and normal["Q"] != 0 and normal["mu"] != "0" and normal["cone"] == 0,
        IDENTITIES[3]: rank == 12,
        IDENTITIES[4]: line["in_kernel"] and line["z0_in_C"] and line["stack_rank"] == 12,
        IDENTITIES[5]: line["ranks"] == [8, 8, 8, 8, 8],
    }
    exact = {
        "rank_M_z0": rank,
        "stack_rank": line["stack_rank"],
        "dim_C": 15 - line["stack_rank"],
        "polar_line_ranks": line["ranks"],
    }
    return identities, point, exact


# --- the interval evaluation --------------------------------------------------------------------------------------


def _gaussian(entry: Any) -> acb:
    value = sp.expand(entry)
    real, imag = sp.Rational(sp.re(value)), sp.Rational(sp.im(value))
    return acb(arb(int(real.p)) / int(real.q), arb(int(imag.p)) / int(imag.q))


@functools.cache
def _pairing_factors() -> tuple[acb_mat, acb_mat]:
    """conjugate(z_0, c_2, c_3)^T (3 x 15) and the columns of l (15 x 2), exact balls."""
    ctx.prec = PRECISION
    _, line, basis = _exact()
    rows = [[_gaussian(sp.conjugate(entry)) for entry in vector] for vector in basis]
    columns = [[_gaussian(line[c][r]) for c in range(2)] for r in range(15)]
    return acb_mat(rows), acb_mat(columns)


@functools.cache
def _derivation_terms() -> tuple[tuple[tuple[int, int, int, int], ...], ...]:
    """The nonzero entries (row, column, numerator, denominator) of the 14 derivation matrices."""
    out = []
    for matrix in _derivations():
        terms = []
        for i in range(15):
            for j in range(15):
                if matrix[i, j] != 0:
                    value = sp.Rational(matrix[i, j])
                    terms.append((i, j, int(value.p), int(value.q)))
        out.append(tuple(terms))
    return tuple(out)


def _dyadic(numerator: int, bits: int) -> arb:
    return arb(numerator) / (1 << bits)


def _slice_point(midpoint: tuple[int, ...], radius_bits: int) -> list[arb]:
    """xi as balls: the dyadic constants, and the free coordinates with radius 2^-radius_bits (zero for 0)."""
    xi = [_dyadic(FIXED_NUMERATORS[i], FIXED_BITS) if i in FIXED_NUMERATORS else arb(0) for i in range(14)]
    for index, numerator in zip(SLICE_FREE, midpoint, strict=True):
        mid = _dyadic(numerator, MIDPOINT_BITS)
        xi[index] = arb(mid, _dyadic(1, radius_bits)) if radius_bits else mid
    return xi


def _block_matrix(xi: list[arb], k: int) -> acb_mat:
    """The 30 x 30 matrix [[2H, 2 i D_k], [0, 2H]] with H = i sum xi_j D_j."""
    entries = [[acb(0) for _ in range(30)] for _ in range(30)]
    for j, terms in enumerate(_derivation_terms()):
        for i, c, numerator, denominator in terms:
            value = acb(0, 2 * xi[j] * arb(numerator) / denominator)
            entries[i][c] += value
            entries[15 + i][15 + c] += value
    for i, c, numerator, denominator in _derivation_terms()[k]:
        entries[i][15 + c] += acb(0, 2 * arb(numerator) / denominator)
    return acb_mat(entries)


def _ser(x: arb) -> tuple[int, int, int, int]:
    mid, exponent = x.mid().man_exp()
    radius, radius_exponent = x.rad().man_exp()
    return int(mid), int(exponent), int(radius), int(radius_exponent)


def _de(t: tuple[int, int, int, int]) -> arb:
    mid = arb(t[0]) * arb(2) ** t[1]
    return arb(mid, arb(t[2]) * arb(2) ** t[3])


def _ser_matrix(matrix: acb_mat) -> list[tuple[int, int, int, int]]:
    return [_ser(matrix[a, b].real) for a in range(3) for b in range(2)] + [
        _ser(matrix[a, b].imag) for a in range(3) for b in range(2)
    ]


def _de_matrix(rows: list[tuple[int, int, int, int]]) -> acb_mat:
    return acb_mat([[acb(_de(rows[2 * a + b]), _de(rows[6 + 2 * a + b])) for b in range(2)] for a in range(3)])


def evaluation(job: tuple[int, tuple[int, ...], int]) -> tuple[list[Any], list[Any]]:
    """T = conjugate(Z)^T Pi l and its derivative along xi_k at the ball point of the job, serialized."""
    radius_bits, midpoint, k = job
    ctx.prec = PRECISION
    exponential = _block_matrix(_slice_point(midpoint, radius_bits), k).exp()
    pi = acb_mat([[exponential[a, b] for b in range(15)] for a in range(15)])
    derivative = acb_mat([[exponential[a, 15 + b] for b in range(15)] for a in range(15)])
    z, line = _pairing_factors()
    return _ser_matrix(z * pi * line), _ser_matrix(z * derivative * line)


def _equations(t: acb_mat, derivatives: list[acb_mat]) -> tuple[list[arb], list[list[arb]]]:
    """f = (Re F, Im F, Re det N, Im det N) and its Jacobian over the free coordinates from T and dT_k."""
    n = [[t[1, 0], t[1, 1]], [t[2, 0], t[2, 1]]]
    det = n[0][0] * n[1][1] - n[0][1] * n[1][0]
    f = [t[0, 0].real, t[0, 0].imag, t[0, 1].real, t[0, 1].imag, det.real, det.imag]
    columns = []
    for d in derivatives:
        dn = [[d[1, 0], d[1, 1]], [d[2, 0], d[2, 1]]]
        ddet = n[0][0] * dn[1][1] + dn[0][0] * n[1][1] - n[0][1] * dn[1][0] - dn[0][1] * n[1][0]
        columns.append([d[0, 0].real, d[0, 0].imag, d[0, 1].real, d[0, 1].imag, ddet.real, ddet.imag])
    return f, [[columns[c][r] for c in range(len(columns))] for r in range(6)]


def _largest_power(x: arb, below: bool, limit: int) -> int:
    """The largest e in 0..limit with x < 2^-e (below) or x > 2^e, certified by ball comparison; -1 when none."""
    best = -1
    for e in range(limit + 1):
        bound = arb(2) ** (-e if below else e)
        if (x < bound) if below else (x > bound):
            best = e
    return best


def krawczyk(midpoint: tuple[int, ...], radius_bits: int) -> dict[str, Any]:
    """The Krawczyk test of the box of the given midpoint and radius: containment, contraction bits, pairing bound."""
    ctx.prec = PRECISION
    jobs = [(0, midpoint, k) for k in SLICE_FREE] + [(radius_bits, midpoint, k) for k in SLICE_FREE]
    rows = parallel.ordered_map(evaluation, jobs, min_items=2)
    count = len(SLICE_FREE)
    point_t = _de_matrix(rows[0][0])
    box_t = _de_matrix(rows[count][0])
    f0, j0 = _equations(point_t, [_de_matrix(rows[k][1]) for k in range(count)])
    _, jx = _equations(box_t, [_de_matrix(rows[count + k][1]) for k in range(count)])
    inverse = arb_mat([[j0[a][b].mid() for b in range(count)] for a in range(count)]).inv().mid()
    radius = _dyadic(1, radius_bits)
    identity = arb_mat([[arb(1 if a == b else 0) for b in range(count)] for a in range(count)])
    offset = arb_mat([[arb(0, radius)] for _ in range(count)])
    image = -(inverse * arb_mat([[v] for v in f0])) + (identity - inverse * arb_mat(jx)) * offset
    interior = all(image[c, 0].lower() > -radius and image[c, 0].upper() < radius for c in range(count))
    worst = max((image[c, 0].abs_upper() for c in range(count)), key=lambda x: float(x.mid()))
    contraction = _largest_power(worst / radius, True, 200) if interior else 0
    entry = box_t[PAIRING_ENTRY[0] + 1, PAIRING_ENTRY[1]].abs_lower()
    return {
        "interior": bool(interior),
        "contraction_bits": contraction,
        "pairing_bound_bits": _largest_power(entry, False, 300),
    }


def double_precision_facts(midpoint: tuple[int, ...]) -> dict[str, Any]:
    """K(z), P, the ranks on P and dim L_z from their definitions at z = exp(H) z_0, at the midpoint in doubles."""
    xi = np.array([float(sp.Rational(FIXED_NUMERATORS.get(i, 0), 1 << FIXED_BITS)) for i in range(14)])
    for index, numerator in zip(SLICE_FREE, midpoint, strict=True):
        xi[index] = float(sp.Rational(numerator, 1 << MIDPOINT_BITS))
    matrices = np.array([np.array(m.tolist(), dtype=float) for m in _derivations()])
    values, vectors = np.linalg.eigh(1j * np.tensordot(xi, matrices, axes=1))
    theta = (vectors * np.exp(values)) @ vectors.conj().T
    z0 = np.array([complex(sp.N(entry, 30)) for entry in _exact()[0]])
    z = theta @ z0
    coordinates = tuple(repr(float(part)) for x in z for part in (x.real, x.imag))
    return real_line.witness_facts(coordinates)


# --- record -------------------------------------------------------------------------------------------------------


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def _slice_record() -> dict[str, Any]:
    return {
        "free": list(SLICE_FREE),
        "fixed_bits": FIXED_BITS,
        "fixed": {str(i): n for i, n in sorted(FIXED_NUMERATORS.items())},
        "midpoint_bits": MIDPOINT_BITS,
        "midpoint": list(MIDPOINT),
        "radius_bits": RADIUS_BITS,
    }


def compute() -> dict[str, Any]:
    identities, point, exact = exact_facts()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "point": point,
        "exact": exact,
        "slice": _slice_record(),
        "krawczyk": {"precision_bits": PRECISION, **krawczyk(MIDPOINT, RADIUS_BITS)},
        "double_precision": double_precision_facts(MIDPOINT),
        "claims": dict(CLAIMS),
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
        "point": dict(POINT_FACTS),
        "exact": copy.deepcopy(EXACT_FACTS),
        "slice": _slice_record(),
        "krawczyk": {
            "precision_bits": PRECISION,
            "interior": True,
            "contraction_bits": CONTRACTION_BITS,
            "pairing_bound_bits": PAIRING_BOUND_BITS,
        },
        "double_precision": dict(DOUBLE_FACTS),
        "claims": dict(CLAIMS),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity at the normal form fails",
        "point": "the normal-form point leaves V(G) minus V(Q) or has mu zero",
        "exact": "a rank at the normal form differs",
        "slice": "the slice or the box differs from the pinned constants",
        "krawczyk": "the Krawczyk operator does not map the box into its interior, or the pairing entry reaches zero",
        "double_precision": "the double-precision dimensions at the midpoint differ from 3, 2 and 2",
        "claims": "the stated claims differ",
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
    k = record["krawczyk"]
    bits = k["contraction_bits"]
    print(f"pass: {len(record['identities'])} identities, radius 2^-{RADIUS_BITS}, contraction 2^-{bits}")


if __name__ == "__main__":
    main()
