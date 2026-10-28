"""External replay of the repository's three-dimensional point sets through spglib and SeeK-path.

spglib finds the space group of a periodic cell (basis, fractional positions, site types); SeeK-path standardizes
that cell after the HPKOT convention and returns the extended Bravais symbol, labeled k-points and band path. Neither
accepts a finite point set or a lattice of dimension other than 3, so the replay feeds them two kinds of input:

- the integer lattice a point set spans, as a one-site cell, which fixes its Bravais type;
- the finite set itself inside a cubic box of edge BOX, as one site per point. The box lattice is cubic and holds
  the set's full symmetry, and the space-group operations with zero translation are the set's point group about the
  origin. For the planar S_2 the embedding adds the mirror z -> -z, so the replay keeps the operations that fix e_z.

Sections:

1. Coordinate projection of the D14 roots +-e_i +-e_j (i < j < 14) onto three of the fourteen axes: the 19 distinct
   images, their multiplicities, and the lattices the shells span.
2. The star lattices S_3 (tetrahedral boundary) and S_2 (Tuna-17), whose point groups are compared field by field
   with the boundary_symmetry rows of docs/evidence/cd-star-lattice/census.json.
3. Brillouin-zone face counts of the cubic lattices from seekpath.brillouinzone.BZ.
4. Textbook cells: the conventional FCC copper cell, a one-site cubic cell, a two-site honeycomb layer and a
   five-site heavy-hex layer, each with a vacuum axis where planar.
5. The dimension guard: a 14 x 14 lattice.

Usage, from the repository root, with SEEKPATH_PYTHON an interpreter that imports seekpath and scipy:

    "$SEEKPATH_PYTHON" docs/evidence/seekpath-lattice-crosscheck/seekpath_replay.py \
        > docs/evidence/seekpath-lattice-crosscheck/seekpath_replay.txt
"""

from __future__ import annotations

import itertools
import json
import math
import platform
import sys
import warnings
from collections import Counter
from collections.abc import Iterable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import seekpath
import spglib
from seekpath.brillouinzone.brillouinzone import BZ

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_star_lattice import ball, cd_boundary, tetrahedral_boundary  # noqa: E402

from parallel import ordered_map  # noqa: E402

CENSUS = ROOT / "docs/evidence/cd-star-lattice/census.json"
# Box edge for a finite set: larger than twice the set's radius, so no point meets a periodic image.
BOX = 20
D14_RANK = 14
PROJECTION_AXES = (0, 1, 2)

Cell = tuple[list[list[float]], list[list[float]], list[int]]


class ReplayError(RuntimeError):
    """A recomputed fact disagrees with its closed form or with the retained census."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def frac(value: float) -> str:
    return str(Fraction(value).limit_denominator(48))


def one_site(basis: Sequence[Sequence[int]]) -> Cell:
    return [list(map(float, row)) for row in basis], [[0.0, 0.0, 0.0]], [1]


def boxed(points: Iterable[Sequence[int]]) -> Cell:
    pts = [list(p) + [0] * (3 - len(p)) for p in points]
    return (
        [[float(BOX), 0.0, 0.0], [0.0, float(BOX), 0.0], [0.0, 0.0, float(BOX)]],
        [[c / BOX for c in p] for p in pts],
        [1] * len(pts),
    )


def span_index(points: Iterable[Sequence[int]]) -> int:
    """Index in Z^3 of the integer span: the gcd of all 3 x 3 minors."""
    g = 0
    for rows in itertools.combinations(points, 3):
        g = math.gcd(g, abs(round(np.linalg.det(np.array(rows, dtype=float)))))
    return g


def point_group(cell: Cell, planar: bool) -> list[np.ndarray]:
    """Rotations of the space-group operations with zero translation, as integer matrices."""
    dataset = spglib.get_symmetry_dataset(cell)
    require(dataset is not None, "spglib found no symmetry")
    ops = []
    for rotation, translation in zip(dataset.rotations, dataset.translations, strict=True):
        if np.allclose(translation - np.round(translation), 0.0) and (not planar or rotation[2][2] == 1):
            ops.append(np.array(rotation, dtype=int))
    return ops


def element_order(matrix: np.ndarray) -> int:
    power = matrix.copy()
    for order in range(1, 13):
        if np.array_equal(power, np.eye(3, dtype=int)):
            return order
        power = power @ matrix
    raise ReplayError("element order exceeds 12")


def group_profile(ops: list[np.ndarray], planar: bool) -> dict[str, Any]:
    """Order, determinants and element orders; a planar set's -1 is diag(-1, -1, 1), its determinant the 2 x 2 one."""
    dets = Counter(str(round(np.linalg.det(m))) for m in ops)
    orders = Counter(str(element_order(m)) for m in ops)
    minus = np.diag([-1, -1, 1]) if planar else -np.eye(3, dtype=int)
    minus_one = any(np.array_equal(m, minus) for m in ops)
    return {
        "order": len(ops),
        "determinant_counts": dict(sorted(dets.items())),
        "element_order_profile": dict(sorted(orders.items(), key=lambda kv: int(kv[0]))),
        "contains_minus_one": minus_one,
    }


