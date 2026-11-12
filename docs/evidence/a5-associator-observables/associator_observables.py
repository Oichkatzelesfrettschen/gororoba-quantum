"""Associator observables of the twelve A_5 rank strata over sampled points of each stratum, in exact arithmetic.

For a doubly pure y of the 32-dimensional Cayley-Dickson algebra A_5 (products from cd_core), y^2 = -N e_0 with
N = sum y_k^2, and the left alternative associator operator L_y^2 - L_(y^2) = L_y^2 + N I has the right analog
R_y^2 - R_(y^2). At every point the record holds, over Q:

    nullity of L_y and of R_y
    rank of L_y^2 + N I and of R_y^2 + N I
    the factorization over Q of the characteristic polynomial of -L_y^2 / N (the spectrum, scale free),
    and, in the controls, the unnormalized characteristic polynomial of -L_y^2.

The twelve strata are the H-orbits of the regularity record, H = G_2(C) x SO(2, C) x C^*, certified at a point by an
exact nullity of L_y at least 8 and the membership pattern of the representative (a point of R_8 lies in one of the
twelve orbits and the twelve patterns are distinct). The sampled families of one stratum are

    representative            the retained representative
    unipotent                 exp(t N_i) for the 60 nilpotent derivations N_i of the split octonions, t in 1, 1/2, -2
    boost-scale-reflect       rational boosts, scalings and the reflection mu' -> -mu'
    composite                 a unipotent, a boost and a second unipotent, by a fixed index rule
    grid                      points of the grid {-1, 0, 1}^15 of split coordinates in the stratum, a stride sample

The movements of the unipotent, boost-scale-reflect and composite families preserve every stratum and are not
automorphisms of A_5; the script counts the basis products each real realization breaks. The control maps are exact
rational automorphisms of A_5, the compact G_2 elements exp(theta D) = I + sin(theta) D + (1 - cos(theta)) D^2 with
a Pythagorean pair (cos, sin), lifted to the four octonion blocks of A_5, and the outer reflection (a, b) -> (a, -b);
each is verified on all 1,024 basis pairs against cd_multiply_exact. Every point comes from this deterministic
enumeration and no random draw enters.

Usage:
    "$PYTHON" -B -W error docs/evidence/a5-associator-observables/associator_observables.py --check
    "$PYTHON" -B -W error docs/evidence/a5-associator-observables/associator_observables.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import flint
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE.parent / "a5-rank-strata-equations"))
sys.path.insert(0, str(HERE.parent / "a5-strata-regularity"))

import rederive_strata_equations as eq  # noqa: E402
import strata_regularity as strata  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign  # noqa: E402

SCHEMA = "a5-associator-observables-v1"
RECORD = HERE / "associator-observables.json"
DIM = 32
HALF = 16
E16 = HALF

# Task name of each stratum, with its key in the regularity verifier and in the strata script.
STRATA: dict[str, tuple[str, str]] = {
    "W8": ("W8", "W8"),
    "Ehat": ("E8bar", "Ehat"),
    "Iso": ("Iso", "Iso"),
    "X+": ("X+", "Xp"),
    "X-": ("X-", "Xm"),
    "B9": ("B9", "B9"),
    "V": ("V", "V"),
    "VB": ("VB", "VB"),
    "Va+": ("Va+", "Vap"),
    "Va-": ("Va-", "Vam"),
    "N+": ("N+", "Np"),
    "N-": ("N-", "Nm"),
}
NULLITY = {name: independent.NULLITY[key] for name, (key, _) in STRATA.items()}
# Strata whose closure holds B9 (the closure order of the regularity record).
CLOSURE_HOLDS_B9 = tuple(name for name, (key, _) in STRATA.items() if "B9" in independent.LOWER[key])
FAMILIES = ("representative", "unipotent", "boost-scale-reflect", "composite", "grid")
UNIPOTENT_PARAMETERS = (Fraction(1), Fraction(1, 2), Fraction(-2))
BOOSTS = ((Fraction(5, 4), Fraction(3, 4)), (Fraction(13, 12), Fraction(5, 12)), (Fraction(5, 3), Fraction(4, 3)))
COMPOSITE_COUNT = 20
COMPOSITE_T1 = (Fraction(1), Fraction(1, 2), Fraction(2), Fraction(-1))
COMPOSITE_T2 = (Fraction(-1), Fraction(2), Fraction(1, 2), Fraction(1))
GRID_STRIDE = 11
GRID_PER_STRATUM = 100
GRID_CHUNK = 4096
GRID_SIZE = 3**15
GRID_CANDIDATE_CHUNK = 1 << 19
# (index of the compact derivation, cos, sin); every pair satisfies cos^2 + sin^2 = 1.
AUTOMORPHISMS: dict[str, tuple[tuple[int, Fraction, Fraction], ...]] = {
    "rot-a": ((0, Fraction(3, 5), Fraction(4, 5)),),
    "rot-b": ((2, Fraction(5, 13), Fraction(12, 13)), (9, Fraction(8, 17), Fraction(15, 17))),
    "rot-c": (
        (4, Fraction(3, 5), Fraction(-4, 5)),
        (7, Fraction(5, 13), Fraction(12, 13)),
        (11, Fraction(20, 29), Fraction(21, 29)),
    ),
    "rot-d": (
        (1, Fraction(7, 25), Fraction(24, 25)),
        (6, Fraction(3, 5), Fraction(4, 5)),
        (10, Fraction(5, 13), Fraction(-12, 13)),
        (13, Fraction(8, 17), Fraction(15, 17)),
    ),
}
AUTOMORPHISM_NAMES = (*AUTOMORPHISMS, "reflect", "rot-c*reflect")
# The outer reflection (a, b) -> (a, -b) is complex conjugation of z; the sign-paired strata are exchanged.
REFLECTION_IMAGE = {"X+": "X-", "X-": "X+", "Va+": "Va-", "Va-": "Va+", "N+": "N-", "N-": "N+"}
PHASES = ((Fraction(3, 5), Fraction(4, 5)), (Fraction(5, 13), Fraction(12, 13)))
PHASE_BASES = ("rep", "u0:1")

RationalVector = tuple[Fraction, ...]
Program = tuple[tuple[Any, ...], ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> Any:
    return flint.fmpq(value.numerator, value.denominator)


def _frac(value: Any) -> Fraction:
    return Fraction(int(value.p), int(value.q))


def _identity() -> Any:
    return flint.fmpq_mat(DIM, DIM, [1 if i == j else 0 for i in range(DIM) for j in range(DIM)])


def _text(value: Fraction) -> str:
    return str(value)


# ---------------------------------------------------------------------------------------------------------------------
# Representatives, splitting and certification

REPRESENTATIVES: dict[str, RationalVector] = {name: tuple(independent.REPS[key]) for name, (key, _) in STRATA.items()}
PATTERNS: dict[str, str] = {name: independent.pattern(list(point)) for name, point in REPRESENTATIVES.items()}
STRATUM_OF_PATTERN = {pattern: name for name, pattern in PATTERNS.items()}


def split_from_y(y: Sequence[Fraction]) -> list[Any]:
    """Split coordinates z'_k = i^(-popcount k) (y_k + i y_(16+k)) as Gaussian rationals."""
    return [independent.Gq(y[k], y[HALF + k]) * independent.i_pow(-independent.popcount(k)) for k in range(1, HALF)]


