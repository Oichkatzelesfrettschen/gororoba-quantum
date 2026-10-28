# seekpath

## NAME

seekpath 2.2.2 -- crystal-cell standardization, Bravais-lattice detection,
labeled high-symmetry k-points, recommended band paths and first Brillouin
zones of three-dimensional periodic crystals, after the HPKOT convention of
Hinuma, Pizzi, Kumagai, Oba and Tanaka
([1602.06402](../papers/1602.06402.md)); symmetry detection is delegated to
spglib ([1808.01590](../papers/1808.01590.md)).

## SYNOPSIS

```python
import seekpath
cell = (lattice_rows_3x3, fractional_positions_Nx3, type_numbers_N)
seekpath.get_path(cell, with_time_reversal=True, recipe="hpkot",
                  threshold=1e-7, symprec=1e-5, angle_tolerance=-1.0)
seekpath.get_explicit_k_path(cell, with_time_reversal=True, reference_distance=0.025, ...)
seekpath.get_path_orig_cell(cell, ...)              # no standardization
seekpath.get_explicit_k_path_orig_cell(cell, ...)   # no standardization
from seekpath.brillouinzone.brillouinzone import BZ  # needs scipy
BZ(b1, b2, b3).faces; BZ(b1, b2, b3).is_inside_bz(k)
```

| Substrate | Status |
| --- | --- |
| Build host | not an Arch package; installed from the PyPI sdist into a virtual environment under `${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/` with spglib 2.8.0 (wheel), numpy 2.5.4 and scipy 1.18.1 on Python 3.14.8. The system `python3` carries spglib 2.8.1.dev0 from the `spglib` 2.8.0 Arch package and no seekpath. |
| Repository pins | none: `requirements.txt`, `ci/requirements-ci.txt` and `KERNEL_PINS` hold no seekpath or spglib, and no gate imports either. |
| Kaggle | not in any `PIN_GROUPS` group. |
| Retained source | [seekpath-2.2.2.tar.gz](../../source_archives/seekpath-2.2.2.tar.gz), the PyPI sdist https://files.pythonhosted.org/packages/source/s/seekpath/seekpath-2.2.2.tar.gz (44,937 bytes, SHA-256 `d3bb08b7fb21d5cff5fc27aff9904a865da5e0648fc0f8fef699642d88e27f2b`), MIT; the installed `seekpath/` tree is byte-identical to the archive's `seekpath-2.2.2/seekpath/` (`diff -r`, `__pycache__` excluded). |

Install, from any directory:

```sh
PYTHON=${PYTHON:-python3}
VENV="${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/seekpath-venv"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" install seekpath==2.2.2 spglib==2.8.0 scipy==1.18.1 numpy==2.5.4
```

## CAPABILITIES IN THIS REPOSITORY

The repository computes no band structures, so seekpath's k-path output has
no consumer here. Its one productive role is an independent implementation
of three-dimensional symmetry and lattice classification that can check
claims the repository's own exact code makes about three-dimensional point
sets. The [lattice cross-check
replay](../../evidence/seekpath-lattice-crosscheck/README.md) uses it for:

- The Bravais type of the integer lattice a point set spans. The coordinate
  projection of the 364 D14 roots onto three axes is the Z^3 ball of squared
  radius 2, which spans the primitive cubic lattice (Pm-3m, `cP2`); its
  12-point cuboctahedral shell alone spans the face-centered cubic lattice
  D3 (Fm-3m, `cF2`) at index 2 in Z^3. The [AFLOW prototype
  note](../papers/aflow-a_cf4-225-a.md) carries the consequence for the FCC
  comparison.
- The point group of a finite set, through a one-site-per-point cell in a
  cubic box. The tetrahedral star lattice S_3 returns m-3 (Th, order 24, 12
  operations of determinant -1, element orders 1, 2^7, 3^8, 6^8), equal field
  by field to the `tetrahedral_3d` row of
  [census.json](../../evidence/cd-star-lattice/census.json); S_2 (Tuna-17)
  returns 4/m, whose z-fixing subgroup C4 equals the `dimension: 2` row.
- Brillouin-zone shapes: 6, 14 and 12 faces for the simple, face-centered and
  body-centered cubic lattices.

