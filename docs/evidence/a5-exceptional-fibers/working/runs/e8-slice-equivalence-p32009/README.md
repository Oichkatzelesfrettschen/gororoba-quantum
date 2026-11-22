# A linear map between the weight-slice and header-slice quadric ideals of E8-bar -> N+-

Ledger row A5-583 asks whether an invertible linear map of the 21 generators y(1..21) carries the weight-slice quadric
ideal K of E8-bar onto the header-slice quadric ideal K2, which A5-582 measures as another ideal in the retained
coordinates. This directory constructs such a map at both basepoints modulo 32009 (root of -1 = 10754) and verifies it
in Singular 4.4.1. The row is certified.

## Result

| Cell | Weight-slice file | Header-slice file | f(K) modulo K2 | K2 modulo f(K) | Identity control | Perturbed-entry control |
|---|---|---|---|---|---|---|
| E8-bar -> N- | `KA-e8-nm.sing` (`5b161d88...`) | `KH-e8-nm.sing` (`22b66f62...`) | 0 | 0 | 141 and 134 nonzero | 22 and 128 nonzero |
| E8-bar -> N+ | `KA-e8-np.sing` (`6beae5ed...`) | `KH-e8-np.sing` (`ed8d5790...`) | 0 | 0 | 141 and 133 nonzero | 22 and 132 nonzero |

- The four ideal files are those of [../e8-rees-fibers-v2-kcompare-p32009](../e8-rees-fibers-v2-kcompare-p32009/README.md):
  `KA` holds the 148 relations of the weight-slice producer and `KH` the 148 relations of the header-slice receipt.
- `bridge-CELL.json` holds the matrix G (`map`, 21 rows) of the substitution y(i) -> sum_j G[i][j] y(j). Applied to
  the weight-slice quadrics it gives an ideal f(K) with 148 minimal generators, dimension 5 and multiplicity 11, and
  each of f(K) and K2 reduces to zero modulo a standard basis of the other (`BRIDGE VERIFY`). G has nonzero
  determinant (`BRIDGE DET`).
- Known-bad controls, which must come out unequal before the verdict counts: the identity substitution leaves 141 of
  the weight-slice relations outside K2 and 134 (N-) or 133 (N+) of the header relations outside K, the numbers of
  A5-582; G with its first entry raised by one leaves 22 and 128 or 132 nonzero remainders.

## Method

A linear map g with g(K) = K2 conjugates the group of linear symmetries of K onto that of K2. Composed with a symmetry
of K2 it carries a chosen maximal torus of the first group onto a chosen maximal torus of the second, and in joint
eigen-coordinates of the two tori such a map is a permutation matrix times a diagonal matrix. `slice_bridge.py`
computes, for each quadric space over F_32009 with python-flint:

1. the Lie algebra of matrices A whose derivation y_i -> sum_j A_ij y_j preserves the space (dimension 34 on both
   sides, the number of A5-347 and A5-424);
2. the centralizer of an element of that algebra (dimension 6 on both sides), retried on further elements until all 21
   eigenvalues of a general element of the centralizer lie in F_32009 (1 to 6 attempts; an element whose torus is a
   non-split form of the sl2 factor shows 5 eigenvalues there);
3. joint eigen-coordinates, in which the 21 weights are pairwise distinct, the 231 quadratic monomials fall into 148
   weight classes and the ranks of the quadric space on the classes sum to 148, so the space is the direct sum of its
   weight components (the statement of A5-426 for the weight slice, here on both sides);
4. the permutations of the 21 eigen-coordinates that carry the weight partition of the monomials of one side onto that
   of the other with equal ranks: exactly 2 at each cell;
5. for a permutation, the diagonal entries from the reduced echelon bases of the classes of partial rank: each nonzero
   non-pivot entry gives one multiplicative equation, solved as a linear system modulo 32008 through discrete
   logarithms to the primitive root 3 and a Hermite normal form over Z.

The first permutation solves at both cells. The script accepts a map only when the transported quadric space and the
header space have a joint rank of 148; `bridge_verify.py` then writes the Singular check of the table.

The elements of steps 2 and 3 are read from a sha256 stream of fixed labels. They select a torus and enter no verdict:
the map is checked by a rank and by the mutual reduction.

## Scope

- One prime and one root, (32009, 10754), the cells of the retained header relation files. The header-slice quadrics
  over Q(i) are not retained, so the map over Q(i) is not computed.
- The map is a linear equivalence of the two quadric ideals. This directory does not show that it is the map that the
  transverse-slice isomorphism of A5-423 induces on I / m I; the symmetry group of K2 has dimension 34, so the
  equivalence is far from unique.
- With L = K on the weight slice (A5-572, A5-573) and L = K2 on the header slice (A5-559), the two fiber cones of
  each basepoint are isomorphic graded rings at this prime: dimension, multiplicity, Hilbert series, associated
  primes and nilradical structure pass from one presentation to the other.

## Replay

    PYTHON=/path/to/python sh docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/run_bridge.sh

from the repository root, with python-flint and numpy in that interpreter and Singular on PATH. The retained run used
Python 3.14.4, python-flint 0.9.0, numpy 2.5.5 and Singular 4.4.1 on an aarch64 Linux host: 29 s (N-) and 88 s (N+)
for `slice_bridge.py` at 0.36 GB, under 1 s per Singular check. The run copied this tree without git metadata from
commit `78c5e5c3a` with the scripts of this directory added.

| File | Content |
|---|---|
| `slice_bridge.py` | the torus frames, the matching and the scalar system; writes `bridge-CELL.json` |
| `bridge_verify.py` | writes `bridge-verify-CELL.sing` from a record |
| `run_bridge.sh` | both cells: script digests, the Python run with its timing file, the Singular check |
| `bridge-CELL.json`, `.log`, `.time` | the record (map, permutation, exponents, frame numbers), the verdict line and the timing |
| `bridge-verify-CELL.sing`, `.log` | the Singular check and its output |
| `sha256.txt` | sha256 of every other file of this directory |
