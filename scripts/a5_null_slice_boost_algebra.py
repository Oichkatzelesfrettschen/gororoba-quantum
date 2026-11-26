"""Exact identities of the Clifford-defect operators on a Lorentzian slice of the 32-dimensional algebra A_5.

For a time index tau and spatial indices S the slice holds y = sum_a x_a e_a + t e_tau. With A_a = L_(e_a) and
J = L_(e_tau), the defect K_a = -(A_a J + J A_a)/2 measures the failure of A_a and J to anticommute. The record
checks, over Z and by FLINT ranks, the Gram identity L_y^T L_y = (r^2 + t^2) I + 2 t K(x), the cubic relation of
K(x), the so(n,1) commutation relations of the K_a, the kernel of L_y on the cone r^2 = t^2, the covariance algebra
of the slice, and the same statements on every axis-aligned slice of dimensions 16, 32 and 64. Independent slices
run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpz_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

DIMENSION = 32
TIME = 26
SPACE: tuple[int, ...] = (1, 3, 4, 5, 6, 7)
TIME_SUPPORT: tuple[int, ...] = (2, 8, 18, 24)
TOWER_DIMENSIONS: tuple[int, ...] = (16, 32, 64)
LIE_CAP = 60
LIE_SPACE_LIMIT = 8
SOURCE_FILES = ("gororoba_quantum/cd_core.py", "gororoba_quantum/parallel.py", "scripts/a5_null_slice_boost_algebra.py")
DETERMINANT_POINTS: tuple[tuple[tuple[int, ...], int], ...] = (
    ((1, 0, 0, 0, 0, 0), 0),
    ((0, 0, 0, 0, 0, 0), 1),
    ((2, 3, 6, 0, 0, 0), 5),
    ((1, 2, 3, 4, 5, 6), 7),
    ((3, 4, 0, 0, 0, 0), 5),
    ((1, -2, 2, 0, 4, -4), -3),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def left_tables(dimension: int) -> list[Any]:
    """L_(e_k) for every basis index: column q holds cd_sign(dimension, k, q) in row k XOR q."""
    tables = []
    for index in range(dimension):
        rows = [[0] * dimension for _ in range(dimension)]
        for column in range(dimension):
            rows[index ^ column][column] = cd_core.cd_sign(dimension, index, column)
        tables.append(fmpz_mat(rows))
    return tables


def identity(dimension: int) -> Any:
    return fmpz_mat([[int(row == column) for column in range(dimension)] for row in range(dimension)])


def zero(dimension: int) -> Any:
    return fmpz_mat(dimension, dimension)


def entries(matrix: Any) -> list[list[int]]:
    return [[int(value) for value in row] for row in matrix.tolist()]


def halve(matrix: Any) -> Any:
    rows = entries(matrix)
    require(all(value % 2 == 0 for row in rows for value in row), "defect entries are even")
    return fmpz_mat([[value // 2 for value in row] for row in rows])


def defects(lefts: list[Any], time: int, space: tuple[int, ...]) -> dict[int, Any]:
    clock = lefts[time]
    return {a: halve(-1 * (lefts[a] * clock + clock * lefts[a])) for a in space}


def combination(matrices: dict[int, Any], space: tuple[int, ...], point: tuple[int, ...]) -> Any:
    dimension = matrices[space[0]].nrows()
    total = zero(dimension)
    for a, value in zip(space, point, strict=True):
        total = total + value * matrices[a]
    return total


def slice_invariants() -> dict[str, Any]:
    """Q, Delta and G of the strata record restricted to real slices with time coordinate t on index 26.

    The imaginary unit is the symbol i, reduced by i^2 = -1 after expansion, so every step is integer polynomial
    arithmetic.
    """
    names = {index: sp.Symbol(f"x{index}") for index in range(1, 16)}
    t, unit = sp.Symbol("t"), sp.Symbol("i")

    def parts(expression: Any) -> tuple[Any, Any]:
        polynomial = sp.Poly(sp.expand(expression), unit)
        real, imaginary = sp.Integer(0), sp.Integer(0)
        for (degree,), coefficient in polynomial.terms():
            sign = (1, 1, -1, -1)[degree % 4]
            if degree % 2:
                imaginary += sign * coefficient
            else:
                real += sign * coefficient
        return sp.expand(real), sp.expand(imaginary)

    def restricted(space: tuple[int, ...], factor: bool) -> dict[str, Any]:
        z = [sp.Integer(0)] * 16
        for index in space:
            z[index] = names[index]
        z[TIME - 16] = z[TIME - 16] + unit * t
        u, mu, v = z[1:8], z[8], z[9:16]
        big_u = sum(value * value for value in u)
        big_v = sum(value * value for value in v)
        big_w = sum(first * second for first, second in zip(u, v, strict=True))
        q_real, q_imag = parts(big_u + mu * mu + big_v)
        d_real, d_imag = parts(big_u * big_v - big_w * big_w)
        g_real = sp.expand(q_real * q_real - q_imag * q_imag - 4 * d_real)
        g_imag = sp.expand(2 * q_real * q_imag - 4 * d_imag)
        show = (
            (lambda value: str(sp.factor(value))) if factor else (lambda value: f"{len(sp.Add.make_args(value))} terms")
        )
        return {
            "Q_real": str(sp.factor(q_real)),
            "Q_imag": str(sp.factor(q_imag)),
            "Delta_real": show(d_real),
            "G_real": show(g_real),
            "G_imag": show(g_imag),
            "_g": (g_real, g_imag, q_real),
        }

    radius = sum(names[index] ** 2 for index in SPACE)
    six = restricted(SPACE, True)
    g_real, g_imag, q_real = six.pop("_g")
    require(sp.expand(q_real - (radius - t * t)) == 0, "Q = r^2 - t^2 on the slice")
    require(sp.expand(g_real - (radius + t * t) ** 2) == 0 and g_imag == 0, "G = (r^2 + t^2)^2 on the slice")
    rows = {"six_plus_time": six}
    for label, space, factor in (
        ("six_with_e2", (*SPACE, 2), True),
        ("six_with_e8", (*SPACE, 8), True),
        ("fourteen_plus_time", tuple(index for index in range(1, 16) if index != TIME - 16), False),
    ):
        row = restricted(space, factor)
        row.pop("_g")
        rows[label] = row
    return rows


def cubic_failures(matrices: dict[int, Any], space: tuple[int, ...]) -> list[int]:
    """Coefficients of K(x)^3 - r^2 K(x) over the cubic monomials of x: [monomials, nonzero coefficients]."""
    dimension = matrices[space[0]].nrows()
    failed = 0
    monomials = 0
    for multiset in combinations_with_replacement(space, 3):
        monomials += 1
        left = zero(dimension)
        for first, second, third in set(permutations(multiset)):
            left = left + matrices[first] * matrices[second] * matrices[third]
        distinct = set(multiset)
        if len(distinct) == 3:
            right = zero(dimension)
        elif len(distinct) == 1:
            right = matrices[multiset[0]]
        else:
            right = matrices[next(index for index in distinct if multiset.count(index) == 1)]
        failed += int(left != right)
    return [monomials, failed]


def operator_identities(lefts: list[Any], time: int, space: tuple[int, ...]) -> dict[str, Any]:
    dimension = lefts[0].nrows()
    one = identity(dimension)
    clock = lefts[time]
    matrices = defects(lefts, time, space)
    anticommute = all(
        lefts[a] * lefts[b] + lefts[b] * lefts[a] == (-2 * one if a == b else zero(dimension))
        for a in space
        for b in space
    )
    skew = all(lefts[index].transpose() == -1 * lefts[index] for index in (*space, time))
    trace_squares = sorted({int(sum((matrices[a] * matrices[a])[i, i] for i in range(dimension))) for a in space})
    return {
        "left_tables_skew": skew,
        "space_tables_anticommute_and_square_to_minus_one": anticommute,
        "clock_squares_to_minus_one": clock * clock == -1 * one,
        "defects_symmetric": all(matrices[a].transpose() == matrices[a] for a in space),
        "defect_traces": sorted({int(sum(matrices[a][i, i] for i in range(dimension))) for a in space}),
        "defect_square_traces": trace_squares,
        "defect_ranks": sorted({int(matrices[a].rank()) for a in space}),
        "cubic_relation": cubic_failures(matrices, space),
    }


def gram_identity(lefts: list[Any], time: int, space: tuple[int, ...], point: tuple[int, ...], t: int) -> bool:
    dimension = lefts[0].nrows()
    operand = combination({a: lefts[a] for a in space}, space, point) + t * lefts[time]
    radius = sum(value * value for value in point)
    gram = operand.transpose() * operand
    return bool(
        gram == (radius + t * t) * identity(dimension) + 2 * t * combination(defects(lefts, time, space), space, point)
    )


def determinant_rows(lefts: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for point, t in DETERMINANT_POINTS:
        operand = combination({a: lefts[a] for a in SPACE}, SPACE, point) + t * lefts[TIME]
        radius = sum(value * value for value in point)
        expected = (radius - t * t) ** 4 * (radius + t * t) ** 12
        rows.append(
            {
                "x": list(point),
                "t": t,
                "determinant": str(operand.det()),
                "formula": str(expected),
                "nullity": DIMENSION - int(operand.rank()),
                "gram_identity": gram_identity(lefts, TIME, SPACE, point, t),
            }
        )
        require(rows[-1]["determinant"] == rows[-1]["formula"], "det L_y = (r^2 - t^2)^4 (r^2 + t^2)^12")
    return rows


def triple_failures(matrices: dict[int, Any], space: tuple[int, ...]) -> list[int]:
    """[[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b over a < b and every c: [relations, failures]."""
    dimension = matrices[space[0]].nrows()
    total = 0
    failed = 0
    for a, b in combinations(space, 2):
        rotation = matrices[a] * matrices[b] - matrices[b] * matrices[a]
        for c in space:
            total += 1
            left = rotation * matrices[c] - matrices[c] * rotation
            right = (matrices[a] if b == c else zero(dimension)) - (matrices[b] if a == c else zero(dimension))
            failed += int(left != right)
    return [total, failed]


def flat(matrix: Any) -> list[int]:
    return [value for row in entries(matrix) for value in row]


def lie_dimension(generators: list[Any], cap: int = LIE_CAP) -> dict[str, Any]:
    """Dimension over Q of the Lie algebra the generators span under commutators, stopped at cap."""
    rows: list[list[int]] = []
    basis: list[Any] = []

    def admit(matrix: Any) -> None:
        candidate = flat(matrix)
        if any(candidate) and int(fmpz_mat([*rows, candidate]).rank()) == len(rows) + 1:
            rows.append(candidate)
            basis.append(matrix)

    for generator in generators:
        admit(generator)
    position = 0
    while position < len(basis) and len(basis) < cap:
        for earlier in range(position):
            admit(basis[position] * basis[earlier] - basis[earlier] * basis[position])
            if len(basis) >= cap:
                break
        position += 1
    return {"dimension": len(basis), "capped": len(basis) >= cap}


def column_span(matrices: list[Any]) -> int:
    stacked = [row for matrix in matrices for row in entries(matrix.transpose())]
    return int(fmpz_mat(stacked).rank())


def boost_algebra(lefts: list[Any], time: int, space: tuple[int, ...], support: tuple[int, ...]) -> dict[str, Any]:
    dimension = lefts[0].nrows()
    one = identity(dimension)
    matrices = defects(lefts, time, space)
    products = [matrices[a] * matrices[a] * matrices[b] * matrices[b] for a, b in combinations(space, 2)]
    projector = products[0]
    diagonal = [int(projector[i, i]) for i in range(dimension)]
    is_diagonal = projector == fmpz_mat(
        [[diagonal[r] if r == c else 0 for c in range(dimension)] for r in range(dimension)]
    )
    form = one - 2 * projector
    stacked = fmpz_mat([row for a in space for row in entries(matrices[a])])
    kernel_basis, nullity = stacked.nullspace()
    kernel_support = sorted(
        {row for row in range(dimension) for column in range(int(nullity)) if kernel_basis[row, column] != 0}
    )
    orbits = {}
    orbit_ok = True
    for m in support:
        unit = fmpz_mat([[int(row == m)] for row in range(dimension)])
        images = {a: matrices[a] * unit for a in space}
        signed = {}
        for a in space:
            column = [int(images[a][row, 0]) for row in range(dimension)]
            nonzero = [(row, value) for row, value in enumerate(column) if value]
            orbit_ok = orbit_ok and len(nonzero) == 1 and abs(nonzero[0][1]) == 1
            signed[str(a)] = [nonzero[0][0], nonzero[0][1]] if len(nonzero) == 1 else nonzero
            for b in space:
                orbit_ok = orbit_ok and matrices[b] * images[a] == (unit if a == b else fmpz_mat(dimension, 1))
        orbits[str(m)] = signed
    orbit_indices = sorted([m for m in support] + [value[0] for signed in orbits.values() for value in signed.values()])
    return {
        "triple_relations": triple_failures(matrices, space),
        "lie_dimension": lie_dimension([matrices[a] for a in space]),
        "time_projector_common": all(product == projector for product in products),
        "time_projector_diagonal": bool(is_diagonal),
        "time_support": [index for index, value in enumerate(diagonal) if value],
        "defects_anticommute_with_form": all(matrices[a] * form + form * matrices[a] == zero(dimension) for a in space),
        "range_span": column_span([matrices[a] for a in space]),
        "common_kernel_dimension": int(nullity),
        "common_kernel_support": kernel_support,
        "vector_orbits": orbits,
        "vector_orbits_are_boosts": bool(orbit_ok),
        "orbit_indices_distinct": len(set(orbit_indices)) == len(orbit_indices) == len(support) * (len(space) + 1),
        "disjoint_stars": disjoint_stars(matrices, space),
    }


def conjugate_maps(lefts: list[Any], time: int, space: tuple[int, ...], support: tuple[int, ...]) -> dict[str, Any]:
    """Phi_m(y) = (t - K(x)) e_m satisfies y Phi_m(y) = sign (r^2 - t^2) e_target, coefficient by coefficient."""
    dimension = lefts[0].nrows()
    matrices = defects(lefts, time, space)
    clock = lefts[time]
    rows = {}
    for m in support:
        unit = fmpz_mat([[int(row == m)] for row in range(dimension)])
        time_square = [int((clock * unit)[row, 0]) for row in range(dimension)]
        nonzero = [(row, value) for row, value in enumerate(time_square) if value]
        require(len(nonzero) == 1, "J e_m is a signed basis vector")
        target, sign = nonzero[0][0], -nonzero[0][1]
        expected = fmpz_mat([[sign * int(row == target)] for row in range(dimension)])
        mixed = all(lefts[a] * unit - clock * (matrices[a] * unit) == fmpz_mat(dimension, 1) for a in space)
        quadratic = all(
            -1 * (lefts[a] * (matrices[b] * unit) + lefts[b] * (matrices[a] * unit))
            == (2 * expected if a == b else fmpz_mat(dimension, 1))
            for a in space
            for b in space
        )
        rows[str(m)] = {"target": target, "sign": sign, "t_x_coefficients_vanish": mixed, "x_x_coefficients": quadratic}
    return rows


def kernel_formula(lefts: list[Any], time: int, space: tuple[int, ...], support: tuple[int, ...]) -> dict[str, Any]:
    """On the cone the four vectors (t - K(x)) e_m lie in ker L_y and are independent, so they span it."""
    dimension = lefts[0].nrows()
    matrices = defects(lefts, time, space)
    rows = []
    for point, t in (
        ((1, 0, 0, 0, 0, 0), 1),
        ((1, 0, 0, 0, 0, 0), -1),
        ((3, 4, 0, 0, 0, 0), 5),
        ((2, 3, 6, 0, 0, 0), -7),
    ):
        operand = combination({a: lefts[a] for a in space}, space, point) + t * lefts[time]
        shift = t * identity(dimension) - combination(matrices, space, point)
        columns = fmpz_mat([[int(shift[row, m]) for m in support] for row in range(dimension)])
        rows.append(
            {
                "x": list(point),
                "t": t,
                "annihilated": operand * columns == fmpz_mat(dimension, len(support)),
                "span_rank": int(columns.rank()),
                "nullity": dimension - int(operand.rank()),
            }
        )
    return {"points": rows}


def covariance() -> dict[str, Any]:
    """Pairs (X, Y) and generators w of so(6,1) with X L_y + L_y Y = L_(w y) for every y of the slice.

    The unknowns are the entries of X and Y and one coefficient per generator. The image dimension is the rank of the
    projection of the solution space onto the generator coefficients: nullity(all columns) - nullity(X, Y columns).
    """
    lefts = left_tables(DIMENSION)
    frame = (*SPACE, TIME)
    size = len(frame)
    generators: list[tuple[str, list[list[int]]]] = []
    for a, b in combinations(range(size), 2):
        matrix = [[0] * size for _ in range(size)]
        boost = frame[b] == TIME
        matrix[a][b] = 1
        matrix[b][a] = 1 if boost else -1
        generators.append(("boost" if boost else "rotation", matrix))
    tables = {index: entries(lefts[index]) for index in frame}
    block = DIMENSION * DIMENSION

    def system(kinds: tuple[str, ...]) -> tuple[int, int]:
        chosen = [matrix for kind, matrix in generators if kind in kinds]
        rows = []
        for position, index in enumerate(frame):
            table = tables[index]
            images = []
            for matrix in chosen:
                image = [[0] * DIMENSION for _ in range(DIMENSION)]
                for other in range(size):
                    weight = matrix[other][position]
                    if weight:
                        source = tables[frame[other]]
                        for r in range(DIMENSION):
                            for c in range(DIMENSION):
                                image[r][c] += weight * source[r][c]
                images.append(image)
            for r in range(DIMENSION):
                for c in range(DIMENSION):
                    row = [0] * (2 * block + len(chosen))
                    for k in range(DIMENSION):
                        if table[k][c]:
                            row[r * DIMENSION + k] = table[k][c]
                        if table[r][k]:
                            row[block + k * DIMENSION + c] = table[r][k]
                    for g, image in enumerate(images):
                        row[2 * block + g] = -image[r][c]
                    rows.append(row)
        full = fmpz_mat(rows)
        rank_full = int(full.rank())
        rank_plain = int(fmpz_mat([row[: 2 * block] for row in rows]).rank())
        return len(chosen), (2 * block + len(chosen) - rank_full) - (2 * block - rank_plain)

    result = {}
    for label, kinds in (("so_6_1", ("rotation", "boost")), ("rotations", ("rotation",)), ("boosts", ("boost",))):
        count, image = system(kinds)
        result[label] = {"generators": count, "covariant_dimension": image}
    return result


def pair_nullities(dimension: int, lefts: list[Any], k: int) -> list[int]:
    """Nullity of e_j + e_(h+k) and of e_j - e_(h+k), j = 1 .. h - 1; a clean j has nullity 4 for both signs."""
    half = dimension // 2
    values = []
    for j in range(1, half):
        plus = dimension - int((lefts[j] + lefts[half + k]).rank())
        minus = dimension - int((lefts[j] - lefts[half + k]).rank())
        values.append(plus if plus == minus else -1)
    return values


def clifford(lefts: list[Any], space: tuple[int, ...]) -> bool:
    """The spatial tables anticommute pairwise and square to -I, which the Gram identity requires."""
    dimension = lefts[0].nrows()
    one = identity(dimension)
    return all(
        lefts[a] * lefts[b] + lefts[b] * lefts[a] == (-2 * one if a == b else zero(dimension))
        for a in space
        for b in space
        if a <= b
    )


def disjoint_stars(matrices: dict[int, Any], space: tuple[int, ...]) -> bool:
    """Each defect is a symmetric signed partial permutation exchanging one common index set with its own leaves.

    With T the common support, K_a maps T onto a leaf set S_a, the S_a are pairwise disjoint and disjoint from T.
    On span(e_m, K_a e_m) for m in T the defects then act as the boosts E_(0a) + E_(a0).
    """
    supports: dict[int, set[int]] = {}
    images: dict[int, dict[int, int]] = {}
    for a in space:
        rows = entries(matrices[a])
        image = {}
        for row, values in enumerate(rows):
            nonzero = [(column, value) for column, value in enumerate(values) if value]
            if len(nonzero) > 1 or any(abs(value) != 1 for _column, value in nonzero):
                return False
            if nonzero:
                image[row] = nonzero[0][0]
        supports[a] = set(image)
        images[a] = image
    common = set.intersection(*supports.values())
    leaves = {a: supports[a] - common for a in space}
    if not common or any({images[a][m] for m in common} != leaves[a] for a in space):
        return False
    return all(not (leaves[a] & leaves[b]) for a, b in combinations(space, 2))


def tower_item(item: tuple[int, int]) -> dict[str, Any]:
    dimension, k = item
    lefts = left_tables(dimension)
    half = dimension // 2
    nullities = pair_nullities(dimension, lefts, k)
    clean = tuple(j for j, value in zip(range(1, half), nullities, strict=True) if value == 4)
    row: dict[str, Any] = {
        "dimension": dimension,
        "time": half + k,
        "nullity_histogram": {str(key): count for key, count in sorted(Counter(nullities).items())},
        "clean": list(clean),
    }
    if len(clean) >= 2:
        matrices = defects(lefts, half + k, clean)
        operand = 3 * lefts[clean[0]] + 4 * lefts[clean[1]] + 5 * lefts[half + k]
        small = len(clean) <= LIE_SPACE_LIMIT
        row["cubic_relation"] = cubic_failures(matrices, clean) if small else None
        row["triple_relations"] = triple_failures(matrices, clean)
        row["lie_dimension"] = lie_dimension([matrices[a] for a in clean]) if small else None
        row["range_span"] = column_span([matrices[a] for a in clean])
        row["defect_ranks"] = sorted({int(matrices[a].rank()) for a in clean})
        row["null_point_nullity"] = dimension - int(operand.rank())
        row["space_clifford"] = clifford(lefts, clean)
        row["gram_identity"] = gram_identity(lefts, half + k, clean, tuple(range(1, len(clean) + 1)), 2)
        row["disjoint_stars"] = disjoint_stars(matrices, clean)
    return row


def tower_control() -> dict[str, Any]:
    items = [(dimension, k) for dimension in TOWER_DIMENSIONS for k in range(1, dimension // 2)]
    rows = parallel.ordered_map(tower_item, items, min_items=1)
    passing = [
        [row["dimension"], row["time"]] for row in rows if "triple_relations" in row and row["triple_relations"][1] == 0
    ]
    summary = {}
    for dimension in TOWER_DIMENSIONS:
        chosen = [row for row in rows if row["dimension"] == dimension]
        summary[str(dimension)] = {
            "clean_sizes": dict(sorted(Counter(str(len(row["clean"])) for row in chosen).items())),
            "lie_dimensions": dict(
                sorted(
                    Counter(
                        str(row["lie_dimension"]["dimension"]) for row in chosen if row.get("lie_dimension")
                    ).items()
                )
            ),
            "slices_with_so_n_1_relations": sum(1 for d, _time in passing if d == dimension),
            "slices_with_clifford_space": sum(1 for row in chosen if row.get("space_clifford")),
            "slices_with_gram_identity": sum(1 for row in chosen if row.get("gram_identity")),
        }
    return {"rows": rows, "slices_with_so_n_1_relations": passing, "summary": summary}


def family_item(level: int) -> dict[str, Any]:
    """The slice of A_level with time index 7 * 2^(level-3) and space {1 .. 2^(level-2) - 1} minus 2^(level-3).

    Prediction recorded before the first run of levels 4 and 7: the defects satisfy the so(m,1) relations with
    m = 2^(level-2) - 2, their ranges span 4 (m + 1) = 2^level - 4 dimensions and their common kernel has dimension 4.
    """
    dimension = 1 << level
    time = 7 << (level - 3)
    space = tuple(index for index in range(1, 1 << (level - 2)) if index != 1 << (level - 3))
    lefts = left_tables(dimension)
    matrices = defects(lefts, time, space)
    operand = 3 * lefts[space[0]] + 4 * lefts[space[1]] + 5 * lefts[time]
    span = column_span([matrices[a] for a in space])
    return {
        "level": level,
        "dimension": dimension,
        "time": time,
        "space_size": len(space),
        "triple_relations": triple_failures(matrices, space),
        "defect_ranks": sorted({int(matrices[a].rank()) for a in space}),
        "range_span": span,
        "common_kernel_dimension": dimension - span,
        "null_point_nullity": dimension - int(operand.rank()),
        "space_clifford": clifford(lefts, space),
        "disjoint_stars": disjoint_stars(matrices, space),
    }


def family_control() -> list[dict[str, Any]]:
    return list(parallel.ordered_map(family_item, [4, 5, 6, 7], min_items=1))


def octonion_space_item(level: int) -> dict[str, Any]:
    """The slice of A_level with time index 2^(level-1) + 2^(level-2) + 8 and the seven octonion units as space.

    Prediction recorded before the first run, from a reviewer's conjecture checked by the reviewer at level 6:
    Clifford space, the Gram identity, the 147 relations of so(7,1) and disjoint stars, at levels 6 and 7.
    """
    dimension = 1 << level
    time = (1 << (level - 1)) + (1 << (level - 2)) + 8
    space = tuple(range(1, 8))
    lefts = left_tables(dimension)
    matrices = defects(lefts, time, space)
    operand = 3 * lefts[1] + 4 * lefts[2] + 5 * lefts[time]
    span = column_span([matrices[a] for a in space])
    return {
        "level": level,
        "dimension": dimension,
        "time": time,
        "space_clifford": clifford(lefts, space),
        "gram_identity": gram_identity(lefts, time, space, (1, 2, 3, 4, 5, 6, 7), 2),
        "triple_relations": triple_failures(matrices, space),
        "disjoint_stars": disjoint_stars(matrices, space),
        "range_span": span,
        "null_point_nullity": dimension - int(operand.rank()),
    }


def octonion_space_control() -> list[dict[str, Any]]:
    return list(parallel.ordered_map(octonion_space_item, [6, 7], min_items=1))


def real_slice_nullities(lefts: list[Any]) -> dict[str, Any]:
    axis = {str(j): DIMENSION - int((lefts[j] + lefts[TIME]).rank()) for j in range(1, 16)}
    mixed = {
        "3e2+4e8+5e26": DIMENSION - int((3 * lefts[2] + 4 * lefts[8] + 5 * lefts[TIME]).rank()),
        "3e1+4e2+5e26": DIMENSION - int((3 * lefts[1] + 4 * lefts[2] + 5 * lefts[TIME]).rank()),
        "3e1+4e8+5e26": DIMENSION - int((3 * lefts[1] + 4 * lefts[8] + 5 * lefts[TIME]).rank()),
        "3e9+4e11": DIMENSION - int((3 * lefts[9] + 4 * lefts[11]).rank()),
        "e1+e9": DIMENSION - int((lefts[1] + lefts[9]).rank()),
        "e1+e11": DIMENSION - int((lefts[1] + lefts[11]).rank()),
    }
    return {"e_j_plus_e_26": axis, "named_points": mixed}


def specification_agreement(lefts: list[Any]) -> bool:
    vector = [0] * DIMENSION
    vector[3], vector[TIME], vector[9] = 2, -5, 7
    expected = cd_core.left_mult_matrix_exact(DIMENSION, vector)
    built = 2 * lefts[3] - 5 * lefts[TIME] + 7 * lefts[9]
    return entries(built) == [[int(value) for value in row] for row in expected]


def source_digests() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def build_result() -> dict[str, Any]:
    lefts = left_tables(DIMENSION)
    require(specification_agreement(lefts), "left tables agree with cd_core.left_mult_matrix_exact")
    result = {
        "schema": "a5-null-slice-boost-algebra/1",
        "slice": {"dimension": DIMENSION, "time": TIME, "space": list(SPACE), "time_support": list(TIME_SUPPORT)},
        "invariants": slice_invariants(),
        "operator_identities": operator_identities(lefts, TIME, SPACE),
        "determinant": determinant_rows(lefts),
        "boost_algebra": boost_algebra(lefts, TIME, SPACE, TIME_SUPPORT),
        "conjugate_maps": conjugate_maps(lefts, TIME, SPACE, TIME_SUPPORT),
        "kernel_formula": kernel_formula(lefts, TIME, SPACE, TIME_SUPPORT),
        "real_slice_nullities": real_slice_nullities(lefts),
        "covariance": covariance(),
        "tower_control": tower_control(),
        "family_control": family_control(),
        "octonion_space_control": octonion_space_control(),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    """The statements the README draws from the record; a failed one ends the run."""
    identities = result["operator_identities"]
    require(identities["left_tables_skew"] and identities["clock_squares_to_minus_one"], "skew tables")
    require(identities["space_tables_anticommute_and_square_to_minus_one"], "spatial Clifford relations")
    require(identities["defects_symmetric"] and identities["defect_traces"] == [0], "symmetric traceless defects")
    require(identities["defect_square_traces"] == [8] and identities["defect_ranks"] == [8], "defect rank 8")
    require(identities["cubic_relation"] == [56, 0], "K^3 = r^2 K on 56 cubic coefficients")
    algebra = result["boost_algebra"]
    require(algebra["triple_relations"] == [90, 0], "so(6,1) relations")
    require(algebra["lie_dimension"] == {"dimension": 21, "capped": False}, "Lie dimension 21")
    require(algebra["time_projector_common"] and algebra["time_projector_diagonal"], "common time projector")
    require(algebra["time_support"] == list(TIME_SUPPORT), "time support")
    require(algebra["defects_anticommute_with_form"], "defects lie in so of the Lorentzian form")
    require(algebra["range_span"] == 28 and algebra["common_kernel_dimension"] == 4, "28 + 4 decomposition")
    require(algebra["vector_orbits_are_boosts"] and algebra["orbit_indices_distinct"], "four vector modules")
    require(algebra["disjoint_stars"], "disjoint stars on the slice")
    for row in result["conjugate_maps"].values():
        require(row["t_x_coefficients_vanish"] and row["x_x_coefficients"], "y Phi_m(y) = sign Q e_target")
    for row in result["kernel_formula"]["points"]:
        require(row["annihilated"] and row["span_rank"] == 4 and row["nullity"] == 4, "kernel formula")
    covariant = result["covariance"]
    require(covariant["so_6_1"]["covariant_dimension"] == 8, "covariance algebra of dimension 8")
    require(
        covariant["rotations"]["covariant_dimension"] == 8 and covariant["boosts"]["covariant_dimension"] == 0,
        "no boost",
    )
    passing = result["tower_control"]["slices_with_so_n_1_relations"]
    expected = [[32, time] for time in range(25, 32)] + [[64, time] for time in range(49, 64)]
    require(
        passing == expected, "so(n,1) relations hold for time index 25..31 of dimension 32 and 49..63 of dimension 64"
    )
    for row in result["tower_control"]["rows"]:
        if "triple_relations" in row:
            require(row["disjoint_stars"] == (row["triple_relations"][1] == 0), "stars decide the so(n,1) relations")
            require(row["gram_identity"] == row["space_clifford"], "the Gram identity holds exactly on Clifford spaces")
    for row in result["octonion_space_control"]:
        require(row["space_clifford"] and row["gram_identity"] and row["disjoint_stars"], "octonion-space slice")
        require(row["triple_relations"] == [147, 0] and row["range_span"] == 32, "so(7,1) on the octonion-space slice")
        require(row["null_point_nullity"] == 4, "octonion-space nullity 4")
    for row in result["family_control"]:
        require(row["disjoint_stars"], "family slice has disjoint stars")
        size = (1 << (row["level"] - 2)) - 2
        require(row["space_size"] == size and row["triple_relations"][1] == 0, "family slice satisfies so(m,1)")
        require(
            row["range_span"] == row["dimension"] - 4 and row["common_kernel_dimension"] == 4, "four vector modules"
        )
        require(row["defect_ranks"] == [8] and row["null_point_nullity"] == 4, "family defect rank 8 and nullity 4")


def self_test() -> None:
    lefts = left_tables(DIMENSION)
    require(specification_agreement(lefts), "specification agreement")
    require(operator_identities(lefts, TIME, SPACE)["cubic_relation"] == [56, 0], "baseline cubic relation")
    with_e2 = (1, 2, 3, 4, 5, 6, 7)
    require(
        cubic_failures(defects(lefts, TIME, with_e2), with_e2)[1] > 0, "the direction e_2 breaks the cubic relation"
    )
    other = tuple(range(10, 16))
    require(triple_failures(defects(lefts, 17, other), other)[1] > 0, "the slice with time e_17 fails so(6,1)")
    sedenion = left_tables(16)
    require(triple_failures(defects(sedenion, 10, SPACE), SPACE)[1] > 0, "the sedenion slice fails so(6,1)")
    flipped = list(lefts)
    rows = entries(lefts[TIME])
    column = next(c for c in range(DIMENSION) if rows[0][c])
    rows[0][column] = -rows[0][column]
    flipped[TIME] = fmpz_mat(rows)
    require(flipped[TIME] * flipped[TIME] != -1 * identity(DIMENSION), "a flipped clock entry breaks J^2 = -I")
    wrong_support = (2, 8, 18, 0)
    wrong = conjugate_maps(lefts, TIME, SPACE, wrong_support)["0"]
    require(not (wrong["t_x_coefficients_vanish"] and wrong["x_x_coefficients"]), "index 0 is outside the time support")
    wrong_kernel = kernel_formula(lefts, TIME, SPACE, wrong_support)["points"][0]
    require(not wrong_kernel["annihilated"], "a wrong support vector leaves the kernel")
    require(gram_identity(lefts, TIME, SPACE, (2, 3, 6, 0, 0, 0), 5), "Gram identity holds at an off-cone point")
    shifted = 2 * lefts[1] + 3 * lefts[3] + 6 * lefts[4] + 5 * lefts[TIME]
    require(
        (shifted.transpose() * shifted) != (49 + 26) * identity(DIMENSION),
        "the Gram operator is not scalar off the cone",
    )
    print("self-test passed: 8 controls")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the record")
    mode.add_argument("--check", type=Path, help="recompute and compare with a written record")
    mode.add_argument("--self-test", action="store_true", help="run the mutation controls")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
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
