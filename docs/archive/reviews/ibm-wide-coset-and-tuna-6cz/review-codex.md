# Codex review: IBM wide cosets and Tuna-17 six-CZ null blocks

## Scope and verdict

The reviewed artifact is a claim-registry and scientific-prose change over retained IBM Heron r2 and Quantum Inspire
Tuna-17 records, with exact Cayley-Dickson censuses and a Rocq proof as supporting material. The review covers the full
`origin/main...HEAD` diff except the review brief, both new claims, every file pinned by those claims, the rule-producing
source, the retained parallel-coset comparison, and the named proof artifacts.

No claim falsifier survives review. Every number stated by the two registry claims matches the pinned record at the
claim's displayed precision. The wide-coset rule table reproduces byte for byte; ibm_kingston passes 23 of 23
single-device rules, ibm_fez fails exactly the eight named rules, and all six cross-device rules pass. The Tuna-17 rule
stops at `unresolved_batch` before any mechanism class. The algebraic statements use the right evidence classes: finite
censuses are computed, the mixed-pair recurrence has a disclosed paper proof rather than a Rocq proof, and half-fold
doubling has explicit Rocq theorem artifacts. One nonblocking reproducibility defect remains: a Tuna-17 regeneration changes
floating-point least-significant digits and therefore does not reproduce the pinned analysis bytes.

## Findings, ranked by consequence

### SOUND, measured and computed: both registry statements reproduce their records

The wide claim reports 12 PUBs, 18,816 shots and 9 billed seconds on ibm_fez, and 21,888 shots and 11 billed seconds on
ibm_kingston. The retained plans record 12 execution PUBs and those shot counts
(`results/live/2026-11-07T153325.440007Z/record.json:98,660-674` and
`results/live/2026-11-07T153325.886771Z/record.json:91,618-632`); the collectors record 9 and 11 final charge seconds
(`results/live/2026-11-07T153325.440007Z/collect.json:6034-6037` and
`results/live/2026-11-07T153325.886771Z/collect.json:5698-5701`). The reported target, null and mutation readings match
the analysis statistics (`results/live/pathion_wide_coset_analysis.json:1605-1666,1677-1702,3231-3292,3303-3328`).

The Tuna-17 claim reports 19 batches, 56 jobs and 2,293,760 shots. Summing `length(circuits) * shots` over the 19 retained
`cases.json` files returns exactly those three values. The two base replicates, every chi-square and every pooled value
match `results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json:184-232`; the secondary terminal-assignment
calibration matches lines 114-180. The QX record contains 12 passing arms at factor 2.0
(`results/quantum_inspire/pathion_one_cz_null_qx_analysis.json:10-74`). The eight claim-pinned SHA-256 values also match
the current bytes. The prose has done the unglamorous but essential job of copying numbers without inventing new ones.

### SOUND, computed from measured records: the wide rule counts and failures are exact

The replay command

```text
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3 \
  scripts/pathion_wide_coset_analysis.py \
  results/live/2026-11-07T153325.440007Z \
  results/live/2026-11-07T153325.886771Z \
  --out /tmp/pathion_wide_coset_analysis.review.json
```

returns the expected scientific status 1 because one device fails rules, and `cmp` returns 0 against the retained JSON.
The analysis source defines all differences as target minus the named control
(`scripts/pathion_wide_coset_analysis.py:341-348`), defines the 23 single-run rules at lines 381-430, and defines the six
device-agreement rules at lines 433-443. The retained table gives ibm_fez's eight failures at
`results/live/pathion_wide_coset_analysis.json:1421,1453-1565`, ibm_kingston's 23 passing entries at lines 3008-3197,
and the six passing device comparisons at lines 3342-3390. `changed_verdicts` is empty, so the covariance and
independent-placement interval models change no decision.

### SOUND, proved arithmetic over measured values: the difference failures add no independent fez departure

The ibm_fez values satisfy

```text
28.602326 = 28.071373 - (-0.530953)
61.033916 = 59.977929 - (-1.055987)
```

up to the analysis record's six-decimal serialization. The target rules pass, while both null controls and both
target-minus-null rules fail. The record therefore supports the bounded interpretation that the two difference failures
restate the null-control offsets for this run. Equality alone would not make two differently banded rules logically
equivalent on every possible input; the passing target readings and the observed magnitudes supply the missing
case-specific premise. The branch boundary states that premise at `docs/state/research_state.json:15448`.

### SOUND, computed from a preregistered rule: Tuna-17 decides only `unresolved_batch`

The decision source evaluates all eight replicate heterogeneity statistics before every mechanism class
(`scripts/qi_pathion_one_cz_null_cases.py:841-890`). The preregistered case sets the replicate bound to 10.83 and states
that a violation returns an unresolved result
(`results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/CASE.md:101-128`). The retained `b0/base` statistic is
34.8597, so later near-zero six-CZ values never reach the `zero` branch. The retained decision explicitly records
`decided=false`, `label=unresolved_batch`, and an unchanged ledger row
(`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json:184-232`). The terminal-assignment calibration is
secondary and cannot rescue a decision vetoed by batch heterogeneity. The claim correctly leaves coin-conditioned
dropout and post-schedule q12 correlation open (`docs/state/research_state.json:15495`).

