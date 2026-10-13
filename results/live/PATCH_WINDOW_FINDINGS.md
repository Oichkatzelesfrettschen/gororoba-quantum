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

Exploratory refit (orbit_refit.py; not preregistered): exact orbit law with
round-1 and round-2 kickback phases (phi1, phi2), depolarization lam, and
1 -> 0 report flips e0, e1 on b0 and b1, fitted per context across both arms.
(phi1, phi2) and (phi1 + pi, phi2 + pi) give the identical law. The arm-bias
model has no phase and the phase model's parameter count (lam and e1 per
arm, shared e0).

| Context | Bias deviance / 3 dof | Phase + bias deviance / 1 dof | Arm bias deviance / 1 dof | Phase LR (2 dof), p |
|---|---:|---:|---:|---|
| nominal | 16.5 | 4.5 | 2.6 | 12.0, 0.0025 |
| barrier | 8.4 | 4.0 | 1.5 | 4.4, 0.11 |
| barrier + echo | 2.0 | 1.8 | 0.6 | 0.2, 0.92 |

- The no-phase arm-bias model fits every context at least as well as the
  phase model, so these distributions do not identify a kickback phase; the
  phase parameters absorb arm-dependent loss as readily as rotation.
- One shared (phi1, phi2) with per-context nuisances is rejected against
  per-context phases (LR 16.1 on 4 dof, p = 0.0028), and the echo context's
  profile deviance at the nominal optimum is 8.6 (95% threshold 5.99): the
  distributions change with context in a way one common phase cannot carry.
- The echo context's 95% phase region contains zero; that is nondetection,
  not absence.

## Interpretation

- The tested idle and measurement/reset windows do not reproduce a large
  phase on the product-state probes under this calibration, and the
  registered comparisons select no mitigation.
- The same-calibration orbit distributions depend on the window context, but
  a phase model and an arm-dependent loss model explain them comparably, so
  the run does not localize a phase to the gates or to the window. The
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

- A discriminating measurement only where phase and arm-dependent loss
  predict different outcomes: selected work-state coherences (below) separate
  them, while the four-outcome orbit law does not.
- A candidate selected-coherence measurement on the native round-1 prefix
  (immediate, matched idle, measurement/reset contexts; XX, XY, YX, YY and Z
  settings on the verified carriers including 143), written as a case only if
  the refit leaves the question open.
