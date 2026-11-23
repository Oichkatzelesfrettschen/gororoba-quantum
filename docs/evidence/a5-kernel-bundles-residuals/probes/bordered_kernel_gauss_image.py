"""Gauss image of the nullity-four strata at a second prime: dimension, linear span and degree-2 Hilbert function.

The bordered matrix A(z, w) of kernel_frames.py is a 16 x 16 skew matrix, linear in z and in w, and a real point has
w = conjugate(z). In split coordinates x (z_k = i^popcount(k) x_k) the nullity-four points are the points of the
quadric V(Q) or the quartic V(G) where A has rank 14; the kernel there is a 2-plane, and (z, w) -> ker A(z, w) is
the kernel Gauss map into Gr(2, 16) in P^119, with z on the hypersurface and w free (the kernel is K(z) n w-perp,
A5-459). gauss_image_quadrics.py measures the degree-2 part of the image modulo 32029 through frames of K(z). This
probe repeats that measurement by another route, the kernel of the bordered matrix itself, modulo 32009 with i sent
to 10754. For each of V(Q) minus V(G) and V(G) minus V(Q) it draws points x of the hypersurface on lines a + t b
and a vector w (all read from a sha256 counter stream; the roots in t are computed), keeps those of rank 14 off the
other hypersurface, and measures

- the rank of the differential of the Gauss map on the tangent space of the locus (first-order kernel frames over
  the dual numbers), a lower bound for the dimension of the image;
- the rank of the sampled Plucker vectors, a lower bound for the dimension of the linear span of the image;
- the rank of the 7260 sampled quadric monomials, a lower bound for the Hilbert function of the image in degree 2.

A rank that the sample size does not limit and that stays equal over the last 1000 points is reported as stable.
The prediction, written before the run, is the pair of ranks of the retained record: 3887 and 4022.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import flint
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[1]
sys.path.insert(0, str(EVIDENCE / "a5-kernel-bundles"))
sys.path.insert(0, str(EVIDENCE.parents[1] / "gororoba_quantum"))

import kernel_frames as frames  # noqa: E402

PRIME, ROOT = 32009, 10754
N = 16
PAIRS = tuple(itertools.combinations(range(N), 2))
QUADS = tuple(itertools.combinations_with_replacement(range(len(PAIRS)), 2))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _mod(value: Any) -> int:
    real, imaginary = sp.nsimplify(value).as_real_imag()
    real, imaginary = sp.Rational(real), sp.Rational(imaginary)
    return int((real.p * pow(real.q, -1, PRIME) + ROOT * imaginary.p * pow(imaginary.q, -1, PRIME)) % PRIME)


class Stream:
    """Field elements from sha256(label, counter); the draws select sample points and enter no verdict as values."""

    def __init__(self, label: str) -> None:
        self.label, self.counter = label, 0

    def draw(self) -> int:
        while True:
            digest = hashlib.sha256(f"{self.label}:{self.counter}".encode()).digest()
            self.counter += 1
            value = int.from_bytes(digest[:4], "big")
            if value < (2**32 // PRIME) * PRIME:
                return value % PRIME


def setup() -> dict[str, Any]:
    z = sp.symbols("z1:16")
    c = sp.symbols("c1:16")
    bordered = frames._bordered_matrix(z)
    _require(bordered.T == -bordered, "the bordered matrix is not skew")
    free = bordered.subs({sp.conjugate(symbol): value for symbol, value in zip(z, c, strict=True)})
    phases = [sp.I ** (index + 1).bit_count() for index in range(15)]
    layers = np.zeros((30, N, N), dtype=np.int64)
    for row in range(N):
        for column in range(N):
            entry = sp.Poly(free[row, column], *z, *c)
            _require(
                entry.total_degree() <= 1 and entry.eval(dict.fromkeys((*z, *c), 0)) == 0, "an entry is not linear"
            )
            for index in range(15):
                layers[index, row, column] = _mod(phases[index] * entry.coeff_monomial(z[index]))
                layers[15 + index, row, column] = _mod(entry.coeff_monomial(c[index]))
    ideals = frames.regularity.closure_ideals()
    names = sp.symbols("z1:16")
    forms = {}
    for key in ("VQ", "VG"):
        _require(len(ideals[key]) == 1, f"{key} is not a hypersurface")
        polynomial = sp.Poly(sp.sympify(str(ideals[key][0]).replace("^", "**")), *names)
        gradient = [polynomial.diff(name) for name in names]
        forms[key] = (
            [(monomial, int(coefficient) % PRIME) for monomial, coefficient in polynomial.terms()],
            [[(monomial, int(coefficient) % PRIME) for monomial, coefficient in part.terms()] for part in gradient],
            polynomial.total_degree(),
        )
    return {"layers": layers, "forms": forms}


def evaluate(terms: list[tuple[tuple[int, ...], int]], point: list[int]) -> int:
    total = 0
    for monomial, coefficient in terms:
        value = coefficient
        for index, exponent in enumerate(monomial):
            if exponent:
                value = value * pow(point[index], exponent, PRIME) % PRIME
        total += value
    return total % PRIME


def points_on(terms: list[tuple[tuple[int, ...], int]], degree: int, stream: Stream) -> list[list[int]]:
    """The F_p points x of the hypersurface on one line a + t b of the split coordinates."""
    a = [stream.draw() for _ in range(15)]
    b = [stream.draw() for _ in range(15)]
    nodes = list(range(degree + 1))
    values = [evaluate(terms, [(a[k] + t * b[k]) % PRIME for k in range(15)]) for t in nodes]
    vandermonde = flint.nmod_mat(
        degree + 1, degree + 1, [pow(t, e, PRIME) for t in nodes for e in range(degree + 1)], PRIME
    )
    coefficients = vandermonde.solve(flint.nmod_mat(degree + 1, 1, values, PRIME))
    polynomial = flint.nmod_poly([int(coefficients[e, 0]) for e in range(degree + 1)], PRIME)
    if polynomial.degree() < 1:
        return []
    roots = []
    for factor, _multiplicity in polynomial.factor()[1]:
        if factor.degree() == 1:
            roots.append(int(-factor[0] * pow(int(factor[1]), -1, PRIME)) % PRIME)
    return [[(a[k] + t * b[k]) % PRIME for k in range(15)] for t in roots]


def matrix_at(layers: np.ndarray, vector: list[int]) -> np.ndarray:
    return np.tensordot(np.array(vector, dtype=np.int64), layers, axes=1) % PRIME


def kernel(matrix: np.ndarray) -> np.ndarray | None:
    """A 16 x 2 kernel basis when the rank is 14."""
    flat = flint.nmod_mat(N, N, [int(v) for v in matrix.reshape(-1)], PRIME)
    if flat.rank() != N - 2:
        return None
    basis, nullity = flat.nullspace()
    _require(nullity == 2, "the nullspace is not a plane")
    return np.array([[int(basis[row, column]) for column in range(2)] for row in range(N)], dtype=np.int64)


def plucker(frame: np.ndarray) -> np.ndarray:
    first, second = frame[:, 0], frame[:, 1]
    rows = np.array([i for i, _ in PAIRS])
    columns = np.array([j for _, j in PAIRS])
    return (first[rows] * second[columns] - first[columns] * second[rows]) % PRIME


def differential_rank(layers: np.ndarray, gradient: list[int], point: list[int], frame: np.ndarray) -> tuple[int, int]:
    """Rank of (p, dp(v)) over a basis v of the tangent space, minus one; and the count of tangency failures."""
    matrix = matrix_at(layers, point)
    p0 = plucker(frame)
    pair = next(index for index, value in enumerate(p0) if value)
    free = PAIRS[pair]
    pivot = [index for index in range(N) if index not in free]
    block = flint.nmod_mat(14, 14, [int(matrix[r, c]) for r in pivot for c in pivot], PRIME)
    _require(block.rank() == 14, "the principal block of a nonzero Plucker coordinate is singular")
    inverse = block.inv()
    coupling = flint.nmod_mat(14, 2, [int(matrix[r, c]) for r in pivot for c in free], PRIME)
    top = inverse * coupling
    schur = np.zeros((N, 2), dtype=np.int64)
    for position, row in enumerate(pivot):
        for column in range(2):
            schur[row, column] = (-int(top[position, column])) % PRIME
    schur[free[0], 0] = schur[free[1], 1] = 1
    _require(not ((matrix @ schur) % PRIME).any(), "the Schur frame is not in the kernel")
    grad = flint.nmod_mat(1, 30, gradient, PRIME)
    tangent, dimension = grad.nullspace()
    _require(dimension == 29, "the point is singular on the hypersurface")
    rows = [plucker(schur)]
    failures = 0
    for column in range(dimension):
        vector = [int(tangent[k, column]) for k in range(30)]
        moved = (matrix_at(layers, vector) @ schur) % PRIME
        right = flint.nmod_mat(14, 2, [int(moved[r, c]) for r in pivot for c in range(2)], PRIME)
        correction = inverse * right
        first = np.zeros((N, 2), dtype=np.int64)
        for position, row in enumerate(pivot):
            for c in range(2):
                first[row, c] = (-int(correction[position, c])) % PRIME
        residual = (moved + matrix @ first) % PRIME
        if residual.any():
            failures += 1
        a, b, da, db = schur[:, 0], schur[:, 1], first[:, 0], first[:, 1]
        ri = np.array([i for i, _ in PAIRS])
        ci = np.array([j for _, j in PAIRS])
        rows.append((da[ri] * b[ci] + a[ri] * db[ci] - da[ci] * b[ri] - a[ci] * db[ri]) % PRIME)
    stacked = flint.nmod_mat(len(rows), len(PAIRS), [int(v) for row in rows for v in row], PRIME)
    return stacked.rank() - 1, failures


def grassmannian_hilbert(n: int) -> list[int]:
    """Hilbert function of Gr(2, n) in degrees 1 and 2: C(n, 2) and C(C(n, 2) + 1, 2) - C(n, 4)."""
    m = n * (n - 1) // 2
    return [m, m * (m + 1) // 2 - n * (n - 1) * (n - 2) * (n - 3) // 24]


def stratum(name: str, own: str, other: str, data: dict[str, Any], sample: int) -> dict[str, Any]:
    started = time.monotonic()
    layers, forms = data["layers"], data["forms"]
    terms, gradient_terms, degree = forms[own]
    stream = Stream(f"a5-nullity4-gauss-image:{name}")
    vectors: list[np.ndarray] = []
    kept: list[list[int]] = []
    lines = rejected_rank = rejected_other = 0
    while len(vectors) < sample:
        lines += 1
        for point in points_on(terms, degree, stream):
            _require(evaluate(terms, point) == 0, "a root is not on the hypersurface")
            if evaluate(forms[other][0], point) == 0:
                rejected_other += 1
                continue
            full = point + [stream.draw() for _ in range(15)]
            frame = kernel(matrix_at(layers, full))
            if frame is None:
                rejected_rank += 1
                continue
            vectors.append(plucker(frame))
            kept.append(full)
    vectors = vectors[:sample]
    differential = []
    for point in kept[:8]:
        frame = kernel(matrix_at(layers, point))
        if frame is None:
            raise RuntimeError("a kept point lost its kernel")
        gradient = [evaluate(part, point[:15]) for part in gradient_terms] + [0] * 15
        differential.append(differential_rank(layers, gradient, point, frame))
    stack = np.array(vectors, dtype=np.int64)
    span = flint.nmod_mat(240, 120, [int(v) for v in stack[:240].reshape(-1)], PRIME).rank()
    absent = [c for c in range(N) if not stack[:, [k for k, pair in enumerate(PAIRS) if c in pair]].any()]
    first = np.array([i for i, _ in QUADS])
    second = np.array([j for _, j in QUADS])
    ranks = {}
    for count in (sample - 1000, sample):
        products = (stack[:count, first] * stack[:count, second]) % PRIME
        ranks[count] = flint.nmod_mat(count, len(QUADS), products.reshape(-1).tolist(), PRIME).rank()
    # A generic point of the ambient space is no point of the stratum: the rank reads 16 there.
    generic = [stream.draw() for _ in range(30)]
    control = kernel(matrix_at(layers, generic)) is None and evaluate(terms, generic[:15]) != 0
    saturated = ranks[sample - 1000] == ranks[sample] < sample - 1000
    return {
        "stratum": name,
        "hypersurface_degree": degree,
        "lines_drawn": lines,
        "points": sample,
        "rejected_rank_below_14": rejected_rank,
        "rejected_on_other_hypersurface": rejected_other,
        "differential_rank_and_tangency_failures": differential,
        "gauss_image_dimension_lower_bound": max(rank for rank, _ in differential),
        "hilbert_function_degree_1": span,
        "hilbert_function_degree_2_by_sample": {str(count): rank for count, rank in ranks.items()},
        "degree_2_rank_stable": saturated,
        "grassmannian_hilbert_function": grassmannian_hilbert(N),
        "linear_forms_on_image": len(PAIRS) - span,
        "coordinates_zero_on_every_kernel_zero_based": absent,
        "grassmannian_of_the_remaining_coordinates_hilbert_function": grassmannian_hilbert(N - len(absent)),
        "quadrics_on_image": len(QUADS) - ranks[sample],
        "generic_point_control_rejected": control,
        "seconds": round(time.monotonic() - started, 1),
    }


def main() -> None:
    sample = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    data = setup()
    record: dict[str, Any] = {
        "schema": "a5-nullity4-gauss-image-probe-v2",
        "prediction": {"V(Q) minus V(G)": 3887, "V(G) minus V(Q)": 4022},
        "field": f"GF({PRIME}), i = {ROOT}",
        "strata": [
            stratum("V(Q) minus V(G)", "VQ", "VG", data, sample),
            stratum("V(G) minus V(Q)", "VG", "VQ", data, sample),
        ],
    }
    problems = [
        entry["stratum"]
        for entry in record["strata"]
        if not entry["degree_2_rank_stable"]
        or not entry["generic_point_control_rejected"]
        or entry["hilbert_function_degree_1"] != 105
        or entry["coordinates_zero_on_every_kernel_zero_based"] != [0]
        or entry["gauss_image_dimension_lower_bound"] != 15
        or entry["hilbert_function_degree_2_by_sample"][str(entry["points"])] != record["prediction"][entry["stratum"]]
        or any(failures for _, failures in entry["differential_rank_and_tangency_failures"])
    ]
    record["pass"] = problems == []
    print(json.dumps(record, indent=1))
    if problems:
        raise SystemExit(f"unstable rank, missed prediction, accepted control or tangency failure on {problems}")


if __name__ == "__main__":
    main()
