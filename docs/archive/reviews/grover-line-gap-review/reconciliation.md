# Reconciliation: gap review of the line-native CCZ Grover results

Reviewers read main 6437f2866d58d4b2a1e5435e07f04d53165e885e. Verdicts:
confirmed (the source or a recomputation agrees), partly confirmed,
refuted (with the refuting source).

## Findings on the results

| # | Reviewer | Finding | Verdict | Check | Disposition |
|---|---|---|---|---|---|
| G1 | codex | Global depolarizing noise predicts equal corrected unmarked cells; a Wald test on `m101-k1` reads 93.0 on 6 degrees of freedom (bootstrap covariance), while the distance from the matched scalar law is only 0.022. | Confirmed. | `unmarked_uniformity_wald` (delta method, new in `gororoba_quantum/grover_line_analysis.py`): 95.7 (`m101-k1`), 130.5 (generic), 75.2 and 60.5 (011 arms), 16.4 (`m101-k2`); 10.3 on 7 for `k0`. A scratch bootstrap gave 97.2. | Design "Analysis": the scalar carries the marked contrast; the unmarked distribution carries per-qubit structure (wrong-bit probability 0.154 on QB20 against 0.180 and 0.178 on QB16 and QB17). |
| G2 | codex, grok, agy | Weight means hide anisotropy; "close to global" had no test. | Confirmed (`m011-k1` weight-2 ratios 0.725 to 0.882). | Analysis record `corrected_walsh_ratio`. | Design text corrected. |
| G3 | codex, grok, agy | Finding 7 (global noise justifies reading associator spectral classes from samples) over-reaches: those circuits sample squared Walsh amplitudes of a phase with no diffuser. | Confirmed. | Tuna-17 record: `class_order_holds` true with every listed combination in `shape_rejected` (`results/quantum_inspire/walsh_exemplar_tuna_17_analysis.json`). | Claim withdrawn from the design; the transferable statement narrowed. |
| G4 | codex, grok, agy | The degree law is proved for every level in gororoba-math; the design called it a computation through dimension 32. | Confirmed. | `Tower.anfDegree_negSign_left` (BooleanAnf.lean), `sign_row_degree` and `sign_row_degree_all` (CdSignRowAnf.v), at gororoba-math 7cf47d872. | Design cites the theorems with sha256 and commit. |
| G5 | codex, grok | Only the left row has degree n - 1; a power-of-two right row has degree 1; `sign_row_leading` fixes the cubic monomials of a sedenion row (one to four). | Confirmed. | `right_row_degree`, `sign_row_leading` in CdSignRowAnf.v. | Design states the operand choice and the monomial count. |
| G6 | codex, grok, agy | The 66-CZ half-contrast forecast transports a three-qubit Grover rate to a four-wire oracle with another gate mix. | Confirmed. | Arithmetic: ln 2 / -ln 0.9896 = 66. | Marked as a hypothesis. |
| G7 | grok | Tuna-17 already ran 66-CZ pairs "and reported no resolved contrast". | Partly refuted: one of three regions is unresolved; two resolve (+0.051 and +0.072 raw). | `results/quantum_inspire/secondary/zero_divisor_tuna_17.md` region table. | Cited accurately in the design. |
| G8 | codex | The residual-risk sentence called model differences upper estimates, while the measured gain (+0.070) is twice the prediction. | Confirmed. | Result table. | Sentence corrected. |
| G9 | codex, grok, agy | The error budget has zero degrees of freedom and no intercept. | Confirmed; codex adds that it predicts 0.749 at the two-iteration counts against 0.746 (101) and 0.718 (011). | Two-equation solve. | Design states both. |
| G10 | agy | The analysis record has `"error_budget": null`. | Refuted: the record has no such key (`grep -c error_budget` returns 0); the budget lives in the design text only. | grep. | None. |
| G11 | grok | The two marked strings retain differently at one iteration, 0.864 against 0.830, against the design's X-conjugation sentence. | Partly confirmed: the per-iteration ratios agree (0.864, 0.866) as the sentence said; the one-iteration retentions differ by about 2.3 standard errors. | corrected_marked_se of both arms. | Design states the difference. |
| G12 | codex | Two depths fit lambda_k = A r^k exactly; A = 1.00 +- 0.02 (101), 0.96 +- 0.03 (011). | Confirmed as arithmetic. | lambda_1^2 / lambda_2. | Design states it; a third depth tests the law. |
| G13 | codex | ABBA balances unweighted positions; kept-shot weights leave 9.444 against 9.516; one job. | Confirmed. | Recomputed from `results.json` shots. | Residual risk. |
| G14 | codex | Path chosen on the same calibration to maximize the line score; one generic seed. | Confirmed as a scope limit (prospective, no outcome peeking). | Builder. | Residual risk. |
| G15 | codex, agy | Heralding: the run returns only kept shots; per requested shot the line arm still wins (0.577 against 0.526) at lower acceptance (85.6 % against 87.0 %). | Confirmed; agy's proposal to compare discarded shots cannot run on this record. | Kept counts over 16000 requested. | Residual risk. |
| G16 | codex | CLAIM_BOUNDARIES.md says the finite denominator is the evidence scope of the degree statements, which the all-level theorems exceed. | Confirmed for degree; the Walsh class census keeps its finite scope. | `gororoba_quantum/CLAIM_BOUNDARIES.md` degree lines. | Open: a claim-boundary edit in its own change. |