def y_from_split(zp: Sequence[Any]) -> list[Fraction]:
    """y in A_5 for split coordinates, Gaussian or rational: z_k = i^popcount(k) z'_k = y_k + i y_(16+k)."""
    y = [Fraction(0)] * DIM
    for k in range(1, HALF):
        z = independent.Gq.of(zp[k - 1]) * independent.i_pow(independent.popcount(k))
        y[k] = z.re
        y[HALF + k] = z.im
    return y


def certified_stratum(y: Sequence[Fraction]) -> str:
    """Name of the stratum holding y, or the empty string when the membership pattern is none of the twelve."""
    return STRATUM_OF_PATTERN.get(independent.pattern(split_from_y(y)), "")


# ---------------------------------------------------------------------------------------------------------------------
# Observables


def _product_matrices(y: Sequence[Fraction]) -> tuple[Any, Any]:
    """L_y and R_y from the cd_core sign table: L_y e_q = sum_p y_p e_p e_q and R_y e_q = sum_p y_p e_q e_p."""
    left = [[Fraction(0)] * DIM for _ in range(DIM)]
    right = [[Fraction(0)] * DIM for _ in range(DIM)]
    for p in range(DIM):
        if y[p]:
            for q in range(DIM):
                left[p ^ q][q] += y[p] * independent.SIGN32[p][q]
                right[p ^ q][q] += y[p] * independent.SIGN32[q][p]
    build = flint.fmpq_mat
    return (
        build(DIM, DIM, [_q(x) for row in left for x in row]),
        build(DIM, DIM, [_q(x) for row in right for x in row]),
    )


def _apply(matrix: Any, vector: Sequence[Fraction]) -> list[Fraction]:
    return [_frac(x) for x in (matrix * flint.fmpq_mat(DIM, 1, [_q(x) for x in vector])).entries()]


def _spectrum(matrix: Any, norm: Any) -> list[tuple[int, tuple[str, ...]]]:
    """Factorization over Q of the characteristic polynomial of -matrix^2 / N, as (multiplicity, coefficients)."""
    scaled = -(matrix * matrix) * (1 / norm)
    _content, factors = scaled.charpoly().factor()
    rows = [(int(mult), tuple(str(c) for c in poly.coeffs())) for poly, mult in factors]
    rows.sort(key=lambda row: (len(row[1]), tuple(Fraction(c) for c in row[1]), row[0]))
    return rows


def _spectrum_id(spectrum: list[tuple[int, tuple[str, ...]]]) -> str:
    return hashlib.sha256(json.dumps(spectrum).encode("utf-8")).hexdigest()[:12]


def _linear_root(coefficients: tuple[str, ...]) -> Fraction:
    """The root -c0 / c1 of a linear factor c0 + c1 x."""
    return -Fraction(coefficients[0]) / Fraction(coefficients[1])