def census_row(census: dict[str, Any], dimension: int) -> dict[str, Any]:
    if dimension == 3:
        return census["tetrahedral_3d"]["boundary_symmetry"]
    return next(row for row in census["cayley_dickson"] if row["dimension"] == dimension)["boundary_symmetry"]


def describe_path(task: tuple[str, Cell]) -> list[str]:
    """Report lines of seekpath.get_path for one labeled cell; a module-level worker for ordered_map."""
    label, cell = task
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = seekpath.get_path(cell)
    path = " ".join(f"{a}-{b}" for a, b in result["path"])
    points = ", ".join(f"{k} ({' '.join(frac(x) for x in v)})" for k, v in sorted(result["point_coords"].items()))
    raised = sorted({w.category.__name__ for w in caught})
    return [
        f"{label}: spacegroup {result['spacegroup_number']} {result['spacegroup_international']}"
        f" bravais {result['bravais_lattice_extended']} inversion {result['has_inversion_symmetry']}"
        f" warnings {raised}",
        f"  path {path}",
        f"  points {points}",
    ]


def print_paths(tasks: list[tuple[str, Cell]]) -> None:
    for lines in ordered_map(describe_path, tasks):
        print("\n".join(lines))


def star_case(task: tuple[str, list[tuple[int, ...]], bool]) -> tuple[str, int, str, dict[str, Any]]:
    """spglib space group and point-group profile of one boxed star lattice; a worker for ordered_map."""
    label, points, planar = task
    cell = boxed(points)
    dataset = spglib.get_symmetry_dataset(cell)
    require(dataset is not None, f"spglib found no symmetry for {label}")
    heading = f"{dataset.number} {dataset.international} point group {dataset.pointgroup}"
    return label, len(points), heading, group_profile(point_group(cell, planar), planar)


def bz_faces(real: list[list[float]]) -> int:
    """Face count of the first Brillouin zone of a real-space basis; a worker for ordered_map."""
    reciprocal = 2 * np.pi * np.linalg.inv(np.array(real, dtype=float)).T
    return len(BZ(*reciprocal).faces)


def section_d14() -> None:
    print("== 1. D14 coordinate projection")
    roots = []
    for i, j in itertools.combinations(range(D14_RANK), 2):
        for s, t in itertools.product((1, -1), repeat=2):
            root = [0] * D14_RANK
            root[i], root[j] = s, t
            roots.append(root)
    images = Counter(tuple(r[a] for a in PROJECTION_AXES) for r in roots)
    shells: dict[int, list[tuple[int, ...]]] = {}
    for image in images:
        shells.setdefault(sum(c * c for c in image), []).append(image)
    multiplicity = {k: sorted({images[p] for p in shells[k]}) for k in sorted(shells)}
    z3_ball = {p for p in itertools.product((-1, 0, 1), repeat=3) if sum(c * c for c in p) <= 2}
    rest = D14_RANK - len(PROJECTION_AXES)
    require(len(roots) == 364 and len(images) == 19, "root or image count")
    require(set(images) == z3_ball, "images differ from the Z^3 ball of squared radius 2")
    require(multiplicity == {0: [4 * math.comb(rest, 2)], 1: [2 * rest], 2: [1]}, "multiplicities")
    print(f"roots {len(roots)} distinct images {len(images)} equal to Z^3 ball |v|^2 <= 2: True")
    for k in sorted(shells):
        print(f"  squared norm {k}: {len(shells[k])} images, multiplicity {multiplicity[k][0]} each")
    index_shell = span_index(shells[2])
    index_all = span_index(list(images))
    print(f"index in Z^3 of the span of the 12 images of squared norm 2: {index_shell}")
    print(f"index in Z^3 of the span of all 19 images: {index_all}")
    require((index_shell, index_all) == (2, 1), "span indices")
    print_paths(
        [
            ("span of the 12-shell (D3, basis 011 101 110)", one_site([[0, 1, 1], [1, 0, 1], [1, 1, 0]])),
            ("span of all 19 images (Z^3)", one_site([[1, 0, 0], [0, 1, 0], [0, 0, 1]])),
        ]
    )
    dataset = spglib.get_symmetry_dataset(boxed(sorted(images)))
    print(f"19 images in a cubic box: spacegroup {dataset.number} {dataset.international}"
          f" point group {dataset.pointgroup}")  # fmt: skip


