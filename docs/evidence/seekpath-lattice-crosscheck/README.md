# spglib and SeeK-path cross-check of the repository's three-dimensional point sets

[seekpath_replay.py](seekpath_replay.py) runs under an interpreter that
imports seekpath and scipy and writes
[seekpath_replay.txt](seekpath_replay.txt) (Python 3.14.8, seekpath 2.2.2,
spglib 2.8.0, numpy 2.5.4, scipy 1.18.1; two runs byte-identical). It raises
on any disagreement with the closed forms below or with
[census.json](../cd-star-lattice/census.json). No gate runs it: the gate
images carry neither package, and no repository claim depends on it. The
[seekpath manual](../../notes/quantum-tools/seekpath.md) gives the install
recipe; the source archive is
[seekpath-2.2.2.tar.gz](../../source_archives/seekpath-2.2.2.tar.gz).

The replay feeds spglib and SeeK-path two kinds of input: the integer
lattice a point set spans, as a one-site cell, and the finite set itself,
one site per point in a cubic box of edge 20, whose zero-translation
operations are the set's point group about the origin.

## D14 coordinate projection

The 364 roots +-e_i +-e_j of D14 projected onto three of the fourteen
coordinates give 19 images, exactly the points of Z^3 with |v|^2 <= 2 [T]:
a root keeps 0, 1 or 2 of its nonzero entries, each +-1. The multiplicities
follow by counting the roots supported off the three axes:

| Squared norm | Images | Multiplicity of each | Count |
| --- | --- | --- | --- |
| 0 | origin | 4 C(11, 2) = 220 | 220 |
| 1 | +-e_a | 2 x 11 = 22 | 132 |
| 2 | +-e_a +- e_b | 1 | 12 |

The 12 images of squared norm 2 span D3, the face-centered cubic lattice,
at index 2 in Z^3; the 19 images span Z^3 itself. spglib places the D3
span in Fm-3m (`cF2`) and Z^3 in Pm-3m (`cP2`), and the boxed 19-point set
in Pm-3m with point group m-3m [E]. The set is therefore the first two
coordination shells of the simple cubic lattice: six neighbors at radius 1,
then twelve at sqrt(2). That is the shell order which
[algebra_measurement_synthesis.tex](../../notes/topics/algebra_measurement_synthesis.tex)
section "FCC resemblance and its limit" calls reversed relative to FCC,
whose first shell is the twelve at a/sqrt(2) and second the six at a. The
cuboctahedral shell alone matches the FCC nearest-neighbor shell. The
statement covers coordinate projections; the seeded generic projections of
that document are different point sets.

## Star lattices

| Set | spglib | Point group checked | census.json row | Agreement |
| --- | --- | --- | --- | --- |
| S_3, tetrahedral boundary, 37 points | Pm-3 (200) | m-3 = Th: order 24, 12 of determinant -1, element orders 1, 2^7, 3^8, 6^8, contains -1 | `tetrahedral_3d.boundary_symmetry` | all four fields |
| S_2, Tuna-17, 17 points | P4/m (83) | the z-fixing subgroup C4: order 4, determinants +1, orders 1, 2, 4^2, contains the planar -1 | `cayley_dickson[dimension 2].boundary_symmetry` | all four fields |
| S_3 ball without boundary | Pm-3m (221) | m-3m | none | |

spglib and the census backtracker of
[scripts/cd_star_lattice.py](../../../scripts/cd_star_lattice.py) are
independent implementations: spglib searches integer rotations against the
lattice metric and the site set, the census enumerates signed permutations
that map the boundary onto itself. The boundary lowers the ball's m-3m to
Th. For S_2 the planar embedding adds the mirror z -> -z, so spglib's full
answer is 4/m and the replay compares its z-fixing subgroup. S_n for n >= 4
is out of reach: spglib accepts only 3 x 3 lattices.

## Brillouin zones

`seekpath.brillouinzone.BZ` on the reciprocal basis 2 pi A^-T returns 6
faces for the simple cubic lattice (a cube), 14 for the face-centered cubic
lattice (the truncated octahedron) and 12 for the body-centered cubic
lattice (the rhombic dodecahedron). The zone of a lattice is the
Wigner-Seitz cell of its reciprocal, and FCC and BCC are reciprocal to each
other up to scale, so the Wigner-Seitz cell of FCC is the rhombic
dodecahedron and that of BCC the truncated octahedron.

## Prompt cells and heavy-hex

Section 4 runs verbatim the three cells of a prompt that proposed SeeK-path
for this repository. The conventional FCC copper cell returns Fm-3m, `cF2`
and the HPKOT short path Gamma-X-U | K-Gamma-L-W-X; the one-site cubic cell
returns Pm-3m, `cP2` and Gamma-X-M-Gamma-R-X | R-M; the two-site honeycomb
layer returns P6/mmm, `hP2` and the full three-dimensional path
Gamma-M-K-Gamma-A-L-H-A | L-M | H-K, of which Gamma-M-K-Gamma is the
in-plane part. The five-site heavy-hex layer (honeycomb vertices plus one
site on each edge) returns the same P6/mmm and path. None of those cells is
a repository data set: the FCC and cubic cells are textbook cells, and the
Heron r2 coupling graph is a finite 156-qubit patch of heavy-hex with no
translation symmetry. The prompt's prediction that the D14 projection would
be detected as space group 225 fails on the repository's own data (section
1 of the output: 221).

## Replay

```sh
SEEKPATH_PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/seekpath-venv/bin/python"
"$SEEKPATH_PYTHON" docs/evidence/seekpath-lattice-crosscheck/seekpath_replay.py \
    > docs/evidence/seekpath-lattice-crosscheck/seekpath_replay.txt
```

Tags: [T] written proof argument; [E] exact finite computation.