Out of reach: any lattice of dimension other than 3 (D14, A13 and the
star lattices S_n for n >= 4 included; spglib raises `SpglibError: lattice
has to be a (3, 3) array`), any finite set treated as a crystal without the
box construction, and the finite 156-qubit Heron r2 coupling graph, which is
a patch of heavy-hex and carries no translation symmetry. The infinite
heavy-hex layer is P6/mmm (`hP2`) with a five-site cell, a fact with no
repository workflow behind it.

## API ENTRY POINTS

`seekpath.__all__` (2.2.2): `get_path`, `get_explicit_k_path`,
`get_path_orig_cell`, `get_explicit_k_path_orig_cell`, `EdgeCaseWarning`,
`SymmetryDetectionError`, `SupercellWarning`, `brillouinzone` (a lazy
module attribute: `seekpath.brillouinzone` imports scipy on first access, so
`import seekpath` works without scipy). The package ships no console script:
the wheel's `RECORD` lists no `bin/` entry and the dist-info carries no
`entry_points.txt`. The four functions are the whole command surface.

### Input cell

Every function takes `structure = (cell, positions, numbers)` in spglib's
tuple form: `cell` is 3 x 3 with lattice vectors as rows (`cell[0]` is
**a**), `positions` is N x 3 in fractional coordinates of those rows,
`numbers` is N positive integers that label site types (atomic numbers by
convention; any distinct positive integers distinguish sites, for example 6
and 1006 for two inequivalent carbons). `seekpath.util.atoms_num_dict` maps
element symbols to atomic numbers for building `numbers`.

Common keyword arguments:

| Argument | Default | Effect |
| --- | --- | --- |
| `with_time_reversal` | `True` | `False` on a structure without inversion appends the inverted wedge: every label gains a primed copy and the path doubles (`augmented_path` True) |
| `recipe` | `"hpkot"` | the only implemented recipe; any other value raises `ValueError` |
| `threshold` | `1e-7` | tolerance for the lattice-parameter comparisons that pick the extended Bravais type (oC1 if a < b, oC2 if a > b, ...); a comparison inside the threshold issues `EdgeCaseWarning` and still picks a case |
| `symprec` | `1e-5` | spglib's distance tolerance epsilon (Cartesian, the units of `cell`) |
| `angle_tolerance` | `-1.0` | spglib's angle tolerance; a negative value makes spglib reuse the distance tolerance for angle comparisons |
| `reference_distance` | `0.025` | explicit-path functions only: target spacing between successive k-points in 1/length units of `cell` (1/angstrom for a cell in angstrom), rounded so each segment holds an integer number of points |

### get_path

