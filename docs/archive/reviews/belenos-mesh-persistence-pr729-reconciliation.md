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
binomial draw at the retained counts, and a numpy seed that carries no QRNG ledger entry. They are diagnoses of
the case as reviewed, with its Student-t slope bound, and no number in the two tables below is a retained record.
The retained power record of the corrected case covers both conditions from a ledgered seed (Resolutions below).

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
| The Student-t upper bound on the slope has no demonstrated coverage | Codex (serious), Opus (most severe) | The second table: redrawn at beta 0.5 is read in 0.083 to 0.085 of jobs under the retained block spreads, against a nominal 0.05, and persists drops from 0.74 to 0.63 | Confirmed and fixed: the bound inverts the within-block relabeling test (Resolutions below) |
| The tests do not bind the thresholds, the degrees of freedom, the drift rule or the power record | Codex, Opus, Grok (noted) | Mutations listed by the reviewers | Fixed: whole-statistic enumeration, the slope bound against an enumerated relabeling test, strict thresholds, a tie counted, the drift stop, the thresholds read from the frozen case, the secondary block counts, and a replay of the power record from its ledgered seed |
| The drift gate adds zero for a missing contrast and keeps its degree of freedom; a zero count divides by zero | Grok (serious), Opus | `swap.two_sample_z` returns None for a zero count | Fixed: `analyze` stops with "an iteration returned no single-click counts in a block" and names the block and settings |
| A missing `computed_circuit` reads as a changed mesh | Opus | `digests` held None, which compared unequal | Fixed: `analyze` stops with "an iteration returned no computed_circuit" |
| The identity check hashes the serialized circuit, so a serializer change reads as a changed mesh | Opus | The digest is over the returned JSON value | Fixed: the decoded unitary decides the identity (Resolutions below) |
| The block-matching fixture has identical centered rows in every block | Opus | Reversed pairing gave slope 1 | Fixed: each block carries its own pattern, and the test asserts a positional pairing misses slope 1 |
| The document calls beta 0.25 the indeterminate region, and "persists" has no slope floor | Opus | Power table row 0.25: persists 0.291, redrawn 0.326, indeterminate 0.384 | Text corrected, and persists takes the useful slope as its floor (Resolutions below) |
| `bound_seconds` re-implements `swap.iteration_seconds()`; `--power` reads sigma from an unsorted glob | Opus | Same formula; nine runs hold one sigma | Fixed: the helper is reused, and the sigma comes from the sorted runs with a stop on disagreement |
| Reusable analysis lived in the script; the histogram reductions ran serially | hosted Codex round | AGENTS.md "Layout and gates" | Fixed: the statistic lives in `gororoba_quantum/mesh_selection.py` with caller-supplied thresholds, and `analyze` maps `swap.iteration_shares` through `parallel.ordered_map` |

The refactor of the reviewed commit changed no number: `power(21344, 0.05150455979158212)` reproduced the power
record of that commit exactly, and `--check` rebuilt its frozen case byte for byte.

## Checks that found nothing, by agreement of the reviewers

The replay rows equal their retained sources and the circuit is byte-identical to job-09; the QRNG ledger row of
`draw-2026-11-01T054809Z.json` index 2 (21344) is present and unique; the duration bound is 257.1 s against the 270 s
margin and the credit ceiling is 1.09; the script has no submission path; the corrected numbers of the best-mesh
investigation and the herald-leak analysis follow from `results/quandela/belenos-best-mesh-first-principles.json`;
that record only gains fields; no mock outcome enters the analysis.

## Resolutions of the four findings the first reconciliation left open

The owner directed that each be resolved in this pull request.

1. **The slope bound.** `mesh_selection.slope_lower_p` tests a slope b by relabeling the residuals e_new - b e_old
   within each block, and `slope_upper_bound` returns the largest b that test keeps at alpha. The bound needs
   exchangeability within a block only, the assumption of the p-value that held up above. `preregistered()` and the
   frozen `cases.json` state it; the case is unsubmitted, so no approved record changes.
2. **A ledgered sensitivity record.** `power()` runs four fresh-error models (one size, each block's retained spread,
   and half or all of the variance shared by a mesh's blocks) from
   `qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#3`, and
   `results/quandela/belenos-mesh-persistence-power.json` holds all four. Index 2 of that draw (21344) seeded the
   power record of the reviewed commit; its ledger row moves to the reserved section, keyed to the script, and the
   value stays consumed.
3. **A floor on "persists".** The reading is persists when p < 0.05 and the slope estimate is at least 0.5.
   "Recurs below the useful slope" needs p < 0.05 and q(0.5) < 0.05, the same test that reads redrawn, so no
   reading rests on the estimate alone on the low side. At beta 0.25 persists falls from 0.29 to between 0.08
   and 0.16.
4. **Identity by decoded parameters.** `analyze` decodes each `computed_circuit` with Perceval and compares the
   24-mode unitaries, one mesh at a largest entry difference of at most 1e-4; single-precision phases move an
   entry by 4.5e-7 and two seeds differ by at least 1.2. The sha256 comparison stays in the record as
   `same_bytes`.

The retained power record under these rules, 2,000 jobs per cell:

| Fresh-error model | persists at beta 0 | redrawn at beta 0.5 | persists at beta 0.25 | persists at beta 0.75 | below the useful slope read at beta 0.75 |
|---|---|---|---|---|---|
| one error size for every block | 0.0095 | 0.0425 | 0.116 | 0.9645 | 0 |
| each block's retained spread | 0.0245 | 0.0525 | 0.1555 | 0.913 | 0.001 |
| half of the variance shared by a mesh's blocks | 0.0035 | 0.0305 | 0.0885 | 0.9705 | 0 |
| all of the variance shared by a mesh's blocks | 0 | 0.0015 | 0.077 | 0.979 | 0 |

The Student-t bound read redrawn at beta 0.5 in 0.083 to 0.085 of jobs under the retained block spreads; the
relabeling bound reads it in 0.0525.

An Opus review of these resolutions before they were committed found the first identity tolerance (1e-9) below
the effect of a rounded serialization, a "recurs below" reading that rested on the estimate alone, a ledger reason
that misdated the spent seed, and test mutations that survived; the tolerance, the reading rule, the ledger row and
the tests in this pull request are the corrected forms. It confirmed the monotonicity of q(b), the bisection
against exact enumeration, and every quoted number against the record.

The hosted Copilot review of these resolutions found three defects, each confirmed against the source and fixed.
`slope_upper_bound` searched 64 fixed steps and returned infinity for retained shares 1e-6 apart, whose bound is
finite near a slope of 8e4; it now reads the two limits of q(b) to decide an infinite bound and doubles its reach
to the bracket otherwise. Its bisection could stall where adjacent floats lie further apart than the tolerance;
it now ends on adjacent floats. `slope_terms` writes the relabeled excess as rise + b lost, with lost half the
squared displacement of the retained deviations, so a near tie keeps its small positive value and an exact tie
is exactly zero. The synthetic-count fixture of the script tests gave 2,575 marginal hits to 1,000 shots through a
negative count; it now nests the blocks' hits over the shots. The audit replay reproduces the power record
unchanged under the rewritten test.

## Open

- The within-block relabeling test would turn liberal for retained deviations that are coherent across slots; the
  retained window shows none (variance ratio 0.76 above), and the case states the exchangeability model.
- The primary cell pools two iterations and so carries half the binomial variance of a replicate cell; the binomial
  error is about a tenth of the mesh error, and the power record includes it at the retained counts.