### SOUND, computed and proved: the 64D/128D implications use the right evidence classes

- **Computed.** The D = 32 census contains nullities 0, 4, 8 and 12 over 930 operands
  (`docs/evidence/pathion-kernel-map/census.json:1-20`). The D = 64 census contains every multiple of four from 0 through
  28 over 3,906 operands, and the D = 128 census contains every multiple of four from 0 through 60 over 16,002 operands.
  Both wide censuses record equality between the aligned-pair count and the `cd_core` integer-rank nullity
  (`docs/evidence/pathion-kernel-map/census-wide.json:16-45,55-76`). The maxima 12, 28 and 60 obey `n -> 2n + 4`.
- **Paper proof plus computation.** The mixed-pair argument derives
  `n_2h = h - 4 - 2 n_h` from the associator-sign census and derives the maximum `D/2 - 4`
  (`docs/notes/singular_sector_dynamics.md:90-119`). `proofs/CdHalfFold.v:43-60` explicitly labels the recurrence as an
  open Rocq statement and names the missing sign identity. The branch says “paper proof,” not “formal proof.”
- **Proved.** `RealHalfFoldDimension.half_fold_dimension_low` and `half_fold_dimension_high` prove that a basis of an
  `n`-dimensional kernel gives a basis of dimension `n+n` after either half embedding
  (`proofs/CdHalfFold.v:232-253`); both theorems end in `Qed`. The rank corollary appears at lines 255-261.
- **Computed boundary.** The measured targets `e1 + e36` and `e4 + e72` are mixed pairs, not half embeddings
  (`gororoba_quantum/pathion_wide_coset.py:85-93`). The ibm_fez run also executes one D = 32 reference *block* of the
  null operand `e1 + e17` (`gororoba_quantum/pathion_wide_coset.py:25-29,50-52,156-160`), but that nullity-zero block
  measures no component, dimension, closure, kernel bundle or attachment of an A_5 real-coefficient locus. The precise
  “no A_5 stratum” boundary therefore holds; a broader claim that the run contains no A_5 circuit would be false.

### SOUND, computed: the registry check leaves exactly the named acquisition

`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3 scripts/research_state.py --check` exits 0 and prints
`unclaimed acquisitions (1): qd-sim-ascella-signed-coherence-job-02-sim-replay`. Both
`python3 scripts/results_index.py claim ...` invocations exit 0. Claim 6 holds exactly.

### SLOPPY, computed, nonblocking: Tuna-17 regeneration is scientifically stable but not byte-stable

Regenerating the Tuna-17 analysis from all 19 retained run directories produces the same keys, strings, booleans and
decision, but `cmp` returns 1. A recursive comparison finds 186 floating-point differences, maximum absolute difference
`1.780e-14`, maximum relative difference `1.058e-12`, and zero structural differences. The QX regeneration is
byte-identical. The numerical drift changes none of the claim's displayed values or decisions, so it does not falsify
either claim; it does mean the pinned Tuna analysis cannot serve as a byte-reproducible derived artifact under the
current numerical execution. A deterministic serializer with explicit rounding, or a pinned numerical reduction path,
would make future digest-bound regenerations defensible.

## Setting-by-setting comparison with the retained parallel-coset pair

The values below are readout-corrected whole-setting estimates, listed as `ibm_fez / ibm_kingston`. The parallel values
come from `results/live/pathion_parallel_coset_analysis.json:570-703,1432-1565`; the wide values come from
`results/live/pathion_wide_coset_analysis.json:1605-1702,3231-3328`.

| Program | Setting and ideal | Measured fez / kingston | Rule-level comparison |
|---|---|---:|---|
| Parallel A_5 | `e1 + e17`, 0 | +0.009 / -0.077 | Whole-operand band passes; kingston's per-placement one-CZ null rule fails |
| Parallel A_5 | `e1 + e26`, 4 | 4.074 / 4.082 | Nullity band passes |
| Parallel A_5 | `e2 + e27`, 4 | 4.027 / 4.081 | Nullity band passes |
| Parallel A_5 | `e1 + e10`, 8 | 8.006 / 7.964 | Nullity band passes |
| Parallel A_5 | `e1 + e18`, 12 | 11.981 / 11.985 | Nullity band passes |
| Parallel A_5 | `e1 + e24`, 12 | 11.973 / 12.008 | Nullity band passes |
| Parallel A_5 | `e17 - e2`, 12 | 11.974 / 12.010 | Twin nullity band passes |
| Parallel A_5 | cocycle-free `e1 + e18`, -2 | -1.943 / -1.958 | Mutation band passes |
| Wide A_6 | `e1 + e33`, 0 | -0.531 / -0.238 | Fez fails; kingston passes the 0.4 band |
| Wide A_6 | `e1 + e36`, 28 | 28.071 / 27.995 | Both targets pass |
| Wide A_6 | cocycle-free `e1 + e36`, -2 | -2.074 / -2.035 | Both mutations pass |
| Wide A_7 | `e1 + e65`, 0 | -1.056 / -0.534 | Fez fails; kingston passes the 0.8 band |
| Wide A_7 | `e4 + e72`, 60 | 59.978 / 60.126 | Both targets pass; fez resolves 127 of 128 signs |
| Wide A_7 | cocycle-free `e4 + e72`, -2 | -2.123 / -1.966 | Both mutations pass |

