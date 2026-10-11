# Handback: sedenion geometry and Cayley-Dickson twist sources

Final statement of the delegate that wrote 2411.18881.md, 2512.13002.md,
1602.02843.md, 1602.02317.md, and math-9802116.md, imported in substance.
[A] marks the delegate's own derivation or computation, run as scratch
scripts against cd_core.py outside the repository and carried by no gate;
[V] marks a claim the orchestrator re-verified in this tree; [P] marks a
statement of the source.

## Reggiani 2024 (2411.18881): known theorem reproduced

- [A] The 84 pairs of Reggiani's Table 1 generate the repository's 336 corpus
  rows under operand swap and the automorphism (a, b) -> (a, -b): 84 x 4, a
  free action.
- [P] Normalized zero-product pairs form Z(S) = G_2, a 14-manifold;
  normalized zero-divisor elements form ZD(S) = V_2(R^7), an 11-manifold,
  with the sphere in ann(u) as fiber.
- [A] The phrase "finite assessor graph with S^3 fibers" occurs nowhere in
  this tree and fails as a description of Z(S) over ZD(S). It survives only
  as a finite sample: 84 base points, each with 4 orthogonal partner axes
  giving 8 fiber points (a 16-cell). Measured rank L_v = 12 everywhere on
  the corpus.

## Koebisu 2026 v2 (2512.13002): new implementation or measurement

- [P] Theorem 3.7: det L_v = D_1^4 D_2^2; Lemma 3.3 and Corollary 3.8 state
  the membership criterion with all three conjuncts (vanishing scalar parts,
  equal norms, orthogonal imaginary halves).
- [A] The formula gives 256 for both e_0 + e_9 and e_1 + e_9 (D_1 = 2,
  D_2 = 4); exact determinants confirm it on 300 random integer vectors, 100
  vectors with vanishing scalar parts, and both counterexamples. Each
  counterexample violates exactly one conjunct, so the equal-norm-only
  reading belongs to the C1465 interpretation, not to the paper.
- [V] cd_core.py checks det L_v = 256 for both elements and
  L_{e_1+e_9}^2 = -2 I in the gate.

## Bales 2016, periodicity (1602.02843): candidate new result for the degree claims

- [A] The repository's cd_sign is Bales's P3T under n-bit reversal of the
  index (0 mismatches for n = 3 to 6). Theorems 2 to 5 bound which bits of
  x enter a sign (checked through n = 7 as a Theorem 4 consequence in the
  cd_core index) but state no ANF degree.
- [A] Both degree claims of DESIGN_NOTES.md now have induction proofs, the
  delegate's and not the source's: the sign-row degree n - 1 from
  Corollary 4.3 with Proposition 4.2 in three cases plus a two-point
  indicator lemma; the associator degree max(1, bitlen - 2) from
  Proposition 4.5 with Definition 3.2. The sign-row case identities were
  verified for n = 3 to 7, the associator slice structure for dims 16 to
  128, and the census 21, 84, 360, 1488, 6048 at dims 8 to 128. Formal
  checks of the induction and its edge cases are not run; they would turn
  the "conjecture beyond dim 128" into a provable lemma.
- [A] The handoff's Boolean negative control f(u, t) = [u != 0] + t is the
  sign row of the highest doubling generator, also the conjugation sign of
  Proposition 3.5.
- [A] Printed Proposition 4.4(iii) has a typo (x2 x2 y3 for x1 x2 y3);
  Proposition 4.4(iv) matches the recursion under none of four readings
  tried (50 to 100 mismatches of 256), so Corollary 4.3 is the verified
  statement. Proposition 3.7(ii) gives 0, 672, and 10080 violating triples
  at n = 3, 4, 5.

## Bales 2016, alternate product (1602.02317)

- [A] Theorem 5.1 is correct for the printed P2 (0 mismatches below 256).
  The printed P1, P2, P1T, P2T give non-alternative 8-dimensional algebras,
  so they are not octonion-type, against the paper's "eight algebras are
  isomorphic": with the nested-pair P2 and top-bit-last index, x = e_1 + e_4
  and y = e_2 + e_7 give |xy|^2 = 8 against |x|^2 |y|^2 = 4, and
  A(e_1, e_4, e_2) + A(e_4, e_1, e_2) = 2 e_7. P0, P3, P0T, P3T pass. No
  GL(n, 2) relabeling with a diagonal sign gauge maps P2 onto cd_sign for
  n = 3 or 4, so the closed form cannot be transplanted. The fourth worked
  example (e51 e12) misstates 12 as 000110B; with 12 = 001100B the index is
  63 and the sign agrees.

## Albuquerque and Majid 1998 (math/9802116): known theorem reproduced

- [A] F_AM(x, y) = cd_sign(y, x) for n = 2 to 6 (their product is P3, the
  transpose of the repository's P3T) and phi is unchanged, so the
  DESIGN_NOTES.md prior-art sentence holds for the associator.
  W = diag(phi(i, j, .)) is their Definition 2.3 / 7.1 regular-representation
  quasi-associativity.
- [A] The wording "twisted group algebra" is loose: F is a 2-cochain and the
  object is a quasialgebra.

## Not run, venue claims open

Formal verification of the induction proofs; Reggiani's code and Bales's
reference [4]; no publication record was queried (the Albuquerque-Majid
journal reference comes only from Koebisu's reference [11] and
DESIGN_NOTES.md).

## Orchestrator's reading

The degree formula and the Walsh-class census stay candidate results: Bales
states no ANF degree, and the delegate's induction proofs are unverified
derivations that name the exact propositions a formal proof would rest on.
The next mathematical deliverable is that formalization, not another census.
The C1465 statement review in the handoff note stands as written; the
"assessor graph with S^3 fibers" phrase appears in no retained document and
is not reintroduced.
