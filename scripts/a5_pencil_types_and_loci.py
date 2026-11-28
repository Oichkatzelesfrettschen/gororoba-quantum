"""Types and loci of the A_5 compression pencils: the census of W8 types, the normal form of the type rule, the VB
rank-4 locus, the order-by-order arc limits at e_1 + e_10 and the full Pfaffians at VB and N+-.

Claim. (1) The full Pfaffian of the pencil, with the coordinate on e_16, is irreducible over Q at VB (degree 6) and at
N- and N+ (degree 8). (2) Every point y = (p, q) of W8 built from a census pair of sedenion zero divisors has pencil
type R, C or H as dim (ker L_p n ker L_q) is 0, 2 or 4 (all pairs with dim 2 and 4, and a deterministic sample with
dim 0). (3) In the normal form a = (t, kt), b = (alpha t, (alpha k) t) of the proof of Theorem 14.6 of Biss, Dugger and
Isaksen, the operator J_k (+L_k on the H part of each octonion slot, -L_k on its complement) preserves the kernel,
squares to -I there and commutes with all 31 compressions, and the kernel splits into an Omega x Omega part that does
not depend on alpha and a complementary part that moves when alpha leaves <1, k>. (4) At the VB point the real
directions of compression rank at most 4 form the 4-plane m = 0, lead Q = 0, lead G = 0, where the rank is exactly 4
off the origin, and on the lines along the rank-4 directions among the unit sums the second-order Schur form vanishes
exactly when the line has nullity 8. (5) At e_1 + e_10 the second-order and third-order Schur terms of arcs with zero
first-order compression lie in the 7-dimensional pencil span.

Arithmetic. Integer and rational matrices (python-flint fmpz_mat, fmpq_mat), integer polynomial rings (fmpz_mpoly), and
one Singular standard basis over Q in the degree reverse lexicographic ordering for the VB ideal; no random draw enters.
The pencil type of a point uses the two-sided bounds of a5_pencil_certificates.structure_item and, where its integer
frame exceeds that script's int64 bound, the rational sympy route of a5_nullity_transitions.structure_item. The replay
commands are in docs/evidence/a5-nullity-transitions/README.md ("Replay").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpq_mat, fmpz_mat, fmpz_mpoly_ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "hardware-orbits"))

import a5_pencil_certificates as certificates  # noqa: E402

import cd_core  # noqa: E402
import parallel  # noqa: E402

SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/parallel.py",
    "scripts/a5_pencil_certificates.py",
    "scripts/a5_nullity_transitions.py",
    "scripts/a5_zero_divisor_strata.py",
    "docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py",
    "scripts/a5_pencil_types_and_loci.py",
)
SAMPLE_MODULUS = 1171
"""A dim-0 census pair (i, j) enters the type census when (131 i + j) is divisible by this modulus."""
CENSUS_CHUNKS = 64
ALPHAS: dict[str, tuple[int, ...]] = {
    "2": (2, 0, 0, 0, 0, 0, 0, 0),
    "2k": (0, 0, 0, 2, 0, 0, 0, 0),
    "2i": (0, 2, 0, 0, 0, 0, 0, 0),
    "1+i": (1, 1, 0, 0, 0, 0, 0, 0),
    "i+k": (0, 1, 0, 1, 0, 0, 0, 0),
    "1+i+j+k": (1, 1, 1, 1, 0, 0, 0, 0),
    "3+2j": (3, 0, 2, 0, 0, 0, 0, 0),
}
VB_PLANE = (9, 10, 13, 14)
VB_OFF_PLANE = (3, 4, 11, 12, 16)
SINGULAR = "Singular"
FAILED_PREDICTIONS: set[str] = set()
PREDICTIONS = {
    "P27": "at N- and N+ the full Pfaffian of the 19-dimensional pencil, with the coordinate on e_16, is irreducible "
    "over Q and of degree 8",
    "P28": "every point y = (p, q) of A_5 built from a census pair of sedenion zero divisors that lies in W8 has "
    "pencil type R, C or H as dim (ker L_p n ker L_q) is 0, 2 or 4",
    "P29": "in the normal form of Theorem 14.6 of Biss, Dugger and Isaksen the operator J_k preserves the kernel, "
    "squares to -I there and commutes with all 31 compressions at alpha = 2, 2k (dim A = 4) and alpha = 2i, 1 + i, "
    "i + k (dim A = 2)",
    "P30": "at VB the real points of compression rank at most 4 are exactly m = 0, lead Q = 0 and lead G = 0",
    "P31": "for a line VB + s w whose compression has rank 4, the second-order form on its kernel vanishes exactly on "
    "the directions whose line has nullity 8",
    "P32": "at e_1 + e_10 the second-order form -K^T L_w L_0^+ L_w K of every w in the kernel of the compression map "
    "lies in the pencil span, checked through its polarization on every pair of a basis of that kernel",
    "P33": "at e_1 + e_10 the symmetrized mixed terms with one zero-space direction and the symmetrized cubic terms "
    "over the zero space lie in the pencil span",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def to_int(matrix: np.ndarray) -> list[list[int]]:
    return [[int(x) for x in row] for row in matrix]


def full_pfaffian_item(name: str) -> dict[str, Any]:
    """The Pfaffian of the pencil on all its basis units, the coordinate on e_16 included, and its factorization."""
    size, _gram, forms, units = certificates.pencil_frame(name)
    terms = certificates.pfaffian_terms(size, forms, units)
    constant, factors = fmpz_mpoly_ctx.get(("x", len(units)), "lex").from_dict(terms).factor()
    return {
        "point": name,
        "units": units,
        "terms": len(terms),
        "degree": max(sum(m) for m in terms),
        "content": str(constant),
        "factor_degrees": sorted([int(f.total_degree()), int(m)] for f, m in factors),
    }


def census_chunk(job: tuple[int, tuple[tuple[int, ...], ...]]) -> list[tuple[int, int, int]]:
    """(i, j, dim A) for the census pairs of rows i = chunk mod CENSUS_CHUNKS with dim A = 2 or 4, or dim A = 0 and
    131 i + j divisible by SAMPLE_MODULUS."""
    chunk, points = job
    table = certificates.sign_table(16)
    matrices = [certificates.left(16, table, dict(enumerate(v))) for v in points]
    out: list[tuple[int, int, int]] = []
    for i in range(chunk, len(points), CENSUS_CHUNKS):
        for j in range(i + 1, len(points), certificates.CENSUS_STRIDE):
            dim = 16 - int(fmpz_mat(to_int(np.vstack([matrices[i], matrices[j]]))).rank())
            if dim or (131 * i + j) % SAMPLE_MODULUS == 0:
                out.append((i, j, dim))
    return out


def type_item(job: tuple[int, tuple[int, ...], tuple[int, ...]]) -> dict[str, Any]:
    """Orbit of y = (p, q) and, on W8, the pencil type with matched bounds."""
    import hardware_orbits

    dim, p, q = job
    vector = {k: Fraction(v) for k, v in enumerate(p) if v}
    vector.update({16 + k: Fraction(v) for k, v in enumerate(q) if v})
    row = hardware_orbits.classify(vector)
    if row.get("orbit") != "W8":
        return {"dim": dim, "orbit": str(row.get("orbit")), "nullity": int(row["nullity"])}
    base = tuple(sorted((k, int(v)) for k, v in vector.items()))
    try:
        s = certificates.structure_item((32, base))
        commutant = (s["commutant_lower"], s["commutant_upper"])
        closure = (s["closure_lower"], s["closure_upper"])
        route = "bounds"
    except ValueError:
        import a5_nullity_transitions

        old = a5_nullity_transitions.structure_item((32, base))
        commutant = (old["commutant_dimension"], old["commutant_dimension"])
        closure = (old["lie_closure_dimension"], old["lie_closure_dimension"])
        route = "sympy"
    return {
        "dim": dim,
        "orbit": "W8",
        "nullity": 8,
        "commutant": list(commutant),
        "closure": list(closure),
        "route": route,
    }


def type_census() -> dict[str, Any]:
    points = tuple(certificates.sedenion_zero_divisors())
    pairs = [
        pair
        for part in parallel.ordered_map(census_chunk, [(c, points) for c in range(CENSUS_CHUNKS)], 1)
        for pair in part
    ]
    pairs.sort()
    rows = parallel.ordered_map(type_item, [(d, points[i], points[j]) for i, j, d in pairs], 1)
    tally: Counter[str] = Counter()
    for row in rows:
        if row["orbit"] == "W8":
            tally[f"dim {row['dim']}, W8, commutant {row['commutant']}, closure {row['closure']}, {row['route']}"] += 1
        else:
            tally[f"dim {row['dim']}, {row['orbit']}, nullity {row['nullity']}"] += 1
    sample = [(i, j) for i, j, d in pairs if d == 0]
    return {
        "pairs_by_dim": {str(d): sum(1 for *_, e in pairs if e == d) for d in (0, 2, 4)},
        "dim0_distinct_p": len({i for i, _ in sample}),
        "dim0_distinct_q": len({j for _, j in sample}),
        "tally": dict(sorted(tally.items())),
    }


def octonion_product(x: tuple[int, ...] | list[int], y: tuple[int, ...] | list[int]) -> list[int]:
    return [int(v) for v in cd_core.cd_multiply_exact(8, list(x), list(y))]


def unit8(index: int) -> list[int]:
    return [int(i == index) for i in range(8)]


def normal_form_item(job: tuple[str, int]) -> dict[str, Any]:
    """J_k on y = (t, kt, alpha t, (alpha k) t) with t = e_4 and k = e_3; job = (alpha, sign of J_k on the H^perp part),
    where sign +1 is the mutant of the self-test."""
    name, perp_sign = job
    alpha = ALPHAS[name]
    t, k = unit8(4), unit8(3)
    y = t + octonion_product(k, t) + octonion_product(alpha, t) + octonion_product(octonion_product(alpha, k), t)
    table = certificates.sign_table(32)
    space, size = fmpz_mat(to_int(certificates.left(32, table, {i: v for i, v in enumerate(y) if v}))).nullspace()
    frame = np.array([[int(space[i, j]) for j in range(size)] for i in range(32)], dtype=np.int64)
    lk = np.array([[octonion_product(k, unit8(c))[row] for c in range(8)] for row in range(8)], dtype=np.int64)
    h_part = np.diag([1, 1, 1, 1, 0, 0, 0, 0]).astype(np.int64)
    slot = lk @ h_part + perp_sign * lk @ (np.eye(8, dtype=np.int64) - h_part)
    j_full = np.kron(np.eye(4, dtype=np.int64), slot)
    preserves = int(fmpz_mat(to_int(np.hstack([frame, j_full @ frame]))).rank()) == size
    kq = fmpq_mat(to_int(frame))
    inverse = (kq.transpose() * kq).inv()
    jk = inverse * kq.transpose() * fmpq_mat(to_int(j_full @ frame))
    identity = fmpq_mat(size, size, [int(i == j) for i in range(size) for j in range(size)])
    compressions = [
        inverse * kq.transpose() * fmpq_mat(to_int(certificates.left(32, table, {w: 1}))) * kq for w in range(1, 32)
    ]
    table16 = certificates.sign_table(16)
    halves = [
        certificates.left(16, table16, {i: v for i, v in enumerate(y[16 * h : 16 * h + 16]) if v}) for h in (0, 1)
    ]
    omega = [s * 8 + c for s in range(4) for c in range(4)]
    perp = [s * 8 + c for s in range(4) for c in range(4, 8)]
    omega_part, perp_part = frame.copy(), frame.copy()
    omega_part[perp, :] = 0
    perp_part[omega, :] = 0
    return {
        "alpha": name,
        "kernel": int(size),
        "dim_a": 16 - int(fmpz_mat(to_int(np.vstack(halves))).rank()),
        "preserves_kernel": bool(preserves),
        "square_is_minus_identity": bool(preserves and jk * jk == -identity),
        "commutes_with_all_31": bool(preserves and all(jk * m == m * jk for m in compressions)),
        "kernel_splits": int(fmpz_mat(to_int(np.hstack([omega_part, perp_part]))).rank()) == size,
        "omega_part": to_int(omega_part[omega]),
        "perp_part": to_int(perp_part[perp]),
    }


def same_span(first: list[list[int]], second: list[list[int]]) -> bool:
    a, b = fmpz_mat(first), fmpz_mat(second)
    return (
        int(a.rank()) == int(b.rank()) == int(fmpz_mat([r1 + r2 for r1, r2 in zip(first, second, strict=True)]).rank())
    )


def vb_singular(_: int) -> dict[str, Any]:
    """The 6x6 sub-Pfaffians of the VB pencil (rank at most 4) and powers of m, x3^2 + x4^2 and x11^2 + x12^2 in their
    ideal, by one Singular standard basis over Q in dp."""
    size, _gram, forms, units = certificates.pencil_frame("VB")
    names = [f"x{w}" for w in units]

    def text(terms: dict[tuple[int, ...], int]) -> str:
        parts = []
        for mono, c in sorted(terms.items()):
            monomial = "*".join(f"{names[i]}^{e}" for i, e in enumerate(mono) if e)
            parts.append(f"({c})" + (f"*{monomial}" if monomial else ""))
        return "+".join(parts)

    pfaffians = []
    plane_vanish = True
    plane_index = [units.index(u) for u in VB_PLANE]
    for subset in combinations(range(size), 6):
        terms = certificates.pfaffian_terms(6, {w: forms[w][list(subset)][:, list(subset)] for w in units}, units)
        if terms:
            pfaffians.append(text(terms))
            plane_vanish = plane_vanish and all(any(e for i, e in enumerate(m) if i not in plane_index) for m in terms)
    script = "\n".join(
        [
            f"ring R = 0, ({','.join(names)}), dp;",
            "ideal I = " + ",\n".join(pfaffians) + ";",
            "ideal S = std(I);",
            "int e; poly f;",
            "list targets = x16, x3^2 + x4^2, x11^2 + x12^2;",
            "for (int t = 1; t <= 3; t++) { for (e = 1; e <= 4; e++) { f = targets[t]^e;"
            ' if (reduce(f, S) == 0) { print("member " + string(t) + " " + string(e)); break; } } }',
            'print("dim " + string(dim(S)));',
            "quit;",
        ]
    )
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "vb.sing"
        path.write_text(script, encoding="utf-8")
        output = subprocess.run(
            [SINGULAR, "-q", str(path)], capture_output=True, text=True, check=True, timeout=1800
        ).stdout
    members = {line.split()[1]: int(line.split()[2]) for line in output.splitlines() if line.startswith("member")}
    dimension = next(int(line.split()[1]) for line in output.splitlines() if line.startswith("dim"))
    return {
        "sub_pfaffians": len(pfaffians),
        "all_vanish_on_plane": bool(plane_vanish),
        "power_in_ideal": {
            "m": members.get("1", 0),
            "x3^2+x4^2": members.get("2", 0),
            "x11^2+x12^2": members.get("3", 0),
        },
        "ideal_dimension": dimension,
    }


def vb_plane_rank(_: int) -> dict[str, Any]:
    """The 4x4 sub-Pfaffians of the pencil restricted to the plane coordinates; two of them are -4 (x9^2 + x14^2) and
    4 (x10^2 + x13^2), so the rank is at least 4 off the origin."""
    size, _gram, forms, _units = certificates.pencil_frame("VB")
    found = set()
    for subset in combinations(range(size), 4):
        terms = certificates.pfaffian_terms(
            4, {w: forms[w][list(subset)][:, list(subset)] for w in VB_PLANE}, list(VB_PLANE)
        )
        found.add(tuple(sorted(terms.items())))
    sums = {
        "x9^2+x14^2": ((((0, 0, 0, 2), -4), ((2, 0, 0, 0), -4))),
        "x10^2+x13^2": ((((0, 0, 2, 0), 4), ((0, 2, 0, 0), 4))),
    }
    return {"distinct_sub_pfaffians": len(found), "sums_of_squares_present": {k: v in found for k, v in sums.items()}}


def vb_line_item(direction: tuple[tuple[int, int], ...]) -> list[Any] | None:
    """For a unit sum w whose compression has rank 4 and lies in the plane: the rank of the second-order form on the
    kernel of the compression and the nullity of VB + s w at s = 2 and 3."""
    table = certificates.sign_table(32)
    base = dict(certificates.STRATA["VB"])
    size, _gram, forms, units = certificates.pencil_frame("VB")
    w = dict(direction)
    compression = sum((v * forms[u] for u, v in w.items()), np.zeros((size, size), np.int64))
    if int(fmpz_mat(to_int(compression)).rank()) != 4:
        return None
    basis = fmpq_mat(
        [[int(forms[u].ravel()[i]) for u in units] + [int(compression.ravel()[i])] for i in range(size * size)]
    )
    reduced, rank = basis.rref()
    coordinates = {}
    for row in range(rank):
        pivot = next(c for c in range(basis.ncols()) if reduced[row, c] != 0)
        coordinates[units[pivot]] = reduced[row, basis.ncols() - 1]
    if any(v != 0 for u, v in coordinates.items() if u not in VB_PLANE):
        return None
    l0 = fmpq_mat(to_int(certificates.left(32, table, base)))
    space, k = fmpz_mat(to_int(certificates.left(32, table, base))).nullspace()
    frame = fmpq_mat(32, k, [space[i, j] for i in range(32) for j in range(k)])
    pinv = (l0.transpose() * l0 + frame * (frame.transpose() * frame).inv() * frame.transpose()).inv() * l0.transpose()
    l1 = fmpq_mat(to_int(certificates.left(32, table, w)))
    null, n = fmpz_mat(to_int(compression)).nullspace()
    nm = fmpq_mat(k, n, [null[i, j] for i in range(k) for j in range(n)])
    second = nm.transpose() * frame.transpose() * l1 * pinv * l1 * frame * nm
    nullities = []
    for s in (2, 3):
        y = dict(base)
        for u, v in w.items():
            y[u] = y.get(u, 0) + s * v
        nullities.append(32 - int(fmpz_mat(to_int(certificates.left(32, table, y))).rank()))
    return [sorted(w.items()), int(second.rank()), nullities]


def vb_lines() -> dict[str, Any]:
    directions: list[tuple[tuple[int, int], ...]] = [((u, 1),) for u in range(1, 32)]
    directions += [((a, 1), (b, sign)) for a, b in combinations(range(1, 32), 2) for sign in (1, -1)]
    rows = [row for row in parallel.ordered_map(vb_line_item, directions, 1) if row is not None]
    tally = Counter(f"second-order rank {row[1]}, nullity {row[2]}" for row in rows)
    return {"plane_rank4_directions": len(rows), "tally": dict(sorted(tally.items()))}


def w8_schur_item(job: tuple[str, int]) -> dict[str, int]:
    """At e_1 + e_10: the polarized second-order terms (job "quadratic"), the mixed terms (job "mixed") or the
    symmetrized cubic terms (job "cubic") over the zero space of the compression map, block = job[1] of 8 blocks,
    and the count that lies outside the pencil span; job "identity" replaces L_0^+ by the identity (the self-test
    mutant)."""
    kind, block = job
    table = certificates.sign_table(32)
    l0z = certificates.left(32, table, {1: 1, 10: 1})
    l0 = fmpq_mat(to_int(l0z))
    space, k = fmpz_mat(to_int(l0z)).nullspace()
    frame = fmpq_mat(32, k, [space[i, j] for i in range(32) for j in range(k)])
    pinv = (l0.transpose() * l0 + frame * (frame.transpose() * frame).inv() * frame.transpose()).inv() * l0.transpose()
    if kind == "identity":
        pinv = fmpq_mat(32, 32, [int(i == j) for i in range(32) for j in range(32)])
    units = {w: fmpq_mat(to_int(certificates.left(32, table, {w: 1}))) for w in range(1, 32)}
    forms = {w: frame.transpose() * units[w] * frame for w in range(1, 32)}
    columns = fmpz_mat([[int(forms[w][i, j]) for w in range(1, 32)] for i in range(k) for j in range(k)])
    zero, dimension = columns.nullspace()
    zero_ops = []
    for c in range(dimension):
        op = fmpq_mat(32, 32)
        for i in range(31):
            if zero[i, c] != 0:
                op += units[i + 1] * int(zero[i, c])
        zero_ops.append(op)
    pencil_rows = [[forms[w][i, j] for i in range(k) for j in range(k)] for w in range(1, 32)]
    pencil_rank = int(fmpq_mat(pencil_rows).rank())

    def outside(matrix: fmpq_mat) -> int:
        rows = [*pencil_rows, [matrix[i, j] for i in range(k) for j in range(k)]]
        return int(int(fmpq_mat(rows).rank()) != pencil_rank)

    if kind in ("quadratic", "identity"):
        jobs = [p for n, p in enumerate(combinations_with_replacement(range(dimension), 2)) if n % 8 == block]
        terms = [
            frame.transpose() * (zero_ops[a] * pinv * zero_ops[b] + zero_ops[b] * pinv * zero_ops[a]) * frame
            for a, b in jobs
        ]
    elif kind == "mixed":
        jobs2 = [
            (a, b) for n, (a, b) in enumerate((a, b) for a in range(dimension) for b in range(1, 32)) if n % 8 == block
        ]
        terms = [
            frame.transpose() * (zero_ops[a] * pinv * units[b] + units[b] * pinv * zero_ops[a]) * frame
            for a, b in jobs2
        ]
    else:
        jobs3 = [t for n, t in enumerate(combinations_with_replacement(range(dimension), 3)) if n % 8 == block]
        terms = []
        for triple in jobs3:
            total = fmpq_mat(k, k)
            for x, y, z in set(permutations(triple)):
                total += frame.transpose() * zero_ops[x] * pinv * zero_ops[y] * pinv * zero_ops[z] * frame
            terms.append(total)
    return {
        "zero_space": dimension,
        "pencil_rank": pencil_rank,
        "terms": len(terms),
        "outside": sum(outside(m) for m in terms),
    }


def w8_schur() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for kind in ("quadratic", "mixed", "cubic"):
        rows = parallel.ordered_map(w8_schur_item, [(kind, b) for b in range(8)], 1)
        out[kind] = {"terms": sum(r["terms"] for r in rows), "outside": sum(r["outside"] for r in rows)}
        out["zero_space"], out["pencil_rank"] = rows[0]["zero_space"], rows[0]["pencil_rank"]
    return out


def type_of(row: dict[str, Any]) -> str:
    names = {(1, 28): "R", (2, 15): "C", (4, 10): "H"}
    lower, upper = row["commutant"]
    closure_lower, closure_upper = row["closure"]
    if lower != upper or closure_lower != closure_upper:
        return "unresolved"
    return names.get((lower, closure_lower), "other")


def build_normal_form() -> dict[str, Any]:
    rows = parallel.ordered_map(normal_form_item, [(name, -1) for name in ALPHAS], 1)
    reference_omega, reference_perp = rows[0]["omega_part"], rows[0]["perp_part"]
    for row in rows:
        row["omega_part_same_as_alpha_2"] = same_span(row.pop("omega_part"), reference_omega)
        row["perp_part_same_as_alpha_2"] = same_span(row.pop("perp_part"), reference_perp)
    return {row["alpha"]: row for row in rows}


def outcomes(result: dict[str, Any]) -> dict[str, bool]:
    full = {row["point"]: row for row in result["full_pfaffians"]}
    census = result["type_census"]["tally"]
    w8_types = [(int(key.split(",")[0].split()[1]), key) for key in census if ", W8," in key]
    lines = result["vb_lines"]["tally"]
    w8 = result["w8_schur"]
    singular = result["vb_singular"]
    normal = result["normal_form"]
    return {
        "P27": all(full[n]["factor_degrees"] == [[8, 1]] for n in ("N-", "N+")),
        "P28": bool(w8_types) and all(census_type_matches(dim, key) for dim, key in w8_types),
        "P29": all(
            normal[a]["preserves_kernel"]
            and normal[a]["square_is_minus_identity"]
            and normal[a]["commutes_with_all_31"]
            for a in ("2", "2k", "2i", "1+i", "i+k")
        ),
        "P30": singular["all_vanish_on_plane"] and all(v > 0 for v in singular["power_in_ideal"].values()),
        "P31": all(("rank 0" in key) == ("[8, 8]" in key) for key in lines),
        "P32": w8["quadratic"]["outside"] == 0,
        "P33": w8["mixed"]["outside"] == 0 and w8["cubic"]["outside"] == 0,
    }


def census_type_matches(dim: int, key: str) -> bool:
    commutant = key.split("commutant ")[1].split("]")[0] + "]"
    closure = key.split("closure ")[1].split("]")[0] + "]"
    row = {"commutant": json.loads(commutant), "closure": json.loads(closure)}
    return type_of(row) == {0: "R", 2: "C", 4: "H"}[dim]


def validate(result: dict[str, Any]) -> None:
    full = {row["point"]: row for row in result["full_pfaffians"]}
    require(
        full["VB"]["terms"] == 50 and full["VB"]["degree"] == 6 and full["VB"]["factor_degrees"] == [[6, 1]],
        "VB: the full Pfaffian is an irreducible sextic with 50 terms",
    )
    for name in ("N-", "N+"):
        row = full[name]
        require(len(row["units"]) == 19 and 16 in row["units"], f"{name}: 19 units, e_16 among them")
        require(
            row["terms"] == 12579 and row["degree"] == 8 and row["factor_degrees"] == [[8, 1]],
            f"{name}: the full Pfaffian is an irreducible octic with 12,579 terms",
        )
    census = result["type_census"]
    require(census["pairs_by_dim"]["2"] == 4268 and census["pairs_by_dim"]["4"] == 417, "every dim-2 and dim-4 pair")
    require(census["pairs_by_dim"]["0"] > 2000, "a dim-0 sample of more than 2,000 pairs")
    require(census["dim0_distinct_p"] > 1000 and census["dim0_distinct_q"] > 1000, "the dim-0 sample spreads")
    w8 = [key for key in census["tally"] if ", W8," in key]
    require(
        all(census_type_matches(int(key.split(",")[0].split()[1]), key) for key in w8), "every W8 type follows dim A"
    )
    require({int(key.split(",")[0].split()[1]) for key in w8} == {0, 2, 4}, "W8 points of every dim A")
    for key in census["tally"]:
        if ", W8," not in key:
            require(not key.endswith("nullity 8") or key.startswith("dim 0"), "nullity 8 with dim A > 0 lies in W8")
    normal = result["normal_form"]
    for name, row in normal.items():
        require(row["kernel"] == 8 and row["kernel_splits"], f"alpha {name}: kernel 8, split into the two parts")
        require(
            row["preserves_kernel"] and row["square_is_minus_identity"] and row["commutes_with_all_31"],
            f"alpha {name}: J_k is a complex structure commuting with the pencil",
        )
        require(row["omega_part_same_as_alpha_2"], f"alpha {name}: the Omega part does not depend on alpha")
        four = name in ("2", "2k")
        require(row["dim_a"] == (4 if four else 2), f"alpha {name}: dim A {4 if four else 2}")
        require(row["perp_part_same_as_alpha_2"] == four, f"alpha {name}: the complementary part moves iff dim A = 2")
    singular = result["vb_singular"]
    require(
        singular["sub_pfaffians"] == 768 and singular["all_vanish_on_plane"],
        "VB: 768 sub-Pfaffians vanish on the plane",
    )
    require(all(v > 0 for v in singular["power_in_ideal"].values()), "VB: m, x3^2 + x4^2, x11^2 + x12^2 in the radical")
    require(all(result["vb_plane_rank"]["sums_of_squares_present"].values()), "VB: rank at least 4 off the origin")
    lines = result["vb_lines"]
    require(lines["plane_rank4_directions"] == 284, "VB: 284 unit-sum directions of rank 4 in the plane")
    require(
        lines["tally"]
        == {
            "second-order rank 0, nullity [8, 8]": 100,
            "second-order rank 4, nullity [0, 0]": 88,
            "second-order rank 4, nullity [4, 4]": 96,
        },
        "VB: the second-order form vanishes exactly on the nullity-8 lines",
    )
    w8s = result["w8_schur"]
    require(w8s["zero_space"] == 24 and w8s["pencil_rank"] == 7, "e_1 + e_10: zero space 24, pencil 7")
    require(
        (w8s["quadratic"]["terms"], w8s["mixed"]["terms"], w8s["cubic"]["terms"]) == (300, 744, 2600),
        "e_1 + e_10: 300 quadratic, 744 mixed and 2,600 cubic terms",
    )
    require(
        w8s["quadratic"]["outside"] == w8s["mixed"]["outside"] == w8s["cubic"]["outside"] == 0,
        "e_1 + e_10: every term lies in the pencil span",
    )
    held = outcomes(result)
    require(set(held) == set(PREDICTIONS), "every prediction has an outcome")
    require({k for k, v in held.items() if not v} == FAILED_PREDICTIONS, "the failed predictions are the recorded ones")
    require(result["predictions"] == PREDICTIONS and result["prediction_held"] == held, "predictions stored")


def build_result() -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "a5-pencil-types-and-loci/1",
        "full_pfaffians": parallel.ordered_map(full_pfaffian_item, ["VB", "N-", "N+"], 1),
        "type_census": type_census(),
        "normal_form": build_normal_form(),
        "vb_singular": vb_singular(0),
        "vb_plane_rank": vb_plane_rank(0),
        "vb_lines": vb_lines(),
        "w8_schur": w8_schur(),
        "predictions": PREDICTIONS,
    }
    result["prediction_held"] = outcomes(result)
    validate(result)
    return result


def self_test() -> list[str]:
    passed: list[str] = []

    def control(name: str, baseline: bool, mutant_fails: bool) -> None:
        require(baseline, f"{name}: holds on the record's input")
        require(mutant_fails, f"{name}: fails on the mutant")
        passed.append(name)

    control(
        "J_k commutes with the pencil, and the operator +L_k on the whole slot does not",
        normal_form_item(("2i", -1))["commutes_with_all_31"],
        not normal_form_item(("2i", 1))["commutes_with_all_31"],
    )
    real = w8_schur_item(("quadratic", 0))
    control(
        "second-order terms lie in the pencil, and with L_0^+ replaced by the identity they leave it",
        real["outside"] == 0 and real["terms"] > 0,
        w8_schur_item(("identity", 0))["outside"] > 0,
    )
    on_plane = vb_line_item(((1, 1), (10, 1)))
    control(
        "e1 + e10 has rank-4 compression in the plane and zero second-order form; e3 + e9 is off the plane",
        on_plane is not None and on_plane[1] == 0 and on_plane[2] == [8, 8],
        vb_line_item(((3, 1), (9, 1))) is None,
    )
    restricted = certificates.strata_item(("VB", False))["pfaffian_factor_degrees"]
    control(
        "the full VB Pfaffian is irreducible, its doubly pure restriction is not",
        full_pfaffian_item("VB")["factor_degrees"] == [[6, 1]],
        restricted != [[6, 1]],
    )
    h_point = type_item((4, (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0), (0,) * 16))
    r_point = type_item((0, (0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1) + (0,) * 11))
    control(
        "e1 + e10 reads type H and e1 + e10 + e3 + e20 type R",
        h_point["orbit"] == "W8" and type_of(h_point) == "H",
        r_point["orbit"] == "W8" and type_of(r_point) != "H",
    )
    return passed


def source_digests() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the record")
    mode.add_argument("--check", type=Path, help="recompute and compare with a written record")
    mode.add_argument("--self-test", action="store_true", help="run the mutation controls")
    arguments = parser.parse_args()
    if arguments.self_test:
        names = self_test()
        print(f"self-test passed: {len(names)} controls")
        return 0
    result = build_result()
    result["sources"] = source_digests()
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if arguments.out:
        arguments.out.write_text(text, encoding="utf-8")
        return 0
    require(arguments.check.read_text(encoding="utf-8") == text, "the record differs from its recomputation")
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
