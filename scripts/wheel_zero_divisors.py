"""Carlstrom's wheel of fractions against Cayley-Dickson zero divisors: what totalized division detects.

cd_core.cd_sign is the multiplication table. Every product, left and right
multiplication matrix and zero-product certificate here is exact rational
arithmetic built from cd_sign; ``cross_check_cd_core`` holds that arithmetic
equal to cd_core.cd_multiply and cd_core.left_mult_matrix on small integer
vectors, where float arithmetic is exact. The record answers five
predictions stated before the run (W1-W5, docs/evidence/wheel_zero_divisors/
README.md).

- W1, inverse versus cancellation. Every nonzero real Cayley-Dickson element
  has the two-sided inverse conj(a) / |a|^2 with |a|^2 a positive rational, so
  a sedenion zero divisor is invertible; ab = 0 with b != 0 breaks
  cancellation through the associator (a^-1, a, b) = (a^-1 a) b - a^-1 (a b)
  = b. The sedenion product is noncommutative and nonassociative, so the
  wheel's commutative-monoid axioms do not describe it; the basis counts of
  noncommuting pairs and nonassociating triples are recorded.
- W2, the Gram detector. G = L_a^T L_a is positive semidefinite and positive
  definite exactly when L_a is nonsingular. Its leading principal minors are
  then positive (Sylvester), so wheel_algebra.solve(G, L_a^T e_0) in natural
  pivot order stays finite and returns a^-1, the unique solution of a x = 1;
  for a left zero divisor some pivot is zero, its sub-column in a PSD matrix
  is zero too, 0 * infinity = bottom, and bottom reaches every component. For
  D = 4 and 8, G = |a|^2 I. The negative control solves L_a x = e_0 directly:
  a pure element has a zero diagonal, so the first pivot is zero and the
  verdict is wrong for invertible elements.
- W3, no nullity. The wheel verdict is the same for nullity 4, 8 and 12
  (dimension 32), and the same with an inconsistent right-hand side, a kernel
  vector of L_a; nullity comes from exact rank over Q and rank modulo
  2^61 - 1.
- W4, the complexified norm. Over Q(i) (gaussian_wheel), N(a) = sum a_k^2
  vanishes on nonzero isotropic a. The totalized inverse conj(a) * /N(a) is a
  finite two-sided inverse for N(a) != 0, and for N(a) = 0 it is infinity on
  every nonzero coefficient of conj(a) and bottom on every zero one; then
  a conj(a) = conj(a) a = N(a) e_0 = 0. The Hermitian Gram L_a^H L_a gives the
  singularity verdict over Q(i).
- W5 is the README's statement of scope.

Independent items (elements, pairs) are drawn first in seeded order and then
mapped through parallel.ordered_map, so pooled and serial runs write the same
bytes.

Usage:
    "$PYTHON" scripts/wheel_zero_divisors.py --out docs/evidence/wheel_zero_divisors/result.json
    "$PYTHON" scripts/wheel_zero_divisors.py --check docs/evidence/wheel_zero_divisors/result.json
    "$PYTHON" scripts/wheel_zero_divisors.py --self-test

``--out`` also cross-checks every Q(i) norm and inverse product with pyadic's
GaussianRational when pyadic imports; ``--check`` recomputes everything else
and compares exactly.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import sys
from collections import Counter
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from moreno_stiefel_nullity import PRIME, cayley_frame, rank_mod, rational_kernel  # noqa: E402

import cd_core  # noqa: E402
import gaussian_wheel as gw  # noqa: E402
import parallel  # noqa: E402
import wheel_algebra  # noqa: E402

SCHEMA = "wheel-zero-divisors-v1"
SEED = 20041029
SIZES = {
    "sedenion_two_term": 240,
    "corpus_pairs": 336,
    "composition_random": 24,
    "sedenion_random": 32,
    "cayley_frames": 16,
    "dimension32_per_nullity": 4,
    "gaussian_isotropic": 8,
    "gaussian_anisotropic": 8,
}
SELF_TEST_SIZES = {
    "sedenion_two_term": 12,
    "corpus_pairs": 6,
    "composition_random": 2,
    "sedenion_random": 2,
    "cayley_frames": 2,
    "dimension32_per_nullity": 1,
    "gaussian_isotropic": 1,
    "gaussian_anisotropic": 1,
}

Vector = tuple[Fraction, ...]
Matrix = list[list[Fraction]]
GVector = tuple[gw.GaussianRational, ...]
ZERO = Fraction(0)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


# Exact real arithmetic from cd_core.cd_sign.


def left_matrix(dim: int, a: Sequence[Fraction]) -> Matrix:
    """L_a with L_a e_q = sum_p a_p cd_sign(dim, p, q) e_(p xor q)."""
    m = [[ZERO] * dim for _ in range(dim)]
    for p, ap in enumerate(a):
        if ap:
            for q in range(dim):
                m[p ^ q][q] += ap * cd_core.cd_sign(dim, p, q)
    return m


def right_matrix(dim: int, a: Sequence[Fraction]) -> Matrix:
    """R_a with R_a e_q = e_q a = sum_p a_p cd_sign(dim, q, p) e_(q xor p)."""
    m = [[ZERO] * dim for _ in range(dim)]
    for p, ap in enumerate(a):
        if ap:
            for q in range(dim):
                m[q ^ p][q] += ap * cd_core.cd_sign(dim, q, p)
    return m


def apply(matrix: Matrix, x: Sequence[Fraction]) -> Vector:
    return tuple(sum((r * v for r, v in zip(row, x, strict=True) if r and v), ZERO) for row in matrix)


def multiply(dim: int, a: Sequence[Fraction], b: Sequence[Fraction]) -> Vector:
    return apply(left_matrix(dim, a), b)


def conj(a: Sequence[Fraction]) -> Vector:
    return (a[0], *(-v for v in a[1:]))


def norm_squared(a: Sequence[Fraction]) -> Fraction:
    return sum((v * v for v in a), ZERO)


def unit(dim: int, index: int) -> Vector:
    return tuple(Fraction(int(k == index)) for k in range(dim))


def gram(matrix: Matrix) -> Matrix:
    n = len(matrix[0])
    return [[sum((row[r] * row[c] for row in matrix if row[r] and row[c]), ZERO) for c in range(n)] for r in range(n)]


def transpose_apply(matrix: Matrix, x: Sequence[Fraction]) -> list[Fraction]:
    n = len(matrix[0])
    return [sum((matrix[k][c] * x[k] for k in range(len(matrix)) if matrix[k][c] and x[k]), ZERO) for c in range(n)]


def fraction_rank(matrix: Matrix) -> int:
    rows = [row[:] for row in matrix]
    found = 0
    for column in range(len(rows[0])):
        pivot = next((r for r in range(found, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[found], rows[pivot] = rows[pivot], rows[found]
        lead = rows[found][column]
        for r in range(found + 1, len(rows)):
            if rows[r][column]:
                factor = rows[r][column] / lead
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[found], strict=True)]
        found += 1
    return found


def integer_rows(matrix: Matrix) -> list[list[int]]:
    """Each row times the lcm of its denominators: the same rank over Q and a lower bound on it modulo a prime."""
    out = []
    for row in matrix:
        scale = math.lcm(*(v.denominator for v in row))
        out.append([int(v * scale) for v in row])
    return out


def integer_left_matrix(dim: int, a: Sequence[Fraction]) -> list[list[int]]:
    """L_a for an integral a, without Fraction arithmetic."""
    m = [[0] * dim for _ in range(dim)]
    for p, ap in enumerate(a):
        if ap:
            for q in range(dim):
                m[p ^ q][q] += int(ap) * cd_core.cd_sign(dim, p, q)
    return m


def modular_rank(matrix: Matrix) -> int:
    return rank_mod(integer_rows(matrix), PRIME)


def first_zero_pivot(matrix: Matrix) -> int | None:
    """The index of the first zero pivot of elimination in natural order, the first vanishing leading minor."""
    m = [row[:] for row in matrix]
    n = len(m)
    for c in range(n):
        if not m[c][c]:
            return c
        for i in range(c + 1, n):
            factor = m[i][c] / m[c][c]
            if factor:
                m[i] = [x - factor * y for x, y in zip(m[i], m[c], strict=True)]
    return None


def kinds(values: Sequence[wheel_algebra.Wheel] | Sequence[gw.GaussianWheel]) -> dict[str, int]:
    return dict(sorted(Counter(w.kind() for w in values).items()))


def verdict(counts: dict[str, int]) -> str:
    """'finite' when every component is finite, else the sorted non-finite kinds joined by '+'."""
    return "finite" if set(counts) == {"finite"} else "+".join(sorted(k for k in counts if k != "finite"))


def sparse(a: Sequence[Any]) -> dict[str, str]:
    return {str(k): str(v) for k, v in enumerate(a) if v}


def cross_check_cd_core() -> dict[str, int]:
    """multiply and left_matrix against cd_core on seeded small-integer vectors, where floats are exact."""
    rng = random.Random(SEED)
    products = matrices = 0
    for dim in (4, 8, 16, 32):
        for _ in range(6):
            a = [rng.randint(-3, 3) for _ in range(dim)]
            b = [rng.randint(-3, 3) for _ in range(dim)]
            exact = multiply(dim, [Fraction(v) for v in a], [Fraction(v) for v in b])
            floats = cd_core.cd_multiply(dim, [float(v) for v in a], [float(v) for v in b])
            require(list(exact) == [Fraction(v) for v in floats], f"multiply differs from cd_core.cd_multiply at {dim}")
            products += 1
            spec = cd_core.left_mult_matrix(dim, [float(v) for v in a])
            mine = left_matrix(dim, [Fraction(v) for v in a])
            require(mine == [[Fraction(v) for v in row] for row in spec], f"left_matrix differs from cd_core at {dim}")
            matrices += 1
    return {"products": products, "left_matrices": matrices}


# W2 / W3: the Gram detector on one real element.


def detect(item: tuple[str, int, Vector, bool]) -> dict[str, Any]:
    """Wheel verdicts, exact and modular rank, and the controls for one element a of A_dim."""
    name, dim, a, full = item
    left = left_matrix(dim, a)
    g = gram(left)
    rhs = transpose_apply(left, unit(dim, 0))
    wheel = wheel_algebra.solve(g, rhs)
    counts = kinds(wheel)
    rank_q = fraction_rank(left)
    norm = norm_squared(a)
    out: dict[str, Any] = {
        "name": name,
        "dimension": dim,
        "element": sparse(a),
        "norm_squared": str(norm),
        "rank_q": rank_q,
        "rank_mod_p": modular_rank(left),
        "nullity": dim - rank_q,
        "gram_first_zero_pivot": first_zero_pivot(g),
        "gram_is_norm_identity": g == [[norm * (r == c) for c in range(dim)] for r in range(dim)],
        "wheel_kinds": counts,
        "wheel_verdict": verdict(counts),
    }
    if verdict(counts) == "finite":
        values = [w.value() for w in wheel]
        inverse = [v / norm for v in conj(a)]
        out["wheel_equals_fraction_solve"] = values == wheel_algebra.fraction_solve(g, rhs)
        out["wheel_equals_inverse"] = values == inverse
    else:
        try:
            wheel_algebra.fraction_solve(g, rhs)
            out["fraction_solve"] = "finished"
        except ZeroDivisionError:
            out["fraction_solve"] = "ZeroDivisionError"
    if rank_q < dim:
        # A kernel vector of L_a is orthogonal to range(G) = range(L_a^T), so G x = k is inconsistent.
        kernel = rational_kernel(integer_rows(left))
        require(len(kernel) == dim - rank_q, f"{name}: kernel dimension differs from the nullity")
        require(all(not v for v in apply(left, kernel[0])), f"{name}: the kernel vector fails a k = 0")
        out["kernel_rhs_wheel_kinds"] = kinds(wheel_algebra.solve(g, kernel[0]))
    if full:
        out["right_rank_q"] = fraction_rank(right_matrix(dim, a))
        if rank_q == dim and name.startswith("two-term"):
            out["direct_wheel_verdict"] = verdict(kinds(wheel_algebra.solve(left, unit(dim, 0))))
    return out


def pair_check(item: tuple[str, int, Vector, Vector, bool]) -> dict[str, Any]:
    """Exact ab and ba, and for a zero product the cancellation failure (a^-1, a, b) = b."""
    name, dim, a, b, integral = item
    ab, ba = multiply(dim, a, b), multiply(dim, b, a)
    out: dict[str, Any] = {
        "name": name,
        "a": sparse(a),
        "b": sparse(b),
        "ab_zero": not any(ab),
        "ba_zero": not any(ba),
        "a_rank_q": fraction_rank(left_matrix(dim, a)),
        "b_rank_q": fraction_rank(left_matrix(dim, b)),
    }
    if integral:
        floats = cd_core.cd_multiply(dim, [float(v) for v in a], [float(v) for v in b])
        out["cd_core_ab_zero"] = all(v == 0.0 for v in floats)
    inverse = tuple(v / norm_squared(a) for v in conj(a))
    left_assoc = multiply(dim, multiply(dim, inverse, a), b)
    right_assoc = multiply(dim, inverse, ab)
    out["inverse_two_sided"] = multiply(dim, a, inverse) == unit(dim, 0) == multiply(dim, inverse, a)
    out["associator_inverse_a_b_equals_b"] = tuple(x - y for x, y in zip(left_assoc, right_assoc, strict=True)) == b
    out["cancellation_fails"] = right_assoc != b
    return out


# W4: the complexified algebra over Q(i).


def g_multiply(dim: int, a: GVector, b: GVector) -> GVector:
    out = [gw.ZERO_Q] * dim
    for p, ap in enumerate(a):
        if ap:
            for q, bq in enumerate(b):
                if bq:
                    term = ap * bq
                    out[p ^ q] = out[p ^ q] + (term if cd_core.cd_sign(dim, p, q) > 0 else -term)
    return tuple(out)


def g_left_matrix(dim: int, a: GVector) -> list[list[gw.GaussianRational]]:
    m = [[gw.ZERO_Q] * dim for _ in range(dim)]
    for p, ap in enumerate(a):
        if ap:
            for q in range(dim):
                m[p ^ q][q] = m[p ^ q][q] + (ap if cd_core.cd_sign(dim, p, q) > 0 else -ap)
    return m


def g_conj(a: GVector) -> GVector:
    """Cayley-Dickson conjugation: negate the imaginary units, leave the Q(i) coefficients alone."""
    return (a[0], *(-v for v in a[1:]))


def g_norm(a: GVector) -> gw.GaussianRational:
    """The complex-bilinear quadratic form N(a) = sum a_k^2, with a conj(a) = N(a) e_0."""
    total = gw.ZERO_Q
    for v in a:
        total = total + v * v
    return total


def realified_rank_mod_p(matrix: list[list[gw.GaussianRational]]) -> int:
    """Rank of [[Re, -Im], [Im, Re]] modulo 2^61 - 1, twice the complex rank when the modular rank is exact."""
    n = len(matrix)
    real: Matrix = []
    for r in range(n):
        real.append([v.re for v in matrix[r]] + [-v.im for v in matrix[r]])
    for r in range(n):
        real.append([v.im for v in matrix[r]] + [v.re for v in matrix[r]])
    return modular_rank(real)


def gaussian_detect(item: tuple[str, int, GVector]) -> dict[str, Any]:
    name, dim, a = item
    n = g_norm(a)
    c = g_conj(a)
    reciprocal = gw.GaussianWheel(n).inv()
    inverse = [gw.GaussianWheel(v) * reciprocal for v in c]
    predicted = (
        ["finite"] * dim if n else [("infinity" if v else "bottom") for v in c]
    )  # a nonzero coefficient times infinity is infinity, 0 * infinity is bottom
    left = g_left_matrix(dim, a)
    rank_c = gw.rank(left)
    hermitian = gw.hermitian_gram(left)
    rhs = [left[0][k].conjugate() for k in range(dim)]
    counts = kinds(gw.solve(hermitian, rhs))
    e0 = tuple(gw.ONE_Q if k == 0 else gw.ZERO_Q for k in range(dim))
    out: dict[str, Any] = {
        "name": name,
        "dimension": dim,
        "element": sparse(a),
        "norm": str(n),
        "isotropic": not n,
        "nonzero": any(a),
        "inverse_kinds": kinds(inverse),
        "inverse_pattern_as_predicted": [w.kind() for w in inverse] == predicted,
        "rank_q_i": rank_c,
        "realified_rank_mod_p": realified_rank_mod_p(left),
        "zero_divisor": rank_c < dim,
        "hermitian_gram_wheel_verdict": verdict(counts),
        "a_conj_a_equals_norm": g_multiply(dim, a, c) == tuple(n if k == 0 else gw.ZERO_Q for k in range(dim)),
    }
    if n:
        values = tuple(w.value() for w in inverse)
        out["inverse_two_sided"] = g_multiply(dim, a, values) == e0 == g_multiply(dim, values, a)
    elif any(a):
        out["a_conj_a_zero_product"] = not any(g_multiply(dim, a, c)) and not any(g_multiply(dim, c, a))
    return out


# Seeded item generation, all draws before any map.


def two_term(dim: int, low: int) -> list[tuple[str, Vector]]:
    out = []
    for i in range(low, dim):
        for j in range(i + 1, dim):
            for s in (1, -1):
                a = [ZERO] * dim
                a[i], a[j] = Fraction(1), Fraction(s)
                out.append((f"e{i}{'+' if s > 0 else '-'}e{j}", tuple(a)))
    return out


def random_rational(rng: random.Random) -> Fraction:
    return Fraction(rng.choice((-1, 1)) * rng.randint(1, 9), rng.randint(1, 9))


def frame_element(dim: int, seed: int) -> Vector:
    """(u, v) with u, v an exactly rational orthonormal pure pair of A_(dim/2) (moreno_stiefel_nullity.cayley_frame)."""
    half = dim // 2
    u, v, _ = cayley_frame(half - 1, seed)
    a = [ZERO] * dim
    for k in range(half - 1):
        a[1 + k], a[half + 1 + k] = u[k], v[k]
    return tuple(a)


def corpus_vector(i: int, j: int, t: int) -> Vector:
    a = [ZERO] * 16
    a[i], a[j] = Fraction(1), Fraction(t)
    return tuple(a)


def census_nullity(item: tuple[str, Vector]) -> int:
    """Nullity of L_a modulo 2^61 - 1 for an integral dimension-32 element."""
    return 32 - rank_mod(integer_left_matrix(32, item[1]), PRIME)


def frame_kernel(seed: int) -> list[list[Fraction]]:
    """The reduced-echelon kernel basis of L_a for the Cayley-frame element of seed; a positive scale of a keeps it."""
    return rational_kernel(integer_rows(left_matrix(16, frame_element(16, seed))))


def pair_name(i: int, j: int, t: int, k: int, el: int, s: int) -> tuple[str, str]:
    return f"e{i}{'+' if t > 0 else '-'}e{j}", f"e{k}{'+' if s > 0 else '-'}e{el}"


def draw(sizes: dict[str, int]) -> dict[str, Any]:
    rng = random.Random(SEED)
    corpus = cd_core.sedenion_zero_divisor_corpus()
    corpus_elements = sorted({(i, j, t) for i, j, t, _k, _l, _s in corpus} | {(k, el, s) for *_, k, el, s in corpus})
    corpus_names = {f"e{i}{'+' if t > 0 else '-'}e{j}" for i, j, t in corpus_elements}
    composition: list[tuple[str, int, Vector, bool]] = []
    for dim in (4, 8):
        composition += [(name, dim, a, True) for name, a in two_term(dim, 1)]
        for index in range(sizes["composition_random"]):
            composition.append((f"random-{dim}-{index}", dim, tuple(random_rational(rng) for _ in range(dim)), True))
    sedenion: list[tuple[str, int, Vector, bool]] = []
    # The corpus factors of every retained dark and bright pair stay in the two-term slice, so a reduced draw keeps
    # each bright factor's wheel verdict.
    needed = {name for row in corpus[: sizes["corpus_pairs"]] for name in pair_name(*row)}
    needed |= {name for i, j, t, k, el, s in corpus[: sizes["corpus_pairs"]] for name in pair_name(i, j, t, k, el, -s)}
    for index, (name, a) in enumerate(two_term(16, 0)):
        if index >= sizes["sedenion_two_term"] and name not in needed:
            continue
        family = "corpus" if name in corpus_names else "two-term"
        sedenion.append((f"{family}:{name}", 16, a, True))
    for index in range(sizes["sedenion_random"]):
        sedenion.append((f"random:{index}", 16, tuple(random_rational(rng) for _ in range(16)), True))
    frames: list[tuple[str, int, Vector, Vector, bool]] = []
    kernels = parallel.ordered_map(frame_kernel, [SEED + index for index in range(sizes["cayley_frames"])], min_items=2)
    for index, kernel in enumerate(kernels):
        scale = Fraction(rng.randint(1, 9), rng.randint(1, 9))
        a = tuple(scale * v for v in frame_element(16, SEED + index))
        require(all(not v for k in kernel for v in apply(left_matrix(16, a), k)), f"frame {index}: kernel of L_a")
        weights = [random_rational(rng) for _ in kernel]
        b = tuple(sum((w * k[q] for w, k in zip(weights, kernel, strict=True)), ZERO) for q in range(16))
        frames.append((f"frame:{index}", 16, a, b, False))
        sedenion.append((f"frame:{index}:a", 16, a, True))
        sedenion.append((f"frame:{index}:b", 16, b, True))
    pairs: list[tuple[str, int, Vector, Vector, bool]] = []
    for i, j, t, k, el, s in corpus[: sizes["corpus_pairs"]]:
        name = f"e{i}{'+' if t > 0 else '-'}e{j} * e{k}{'+' if s > 0 else '-'}e{el}"
        pairs.append((f"corpus:{name}", 16, corpus_vector(i, j, t), corpus_vector(k, el, s), True))
    bright: list[tuple[str, int, Vector, Vector, bool]] = []
    for i, j, t, k, el, s in corpus[: sizes["corpus_pairs"]]:
        name = f"e{i}{'+' if t > 0 else '-'}e{j} * e{k}{'+' if s < 0 else '-'}e{el}"
        bright.append((f"bright:{name}", 16, corpus_vector(i, j, t), corpus_vector(k, el, -s), True))
    census_items = two_term(32, 1)
    nullities = parallel.ordered_map(census_nullity, census_items, min_items=64)
    census = [(name, a, nullity) for (name, a), nullity in zip(census_items, nullities, strict=True)]
    strata: dict[int, list[tuple[str, Vector]]] = {}
    for name, a, nullity in census:
        strata.setdefault(nullity, []).append((name, a))
    dimension32 = [
        (f"d32:{name}", 32, a, False)
        for nullity in sorted(strata)
        for name, a in strata[nullity][: sizes["dimension32_per_nullity"]]
    ]
    gaussian: list[tuple[str, int, GVector]] = []
    for dim in (4, 8, 16):
        zero = gw.ZERO_Q
        fixtures = {
            "e0+ie1": {0: gw.ONE_Q, 1: gw.I_Q},
            "e0-ie1": {0: gw.ONE_Q, 1: -gw.I_Q},
            "e0": {0: gw.ONE_Q},
            "zero": {},
        }
        if dim == 16:
            fixtures["e1+e10"] = {1: gw.ONE_Q, 10: gw.ONE_Q}
        for name, coefficients in fixtures.items():
            gaussian.append((f"fixture:{name}", dim, tuple(coefficients.get(k, zero) for k in range(dim))))
        for index in range(sizes["gaussian_isotropic"]):
            u, v, _ = cayley_frame(dim - 1, SEED + 1000 * dim + index)
            factor = gw.GaussianRational(random_rational(rng), random_rational(rng))
            element = (zero, *(factor * gw.GaussianRational(x, y) for x, y in zip(u, v, strict=True)))
            gaussian.append((f"isotropic:{index}", dim, element))
        for index in range(sizes["gaussian_anisotropic"]):
            element = tuple(gw.GaussianRational(random_rational(rng), random_rational(rng)) for _ in range(dim))
            gaussian.append((f"anisotropic:{index}", dim, element))
    return {
        "corpus_size": len(corpus),
        "composition": composition,
        "sedenion": sedenion,
        "frames": frames,
        "pairs": pairs,
        "bright": bright,
        "census": census,
        "dimension32": dimension32,
        "gaussian": gaussian,
    }


# Tables and verdicts.


def basis_counts(dim: int) -> dict[str, int]:
    noncommuting = sum(
        1
        for p in range(dim)
        for q in range(dim)
        if cd_core.cd_sign(dim, p, q) != cd_core.cd_sign(dim, q, p) and p != q and 0 not in (p, q)
    )
    nonassociating = sum(
        1
        for i in range(dim)
        for j in range(dim)
        for k in range(dim)
        if cd_core.triple_sign(dim, i, j, k)[0] != cd_core.triple_sign(dim, i, j, k)[1]
    )
    return {"ordered_noncommuting_pairs": noncommuting, "nonassociating_triples": nonassociating, "triples": dim**3}


def agreement(rows: list[dict[str, Any]]) -> dict[str, Any]:
    table: Counter[str] = Counter()
    for row in rows:
        singular_q = row["rank_q"] < row["dimension"]
        singular_p = row["rank_mod_p"] < row["dimension"]
        table[
            f"wheel={row['wheel_verdict']} rank_q={'singular' if singular_q else 'full'} "
            f"rank_p={'singular' if singular_p else 'full'}"
        ] += 1
    agree = sum(
        1
        for row in rows
        if (row["wheel_verdict"] != "finite")
        == (row["rank_q"] < row["dimension"])
        == (row["rank_mod_p"] < row["dimension"])
    )
    return {"rows": len(rows), "all_three_agree": agree, "table": dict(sorted(table.items()))}


def nullity_table(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    table: dict[str, Counter[str]] = {}
    for row in rows:
        table.setdefault(str(row["nullity"]), Counter())[row["wheel_verdict"]] += 1
    return {k: dict(sorted(v.items())) for k, v in sorted(table.items(), key=lambda kv: int(kv[0]))}


def family(row: dict[str, Any]) -> str:
    return str(row["name"]).split(":")[0]


def build(sizes: dict[str, int]) -> dict[str, Any]:
    items = draw(sizes)
    rows = {
        "composition": parallel.ordered_map(detect, items["composition"], min_items=16),
        "sedenion": parallel.ordered_map(detect, items["sedenion"], min_items=16),
        "dimension32": parallel.ordered_map(detect, items["dimension32"], min_items=4),
        "pairs": parallel.ordered_map(pair_check, items["pairs"] + items["frames"], min_items=16),
        "bright": parallel.ordered_map(pair_check, items["bright"], min_items=16),
        "gaussian": parallel.ordered_map(gaussian_detect, items["gaussian"], min_items=16),
    }
    census = {str(k): v for k, v in sorted(Counter(nullity for _name, _a, nullity in items["census"]).items())}
    return assemble(sizes, rows, census, items["corpus_size"])


def assemble(sizes: dict[str, int], rows: dict[str, Any], census: dict[str, int], corpus_size: int) -> dict[str, Any]:
    """The W1-W4 tables and verdicts from the per-item rows."""
    composition, sedenion, dimension32 = rows["composition"], rows["sedenion"], rows["dimension32"]
    pairs, bright, gaussian = rows["pairs"], rows["bright"], rows["gaussian"]
    by_name = {row["name"]: row for row in sedenion}

    corpus_rows = [row for row in sedenion if family(row) == "corpus"]
    nonzd_rows = [row for row in sedenion if family(row) != "corpus" and row["nullity"] == 0]
    frame_rows = [row for row in sedenion if family(row) == "frame"]
    corpus_pairs = [row for row in pairs if family(row) == "corpus"]
    frame_pairs = [row for row in pairs if family(row) == "frame"]
    w1 = {
        "basis_counts": {str(dim): basis_counts(dim) for dim in (4, 8, 16)},
        "corpus_pairs": len(corpus_pairs),
        "corpus_pairs_cd_core_zero": sum(row["cd_core_ab_zero"] for row in corpus_pairs),
        "corpus_pairs_exact_zero": sum(row["ab_zero"] for row in corpus_pairs),
        "corpus_pairs_ba_zero": sum(row["ba_zero"] for row in corpus_pairs),
        "frame_pairs": len(frame_pairs),
        "frame_pairs_exact_zero": sum(row["ab_zero"] and row["ba_zero"] for row in frame_pairs),
        "inverse_two_sided": sum(row["inverse_two_sided"] for row in pairs),
        "cancellation_fails": sum(row["cancellation_fails"] for row in pairs),
        "associator_equals_b": sum(row["associator_inverse_a_b_equals_b"] for row in pairs),
    }
    w1["pass"] = (
        w1["corpus_pairs_cd_core_zero"] == w1["corpus_pairs_exact_zero"] == w1["corpus_pairs"]
        and w1["frame_pairs_exact_zero"] == w1["frame_pairs"]
        and w1["inverse_two_sided"] == w1["cancellation_fails"] == w1["associator_equals_b"] == len(pairs)
        and all(counts["nonassociating_triples"] > 0 for d, counts in w1["basis_counts"].items() if d != "4")
        and all(counts["ordered_noncommuting_pairs"] > 0 for counts in w1["basis_counts"].values())
    )

    singular_rows = [row for row in sedenion + dimension32 if row["rank_q"] < row["dimension"]]
    finite_rows = [row for row in composition + sedenion + dimension32 if row["wheel_verdict"] == "finite"]
    w2 = {
        "composition": agreement(composition),
        "composition_gram_is_norm_identity": sum(row["gram_is_norm_identity"] for row in composition),
        "sedenion": agreement(sedenion),
        "sedenion_by_family": {
            name: agreement([row for row in sedenion if family(row) == name])
            for name in ("corpus", "two-term", "random", "frame")
        },
        "sedenion_gram_is_norm_identity": sum(row["gram_is_norm_identity"] for row in sedenion),
        "corpus_elements": len(corpus_rows),
        "nonsingular_sedenions": len(nonzd_rows),
        "singular_all_bottom": sum(row["wheel_kinds"] == {"bottom": row["dimension"]} for row in singular_rows),
        "singular_rows": len(singular_rows),
        "finite_equals_fraction_solve_and_inverse": sum(
            row.get("wheel_equals_fraction_solve", False) and row.get("wheel_equals_inverse", False)
            for row in finite_rows
        ),
        "finite_rows": len(finite_rows),
        "singular_fraction_solve_raises": sum(
            row.get("fraction_solve") == "ZeroDivisionError" for row in singular_rows
        ),
        "first_zero_pivot": dict(sorted(Counter(str(row["gram_first_zero_pivot"]) for row in singular_rows).items())),
        "right_rank_equals_left": sum(row["right_rank_q"] == row["rank_q"] for row in sedenion),
        "direct_solve_on_nonsingular_two_term": dict(
            sorted(Counter(row["direct_wheel_verdict"] for row in nonzd_rows if "direct_wheel_verdict" in row).items())
        ),
        "frame_elements_singular": sum(row["nullity"] > 0 for row in frame_rows),
        "frame_elements": len(frame_rows),
        "bright_pairs": len(bright),
        "bright_products_nonzero": sum(not row["ab_zero"] for row in bright),
        "bright_cd_core_nonzero": sum(not row["cd_core_ab_zero"] for row in bright),
        "bright_factors_singular": sum(row["a_rank_q"] < 16 and row["b_rank_q"] < 16 for row in bright),
        "bright_factors_wheel_bottom": sum(
            by_name.get(f"corpus:{_name(row['a'])}", {}).get("wheel_verdict") == "bottom"
            and by_name.get(f"corpus:{_name(row['b'])}", {}).get("wheel_verdict") == "bottom"
            for row in bright
        ),
    }
    w2["pass"] = (
        w2["composition"]["all_three_agree"] == w2["composition"]["rows"]
        and w2["composition_gram_is_norm_identity"] == len(composition)
        and w2["sedenion"]["all_three_agree"] == w2["sedenion"]["rows"]
        and w2["singular_all_bottom"] == w2["singular_rows"]
        and w2["finite_equals_fraction_solve_and_inverse"] == w2["finite_rows"]
        and w2["frame_elements_singular"] == w2["frame_elements"]
        and w2["right_rank_equals_left"] == len(sedenion)
        and w2["bright_products_nonzero"] == w2["bright_cd_core_nonzero"] == len(bright)
        and w2["bright_factors_singular"] == w2["bright_factors_wheel_bottom"] == len(bright)
    )

    w3 = {
        "sedenion_nullity_by_verdict": nullity_table(sedenion),
        "dimension32_census_mod_p_nullity": dict(sorted(census.items(), key=lambda kv: int(kv[0]))),
        "dimension32_sample": agreement(dimension32),
        "dimension32_nullity_by_verdict": nullity_table(dimension32),
        "dimension32_rank_q_equals_mod_p": sum(row["rank_q"] == row["rank_mod_p"] for row in dimension32),
        "kernel_rhs_kinds": dict(
            sorted(Counter(json.dumps(row["kernel_rhs_wheel_kinds"]) for row in singular_rows).items())
        ),
    }
    singular_verdicts = {
        verdict
        for table in (w3["sedenion_nullity_by_verdict"], w3["dimension32_nullity_by_verdict"])
        for nullity, counts in table.items()
        if nullity != "0"
        for verdict in counts
    }
    w3["pass"] = (
        singular_verdicts == {"bottom"}
        and len([k for k in w3["dimension32_nullity_by_verdict"] if k != "0"]) >= 3
        and all(set(json.loads(kind)) == {"bottom"} for kind in w3["kernel_rhs_kinds"])
        and w3["dimension32_rank_q_equals_mod_p"] == len(dimension32)
    )

    w4_tables: dict[str, Any] = {}
    w4_pass = True
    for dim in (4, 8, 16):
        members = [row for row in gaussian if row["dimension"] == dim]
        nonzero = [row for row in members if row["nonzero"]]
        isotropic = [row for row in nonzero if row["isotropic"]]
        anisotropic = [row for row in nonzero if not row["isotropic"]]
        table = {
            "elements": len(members),
            "isotropic_nonzero": len(isotropic),
            "anisotropic": len(anisotropic),
            "inverse_pattern_as_predicted": sum(row["inverse_pattern_as_predicted"] for row in members),
            "a_conj_a_equals_norm": sum(row["a_conj_a_equals_norm"] for row in members),
            "anisotropic_inverse_two_sided": sum(row["inverse_two_sided"] for row in anisotropic),
            "isotropic_zero_product_with_conj": sum(row["a_conj_a_zero_product"] for row in isotropic),
            "isotropic_singular": sum(row["zero_divisor"] for row in isotropic),
            "anisotropic_singular": sum(row["zero_divisor"] for row in anisotropic),
            "rank_q_i_equals_realified_mod_p": sum(
                2 * row["rank_q_i"] == row["realified_rank_mod_p"] for row in members
            ),
            "hermitian_gram_verdict_agrees_with_rank": sum(
                (row["hermitian_gram_wheel_verdict"] != "finite") == (row["rank_q_i"] < dim) for row in members
            ),
            "inverse_kinds": {
                row["name"]: row["inverse_kinds"] for row in members if row["name"].startswith("fixture")
            },
        }
        w4_tables[str(dim)] = table
        w4_pass = w4_pass and (
            table["inverse_pattern_as_predicted"] == table["a_conj_a_equals_norm"] == len(members)
            and table["anisotropic_inverse_two_sided"] == len(anisotropic)
            and table["isotropic_zero_product_with_conj"] == table["isotropic_singular"] == len(isotropic)
            and table["rank_q_i_equals_realified_mod_p"] == len(members)
            and table["hermitian_gram_verdict_agrees_with_rank"] == len(members)
            and table["anisotropic_singular"] == (1 if dim == 16 else 0)
        )
    w4 = {"by_dimension": w4_tables, "pass": w4_pass}

    return {
        "schema": SCHEMA,
        "seed": SEED,
        "sizes": sizes,
        "prime": str(PRIME),
        "cd_core_cross_check": cross_check_cd_core(),
        "corpus_size": corpus_size,
        "W1": w1,
        "W2": w2,
        "W3": w3,
        "W4": w4,
        "rows": rows,
    }


def _name(element: dict[str, str]) -> str:
    (i, vi), (j, vj) = sorted(element.items(), key=lambda kv: int(kv[0]))
    require(vi == "1" and vj in ("1", "-1"), f"not a corpus element: {element}")
    return f"e{i}{'+' if vj == '1' else '-'}e{j}"


def pyadic_cross_check(record: dict[str, Any]) -> dict[str, Any]:
    """N(a) and the two-sided inverse of every anisotropic Q(i) row recomputed with pyadic.GaussianRational."""
    import importlib.metadata

    try:
        from pyadic import GaussianRational
    except ImportError:
        return {"status": "not run: pyadic does not import"}

    def parse(text: str) -> Any:
        sign = max(text.rfind("+"), text.rfind("-"))
        return GaussianRational(Fraction(text[:sign]), Fraction(text[sign:-1]))

    checked = agree = 0
    for row in record["rows"]["gaussian"]:
        dim = row["dimension"]
        a = [parse(row["element"][str(k)]) if str(k) in row["element"] else GaussianRational(0, 0) for k in range(dim)]
        norm = sum((v * v for v in a), GaussianRational(0, 0))
        expected = parse(row["norm"])
        ok = norm.real == expected.real and norm.imag == expected.imag
        if norm.real or norm.imag:
            inverse = [a[0] / norm, *(-v / norm for v in a[1:])]
            ours = g_multiply(
                dim,
                tuple(gw.GaussianRational(v.real, v.imag) for v in a),
                tuple(gw.GaussianRational(v.real, v.imag) for v in inverse),
            )
            ok = ok and ours == tuple(gw.ONE_Q if k == 0 else gw.ZERO_Q for k in range(dim))
        checked += 1
        agree += ok
    return {"status": "run", "pyadic": importlib.metadata.version("pyadic"), "rows": checked, "agree": agree}


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def compare(fresh: dict[str, Any], retained: dict[str, Any]) -> list[str]:
    retained = copy.deepcopy(retained)
    retained.pop("pyadic_cross_check", None)
    if render(fresh) == render(retained):
        return []
    return [key for key in sorted(set(fresh) | set(retained)) if fresh.get(key) != retained.get(key)]


def summary(record: dict[str, Any]) -> str:
    return " ".join(f"{name}={'pass' if record[name]['pass'] else 'FAIL'}" for name in ("W1", "W2", "W3", "W4"))


def self_test() -> int:
    counts = cross_check_cd_core()
    print(f"cd_core cross-check: {counts}")
    e1e10 = detect(("e1+e10", 16, corpus_vector(1, 10, 1), True))
    require(e1e10["wheel_kinds"] == {"bottom": 16} and e1e10["nullity"] == 4, f"e1+e10: {e1e10}")
    e1e2 = detect(("two-term:e1+e2", 16, corpus_vector(1, 2, 1), True))
    require(e1e2["wheel_verdict"] == "finite" and e1e2["wheel_equals_inverse"], f"e1+e2: {e1e2}")
    require(e1e2["direct_wheel_verdict"] != "finite", "the direct solve of a pure element has a finite first pivot")
    octonion = detect(("oct", 8, tuple(Fraction(k + 1, 3) for k in range(8)), True))
    require(octonion["gram_is_norm_identity"] and octonion["wheel_equals_inverse"], f"octonion: {octonion}")
    pair = pair_check(("dark", 16, corpus_vector(1, 10, 1), corpus_vector(4, 15, -1), True))
    require(pair["ab_zero"] and pair["cd_core_ab_zero"] and pair["cancellation_fails"], f"dark pair: {pair}")
    bright = pair_check(("bright", 16, corpus_vector(1, 10, 1), corpus_vector(4, 15, 1), True))
    require(not bright["ab_zero"], "the bright control (e1 + e10)(e4 + e15) is zero")
    fixture = gaussian_detect(("e0+ie1", 4, (gw.ONE_Q, gw.I_Q, gw.ZERO_Q, gw.ZERO_Q)))
    require(fixture["isotropic"] and fixture["inverse_kinds"] == {"bottom": 2, "infinity": 2}, f"e0+ie1: {fixture}")
    require(fixture["a_conj_a_zero_product"] and fixture["zero_divisor"], f"e0+ie1 product: {fixture}")
    record = build(SELF_TEST_SIZES)
    require(compare(record, json.loads(render(record))) == [], "a record differs from its own rendering")
    corrupt = json.loads(render(record))
    corrupt["W2"]["singular_rows"] += 1
    require(compare(record, corrupt) == ["W2"], "--check accepts a corrupted W2 count")
    corrupt = json.loads(render(record))
    corrupt["rows"]["sedenion"][0]["wheel_verdict"] = "corrupt"
    require(compare(record, corrupt) == ["rows"], "--check accepts a corrupted row")
    require(summary(record) == "W1=pass W2=pass W3=pass W4=pass", f"reduced record: {summary(record)}")
    census = record["W3"]["dimension32_census_mod_p_nullity"]
    corruptions = {
        "W1": ("pairs", lambda row: row["name"].startswith("corpus"), "cancellation_fails", False),
        "W2": ("sedenion", lambda row: row["name"].startswith("corpus"), "wheel_verdict", "finite"),
        "W3": ("dimension32", lambda row: row["nullity"] == 8, "wheel_verdict", "infinity"),
        "W4": ("gaussian", lambda row: row["isotropic"] and row["nonzero"], "inverse_pattern_as_predicted", False),
    }
    for name, (group, select, field, value) in corruptions.items():
        rows = copy.deepcopy(record["rows"])
        next(row for row in rows[group] if select(row))[field] = value
        mutated = assemble(SELF_TEST_SIZES, rows, census, record["corpus_size"])
        require(not mutated[name]["pass"], f"{name} passes with a corrupted {group} row")
    print(f"reduced record: {summary(record)}; one corrupted row fails each of W1-W4")
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    record = build(SIZES)
    if args.out is not None:
        record["pyadic_cross_check"] = pyadic_cross_check(record)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render(record))
        print(f"wrote {args.out}: {summary(record)}; pyadic {record['pyadic_cross_check']}")
        cross = record["pyadic_cross_check"]
        pyadic_ok = cross.get("status") != "run" or cross.get("agree") == cross.get("rows")
        return 0 if pyadic_ok and all(record[name]["pass"] for name in ("W1", "W2", "W3", "W4")) else 1
    retained = json.loads(args.check.read_text())
    differing = compare(record, retained)
    require(not differing, f"{args.check} differs from the recomputation in {differing}")
    failing = [name for name in ("W1", "W2", "W3", "W4") if not record[name]["pass"]]
    require(not failing, f"{args.check} records failing predictions {failing}")
    cross = retained.get("pyadic_cross_check", {})
    require(
        cross.get("status") != "run" or cross.get("agree") == cross.get("rows"),
        f"{args.check} records a pyadic cross-check that disagrees: {cross}",
    )
    print(f"{args.check} matches: {summary(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
