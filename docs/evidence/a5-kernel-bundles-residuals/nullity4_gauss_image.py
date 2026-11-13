"""The image of the nullity-4 kernel Gauss map: a plane bundle over the three-plane map z -> ker M(z), modulo 32029.

The bordered skew matrix A(z, w) of `kernel_frames._bordered_matrix` has first row -w and lower 15 x 15 block M(z),
linear in z; at a real point w is the conjugate of z. This producer treats z and w as independent, in split
coordinates z_k = i^popcount(k) z'_k, w_k = (-i)^popcount(k) w'_k, with i sent to 9115 modulo 32029, and measures at
deterministic points of the three nullity-4 strata V(Q) minus V(G), V(G) minus V(Q) and V(Q) n V(G):

- rank M(z) = 12 with z in ker M(z), and rank A(z, w) = 14 for every sampled w, on the stratum or off it;
- ker A(z, w) has first coordinate zero, lies in ker M(z) and is orthogonal to w: it is the plane ker M(z) n w-perp
  of the three-plane ker M(z);
- the rank of the differential of z -> ker M(z) on the stratum (the dimension of the family of three-planes), of
  the Gauss map (z, w) -> ker A(z, w) with w free and with w on the conjugate stratum, and of the pair (Gauss map,
  conjugate Gauss map) on stratum x conjugate stratum, which is the real rank of the Gauss map at real points;
- the number of linear forms and of quadrics in the 105 Plucker coordinates of Gr(2, 15) that vanish on the image,
  by interpolation at more points than there are monomials, with the rank read at two sample sizes.

Off the strata the control point has rank M = 14 with kernel spanned by z, and rank A = 16.

The retained fixture record `nullity4-kernel-gauss-result.json` (exact, characteristic 0, real points) is read for
one fact: at each of its 66 fixtures the 15 Plucker coordinates p_(0 j) vanish, the first-coordinate statement above.

The points come from sha256 of a label and a counter, reduced modulo 32029: a fixed list, with no seed.

`--write` writes nullity4-gauss-image-result.json beside this file; `--check` recomputes and compares.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_gauss_image.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from flint import nmod_mat, nmod_poly

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(BUNDLES))

import kernel_frames as frames  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-gauss-image-v1"
RECORD = HERE / "nullity4-gauss-image-result.json"
FIXTURES = HERE / "nullity4-kernel-gauss-result.json"
SOURCE_PATHS = (HERE / "nullity4_gauss_image.py", BUNDLES / "kernel_frames.py", FIXTURES)
PRIME, ROOT_OF_MINUS_ONE = 32029, 9115
FIELD = f"GF({PRIME}), i = {ROOT_OF_MINUS_ONE}"
IMAGINARY, BORDERED = 15, 16
STRATA = ("V(Q) minus V(G)", "V(G) minus V(Q)", "V(Q) intersect V(G)")
RANK_POINTS = 4
FREE_W_PER_POINT = 3
PLUCKER_PAIRS = tuple(itertools.combinations(range(1, BORDERED), 2))
QUADRIC_MONOMIALS = tuple(itertools.combinations_with_replacement(range(len(PLUCKER_PAIRS)), 2))
PLUCKER_QUADRICS = math.comb(IMAGINARY, 4)
LINEAR_SAMPLES = 300
QUADRIC_SAMPLES = (5800, 6100)
# Per stratum: rank of the three-plane map, of the Gauss map (w free, w on the conjugate stratum), the real rank,
# the dimension of the linear span of the image and the number of quadrics that vanish on it.
EXPECTED: dict[str, dict[str, int]] = {
    STRATA[0]: {
        "tangent_dimension": 14,
        "three_plane_map_rank": 13,
        "gauss_rank_w_free": 15,
        "real_rank": 26,
        "linear_span_dimension": 105,
        "quadrics_vanishing": 1678,
    },
    STRATA[1]: {
        "tangent_dimension": 14,
        "three_plane_map_rank": 13,
        "gauss_rank_w_free": 15,
        "real_rank": 26,
        "linear_span_dimension": 105,
        "quadrics_vanishing": 1543,
    },
    STRATA[2]: {
        "tangent_dimension": 13,
        "three_plane_map_rank": 10,
        "gauss_rank_w_free": 12,
        "real_rank": 24,
        "linear_span_dimension": 90,
        "quadrics_vanishing": 2940,
    },
}
SIGNS = tuple(
    tuple(cd_sign(BORDERED, row ^ column, column) if row and column and row != column else 0 for column in range(16))
    for row in range(16)
)
Vector = list[int]
Matrix = list[list[int]]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _flint(rows: Matrix) -> nmod_mat:
    return nmod_mat(len(rows), len(rows[0]), [value % PRIME for row in rows for value in row], PRIME)


def _rank(rows: Matrix) -> int:
    return int(_flint(rows).rank())


def _nullspace(rows: Matrix) -> Matrix:
    basis, nullity = _flint(rows).nullspace()
    return [[int(basis[i, j]) for i in range(len(rows[0]))] for j in range(nullity)]


class Points:
    """Coordinates modulo PRIME from sha256 of a label and a counter."""

    def __init__(self, label: str) -> None:
        self.label, self.counter = label, 0

    def value(self) -> int:
        self.counter += 1
        digest = hashlib.sha256(f"{self.label}:{self.counter}".encode()).digest()
        return int.from_bytes(digest[:8], "big") % PRIME

    def vector(self) -> Vector:
        return [self.value() for _ in range(IMAGINARY)]


def _twist(split: Sequence[int], unit: int) -> Vector:
    return [pow(unit, (index + 1).bit_count(), PRIME) * value % PRIME for index, value in enumerate(split)]


def bordered(point: Sequence[int], conjugate: bool = False) -> Matrix:
    """A(z, w) at the split point (z', w') of length 30; with `conjugate`, its complex conjugate A-bar(w, z)."""
    first, second = (point[IMAGINARY:], point[:IMAGINARY]) if conjugate else (point[:IMAGINARY], point[IMAGINARY:])
    unit = PRIME - ROOT_OF_MINUS_ONE if conjugate else ROOT_OF_MINUS_ONE
    z, w = _twist(first, unit), _twist(second, PRIME - unit)
    matrix = [[0] * BORDERED for _ in range(BORDERED)]
    for index in range(1, BORDERED):
        matrix[0][index], matrix[index][0] = -w[index - 1] % PRIME, w[index - 1]
    for row in range(1, BORDERED):
        for column in range(1, BORDERED):
            if row != column:
                matrix[row][column] = SIGNS[row][column] * z[(row ^ column) - 1] % PRIME
    return matrix


def conjugate_bordered(point: Sequence[int]) -> Matrix:
    return bordered(point, conjugate=True)


def lower_block(split: Sequence[int]) -> Matrix:
    """M(z): A(z, 0) without its first row and column."""
    return [row[1:] for row in bordered([*split, *([0] * IMAGINARY)])[1:]]


def _polynomials() -> dict[str, Any]:
    ideals = frames.regularity.closure_ideals()
    return {"Q": ideals["VQ"][0], "G": ideals["VG"][0]}


def _value(polynomial: Any, point: Sequence[int]) -> int:
    return int(polynomial(*point)) % PRIME


def _gradient(polynomial: Any, point: Sequence[int]) -> Vector:
    return [int(polynomial.derivative(index)(*point)) % PRIME for index in range(IMAGINARY)]


def _roots(function: Callable[[int], int], degree: int) -> list[int]:
    """Roots modulo PRIME of a univariate polynomial of at most the given degree, known through its values."""
    nodes = list(range(1, degree + 2))
    coefficients = [0] * (degree + 1)
    for node in nodes:
        numerator, denominator = [1], 1
        for other in nodes:
            if other != node:
                numerator = [
                    (low - other * high) % PRIME for low, high in zip([0, *numerator], [*numerator, 0], strict=True)
                ]
                denominator = denominator * (node - other) % PRIME
        scale = function(node) * pow(denominator, -1, PRIME) % PRIME
        for position, value in enumerate(numerator):
            coefficients[position] = (coefficients[position] + scale * value) % PRIME
    if not any(coefficients):
        return []
    return sorted(int(root) for root, _ in nmod_poly(coefficients, PRIME).roots())


def _on_hypersurface(polynomial: Any, degree: int, points: Points) -> Vector:
    """A point of the hypersurface: 14 coordinates from the list, the last one a root."""
    while True:
        point = points.vector()

        def restricted(last: int, base: Vector = point) -> int:
            return _value(polynomial, [*base[:-1], last])

        roots = _roots(restricted, degree)
        if roots:
            return [*point[:-1], roots[points.value() % len(roots)]]


def _on_intersection(polynomials: dict[str, Any], points: Points) -> Vector:
    """A point of V(Q) n V(G): the conic through a point of V(Q) along a pencil of directions, cut by G."""
    quadric, quartic = polynomials["Q"], polynomials["G"]
    while True:
        base, first, second = _on_hypersurface(quadric, 2, points), points.vector(), points.vector()

        def on_quadric(parameter: int, base: Vector = base, first: Vector = first, second: Vector = second) -> Vector:
            direction = [(a + parameter * b) % PRIME for a, b in zip(first, second, strict=True)]
            norm = _value(quadric, direction)
            polar = (_value(quadric, [(a + b) % PRIME for a, b in zip(base, direction, strict=True)]) - norm) % PRIME
            return [(norm * a - polar * b) % PRIME for a, b in zip(base, direction, strict=True)]

        for root in _roots(lambda parameter: _value(quartic, on_quadric(parameter)), 8):
            point = on_quadric(root)
            if any(point) and _value(quadric, point) == 0 and _value(quartic, point) == 0:
                return point


def sample(stratum: str, points: Points, polynomials: dict[str, Any]) -> Vector:
    """A point of the stratum in split coordinates, off the other hypersurface where the stratum excludes it."""
    while True:
        if stratum == STRATA[0]:
            point = _on_hypersurface(polynomials["Q"], 2, points)
            accepted = _value(polynomials["G"], point) != 0
        elif stratum == STRATA[1]:
            point = _on_hypersurface(polynomials["G"], 4, points)
            accepted = _value(polynomials["Q"], point) != 0
        else:
            point = _on_intersection(polynomials, points)
            accepted = True
        if accepted:
            return point


def tangent_space(stratum: str, point: Sequence[int], polynomials: dict[str, Any]) -> Matrix:
    names = {STRATA[0]: ("Q",), STRATA[1]: ("G",), STRATA[2]: ("Q", "G")}[stratum]
    return _nullspace([_gradient(polynomials[name], point) for name in names])


def _principal_pivots(matrix: Matrix, rank: int) -> list[int]:
    """Indices of an invertible principal block of a skew matrix of the given rank, grown two indices at a time."""
    pivots: list[int] = []
    while len(pivots) < rank:
        rest = [index for index in range(len(matrix)) if index not in pivots]
        for pair in itertools.combinations(rest, 2):
            trial = sorted([*pivots, *pair])
            if _rank([[matrix[a][b] for b in trial] for a in trial]) == len(trial):
                pivots = trial
                break
        else:
            raise RuntimeError("no principal block of full rank")
    return pivots


def kernel_differential(
    matrix_of: Callable[[Sequence[int]], Matrix], point: Sequence[int], directions: Matrix, rank: int
) -> tuple[Matrix, Matrix]:
    """Chart coordinates of d ker(matrix_of) along each direction, and the Schur frame of the kernel.

    matrix_of is linear. With principal pivots P and free rows F the frame is K = [-A_PP^-1 A_PF; I], and along a
    direction v tangent to the rank locus (K^T A(v) K = 0, which is checked) dK = -A_PP^-1 (A(v) K)_P, zero on F.
    """
    matrix = matrix_of(point)
    size = len(matrix)
    pivots = _principal_pivots(matrix, rank)
    free = [index for index in range(size) if index not in pivots]
    inverse = _flint([[matrix[a][b] for b in pivots] for a in pivots]).inv()
    upper = inverse * _flint([[-matrix[a][b] for b in free] for a in pivots])
    frame = [[0] * len(free) for _ in range(size)]
    for position, row in enumerate(pivots):
        frame[row] = [int(upper[position, column]) for column in range(len(free))]
    for position, row in enumerate(free):
        frame[row][position] = 1
    product = _flint(matrix) * _flint(frame)
    _require(product.rank() == 0, "the Schur frame leaves the kernel")
    rows = []
    for direction in directions:
        moved = _flint(matrix_of(direction)) * _flint(frame)
        _require((_flint(frame).transpose() * moved).rank() == 0, "a direction leaves the rank locus")
        change = inverse * _flint([[-int(moved[a, column]) for column in range(len(free))] for a in pivots])
        rows.append([int(change[i, j]) for i in range(len(pivots)) for j in range(len(free))])
    return rows, frame


def rank_point(job: tuple[str, int]) -> dict[str, Any]:
    """Every rank and kernel statement at one point of one stratum."""
    stratum, number = job
    polynomials = _polynomials()
    points = Points(f"rank:{stratum}:{number}")
    z, w_on = sample(stratum, points, polynomials), sample(stratum, points, polynomials)
    block = lower_block(z)
    block_kernel = _nullspace(block)
    twisted = _twist(z, ROOT_OF_MINUS_ONE)
    free_w = [points.vector() for _ in range(FREE_W_PER_POINT)]
    kernel_checks = []
    for w in [*free_w, w_on]:
        matrix = bordered([*z, *w])
        kernel = _nullspace(matrix)
        border = _twist(w, PRIME - ROOT_OF_MINUS_ONE)
        kernel_checks.append(
            {
                "rank_bordered": _rank(matrix),
                "first_coordinate_zero": all(vector[0] == 0 for vector in kernel),
                "inside_lower_kernel": _rank([*block_kernel, *(vector[1:] for vector in kernel)]) == len(block_kernel),
                "orthogonal_to_w": all(
                    sum(a * b for a, b in zip(border, vector[1:], strict=True)) % PRIME == 0 for vector in kernel
                ),
            }
        )
    tangent_z = tangent_space(stratum, z, polynomials)
    tangent_w = tangent_space(stratum, w_on, polynomials)
    zero = [0] * IMAGINARY
    along_z = [[*direction, *zero] for direction in tangent_z]
    every_w = [[*zero, *(int(i == k) for i in range(IMAGINARY))] for k in range(IMAGINARY)]
    along_w = [[*zero, *direction] for direction in tangent_w]
    three_planes, _ = kernel_differential(lower_block, z, tangent_z, IMAGINARY - len(block_kernel))
    free, _ = kernel_differential(bordered, [*z, *free_w[0]], [*along_z, *every_w], 14)
    on_stratum, _ = kernel_differential(bordered, [*z, *w_on], [*along_z, *along_w], 14)
    conjugate, _ = kernel_differential(conjugate_bordered, [*z, *w_on], [*along_z, *along_w], 14)
    return {
        "stratum": stratum,
        "point_sha256": hashlib.sha256(json.dumps([z, w_on, free_w]).encode()).hexdigest(),
        "rank_lower_block": _rank(block),
        "z_in_lower_kernel": _rank([*block_kernel, twisted]) == len(block_kernel),
        "kernels": kernel_checks,
        "tangent_dimension": len(tangent_z),
        "three_plane_map_rank": _rank(three_planes),
        "gauss_rank_w_free": _rank(free),
        "gauss_rank_w_on_conjugate_stratum": _rank(on_stratum),
        "real_rank": _rank([a + b for a, b in zip(on_stratum, conjugate, strict=True)]),
    }


def plucker(job: tuple[str, int]) -> Vector:
    """The 105 Plucker coordinates in Gr(2, 15) of ker A(z, w) at one point of the stratum with w free."""
    stratum, number = job
    points = Points(f"image:{stratum}:{number}")
    z = sample(stratum, points, _polynomials())
    kernel = _nullspace(bordered([*z, *points.vector()]))
    _require(len(kernel) == 2 and kernel[0][0] == 0 == kernel[1][0], "the kernel is not a plane in the last 15")
    return [(kernel[0][a] * kernel[1][b] - kernel[0][b] * kernel[1][a]) % PRIME for a, b in PLUCKER_PAIRS]


def image_equations(stratum: str) -> dict[str, Any]:
    """Linear span of the image and the count of quadrics vanishing on it, at two sample sizes."""
    rows = parallel.ordered_map(plucker, [(stratum, number) for number in range(QUADRIC_SAMPLES[-1])], min_items=2)
    quadrics = [[row[a] * row[b] % PRIME for a, b in QUADRIC_MONOMIALS] for row in rows]
    ranks = [_rank(quadrics[:count]) for count in QUADRIC_SAMPLES]
    return {
        "stratum": stratum,
        "linear_samples": LINEAR_SAMPLES,
        "linear_span_dimension": _rank(rows[:LINEAR_SAMPLES]),
        "plucker_coordinates": len(PLUCKER_PAIRS),
        "quadric_samples": list(QUADRIC_SAMPLES),
        "quadric_ranks": ranks,
        "quadric_monomials": len(QUADRIC_MONOMIALS),
        "quadrics_vanishing": len(QUADRIC_MONOMIALS) - ranks[-1],
        "plucker_quadrics": PLUCKER_QUADRICS,
    }


def control() -> dict[str, Any]:
    """A point off both hypersurfaces: M(z) has kernel z alone and A(z, w) is invertible."""
    polynomials = _polynomials()
    points = Points("control")
    while True:
        z = points.vector()
        if _value(polynomials["Q"], z) and _value(polynomials["G"], z):
            break
    block = lower_block(z)
    kernel = _nullspace(block)
    return {
        "rank_lower_block": _rank(block),
        "lower_kernel_is_z": len(kernel) == 1 and _rank([kernel[0], _twist(z, ROOT_OF_MINUS_ONE)]) == 1,
        "rank_bordered": _rank(bordered([*z, *points.vector()])),
    }


def fixtures() -> dict[str, int]:
    """In the retained exact record, the fixtures whose 15 coordinates p_(0 j) all vanish."""
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    order = list(itertools.combinations(range(BORDERED), 2))
    first = [position for position, pair in enumerate(order) if pair[0] == 0]
    vanishing = sum(all(row["normalized_plucker_coordinates"][position] == "0" for position in first) for row in rows)
    return {"fixtures": len(rows), "first_coordinate_zero": vanishing}


def compute() -> dict[str, Any]:
    jobs = [(stratum, number) for stratum in STRATA for number in range(RANK_POINTS)]
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS},
        "points": parallel.ordered_map(rank_point, jobs, min_items=2),
        "image": [image_equations(stratum) for stratum in STRATA],
        "control": control(),
        "exact_fixtures": fixtures(),
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    if (record.get("schema"), record.get("field")) != (SCHEMA, FIELD):
        problems.append("the record is headed otherwise")
    points = record["points"]
    if [row["stratum"] for row in points] != [stratum for stratum in STRATA for _ in range(RANK_POINTS)]:
        problems.append("the points differ from the sampled strata")
    if len({row["point_sha256"] for row in points}) != len(points):
        problems.append("two rank points coincide")
    for number, row in enumerate(points):
        name = f"{row['stratum']} point {number % RANK_POINTS}"
        expected = EXPECTED.get(row["stratum"], {})
        if row["rank_lower_block"] != 12 or row["z_in_lower_kernel"] is not True:
            problems.append(f"{name}: ker M(z) is not a three-plane through z")
        if len(row["kernels"]) != FREE_W_PER_POINT + 1:
            problems.append(f"{name}: {len(row['kernels'])} kernels")
        for kernel in row["kernels"]:
            if kernel != {
                "rank_bordered": 14,
                "first_coordinate_zero": True,
                "inside_lower_kernel": True,
                "orthogonal_to_w": True,
            }:
                problems.append(f"{name}: ker A(z, w) is not ker M(z) n w-perp")
        for key in ("tangent_dimension", "three_plane_map_rank", "gauss_rank_w_free", "real_rank"):
            if row[key] != expected.get(key):
                problems.append(f"{name}: {key} is {row[key]}, expected {expected.get(key)}")
        if row["gauss_rank_w_on_conjugate_stratum"] != row["gauss_rank_w_free"]:
            problems.append(f"{name}: the Gauss rank drops when w lies on the conjugate stratum")
    if [row["stratum"] for row in record["image"]] != list(STRATA):
        problems.append("the image rows differ from the three strata")
    for row in record["image"]:
        name, expected = row["stratum"], EXPECTED.get(row["stratum"], {})
        if row["quadric_samples"] != list(QUADRIC_SAMPLES) or row["quadric_samples"][0] <= row["quadric_monomials"]:
            problems.append(f"{name}: the quadric interpolation has too few samples")
        if len(set(row["quadric_ranks"])) != 1:
            problems.append(f"{name}: the quadric rank still grows between the two sample sizes")
        if row["quadrics_vanishing"] != row["quadric_monomials"] - row["quadric_ranks"][-1]:
            problems.append(f"{name}: the count of vanishing quadrics is not monomials minus rank")
        for key in ("linear_span_dimension", "quadrics_vanishing"):
            if row[key] != expected.get(key):
                problems.append(f"{name}: {key} is {row[key]}, expected {expected.get(key)}")
        if (row["plucker_coordinates"], row["quadric_monomials"], row["plucker_quadrics"]) != (
            len(PLUCKER_PAIRS),
            len(QUADRIC_MONOMIALS),
            PLUCKER_QUADRICS,
        ):
            problems.append(f"{name}: the coordinate counts differ from Gr(2, 15)")
    if record["control"] != {"rank_lower_block": 14, "lower_kernel_is_z": True, "rank_bordered": 16}:
        problems.append("the control point off the strata does not have ker M(z) = z and A invertible")
    exact = record["exact_fixtures"]
    if exact["fixtures"] != 66 or exact["first_coordinate_zero"] != exact["fixtures"]:
        problems.append("an exact fixture has a kernel vector with nonzero first coordinate")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(RECORD.read_text(encoding="utf-8")) != record:
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    for row in record["points"][::RANK_POINTS]:
        print(row["stratum"], row["three_plane_map_rank"], row["gauss_rank_w_free"], row["real_rank"])
    for row in record["image"]:
        print(row["stratum"], row["linear_span_dimension"], row["quadrics_vanishing"])


if __name__ == "__main__":
    main()
