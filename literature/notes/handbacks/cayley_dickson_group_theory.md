# Handback: Cayley-Dickson group theory sources

Final statement of the delegate that wrote 1207.4230.md, 0905.2987.md,
math-0511691.md, math-0702075.md, and math-0512517.md, imported verbatim in
substance. [A] marks the delegate's own derivation or computation, run as a
scratch script outside the repository and carried by no gate; [V] marks a
claim the orchestrator re-verified in this tree; [P] marks a statement of the
source. Every claim below is also in the per-source note with its theorem
number.

## Kirshtein 2012 (1207.4230): known theorem reproduced

- [P] Theorem 35 (the normal subgroup N in step 1 of its proof), Theorem 34,
  and Lemma 10 give G_n = Mlt_l(Q_n), C_n = Inn_l(Q_n), and
  H_n = N = Inn_l x Z(Q_n) = C_n x Z_2. Equation (5), L_{x,y}(z) = [y, x, z] z,
  is the associator-sign identity [omega_{a,b} = -1] = P(s_{a,b}) in
  basis-sign coordinates. Theorem 9 is the Schreier generation.
- [A] Convention map: cd_sign equals the four loop rules branch for branch
  (checked for dimensions 1 to 128); e_m is the loop element with the bits
  of m as exponents, the top bit is e = i_n, L_{-1} = -I; Kirshtein's
  L_{x,y} differs from the repository's s_{a,b} by the scalar sign psi(a, b).
- [A] The repository's coordinate description of H_n is Kirshtein's page 20
  generators rewritten: known theorem reproduced. The repository's proof,
  with its parity lemma, is a new proof or formalization.
- [A] Kirshtein's printed upper bound at the end of the Theorem 34 proof
  leaves a factor 2 open (a constant c_f that varies with the pair; his own
  element h has a trivial lower half and a nontrivial upper half). The
  repository's Lemma 2 (even-weight lower half) closes it. The statement
  itself holds for n = 3 to 11.
- [A] Theorems 34 and 35 fail at n = 2 as printed (Theorem 34 carries no
  restriction on n; Theorem 35 says n >= 2): Q_2 = H_8 has order 8 and
  Inn_l = 1 while the formulas give 2 and 16. This matches the repository's
  n = 2 exception. No published erratum was compared.
- [A] ANF degree <= n - 2 and the RM(n-2, n-1) plus top-coordinate form are
  near-corollaries of Kirshtein's generators and are labeled candidate new
  result pending a literature search for that exact statement.

## Biss, Christensen, Dugger, Isaksen 2009 (0905.2987): known theorem reproduced

- [P] Theorem 7.2, Corollary 7.3, and Proposition 7.4: the operator is
  M_a = L_{a*} L_a / |a|^2 with eigenvalues {0 (x4), 1 (x8), 2 (x4)} at every
  sedenion zero divisor, with explicit eigenspaces.
- [A] The repository's B = (L_{e_i} + t L_{e_j}) / 2 gives
  B^T B = (|a|^2 / 4) M_a = M_a / 2, hence {0, 1/2, 1}. The theorem covers
  every sedenion zero divisor, not only the 84 corpus elements; all 84 were
  confirmed numerically with cd_sign matrices.
- [A] The Design D fringe (1 - s cos phi) / 2 is the weight on the
  eigenvalue-2 space: new proof or formalization. Any basis input gives
  exactly 1/2.

## Biss, Dugger, Isaksen 2005 (math/0511691): known theorem reproduced

- [P] The annihilator bound 2^n - 4n + 4 is Proposition 9.10; every multiple
  of 4 occurs by Theorem 13.2 (collected as Theorem 1.2); the maximal
  stratum is Theorem 15.7 (Theorem 1.3): 2^(n-4) copies of V_2(R^7) for
  n >= 4, homeomorphic.
- [A] The corrected zero-divisor predicate of the handoff note is
  Lemma 9.4 + Lemma 9.5 + Proposition 12.1. The 4-dimensional annihilator
  holds for every sedenion zero divisor (Corollary 11.2). An index-form
  predictor of the four partners with signs from cd_sign(8, ., .) was
  verified on all 336 element-partner pairs.
- [P] A_5 annihilator dimensions are {0, 4, 8, 12, 16}. Settled: ZD_16 is two
  copies of V_2(R^7). Partial: Theorem 14.6, for pairs whose annihilators
  meet. Open: ZD_12, ZD_8, ZD_4 as spaces ("unknown even in A_5"), and Alt
  dimensions 20 and 28.
- [A] The repository holds no nullity table for A_5; the note supplies the
  paper-based list, fixtures with nullities 16, 12, 8, and 4, and a census
  of two-term elements (nullity 0: 342, 4: 168, 8: 168, 12: 252, 16: none).
- [A] Proposition 15.6's statement has i_n where its proof uses i_{n-1}.
- [A] Lemma 9.2 and Corollary 9.3 (left and right annihilators coincide) are
  a route to the survey's open ker L_x = ker R_x item.

## Biss, Christensen, Dugger, Isaksen 2007 (math/0702075): known theorem reproduced

- [P] Theorems 1.3, 1.5, and 7.5. Nullities inside H_5^perp follow from the
  D-locus table: both components zero divisors gives 8 outside the D-locus
  and 12 inside; exactly one gives 4 and 8; neither gives 0 and 4. {a, 0} and
  {0, a} give 12 or 16.
- [A] Theorem 7.5 fixes |a| = |b| = 1, so the length-ratio parameter of the
  ZD_12 piece is undescribed: candidate new result, the delegate's reading.
- [A] Moreno's unequal-norm example lies outside H_5^perp (nullity 4
  measured).
- [A] The text extraction garbled the stability threshold: Theorems 1.7 and
  8.12 read n >= c/4 + 4 on the page images (pages 4 and 21).

## Moreno 2005 (math/0512517): known theorem reproduced

- [A] Moreno's worked example (e1, e2)(-e4, e7) = 0 is the Design B pair
  (e1 + e10)(e4 - e15); checked numerically against cd_sign (zero product,
  L^2 eigenvalues -4 and -2).
- [P] Spec((e1, e2)) = {0, 1, 2} is the M_a spectrum, though the text uses
  both a lambda and a lambda^2 labeling. L_v^2 = -2 I for e1 + e9 follows
  from Theorem 2.3 (a = b = e1: A = -2 I, S = 0 by flexibility).
- [P] Theorem 4.4 has lambda as a singular-value ratio: lambda = 1 and
  sqrt(2) give nullity 4, lambda = 2 gives nullity 0.
- [A] Stiefel measurement (new implementation or measurement): random pure
  orthogonal equal-norm pairs (Moreno's Stiefel elements) in A_5 gave
  nullity 4 in 200 of 200 samples; in A_6, 100 of 100 had nullity 0
  (floating-point SVD, smallest singular value about 9e-5). That is a
  negative answer to Moreno's open question at A_6 (page 26) if it survives
  exact arithmetic; the note's action item 5 asks for the exact rerun before
  anyone relies on it.

## Orchestrator's reading

The sign-rank theorem of this repository is Kirshtein's group-level result
in Boolean coordinates and is labeled so in DESIGN_NOTES.md and the sign-rank
note; the parity-lemma proof and the Rocq formalization plan remain the
repository's contribution, and the factor-2 gap in Kirshtein's printed bound
is worth a line in the formalization handoff. The sedenion spectrum is a
rescaling of BCDI 2009 and is labeled so. Two finite computations the
delegate made deserve a gate before they are cited: the A_5 two-term nullity
census and the A_6 Stiefel nullity (exact arithmetic).
