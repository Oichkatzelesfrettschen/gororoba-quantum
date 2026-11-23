# The map that the slice change induces on the fiber cone of E8-bar -> N+-, over Q(i)

Ledger row A5-583 holds an invertible linear map between the weight-slice and the header-slice quadric ideals of
E8-bar at one prime, found by a torus search, and leaves two items open: the map over Q(i), and whether it is the map
that the change of slice induces. This directory computes the induced map itself over Q(i) and checks its reductions
against every retained header relation file (ledger row A5-598).

## Mechanism

Both slices are nine-dimensional affine slices through one basepoint z_0 of N+ or N- in the fifteen complex
coordinates: the header slice moves nine split coordinates, the weight slice moves nine torus eigenvectors. Each
producer takes its 21 generators among the 126 principal 4-Pfaffians of a Schur form of the skew matrix C(z): the
header in the frame of a principal pivot of C(z_0) (`nullity16_basepoints.py`), the weight slice in a frame of torus
eigenvectors (`weight_slice_fiber_relations.py`).

For a skew matrix over a ring in which the Pfaffian of a 6 x 6 pivot block B is a unit, a congruence over that ring
carries C to the direct sum of B and its Schur form S, so the ideal of 10-Pfaffians of C equals the ideal of
4-Pfaffians of S. Both pivot Pfaffians are units at z_0, so the two families of 126 Pfaffians generate one ideal I of
the local ring of the ambient space at z_0, and the group G_2(C) x C^*, which acts on the kernel bundle (A5-415) and
whose orbit of z_0 is open in N+-, makes the germ of (source closure, I) a product of its restriction to either slice
with the orbit. The restriction maps I / m I -> I_h / m I_h and I / m I -> I_w / m I_w are then isomorphisms, and
their composite is the map of generators that identifies the two fiber cones. It is computed on the weight slice
alone: `induced_slice_map.py` restricts the header frame's 21 selected Pfaffians to the weight slice and solves for
each as a constant combination of the 21 weight-slice generators modulo J + m I.

The computation runs in R = Q(i)[s1..s9, v] / (v u - 1), where u is the product of the two pivot Pfaffians restricted
to the axis of the one weight-zero coordinate s2. The weight pivot Pfaffian is a polynomial in s2 alone
(`weight_pivot_on_axis 1`), so it is a unit of R; the header pivot Pfaffian is a unit of the local ring at the origin
and need not be one in R. Three facts make the constant combination the class in I / m I, with m = (s1, ..., s9):

1. Each header Pfaffian is, by the identity of A5-593 in the header frame, a multiple of a 10-Pfaffian of C(z), and
   the 10-Pfaffians of C(z) lie in the ideal of the weight-slice Pfaffians once the weight pivot is inverted. So every
   header Pfaffian lies in the weight-graded ideal I R, although it is not weight-homogeneous.
2. I is generated in weights up to the largest weight d of a weight-slice Pfaffian, so the components of weight
   above d of an element of I lie in m I. Discarding them, as the truncation of the weight-slice producer does,
   leaves the class modulo J + m I unchanged.
3. I / (J + m I) is killed by all of m, so it is supported at the origin, and its localization there is itself.
   A class that vanishes in the local ring vanishes in R.

## Result

| Basepoint | Header Pfaffians in the span | Map | Weight relations over Q(i) |
|---|---|---|---|
| N- | 21 of 21, residual 0 | 21 x 21 over Q(i), constant entries, invertible | 148, digest of the retained record |
| N+ | 21 of 21, residual 0 | 21 x 21 over Q(i), constant entries, invertible | 148, digest of the retained record |

`induced-CELL.json` holds the matrix G (`map`) of the substitution y(i) -> sum_j G[i][j] y(j) that carries a
weight-slice relation to a header-slice relation, and the 148 weight-slice relations over Q(i). Reduced at a prime
and a root of -1, the transported ideal equals the retained header ideal in both directions:

| Cell | Prime, root | Header relation file | Transported modulo header, header modulo transported | Controls (identity; one entry raised; header generators 1 and 2 swapped) |
|---|---|---|---|---|
| N- | 32009, 10754 | `KH-e8-nm.sing` | 0, 0 | 141, 134; 22, 60; 47, 35 |
| N+ | 32009, 10754 | `KH-e8-np.sing` | 0, 0 | 141, 133; 22, 64; 47, 72 |
| N+ | 32009, 21255 | `KH-e8-np-r21255.sing` | 0, 0 | 141, 134; 22, 60; 47, 35 |
| N- | 32029, 9115 | `a5-e8-d2/e8nm_p2` | 0, 0 | 141, 134; 22, 60; 47, 35 |
| N+ | 32029, 9115 | `a5-e8-d2/e8np_p2` | 0, 0 | 141, 134; 22, 60; 47, 35 |
| N- | 32057, 8059 | `third-prime/relations/e8-nm` | 0, 0 | 141, 134; 22, 60; 47, 35 |

Each check also reads 148 minimal generators, dimension 5, multiplicity 11 and a nonzero determinant, and at the root
10754 the reduced Q(i) weight relations equal the retained modular file `KA-e8-CELL.sing` in both directions. A
polynomial outside I (the first header Pfaffian plus s2) leaves a nonzero residual against the span.

## Consequences and scope

- With L = K on the weight slice over Q(i) (A5-457), the header-slice fiber cone over Q(i) is Q(i)[y] / G(K): the
  header quadric ideal in characteristic 0 is the transported weight-slice ideal, and no standard basis over Q(i) of
  the header slice is computed.
- The header relation files of five of the six cells were computed by engines that never saw this map, at three
  primes, so the agreement tests the Pfaffian-ideal lemma, the product structure and the frame conventions together.
- The map of A5-583 is another equivalence of the same two ideals at (32009, 10754); the symmetry group of the ideal
  has dimension 34, so the two maps need not be equal, and this directory does not compare them.
- The six reductions compare ideals, and the symmetry group of the ideal has dimension 34, so they cannot by
  themselves single out the induced map among the equivalences. That G is the induced map rests on the three facts
  above and the product structure, which are prose; a kernel-checked form is a target for gororoba-math.
- E8-bar only. The same script applies to W8, Iso and X with their header selections; those cells are not run.

## Replay

    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map/run_induced.sh

from the repository root, with Singular on PATH and sympy and python-flint in that interpreter. The driver exits
nonzero unless both records pass their internal checks and all six reductions print `INDUCED VERDICT ... PASS`. The
retained run used Singular 4.4.1, Python 3.14.4, sympy 1.14.0 and python-flint 0.9.0 on an aarch64 Linux host: 2 min
48 s in all, 5 s for each map and 71 s for each relation script. The run copied the tree of commit `05f99ece3`
without git metadata with the scripts of this directory added.

| File | Content |
|---|---|
| `induced_slice_map.py` | script generator (`--emit`), record builder (`--collect`) and reduction check (`--check`) |
| `run_induced.sh` | both basepoints and the six reduction checks |
| `map-CELL-qi.sing`, `.log` | the induced map over Q(i) |
| `relations-CELL-qi.sing`, `.log` | the weight-slice producer's script for the cell and its 148 relations |
| `induced-CELL.json` | the record: map, relations, selections, digests, verdict |
| `check-CELL-pPRIME-rROOT.sing`, `.log` | one reduction check |
| `sha256.txt` | sha256 of every other file of this directory |