def section_star(census: dict[str, Any]) -> None:
    print("== 2. Star lattices against census.json boundary_symmetry")
    dimensions = (3, 2)
    tasks = [
        ("S_3 tetrahedral boundary", sorted(ball(3) | tetrahedral_boundary()), False),
        ("S_2 Tuna-17", sorted(ball(2) | cd_boundary(2)), True),
        ("S_3 ball without boundary", sorted(ball(3)), False),
    ]
    results = ordered_map(star_case, tasks)
    for dimension, (label, count, heading, profile), (_, _, planar) in zip(
        dimensions, results[:2], tasks[:2], strict=True
    ):
        expected = census_row(census, dimension)
        fields = ("order", "determinant_counts", "element_order_profile", "contains_minus_one")
        agree = {f: profile[f] == expected[f] for f in fields}
        print(f"{label}: points {count} spglib {heading}{' (z-fixing subgroup kept)' if planar else ''}")
        print(f"  spglib profile {json.dumps(profile, sort_keys=True)}")
        print(f"  census agreement {json.dumps(agree, sort_keys=True)}")
        require(all(agree.values()), f"{label} disagrees with census.json")
    label, _, heading, _ = results[2]
    print(f"{label}: spacegroup {heading}")


def section_bz() -> None:
    print("== 3. Brillouin-zone faces (seekpath.brillouinzone.BZ, reciprocal basis 2 pi A^-T)")
    lattices = {
        "simple cubic": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "face-centered cubic": [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
        "body-centered cubic": [[-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5]],
    }
    expected = {"simple cubic": 6, "face-centered cubic": 14, "body-centered cubic": 12}
    for name, faces in zip(lattices, ordered_map(bz_faces, list(lattices.values())), strict=True):
        print(f"{name}: {faces} faces")
        require(faces == expected[name], f"{name} face count")


def section_textbook_cells() -> None:
    print("== 4. Textbook cells and the heavy-hex layer")
    hexagonal = [[1.0, 0.0, 0.0], [-0.5, 3**0.5 / 2, 0.0], [0.0, 0.0, 10.0]]
    cells: list[tuple[str, Cell]] = [
        ("FCC Cu conventional cell", (
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            [[0.0, 0.0, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]],
            [29, 29, 29, 29],
        )),
        ("one-site cubic cell", ([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.0]], [1])),
        ("two-site honeycomb layer", (hexagonal, [[0.0, 0.0, 0.5], [1 / 3, 2 / 3, 0.5]], [6, 6])),
        ("five-site heavy-hex layer", (
            hexagonal,
            [[1 / 3, 2 / 3, 0.5], [2 / 3, 1 / 3, 0.5], [0.5, 0.0, 0.5], [0.0, 0.5, 0.5], [0.5, 0.5, 0.5]],
            [1, 1, 2, 2, 2],
        )),
    ]  # fmt: skip
    print_paths(cells)


def section_dimension() -> None:
    print("== 5. Dimension guard")
    try:
        seekpath.get_path((np.eye(D14_RANK).tolist(), [[0.0] * D14_RANK], [1]))
    except Exception as error:  # noqa: BLE001 - the replay records whatever the library raises
        print(f"14 x 14 lattice: {type(error).__name__}: {' '.join(str(error).split())}")
        return
    raise ReplayError("a 14 x 14 lattice was accepted")


def main() -> int:
    print(
        f"python {platform.python_version()} seekpath {seekpath.__version__} spglib {spglib.__version__}"
        f" numpy {np.__version__} scipy {scipy.__version__}"
    )
    census = json.loads(CENSUS.read_text())
    section_d14()
    section_star(census)
    section_bz()
    section_textbook_cells()
    section_dimension()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
