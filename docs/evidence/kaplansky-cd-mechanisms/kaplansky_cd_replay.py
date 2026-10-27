"""Exact checks of the Kaplansky-type mechanisms inside the Cayley-Dickson algebras of cd_core.

The Cayley-Dickson algebra of dimension D = 2^k is the twisted group algebra R^sigma[Z_2^k] with
e_p e_q = cd_sign(D, p, q) e_(p xor q). The replay fixes, on that sign table alone:

- Fano incidence. The seven lines {i, j, fano_completion(i, j)} of the octonion table meet pairwise in one
  point, so their incidence Gram matrix is the all-ones matrix modulo 2 (the q = 2 instance of the odd
  line-intersection condition of the projective planes over F_q, q even). Their complements are the seven
  nontrivial cosets of the order-4 subgroups of Z_2^3, the index sets of O minus a quaternion subalgebra; they
  have four elements each and meet pairwise in two.
- Two-blade zero products. (e_i + t e_j)(e_k + s e_l), with i, j, k, l distinct and nonzero and t, s = +-1,
  vanishes only on the XOR skeleton i xor j = k xor l, and there exactly when the cocycle cross-ratio
  chi = sigma(i, k) sigma(j, l) sigma(i, l) sigma(j, k) equals +1, with two sign choices (t, s). A brute-force
  search over every disjoint pair of pairs finds no other zero product. chi is unchanged by every single-index
  re-signing e_a -> -e_a, and single flips generate every re-signing.
- Twisted squares. e_m^2 = -1 for every m != 0, so the torsion zero divisor (1 - g)(1 + g) of the untwisted
  algebra R[Z_2^k] has no twisted analog, and the sign row of L_(e_m) is affine over F_2 (a signed Pauli
  string) only at D = 4.
- Annihilators. For every two-blade zero divisor a at D = 16 and D = 32, the kernel of L_a consists of pure
  elements, each annihilated by right multiplication by a as well.
- Inverse and zero divisor. a = e_1 + e_10 has the zero-divisor partner b = e_4 - e_15 and two distinct
  two-sided inverses, -a / 2 and -a / 2 + b (b lies in ker L_a = ker R_a), so a^(-1) (a b) = 0 while
  (a^(-1) a) b = b.
- Qubit reading. Every normalized two-blade zero divisor (e_i + t e_j) / sqrt(2), on the little-endian index
  register, is an eigenstate of X^m, m = i xor j, with eigenvalue t, and every qubit in the support of m has a
  zero single-qubit Bloch vector because |m| >= 2.
- Squares of left multiplication. For two-unit pure u at D = 16, L_u^2 is the scalar -|u|^2 exactly when u is
  not a zero divisor; the invertible three-unit element e_1 + e_2 + e_12 has a non-scalar L_u^2.

result.json records the counts; --check recomputes them and compares the bytes.

Usage: "$PYTHON" docs/evidence/kaplansky-cd-mechanisms/kaplansky_cd_replay.py [--check]
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact, cd_sign, fano_completion, left_mult_determinant_exact  # noqa: E402
from parallel import ordered_map  # noqa: E402

BUNDLE = Path(__file__).resolve().parent
RESULT = BUNDLE / "result.json"
SKELETON_DIMENSIONS = (8, 16, 32)
AFFINE_DIMENSIONS = (4, 8, 16, 32)
KERNEL_DIMENSIONS = (16, 32)
SQUARE_DIMENSION = 16

Table = list[list[int]]


def sign_table(dim: int) -> Table:
    return [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]


def fano_facts() -> dict[str, Any]:
    lines = sorted({tuple(sorted((i, j, fano_completion(i, j)))) for i, j in itertools.combinations(range(1, 8), 2)})
    if len(lines) != 7 or any(a ^ b != c for a, b, c in lines):
        raise SystemExit(f"kaplansky-cd: Fano lines are not the seven XOR triples: {lines}")
    meets = Counter(len(set(x) & set(y)) for x, y in itertools.combinations(lines, 2))
    complements = [tuple(sorted(set(range(1, 8)) - set(line))) for line in lines]
    complement_meets = Counter(len(set(x) & set(y)) for x, y in itertools.combinations(complements, 2))
    point_cover = Counter(sum(p in c for c in complements) for p in range(1, 8))
    pair_cover = Counter(sum(p in c and r in c for c in complements) for p, r in itertools.combinations(range(1, 8), 2))
    coset = True
    for line, comp in zip(lines, complements, strict=True):
        subgroup = (0, *line)
        x = comp[0]
        if sorted(x ^ h for h in subgroup) != list(comp):
            coset = False
    return {
        "lines": [list(line) for line in lines],
        "line_intersection_sizes": dict(sorted(meets.items())),
        "incidence_gram_mod_2_all_ones": set(meets) == {1} and all(len(line) % 2 == 1 for line in lines),
        "complements": [list(c) for c in complements],
        "complement_intersection_sizes": dict(sorted(complement_meets.items())),
        "complements_per_point": dict(sorted(point_cover.items())),
        "complements_per_point_pair": dict(sorted(pair_cover.items())),
        "complements_are_nontrivial_subgroup_cosets": coset,
    }


def _skeleton_rows(job: tuple[int, int]) -> list[tuple[int, int, int, int, int, int]]:
    """Rows (i, j, k, l, chi, lifts) for one first pair (i, j) on the XOR skeleton of dimension dim."""
    dim, i = job
    table = sign_table(dim)
    rows = []
    for j in range(i + 1, dim):
        m = i ^ j
        for k in range(1, dim):
            el = k ^ m
            if k >= el or len({i, j, k, el}) != 4:
                continue
            chi = table[i][k] * table[j][el] * table[i][el] * table[j][k]
            lifts = sum(
                1
                for t in (1, -1)
                for s in (1, -1)
                if table[i][k] + t * s * table[j][el] == 0 and s * table[i][el] + t * table[j][k] == 0
            )
            rows.append((i, j, k, el, chi, lifts))
    return rows


def _off_skeleton_zero_products(job: tuple[int, int]) -> int:
    """Zero products (e_i + t e_j)(e_k + s e_l) with i xor j != k xor l, for one first index i."""
    dim, i = job
    table = sign_table(dim)
    found = 0
    for j in range(i + 1, dim):
        for k, el in itertools.combinations(range(1, dim), 2):
            if len({i, j, k, el}) != 4 or i ^ j == k ^ el:
                continue
            for t in (1, -1):
                for s in (1, -1):
                    product: Counter[int] = Counter()
                    product[i ^ k] += table[i][k]
                    product[i ^ el] += s * table[i][el]
                    product[j ^ k] += t * table[j][k]
                    product[j ^ el] += t * s * table[j][el]
                    if not any(product.values()):
                        found += 1
    return found


def skeleton_facts(dim: int) -> dict[str, Any]:
    rows = [row for group in ordered_map(_skeleton_rows, [(dim, i) for i in range(1, dim)]) for row in group]
    off = sum(ordered_map(_off_skeleton_zero_products, [(dim, i) for i in range(1, dim)]))
    if any(lifts != (2 if chi == 1 else 0) for *_, chi, lifts in rows):
        raise SystemExit(f"kaplansky-cd: chi does not predict the sign lift at D = {dim}")
    table = sign_table(dim)
    invariant = True
    for a in range(1, dim):
        f = [-1 if x == a else 1 for x in range(dim)]
        for i, j, k, el, chi, _ in rows:
            resigned = 1
            for p, q in ((i, k), (j, el), (i, el), (j, k)):
                resigned *= f[p] * f[q] * f[p ^ q] * table[p][q]
            if resigned != chi:
                invariant = False
    lifted = [(i, j, k, el) for i, j, k, el, chi, _ in rows if chi == 1]
    by_m = Counter(i ^ j for i, j, _, _ in lifted)
    weights = Counter(bin(i ^ j).count("1") for i, j, _, _ in lifted)
    pairs = {(i, j) for i, j, _, _ in lifted} | {(k, el) for _, _, k, el in lifted}
    return {
        "skeleton_ordered_pairs_of_index_pairs": len(rows),
        "chi_plus_one": len(lifted),
        "signed_zero_products_on_skeleton": 2 * len(lifted),
        "zero_products_off_skeleton": off,
        "chi_invariant_under_single_index_resigning": invariant,
        "zero_divisor_index_pairs": len(pairs),
        "two_blade_zero_divisor_elements": 2 * len(pairs),
        "chi_plus_one_by_m": {str(m): n for m, n in sorted(by_m.items())},
        "chi_plus_one_by_weight_of_m": {str(w): n for w, n in sorted(weights.items())},
        "min_weight_of_m": min(weights) if weights else None,
    }


def affine_rows(dim: int) -> int:
    bits = dim.bit_length() - 1
    count = 0
    for m in range(1, dim):
        f = [0 if cd_sign(dim, m, x) == 1 else 1 for x in range(dim)]
        lin = [f[1 << b] ^ f[0] for b in range(bits)]
        if all(f[x] == f[0] ^ (sum(lin[b] for b in range(bits) if x >> b & 1) & 1) for x in range(dim)):
            count += 1
    return count


def _pure_kernel_annihilated(job: tuple[int, int, int, int]) -> tuple[int, bool]:
    """Exact kernel of L_a for a = e_i + t e_j: (nullity, every kernel vector pure and right-annihilated)."""
    dim, i, j, t = job
    a: list[Fraction] = [Fraction(0)] * dim
    a[i], a[j] = Fraction(1), Fraction(t)
    columns = []
    for c in range(dim):
        e: list[Fraction] = [Fraction(0)] * dim
        e[c] = Fraction(1)
        columns.append(cd_multiply_exact(dim, a, e))
    m = [[columns[c][r] for c in range(dim)] for r in range(dim)]
    pivots: list[int] = []
    r = 0
    for c in range(dim):
        p = next((x for x in range(r, dim) if m[x][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inv = 1 / m[r][c]
        m[r] = [v * inv for v in m[r]]
        for x in range(dim):
            if x != r and m[x][c] != 0:
                factor = m[x][c]
                m[x] = [v - factor * w for v, w in zip(m[x], m[r], strict=True)]
        pivots.append(c)
        r += 1
    ok = True
    free = [c for c in range(dim) if c not in pivots]
    for fc in free:
        z: list[Fraction] = [Fraction(0)] * dim
        z[fc] = Fraction(1)
        for row, pc in enumerate(pivots):
            z[pc] = -m[row][fc]
        if z[0] != 0 or any(cd_multiply_exact(dim, a, z)) or any(cd_multiply_exact(dim, z, a)):
            ok = False
    return len(free), ok


def kernel_facts(dim: int, pairs: list[tuple[int, int, int]]) -> dict[str, Any]:
    results = ordered_map(_pure_kernel_annihilated, [(dim, i, j, t) for i, j, t in pairs])
    return {
        "elements": len(results),
        "nullities": {str(n): c for n, c in sorted(Counter(n for n, _ in results).items())},
        "kernel_pure_and_right_annihilated": all(ok for _, ok in results),
    }


def zero_divisor_elements(dim: int) -> list[tuple[int, int, int]]:
    table = sign_table(dim)
    out = set()
    for i, j in itertools.combinations(range(1, dim), 2):
        m = i ^ j
        for k in range(1, dim):
            el = k ^ m
            if k < el and len({i, j, k, el}) == 4 and table[i][k] * table[j][el] * table[i][el] * table[j][k] == 1:
                out.add((i, j, 1))
                out.add((i, j, -1))
                break
    return sorted(out)


def qubit_facts(dim: int, elements: list[tuple[int, int, int]]) -> dict[str, Any]:
    bits = dim.bit_length() - 1
    eigen = True
    zero_bloch = 0
    supported = 0
    for i, j, t in elements:
        m = i ^ j
        # X^m |i> = |j>, so X^m (|i> + t |j>) = |j> + t |i> = t (|i> + t |j>).
        if (i ^ m, j ^ m) != (j, i):
            eigen = False
        for b in range(bits):
            if not m >> b & 1:
                continue
            supported += 1
            z = Fraction((1 if not i >> b & 1 else -1) + (1 if not j >> b & 1 else -1), 2)
            x = Fraction(t) if m == 1 << b else Fraction(0)
            if z == 0 and x == 0:
                zero_bloch += 1
    return {
        "x_string_eigenstates": eigen,
        "support_qubits": supported,
        "support_qubits_with_zero_bloch_vector": zero_bloch,
    }


def square_facts() -> dict[str, Any]:
    dim = SQUARE_DIMENSION
    table = sign_table(dim)
    zd = {(i, j) for i, j, _ in zero_divisor_elements(dim)}

    def left(u: dict[int, int]) -> list[list[int]]:
        mat = [[0] * dim for _ in range(dim)]
        for p, c in u.items():
            for x in range(dim):
                mat[p ^ x][x] += c * table[p][x]
        return mat

    def scalar_square(u: dict[int, int]) -> bool:
        mat = left(u)
        sq = [[sum(mat[r][k] * mat[k][c] for k in range(dim)) for c in range(dim)] for r in range(dim)]
        norm = sum(c * c for c in u.values())
        return all(sq[r][c] == (-norm if r == c else 0) for r in range(dim) for c in range(dim))

    scalar: Counter[tuple[str, bool]] = Counter()
    for i, j in itertools.combinations(range(1, dim), 2):
        scalar[("zero divisor" if (i, j) in zd else "invertible", scalar_square({i: 1, j: 1}))] += 1
    witness = [Fraction(0)] * dim
    for p in (1, 2, 12):
        witness[p] = Fraction(1)
    return {
        "two_unit_invertible_scalar_square": scalar[("invertible", True)],
        "two_unit_invertible_nonscalar_square": scalar[("invertible", False)],
        "two_unit_zero_divisor_scalar_square": scalar[("zero divisor", True)],
        "two_unit_zero_divisor_nonscalar_square": scalar[("zero divisor", False)],
        "e1_e2_e12_determinant": str(left_mult_determinant_exact(dim, witness)),
        "e1_e2_e12_scalar_square": scalar_square({1: 1, 2: 1, 12: 1}),
    }


def inverse_witness() -> dict[str, Any]:
    dim = 16

    def vec(terms: dict[int, Fraction]) -> list[Fraction]:
        v = [Fraction(0)] * dim
        for p, c in terms.items():
            v[p] = c
        return v

    def show(v: Sequence[Fraction]) -> dict[str, str]:
        return {f"e{p}": str(c) for p, c in enumerate(v) if c}

    a = vec({1: Fraction(1), 10: Fraction(1)})
    b = vec({4: Fraction(1), 15: Fraction(-1)})
    a_inv = vec({1: Fraction(-1, 2), 10: Fraction(-1, 2)})
    second = [x + y for x, y in zip(a_inv, b, strict=True)]
    return {
        "a": show(a),
        "b": show(b),
        "a_inverse": show(a_inv),
        "a_times_b": show(cd_multiply_exact(dim, a, b)),
        "a_inverse_times_a": show(cd_multiply_exact(dim, a_inv, a)),
        "a_times_a_inverse": show(cd_multiply_exact(dim, a, a_inv)),
        "a_inverse_times_a_b": show(cd_multiply_exact(dim, a_inv, cd_multiply_exact(dim, a, b))),
        "a_inverse_a_times_b": show(cd_multiply_exact(dim, cd_multiply_exact(dim, a_inv, a), b)),
        "second_inverse": show(second),
        "second_inverse_times_a": show(cd_multiply_exact(dim, second, a)),
        "a_times_second_inverse": show(cd_multiply_exact(dim, a, second)),
    }


def derivation() -> dict[str, Any]:
    skeleton = {str(d): skeleton_facts(d) for d in SKELETON_DIMENSIONS}
    elements = {d: zero_divisor_elements(d) for d in KERNEL_DIMENSIONS}
    result: dict[str, Any] = {
        "schema": "kaplansky-cd-mechanisms-v1",
        "fano": fano_facts(),
        "skeleton": skeleton,
        "units_square_to_minus_one": {
            str(d): all(cd_sign(d, m, m) == -1 for m in range(1, d)) for d in SKELETON_DIMENSIONS
        },
        "affine_sign_rows": {str(d): {"affine": affine_rows(d), "rows": d - 1} for d in AFFINE_DIMENSIONS},
        "annihilators": {str(d): kernel_facts(d, elements[d]) for d in KERNEL_DIMENSIONS},
        "qubit_reading": {str(d): qubit_facts(d, elements[d]) for d in KERNEL_DIMENSIONS},
        "left_multiplication_squares": square_facts(),
        "inverse_and_zero_divisor": inverse_witness(),
    }
    failures = []
    if (
        not result["fano"]["incidence_gram_mod_2_all_ones"]
        or not result["fano"]["complements_are_nontrivial_subgroup_cosets"]
    ):
        failures.append("Fano incidence")
    for d, facts in skeleton.items():
        if facts["zero_products_off_skeleton"] or not facts["chi_invariant_under_single_index_resigning"]:
            failures.append(f"skeleton at D = {d}")
    if not all(result["units_square_to_minus_one"].values()):
        failures.append("unit squares")
    for d, facts in result["annihilators"].items():
        if not facts["kernel_pure_and_right_annihilated"]:
            failures.append(f"annihilators at D = {d}")
    for d, facts in result["qubit_reading"].items():
        if (
            not facts["x_string_eigenstates"]
            or facts["support_qubits"] != facts["support_qubits_with_zero_bloch_vector"]
        ):
            failures.append(f"qubit reading at D = {d}")
    witness = result["inverse_and_zero_divisor"]
    if (
        witness["a_times_b"]
        or witness["a_inverse_times_a"] != {"e0": "1"}
        or witness["a_times_a_inverse"] != {"e0": "1"}
        or witness["second_inverse_times_a"] != {"e0": "1"}
        or witness["a_times_second_inverse"] != {"e0": "1"}
        or witness["second_inverse"] == witness["a_inverse"]
    ):
        failures.append("inverse witness")
    if failures:
        raise SystemExit("kaplansky-cd: " + "; ".join(failures))
    return result


def main(argv: list[str]) -> int:
    if argv not in ([], ["--check"]):
        raise SystemExit('usage: "$PYTHON" docs/evidence/kaplansky-cd-mechanisms/kaplansky_cd_replay.py [--check]')
    text = json.dumps(derivation(), indent=1, sort_keys=True) + "\n"
    if argv == ["--check"]:
        if RESULT.read_text(encoding="utf-8") != text:
            raise SystemExit(f"kaplansky-cd: {RESULT.name} differs from the replay")
        return 0
    RESULT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