The parallel pair passes its packed-minus-isolated k0 crosstalk rule on both devices: -0.00415 with 90 percent interval
[-0.00897, 0.00066] on fez and -0.00183 [-0.00822, 0.00455] on kingston
(`results/live/pathion_parallel_coset_analysis.json:773-786,1635-1648`). The wide run has no corresponding isolated
control for every placement. Its fez copy comparisons instead expose large placement-systematic discrepancies, z =
-11.42 for n64 and -5.61 for o64 (`results/live/pathion_wide_coset_analysis.json:410-421`). The two programs therefore agree
on target and mutation realization while disagreeing sharply on whether fez's wide null placements behave uniformly.

## Systematic effects the analyses do not separate

| Effect | What the records measure | Remaining separation failure |
|---|---|---|
| Calibration drift between PUBs or batches | The wide covariance uses aligned shots inside one PUB; Tuna-17 has bracketed batches and flags five shifts above 0.02, all on q11 | Wide target, null and mutation arms occupy separate PUBs, so inter-PUB drift is absent from the covariance. Tuna-17 batch 15 changes q11 `e10` from 0.095 to 0.434, but temporal coincidence does not identify causation. |
| Readout correlation | Wide records invert per-qubit confusion matrices; Tuna-17's eight X-only preparations classify terminal-assignment coin dropout and q12 correlation as small | A factorized readout inverse does not identify correlated assignment. Tuna's X-only calibration does not reproduce the template's CZ and X90 schedule, so a schedule-conditioned q12 correlation remains open. |
| Crosstalk across placements | The parallel pair measures one packed-minus-isolated setting and passes. Wide shot covariance finds negligible stochastic co-movement. | Wide circuits run all placements concurrently and lack an isolated replay per placement. The fez copy failures and low visibility can arise from local qubit quality, coherent crosstalk, or time-local calibration; shot covariance cannot distinguish static mechanisms. |
| Two-level-system defects | The wide run localizes loss to two physical placements during one calibration | The records contain neither spectroscopy, a time series, nor a reroute of the same block. A two-level-system defect remains observationally equivalent to another local transient defect. |

## Record-supported conjectures and falsifiers

- **Hypothesis, moderate confidence:** the fez wide loss follows the physical qubits of placements 7 and 15 rather than
  block `k28`. A rerun that moves `k28` to other qubits and preserves the loss on `k28` falsifies the hypothesis. The
  present two-placement evidence appears at `docs/evidence/pathion-kernel-map/README.md:91-95`.
- **Hypothesis:** q11 readout drift causes the Tuna-17 `b0/base` heterogeneity. A repeat with per-batch q11 admission
  whose b0 replicates still exceed chi-square 10.83 falsifies the hypothesis
  (`docs/state/research_state.json:15495`).
- **Hypothesis:** the positive kingston A_7 target offset is the N_b = 3 local output-bit bias seen in the retained
  parallel/wide estimator audit. A wide repeat whose target offset takes the null controls' sign, or a channel-corrected
  analysis that removes the predicted N_b = 3 bias without moving the null, falsifies the hypothesis
  (`docs/state/research_state.json:15448`; `docs/evidence/pathion-kernel-map/nhat-bias/README.md:189-204`).
- **Hypothesis:** the two bad fez placements reflect a time-local device defect, including a possible two-level system,
  rather than concurrent-placement crosstalk. An isolated replay that recovers visibility while the simultaneous replay
  fails falsifies the local-defect version; repeated loss on the same qubits after rerouting different blocks supports
  it. The current record decides neither branch.

## Final verdict

The branch earns its two claims. The records support every displayed number, the preregistered rules produce the stated
decisions, and the prose separates measurement, finite computation, paper proof, Rocq proof and hypothesis with unusual
care. The most important scientific boundary is also present: the IBM targets validate a compiled sign-network
instrument whose forced blocks supply most of each total; they do not test the nullity growth law or any A_5 stratum.
The Tuna-17 record reports useful numbers but establishes only batch heterogeneity. The least-significant-digit drift in
the Tuna regeneration deserves a reproducibility repair, but it changes neither claim, interval, class nor verdict.
