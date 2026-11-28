"""Derivations of the exceptional Jordan algebra J_3(O) over Q and its stabilizers, under the cd_core octonion product.

The octonion product is e_p e_q = s(p, q) e_(p ^ q) with s = gororoba_quantum.cd_core.cd_sign(8, p, q). J_3(O) is the
space of 3 x 3 octonion-Hermitian matrices with the Jordan product (XY + YX) / 2; the equations use XY + YX, which has
integer structure constants and the same derivations. A derivation is a square matrix D with D(e_a) = sum_b D[b][a] e_b
and D(xy) = D(x) y + x D(y) on every pair of basis vectors; its space is the kernel of that linear system, an exact
rank over Z (python-flint fmpz_mat).

This record checks, exactly over Q:

- the product of cd_core on the 64 basis pairs equals the structure constants used here;
- dim Der(O) = 14 (the algebra G_2) and dim Der(J_3(O)) = 52, the dimension of F_4;
- the entrywise action of Der(O) on J_3(O) lies inside Der(J_3(O)) (zero residual, stacked rank 52);
- the stabilizer in Der(J_3(O)) of J_3(R) (the three diagonal idempotents and the real unit of each off-diagonal
  pair) has dimension 14 and equals the entrywise G_2 (stacked rank 14);
- the stabilizer of J_3(C_e2), C_e2 = span(1, e_2), has dimension 8 and equals the entrywise su(3) = Stab_(G_2)(e_2)
  (stacked rank 8), the algebra that A5-619 identifies with the covariance algebra of the A_5 slice of A5-615;
- the stabilizer of E1 has dimension 36 and that of E1, E2, E3 dimension 28.

Controls: a zero product, three octonion tables with one anticommuting sign pair negated, a vector that is not a
derivation, and the stabilizer of J_3(C_e3) stacked with the su(3) of e_2 and with the su(3) of e_3. No random
draw enters.
"""

from __future__ import annotations

import argparse
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

from flint import fmpz_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

