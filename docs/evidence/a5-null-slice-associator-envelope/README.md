# The Lorentzian slice of A_5: associator form, isotropic strata, associative envelope and the tower to 4096

`result.json` is the output of
[`scripts/a5_null_slice_associator_envelope.py`](../../../scripts/a5_null_slice_associator_envelope.py) `--out`. The
record extends [the null-slice boost algebra](../a5-null-slice-boost-algebra/README.md) on the same slice of A_5,

    y = x_1 e_1 + x_3 e_3 + x_4 e_4 + x_5 e_5 + x_6 e_6 + x_7 e_7 + t e_26,    r^2 = sum of x_a^2,

with A_a = L_(e_a), J = L_(e_26), the Clifford defect K_a = -(A_a J + J A_a)/2 and T = span(e_2, e_8, e_18, e_24).
Every decision is an identity of integer matrices, a FLINT rank over Z or over F_p, or a count; no random draw
enters. `--check` recomputes the record and compares its bytes, and `--self-test` runs seven controls, each a
property that holds on the record's input and fails on a mutant, in normal and `-O` modes. Sign tables come from a
vectorized form of the `cd_core.cd_sign` loop, and every sign row the record uses is compared with `cd_core`
entry by entry.

## Statements

1. **Associator form** (`associator`). For every pair of distinct imaginary units of dimensions 16, 32 and 64,
   2 K_a = [e_a, e_t, .] + [e_t, e_a, .] with [p, q, z] = (pq)z - p(qz), and at three integer points of each
   dimension L_y^T L_y = N(y) I + [y, y, .]. Both are elementary: the first is the anticommutativity
   e_a e_t = -e_t e_a of distinct imaginary units, and the second is L_y^T = -L_y with y^2 = -N(y) for imaginary y,
   the identity L^2 = -G of Moreno (math/0512517) that `gororoba_quantum/pathion_kernel_map.py` cites. On the slice
   [x, x, .] and [e_26, e_26, .] vanish, so the Gram identity of the earlier record reads Gram = (r^2 + t^2) I plus the
   left associator of y, and K(x) is the mixed associator of x and t e_26 divided by 2t.
2. **Three null strata over F_p** (`strata`). From statement 1, L_y^2 = -(r^2 + t^2) I - 2 t K(x). At p = 32009
   (where -1 is a square) and p = 32003 (where it is not), every point of the grid x in {0, 1, 2}^6, x != 0, gives:
   - nullity 4 on the Lorentzian cone r^2 = t^2, t != 0 (411 and 409 points);
   - nullity 12 on the Euclidean cone r^2 + t^2 = 0, t != 0 (411 and 319 points), where y^2 = 0 and rank L_y^2 = 8;
   - nullity 16 on the null space r^2 = 0, t = 0 (twelve points x = (a, b, c, 0, 0, 0) per prime), where L_y^2 = 0.

   The real slice meets the first stratum only. The bound nullity >= 12 on the Euclidean cone holds over every field
   of characteristic 0 or above 32 by an argument the record does not machine-check: there r^2 = -t^2 != 0, so
   P = K(x)^2 / r^2 is idempotent with trace 8 and rank K(x) = rank P = 8; L_y commutes with L_y^2 = -2 t K(x), so it
   preserves ker K(x), of dimension 24, and squares to zero on it.
   Equality is computed at the two primes only. Over a p-adic field a quadratic form in five or more variables is
   isotropic, so the slice has Euclidean-cone points over every Q_p; that statement is a cited theorem, not a computation
   of the record.
3. **Associative envelope** (`envelope`). The algebra the seven tables A_a and J generate over Q has dimension 256
   (word lengths 1 to 6 give 8, 35, 111, 210, 255, 256), is closed under products and under transposition, and
   contains eta = I - 2 P_T. Its commutant in M_32(Q) has dimension 4, is closed under products and is not
   commutative, and the trace form on its traceless part has signature (2, 1): a noncommutative four-dimensional
   semisimple real algebra is M_2(R) or the quaternions, and the signature excludes the quaternions (signature (0, 3)).
   Closure under transposition makes the envelope semisimple, so by the double-commutant theorem it is the commutant
   of M_2(R), namely M_16(R), and R^32 is two copies of one irreducible 16-dimensional module. The six spatial tables alone have a commutant of dimension 16 (M_8(R) acting four times),
   and the 31 imaginary tables of A_5 together have a commutant of dimension 1.