## The quasi-Riemann-hypothesis formalization (math/ family 003)

All three reviewers agree, and the sources confirm:
`OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` states `riemannZeta s != 0`
for Re s > 7/8, and `OAI.DirichletCharacter.LFunction_ne_zero_of_seven_eighths_lt_re`
the same for every modulus and character except the principal pole. The
comparator configuration admits only `propext`, `Quot.sound` and
`Classical.choice`; a source search of the DirichletL subtree finds no
`sorry`, `admit`, `native_decide` or declared axiom; the comparator was not
run here, and imported libraries were not audited transitively. It is
neither the Riemann hypothesis nor GRH: the strip 1/2 < Re s <= 7/8 stays
open. Its connection to these oracles is empty: a finite Dirichlet
character loaded as a qubit phase tests phase loading and interference
(codex: chi_8 on the odd residues is (-1)^(x0 + x1), an exact control), and
says nothing about zeros of the continued L-function.

Families of `math/` that share a mechanism with the open questions:
family 119 (Courtade-Kumar: information contraction under independent
symmetric cube noise, an alternative noise model for parity attenuation),
family 192 (real multilinear degree, a different degree from the F_2 degree
used here), family 127 (average sensitivity of degree-d polynomial
threshold functions; relevance to oracle noise is a hypothesis). None is
cited by gororoba-quantum.

## Questions the records do not yet ask

1. Does class ordering of the cubic associator spectra survive the measured
   structured noise? Simulate both exact histograms through per-qubit and
   class-specific attenuation with the Tuna block-interaction analysis; no
   credits.
2. Does a third depth stay on lambda_k = A r^k? A k = 3 or identity-folded
   arm; about 1 credit on Garnet.
3. Is the generic loss its 46 extra `prx`? A generic compile resynthesized
   to 22 `prx` at 18 CZ; about 1 credit.
4. Does the line-native gain hold on a typical path and against a
   seed-optimized generic compile? A seed and path sweep of predicted
   differences first; no credits.
5. Which of the 15 sedenion left rows is cheapest, compiled with shared
   parities and tracked permutations on four wires? Synthesis and exact
   verification; no credits.
6. Is the per-qubit residual (QB20 more reliable than QB16 and QB17) a
   property of the qubits or of their position in the network? The same
   arms on a permuted path; about 1 credit.
7. How much of the rejected shape is assignment-matrix drift? Compare the
   measured matrix with the calibrated product channel; no credits.
8. Can the planned sampler distinguish the claimed associator classes on
   ideal hardware (identical squared spectra exist)? Enumeration; no
   credits.
