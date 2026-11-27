# A_5 and octonion-space null slices: covariance algebras by XOR blocks

The covariance algebra of the octonion-space slices of A_6, A_7 and A_8 is the derivation algebra of the octonions,
G_2, dimension 14, with no boost. The covariance algebra of the A_5 slice is the stabilizer of e_2 in G_2, su(3), dimension 8. Ledger row
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

The record runs in about 3 minutes on the compute workstation at 16 workers, most of it at A_8.

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
3b. **A_8.** On the octonion-space slice of A_8 (space 1..7, time 200; 256 blocks of 2048 equations, 1996 constraint
   rows of rank 14) the result repeats: 14 dimensions, all rotations, no boost, equal to the octonion derivations,
   and 14 for the derivation-type system. The prediction was written before the run (pool row MATH-80).
4. **su(3).** The derivations with D e_2 = 0 span 8 dimensions. Written in the A_5 frame, their span and the A_5
   covariant span have a joint rank of 8, so the A_5 covariance algebra is the stabilizer of e_2 in G_2.

5. **Every n >= 6.** The covariance algebra of the octonion-space slice of A_n is G_2, with no boost, for every
   n >= 6. Proof:
   - **G_2 lies inside.** A derivation D of A_(k-1) with D(1) = 0 commutes with conjugation. Then
     (a, b) -> (Da, Db) is a derivation of A_k under (a, b)(c, d) = (ac - d* b, da + b c*). Both sides of the
     Leibniz rule expand to ((Da) c + a (Dc) - d* (Db) - (Dd)* b, (Dd) a + d (Da) + (Db) c* + b (Dc)*), and the
     extension again commutes with conjugation, so induction from the octonions gives a derivation of A_n. It kills
     every e_m with m = 0 mod 8 (a copy of D(1) = 0), so it kills e_tau, and X = D, Y = -D, w = D solves the system.
     The record's derivation-type count (14 at A_6, A_7 and A_8) agrees.
   - **Nothing else lies inside.** V = span(e_0..e_7, e_(tau ^ 0)..e_(tau ^ 7)) is invariant under L_1..L_7 and
     L_tau, since a ^ V = V and tau ^ V = V. So a solution (X, Y, w) on A_n restricts to (X_VV, Y_VV, w) on V: the
     entries of X L_y and L_y Y at r, c in V use only X and Y entries inside V. The restricted tables do not depend on
     n >= 6. By Step 0 of the [family proof](../a5-null-slice-family-proof/README.md), with H = 2^(n-1),
     tau' = 2^(n-2) + 8, a and j in 0..7:
     - s_n(a, tau ^ j) = s_(n-1)(tau' ^ j, a) (LH) = -s_(n-2)(8 ^ j, a) (HL, a != 0);
     - s_n(tau, j) = -s_(n-1)(tau', j) = s_(n-2)(8, j) (HL twice, j != 0);
     - s_n(tau, tau ^ j) = s_(n-1)(tau' ^ j, tau') = s_(n-2)(8, 8 ^ j) (HH twice).

     In each case the indices of the remaining sign lie below 16 <= 2^(n-2), so LL carries it to level 4. The
     restricted system on V (16 x 16 unknowns X and Y, 28 generators) has covariant dimension 14 with no boost, so
     the covariance algebra on A_n has at most 14 dimensions and no boost, and it contains G_2.
   - The record computes the restricted system once and checks that the restricted tables agree at n = 6 to 12. The
     direct block computations at A_6, A_7 and A_8 corroborate the result. A reviewer proposed this route in the
     red-team round of this record's A_8 extension.

## What is new against the known theorem

A derivation D of the octonions satisfies D L_x - L_x D = L_(D x) (the Leibniz rule). If D extends to a matrix X on
A_n with X L_y - L_y X = L_(D y) for every y of the slice, then X, Y = -X and w = D solve the covariance system.
That extension is the step a citation would have to supply (a reviewer opened Baez, The Octonions, 2002, section 4.1,
for Der(O) = g_2; the extension to A_n was not opened here). The record checks it directly instead. With Y = -X
imposed, the derivation-type system X L_y - L_y X = L_(w y) has covariant dimension 14 at A_6, A_7 and A_8, the
prediction written before each run. So G_2 lies inside the covariance algebra there through matrices of derivation
type. The record's further content is the reverse inclusion: arbitrary X and Y admit no other generator, no rotation
outside G_2 and no boost.

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