def _root_multiplicity(spectrum: list[tuple[int, tuple[str, ...]]], root: Fraction) -> int:
    """Multiplicity of a rational root among the linear factors of the factorization."""
    return sum(mult for mult, coeffs in spectrum if len(coeffs) == 2 and _linear_root(coeffs) == root)


def _unit(k: int) -> list[Fraction]:
    return [Fraction(int(i == k)) for i in range(DIM)]


def observables(y: Sequence[Fraction]) -> dict[str, Any]:
    """Every exact observable of y; raises when y is not doubly pure with y^2 = -N e_0."""
    _require(not y[0] and not y[HALF], "y is not doubly pure")
    norm = sum((c * c for c in y), Fraction(0))
    _require(norm > 0, "y is zero")
    left, right = _product_matrices(y)
    square = _apply(left, y)
    _require(square[0] == -norm and not any(square[1:]), "y^2 is not -N e_0")
    n_q = _q(norm)
    identity = _identity()
    left_alt = left * left + n_q * identity
    right_alt = right * right + n_q * identity
    minus_left2 = -(left * left)
    minus_right2 = -(right * right)
    y_e16 = [Fraction(0)] * DIM
    for p in range(DIM):
        if y[p]:
            y_e16[p ^ E16] += y[p] * independent.SIGN32[p][E16]
    kernel_vectors = (_unit(0), list(y), _unit(E16), y_e16)
    kernel_contains = all(not any(_apply(left_alt, v)) for v in kernel_vectors) and all(
        not any(_apply(right_alt, v)) for v in kernel_vectors
    )
    spectrum = _spectrum(left, n_q)
    spectrum_right = _spectrum(right, n_q)
    cp_left = [str(c) for c in minus_left2.charpoly().coeffs()]
    cp_right = [str(c) for c in minus_right2.charpoly().coeffs()]
    rank_left = int(left_alt.rank())
    nullity_left = DIM - int(left.rank())
    return {
        "norm": str(norm),
        "nullity_left": nullity_left,
        "nullity_right": DIM - int(right.rank()),
        "rank_left": rank_left,
        "rank_right": int(right_alt.rank()),
        "spectrum": spectrum,
        "spectrum_id": _spectrum_id(spectrum),
        "charpoly": cp_left,
        "consistent": (
            kernel_contains
            and spectrum == spectrum_right
            and cp_left == cp_right
            and rank_left == DIM - _root_multiplicity(spectrum, Fraction(1))
            and nullity_left == _root_multiplicity(spectrum, Fraction(0))
        ),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Maps on y: compact automorphisms, the induced real maps of the stratum-preserving movements


@cache
def _derivation_matrices() -> tuple[Any, ...]:
    table = [[cd_sign(8, a, b) for b in range(8)] for a in range(8)]
    ders = eq.derivations(table)
    _require(len(ders) == 14, "the octonion derivation algebra has dimension other than 14")
    matrices = tuple(flint.fmpq_mat(8, 8, [_q(Fraction(x)) for row in d for x in row]) for d in ders)
    for d in matrices:
        _require(d * d * d == -d, "a compact derivation does not satisfy D^3 = -D")
    return matrices


def _block_diagonal(block: Any) -> Any:
    entries = [flint.fmpq(0)] * (DIM * DIM)
    for m in range(4):
        for i in range(8):
            for j in range(8):
                entries[(8 * m + i) * DIM + 8 * m + j] = block[i, j]
    return flint.fmpq_mat(DIM, DIM, entries)


def rotation(index: int, cos: Fraction, sin: Fraction) -> Any:
    """exp(theta D) on A_5 for the compact derivation D with D^3 = -D: I + sin D + (1 - cos) D^2, lifted blockwise."""
    d = _derivation_matrices()[index]
    block = flint.fmpq_mat(8, 8, [1 if i == j else 0 for i in range(8) for j in range(8)])
    block = block + _q(sin) * d + _q(1 - cos) * (d * d)
    return _block_diagonal(block)


def reflection() -> Any:
    """The outer reflection (a, b) -> (a, -b) of the Cayley-Dickson doubling A_4 -> A_5."""
    return flint.fmpq_mat(DIM, DIM, [(1 if i < HALF else -1) if i == j else 0 for i in range(DIM) for j in range(DIM)])


@cache
def automorphism_matrix(name: str) -> Any:
    if name == "reflect":
        return reflection()
    if name == "rot-c*reflect":
        return automorphism_matrix("rot-c") * reflection()
    matrix = _identity()
    for index, cos, sin in AUTOMORPHISMS[name]:
        matrix = matrix * rotation(index, cos, sin)
    return matrix


def phase_matrix(cos: Fraction, sin: Fraction) -> Any:
    """z -> (cos + i sin) z on the doubly pure coordinates, the identity on e_0 and e_16."""
    entries = [flint.fmpq(0)] * (DIM * DIM)
    for k in range(DIM):
        entries[k * DIM + k] = _q(cos if k not in (0, E16) else Fraction(1))
    for k in range(1, HALF):
        entries[k * DIM + HALF + k] = _q(-sin)
        entries[(HALF + k) * DIM + k] = _q(sin)
    return flint.fmpq_mat(DIM, DIM, entries)


def automorphism_failures(matrix: Any) -> int:
    """Basis pairs (p, q) among the 1,024 of A_5 with T(e_p e_q) different from T(e_p) T(e_q), by cd_multiply_exact."""
    columns = [[_frac(matrix[r, c]) for r in range(DIM)] for c in range(DIM)]
    unit = [[Fraction(int(i == k)) for i in range(DIM)] for k in range(DIM)]
    failures = 0
    for p, q in itertools.product(range(DIM), repeat=2):
        product = cd_multiply_exact(DIM, unit[p], unit[q])
        index = next(i for i, value in enumerate(product) if value)
        expected = [product[index] * x for x in columns[index]]
        if list(cd_multiply_exact(DIM, columns[p], columns[q])) != expected:
            failures += 1
    return failures


def induced_real_map(action: Callable[[list[Any]], list[Any]]) -> Any:
    """The real 32 x 32 matrix of a map z' -> action(z') of the split coordinates; e_0 and e_16 stay fixed."""
    entries = [flint.fmpq(0)] * (DIM * DIM)
    entries[0] = flint.fmpq(1)
    entries[E16 * DIM + E16] = flint.fmpq(1)
    for j in (*range(1, HALF), *range(HALF + 1, DIM)):
        basis = [Fraction(int(i == j)) for i in range(DIM)]
        image = y_from_split(action(split_from_y(basis)))
        for r in range(DIM):
            entries[r * DIM + j] = _q(image[r])
    return flint.fmpq_mat(DIM, DIM, entries)


@cache
def _nilpotents() -> tuple[Any, ...]:
    return tuple(independent.nilpotent_derivations())


@cache
def unipotent(index: int, t: Fraction) -> list[list[Fraction]]:
    nilpotent = _nilpotents()[index]
    return independent.expm_nilpotent([[t * x for x in row] for row in nilpotent])


def apply_program(point: RationalVector, program: Program) -> RationalVector:
    z: list[Any] = list(point)
    for op in program:
        if op[0] == "u":
            z = independent.act_g2(unipotent(op[1], op[2]), z)
        elif op[0] == "b":
            z = independent.act_boost(op[1], op[2], z)
        elif op[0] == "s":
            z = [op[1] * x for x in z]
        elif op[0] == "m":
            z[7] = -z[7]
        else:
            raise ValueError(f"unknown movement {op[0]!r}")
    return tuple(z)


def program_label(program: Program) -> str:
    parts = []
    for op in program:
        if op[0] == "u":
            parts.append(f"u{op[1]}:{op[2]}")
        elif op[0] == "b":
            parts.append(f"b:{op[1]}:{op[2]}")
        elif op[0] == "s":
            parts.append(f"scale:{op[1]}")
        else:
            parts.append("mu-reflect")
    return ">".join(parts) if parts else "rep"


def programs() -> list[tuple[str, Program]]:
    """The deterministic movement programs of the four movement families, in a fixed order."""
    out: list[tuple[str, Program]] = [("representative", ())]
    for index, t in itertools.product(range(len(_nilpotents())), UNIPOTENT_PARAMETERS):
        out.append(("unipotent", (("u", index, t),)))
    out.extend(("boost-scale-reflect", (("b", c, s),)) for c, s in BOOSTS)
    out.extend(("boost-scale-reflect", (("s", k),)) for k in (Fraction(2), Fraction(1, 3)))
    out.append(("boost-scale-reflect", (("m",),)))
    count = len(_nilpotents())
    for j in range(COMPOSITE_COUNT):
        c, s = BOOSTS[j % len(BOOSTS)]
        first = (("u", (3 * j + 1) % count, COMPOSITE_T1[j % 4]),)
        second = (("u", (7 * j + 4) % count, COMPOSITE_T2[j % 4]),)
        out.append(("composite", (*first, ("b", c, s), *second)))
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Grid points


def _grid_candidate_chunk(bounds: tuple[int, int]) -> list[int]:
    """Ascending grid indices in the half-open bounds satisfying a necessary equation of R_8."""
    start, stop = bounds
    eta = np.array(independent.ETA[1:8], dtype=np.int64)
    powers = 3 ** np.arange(15, dtype=np.int64)
    indices = np.arange(start, stop, dtype=np.int64)
    digits = (indices[:, None] // powers[None, :]) % 3 - 1
    first_vector, scalar, second_vector = digits[:, 0:7], digits[:, 7], digits[:, 8:15]
    first_norm = (first_vector * first_vector * eta).sum(axis=1)
    second_norm = (second_vector * second_vector * eta).sum(axis=1)
    mixed = (first_vector * second_vector * eta).sum(axis=1)
    w8 = (scalar == 0) & (first_norm + second_norm == 0) & (mixed == 0)
    quadric = (first_norm - scalar * scalar - second_norm == 0) & (mixed * mixed - first_norm * second_norm == 0)
    keep = (w8 | quadric) & (digits != 0).any(axis=1)
    candidates: list[int] = indices[keep].tolist()
    return candidates


def _grid_candidates() -> list[int]:
    """Indices i of {-1, 0, 1}^15 (digit k of i in base 3, minus 1, is z'_(k+1)) on a necessary equation of R_8."""
    bounds = [
        (start, min(start + GRID_CANDIDATE_CHUNK, GRID_SIZE)) for start in range(0, GRID_SIZE, GRID_CANDIDATE_CHUNK)
    ]
    return [index for chunk in parallel.ordered_map(_grid_candidate_chunk, bounds, min_items=1) for index in chunk]


def grid_point(index: int) -> RationalVector:
    return tuple(Fraction((index // 3**k) % 3 - 1) for k in range(15))


def classify_chunk(indices: tuple[int, ...]) -> list[str]:
    return [STRATUM_OF_PATTERN.get(independent.pattern(list(grid_point(i))), "") for i in indices]


def grid_selection() -> tuple[dict[str, list[int]], dict[str, int]]:
    """Per stratum, GRID_PER_STRATUM evenly spaced grid indices out of those at every GRID_STRIDE-th candidate."""
    candidates = _grid_candidates()[::GRID_STRIDE]
    chunks = [tuple(candidates[i : i + GRID_CHUNK]) for i in range(0, len(candidates), GRID_CHUNK)]
    names = [name for chunk in parallel.ordered_map(classify_chunk, chunks, min_items=1) for name in chunk]
    members: dict[str, list[int]] = {name: [] for name in STRATA}
    for index, name in zip(candidates, names, strict=True):
        if name:
            members[name].append(index)
    counts = {name: len(items) for name, items in members.items()}
    chosen = {
        name: items
        if len(items) <= GRID_PER_STRATUM
        else [items[(j * len(items)) // GRID_PER_STRATUM] for j in range(GRID_PER_STRATUM)]
        for name, items in members.items()
    }
    return chosen, counts


# ---------------------------------------------------------------------------------------------------------------------
# Point evaluation


@dataclass(frozen=True)
class PointSpec:
    stratum: str
    family: str
    label: str
    point: RationalVector
    transform: str = ""
    base_label: str = ""


def _transformed(y: list[Fraction], transform: str) -> list[Fraction]:
    if not transform:
        return y
    kind, _, rest = transform.partition(":")
    if kind == "aut":
        return _apply(automorphism_matrix(rest), y)
    if kind == "phase":
        cos, sin = (Fraction(x) for x in rest.split(":"))
        return _apply(phase_matrix(cos, sin), y)
    raise ValueError(f"unknown transform {transform!r}")


def evaluate_point(spec: PointSpec) -> dict[str, Any]:
    base = y_from_split(spec.point)
    y = _transformed(base, spec.transform)
    obs = observables(y)
    stratum = certified_stratum(y)
    expected = REFLECTION_IMAGE.get(spec.stratum, spec.stratum) if "reflect" in spec.transform else spec.stratum
    row: dict[str, Any] = {
        "stratum": spec.stratum,
        "family": spec.family,
        "label": spec.label,
        "base": spec.base_label,
        "certified": stratum == expected and obs["nullity_left"] == NULLITY[expected],
        "observed_stratum": stratum,
        "obs": obs,
    }
    if spec.transform:
        row["identical_to_base"] = obs == observables(base)
    return row


def stratum_point_specs(item: tuple[str, RationalVector, list[int]]) -> list[PointSpec]:
    """Construct one stratum's movement and control points in their deterministic order."""
    name, rep, grid_indices = item
    specs: list[PointSpec] = []
    movement = programs()
    moved: dict[str, RationalVector] = {}
    for family, program in movement:
        label = program_label(program)
        point = apply_program(rep, program)
        moved[label] = point
        specs.append(PointSpec(name, family, label, point))
    grid_labels = []
    for index in grid_indices:
        label = f"grid:{index}"
        grid_labels.append(label)
        moved[label] = grid_point(index)
        specs.append(PointSpec(name, "grid", label, moved[label]))
    bases = ["rep", "u0:1", program_label(movement[-COMPOSITE_COUNT][1])]
    bases += grid_labels[:1]
    for base in bases:
        for aut in AUTOMORPHISM_NAMES:
            specs.append(PointSpec(name, "automorphism-image", f"{base}|{aut}", moved[base], f"aut:{aut}", base))
    for base in PHASE_BASES:
        for cos, sin in PHASES:
            label = f"{base}|phase:{cos}:{sin}"
            specs.append(PointSpec(name, "phase-image", label, moved[base], f"phase:{cos}:{sin}", base))
    return specs


def point_specs(grid: dict[str, list[int]]) -> list[PointSpec]:
    items = [(name, representative, grid[name]) for name, representative in REPRESENTATIVES.items()]
    return [spec for group in parallel.ordered_map(stratum_point_specs, items, min_items=1) for spec in group]


# ---------------------------------------------------------------------------------------------------------------------
# Real realizations of the movements, and the mutation control


def movement_maps() -> dict[str, Callable[[], Any]]:
    """Real 32 x 32 realizations of representative stratum-preserving movements, built on demand."""
    boost = BOOSTS[0]
    return {
        "unipotent u0:1": lambda: induced_real_map(lambda z: independent.act_g2(unipotent(0, Fraction(1)), z)),
        "unipotent u29:1": lambda: induced_real_map(lambda z: independent.act_g2(unipotent(29, Fraction(1)), z)),
        "unipotent u59:1": lambda: induced_real_map(lambda z: independent.act_g2(unipotent(59, Fraction(1)), z)),
        f"boost c={boost[0]} s={boost[1]}": lambda: induced_real_map(
            lambda z: independent.act_boost(boost[0], boost[1], z)
        ),
        "scale 2": lambda: induced_real_map(lambda z: [2 * x for x in z]),
        "mu-reflect": lambda: induced_real_map(lambda z: [*z[:7], -z[7], *z[8:]]),
        "phase 3/5 4/5": lambda: phase_matrix(Fraction(3, 5), Fraction(4, 5)),
    }


def verification_task(name: str) -> dict[str, Any]:
    """Automorphism failures of one named map: a compact automorphism, a movement or the mutated rotation."""
    if name in AUTOMORPHISM_NAMES:
        matrix = automorphism_matrix(name)
        kind = "compact automorphism"
    elif name == "mutated rotation":
        matrix = _mutated_matrix()
        kind = "mutated rotation, cos = sin = 4/5"
    else:
        matrix = movement_maps()[name]()
        kind = "stratum-preserving movement"
    return {"map": name, "kind": kind, "failed_basis_pairs": automorphism_failures(matrix), "pairs": DIM * DIM}


def doubling_pair_failure(pair: tuple[int, int]) -> int:
    """Compare one basis product with (a, b)(c, d) = (ac - conj(d) b, da + b conj(c))."""

    def conj(v: Sequence[Fraction]) -> list[Fraction]:
        return [v[0], *(-x for x in v[1:])]

    def product(x: Sequence[Fraction], y: Sequence[Fraction]) -> list[Fraction]:
        return list(cd_multiply_exact(HALF, x, y))

    p, q = pair
    a, b = _unit(p)[:HALF], _unit(p)[HALF:]
    c, d = _unit(q)[:HALF], _unit(q)[HALF:]
    first = [x - y for x, y in zip(product(a, c), product(conj(d), b), strict=True)]
    second = [x + y for x, y in zip(product(d, a), product(b, conj(c)), strict=True)]
    return int([*first, *second] != list(cd_multiply_exact(DIM, _unit(p), _unit(q))))


def doubling_failures() -> int:
    """Count convention failures across independent basis pairs with ordered parallel dispatch."""
    pairs = list(itertools.product(range(DIM), repeat=2))
    return sum(parallel.ordered_map(doubling_pair_failure, pairs, min_items=1))


def unipotent_task(item: tuple[int, Fraction]) -> bool:
    return bool(independent.is_automorphism(unipotent(item[0], item[1])))


# ---------------------------------------------------------------------------------------------------------------------
# Record


def _pattern_key(spectrum: list[tuple[int, tuple[str, ...]]]) -> str:
    """The multiplicity pattern of a spectrum: the sorted pairs (degree, multiplicity) of its irreducible factors."""
    return json.dumps(sorted([len(c) - 1, mult] for mult, c in spectrum))


def _unique_points(
    rows: list[dict[str, Any]], coordinates: dict[tuple[str, str], RationalVector]
) -> list[dict[str, Any]]:
    unique: dict[RationalVector, dict[str, Any]] = {}
    for row in rows:
        point = coordinates[(row["stratum"], row["label"])]
        if point in unique:
            _require(unique[point]["obs"] == row["obs"], "duplicate coordinates have different observables")
        else:
            unique[point] = row
    return list(unique.values())


def _summaries(rows: list[dict[str, Any]], specs: list[PointSpec]) -> dict[str, Any]:
    coordinates = {(spec.stratum, spec.label): spec.point for spec in specs if spec.family in FAMILIES}
    out: dict[str, Any] = {}
    for name in STRATA:
        evaluations = [r for r in rows if r["stratum"] == name and r["family"] in FAMILIES]
        sample = _unique_points(evaluations, coordinates)
        ranks = Counter(r["obs"]["rank_left"] for r in sample)
        spec_counts = Counter(r["obs"]["spectrum_id"] for r in sample)
        nullities = Counter(r["obs"]["nullity_left"] for r in sample)
        patterns = Counter(_pattern_key(r["obs"]["spectrum"]) for r in sample)
        witness_pattern = {}
        for value in sorted(patterns):
            witness_pattern[value] = next(r for r in sample if _pattern_key(r["obs"]["spectrum"]) == value)["label"]
        witness_rank = {}
        for value in sorted(ranks):
            first = next(r for r in sample if r["obs"]["rank_left"] == value)
            witness_rank[str(value)] = first["label"]
        out[name] = {
            "nullity": NULLITY[name],
            "points": len(sample),
            "evaluations": len(evaluations),
            "points_by_family": {
                family: len(_unique_points([row for row in evaluations if row["family"] == family], coordinates))
                for family in FAMILIES
            },
            "evaluations_by_family": {
                family: sum(1 for row in evaluations if row["family"] == family) for family in FAMILIES
            },
            "certified": sum(1 for r in sample if r["certified"]),
            "nullity_values": {str(k): v for k, v in sorted(nullities.items())},
            "rank_values": {str(k): v for k, v in sorted(ranks.items())},
            "rank_values_by_family": {
                f: {
                    str(k): v
                    for k, v in sorted(
                        Counter(
                            row["obs"]["rank_left"]
                            for row in _unique_points([row for row in evaluations if row["family"] == f], coordinates)
                        ).items()
                    )
                }
                for f in FAMILIES
            },
            "rank_right_equals_rank_left": all(r["obs"]["rank_left"] == r["obs"]["rank_right"] for r in sample),
            "nullity_right_equals_nullity_left": all(
                r["obs"]["nullity_left"] == r["obs"]["nullity_right"] for r in sample
            ),
            "consistent": all(r["obs"]["consistent"] for r in sample),
            "spectrum_values": dict(sorted(spec_counts.items())),
            "rank_witness": witness_rank,
            "multiplicity_pattern_values": dict(sorted(patterns.items())),
            "multiplicity_pattern_witness": witness_pattern,
            "rank_status": "varies" if len(ranks) > 1 else "constant on the sample",
            "spectrum_status": "varies" if len(spec_counts) > 1 else "constant on the sample",
            "rank_28_attained": 28 in ranks,
            "maximum_rank": max(ranks),
        }
    return out


def _spectra_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    table: dict[str, Any] = {}
    for row in rows:
        obs = row["obs"]
        key = obs["spectrum_id"]
        if key not in table:
            spectrum = obs["spectrum"]
            table[key] = {
                "factors": [{"multiplicity": mult, "coefficients_low_to_high": list(c)} for mult, c in spectrum],
                "rational_roots": {str(_linear_root(c)): mult for mult, c in spectrum if len(c) == 2},
                "irreducible_degrees_with_multiplicity": sorted([len(c) - 1, mult] for mult, c in spectrum),
                "rank_left": obs["rank_left"],
            }
    return dict(sorted(table.items()))


def _point_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    columns = [
        "family",
        "label",
        "certified",
        "nullity_left",
        "nullity_right",
        "rank_left",
        "rank_right",
        "spectrum",
        "norm",
    ]
    out: dict[str, Any] = {"columns": columns}
    for name in STRATA:
        out[name] = [
            [
                r["family"],
                r["label"],
                int(r["certified"]),
                r["obs"]["nullity_left"],
                r["obs"]["nullity_right"],
                r["obs"]["rank_left"],
                r["obs"]["rank_right"],
                r["obs"]["spectrum_id"],
                r["obs"]["norm"],
            ]
            for r in rows
            if r["stratum"] == name and r["family"] in FAMILIES
        ]
    return out


def _witnesses(rows: list[dict[str, Any]], specs: list[PointSpec]) -> dict[str, Any]:
    by_key = {(s.stratum, s.label): s for s in specs if s.family in FAMILIES}
    out: dict[str, Any] = {}
    for name in STRATA:
        seen: dict[int, dict[str, Any]] = {}
        for r in rows:
            if r["stratum"] != name or r["family"] not in FAMILIES:
                continue
            value = r["obs"]["rank_left"]
            if value not in seen:
                spec = by_key[(name, r["label"])]
                seen[value] = {
                    "label": r["label"],
                    "split_coordinates": [str(x) for x in spec.point],
                    "rank_left": value,
                    "spectrum": r["obs"]["spectrum_id"],
                    "norm": r["obs"]["norm"],
                }
        out[name] = [seen[k] for k in sorted(seen)]
    return out


def _controls(rows: list[dict[str, Any]]) -> dict[str, Any]:
    aut = [r for r in rows if r["family"] == "automorphism-image"]
    phase = [r for r in rows if r["family"] == "phase-image"]
    return {
        "automorphism_images": {
            "points": len(aut),
            "identical_to_base": sum(1 for r in aut if r["identical_to_base"]),
            "certified_in_stratum": sum(1 for r in aut if r["certified"]),
            "reflection_image_strata": sorted(
                {f"{r['stratum']} -> {r['observed_stratum']}" for r in aut if "reflect" in r["label"]}
            ),
            "observables_compared": (
                "nullity of L_y and R_y, ranks of both alternative operators, the factored spectrum of "
                "-L_y^2 / N, the unnormalized characteristic polynomial of -L_y^2 and the norm N"
            ),
        },
        "phase_images": {
            "points": len(phase),
            "identical_to_base": sum(1 for r in phase if r["identical_to_base"]),
            "certified_in_stratum": sum(1 for r in phase if r["certified"]),
            "differing": [f"{r['stratum']} {r['label']}" for r in phase if not r["identical_to_base"]],
        },
    }


def build_record() -> dict[str, Any]:
    for name, (_key, strata_key) in STRATA.items():
        _require(
            tuple(Fraction(x) for x in strata.REPS[strata_key]) == REPRESENTATIVES[name],
            f"representative {name} differs between the regularity verifier and the strata script",
        )
    _require(len(set(PATTERNS.values())) == len(STRATA), "two representatives share a membership pattern")
    grid, grid_counts = grid_selection()
    specs = point_specs(grid)
    rows = parallel.ordered_map(evaluate_point, specs, min_items=1)
    unipotent_items = list(itertools.product(range(len(_nilpotents())), UNIPOTENT_PARAMETERS))
    unipotent_ok = parallel.ordered_map(unipotent_task, unipotent_items, min_items=1)
    names = [*AUTOMORPHISM_NAMES, "mutated rotation", *movement_maps()]
    verification = parallel.ordered_map(verification_task, names, min_items=1)
    spectra = _spectra_table(rows)
    summary = _summaries(rows, specs)
    controls = _controls(rows)
    mutated = next(v for v in verification if v["map"] == "mutated rotation")
    base_obs = observables(y_from_split(REPRESENTATIVES["W8"]))
    mutated_image = observables(_apply(_mutated_matrix(), y_from_split(REPRESENTATIVES["W8"])))
    compact_ok = all(v["failed_basis_pairs"] == 0 for v in verification if v["kind"] == "compact automorphism")
    movements = [v for v in verification if v["kind"] == "stratum-preserving movement"]
    doubling = doubling_failures()
    checks = {
        "cd_core at dimension 32 is the doubling of dimension 16": doubling == 0,
        "every point is certified in its stratum": all(r["certified"] for r in rows),
        "every point satisfies the structural identities": all(r["obs"]["consistent"] for r in rows),
        "every unipotent is a split octonion automorphism": all(unipotent_ok),
        "every compact map is an automorphism of A_5": compact_ok,
        "the mutated rotation breaks basis products": mutated["failed_basis_pairs"] > 0,
        "the mutated rotation changes the observables": mutated_image != base_obs,
        "every stratum-preserving movement breaks basis products": all(
            v["failed_basis_pairs"] > 0 for v in movements if not v["map"].startswith("phase")
        ),
        "every automorphism image keeps every observable": (
            controls["automorphism_images"]["identical_to_base"] == controls["automorphism_images"]["points"]
        ),
    }
    passed = all(checks.values())
    inputs = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            HERE / "associator_observables.py",
            ROOT / "gororoba_quantum" / "cd_core.py",
            ROOT / "gororoba_quantum" / "parallel.py",
            HERE.parent / "a5-strata-regularity" / "verify_regularity_independent.py",
            HERE.parent / "a5-strata-regularity" / "strata_regularity.py",
            HERE.parent / "a5-rank-strata-equations" / "rederive_strata_equations.py",
        )
    }
    return {
        "schema": SCHEMA,
        "script_sha256": inputs["docs/evidence/a5-associator-observables/associator_observables.py"],
        "inputs": inputs,
        "strata": list(STRATA),
        "representatives": {
            name: {
                "split_coordinates": [str(x) for x in point],
                "pattern": PATTERNS[name],
                "nullity_left": NULLITY[name],
            }
            for name, point in REPRESENTATIVES.items()
        },
        "enumeration": {
            "unipotent_parameters": [str(t) for t in UNIPOTENT_PARAMETERS],
            "nilpotent_derivations": len(_nilpotents()),
            "unipotents_are_split_octonion_automorphisms": f"{sum(unipotent_ok)} of {len(unipotent_ok)}",
            "boosts": [[str(c), str(s)] for c, s in BOOSTS],
            "composite_count": COMPOSITE_COUNT,
            "grid": {
                "alphabet": [-1, 0, 1],
                "candidate_rule": "mu' = 0, eta(u') = -eta(v'), eta(u', v') = 0, or Q = 0 and Delta = 0",
                "stride": GRID_STRIDE,
                "per_stratum": GRID_PER_STRATUM,
                "members_at_stride_by_stratum": grid_counts,
            },
            "compact_automorphisms": {
                name: [[index, str(c), str(s)] for index, c, s in spec] for name, spec in AUTOMORPHISMS.items()
            },
            "phases": [[str(c), str(s)] for c, s in PHASES],
        },
        "doubling_convention_failed_basis_pairs": doubling,
        "map_verification": verification,
        "mutation_control": {
            "name": "rotation with cos = sin = 4/5",
            "failed_basis_pairs": mutated["failed_basis_pairs"],
            "observables_differ_at_W8_representative": mutated_image != base_obs,
        },
        "controls": controls,
        "summary": summary,
        "spectra": spectra,
        "witnesses": _witnesses(rows, specs),
        "points": _point_rows(rows),
        "checks": checks,
        "pass": passed,
    }


def _mutated_matrix() -> Any:
    d = _derivation_matrices()[0]
    block = flint.fmpq_mat(8, 8, [1 if i == j else 0 for i in range(8) for j in range(8)])
    return _block_diagonal(block + _q(Fraction(4, 5)) * d + _q(Fraction(1, 5)) * (d * d))


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the deterministic JSON record")
    mode.add_argument("--check", action="store_true", help="recompute the record and compare it byte for byte")
    arguments = parser.parse_args()
    record = build_record()
    failed = [name for name, ok in record["checks"].items() if not ok]
    _require(not failed, "failed checks: " + "; ".join(failed))
    rendered = _record_bytes(record)
    if arguments.write:
        RECORD.write_bytes(rendered)
    else:
        retained = RECORD.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )
    for name, row in record["summary"].items():
        print(name, row["points"], row["rank_values"], len(row["spectrum_values"]), sep="\t")


if __name__ == "__main__":
    main()
