# Non-associating basis triples along the Cayley-Dickson ladder

[scripts/cd_associator_defect_census.py](../../../scripts/cd_associator_defect_census.py)
counts ordered triples (a, b, c) of basis indices of the algebra of
dimension D = 2^n whose two bracketings differ, using
omega(a, b, c) = s(a, b) s(a^b, c) s(b, c) s(a, b^c) from `cd_core.cd_sign`,
the value of `predict.associator_phase(D, a, b)[c]`. The retained run is
[census.json](../../evidence/cd_associator_defect_census/census.json); the CI
gate repeats the exhaustive checks through D = 128, pairs through 64,
subspaces through 32 and the lifting certificate for lower dimension up to
32, and the full-tier gate replays the retained run. Tags: [P] source
statement, [E] finite evidence, [T] proved below, [I] interpretation.

## Results

| Statement | Status |
|---|---|
| Every linearly dependent triple associates | [T] Kirshtein Lemma 3 ([1207.4230](../1207.4230.md)): it generates a subloop of order at most 8 |
| Non-associating ordered triples: N(D) = (D-2)(D-4)(D+6)/2 = (D^3 - 28D + 48)/2; fraction (D+6)/(2(D-1)) among independent triples, 1/2 - 14/D^2 + 24/D^3 among all D^3 | [T] Theorem 1; [E] exhaustive 8 to 512, sampled to 4096 |
| An independent pair has 0 associating completions when D/2 lies in span{a, b}, and D/2 - 4 otherwise; 3(D-2) and (D-2)(D-4) pairs of each kind | [T] Theorem 2 (D >= 16 for the "exactly when" reading; at D = 8 both counts are 0); [E] 16 to 256 |
| Each 3-dimensional index plane W carries a linear functional l_W with omega(a, b, c) = -(-1)^l_W(a xor c) on its ordered bases; 168 non-associating triples when l_W = 0 and 72 otherwise; O(D) = (D-2)(D-4)(D+48)/1344 and Q(D) = (D-2)(D-4)(D-8)/192 planes of each type | [T] Theorem 3; [E] the 168/72 counts on every plane through 128; counts agree with [Wilmot](../papers/2505.11747.md) Table 5 (prior tabulation) |
| omega(1, 6, k) = (-1)^popcount((D-2) & k) | [T] Theorem 4 |
| The pair (D/2+1, D/4+3): omega = -(-1)^(q.k + [k in E_D]) with q = D - 4 and E_D = {0, 2, 3, D/4+2} + {0, D/2}; algebraic degree n - 2; Walsh support 5D/16, largest normalized amplitude 1 - 16/D and nonlinearity 8 | [E] eight-point formula and degree 16 to 4096, support, amplitude and nonlinearity laws 32 to 4096 (at D = 16 support 4, amplitude 1/2, nonlinearity 4); no proof yet |
| With indices 0 to 23 as one block: ordered complement pairs landing in the block 24D - 704 (23D - 680 off-diagonal), block pairs landing in the complement 128 | [T] i >= 24 meets k < 8 inside the complement always and k in [8, 24) only for i >= 32 |

## Proofs

Write D = 2d, a full index as x + u d with x < d and top bit u, and
kappa(x, y) = [x != 0] + [y != 0] + [x xor y != 0] mod 2, which is 1 exactly
when x, y are distinct and nonzero.

**Lemma 1 (commutation).** s_d(y, x) = s_d(x, y) (-1)^kappa(x, y): distinct
nonzero basis units anticommute and every other pair commutes
([left_mult_sign_rank.md](../left_mult_sign_rank.md), Lemma 1; Kirshtein
Lemma 3, item 1).

**Lemma 2 (sign lifting).** s_2d(a + u d, b + v d) = s_d(a, b)
(-1)^(v kappa(a, b) + u [b != 0] + u v). The four cases of the doubling
(x, y)(z, w) = (xz - conj(w) y, wx + y conj(z)) on basis pairs give
s_d(a, b), s_d(b, a), -s_d(a, b) for b != 0 and s_d(b, a) (b != 0) or -1
(b = 0); Lemma 1 rewrites s_d(b, a). The gate checks the identity
exhaustively for d <= 32.

**Lemma 3 (associator lifting).** Substituting Lemma 2 into the four factors
of omega cancels every product of top bits and leaves
omega_2d = omega_d(a, b, c) (-1)^(A u + B v + C w) with
A = kappa(b, c), B = kappa(a, b) + kappa(a, b xor c),
C = kappa(a xor b, c) + kappa(b, c) + kappa(a, b xor c). Each kappa depends
only on which of a, b, c, a xor b, b xor c, a xor b xor c vanish, that is on
the set of F_2 relations among a, b, c, so (A, B, C) is a function on the 16
possible relation sets:

| Lower triple | (A, B, C) |
|---|---|
| rank at most 1 | (0, 0, 0) |
| exactly one relation m_a a + m_b b + m_c c = 0 | (m_a, m_b, m_c) |
| independent | (1, 0, 1) |

The table is independent of d; the gate enumerates all 16 classes and checks
the lifted associators for d <= 32.