MUTATED_PAIRS = ((1, 2), (1, 4), (3, 5))
Sign = list[list[int]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def octonion_sign() -> Sign:
    table = [[cd_core.cd_sign(8, p, q) for q in range(8)] for p in range(8)]
    mismatches = 0
    for p in range(8):
        for q in range(8):
            a = [0] * 8
            b = [0] * 8
            a[p] = 1
            b[q] = 1
            mine = [0] * 8
            mine[p ^ q] = table[p][q]
            mismatches += [int(x) for x in cd_core.cd_multiply_exact(8, a, b)] != mine
    require(mismatches == 0, f"cd_sign differs from cd_multiply_exact at {mismatches} basis pairs")
    return table


def make_division(sign: Sign, d: int):
    def mul(a: list[int], b: list[int]) -> list[int]:
        out = [0] * d
        for p in range(d):
            if a[p]:
                for q in range(d):
                    if b[q]:
                        out[p ^ q] += sign[p][q] * a[p] * b[q]
        return out

    def conj(a: list[int]) -> list[int]:
        return [a[0]] + [-x for x in a[1:]]

    return mul, conj


def vec(d: int, idx: int) -> list[int]:
    v = [0] * d
    v[idx] = 1
    return v


class Alg:
    """Finite algebra given by integer structure constants mult[i][j] = {k: c}."""

    def __init__(self, n: int, mult: list[list[dict[int, int]]], commutative: bool) -> None:
        self.n = n
        self.mult = mult
        self.commutative = commutative


def octonion_algebra(sign: Sign) -> Alg:
    mul, _ = make_division(sign, 8)
    mult = [[{k: c for k, c in enumerate(mul(vec(8, i), vec(8, j))) if c} for j in range(8)] for i in range(8)]
    return Alg(8, mult, False)


def jordan_algebra(sign: Sign, d: int):
    """J_3(A) for A of dimension d (1 or 8): E1..E3, then A_t(e_a) over the slot pairs (0,1), (1,2), (2,0)."""
    mul, conj = make_division(sign, d)
    pairs = [(0, 1), (1, 2), (2, 0)]
    n = 3 + 3 * d

    def to_mat(idx: int) -> list[list[list[int]]]:
        m = [[[0] * d for _ in range(3)] for _ in range(3)]
        if idx < 3:
            m[idx][idx][0] = 1
        else:
            t, a = divmod(idx - 3, d)
            i, j = pairs[t]
            m[i][j] = vec(d, a)
            m[j][i] = conj(vec(d, a))
        return m

    def mat_mul(x, y):
        z = [[[0] * d for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                acc = [0] * d
                for k in range(3):
                    acc = [u + v for u, v in zip(acc, mul(x[i][k], y[k][j]), strict=True)]
                z[i][j] = acc
        return z

    def from_mat(z) -> dict[int, int]:
        out = {}
        for i in range(3):
            require(all(x == 0 for x in z[i][i][1:]), "diagonal entry not real")
            if z[i][i][0]:
                out[i] = z[i][i][0]
        for t, (i, j) in enumerate(pairs):
            require(z[j][i] == conj(z[i][j]), "result not Hermitian")
            for a in range(d):
                if z[i][j][a]:
                    out[3 + t * d + a] = z[i][j][a]
        return out

    mats = [to_mat(i) for i in range(n)]
    mult: list[list[dict[int, int]]] = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            a = mat_mul(mats[i], mats[j])
            b = mat_mul(mats[j], mats[i])
            s = [[[u + v for u, v in zip(a[r][c], b[r][c], strict=True)] for c in range(3)] for r in range(3)]
            mult[i][j] = mult[j][i] = from_mat(s)
    return Alg(n, mult, True), (mats, from_mat)


def der_system(alg: Alg) -> list[dict[int, int]]:
    """Rows of D(e_i e_j) - D(e_i) e_j - e_i D(e_j) = 0 in the unknowns D[b][a] (index b * n + a)."""
    n = alg.n
    rows: list[dict[int, int]] = []
    for i in range(n):
        for j in range(i if alg.commutative else 0, n):
            eq: list[dict[int, int]] = [{} for _ in range(n)]
            for k, ck in alg.mult[i][j].items():
                for c in range(n):
                    eq[c][c * n + k] = eq[c].get(c * n + k, 0) + ck
            for b in range(n):
                for c, cc in alg.mult[b][j].items():
                    eq[c][b * n + i] = eq[c].get(b * n + i, 0) - cc
            for b in range(n):
                for c, cc in alg.mult[i][b].items():
                    eq[c][b * n + j] = eq[c].get(b * n + j, 0) - cc
            rows.extend(row for row in ({u: v for u, v in e.items() if v} for e in eq) if row)
    return rows


def to_fmpz(rows: list[dict[int, int]], ncols: int) -> fmpz_mat:
    m = fmpz_mat(max(len(rows), 1), ncols)
    for r, row in enumerate(rows):
        for u, v in row.items():
            m[r, u] = v
    return m


def derivations(alg: Alg) -> tuple[int, list[list[int]], int, int]:
    """(dimension, kernel basis as integer lists of length n * n, rank, row count)."""
    n = alg.n
    rows = der_system(alg)
    m = to_fmpz(rows, n * n)
    rk = m.rank()
    x, nullity = m.nullspace()
    require(nullity == n * n - rk, "nullspace dimension differs from n^2 - rank")
    return n * n - rk, [[int(x[r, c]) for r in range(n * n)] for c in range(nullity)], rk, len(rows)


def rank_of(vectors: list[list[int]]) -> int:
    if not vectors:
        return 0
    m = fmpz_mat(len(vectors), len(vectors[0]))
    for r, v in enumerate(vectors):
        for c, x in enumerate(v):
            m[r, c] = x
    return m.rank()


def column(values: list[int]) -> fmpz_mat:
    col = fmpz_mat(len(values), 1)
    for k, x in enumerate(values):
        col[k, 0] = x
    return col


def nonzero_entries(m: fmpz_mat, vector: list[int]) -> int:
    return sum(1 for x in (m * column(vector)).entries() if x != 0)


def mutated_sign(sign: Sign, a: int, b: int) -> Sign:
    out = [row[:] for row in sign]
    out[a][b] = -out[a][b]
    out[b][a] = -out[b][a]
    return out


@cache
def baseline() -> dict[str, Any]:
    """Der(O), Der(J_3(R)), Der(J_3(O)) and their bases for the cd_core product."""
    sign = octonion_sign()
    d_o, b_o, rk_o, rows_o = derivations(octonion_algebra(sign))
    j1, _ = jordan_algebra([[1]], 1)
    d_j1, _, rk_j1, rows_j1 = derivations(j1)
    j8, ctx = jordan_algebra(sign, 8)
    d_j8, b_j8, rk_j8, rows_j8 = derivations(j8)
    return {
        "sign": sign,
        "O": (d_o, b_o, rk_o, rows_o),
        "J1": (d_j1, rk_j1, rows_j1),
        "J8": (d_j8, b_j8, rk_j8, rows_j8),
        "j8": j8,
        "ctx": ctx,
    }


def mutant_dims(pair: tuple[int, int]) -> dict[str, int]:
    """Derivation dimensions of O and J_3(O) with the sign of one basis pair (and its reverse) negated."""
    s = mutated_sign(octonion_sign(), *pair)
    return {
        "dim_Der_O": derivations(octonion_algebra(s))[0],
        "dim_Der_J3_O": derivations(jordan_algebra(s, 8)[0])[0],
    }


def compute() -> dict[str, Any]:
    base = baseline()
    d_o, b_o, rk_o, rows_o = base["O"]
    d_j1, rk_j1, rows_j1 = base["J1"]
    d_j8, b_j8, rk_j8, rows_j8 = base["J8"]
    sign, j8 = base["sign"], base["j8"]
    mats, from_mat = base["ctx"]
    n8, nj = 8, j8.n
    res: dict[str, Any] = {"schema": "a5-albert-derivation-stabilizers/1", "basis_pairs_checked": 64}
    res["Der_O"] = {"dim": d_o, "rank": rk_o, "rows": rows_o}
    res["Der_J3_R"] = {"dim": d_j1, "rank": rk_j1, "rows": rows_j1}
    res["Der_J3_O"] = {"dim": d_j8, "rank": rk_j8, "rows": rows_j8, "unknowns": nj * nj}
    res["zero_product_dim_Der"] = derivations(Alg(8, [[{} for _ in range(8)] for _ in range(8)], False))[0]
    pairs = list(MUTATED_PAIRS)
    dims = parallel.ordered_map(mutant_dims, pairs, min_items=1)
    res["mutants"] = {f"{a},{b}": d for (a, b), d in zip(pairs, dims, strict=True)}

    def act_on_j(dvec_flat: list[int]) -> list[int]:
        """Entrywise action of a derivation of O on each basis element of J_3(O), as a flat nj x nj matrix."""
        dm = [[dvec_flat[b * n8 + a] for a in range(n8)] for b in range(n8)]
        flat = [0] * (nj * nj)
        for a_idx in range(nj):
            m = mats[a_idx]
            z = [
                [[sum(dm[b][a] * m[i][j][a] for a in range(n8)) for b in range(n8)] for j in range(3)] for i in range(3)
            ]
            for b_idx, c in from_mat(z).items():
                flat[b_idx * nj + a_idx] = c
        return flat

    m_o = to_fmpz(der_system(octonion_algebra(sign)), 64)
    require(all(nonzero_entries(m_o, v) == 0 for v in b_o), "a Der(O) basis vector fails the O system")
    m_j = to_fmpz(der_system(j8), nj * nj)
    g2_j = [act_on_j(v) for v in b_o]
    res["G2_in_Der_J3_O"] = {
        "rank_G2_images": rank_of(g2_j),
        "rank_Der_J3_O": rank_of(b_j8),
        "rank_stacked": rank_of(b_j8 + g2_j),
        "nonzero_residual_entries": sum(nonzero_entries(m_j, v) for v in g2_j),
    }
    bad = [0] * (nj * nj)
    bad[0 * nj + 3] = 1
    res["control_non_derivation"] = {
        "rank_stacked": rank_of(b_j8 + [bad]),
        "nonzero_residual_entries": nonzero_entries(m_j, bad),
    }

    def su3_of(e: int) -> tuple[int, int, list[list[int]]]:
        """Stabilizer of e_e in Der(O): (rank of D -> D(e_e), dimension, entrywise images in J_3(O))."""
        m = fmpz_mat(8, len(b_o))
        for c, v in enumerate(b_o):
            for b in range(8):
                m[b, c] = v[b * 8 + e]
        x, nul = m.nullspace()
        vs = []
        for c in range(nul):
            coeffs = [int(x[r, c]) for r in range(len(b_o))]
            vs.append([sum(coeffs[r] * b_o[r][k] for r in range(len(b_o))) for k in range(64)])
        return m.rank(), nul, [act_on_j(v) for v in vs]

    rk_img, dim_su3, su3_e2 = su3_of(2)
    res["su3"] = {"rank_D_to_De2": rk_img, "dim_stab_e2_in_Der_O": dim_su3, "rank_su3_images": rank_of(su3_e2)}

    def stab(indices: list[int]) -> tuple[int, list[list[int]]]:
        """Derivations of J_3(O) that vanish on the basis elements with these indices."""
        m = fmpz_mat(nj * len(indices), len(b_j8))
        for c, v in enumerate(b_j8):
            for t, a_idx in enumerate(indices):
                for b in range(nj):
                    m[t * nj + b, c] = v[b * nj + a_idx]
        x, nul = m.nullspace()
        out = []
        for c in range(nul):
            coeffs = [int(x[r, c]) for r in range(len(b_j8))]
            out.append([sum(coeffs[r] * b_j8[r][k] for r in range(len(b_j8))) for k in range(nj * nj)])
        require(rank_of(out) == nul, "stabilizer basis rank differs from its nullity")
        return nul, out

    def off(t: int, a: int) -> int:
        return 3 + t * 8 + a

    jr = [0, 1, 2] + [off(t, 0) for t in range(3)]

    def jc(e: int) -> list[int]:
        return jr + [off(t, e) for t in range(3)]

    d_r, s_r = stab(jr)
    res["stab_J3_R"] = {"indices": jr, "dim": d_r, "rank_with_entrywise_G2": rank_of(s_r + g2_j)}
    d2, s2 = stab(jc(2))
    res["stab_J3_C_e2"] = {"indices": jc(2), "dim": d2, "rank_with_entrywise_su3_e2": rank_of(s2 + su3_e2)}
    d3, s3 = stab(jc(3))
    _, dim_su3_e3, su3_e3 = su3_of(3)
    res["control_stab_J3_C_e3"] = {
        "dim": d3,
        "rank_with_entrywise_su3_e2": rank_of(s3 + su3_e2),
        "rank_with_entrywise_su3_e3": rank_of(s3 + su3_e3),
        "dim_su3_e3": dim_su3_e3,
    }
    res["stab_E1"] = stab([0])[0]
    res["stab_E1_E2_E3"] = stab([0, 1, 2])[0]
    return res


EXPECTED: dict[str, Any] = {
    "basis_pairs_checked": 64,
    "Der_O": {"dim": 14, "rank": 50, "rows": 512},
    "Der_J3_R": {"dim": 3, "rank": 33, "rows": 117},
    "Der_J3_O": {"dim": 52, "rank": 677, "rows": 9063, "unknowns": 729},
    "zero_product_dim_Der": 64,
    "mutants": {k: {"dim_Der_O": 4, "dim_Der_J3_O": 7} for k in ("1,2", "1,4", "3,5")},
    "G2_in_Der_J3_O": {"rank_G2_images": 14, "rank_Der_J3_O": 52, "rank_stacked": 52, "nonzero_residual_entries": 0},
    "control_non_derivation": {"rank_stacked": 53, "nonzero_residual_entries": 26},
    "su3": {"rank_D_to_De2": 6, "dim_stab_e2_in_Der_O": 8, "rank_su3_images": 8},
    "stab_J3_R": {"dim": 14, "rank_with_entrywise_G2": 14},
    "stab_J3_C_e2": {"dim": 8, "rank_with_entrywise_su3_e2": 8},
    "control_stab_J3_C_e3": {
        "dim": 8,
        "rank_with_entrywise_su3_e2": 13,
        "rank_with_entrywise_su3_e3": 8,
        "dim_su3_e3": 8,
    },
    "stab_E1": 36,
    "stab_E1_E2_E3": 28,
}


def validate(result: dict[str, Any]) -> None:
    for key, want in EXPECTED.items():
        got = result[key]
        if isinstance(want, dict):
            got = {k: got[k] for k in want}
        require(got == want, f"{key}: {got} differs from {want}")


def self_test() -> None:
    def control(baseline_ok: bool, mutant_ok: bool, name: str) -> None:
        require(baseline_ok and not mutant_ok, f"control {name}: baseline {baseline_ok}, mutant {mutant_ok}")

    r = compute()
    mutant = r["mutants"]["1,2"]
    control(r["Der_O"]["dim"] == 14, mutant["dim_Der_O"] == 14, "one negated octonion sign pair, Der(O)")
    control(r["Der_J3_O"]["dim"] == 52, mutant["dim_Der_J3_O"] == 52, "one negated octonion sign pair, Der(J_3(O))")
    full = r["Der_J3_O"]["dim"]
    control(
        r["G2_in_Der_J3_O"]["rank_stacked"] == full,
        r["control_non_derivation"]["rank_stacked"] == full,
        "a vector that is not a derivation",
    )
    e3 = r["control_stab_J3_C_e3"]
    control(
        r["stab_J3_C_e2"]["rank_with_entrywise_su3_e2"] == r["stab_J3_C_e2"]["dim"],
        e3["rank_with_entrywise_su3_e2"] == e3["dim"],
        "su(3) of e_2 against the stabilizer of J_3(C_e3)",
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
        print("self-test: 4 paired controls pass")
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