Standardizes the cell and returns the HPKOT labels and path. Flow
(`seekpath/hpkot/__init__.py`): `check_spglib_version` (raises below spglib
1.9.4, warns below 1.13) -> `spglib.get_symmetry_dataset(structure, symprec,
angle_tolerance)` (None raises `SymmetryDetectionError`) -> the standardized
conventional cell `std_lattice`, `std_positions`, `std_types` and spglib's
`std_rotation_matrix` -> the first two characters of the extended Bravais
symbol from the space-group number through the `spg_db.spgroup_data` table
(crystal family, centering, inversion) -> the third character from the
space-group number or lattice-parameter logic of HPKOT Table 94 (aP via
spglib's Niggli reduction) -> the tables in
`band_path_data/<extended symbol>/` -> axial-ratio-dependent k-point
coefficients through `extend_kparam` and `eval_expr` -> the primitive cell
through `get_primitive` with the HPKOT matrix P of `get_P_matrix`.

Return keys (20):

| Key | Content |
| --- | --- |
| `point_coords` | label -> k-point coefficients in the basis of `reciprocal_primitive_lattice` |
| `path` | list of (start, end) label pairs; a jump `X|Y` is two consecutive pairs that share no label |
| `has_inversion_symmetry` | whether the point group contains -1 |
| `augmented_path` | True when inversion is absent and `with_time_reversal=False` |
| `bravais_lattice` | two-character symbol: aP, mP, mC, oP, oF, oI, oC, oA, tP, tI, hP, hR, cP, cF, cI |
| `bravais_lattice_extended` | HPKOT extended symbol, one of the 29 `band_path_data` directories: aP2, aP3, cF1, cF2, cI1, cP1, cP2, hP1, hP2, hR1, hR2, mC1, mC2, mC3, mP1, oA1, oA2, oC1, oC2, oF1, oF2, oF3, oI1, oI2, oI3, oP1, tI1, tI2, tP1 |
| `spacegroup_number`, `spacegroup_international` | from the spglib dataset |
| `conv_lattice`, `conv_positions`, `conv_types` | spglib's standardized conventional cell |
| `primitive_lattice`, `primitive_positions`, `primitive_types` | conventional cell times P, duplicates merged |
| `reciprocal_primitive_lattice` | rows b_i with a_i . b_j = 2 pi delta_ij |
| `primitive_transformation_matrix`, `inverse_primitive_transformation_matrix` | P and P^-1; det(P^-1) is the conventional-to-primitive volume ratio |
| `rotation_matrix` | Cartesian rotation from the input cell to the standardized one |
| `volume_original_wrt_conv`, `volume_original_wrt_prim` | input volume over conventional or primitive volume, negative for a left-handed input |

### get_explicit_k_path

Calls `get_path`, then `get_explicit_from_implicit` samples each segment.
Adds five keys to the `get_path` result:

| Key | Content |
| --- | --- |
| `explicit_kpoints_rel` | k-points in the reciprocal primitive basis |
| `explicit_kpoints_abs` | the same in Cartesian 1/length |
| `explicit_kpoints_labels` | label at a segment end, empty string elsewhere |
| `explicit_kpoints_linearcoord` | cumulative path length, the x axis of a band plot |
| `explicit_segments` | half-open (start, stop) slices into the arrays, one per `path` pair; a continuous path starts the next slice at the previous slice's last index, a jump starts it at the previous slice's stop |

### get_path_orig_cell and get_explicit_k_path_orig_cell

Return the same labels and path expressed in the reciprocal basis of the
input cell, with no standardization or rotation. The result carries
`augmented_path`, `bravais_lattice`, `bravais_lattice_extended`,
`has_inversion_symmetry`, `is_supercell`, `path`, `point_coords`,
`spacegroup_international` and `spacegroup_number`, and none of the cell
keys. When the input is a supercell of a smaller primitive cell, the
coefficients are those of the primitive cell's path written in the
supercell basis, the labels no longer sit at zone-boundary points of the
supercell's own zone, and `SupercellWarning` is issued.

### Exceptions and warnings

| Name | Raised when |
| --- | --- |
| `SymmetryDetectionError` (`seekpath.hpkot`) | spglib returns no dataset, for example two atoms on one site |
| `EdgeCaseWarning` (`RuntimeWarning`) | a lattice-parameter comparison falls inside `threshold` (tI with a ~ c, oC with a ~ b, ...) |
| `SupercellWarning` (`UserWarning`) | an `*_orig_cell` input is an undistorted supercell |
| `ValueError` | unknown `recipe`; spglib older than 1.9.4 |

### seekpath.brillouinzone

`BZ(b1, b2, b3)` builds the first Brillouin zone from three reciprocal
vectors: the 7 x 7 x 7 block of reciprocal lattice points `i b1 + j b2 + k
b3`, |i|, |j|, |k| <= 3, goes to `scipy.spatial.Voronoi`, and the Voronoi
region of the origin is the zone. Attributes: `b_vectors`, `hull`
(`scipy.spatial.ConvexHull`), `delaunay`, `triangles_vertices`, `triangles`
(outward-oriented), `faces` (coplanar triangles merged into polygons,
unoriented). Method: `is_inside_bz(k)` (Delaunay simplex lookup).
`get_BZ(b1, b2, b3)` returns the same data as a dictionary and is deprecated
in favor of the class.

### Internal modules

| Module | Names |
| --- | --- |
| `seekpath.getpaths` | the four public functions and `get_explicit_from_implicit(seekpath_output, reference_distance)` |
| `seekpath.hpkot` | `get_path` (the recipe), `EdgeCaseWarning`, `SymmetryDetectionError`; `band_path_data/<symbol>/` holds `path.txt`, `points.txt`, `k_vector_parameters.txt` and two example POSCARs (`POSCAR_inversion`, `POSCAR_noinversion`, from the Materials Project) |
| `seekpath.hpkot.tools` | `check_spglib_version`, `get_dot_access_dataset` (a namespace over the dict datasets of spglib < 2.5), `get_cell_params` (a, b, c, cos alpha, cos beta, cos gamma), `get_reciprocal_cell_rows`, `get_real_cell_from_reciprocal_rows`, `get_path_data`, `extend_kparam`, `eval_expr`, `eval_expr_simple` (the fewer than 40 tabulated coefficient expressions, mapped to Python functions instead of parsed) |
| `seekpath.hpkot.spg_mapping` | `get_crystal_family`, `pointgroup_has_inversion` (spglib point-group index 1-32), `pgnum_from_pgint`, `get_spgroup_data` (the stored table), `get_spgroup_data_realtime` (the same table rebuilt from the 530 Hall settings through spglib), `get_P_matrix`, `get_primitive` |
| `seekpath.hpkot.spg_db` | `spgroup_data` and `centering` tables |
| `seekpath.util` | `atoms_num_dict` |

The `aiidawrappers` module named in section 5 of the HPKOT paper is absent
from 2.2.2.

## EXAMPLES

Run with the virtual environment's interpreter; spglib 2.8.0 emits a
`DeprecationWarning` ("Set OLD_ERROR_HANDLING to false and catch the errors
directly") on every call, which the script silences.

```python
import warnings
import numpy as np
import seekpath
from seekpath.brillouinzone.brillouinzone import BZ
warnings.filterwarnings("ignore", category=DeprecationWarning)

fcc = ([[4.0, 0, 0], [0, 4.0, 0], [0, 0, 4.0]], [[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]], [29] * 4)
r = seekpath.get_path(fcc)
print("bravais", r["bravais_lattice_extended"], "sg", r["spacegroup_number"], r["spacegroup_international"])
print("primitive_lattice", np.round(r["primitive_lattice"], 6).tolist())
print("primitive_transformation_matrix", np.round(r["primitive_transformation_matrix"], 6).tolist())
print("volume_original_wrt_prim", r["volume_original_wrt_prim"], "wrt_conv", r["volume_original_wrt_conv"])

e = seekpath.get_explicit_k_path(fcc, reference_distance=0.05)
labels = [(i, l) for i, l in enumerate(e["explicit_kpoints_labels"]) if l]
print("kpoints", len(e["explicit_kpoints_abs"]), "labeled", labels[:8], "segments", e["explicit_segments"][:3])

zb = ([[5.65, 0, 0], [0, 5.65, 0], [0, 0, 5.65]],
      [[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0],
       [.25, .25, .25], [.25, .75, .75], [.75, .25, .75], [.75, .75, .25]],
      [31] * 4 + [33] * 4)
z = seekpath.get_path(zb, with_time_reversal=False)
print("zincblende", z["spacegroup_international"], "inversion", z["has_inversion_symmetry"], "augmented", z["augmented_path"])
print("  path", z["path"])

ti = ([[3, 0, 0], [0, 3, 0], [0, 0, 3]],
      [[0, 0, 0], [.5, .5, .5], [0, 0, .3], [0, 0, .7], [.5, .5, .8], [.5, .5, .2]], [1, 1, 2, 2, 2, 2])
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    t = seekpath.get_path(ti)
    print(t["spacegroup_international"], t["bravais_lattice_extended"],
          [str(x.message) for x in w if x.category is seekpath.EdgeCaseWarning])

sc = ([[2.0, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 0], [.5, 0, 0]], [1, 1])
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    o = seekpath.get_path_orig_cell(sc)
    print("orig-cell supercell", sorted({x.category.__name__ for x in w if x.category is not DeprecationWarning}),
          "X_1", [float(c) for c in o["point_coords"]["X_1"]])

bz = BZ(*(2 * np.pi * np.eye(3)))
print("cube BZ faces", len(bz.faces), "triangles", len(bz.triangles),
      bz.is_inside_bz([0.4 * 2 * np.pi, 0, 0]), bz.is_inside_bz([0.6 * 2 * np.pi, 0, 0]))
try:
    seekpath.get_path(([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 0], [0, 0, 0]], [1, 1]))
except seekpath.SymmetryDetectionError as ex:
    print("overlapping atoms:", ex)
```

Output on the build host:

```text
bravais cF2 sg 225 Fm-3m
primitive_lattice [[0.0, 2.0, 2.0], [2.0, 0.0, 2.0], [2.0, 2.0, 0.0]]
primitive_transformation_matrix [[0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]]
volume_original_wrt_prim 4.0 wrt_conv 1.0
kpoints 135 labeled [(0, 'GAMMA'), (30, 'X'), (40, 'U'), (41, 'K'), (73, 'GAMMA'), (99, 'L'), (120, 'W'), (134, 'X')] segments [(0, 31), (30, 41), (41, 74)]
zincblende F-43m inversion False augmented True
  path [('GAMMA', 'X'), ('X', 'U'), ('K', 'GAMMA'), ('GAMMA', 'L'), ('L', 'W'), ('W', 'X'), ('GAMMA', "X'"), ("X'", "U'"), ("K'", 'GAMMA'), ('GAMMA', "L'"), ("L'", "W'"), ("W'", "X'")]
I4/mmm tI1 ['tI lattice, but a almost equal to c']
orig-cell supercell ['SupercellWarning'] X_1 [1.0, 0.0, 0.0]
cube BZ faces 6 triangles 12 True False
overlapping atoms: Spglib could not detect the symmetry of the system
```

Reading the output: the slices `(0, 31)` and `(30, 41)` both hold index 30,
the X point where the path continues; `(30, 41)` ends at U (index 40) and
`(41, 74)` begins at K (index 41), the jump U|K. In the 2 x 1 x 1 supercell the primitive cell's X_1 = (1/2,
0, 0) becomes (1, 0, 0) of the doubled reciprocal basis, which is a
reciprocal lattice vector of the supercell, the case `SupercellWarning`
flags.

## TRAPS

- The returned `point_coords` refer to `reciprocal_primitive_lattice` of the
  standardized cell, which `rotation_matrix` rotates away from the input and
  P re-bases. A band calculation uses `primitive_lattice` and
  `primitive_positions`, or the `*_orig_cell` functions to stay in the input
  frame.
- seekpath implements HPKOT labels. The Setyawan-Curtarolo labels used by
  AFLOW and the Materials Project differ for many lattices, and HPKOT was
  designed because the Setyawan-Curtarolo standard primitive cell departs
  from the crystallographic conventional cell
  ([1602.06402 introduction](../papers/1602.06402.md#relation-to-setyawan-curtarolo)).
  A label from seekpath and one from an AFLOW page name points of different
  conventions.
- Optional segments: HPKOT adds M-X1 for cP1, X-W2 for cF1 and K-H2 for
  hP1; `path.txt` for those types already holds the segment, and the
  `*2` types (cP2, cF2, hP2) omit it.
- `point_coords` can hold labels that `path` does not visit (W_2 for cF2,
  X_1 for cP2, H_2 for hP2).
- A layered or two-dimensional system enters as a 3D cell with a vacuum
  axis; the path then includes the out-of-plane points (A, L, H for hP), so
  an in-plane path is a sub-selection the caller makes.
- A finite cluster has no space group. A cubic box larger than twice the
  cluster's radius makes the box group's zero-translation operations the
  cluster's point group about the origin, intersected with the box's m-3m;
  a planar cluster also gains the mirror z -> -z.
- `BZ` uses reciprocal vectors |i|, |j|, |k| <= 3 only. A strongly skewed
  reciprocal basis can need more neighbors for the Voronoi cell; pass a
  reduced basis (`reciprocal_primitive_lattice` of a standardized cell).
- spglib 2.8 warns `DeprecationWarning` on every call through seekpath
  2.2.2 until seekpath sets spglib's new error handling.
- HPKOT Table 95 (arXiv v4) lists point group 4/m at space groups 81-82; 4/m
  is 83-88 (81-82 are P-4 and I-4). The code takes inversion from spglib's
  point-group index (`pointgroup_has_inversion`), not from that table, and is
  unaffected.

## LICENSE

MIT (`LICENSE.txt` of the archive, 1,474 bytes, SHA-256
`4f7b45f47ca69c4fce34f7229e94b808e37f4c3ff586a506b471c2d28bcb66ea`).
spglib is BSD-3-Clause. Users of seekpath are asked to cite HPKOT and the
spglib paper.
