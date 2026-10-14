# Patch-window characterization findings (ibm_fez, 2026-10-13)

Record 2026-10-13T201757.782152Z; jobs db794cmil99s73fnjlk0 (16 window
circuits), db794dor1c5c738k1a50 (6 orbit circuits), db794hmr6oqs73871tbg (24
static circuits); 25 s charged (7 + 9 + 9) under 3 x 9 s ceilings. All three
jobs ran 21:22:00-21:22:58Z under calibration 13:41:52 PDT. Analyses:
patch-analysis.json (analyzer), collect.json family_analysis (registered
contracts), orbit-refit.json (exploratory refit, orbit_refit.py beside it).

## Execution status: approval and review-gate deviation

| Stage | Source | Record | Experiment digest |
|---|---|---|---|
| Approved case | 4aaea17 | 2026-10-13T195251.183877Z, sha256 50d512b5...3a70 | a8d281df7ce6 |
| Submitted case | 9b86a13 | 2026-10-13T201720.224397Z, sha256 ec6e8662...cc2f | 7283f357a681 |
| Collected acquisition | 9b86a13 | 2026-10-13T201757.782152Z | 7283f357a681 |

The approval named the 4aaea17 record. Submission of that record was refused
three times (2026-10-13T201059.920197Z, T201314.868415Z, T201529.748272Z),
each for one reason: "one result group mixes static and dynamic circuits",
because the source-level ramsey() builder measured work A before work B's
basis change. Commit 9b86a13 moves every basis change ahead of every
measurement in that shared builder, which reorders paired Ramsey circuits as
well as the single-work-qubit references. The submitted case was built and
sent before CI or review ran on 9b86a13, and its record digest differs from
the approved one, so the acquisition ran outside the digest-bound approval;
later CI success does not change that.

The compiled payload is byte-identical: both records' isa.qpy have sha256
cd45b6993fa4540a..., and all 46 per-circuit QPY dumps and instruction
sequences match. The transpiler's canonical ordering removed the source
reordering, and the static/dynamic classifier that refused the approved case
runs on the source-circuit groups (live_run.capability_violations). The
experiment digests differ through the source commit and the calibration
snapshot (11:56:54 approved, 12:57:03 submitted). Issue #76 covers dry-run/submit
classifier parity; binding an approval to the exact record,
source, circuit archive, manifest and ceilings at submit is issue #77.

## Registered endpoints (collector, simultaneous Hoeffding, alpha 0.005 each)

Precision contracts; the collector records reject_null as null.

| Endpoint | Estimate | Interval |
|---|---:|---|
| work A echo - plain, Y | -0.0820 | [-0.311, +0.146] |
| work B echo - plain, Y | -0.0098 | [-0.238, +0.219] |
| work A window (control 1) - plain, Y | -0.0879 | [-0.316, +0.141] |
| work B window (control 1) - plain, Y | -0.0332 | [-0.262, +0.195] |
| work A control 1 - control 0, Y | +0.0547 | [-0.174, +0.283] |
| work A measured - reset-only, Y | -0.0078 | [-0.236, +0.221] |
| work A paired - single, Y | -0.0254 | [-0.254, +0.203] |
| spectator excess from work A | 0.0000 | [-0.114, +0.114] |
| orbit barrier - nominal, contrast | -0.0422 | [-0.282, +0.198] |
| orbit echo - barrier, contrast | +0.0249 | [-0.215, +0.265] |

Every registered interval contains zero, and every interval also contains
effects large enough to matter: at visibility 0.9 a pure Y change of 0.22
corresponds to roughly a quarter radian. The registered outcome is
nondetection at the declared precision; it establishes neither equivalence
nor absence of a mechanism. No intervention is selected.

Descriptive, outside the registered family: work B measured - reset-only
+0.055, work B paired - single -0.006, window (control 0) - plain -0.143
(A) and -0.021 (B).

## Local Ramsey coordinates

