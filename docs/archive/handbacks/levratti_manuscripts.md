# Handback: Levratti author-hosted manuscripts

Final statement of the delegate that wrote levratti-2026-fano-css.md and
levratti-2026-active-stabilizers.md, imported in substance. [A] marks the
delegate's own recomputation from cd_core.py, carried by no gate; [V] marks
a claim the orchestrator re-verified in this tree; [P] marks a statement of
the manuscript. Both sources are author-hosted, not peer reviewed, and their
linked Zenodo records were not retrieved.

## Paper 8, Fano Duality, Projective Orthogonality and the CSS Bridge

- [A] Design A's W = L_{ij}^-1 L_i L_j and Levratti's dual Z-string are the
  same seven strings: for all 21 pairs W is diagonal with entries
  sg (-1)^popcount(v & k), and v equals his v_L for the pair's Fano line;
  the real triple product L_p L_q L_{p^q} along each of the 7 lines gives the
  same strings with a real sign where he has +i or -i; the repository's
  "Z on qubit 2" for (1, 2) is his ZII row for line {1, 2, 3}.
- [V] Re-verified here: every one of the 21 associator phases at dimension 8
  is a Z-string Z^v with v nonzero and orthogonal to the pair's Fano line.
- Labels: conceptual content, close prior conceptual overlap with the
  standard label known theorem reproduced (point-line duality of PG(2, 2));
  the interference circuit, normalized slices, and compile record, new
  implementation or measurement.
- [P] The overlap with "circuit reading of that associator" sits in his
  Corollary 4.1(c), "records the geometric obstruction to associativity",
  an interpretation: he computes no associator, normalizes nothing, builds
  no circuit, and does not cite Albuquerque and Majid.
- [A] A three-qubit Z^v is a diagonal operator on 8 basis states while the
  Steane stabilizer is a weight-4 operator on 7 qubits; he joins them only
  by group labeling. The embedding that would make them one claim,
  |x> -> X_x |code>, under which the 3-qubit register is the syndrome
  register, is textbook and he does not state it.
- Internal validity, verified by recomputation: 7 lines with a unique
  orthogonal v each and a bijection; Table 1 (the q column and the
  stabilizer-support columns) and all 15 rows of Table 2; the 35 = 7 + 28
  triple count. Verified by reading: the proof of part (iii) is correct
  linear algebra but covers his assignment L -> Z_L, not the Clifford map.
  Unverified: Q values imported from the unretrieved companion [5] and
  everything from companions [1], [4], [5].
- [A] Theorem 3.1(ii), Theorem 5.1(ii), and Proposition 5.2 hold by
  definition of the generator labeling, so Remark 5.3 adds no independent
  evidence. Remark 5.4's identity L_p L_q = eps L_{p^q} is false; the
  anticommutation conclusion is true via left alternativity. His 63/42
  anticommutator split reproduces in dimension 16, and the repository's 42
  corpus index pairs are exactly the 42 non-anticommuting pairs, which his
  text labels "non-ZD"; whether that labeling is inverted depends on a
  definition in [1].
- Smaller errors: Proposition 5.2 gives the code dimension as 2^(n-1) - n,
  the classical Hamming dimension, where the quantum dimension is
  2^(n-1) - 2n + 1; "all n >= 2" overreaches because CSS(C, C) fails for
  n = 2 and 3; the Table 2 caption says "first four elements" while the
  table lists all seven; Open Problem 3 calls Q a logical operator while
  Theorem 3.1(ii) calls it a stabilizer.

## Paper 5 page, Active Stabilizers in Reed-Muller CSS Codes from Cayley-Dickson Zero-Divisors

- About 340 words of page text were retrievable; the note records exactly
  what the page states.
- [A] The page's mixed-flat shape {i, j, 8+k, 8+l} matches the repository's
  sedenion corpus: all 336 rows have i ^ j ^ k ^ l = 0 with two indices below
  8 and two at or above 8, using 42 distinct supports, assuming the XOR rule
  for mixed flats, which the page defines only for lo-flats.
- No prior overlap is visible for the Design B/D construction or
  observables. Step 1 is known theorem reproduced against the repository's
  Steane reference section, with the zero-divisor tie unassessed; Step 2's
  Pauli identity checks by hand but alone carries no zero-divisor content.
- Every hardware figure on the page is author-reported and unverified: the
  "verified on QPU" statement, ibm_kingston, the job id, and the date; the
  page gives no circuit, shot count, or data. Not assessable from the page:
  its sign convention, the definitions of flat, Type-A/B, and active, and
  the proofs. The page calls itself Paper 5 while paper 8 cites it as [4];
  the DOI matches.

## Orchestrator's reading

Design A's seven strings have close prior conceptual overlap and the
DESIGN_NOTES.md Design A section says so; the repository's claim narrows to
the associator reading with normalized slices, the interference circuit
with controls, and the compile and hardware records. The delegate's
proposed self-tests (Fano-line Z-string product, the 63/42 anticommutation
split, the mixed-flat corpus shape) are cheap and worth a gate; the Zenodo
records are retrieved before anything imported from them is cited.
