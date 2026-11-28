"""The symmetry pattern of the A_5 nullity base point at level A_6: G_2 and the character group (A5-259).

Claim tested (cd-tower report, C12): at A_6 the base-point structure repeats the A_5 pattern, a G_2 factor and a
(Z/2)^5 character group. The record separates the group that acts from the stabilizer of the point:

- derivations: dim Der(A_n) over Q for n = 2..6 with the cd_core product e_p e_q = cd_sign(2^n, p, q) e_(p xor q).
  Conjugation by a diagonal character carries D[r][s] to chi(r xor s) D[r][s], and each Leibniz equation for the
  pair (p, q) and output r involves only D[r][p xor q], D[r xor q][p], D[p xor r][q], whose index differences are all
  g = r xor p xor q. The system therefore splits into one block per g of 2^n unknowns, and each block rank is an
  exact python-flint fmpz_mat rank over Z. Nothing is computed modulo a prime;
- extension: the 14 rational derivations of A_3 (an exact rational null space) extended block-diagonally,
  D_n = diag(D_(n-1), D_(n-1)), satisfy the Leibniz rule of A_n at every basis pair (exact integers), so the extension
  is an injective Lie homomorphism g_2 = Der(A_3) -> Der(A_n), an isomorphism when dim Der(A_n) = 14;
- equivariance: C_(D z) = D C_z - C_z D for the Im-block kernel matrix C_z[a][b] = cd_sign(2^(n-1), a xor b, b)
  z_(a xor b) of A_(n-1) at n = 5 and n = 6, on every basis vector z (C_z is linear in z), so G_2 acts on the kernel
  coordinates; and C_(chi z) = D_chi C_z D_chi for every character chi_s(k) = (-1)^popcount(s AND k) of (Z/2)^(n-1);
- base point: the N- point z0 of the strata record (split coordinates strata_regularity.REPS["Nm"], original
  coordinates z_k = i^popcount(k) z'_k) at A_5, and two A_6 points in C^31: the lift (z0 in coordinates 1..15) and
  the real doubling (y, 0) of the A_5 point y = (Re z0, Im z0), whose coordinates are z_k = Re z0_k,
  z_(16+k) = Im z0_k. The prediction written before the run was nullity 32 for both A_6 points (doubling); the lift
  reads 36, the real doubling 32. The record computes the
  nullity of the real left multiplication L_y (y_k = Re z_k, y_(2^(n-1)+k) = Im z_k), the dimension over Q(i) of the
  stabilizer {D in g_2 : D z = 0} (SymPy Gaussian rationals), and the order of the stabilizer of z among the
  diagonal maps z_k -> epsilon chi_s(k) z_k, (s, epsilon) in (Z/2)^(n-1) x {+-1}.

Controls (--self-test; each baseline holds and its mutant fails): one negated table entry cd_sign(8, 1, 2) changes
dim Der(A_3) from 14; the extended derivations fail the Leibniz rule of A_6 when one of them has one entry changed;
a non-character sign map (one coordinate negated) breaks C_(chi z) = D_chi C_z D_chi. Tower control: dim Der(A_2) = 3
(the quaternions), so the value 14 is a property of n >= 3. No random draw enters.

Usage:
    "$PYTHON" -B -W error scripts/a5_a6_stabilizer.py --self-test
    "$PYTHON" -B -W error scripts/a5_a6_stabilizer.py --out docs/evidence/a5-a6-stabilizer/result.json
    "$PYTHON" -B -W error scripts/a5_a6_stabilizer.py --check docs/evidence/a5-a6-stabilizer/result.json
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import flint
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-strata-regularity"))

import strata_regularity as sr  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

LEVELS = (2, 3, 4, 5, 6)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@cache
def table(dim: int, flip: bool = False) -> tuple[tuple[int, ...], ...]:
    rows = [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]
    if flip:
        rows[1][2] = -rows[1][2]
    return tuple(tuple(r) for r in rows)


def block_rows(dim: int, g: int, flip: bool) -> list[list[int]]:
    """Leibniz equations of the block D[s xor g][s] = x_s, plus D e_0 = 0."""
    t = table(dim, flip)
    rows = []
    for p in range(dim):
        for q in range(dim):
            r = g ^ p ^ q
            row = [0] * dim
            row[p ^ q] += t[p][q]
            row[p] -= t[r ^ q][q]
            row[q] -= t[p][p ^ r]
            if any(row):
                rows.append(row)
    zero = [0] * dim
    zero[0] = 1
    rows.append(zero)
    return rows


def block_nullity(job: tuple[int, int, bool]) -> int:
    dim, g, flip = job
    rows = block_rows(dim, g, flip)
    return dim - int(flint.fmpz_mat(rows).rank())


def der_dim(n: int, flip: bool = False) -> dict[str, Any]:
    dim = 1 << n
    nul = parallel.ordered_map(block_nullity, [(dim, g, flip) for g in range(dim)], min_items=1)
    return {"n": n, "dim": sum(nul), "blocks": {str(g): k for g, k in enumerate(nul) if k}}


@cache
def octonion_derivations() -> list[list[list[Fraction]]]:
    """Exact rational basis of Der(A_3): the null space of the full Leibniz system over Q."""
    dim = 8
    t = table(dim)
    rows = []
    for p in range(dim):
        for q in range(dim):
            for r in range(dim):
                row = [0] * (dim * dim)
                row[r * dim + (p ^ q)] += t[p][q]
                row[(r ^ q) * dim + p] -= t[r ^ q][q]
                row[(p ^ r) * dim + q] -= t[p][p ^ r]
                rows.append(row)
    for r in range(dim):
        row = [0] * (dim * dim)
        row[r * dim] = 1
        rows.append(row)
    mat = flint.fmpq_mat(rows)
    rref, rank = mat.rref()
    ncols = dim * dim
    pivots = []
    for i in range(rank):
        for j in range(ncols):
            if rref[i, j] != 0:
                pivots.append(j)
                break
    free = [j for j in range(ncols) if j not in pivots]
    out = []
    for f in free:
        vec = [Fraction(0)] * ncols
        vec[f] = Fraction(1)
        for i, pj in enumerate(pivots):
            c = rref[i, f]
            vec[pj] = -Fraction(int(c.p), int(c.q))
        out.append([[vec[r * dim + s] for s in range(dim)] for r in range(dim)])
    return out


def extend(d: list[list[Fraction]], dim: int) -> list[list[Fraction]]:
    """Block-diagonal extension diag(D, D, ..., D) of an 8 x 8 derivation to dimension dim."""
    out = [[Fraction(0)] * dim for _ in range(dim)]
    for base in range(0, dim, 8):
        for r in range(8):
            for s in range(8):
                out[base + r][base + s] = d[r][s]
    return out


def leibniz_failures(d: list[list[Fraction]], dim: int) -> int:
    """Number of basis pairs (p, q) with D(e_p e_q) != D(e_p) e_q + e_p D(e_q) in A_n."""
    t = table(dim)
    bad = 0
    for p in range(dim):
        for q in range(dim):
            lhs = [Fraction(0)] * dim
            for r in range(dim):
                lhs[r] = t[p][q] * d[r][p ^ q]
            rhs = [Fraction(0)] * dim
            for j in range(dim):
                if d[j][p]:
                    rhs[j ^ q] += d[j][p] * t[j][q]
                if d[j][q]:
                    rhs[p ^ j] += d[j][q] * t[p][j]
            if lhs != rhs:
                bad += 1
    return bad


def kernel_matrix(half: int, z: list[Any]) -> list[list[Any]]:
    """C_z[a][b] = cd_sign(half, a xor b, b) z_(a xor b), a, b = 1..half-1, z indexed 1..half-1 (z[0] unused)."""
    out = []
    for a in range(1, half):
        row = []
        for b in range(1, half):
            k = a ^ b
            row.append(cd_sign(half, k, b) * z[k] if k else 0)
        out.append(row)
    return out


def equivariance_failures(ders: list[list[list[Fraction]]], half: int) -> int:
    """Basis vectors z = e_k and derivations D with C_(D z) != D C_z - C_z D on the Im block."""
    bad = 0
    for d in ders:
        dm = [[d[a][b] for b in range(1, half)] for a in range(1, half)]
        for k in range(1, half):
            z = [0] * half
            z[k] = 1
            dz = [Fraction(0)] + [d[a][k] for a in range(1, half)]
            lhs = kernel_matrix(half, dz)
            c = kernel_matrix(half, z)
            m = half - 1
            rhs = [
                [sum((dm[a][j] * c[j][b] - c[a][j] * dm[j][b] for j in range(m)), Fraction(0)) for b in range(m)]
                for a in range(m)
            ]
            if lhs != rhs:
                bad += 1
    return bad


def chi(s: int, k: int) -> int:
    return -1 if bin(s & k).count("1") % 2 else 1


def character_failures(half: int, broken: bool = False) -> int:
    """Characters s with C_(chi z) != D_chi C_z D_chi on some basis vector z; broken negates coordinate 1 only."""
    bad = 0
    for s in range(half):
        signs = [0] + [chi(s, k) for k in range(1, half)]
        if broken:
            signs = [0] + [-1 if k == 1 else 1 for k in range(1, half)]
        for k in range(1, half):
            z = [0] * half
            z[k] = 1
            cz = kernel_matrix(half, [signs[j] * z[j] for j in range(half)])
            c = kernel_matrix(half, z)
            m = half - 1
            if any(cz[a][b] != signs[a + 1] * c[a][b] * signs[b + 1] for a in range(m) for b in range(m)):
                bad += 1
                break
        if broken:
            break
    return bad


def base_point(half: int, mode: str) -> list[Any]:
    """z (index 1..half-1, z[0] unused) of the N- point.

    mode "lift": z0 placed in the coordinates 1..15 of C^(half-1); mode "real": the real doubling (y, 0) of the A_5
    point y = (Re z0, Im z0), whose complex coordinates in C^31 are z_k = Re z0_k and z_(16+k) = Im z0_k."""
    zp = sr.REPS["Nm"]
    units = [1, sp.I, -1, -sp.I]
    z0: list[Any] = [sp.Integer(0)] * 16
    for k in range(1, 16):
        z0[k] = units[bin(k).count("1") % 4] * zp[k - 1]
    z: list[Any] = [sp.Integer(0)] * half
    for k in range(1, 16):
        if mode == "lift":
            z[k] = z0[k]
        else:
            z[k] = sp.re(z0[k])
            z[16 + k] = sp.im(z0[k])
    return z


def point_facts(n: int, mode: str, ders: list[list[list[Fraction]]]) -> dict[str, Any]:
    half = 1 << (n - 1)
    z = base_point(half, mode)
    y = [Fraction(0)] * (2 * half)
    for k in range(1, half):
        re, im = sp.re(z[k]), sp.im(z[k])
        y[k] = Fraction(int(re))
        y[half + k] = Fraction(int(im))
    lm = left_mult_matrix_exact(2 * half, y)
    require(all(Fraction(x).denominator == 1 for r in lm for x in r), "L_y has a non-integer entry")
    rank = flint.fmpz_mat([[int(x) for x in r] for r in lm]).rank()
    vecs = []
    for d in ders:
        vecs.append(
            [
                sum((sp.Rational(d[a][b].numerator, d[a][b].denominator) * z[b] for b in range(1, half)), 0)
                for a in range(1, half)
            ]
        )
    orbit = sp.Matrix(vecs).rank()
    support = [k for k in range(1, half) if z[k] != 0]
    stab = [[s, eps] for s in range(half) for eps in (1, -1) if all(eps * chi(s, k) * z[k] == z[k] for k in support)]
    return {
        "n": n,
        "mode": mode,
        "support": support,
        "nullity": 2 * half - int(rank),
        "g2_orbit_rank": int(orbit),
        "g2_stabilizer_dim": len(ders) - int(orbit),
        "character_stabilizer": stab,
    }


def extension_job(job: tuple[str, int, int]) -> int:
    """One (check, derivation index, level) item: Leibniz failures at A_n or equivariance failures of C_z."""
    kind, i, n = job
    d = octonion_derivations()[i]
    if kind == "leibniz":
        return leibniz_failures(extend(d, 1 << n), 1 << n)
    half = 1 << (n - 1)
    return equivariance_failures([extend(d, half)], half)


def compute() -> dict[str, Any]:
    ders3 = octonion_derivations()
    dims = [der_dim(n) for n in LEVELS]
    jobs = [("leibniz", i, n) for n in (4, 5, 6) for i in range(len(ders3))]
    jobs += [("equivariance", i, n) for n in (5, 6) for i in range(len(ders3))]
    counts = parallel.ordered_map(extension_job, jobs, min_items=1)
    ext = {str(n): 0 for n in (4, 5, 6)}
    equiv = {str(n): 0 for n in (5, 6)}
    for (kind, _, n), c in zip(jobs, counts, strict=True):
        (ext if kind == "leibniz" else equiv)[str(n)] += c
    chars = {str(n): character_failures(1 << (n - 1)) for n in (5, 6)}
    points = [
        point_facts(n, mode, [extend(d, 1 << (n - 1)) for d in ders3])
        for n, mode in ((5, "lift"), (6, "lift"), (6, "real"))
    ]
    return {
        "derivation_dims": dims,
        "octonion_derivations": len(ders3),
        "extension_leibniz_failures": ext,
        "equivariance_failures": equiv,
        "character_failures": chars,
        "points": points,
    }


def validate(result: dict[str, Any]) -> None:
    dims = {r["n"]: r["dim"] for r in result["derivation_dims"]}
    require(dims == {2: 3, 3: 14, 4: 14, 5: 14, 6: 14}, f"derivation dimensions {dims}")
    require(result["octonion_derivations"] == 14, "Der(A_3) basis size")
    require(all(v == 0 for v in result["extension_leibniz_failures"].values()), "an extension fails Leibniz")
    require(all(v == 0 for v in result["equivariance_failures"].values()), "C_z is not G_2-equivariant")
    require(all(v == 0 for v in result["character_failures"].values()), "a character breaks C_z")
    a5, a6, real = result["points"]
    require((a5["nullity"], a6["nullity"], real["nullity"]) == (16, 36, 32), "nullities of the three points")
    require((a5["g2_stabilizer_dim"], a6["g2_stabilizer_dim"]) == (8, 8), "the G_2 stabilizer of the lift")
    require(real["g2_stabilizer_dim"] == 3, f"the G_2 stabilizer of the real doubling {real['g2_stabilizer_dim']}")
    klein = {(0, 1), (1, -1), (4, 1), (5, -1)}
    k5 = {tuple(x) for x in a5["character_stabilizer"]}
    k6 = {tuple(x) for x in a6["character_stabilizer"]}
    kr = {tuple(x) for x in real["character_stabilizer"]}
    require(k5 == klein, f"A_5 character stabilizer {sorted(k5)}")
    require(k6 == klein | {(s ^ 16, e) for s, e in klein}, f"A_6 lift character stabilizer {sorted(k6)}")
    require(len(kr) == 8 and klein <= kr, f"A_6 real-doubling character stabilizer {sorted(kr)}")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    control(der_dim(3)["dim"] == 14, der_dim(3, flip=True)["dim"] == 14, "Der(A_3) under one negated sign")
    ders3 = octonion_derivations()
    good = extend(ders3[0], 64)
    bad = [list(r) for r in good]
    j = next(c for c in range(64) if bad[1][c] == 0 and c != 1)
    bad[1][j] = Fraction(1)
    control(leibniz_failures(good, 64) == 0, leibniz_failures(bad, 64) == 0, "Leibniz of an extension at A_6")
    control(character_failures(32) == 0, character_failures(32, broken=True) == 0, "a non-character sign map")


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
