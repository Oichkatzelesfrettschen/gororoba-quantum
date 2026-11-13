"""Components of the centralizer of G_2 in the group of constant kernel-pencil symmetries of A_5.

A constant kernel-pencil symmetry is a triple (G, P, Q) of invertible linear maps, G on the doubly pure space U
and P, Q on A_5, with Q L_y = L_(G y) P for every y in U. The group K of such triples has identity component with
Lie algebra g_2 plus four central directions (`../a5-kernel-bundles/README.md`). `Out(g_2)` is trivial and g_2 is
the derived algebra of Lie(K), so every component of K meets the centralizer Z of G_2 in K; Z meets the identity
component G_2 T in the connected central torus T, because G_2 has trivial center; hence pi_0(K) = pi_0(Z). This
script counts the components of the complex algebraic group Z_C and deduces pi_0 of the real group.

Structure. An element of Z commutes with G_2, so P, Q and G act on the multiplicity spaces of the trivial and the
7-dimensional representation. The identity component of Z is the torus T with Lie algebra spanned by the base
scaling (1, 0, 1), the domain scaling (0, 1, 1), the vertical phase (0, J, -J) and the base-phase lift (J, R, J + R),
J = L_(e_16), R = R_(e_16). J and R commute and square to -1. Their joint eigenspaces are four lines on the unit
multiplicity space (one per sign pair) and two planes on the vector multiplicity space (sign pairs (e, -e) only).
Z normalizes T, so P and Q permute the four unit lines and the two vector planes, and G permutes the two eigenspaces
of J on U (each a unit line plus a vector plane). A pattern is a choice of these permutations: 24 * 2 for P, 24 * 2
for Q and 2 for G, 4,608 in all. Within a pattern the unknowns are 10 scalars and six 2 x 2 blocks.

Count. T acts on the solutions of a pattern by right multiplication and scales the unit scalars of P and Q by
characters. Four of those characters generate the character lattice of T (the script computes the index from the
exact eigenvalues of the four generators), so fixing the four scalars to 1 meets every coset of T in exactly one
point. For each pattern Singular computes, over Q(i), the dimension and the number of points of the ideal of the
equations Q L_y = L_(G y) P on eigen-coordinates (y over one unit and one vector eigen-class representative; the
other y follow by G_2), the gauge and the inverses of every scalar and block determinant, and the number of points
of its radical. The sum over the patterns is the number of components of Z_C.

Real group. Complex conjugation acts on the character lattice X of T; the component group of the real points of T
is the fixed cocharacters modulo the norms, Y^c / (1 + c) Y, computed here by integer linear algebra. When T(R) is
connected, two real points in one complex component lie in one real component, so the number of real components is
at most the number of complex ones.

Controls: flipping the sign of one structure constant must change the count, and the identity triple must solve
the identity pattern.

`--write` writes centralizer-components-result.json beside this file, `--check` recomputes and compares. Both need
Singular 4.4 on PATH.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-bundles-residuals/centralizer_components.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

import sympy as sp
from flint import fmpz_mat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-centralizer-components-v1"
RECORD = HERE / "centralizer-components-result.json"
DIMENSION = 32
HALF = 16
UNIT_CLASSES = ((1, 1), (1, -1), (-1, 1), (-1, -1))
SIGNS = (1, -1)
SINGULAR_ADDRESS_SPACE_BYTES = 4 * 1024**3
SINGULAR_TIMEOUT_SECONDS = 600
PATTERNS_PER_JOB = 64
RESULT_LINE = re.compile(r"^RESULT (\S+) (-?\d+) (-?\d+) (-?\d+)$")
# The four unit scalars fixed to 1: P on three unit lines and Q on one.
GAUGE = (("p", (1, 1)), ("p", (1, -1)), ("p", (-1, 1)), ("q", (1, 1)))
# (base, domain, codomain) of the four generators of T as combinations (identity, J, R) on each slot.
GENERATORS = {
    "base_scaling": ((1, 0, 0), (0, 0, 0), (1, 0, 0)),
    "domain_scaling": ((0, 0, 0), (1, 0, 0), (1, 0, 0)),
    "vertical_phase": ((0, 0, 0), (0, 1, 0), (0, -1, 0)),
    "base_phase_lift": ((0, 1, 0), (0, 0, 1), (0, 1, 1)),
}

# The count the record certifies: the order of the visible S_3 x Z_2, on the identity pattern and on the pattern
# that sends every sign pair to its negative.
EXPECTED_COMPONENTS = 12
EXPECTED_PATTERNS = [[[0, 1, 2, 3], 0, [0, 1, 2, 3], 0, 0], [[3, 2, 1, 0], 1, [3, 2, 1, 0], 1, 1]]

Pattern = tuple[tuple[int, ...], int, tuple[int, ...], int, int]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def structure_sign(left: int, right: int, mutation: str) -> int:
    sign = int(cd_sign(DIMENSION, left, right))
    return -sign if mutation == "flip_structure_sign" and (left, right) == (1, 2) else sign


def left_matrix(index: int, mutation: str) -> sp.Matrix:
    matrix = sp.zeros(DIMENSION, DIMENSION)
    for column in range(DIMENSION):
        matrix[index ^ column, column] = structure_sign(index, column, mutation)
    return matrix


def right_matrix(index: int, mutation: str) -> sp.Matrix:
    matrix = sp.zeros(DIMENSION, DIMENSION)
    for column in range(DIMENSION):
        matrix[column ^ index, column] = structure_sign(column, index, mutation)
    return matrix


Label = tuple[int, int, int, int, int]


@cache
def eigen_frame(mutation: str) -> tuple[tuple[Label, ...], sp.Matrix, sp.Matrix]:
    """Joint eigenvectors of J and R: labels (type, sign of J, sign of R, copy, octonion index), the frame, its inverse.

    Type 0 is the unit multiplicity space (octonion index 0) and type 1 the vector one (indices 1 to 7). An
    eigenvector comes from projecting a basis vector of one of the four octonion blocks; `copy` counts the
    independent ones of a sign pair.
    """
    j, r = left_matrix(HALF, mutation), right_matrix(HALF, mutation)
    identity = sp.eye(DIMENSION)
    _require(
        j * r == r * j and j * j == -identity and r * r == -identity, "J and R are not commuting complex structures"
    )
    labels: list[Label] = []
    columns = []
    for kind in (0, 1):
        indices = (0,) if kind == 0 else tuple(range(1, 8))
        for first in SIGNS:
            for second in SIGNS:
                projector = (identity - sp.I * first * j) * (identity - sp.I * second * r) / 4
                span: list[sp.Matrix] = []
                blocks = []
                for block in range(4):
                    vector = projector[:, 8 * block + indices[0]]
                    if any(vector) and sp.Matrix.hstack(*span, vector).rank() == len(span) + 1:
                        span.append(vector)
                        blocks.append(block)
                for copy, block in enumerate(blocks):
                    for index in indices:
                        column = projector[:, 8 * block + index]
                        _require(
                            any(column)
                            and j * column == sp.I * first * column
                            and r * column == sp.I * second * column,
                            "a frame column is no joint eigenvector",
                        )
                        columns.append(column)
                        labels.append((kind, first, second, copy, index))
    frame = sp.Matrix.hstack(*columns)
    _require(frame.shape == (DIMENSION, DIMENSION) and frame.rank() == DIMENSION, "the eigenvectors do not span")
    return tuple(labels), frame, frame.inv()


def eigen_classes(mutation: str) -> dict[str, Any]:
    """Multiplicities of the joint eigenspaces: {(sign of J, sign of R): copies} for units and for vectors."""
    labels, _, _ = eigen_frame(mutation)
    units: dict[str, int] = {}
    vectors: dict[str, int] = {}
    for kind, first, second, _copy, index in labels:
        if index in (0, 1):
            table = units if kind == 0 else vectors
            table[f"{first},{second}"] = table.get(f"{first},{second}", 0) + 1
    return {"unit": units, "vector": vectors}


@cache
def eigen_left(label: Label, mutation: str) -> sp.Matrix:
    """Left multiplication by the eigenvector `label`, on eigen-coordinates."""
    labels, frame, inverse = eigen_frame(mutation)
    column = frame[:, labels.index(label)]
    total = sp.zeros(DIMENSION, DIMENSION)
    for index in range(DIMENSION):
        if column[index] != 0:
            total += column[index] * left_matrix(index, mutation)
    return inverse * total * frame


def all_patterns() -> list[Pattern]:
    """(unit permutation of P, vector swap of P, unit permutation of Q, vector swap of Q, swap of G)."""
    permutations = list(itertools.permutations(range(4)))
    return [
        (unit_p, swap_p, unit_q, swap_q, swap_g)
        for unit_p in permutations
        for swap_p in (0, 1)
        for unit_q in permutations
        for swap_q in (0, 1)
        for swap_g in (0, 1)
    ]


def pattern_ideal(pattern: Pattern, mutation: str, indices: tuple[int, ...] = (1,)) -> tuple[list[str], list[str]]:
    """Variable names and generators (Singular text) of the gauge-fixed ideal of one pattern.

    `indices` lists the octonion indices of the vector eigenvectors y the equations use; index 1 alone suffices by
    the action of G_2, and `full_reduction` checks that claim on the patterns that have points."""
    unit_p, swap_p, unit_q, swap_q, swap_g = pattern
    labels, _, _ = eigen_frame(mutation)
    position = {label: k for k, label in enumerate(labels)}
    names: list[str] = []

    def symbol(name: str) -> sp.Symbol:
        names.append(name)
        return sp.Symbol(name)

    def target(sign: int, swap: int) -> int:
        return -sign if swap else sign

    p_unit = {c: symbol(f"p{k}") for k, c in enumerate(UNIT_CLASSES)}
    q_unit = {c: symbol(f"q{k}") for k, c in enumerate(UNIT_CLASSES)}
    p_block = {e: sp.Matrix(2, 2, lambda r, c, e=e: symbol(f"a{(1 - e) // 2}{r}{c}")) for e in SIGNS}
    q_block = {e: sp.Matrix(2, 2, lambda r, c, e=e: symbol(f"b{(1 - e) // 2}{r}{c}")) for e in SIGNS}
    g_unit = {e: symbol(f"g{(1 - e) // 2}") for e in SIGNS}
    g_block = {e: sp.Matrix(2, 2, lambda r, c, e=e: symbol(f"c{(1 - e) // 2}{r}{c}")) for e in SIGNS}
    p_matrix, q_matrix = sp.zeros(DIMENSION, DIMENSION), sp.zeros(DIMENSION, DIMENSION)
    for k, source in enumerate(UNIT_CLASSES):
        image_p, image_q = UNIT_CLASSES[unit_p[k]], UNIT_CLASSES[unit_q[k]]
        p_matrix[position[(0, *image_p, 0, 0)], position[(0, *source, 0, 0)]] = p_unit[source]
        q_matrix[position[(0, *image_q, 0, 0)], position[(0, *source, 0, 0)]] = q_unit[source]
    for sign in SIGNS:
        for index in range(1, 8):
            for copy, image in itertools.product(range(2), range(2)):
                column = position[(1, sign, -sign, copy, index)]
                tp, tq = target(sign, swap_p), target(sign, swap_q)
                p_matrix[position[(1, tp, -tp, image, index)], column] = p_block[sign][image, copy]
                q_matrix[position[(1, tq, -tq, image, index)], column] = q_block[sign][image, copy]
    equations: set[sp.Expr] = set()
    for sign in SIGNS:
        image_sign = target(sign, swap_g)
        unit = (
            q_matrix * eigen_left((0, sign, -sign, 0, 0), mutation)
            - g_unit[sign] * eigen_left((0, image_sign, -image_sign, 0, 0), mutation) * p_matrix
        )
        equations.update(sp.expand(entry) for entry in unit)
        for copy, index in itertools.product(range(2), indices):
            moved = sp.zeros(DIMENSION, DIMENSION)
            for image in range(2):
                moved += g_block[sign][image, copy] * eigen_left((1, image_sign, -image_sign, image, index), mutation)
            vector = q_matrix * eigen_left((1, sign, -sign, copy, index), mutation) - moved * p_matrix
            equations.update(sp.expand(entry) for entry in vector)
    equations.discard(sp.Integer(0))
    scalars = {"p": p_unit, "q": q_unit}
    generators = [scalars[slot][unit_class] - 1 for slot, unit_class in GAUGE]
    inverses = []
    for k, scalar in enumerate([*p_unit.values(), *q_unit.values(), *g_unit.values()]):
        inverses.append(scalar * symbol(f"w{k}") - 1)
    for k, block in enumerate([p_block[1], p_block[-1], q_block[1], q_block[-1], g_block[1], g_block[-1]]):
        inverses.append(sp.expand(block.det() * symbol(f"d{k}") - 1))
    everything = [*sorted(equations, key=str), *generators, *inverses]
    return names, [str(entry).replace("**", "^").replace("I", "i") for entry in everything]


def job_script(job: tuple[tuple[tuple[int, Pattern], ...], str]) -> str:
    patterns, mutation = job
    parts = ['LIB "primdec.lib";', "option(redSB);"]
    for number, pattern in patterns:
        names, generators = pattern_ideal(pattern, mutation)
        parts += [
            f"ring r{number}=(0,i),({','.join(names)}),dp; minpoly=i^2+1;",
            f"ideal S=std(ideal({','.join(generators)}));",
            "int dS=dim(S); int vS=-1; int vR=-1;",
            "if(dS==0){ vS=vdim(S); vR=vdim(std(radical(S))); }",
            f'print("RESULT {number} "+string(dS)+" "+string(vS)+" "+string(vR));',
            f"kill r{number};",
        ]
    return "\n".join([*parts, 'print("DONE");', "quit;"]) + "\n"


def run_job(job: tuple[tuple[tuple[int, Pattern], ...], str]) -> list[tuple[int, int, int, int]]:
    """(pattern number, dimension, points, points of the radical) for each pattern of the job."""
    with tempfile.TemporaryDirectory(prefix="centralizer-") as directory:
        path = Path(directory) / "job.sing"
        path.write_text(job_script(job), encoding="utf-8")
        process = subprocess.run(
            ["prlimit", f"--as={SINGULAR_ADDRESS_SPACE_BYTES}", "Singular", "-q", "--no-warn", "--no-rc", str(path)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
            timeout=SINGULAR_TIMEOUT_SECONDS,
        )
    lines = process.stdout.splitlines()
    failed = (
        process.returncode != 0 or process.stderr.strip() != "" or any(line.lstrip().startswith("?") for line in lines)
    )
    _require(not failed and "DONE" in lines, f"Singular failed: {(process.stderr + process.stdout)[-1500:]}")
    rows = []
    for line in lines:
        match = RESULT_LINE.match(line)
        if match is not None:
            rows.append((int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))))
    _require([row[0] for row in rows] == [number for number, _ in job[0]], "a pattern has no result line")
    return rows


def count_patterns(mutation: str, patterns: list[Pattern] | None = None) -> dict[str, Any]:
    """Run every pattern and summarize: the patterns with points, their counts, and the totals."""
    numbered = list(enumerate(all_patterns() if patterns is None else patterns))
    jobs = [
        (tuple(numbered[start : start + PATTERNS_PER_JOB]), mutation)
        for start in range(0, len(numbered), PATTERNS_PER_JOB)
    ]
    rows = [row for chunk in parallel.ordered_map(run_job, jobs, min_items=1) for row in chunk]
    table = dict(numbered)
    solved = [
        {
            "pattern": [list(table[n][0]), table[n][1], list(table[n][2]), table[n][3], table[n][4]],
            "points": points,
            "reduced_points": reduced,
        }
        for n, dimension, points, reduced in rows
        if dimension == 0
    ]
    return {
        "patterns": len(rows),
        "patterns_of_positive_dimension": sum(dimension > 0 for _, dimension, _, _ in rows),
        "patterns_with_points": solved,
        "points": sum(entry["points"] for entry in solved),
        "reduced_points": sum(entry["reduced_points"] for entry in solved),
    }


def full_reduction(pattern: Pattern, mutation: str) -> int:
    """The number of equations for y over every octonion index that fail to reduce to zero modulo the ideal built
    from index 1 alone; 0 confirms that the representatives imply the equation for every y in U."""
    names, representative = pattern_ideal(pattern, mutation)
    full_names, everything = pattern_ideal(pattern, mutation, tuple(range(1, 8)))
    _require(names == full_names, "the two ideals use different variables")
    script = "\n".join(
        [
            "option(redSB);",
            f"ring r=(0,i),({','.join(names)}),dp; minpoly=i^2+1;",
            f"ideal S=std(ideal({','.join(representative)}));",
            f"ideal A={','.join(everything)};",
            'print("RESULT 0 "+string(size(reduce(A,S)))+" "+string(ncols(A))+" 0");',
            'print("DONE");',
            "quit;",
        ]
    )
    with tempfile.TemporaryDirectory(prefix="centralizer-") as directory:
        path = Path(directory) / "full.sing"
        path.write_text(script + "\n", encoding="utf-8")
        process = subprocess.run(
            ["prlimit", f"--as={SINGULAR_ADDRESS_SPACE_BYTES}", "Singular", "-q", "--no-warn", "--no-rc", str(path)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
            timeout=SINGULAR_TIMEOUT_SECONDS,
        )
    lines = process.stdout.splitlines()
    match = next((RESULT_LINE.match(line) for line in lines if RESULT_LINE.match(line)), None)
    failed = process.stderr.strip() != "" or any(line.lstrip().startswith("?") for line in lines)
    _require(
        not failed and process.returncode == 0 and "DONE" in lines and match is not None,
        f"Singular failed: {(process.stderr + process.stdout)[-800:]}",
    )
    return int(match.group(2)) if match is not None else -1


# ---------------------------------------------------------------------------------------------------------------------
# The character lattice of T, the gauge and the real points


def _slot(combination: tuple[int, int, int], mutation: str) -> sp.Matrix:
    identity = sp.eye(DIMENSION)
    return (
        combination[0] * identity
        + combination[1] * left_matrix(HALF, mutation)
        + combination[2] * right_matrix(HALF, mutation)
    )


def torus_characters(mutation: str) -> dict[str, Any]:
    """Characters of T on the unit lines of P and Q and on the eigenspaces of G, as integer vectors.

    A generator with matrix a + b J + c R on a slot has eigenvalue a + i (b e_1 + c e_2) on the class (e_1, e_2); the
    coordinate of the character on that generator is a for a scaling and b e_1 + c e_2 for a phase. The script reads
    the eigenvalues from the matrices on the eigenvectors, so a wrong table of generators shows as a non-eigenvector.
    """
    labels, frame, _ = eigen_frame(mutation)

    def value(combination: tuple[int, int, int], label: Label) -> int:
        vector = frame[:, labels.index(label)]
        moved = _slot(combination, mutation) * vector
        pivot = next(k for k in range(DIMENSION) if vector[k] != 0)
        eigenvalue = sp.nsimplify(moved[pivot] / vector[pivot])
        _require((moved - eigenvalue * vector).is_zero_matrix is True, "a generator of T has a non-eigenvector")
        real, imaginary = eigenvalue.as_real_imag()
        return int(real) if imaginary == 0 else int(imaginary)

    def character(slot: int, label: Label) -> list[int]:
        return [value(GENERATORS[name][slot], label) for name in GENERATORS]

    p_unit = {c: character(1, (0, *c, 0, 0)) for c in UNIT_CLASSES}
    q_unit = {c: character(2, (0, *c, 0, 0)) for c in UNIT_CLASSES}
    others = [character(1, (1, e, -e, 0, 1)) for e in SIGNS] + [character(2, (1, e, -e, 0, 1)) for e in SIGNS]
    others += [character(0, (0, e, -e, 0, 0)) for e in SIGNS] + [character(0, (1, e, -e, 0, 1)) for e in SIGNS]
    every = [*p_unit.values(), *q_unit.values(), *others]
    gauge = [{"p": p_unit, "q": q_unit}[slot][unit_class] for slot, unit_class in GAUGE]
    return {"all": every, "gauge": gauge}


def lattice_basis(vectors: list[list[int]]) -> list[list[int]]:
    """A basis (rows) of the lattice the integer vectors generate: the nonzero rows of the Hermite normal form."""
    reduced = fmpz_mat(vectors).hnf().tolist()
    return [[int(value) for value in row] for row in reduced if any(row)]


def integer_kernel(matrix: list[list[int]]) -> list[list[int]]:
    """A basis (rows) of {x in Z^n : matrix x = 0}.

    With U A^T = H the Hermite form of the transpose, the rows of the unimodular U that meet zero rows of H span the
    integer kernel, which is saturated because U is unimodular.
    """
    transposed = fmpz_mat([list(row) for row in zip(*matrix, strict=True)])
    hermite, transform = transposed.hnf(True)
    rows = hermite.tolist()
    return [[int(v) for v in transform.tolist()[k]] for k in range(len(rows)) if not any(rows[k])]


def lattice_coordinates(basis: list[list[int]], vector: list[int]) -> list[int] | None:
    """The integer coordinates of the vector on the basis rows, or None when it lies outside the lattice."""
    frame = sp.Matrix(basis).T
    solution = (frame.T * frame).inv() * frame.T * sp.Matrix(vector)
    if frame * solution != sp.Matrix(vector) or any(not value.is_integer for value in solution):
        return None
    return [int(value) for value in solution]


def torus_summary(mutation: str) -> dict[str, Any]:
    """Rank of the character lattice X, the index of the gauge characters in X, and pi_0 of the real points of T."""
    characters = torus_characters(mutation)
    basis = lattice_basis(characters["all"])
    rank = len(basis)
    gauge = [lattice_coordinates(basis, vector) for vector in characters["gauge"]]
    _require(all(row is not None for row in gauge), "a gauge character lies outside the lattice")
    index = abs(int(sp.Matrix(gauge).det())) if rank == len(gauge) else 0
    # Complex conjugation keeps a scaling coordinate and negates a phase coordinate of every character.
    signs = [1 if name.endswith("scaling") else -1 for name in GENERATORS]
    conjugated = [
        lattice_coordinates(basis, [sign * value for sign, value in zip(signs, row, strict=True)]) for row in basis
    ]
    _require(all(row is not None for row in conjugated), "conjugation leaves the lattice")
    # Row k holds the coordinates of the conjugate of basis character k, so a cocharacter y (a column on the dual
    # basis) moves to `conjugated` y, and y is fixed when (conjugated - 1) y = 0.
    action = sp.Matrix(conjugated)
    _require(action * action == sp.eye(rank), "conjugation is no involution on the lattice")
    fixed = integer_kernel([[int(v) for v in row] for row in (action - sp.eye(rank)).tolist()])
    norms = (action + sp.eye(rank)).T.tolist()
    inside = [lattice_coordinates(fixed, [int(v) for v in column]) for column in norms] if fixed else []
    _require(all(row is not None for row in inside), "a norm lies outside the fixed cocharacters")
    divisors: list[int] = []
    if fixed:
        smith = fmpz_mat([list(row) for row in inside if row is not None]).snf().tolist()
        divisors = [abs(int(smith[k][k])) for k in range(min(len(smith), len(fixed)))]
    components = 1
    for divisor in divisors:
        components *= divisor
    return {
        "generators": list(GENERATORS),
        "character_lattice_rank": rank,
        "gauge_index_in_character_lattice": index,
        "fixed_cocharacter_rank": len(fixed),
        # Elementary divisors of the norms (1 + c) Y inside the fixed cocharacters Y^c; all 1 means T(R) is connected,
        # and a 0 means the quotient is infinite, which a torus excludes.
        "norm_elementary_divisors": divisors,
        "real_torus_components": components,
    }


def identity_solves(mutation: str) -> bool:
    """Whether the identity triple satisfies the equations of the identity pattern."""
    identity: Pattern = ((0, 1, 2, 3), 0, (0, 1, 2, 3), 0, 0)
    names, generators = pattern_ideal(identity, mutation)
    # Scalars, their inverses and the determinant inverses are 1; a block entry is 1 on the diagonal and 0 off it.
    values = {name: (int(name[-1] == name[-2]) if name[0] in "abc" else 1) for name in names}
    table = {sp.Symbol(name): value for name, value in values.items()}
    for text in generators:
        expression = sp.sympify(text.replace("^", "**"), locals={name: sp.Symbol(name) for name in names} | {"i": sp.I})
        if sp.simplify(expression.subs(table)) != 0:
            return False
    return True


def compute() -> dict[str, Any]:
    banner = subprocess.run(
        ["Singular", "--version"], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False
    )
    version = re.search(r"version (\d+\.\d+\.\d+)", banner.stdout)
    _require(version is not None, "no Singular version")
    counts = count_patterns("")
    torus = torus_summary("")
    identity: Pattern = ((0, 1, 2, 3), 0, (0, 1, 2, 3), 0, 0)
    mutated = count_patterns("flip_structure_sign", [identity])
    index = torus["gauge_index_in_character_lattice"]
    for entry in counts["patterns_with_points"]:
        unit_p, swap_p, unit_q, swap_q, swap_g = entry["pattern"]
        entry["equations_over_all_indices_not_reduced"] = full_reduction(
            (tuple(unit_p), swap_p, tuple(unit_q), swap_q, swap_g), ""
        )
    components = counts["reduced_points"] // index if index else None
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (HERE / "centralizer_components.py", ROOT / "gororoba_quantum" / "cd_core.py")
        },
        "singular_version": version.group(1) if version else None,
        "eigen_classes": eigen_classes(""),
        "torus": torus,
        "counts": counts,
        "complex_components": components,
        "controls": {
            "identity_triple_solves_identity_pattern": identity_solves(""),
            "identity_pattern_points_with_flipped_sign": mutated["points"],
            "identity_pattern_dimension_positive_with_flipped_sign": mutated["patterns_of_positive_dimension"],
        },
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    counts, torus, controls = record["counts"], record["torus"], record["controls"]
    if record["complex_components"] != EXPECTED_COMPONENTS:
        problems.append(f"the complex centralizer has {record['complex_components']} components")
    if sorted(entry["pattern"] for entry in counts["patterns_with_points"]) != sorted(EXPECTED_PATTERNS):
        problems.append("the patterns with points differ from the identity and the sign-negating pattern")
    if counts["patterns"] != 4608:
        problems.append("the pattern enumeration is incomplete")
    if counts["patterns_of_positive_dimension"]:
        problems.append("a gauge-fixed pattern has positive dimension")
    if any(entry.get("equations_over_all_indices_not_reduced") != 0 for entry in counts["patterns_with_points"]):
        problems.append("an equation for another octonion index does not follow from the representatives")
    if counts["points"] != counts["reduced_points"]:
        problems.append("a pattern ideal is not radical")
    if torus["character_lattice_rank"] != 4 or torus["gauge_index_in_character_lattice"] != 1:
        problems.append("the gauge does not meet each coset of T once")
    if torus["real_torus_components"] != 1:
        problems.append("the real points of T are disconnected")
    if record["complex_components"] != counts["reduced_points"]:
        problems.append("the component count differs from the point count")
    if not controls["identity_triple_solves_identity_pattern"]:
        problems.append("the identity triple fails the identity pattern")
    identity_points = next(
        (
            entry["points"]
            for entry in counts["patterns_with_points"]
            if entry["pattern"] == [[0, 1, 2, 3], 0, [0, 1, 2, 3], 0, 0]
        ),
        0,
    )
    if (
        controls["identity_pattern_points_with_flipped_sign"] == identity_points
        and not controls["identity_pattern_dimension_positive_with_flipped_sign"]
    ):
        problems.append("the flipped structure sign leaves the count unchanged")
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
    print(record["complex_components"], [entry["pattern"] for entry in record["counts"]["patterns_with_points"]])


if __name__ == "__main__":
    main()
