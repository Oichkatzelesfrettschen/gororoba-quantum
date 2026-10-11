# Handback: Boolean functions and hidden-shift sources

Final statement of the delegate that wrote 0811.3208.md, 0911.4724.md,
1103.3017.md, quant-ph-0703195.md, 1107.2189.md, 2202.08688.md,
elkies-2013-m256.md, and pmc-4957665-nonlinearity-measures.md, imported in
substance. [A] marks the delegate's own derivation or computation, carried by
no gate; [P] marks a statement of the source. The delegate disclosed one
read-only git status call and one enumeration script run outside the
repository (the (u|u+w) form of H_n equals the monomial span for n = 3 to 6;
dim C_n = 2^(n-1) - 1 for n = 3 to 6; H_n has minimum weight 4 for n = 3 to
5). Labels in the eight notes: 12 "known theorem reproduced", 7 "new
implementation or measurement".

## Roetteler 2008 (0811.3208)

- [A] No associator phase omega_{a,b} is bent: every omega_{a,b} lies in
  H_n, so it has the constant derivative Delta_{e_{n-1}} omega_{a,b} = c,
  while a bent function needs every nonzero derivative balanced. Theorems 6
  to 9 never apply to the associator family.
- [P] Theorem 9 is Theta(2^(N/4)) in N input bits, not 2^(N/2). Its upper
  bound is stated without proof.

## Gavinsky, Roetteler, Roland 2011 (1103.3017)

- [A] The high-bit rung is OR on the live bits 1..n-2: a complemented delta
  function, the Grover-extremal case of the Boolean hidden shift problem,
  with minimum influence 2^(1-m) for m = n - 2.
- [A] Definition 1's trivial-period condition fails on the full n bits,
  because e_0 and e_{n-1} are periods.
- [A] The Design C readout equals the u-marginal of the paper's Sampling
  Subroutine: new implementation or measurement.
- [P] Definition 2's minimum does not exclude v = 0; the paper quotes the
  bent classical cost as Omega(sqrt(2^n)) with n the input length while
  Theorem 9 of 0811.3208 proves it with n half the input length.

## Decker and Wocjan 2007 (quant-ph/0703195)

- [P] The model is a graph oracle over a large prime field F_p; it has no
  F_2 content: the fidelity bound n / sqrt(p) is vacuous at p = 2 and the
  cubic conditions exclude all of F_2. The classical "polynomial in p" bound
  is a heuristic and the non-prime-field extension is asserted without proof.
- [A] The Design C state is the w = 1 Fourier block of the F_2 graph state:
  new implementation or measurement.

## Decker, Ivanyos, Santha, Wocjan 2011 (1107.2189)

- [P] Theorem 4 and Corollary 2 place graph-oracle polynomial problems inside
  a nonabelian hidden subgroup problem; Theorem 5 costs poly(C(d+n, n)),
  exponential at d = n - 2, so it neither refutes nor supports hardness at
  that degree.
- [A] The DESIGN_NOTES.md sentence "outside standard HSP coset sampling"
  holds only relative to abelian Z_2^n.

## Roetteler 2009 (0911.4724): known theorem reproduced

- [P] A rank-2h quadratic has flat Walsh support on an affine subspace of
  size 2^(2h), by Theorem 1 (Dickson) and Remark 6.
- [A] The paper's "degree k" derivative criterion is off by one; the correct
  form is the (d+1)-fold derivative, and the displayed derivative is additive
  where the Gowers norm uses the multiplicative form.

## Kaufman and Minzer 2022 (2202.08688): known theorem reproduced

- [P] The 2^(d+1) classical test (the (d+1)-fold derivative of a degree-d
  function vanishes) holds for q = 2; the cited prior work [1] and [2] proved
  the q = 2 case, not this paper. Lemma 2.1 is scoped to F_q^(k+1), not to
  F_2^n with n > t + 1.
- [A] It refutes any blanket Omega(2^(n/2)) classical bound for distinguishing
  degree <= d from random whenever d + 1 < n/2. Exception: the OR rung is
  2^-(n-2)-close to a constant, so the 1/delta term dominates and the tester
  needs about 2^(n-2) queries.

## Elkies 2013 course notes: known theorem reproduced

- [P] RM(m-1, m) is the parity-check code, so even-weight functions of m bits
  are exactly RM(m-1, m). The page embeds every lecture write-up; it contains
  no puncturing and no (u|u+v) construction, which the note marks [I] as
  textbook facts. The page prints min(k_1, k_2) where min(d_1, d_2) is meant.
- [A] H_n = {(g | g + c 1)}, the (u|u+w) form with u in RM(n-2, n-1) and w in
  the repetition code; C_n is H_n shortened at the origin, and puncturing
  loses no dimension; H_3 = RM(1, 3), the extended Hamming code. The
  repository's "RM(n-2, n-1) direct sum the top coordinate" sentence is a
  reformulation resting on a known theorem; the group-theoretic content of
  the H_n theorem is not in Elkies.

## Boyar, Find, Peralta (PMC 4957665): known theorem reproduced

- [P] The pair Sigma_2^n against Sigma_n^n separates degree from both
  nonlinearity and annihilator immunity: Sigma_n^n has degree n,
  nonlinearity 1, annihilator immunity 1.
- [A] The OR rung has the same profile: degree n - 2, nonlinearity 4,
  annihilator immunity 1. The values for f(u, t) = [u != 0] + t come from the
  repository's measurement, not from the paper. The order of Table 1's cells
  is unresolved in the extraction; the note rests on Table 2 and Section 3.
- [A] Cross-source: bent functions are quantum-easy and delta-type functions
  quantum-hard, so the six measures do not predict hidden-shift cost; the
  minimum influence does, and it is not one of the six.

## Orchestrator's reading

The associator family is not bent and the OR rung is the Grover-extremal
hidden-shift case, so no hidden-shift speedup claim attaches to Design C as
built; the Design C readout is the u-marginal of a known sampling subroutine
and is labeled new implementation or measurement only. The 2^(d+1)
derivative test refutes the "cubic and above is classically hard" framing
the pasted program carried, as the review already said. The RM description
of H_n is a reformulation; the group-level result is Kirshtein's.