4. **Seven anticommuting units** (`envelope`). The six A_a and J eta anticommute pairwise and square to -I. Their
   product is not a scalar and squares to I, and the elements anticommuting with all seven form a space of dimension 8.
5. **Two-term strata of A_5** (`two_term_strata`). For e_j + e_tau, 1 <= j < 16 <= tau, j XOR tau != 16, the
   nullities are 0 (15 pairs, the strut s = j XOR tau XOR 16 equal to j), 4 (84 pairs) and 12 (126 pairs); every
   nullity-4 pair has s > 8 (the range `gororoba_quantum/demarrais_structures.py` marks `is_dmz_sparse`). The six
   spatial directions of the slice pair with e_26 at the struts 11, 9, 14, 15, 12 and 13. The record tests counts
   only; Proposition 2.2 of Skiouris, "Aphanics at the pathion level" (2026), states the 4 and 12 strata of these pairs
   and names e_1 + e_26 the canonical representative of the nullity-4 stratum, with Gram spectrum 0, 2, 4 at
   multiplicities 4, 24, 4.
6. **The families to dimension 4096** (`families`). For n = 8 to 12, the slice with time index 7 * 2^(n-3) and
   space {1 .. 2^(n-2) - 1} minus 2^(n-3) has disjoint stars, a common support of size 4, a common kernel of dimension
   4 and nullity 4 at a null point; the so(2^(n-2) - 2, 1) relations hold by direct check at n = 8 (117,242 relations)
   and n = 9 (992,250), and at n = 10, 11, 12 they follow from the disjoint stars by the sufficient direction of the
   star criterion (ledger row A5-617). The octonion-space slice (time 2^(n-1) + 2^(n-2) + 8, space e_1 .. e_7) has a
   Clifford space, disjoint stars, the 147 relations of so(7,1) and a common kernel of dimension 2^n - 32 at every
   n = 8 to 12. Up to 1023 sign rows per level are compared with `cd_core`, with zero disagreements.

## Relation to retained hardware data

The operand e_1 + e_26 is the cone point x = e_1, t = 1 of the slice ([findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)).
The full kernel map on ibm_fez (acquisition `ibm-fez-pathion-kernel-map`, 167 routed CZ) left it unresolved, with
23 of 32 contrast signs. The coset-block map (acquisitions `ibm-fez-pathion-coset-map` and
`ibm-marrakesh-pathion-coset-map`) read N_hat = 4.25 [4.15, 4.35] on ibm_fez and 4.28 [4.19, 4.38] on ibm_marrakesh,
4.02 and 4.05 after readout correction, with 32 of 32 signs. The runs read a nullity count and contrast signs; K_1 is
the symmetric part of the module's signed permutation L_1^T L_26, and the module's aligned pairs are the support of K_1.

## Relation to arXiv 2611.34924

The paper's boost is one generator, K = A/(8 pi G_N), acting by conjugation (equation 5.22) and on area eigenstates by
the phase of equation 4.12a; it names no non-abelian Lorentz algebra. A bracket-preserving map from that algebra to
the defects exists only trivially, which retires ledger row A5-620 as worded.

## Reproduce

    "$PYTHON" -B -W error scripts/a5_null_slice_associator_envelope.py --check docs/evidence/a5-null-slice-associator-envelope/result.json
    "$PYTHON" -B -W error scripts/a5_null_slice_associator_envelope.py --self-test

The check takes about 60 s on a 32-thread pool (gate `core-a5-null-slice-associator-envelope`).

## Open

- The orbits of the strata classification ([a5-strata-regularity](../a5-strata-regularity/README.md)) that contain
  the nullity-12 and nullity-16 points of statement 2; the record does not place them.
- An eighth unit anticommuting with the seven of statement 4 and squaring to -I, which would make the envelope the
  image of Cl(0,8); the space of candidates has dimension 8.
- The nullity on the Euclidean cone over Q(i) and over Q_p, beyond the two primes and the bound of statement 2.
- The so(m,1) relations at n >= 10 by direct check, and the families beyond n = 12.
- A machine-checked form of statements 1, 3 and 6; the two-term kernels of statement 5 are already formal in
  gororoba-math (`rocq/quantum/CdTowerTwoTermNullity.v` and `lean/GororobaMath/CayleyDickson/TwoTermNullity.lean`).
