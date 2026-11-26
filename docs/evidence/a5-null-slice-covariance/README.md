# A_5 and A_6 null slices: covariance algebras by XOR blocks

The covariance algebra of the octonion-space slices of A_6 and A_7 is the derivation algebra of the octonions, G_2,
dimension 14, with no boost. The covariance algebra of the A_5 slice is the stabilizer of e_2 in G_2, su(3), dimension 8. Ledger row
A5-619 records both.
[`scripts/a5_null_slice_covariance_blocks.py`](../../../scripts/a5_null_slice_covariance_blocks.py) computes them
exactly over Q.

## Method

The covariance system asks for matrices X, Y and a generator w of so(m,1), acting on the frame (space..., tau), with
X L_y + L_y Y = L_(w y) for every y in the frame's span. The equation at (a, r, c) involves X[r, a ^ c] and
Y[a ^ r, c], because L_a e_c = s(a, c) e_(a ^ c), and both unknowns carry the XOR e = r ^ c ^ a.

So the dense system splits into blocks:
- **Size.** The dense system is 32768 x 8220 at A_6 (about 2.2 GB as a dense matrix over F_p). It splits into 64 blocks, one per e. Each block has 512 equations, 128 X and Y unknowns, and the 28 generator coefficients.
- **Constraints.** Each block's left kernel gives linear constraints on the generators. The covariant generators are their common solutions.
- **Subsystems.** The constraints do not depend on which generators are admitted, so the rotation and boost subsystems take column subsets of one constraint matrix.

The record runs in about 2 s on the compute workstation.

## Statements, each checked by `--check`

1. **Calibration.** On the A_5 slice (space 1, 3, 4, 5, 6, 7; time 26) the method gives 8, 8 and 0 covariant
   dimensions for all generators, rotations and boosts. These are the values the dense 7168-row system of the
   [boost-algebra record](../a5-null-slice-boost-algebra/README.md) records (A5-615): 344 constraint rows of rank 13
   on 21 generators.
2. **A_6.** On the octonion-space slice of A_6 (space 1..7, time 56) the covariant generators span 14 dimensions, all
   rotations, no boost: 652 constraint rows of rank 14 on 28 generators.
3. **G_2.** The octonion derivations, the solutions of D(e_i e_j) = D(e_i) e_j + e_i D(e_j) in so(7) under the cd_core
   signs, span 14 dimensions. Their span and the A_6 covariant span have a joint rank of 14, so the two spaces are equal.
3a. **A_7.** On the octonion-space slice of A_7 (space 1..7, time 104; 128 blocks of 1024 equations) the covariant
   generators again span 14 dimensions, all rotations, no boost, equal to the octonion derivations. A reviewer
   proposed this extension as a conjecture, and the prediction of 14 was written before the run.
4. **su(3).** The derivations with D e_2 = 0 span 8 dimensions. Written in the A_5 frame, their span and the A_5
   covariant span have a joint rank of 8, so the A_5 covariance algebra is the stabilizer of e_2 in G_2.

## What is new against the known theorem

Every derivation D of the octonions satisfies D L_x - L_x D = L_(D x) (the Leibniz rule). So X = D, Y = -D, w = D
solves the covariance system, and G_2 = Der(O) (Cartan) lies inside the covariance algebra of any slice whose space
is e_1..e_7. The record's content is the reverse inclusion. Arbitrary X and Y, with X not tied to -Y, admit no further
generator: no rotation outside G_2 and no boost.

## Prediction

Ledger row A5-619 predicted 14, all derivations of G_2, and no boost. The program note listed the su(3)
identification as a next computation. Both held at the first run.

## Controls

`--self-test` runs three paired controls:

| Control | Baseline | Mutant |
|---|---|---|
| block signs | A_5 rotations give 8 | one negated sign s(1, 2) does not |
| Leibniz system | 14 derivations | one negated structure constant does not give 14 |
| stabilized unit | the e_2 stabilizer matches the A_5 space | the e_3 stabilizer does not |

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_null_slice_covariance_blocks.py --check docs/evidence/a5-null-slice-covariance/result.json
"$PYTHON" -B -W error scripts/a5_null_slice_covariance_blocks.py --self-test
```

Gates `core-a5-null-slice-covariance` and `core-a5-null-slice-covariance-self-test` run both.