**Theorem 1 (total count).** Summing Lemma 3 over the eight top-bit choices
annihilates every lower triple with nonzero (A, B, C), so
sum over all D^3 ordered triples of omega_D = 8 sum over rank-at-most-1 lower
triples of omega_d = 8 (1 + 7(d - 1)) = 28D - 48, since a rank-at-most-1
triple lies in span{1, e_x}, which is associative. With dependent triples
associating, N(D) = (D^3 - (28D - 48))/2 counts the independent
non-associating triples.

**Theorem 2 (pair law).** Fix independent p = a + u d, q = b + v d. If
d in span{p, q}, every independent completion projects to a lower triple of
rank 2 whose single relation pairs with (u, v, w) to 1, so
omega = omega_d (-1) = -1: none associates. Otherwise a, b are independent.
For c in span{a, b} exactly one lift w makes the triple independent and it
fails to associate (4 completions). For each of the d - 4 lower indices c
outside span{a, b}, (A, B, C) = (1, 0, 1) gives the two lifts opposite signs,
so exactly one associates: d - 4 = D/2 - 4 associating completions among
D - 4.

**Theorem 3 (plane functional and type counts).** For D = 8 every plane is
the whole imaginary octonion index space and all 168 ordered bases fail to
associate (l = 0). A plane containing d projects onto a lower 2-plane, so
every ordered basis projects to a rank-2 lower triple, which associates,
and its single relation pairs with the top bits to 1 because the full
triple is independent: omega = -1 for all 168 bases and l = 0. A plane
avoiding d is the graph of a linear f over a lower plane V, and Lemma 3 with
(1, 0, 1) gives l_W = l_V + f. A zero functional gives 168 defects; a
nonzero one has three nonzero kernel vectors, each the value of a xor c for
24 ordered bases, giving 72. Planes containing d number
G2(d) = (d-1)(d-2)/6, and each of the G3(d) = (d-1)(d-2)(d-4)/168 lower
planes has eight graph lifts, one with l = 0, so O(D) = G2(d) + G3(d) and
Q(D) = 7 G3(d), and 168 O + 72 Q = N.

**Theorem 4 (fixed-pair parity).** For distinct nonzero lower a, b no
relation among a, b, c has zero c-coefficient except relations excluded by
a != 0, b != 0, a != b, so C = 1 for every c and
omega_2d(a, b, c + w d) = (-1)^w omega_d(a, b, c). The D = 8 signs of (1, 6)
are the parity character with mask 6, and each doubling adds the new top bit
to the mask, giving mask D - 2.

## Relation to known results

- [P] Wilmot ([2505.11747v3](../papers/2505.11747.md), Table 5 and Theorem 8)
  tabulates the octonion subalgebra counts 1, 8, 50, 310, 2046, 14478,
  107950, 831470 and the quasi-octonion totals 7, 105, 1085, 9765, 82677,
  680085, 5516245 along the ladder, with a recurrence argued by induction.
  O(D) and Q(D) above reproduce every listed value, and the H row is
  (D-1)(D-2)/6, the count of 2-dimensional index subspaces. Wilmot also
  splits the 72 type into P_4, P_12 and P_14, so the 168/72 defect count is a
  coarse signature of a finer classification.
- [T] Theorem 3 derives Wilmot's Theorem 8, which its source argues from the
  observed table pattern by induction. The lower planes number
  G3(d) = O(d) + Q(d), since each has one of the two types, and each carries
  seven graph lifts with a nonzero functional, so
  Q(D) = 7 (O(d) + Q(d)), Wilmot's S_{m+1} = 7 (O_m + S_m). The same count
  gives the companion recurrence O(D) = H(d) + O(d) + Q(d): the planes
  through d project onto the H(d) lower 2-planes and each lower plane has one
  lift with zero functional. Table 5's O row satisfies it
  (8 = 7 + 1 + 0, 50 = 35 + 8 + 7, 310 = 155 + 50 + 105).
- [P] Kirshtein Lemma 3 gives sufficient conditions for each associator
  value; Theorem 3 supplies what the lemma leaves open for order-16
  subloops other than O_16.
- [I] The lifting identity, the plane functional and the pair-law proof
  arrived as derivations in external reviews of this repository; each step
  above is checked against `cd_core` here, and no literature priority is
  claimed. A Rocq formalization of Lemmas 2 and 3 and Theorems 1 to 4 is
  open.
- [I] omega is the coboundary of the sign cochain s on (Z_2)^n, so its
  cocycle identity holds by construction and defines no nontrivial
  cohomology class ([Albuquerque-Majid](../math-9802116.md)). Split doublings
  change s by a symmetric bilinear form, whose coboundary vanishes, so split
  algebras carry the same omega with a different quadratic form
  ([packages/splitoct.md](../packages/splitoct.md)).
- [I] For the cross-scale pair the dominant Walsh outcome carries probability
  (1 - 16/D)^2 and the remaining mass 32/D - 256/D^2 (0.0078 at D = 4096):
  growing support and degree coexist with a function eight truth-table
  entries from affine, so larger D is not by itself a harder or more
  informative sampling experiment.
- [I] The index block of the last result row is a coordinate convention, not
  a physical sector
  ([open_gororoba_handoff.md](open_gororoba_handoff.md#vacuum-model-code-checks)).
