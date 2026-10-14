# Non-associating basis triples along the Cayley-Dickson ladder

[scripts/cd_associator_defect_census.py](../../scripts/cd_associator_defect_census.py)
counts ordered triples (a, b, c) of distinct imaginary basis units of the
algebra of dimension D = 2^n whose two bracketings differ, using
omega(a, b, c) = s(a, b) s(a^b, c) s(b, c) s(a, b^c) from `cd_core.cd_sign`,
the value of `predict.associator_phase(D, a, b)[c]`. The retained run is
[census.json](../evidence/cd_associator_defect_census/census.json); the CI
gate repeats the exhaustive checks through D = 128, pairs through 64 and
subspaces through 32. Tags: [P] source statement, [E] retained finite
evidence, [T] proved here, [I] interpretation.

## Results

| Statement | Range checked | Status |
|---|---|---|
| Every linearly dependent triple (c = a^b) associates | exhaustive 8 to 512 | [T] from Kirshtein Lemma 3: such a triple generates a subloop of order at most 8, a subgroup of H_8 ([1207.4230](1207.4230.md)) |
| Non-associating ordered triples of distinct units: N(D) = (D-2)(D-4)(D+6)/2; among the (D-1)(D-2)(D-4) independent triples the fraction is (D/2+3)/(D-1), and among all distinct triples (D-4)(D+6)/(2(D-1)(D-3)) | exhaustive 8 to 512; sampled 1024 to 4096 within 4 standard errors | [E] |
| Each 3-dimensional index subspace carries 168 non-associating ordered triples or 72; O(D) = (D-2)(D-4)(D+48)/1344 carry 168: 8, 50, 310, 2046 at D = 16, 32, 64, 128 | exhaustive 16 to 128 | [E]; the 8 to 7 split at D = 16 matches the eight octonion and seven power-associative sedenion subalgebras of [Wilmot](2505.11747.md); [I] the 168 type is the octonion type and the 72 type plausibly the quasi-octonion (power-associative) type named in the literature ([web-source note](casimir-dark-sector-web-sources.md)), an identification not checked subspace by subspace |
| An independent ordered pair (a, b) has no associating completion exactly when {a, b, a^b} contains D/2, and otherwise D/2 - 4: (D-2)(D-4) pairs of the second kind and 3(D-2) of the first | exhaustive 16 to 256 | [E]; summing over pairs reproduces N(D) |
| omega(1, 6, k) = (-1)^popcount((D-2) & k), one Walsh character at mask D-2 | 16 to 4096 | [E]; the degree-1 case of the associator degree formula max(1, bitlen(j) - 2), whose proof is open (task M1, [prior_work_synthesis.md](prior_work_synthesis.md)) |
| The pair (D/2+1, D/4+3) has Walsh support 5D/16 and largest normalized amplitude 1 - 16/D | 32 to 4096 (fails at 16) | [E] |
| With indices 0 to 23 as one block: complement pairs landing in the block number 24D - 704, block pairs landing in the complement 128 | 32 to 4096 | [T] i >= 24 meets k < 8 inside the complement always and k in [8, 24) only for i >= 32, giving 8(D-24) + 16(D-32); block pairs leave only as one index in [8, 16) and the other in [16, 24) |

## Relation to known results

- [P] Kirshtein Lemma 3 gives sufficient conditions for each associator
  value; the census measures what it leaves open. The 72-type
  3-subspaces generate order-16 subloops other than O_16, and 72 of their
  168 independent ordered triples fail to associate.
- [I] The asymptotic defect fraction 1/2 follows from the per-pair
  structure: almost every independent pair has D/2 - 4 associating
  completions out of D - 4.
- [I] The closed forms, the pair characterization and the subspace split
  are finite evidence; proofs and a literature search beyond the sources
  above remain open. A review of the repository supplied the (1, 6) parity
  law, the cross-scale Walsh family, sampled defect rates near 1/2 and the
  24D - 704 count; the census confirms each against `cd_core` and replaces
  the sampled rate with the closed form.
- [I] omega is the coboundary of the sign cochain s on (Z_2)^n, so its
  cocycle identity holds by construction and defines no nontrivial
  cohomology class; associator signs alone do not supply a topological
  invariant ([Albuquerque-Majid](math-9802116.md)).
- [I] The index block of the last row is a coordinate convention; it is not
  a physical sector (see [open_gororoba_handoff.md](open_gororoba_handoff.md#vacuum-model-code-checks)).
