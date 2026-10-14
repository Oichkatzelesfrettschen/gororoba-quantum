"""Cayley-Dickson basis arithmetic ported from open_gororoba cd_kernel.

The basis product is e_p * e_q = cd_sign(dim, p, q) * e_{p XOR q}, with the sign
recursion of cd_kernel::cayley_dickson::signs::cd_basis_mul_sign_iter and the
doubling (a,b)(c,d) = (ac - conj(d) b, d a + b conj(c)). The classification of
associative basis triples and of sedenion zero divisors follows from this sign
table alone, so every circuit prediction downstream rests on the functions here.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations


def cd_sign(dim: int, p: int, q: int) -> int:
    """Sign of e_p * e_q within a 2^k-dimensional Cayley-Dickson algebra."""
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


def cd_multiply(dim: int, a: list[float], b: list[float]) -> list[float]:
    """Full Cayley-Dickson product of two dim-vectors."""
    out = [0.0] * dim
    for p in range(dim):
        ap = a[p]
        if ap == 0.0:
            continue
        for q in range(dim):
            bq = b[q]
            if bq == 0.0:
                continue
            out[p ^ q] += cd_sign(dim, p, q) * ap * bq
    return out


def basis(dim: int, index: int, scale: float = 1.0) -> list[float]:
    v = [0.0] * dim
    v[index] = scale
    return v


def _lmat(dim: int, m: int) -> list[list[float]]:
    mat = [[0.0] * dim for _ in range(dim)]
    for q in range(dim):
        mat[m ^ q][q] = float(cd_sign(dim, m, q))
    return mat


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    n = len(a)
    return [[sum(a[r][k] * b[k][c] for k in range(n)) for c in range(n)] for r in range(n)]


def left_mult_matrix_check(i: int, j: int) -> list[list[float]]:
    """W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j} on the octonions, pure-Python.

    e_i e_j = cd_sign(8,i,j) e_{i^j}, so L_{e_i e_j} = cd_sign(8,i,j) L_{e_{i^j}}.
    L_{e_m} is a signed permutation, hence orthogonal, so its inverse is its
    transpose.
    """
    li, lj, lij = _lmat(8, i), _lmat(8, j), _lmat(8, i ^ j)
    s = cd_sign(8, i, j)
    inv = [[lij[c][r] / s for c in range(8)] for r in range(8)]
    return _matmul(inv, _matmul(li, lj))


def associator(dim: int, x: list[float], y: list[float], z: list[float]) -> list[float]:
    left = cd_multiply(dim, cd_multiply(dim, x, y), z)
    right = cd_multiply(dim, x, cd_multiply(dim, y, z))
    return [lv - rv for lv, rv in zip(left, right, strict=True)]


def triple_sign(dim: int, i: int, j: int, k: int) -> tuple[int, int]:
    """Return (left_sign, right_sign) for (e_i e_j) e_k vs e_i (e_j e_k).

    Both land on e_{i^j^k}; equal signs mean the triple associates.
    """
    left = cd_sign(dim, i, j) * cd_sign(dim, i ^ j, k)
    right = cd_sign(dim, j, k) * cd_sign(dim, i, j ^ k)
    return left, right


def classify_octonion_triples() -> tuple[int, int]:
    """Count ordered distinct imaginary-unit triples that associate vs not."""
    assoc = anti = 0
    for i, j, k in permutations(range(1, 8), 3):
        left, right = triple_sign(8, i, j, k)
        if left == right:
            assoc += 1
        else:
            anti += 1
    return assoc, anti


def fano_completion(i: int, j: int) -> int | None:
    """The unique k making (i, j, k) an associative octonion triple, if any."""
    for k in range(1, 8):
        if k in (i, j):
            continue
        left, right = triple_sign(8, i, j, k)
        if left == right:
            return k
    return None


def sedenion_zero_divisor_corpus() -> list[tuple[int, int, int, int, int, int]]:
    """Signed zero-divisor pairs (e_i + t e_j)(e_k + s e_l) = 0 in the sedenions.

    Returns (i, j, t, k, l, s) with t, s in {+1, -1}, i<j, k<l, and the index
    sets disjoint: the row layout (u_low, u_high, u_sign, v_low, v_high, v_sign)
    of the kernel's reggiani_standard_zero_divisor_pairs.csv.
    """
    dim = 16
    found = []
    pairs = list(combinations(range(1, dim), 2))
    for i, j in pairs:
        for t in (1, -1):
            a = [0.0] * dim
            a[i] = 1.0
            a[j] = float(t)
            for k, el in pairs:
                if len({i, j, k, el}) != 4:
                    continue
                for s in (1, -1):
                    b = [0.0] * dim
                    b[k] = 1.0
                    b[el] = float(s)
                    prod = cd_multiply(dim, a, b)
                    if all(abs(v) < 1e-12 for v in prod):
                        found.append((i, j, t, k, el, s))
    return found


def sedenion_zero_divisors() -> list[tuple[tuple[int, int], tuple[int, int], int]]:
    """The t = +1 half of the corpus: (e_i + e_j)(e_k + s e_l) = 0.

    Returns (i, j), (k, l), s, the operand shape design B's LCU consumes.
    """
    return [((i, j), (k, el), s) for i, j, t, k, el, s in sedenion_zero_divisor_corpus() if t == 1]


def left_mult_matrix(dim: int, v: list[float]) -> list[list[float]]:
    """L_v: x -> v x as a dim x dim matrix over the basis, L_v = sum_p v_p L_{e_p}."""
    mat = [[0.0] * dim for _ in range(dim)]
    for p, vp in enumerate(v):
        if vp == 0.0:
            continue
        for q in range(dim):
            mat[p ^ q][q] += vp * cd_sign(dim, p, q)
    return mat


def _determinant(mat: list[list[float]]) -> float:
    """Exact determinant by Gaussian elimination over Fractions; integral entries give an exact integer."""
    n = len(mat)
    a = [[Fraction(x) for x in row] for row in mat]
    det = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            return 0.0
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            det = -det
        det *= a[col][col]
        for r in range(col + 1, n):
            factor = a[r][col] / a[col][col]
            if factor:
                a[r] = [x - factor * y for x, y in zip(a[r], a[col], strict=True)]
    return float(det)


def sedenion_counterexamples() -> dict[str, dict[str, float]]:
    """det L_v and the squared-norm identity for e_0 + e_9 and e_1 + e_9 in the sedenions.

    Neither element is a zero divisor: det L_v = 256 for both, so a predicate
    that reads only the equal norms of the two octonion halves (both 1 here)
    or the polynomial that vanishes on e_0 + e_9 misclassifies them. The
    imaginary halves of e_1 + e_9 are parallel (e_1 and e_1 after the
    doubling), so L_v^2 = -2 I rather than the orthogonal zero-divisor
    structure.
    """
    dim = 16
    out: dict[str, dict[str, float]] = {}
    for name, (i, j) in (("e0+e9", (0, 9)), ("e1+e9", (1, 9))):
        v = basis(dim, i)
        v[j] = 1.0
        mat = left_mult_matrix(dim, v)
        square = _matmul(mat, mat)
        identity_scale = square[0][0]
        is_scalar = all(square[r][c] == (identity_scale if r == c else 0.0) for r in range(dim) for c in range(dim))
        out[name] = {
            "det": _determinant(mat),
            "square_is_scalar": float(is_scalar),
            "square_scale": identity_scale if is_scalar else float("nan"),
        }
    return out


def _check_sedenion_counterexamples() -> None:
    found = sedenion_counterexamples()
    for name, facts in found.items():
        if abs(facts["det"] - 256.0) > 1e-9:
            raise RuntimeError(f"{name}: det L_v = {facts['det']}, expected 256")
    if found["e1+e9"]["square_is_scalar"] != 1.0 or found["e1+e9"]["square_scale"] != -2.0:
        raise RuntimeError(f"e1+e9: L_v^2 is not -2 I: {found['e1+e9']}")
    if found["e0+e9"]["square_is_scalar"] == 1.0:
        raise RuntimeError("e0+e9: L_v^2 is scalar, but e_0 + e_9 is not purely imaginary")
    # Every corpus zero divisor has a singular L_v, the property the counterexamples lack.
    for i, j, t, _k, _l, _s in sedenion_zero_divisor_corpus()[:8]:
        v = basis(dim := 16, i)
        v[j] = float(t)
        if _determinant(left_mult_matrix(dim, v)) != 0.0:
            raise RuntimeError(f"corpus zero divisor e_{i} {t:+d} e_{j} has invertible L_v")


if __name__ == "__main__":
    _check_sedenion_counterexamples()
    print(f"sedenion counterexamples: {sedenion_counterexamples()}")
    assoc, anti = classify_octonion_triples()
    print(f"octonion ordered distinct triples: associative={assoc} anti={anti} total={assoc + anti}")
    print(f"quaternion check e1*e2 -> sign {cd_sign(8, 1, 2)} index {1 ^ 2}")
    print(f"octonion non-associativity example A(e1,e2,e4) = {associator(8, basis(8, 1), basis(8, 2), basis(8, 4))}")
    zds = sedenion_zero_divisors()
    print(f"sedenion (e_i+e_j)(e_k+-e_l)=0 zero-divisor pairs: {len(zds)}")
    for entry in zds[:5]:
        print(
            f"  (e_{entry[0][0]}+e_{entry[0][1]}) * (e_{entry[1][0]}{'+' if entry[2] > 0 else '-'}e_{entry[1][1]}) = 0"
        )