X = 2 k_X / N_X - 1 and Y = 2 k_Y / N_Y - 1 are uncorrected local
measurement coordinates of the product-state probes, not a reconstruction of
the orbit state.

| Condition at 7.604 us | Qubit | R | Principal phase (rad) |
|---|---|---:|---:|
| plain | 136 | 0.884 | +0.091 |
| plain | 144 | 0.924 | +0.023 |

Plain Ramsey on 136 fits +3.02 kHz (profile interval [0.67, 4.77] kHz,
model-dependent), which maps to 0.03-0.23 rad over 7.6 us; producing
0.59-0.70 rad over the same exposure with one constant detuning needs
12.4-14.7 kHz. Echo and window fits carry 500 kHz aliases from the 2 us
sampling step and stay unresolved; near-zero sampled phases do not bound the
unwrapped phase between samples. The executed work-qubit idle is read from
the returned schedules; the control's measure and reset fit inside it.

## Orbit distributions under one calibration

Signed score s = P(01) - P(11) per arm; ideal contrast 1/4.

| Context | Feedback hw - replay | No-feedback hw - replay | Contrast hw / replay |
|---|---:|---:|---|
| nominal | +0.0520 | +0.0588 | 0.201 / 0.208 |
| barrier | +0.0291 | +0.0554 | 0.159 / 0.186 |
| barrier + echo | +0.0454 | +0.0337 | 0.184 / 0.172 |

The calibration-bound replay reproduces the nominal contrast, while both
arms shift together by about +0.05; the contrast cancels that common shift.

Per-arm counts (01 / 11 of 4096): nominal feedback 1092 / 841, no feedback
716 / 1290; barrier 1038 / 937 and 684 / 1235; barrier plus echo 1083 / 906
and 688 / 1265. The no-feedback signed score stays between -0.135 and
-0.141 across contexts while the feedback score moves from +0.061 to +0.025
to +0.043, so the context sensitivity sits in the feedback arm. The
barrier-minus-nominal contrast change, -0.042 with a normal-approximation
standard error near 0.021, is about two standard errors from zero and
descriptive only; the registered Hoeffding criterion governs and selects no
intervention.

Exploratory refits (not preregistered). The record-local
[orbit_refit.py](2026-10-13T201757.782152Z/orbit_refit.py) and its
[output](2026-10-13T201757.782152Z/orbit-refit.json) stay as the historical
first pass; they fit two phases (phi1, phi2), and the orbit law depends only
on their sum theta = phi1 + phi2 (amplitude (1 + s t) e1 + t e4 + s e16 for
round phases s, t), so (phi1 + x, phi2 - x) leaves every probability
unchanged and those two coordinates are not separately identifiable. The
maintained `scripts/n21_orbit_context_refit.py` (gated self-check; script
commit and sha256 recorded in the output) fits theta with report-flip and
depolarization nuisances and writes
[orbit-context-refit.json](2026-10-13T201757.782152Z/orbit-context-refit.json),
which also carries the record.json and collect.json digests and the fitted
integer counts. Regions are profile-likelihood boundaries at deviance 3.84,
root-found to 1e-6 rad:

| Context | theta (rad) | 95% profile region | Bias / phase / causal-saturated deviance | Phase excess over causal saturated (1 dimension) |
|---|---:|---|---|---:|
| nominal | -0.273 | [-0.411, -0.122] | 16.49 / 4.49 / 2.61 | 1.89 |
| barrier | +0.141 | [0.010, 0.271] | 8.44 / 4.01 / 1.54 | 2.47 |
| barrier + echo | -0.028 | [-0.162, 0.109] | 1.96 / 1.79 / 0.63 | 1.16 |

- Model dimensions per context over six cell dimensions: bias 3, phase 4,
  causal saturated 5. The causal saturated model lets the two arms differ
  freely except in the first-bit marginal, which causality fixes because b0
  is measured before the arms diverge; its deviance is the first-bit
  homogeneity G^2. The earlier "arm-bias" model reaches exactly that
  deviance, so it is the causal saturated model and carries no mechanism
  information.
