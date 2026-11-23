# Reconciliation of the state audit of the A_5 fiber program

Two reviewers read one brief ([brief.md](brief.md)) on main `78c5e5c3a` on 2026-11-22: `codex` on
`gpt-daybreak-blue-latest` at high effort ([review-codex.md](review-codex.md)) and `agy` on `gemini-4-neon-high`
briefed as a red-teamer ([review-agy-neon.md](review-agy-neon.md)). The brief carried the orchestrator's reading C1
to C4 for attack. The Advisor was not run, on the owner's instruction for this session. Each finding below is
justified against the ledger or a computation of this change; a reviewer's own "confirmed" label counts for
nothing until the source is read here.

## Corrections to the orchestrator's reading

| Finding | Reviewer | Check | Outcome |
|---|---|---|---|
| The degree-3 component of E8-bar -> VB is proved, so C2(c) is stale | both | A5-016 reads proved at both primes | accepted; the status note lists only characteristic 0 and the boost for VB |
| A5-458 is superseded by A5-475 | both | ledger statuses | accepted |
| A5-571 and A5-577 are receipt gaps, not missing mathematics | codex | the rows' own bases | accepted; both are closed or run in this change |
| The 100 rows with status survives are mostly hardware observations and method timings | both | kinds and fibers of those rows | accepted; the note counts open theorems, not survives rows |
| C1 mixes header-slice proofs (A5-270, A5-305) with weight-slice proofs (A5-446, A5-448, A5-457) | agy | the rows name their slices | accepted; the completion table names the slice in each cell |
| 26 of 33 incidences have proved real limit sets, so A5-250 is narrower than C2(d) states | both | A5-411 (14), A5-412 (8), A5-417 (4) | accepted |
| C3 omits `A5W8ArcMatrixRanks.v` | agy | the file exists in gororoba-math; the brief named it | accepted as a wording point; no fiber-cone statement is formalized |
| The status note of 2026-11-11 is stale in its counts, the E8-bar degree-6 cell, A5-016, characteristic 0 and the real part | both | each passage against A5-335, A5-559, A5-016, A5-446 to A5-475, A5-411 to A5-417 | accepted; the note is rewritten |

## Proposals tested in this change

| Proposal | Reviewer | Test | Outcome |
|---|---|---|---|
| Unit polynomials of A5-592 follow from Pf_4(W) = Pf(B)^3 Pf_10(T) | agy, as "confirmed derivation" without a run | `e8-pfaffian-schur-identity`: 126 quadruples over Q(i) at both signs, control with exponent 2 | holds; A5-593. The claim that the extra factor of generators 10 and 16 sits in Pf_10 also holds; A5-594 |
| The block splits factor as characters of two nodal conics | agy | `fiber_coefficients.py`: d = 1 to 12 and nine measured splits | the character identity holds; the ring structure is untested; A5-596 survives, A5-278 stays open |
| The Hilbert numerators factor with a component reading | both | exact division and the identity on the retained numerators | holds; A5-595. The pieces are the rows A5-503, A5-502, A5-501 and A5-454 |
| A5-583 by GL-invariants first, then a map | both | `slice_bridge.py`: tori of the symmetry algebras, matching, scalars, Singular verification | a map exists at both cells modulo 32009; A5-583 certified. Neither reviewer proposed the torus route |
| A5-577 by the producer's own functions | both | `weight_slice_modular_cells.py` | both digests agree; A5-577 certified |
| E8-bar -> VB over Q(i) by the arc families | both | `arcs-vb-qi.sing` | L = K2 over Q(i) at the retained basepoint; A5-597 |
| A5-571 by the receipt driver at the second root | both | `e8np-d2-receipt-p32009-r21255` | the driver run on the second-root header had not ended when this record was written; A5-571 stays open and its receipt joins the record when the run ends |

## Findings not adopted or corrected

| Finding | Reviewer | Reason |
|---|---|---|
| The basis files of the open-cell runs are not retained | both | the repository retains their digests; the files are kept outside it with the working directories of the runs. The single-engine point stands |
| A5-005 to A5-009 are "status inflation" | agy | the rows state primes `both`, which the ledger defines as the two primes; the note records that they are modular |
| A boost family, a nullity-4 chart and a second-system cross-check "fit one workday" | agy | not run; the note lists them as next computations with the retained timings, and the cross-check as not run for want of the tool |
| The equivalence of A5-583 "would take under one minute by a Pluecker frame" | agy | no such frame is retained; the map came from the torus computation (30 s and 88 s) |
| `satstd` is trusted without a containment check | agy | correct for the v2 scripts; recorded under the single-engine risk, not changed here |
| The L = K argument depends on `primdecGTZ` completeness | agy | correct; recorded as a weakest link with formal target 7 |

## Not run

Local reviewers on the diff of this change: asked of the owner at the draft pull request. Macaulay2 cross-check:
not run (tool absent on the compute hosts, package `macaulay2`).
