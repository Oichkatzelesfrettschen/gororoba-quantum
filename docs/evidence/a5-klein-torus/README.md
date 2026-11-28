# The Klein sign group of N- is the 2-torsion of a rank-2 torus of the stabilizer

The Klein four-group of diagonal sign changes that fixes the N- base point (cd-tower report, section 3.1) is the
2-torsion T'_K[2] of a rank-2 algebraic torus T'_K inside the stabilizer of that point in
H = G_2(C) x SO(2, C) x C^*. [`scripts/a5_klein_torus.py`](../../../scripts/a5_klein_torus.py) decides every step
exactly over Q (SymPy Rational matrices) in 0.5 s, with no random draw. Ledger row A5-254.

## Setup

The 16 tangent generators of H are `strata_regularity.h_generators`
([strata record](../a5-strata-regularity/README.md)), applied to the standard basis of the split coordinates z' in
C^15 to give 15 x 15 matrices: 14 split-octonion derivations acting on u' and v' alike, the scaling and the boost.
The base point p is `strata_regularity.REPS["Nm"]` (support {1, 3, 9, 11}). The Klein matrices are
z'_k -> epsilon chi_s(k) z'_k with chi_s(k) = (-1)^popcount(s AND k) and (s, epsilon) = (1, -1), (4, 1), (5, -1). The
substitution z_k = i^popcount(k) z'_k is diagonal, so they are the same maps in original coordinates.

## Statements, each checked by `--check`

1. The stabilizer algebra s = {X in span(A_k) : X p = 0} has dimension 10, and 9 without the boost. Each Klein matrix
   fixes p.
2. The centralizer c of the three Klein matrices in s has dimension 3 and is abelian. Its boost-free part c' has
   dimension 2.
3. c and c' act diagonalizably on C^15 with integer weights: the joint eigenspaces of a basis span C^15. The Jordan
   decomposition of every element therefore has zero nilpotent part, and exp(c) = T_K and exp(c') = T'_K are tori of
   ranks 3 and 2. The boost-free weights are (0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (2, 1) and (2, 2), with
   multiplicities 2, 2, 2, 3, 2, 2 and 2. The weight lattice is Z^2 (Z^3 for c).
4. With the dual cocharacter lattice N, T[2] = exp(pi i N) acts by (-1)^(w . lambda) on the weight spaces. The four
   matrices of T'_K[2] equal {1, K_1, K_2, K_3}. The eight matrices of T_K[2] contain the Klein group.
5. At one integer point of the boost-free stabilizer, the generalized zero space of ad has dimension 2 (3 for the
   full stabilizer). This bounds the rank from above, so T'_K and T_K are maximal tori.

The earlier floating-point check (cd-tower report, section 3.2) compared the Klein matrices with a Cartan subalgebra
of a random element. That Cartan is not the centralizer torus, so the commutators it read (1.0 to 1.4) measure the
choice of torus; statement 4 shows that a torus containing the Klein group exists.

## Controls (`--self-test`)

- The character s = 2 in place of s = 1 does not fix p.
- With the scaling generator removed, the boost-free torus has rank 1. Its 2-torsion misses the Klein elements with
  epsilon = -1.
- The Klein matrices times the reflection mu' -> -mu' differ from T'_K[2]. The rank-3 torus with the boost contains
  them, because its 2-torsion acts on mu' through the weight of the scaling plus the boost.

## Use

The T'_K weights grade the slice variables of every fiber into N- and N+. This is the input of the weight-adapted
slice of A5-258 and of the weight-block split of A5-330.

```sh
"$PYTHON" -B -W error scripts/a5_klein_torus.py --check docs/evidence/a5-klein-torus/result.json
"$PYTHON" -B -W error scripts/a5_klein_torus.py --self-test
```
