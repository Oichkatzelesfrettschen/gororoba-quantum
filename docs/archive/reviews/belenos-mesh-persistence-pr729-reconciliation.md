# Reconciliation of the three reviews of pull request #729

Three reviewers read commit `5deb80f95` (branch `analysis/belenos-mesh-persistence` with `main` merged in) against
`origin/main` under one [brief](belenos-mesh-persistence-pr729-review-brief.md):
[Codex gpt-daybreak-blue-latest](belenos-mesh-persistence-pr729-review-codex-daybreak-blue.md) at high effort,
[Grok Build](belenos-mesh-persistence-pr729-review-grok.md) and an
[Opus agent](belenos-mesh-persistence-pr729-review-opus.md). Each finding was then checked against the files or by
computation. The Grok report is filed without the progress lines that preceded its text.

## Diagnoses run for this reconciliation

Two scratch simulations tested the statistical findings. Both use the retained packed set-4 shares and counts
through `mesh_selection.persistence`, a fresh Gaussian mesh error independent of the retained deviations, a
binomial draw at the retained counts, and a numpy seed that carries no QRNG ledger entry. They are diagnoses, and
no number below is a retained record.

*Shared mesh error across blocks* (1,500 jobs per row; the new error is a mix of one term per mesh shared by all
six blocks and one term per cell):

| Shared share of the new mesh variance | Within-block relabeling test, rejections at beta 0 | Whole-mesh test (24 relabelings), rejections at beta 0 |
|---|---|---|
| 0 | 0.053 | 0.047 |
| 0.25 | 0.051 | 0.043 |
| 0.5 | 0.046 | 0.049 |
| 0.75 | 0.025 | 0.041 |
| 1 | 0.009 | 0.041 |

The retained window shows no shared structure: the variance of a mesh's mean deviation over the six blocks is 0.76
of its expectation under independent blocks. At beta 1 both tests reject in every job.

*Unequal block spreads* (3,000 jobs per row; the standard deviation of a block's four centered retained shares is
0.028, 0.038, 0.066, 0.066, 0.082 and 0.040):

| Fresh error size | persists at beta 0 | redrawn at beta 0.5 | persists at beta 0.5 |
|---|---|---|---|
| one size for every block | 0.047 | 0.052 | 0.742 |
| each block's retained spread, rescaled to the pooled size | 0.042 | 0.085 | 0.627 |
| each block's retained spread | 0.048 | 0.083 | 0.627 |

The Opus review's own run, with the slot shift of `power()` included, gives 0.071 and 0.085 for redrawn at beta
0.5 against 0.044 for a flat sigma.

## Findings and dispositions

| Finding | Raised by | Check | Disposition |
|---|---|---|---|
| The relabeling test permutes within each block although a compilation seed yields one mesh across all blocks | Codex (fatal) | The first table: the test keeps its size without shared error and turns conservative with it; Opus reaches the same sizes and the same reason (squared column sums 0.0439 below squared deviations 0.0579) | Refuted as a liberal test for these retained deviations. The case states its within-block exchangeability model in `preregistered()` and the design document. It would turn liberal for retained deviations coherent across slots |
| The Student-t upper bound on the slope has no demonstrated coverage | Codex (serious), Opus (most severe) | The second table: redrawn at beta 0.5 is read in 0.083 to 0.085 of jobs under the retained block spreads, against a nominal 0.05, and persists drops from 0.74 to 0.63 | Confirmed. The design document now states the limit. The replacement bound and the restated power table are an owner decision (below) |
| The tests do not bind the thresholds, the degrees of freedom, the drift rule or the power record | Codex, Opus, Grok (noted) | Mutations listed by the reviewers | Fixed: whole-statistic enumeration, the bound formula on 17 degrees of freedom with a nonzero residual, strict thresholds, a tie counted, the drift stop, the thresholds read from the frozen case, the secondary degrees of freedom, and a replay of the power record from its ledgered seed |
| The drift gate adds zero for a missing contrast and keeps its degree of freedom; a zero count divides by zero | Grok (serious), Opus | `swap.two_sample_z` returns None for a zero count | Fixed: `analyze` stops with "an iteration returned no single-click counts in a block" and names the block and settings |
| A missing `computed_circuit` reads as a changed mesh | Opus | `digests` held None, which compared unequal | Fixed: `analyze` stops with "an iteration returned no computed_circuit" |
| The identity check hashes the serialized circuit, so a serializer change reads as a changed mesh | Opus | The digest is over the returned JSON value | Open, owner decision (below) |
| The block-matching fixture has identical centered rows in every block | Opus | Reversed pairing gave slope 1 | Fixed: each block carries its own pattern, and the test asserts a positional pairing misses slope 1 |
| The document calls beta 0.25 the indeterminate region, and "persists" has no slope floor | Opus | Power table row 0.25: persists 0.291, redrawn 0.326, indeterminate 0.384 | Text corrected. The slope floor is an owner decision (below) |
| `bound_seconds` re-implements `swap.iteration_seconds()`; `--power` reads sigma from an unsorted glob | Opus | Same formula; nine runs hold one sigma | Fixed: the helper is reused, and the sigma comes from the sorted runs with a stop on disagreement |
| Reusable analysis lived in the script; the histogram reductions ran serially | hosted Codex round | AGENTS.md "Layout and gates" | Fixed: the statistic lives in `gororoba_quantum/mesh_selection.py` with caller-supplied thresholds, and `analyze` maps `swap.iteration_shares` through `parallel.ordered_map` |

The refactor changes no number: `power(21344, 0.05150455979158212)` reproduces
`results/quandela/belenos-mesh-persistence-power.json` exactly, and `--check` rebuilds the frozen case byte for
byte.

## Checks that found nothing, by agreement of the reviewers

The replay rows equal their retained sources and the circuit is byte-identical to job-09; the QRNG ledger row of
draw `2026-11-01T054809Z` index 2 (21344) is present and unique; the duration bound is 257.1 s against the 270 s
margin and the credit ceiling is 1.09; the script has no submission path; the corrected numbers of the best-mesh
investigation and the herald-leak analysis follow from `results/quandela/belenos-best-mesh-first-principles.json`;
that record only gains fields; no mock outcome enters the analysis.

## Open, for the owner before the case is approved

1. **The slope bound.** A bound that holds under unequal block spreads (a per-block-variance or sandwich standard
   error, or a bound from the relabeling distribution), with a power simulation that draws a per-slot sigma and a
   restated table. This changes `preregistered()` and so the frozen `cases.json`.
2. **A ledgered sensitivity record.** Whether the two diagnoses above become a retained record with a QRNG-ledgered
   seed beside the power record.
3. **A floor on "persists".** The reading establishes a slope above zero; at beta 0.25 it occurs in 29 % of jobs
   and would open the optional teleportation replay of 8 to 10 credits.
4. **Identity by decoded parameters.** Comparing the decoded mesh within a tolerance, with the byte digest kept as
   a secondary field.