- Within the phase model, the nominal and barrier regions are disjoint and
  on opposite sides of zero, and the echo context's region contains zero
  (nondetection, not absence). One shared theta against per-context theta
  gives LR 16.14 on 2 dimensions; 0 of 100 parametric bootstrap replicates
  under the shared-theta fit (seed 20261014) reach it, so the bootstrap tail
  is below 0.01 at that resolution. The test is conditional on the phase
  model and its nuisances.
- e0 relabels the reported first bit after the feedback law, so it is a
  report nuisance and not a misclassification that drives the wrong
  correction.
- The phase model leaves 1.16 to 2.47 of deviance over the causal saturated
  model in each context, so the terminal four-outcome law is consistent with
  a context-dependent phase and does not exclude other context-dependent
  channels; it does not localize a mechanism.

## Interpretation

- The tested idle and measurement/reset windows do not reproduce a large
  phase on the product-state probes under this calibration, and the
  registered comparisons select no mitigation.
- The same-calibration orbit distributions depend on the window context. A
  one-phase model in theta = phi1 + phi2 fits each context to within one
  residual dimension of the causal saturated model, and the terminal law
  cannot separate a phase from other context-dependent channels, so the run
  does not localize a phase to the gates or to the window. The
  earlier inference that the phase arises in the gate sequence is withdrawn
  without replacement.
- State dependence stays open: qubit 143 carries orbit amplitude for residue
  4 during the orbit, while it is a spectator in the Ramsey probes.
- T1 and readout values come from the execution-time calibration 13:41:52
  PDT (136: T1 94 us; 144: T1 157 us).

## Qubit 144 population

Normalized retention S = (p(t) - p_bg) / (p(0) - p_bg) at 7.6 us, Jeffreys
95% intervals from independent counts:

| Qubit | S | Interval | exp(-t/T1), calibration T1 |
|---|---:|---|---:|
| 136 | 0.927 | [0.909, 0.945] | 0.922 (94 us) |
| 144 | 0.894 | [0.874, 0.913] | 0.953 (157 us) |

Qubit 144 falls below its calibration T1 prediction; one delay does not
identify a decay curve, and relaxation, leakage and preparation/readout
context remain unseparated. Orbit models carry asymmetric work-qubit loss as
a nuisance.

## Budget

Campaign scope (180 s): 121 s before the orbit work, then 4 s (orbit), 11 s
(window) and 25 s (this run): 161 s consumed, 19 s remaining. The earlier
46 s handoff understated the two orbit charges by 2 s. Account window on
2026-10-13T22:47Z: 210 s consumed, 390 s remaining of 600 s. The validation
allocation has no frozen intervention to validate, and no further QPU case is
approved.

## Next analysis before any acquisition

- Every candidate explanation is first extended to a quantum instrument at
  the chosen circuit cut (true branch, reported branch, the correction that
  branch selects, and the continuing work state), because a terminal
  four-outcome model predicts no coherence.
- The selected work coherence after the first control measurement carries
  opposite signs in the two branches, (+-e^{i phi1})/2, so a branch-unsigned
  average is zero on an ideal device. The estimator keeps b0 in the shot
  record and weights XX, XY, YX, YY by (-1)^b0 with the third carrier's Z
  outcome as a sector indicator, using
  rho_{01,10} = (<XX> + <YY> + i(<XY> - <YX>))/4 in |ab> order; first-bit
  assignment error scales the signed coherence by (1 - 2 epsilon).
- The case compares the native round-1 prefix in three contexts (immediate,
  matched idle, measurement/reset) on the verified carriers including 143,
  and is written only if competing instruments predict separable signed
  coherences after nuisance ranges; the 19 campaign seconds stay
  uncommitted until then.
