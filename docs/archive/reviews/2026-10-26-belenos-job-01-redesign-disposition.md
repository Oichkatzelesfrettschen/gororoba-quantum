# Disposition: redesign of the Belenos teleportation rehearsal job-01

The owner chose on 2026-10-26 to redesign job-01 of the single-chip teleportation rehearsal on `qpu:belenos` before
running it. The choice followed the [deep peer review](2026-10-26-belenos-teleportation-rehearsal-review.md). The
owner then asked for a Codex research consult with web access, an independent operator reading, a review of both,
and an implementation of that review. The record:
- the consult's brief ([goal](2026-10-26-belenos-job-01-redesign-consult-goal.md)) and its
  [report](2026-10-26-belenos-job-01-redesign-consult.md), from Codex CLI 0.164.0 running `gpt-daybreak-blue-latest`
  at high effort with live web search;
- the [operator research](2026-10-26-belenos-job-01-redesign-operator-research.md);
- the notes of ten newly registered papers, whose reading was delegated: Specht 2011, Gündoğan 2012, Gill 2003,
  Zhang, Glancy and Knill 2011, Bierhorst 2015, Polacchi 2024, Chiribella and Xie 2013, Anderson 2020, Ma 2012 and
  Strobel 2024 (`docs/notes/papers/`).

## Where the two readings differed

- **Efficiency budget.** The operator note used the protocol's intrinsic 1/18 acceptance; the consult used the
  end-to-end acceptance per optical attempt. The consult holds: the classical device replaces everything from the
  input to the receiver's detector. The memory papers themselves bracket the choice. Specht cancels detection loss,
  while Gündoğan also draws a stricter end-to-end threshold. A budget of the protocol's 1/18 alone would give about
  0.675, but it leaves out on-chip loss, which the service record does not separate from detection loss. The
  end-to-end acceptance, about 3e-6 per attempt in the job-00 model, lies far below the 0.0056 two-copy probability.
  Bound: 3/4 or more.
- **The sector values.** The note on Chiribella and Xie computes the six-state classical value per accepted copy
  number: 2/3, 3/4 and 5/6 at one, two and three copies. A local-search lower bound and the PPT-program upper bound
  agree to six digits. Under free postselection the bound is the largest accepted sector's value, not a weighted
  mean, which settles that the mixture (1 - c) B + c is no bound.

## Recommendations and what the code does

| recommendation | source | implementation |
|---|---|---|
| no applicable "beats classical" verdict; descriptive claim | consult (all questions), operator, notes | descriptive rule `descriptive-v2`; the analysis reports correctness, its anytime-valid lower bound and labeled comparisons, never a verdict |
| the input is visible to the device (one compiled circuit per input) | consult Q2, Bierhorst Appendix 1, Ma Sec. 4 | each comparison names "one label-blind instrument" among its assumptions |
| optional stopping: a radius at the realized count | consult Q3 | fixed-lambda exponential supermartingale with Ville's inequality (`anytime_lower_bound`); lambda from the planned count n*; at n = n* it equals the Hoeffding radius |
| dependence | Gill, Zhang-Glancy-Knill, Bierhorst | the bound holds for the average conditional correctness of the accepted events under any memory; no independence premise |
| two interleaved blocks per input, homogeneity as a veto only | consult Q3 | 12 iterations, block B mirrored; a chi-square block-by-category test per input at 0.01/6 vetoes both comparisons |
| a randomized iteration order | consult Q5 | mirrored order instead, which balances a linear drift with no randomizer; no order hides the input from a compiled circuit |
| attempt box at 1.1 with a break-even ratio | consult Q4 | `box_bound` takes the maximum over the 64 vertices, by the linear-fractional quasi-convexity argument; `break_even_ratio` bisects on [1, 3] |
| the two-copy bound 3/4 | consult Q1, Chiribella-Xie note | comparison (a), naming the truncated two-copy source; the note's 5/6 for three copies is stated in the design |
| drop the 0.02 allowance from the comparisons | review disposition, advisor | the comparisons subtract no allowance, because the data are the realized circuits' correctness |
| preregistered budget 1200 samples per iteration | consult closing design | `DESCRIPTIVE_SAMPLES`; 240 s by job-00's seconds model; `--prepare` refuses only above 300 s or without a shot estimate |
| fresh seeds for every new compilation | consult Q5, repository seed rule | block B takes six values of the keyed ANU draw `draw-2026-10-26T230602Z` |

The submission gate also changed. With no F* to defend, `binding` admits a descriptive case only when the live
performance record's perfs digest equals the prepared read's. The written case quotes that read, so a changed record
calls for a new preparation and approval.

## Process notes

- The consult brief barred every file under `~/.codex/`. The Codex `memories` feature (`use_memories = true`) loads
  `~/.codex/memories/MEMORY.md` into every session, so the session read it; it held no credential, and the report
  discloses the read. Later briefs permit that directory or launch with memories disabled.
- Massar and Popescu 1995 was not retrieved: the DOI resolver and the APS PDF route answered HTTP 403. The N-copy
  formula rests on Specht's and Gündoğan's statements of it.
- Two consult points remain outside job-01:
  - a conditional benchmark needs a label-blind instrument and a measured attempt count;
  - the provider's answer to [Perceval #798](https://github.com/Quandela/Perceval/issues/798) on count provenance
    is the route to the second.
