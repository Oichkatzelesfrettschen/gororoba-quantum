# DAS MERGUS data, statistics and repository-fact review

This review attacks the data, statistics and repository-fact claims of the
DAS MERGUS companion package (chapters 01, 04, 07, 08 and 09, the
`analysis/statistics/` programs and records, `analysis/audit_corpus.py` and
its record, and the README's data claims) and three claim groups from an
earlier pasted review summary: (a) Ascella serial statistics, (b) a
within-job first-versus-last exact test, and (c) an IBM raw-population count.
Every claim is checked against the retained raw files with code written for
this review. The ledger
[2026-10-25-das-mergus-data-claims.json](2026-10-25-das-mergus-data-claims.json)
holds 62 claims, schema `delivery-claim-ledger-v1`.

## Findings

No claim in scope calls for a correction to `docs/state/research_state.json`,
the Ascella evidence README (`docs/evidence/ascella-order-coefficients/README.md`)
or `docs/notes/quandela/strategy.md`. Its run rows ("lag-1 -0.65, not the
setting (Spearman -0.08)", "4 to 586 per setting") match the recomputation.
The arithmetic of the package and of the pasted summary holds up
everywhere checked. Two inferences fail:

1. **The pasted first-versus-last test (b) measures execution-order
   overdispersion, so its rejections carry no configuration-specific
   meaning.** Its counts are exact: 40/60 Holm rejections (24 and 16), and
   4/8192 to 586/8189 as the largest change, and the exact test correctly
   rejects its own equal-probability null. The summary does not itself claim
   a configuration reading; the review refutes that reading. Pairs of
   *different* configurations at the same execution gaps reject just as
   often, and an execution-order dispersion removes every rejection.
2. **"Analyzer configuration statistics repeat extremely well" (chapter 04
   section 4.4) holds only for the block-conditioned estimand.** Under the
   registered twelve-mode denominator the between-job X equality is 47.73 on
   10 degrees of freedom (p about 1e-6). The package table never names its
   denominator.
The direct sign-odd term survives a stronger variance model. It is the one
new-evidence candidate, but its sign is aliased with compilation (see
Opposition). The "rejects a common affine quadrature map" result is the
repository's preregistered fourth-harmonic test under a new name. The package
critiques of the PR #449 omitted-configuration procedure were correct at the
package's snapshot, and main has already superseded that procedure. All
repository counts are exact at `41d5ef0` and stale against current main.

## Verdict counts

| Verdict | Count |
|---|---:|
| confirmed | 30 |
| already-in-repo | 13 |
| stale | 11 |
| unproven | 6 |
| refuted | 2 |
| **total** | **62** |

Actions: 59 none, 2 reject (S11, Pb5), 1 new-evidence candidate (S07).
No row calls for a record correction. Two verdicts rest only on rerunning the
package: S14 (mesh Jacobian ranks) and S20 (phase-command proxy fit), both
`independent: false` and marked unproven. Every other verdict comes from
independent code.

## Method

An independent decoder reads both Ascella `raw/result.json` files:
base64 and zlib over the `:PCVL:zip:` payload, then the PCVL `BSCount` per
iteration. It maps iterations to settings by `observation_index`, checks the
echoed `circuit_params` to 1e-15, and keys each returned configuration by the
SHA-256 of the decompressed `computed_circuit` plus `computed_input`. The
decoder reproduces table 4.1 exactly: 524,175 and 1,048,301 eligible events,
6,659 and 13,268 outside modes 0-3, and 30 configurations per job (28 pairs
and 2 quadruples). All 27 registered endpoints and Hoeffding radii of both
jobs match `analysis.json` to 1.1e-16, including the two mutation endpoints
rebuilt from the weights in `scripts/ascella_coherence_analysis.py`. Exact
tests use Python integers (`math.comb` weights, `Fraction` tails). Permutation
p-values are replaced by asymptotic references or by the retained
`repeat-comparison.json` null; the one probe that draws a permutation null,
`serial3.py`, takes its seed from the ANU QRNG draw
`docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json` (index 0). The check
scripts and their inputs live in
[das-mergus-checks/data/](das-mergus-checks/data/). The registry census reads
`research_state.json`, `ci/gates.json`, `docs/state/plans/` and
`git ls-files` at `41d5ef0` and at main `182fb20`.

## Refuted and record-adjacent claims

### Pb5: first-versus-last rejections do not isolate configuration

The pasted test treats each returned configuration as one binomial
probability. Its rejections are arithmetically right, and they would mean the
configuration does not fix its outside-block rate only if configuration were
the relevant control. Four checks break that reading:

- **Null family.** At the realized Holm cutoff (p <= 7.05e-4), within-job
  pairs of *different* configurations at the same gaps reject at 116/159
  (73%) in job-00 and 452/759 (60%) in job-01. Configuration pairs reject at
  24/30 (80%) and 16/30 (53%). Configuration identity adds nothing.
- **Execution covariate.** Predict each setting's log outside rate,
  log((o+1/2)/N), by the mean of its lag-2 neighbors. Those neighbors share
  the alternation phase and are different settings. The predictor explains
  77% (job-00) and 65% (job-01) of the log-rate variance. The quasi-Poisson
  dispersion of counts about it is 71 and 248. An overdispersed log-Wald
  first-versus-last test with variance phi(1/(o_f+1/2) + 1/(o_l+1/2)) rejects
  0/30 per job under Holm. The first rejection returns only below phi 24.0
  (job-00) and 33.7 (job-01), so the null result does not depend on the
  smoother's details.
- **Parity confound.** In job-00 every one of the 30 first/last pairs
  straddles opposite execution parity (gaps 1 or 3, plus 7 and 51 for the
  quadruples). Half of the test is therefore order-confounded by
  construction. In job-01, same-parity and opposite-parity pairs reject alike
  (8/14 and 8/16).
- **In-block contrast.** The same pairs agree on their registered readout
  statistic within counting noise: 33.0 on 30 and 19.6 on 30 degrees of
  freedom. Configuration determines the in-block response, and execution
  order drives the outside-block rate.

The preregistered alternative already says this:
`repeat-comparison.json` records the job-01 sequence statistic -0.653137 as
supported and the setting-identity Spearman -0.075453 as not supported. The
first/last selection and the exclusion of quadruple middles were chosen after
looking. Including all members changes nothing, because the order process
dominates every within-job comparison.

### S11: "repeat extremely well" needs its denominator

For the pooled between-job comparison, the review pooled settings by returned
configuration within each readout, excluded mutation settings, and used
variance v00 + v01. It reproduces the package values: X 3.329, Y 8.350,
direct 25.504 on 10 degrees of freedom, with residual correlations 0.9966,
0.9649 and 0.8940. With the registered twelve-mode denominator the same
comparison gives X 47.73 (p about 1e-6), Y 15.66 and direct 37.29 (p 5e-5).
Conditioning on modes 0-3 removes the outside-block dilution, which follows
execution order and differs between the two orders. The claim stands for the
block-conditioned estimand and fails as written. The direct 25.504 (p 0.0045)
is also not familywise significant at the registered 0.01 level after three
readouts (Bonferroni 0.013), so S12 is unproven.

## Claims that hold under attack

- **Pasted (a).** The two jobs hold 128 iteration records (64 + 64). The lag-1
  autocorrelation of log(count+1/2) is -0.653137 in execution order (already
  retained) and +0.280039 in design order. The setting-identity Spearman is
  -0.075453 (retained) and the positional-join Spearman is -0.390040. The
  design-order +0.280 is not null itself: its asymptotic two-sided p is 0.025
  with sd 1/8 at n=64. It is not a parity artifact, since 28 of 63
  design-adjacent pairs share execution parity. The positional join pairs
  different settings, so its p of 0.0014 shows position-locked structure
  shared by both orders.
- **Pasted (c).** There are 638 `pub_*.json` files over 36 jobs, 4,586
  register descriptions, 31,145,280 stored bitstrings (36,226,688 bits) and
  2,116,928 aligned positions. Every register's length equals its PUB's
  `num_shots`. The counts are identical at `41d5ef0` and main.
- **Affine map (S04, S05).** The GLS chi-squares reproduce to the printed
  digits: 152.406/355.051, 138.859/316.065 and 44.450/97.225. The six-parameter
  affine map, however, saturates the six constant and 2-theta coefficients,
  with residual 0.0 there. Its statistic is therefore exactly the joint test
  that Xc4, Xs4, Yc4 and Ys4 vanish. The conformance design preregistered that
  support question (line 239) and records X cos(4 theta) 0.0143
  [0.0041, 0.0245] (line 839).
- **Direct sign-odd term (S06, S07).** The coefficients and radii reproduce.
  At each angle the + arms share one returned mesh and the - arms another, so
  within-configuration differences give an empirical per-setting variance
  with 10 degrees of freedom. Against that variance the sin(2 theta)
  coefficient has t(10) = -7.56 (job-00) and -16.54 (job-01). The replicate
  variance is 0.83 and 0.44 times the binomial value, so counting noise is
  not underestimated. The signal sits in mode 3 (-0.00901 and -0.01062), not
  in background mode 2 (-0.0006 and -0.0002), and it does not track the
  outside fraction.
- **Shift fits (S08, S09).** The fits reproduce: 45.239/39.564 and
  89.217/146.767. The implied epsilon is -0.0206 and -0.0219, so "about
  -0.022" matches job-01 only. The measured block X0+Xc2 is -0.02976 and
  -0.030679, which is negative as stated.
- **Repository counts (R01-R11).** Every count matches at `41d5ef0`: 18,277
  files, 225 claims, 414 bindings with 0 hash mismatches, 274 acquisitions,
  82 plans, 487 gates, 332 evidence files, 20 Rocq files, and the status
  split. Main reads 19,011, 233, 439, 276, 86, 491, 354 and 26. Reference
  integrity (dependencies, acquisitions, gates, documents, cycles) is clean
  at both revisions. The chapter 09 appendix rows are set-equal to the
  registry at the pin.
- **Model-table transcription (S16).** Every number spot-checked against
  `physical-models.json` at `f0f1788` matches within rounding.
- **Kingston detuning (C09).** The rounded inputs 1.130 rad and 4.392 us
  give 40,948 Hz, which looks like a rounding slip against the stated
  4.10e4 Hz. The retained `results/live/2026-10-15T030748.903241Z/coherence-analysis.json`
  holds rotation -1.1302658 rad and rate -0.2573465 rad/us, so
  |df| = 40,958 Hz, which rounds to 4.10e4 Hz. The chapter follows the
  unrounded source. The alias spacing of 227.69 kHz is correct.
- **Sum-rule counterexample (C01).** Exact arithmetic gives
  p+ = p- = 1/3 and residual -1/3. The mechanism is already in
  `docs/notes/quandela/bdsc-acceptance-diagnostics.md`.

## Opposition

- **Direct sign-odd term.** The strongest alternative is a configuration
  effect rather than a sign effect. Sign is aliased with compiled mesh, and
  job-01 re-ran job-00's 64 compiled circuits. The "replication" therefore
  repeats a property of two returned meshes per angle and is no prospective
  test of the sign symmetry. The coefficient was chosen after both jobs were
  inspected. The returned matrices predict statistics within 2.2e-4 of ideal,
  so the effect is physical or analyzer-side, and only an acquisition with
  several compilations per sign can attribute it to sign.
- **Affine rejection.** Any configuration-specific error over the five
  compiled angles creates fourth-harmonic content, and the grid aliases
  frequencies congruent mod 5 in 2 theta. The result excludes
  angle-independent affine calibration and nothing narrower.
- **Phase-command proxy.** The relation X0+Xc2 is one scalar inside an
  interval 0.035 wide. The retained static families already land inside it
  (-0.0217 to -0.0261) while failing transfer. Main's drive-linear heater
  family reaches standardized held-out 36.1/24.8 against the proxy's
  355.8/75.5. The proxy's failure therefore adds little.
- **PR #449 critiques (S17, S18).** Both were true at `f0f1788` and
  `41d5ef0`, and both are stale. Commit `7b5df53` (not an ancestor of
  `41d5ef0`) replaced the left-out column with training-only folds that start
  at zero and are scored in counting plus prediction variance
  (`configuration-holdout.json`).
- **Alternation model for the proposed experiments (C10).** Even and odd
  positions do not differ in mean outside fraction (Mann-Whitney p 0.49 and
  0.50), while lag-1 is -0.66 and -0.65. The high/low alternation slips phase
  several times per job, so the package's "fixed parity effect" factor is the
  wrong nuisance term. A design should cross the alternation phase or the
  predecessor transition and retain per-iteration timestamps.
- **Reproducibility receipt.** Rerunning `phase_command_proxy.py` with the
  same Python, NumPy and SciPy versions reproduces the selected fit and the
  summaries to 1e-6. Fold-level optimizer internals differ, for example fold
  25 start 0 takes 38 against 12 evaluations. The README's "identical except
  runtime metadata" therefore holds within one host only.
- **History row R13.** `ed4d793` entered through #443 and #447 registered its
  `parallel` import, as chapter 01 says. The #446 branch holds the single
  commit `f086e16`, and its diff touches no seed ledger. The seed-ledger
  changes before `41d5ef0` come from other merges (`87f9a07`, `27c9e0e`), so
  "#446 already registered three seed files" remains unproven.

## Scope cut

The review covers the README data claims, every numbered table and numeric
statement in chapter 04 sections 4-8, the repository counts of chapters 01,
08 and 09, chapter 07's data statements, and the pasted (a)-(c). It skips
about 45 narrative or purely mathematical items, which hold no repository or
data number:

| Location | Items skipped |
|---|---:|
| Chapter 01 reconciliation rows on algebra (germ bounds, Berlekamp-Massey, degree 196, Proposition 5) | 8 |
| Chapter 04 derivations (sections 1-3, 5.1 and 6.1 lemmas and formulas) | about 12 |
| Chapter 07 measurement identities, hierarchical scaffold, random-effects and timing formulas, heater successor model, rank-boundary sector, and five of six experiment-table rows | about 13 |
| Chapter 08 algebra replay counts (21,840 phase values and similar) and interpretive boundaries | about 12 |

Chapter 07's Tuna-17 and IQM numbers (C06, C07) were matched in the registry
by search, not recomputed from raw counts. No provider, QPU or QRNG service
was contacted. No file in the repository was changed beyond these two review
files.
