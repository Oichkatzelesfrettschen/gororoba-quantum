# Idle-penalty stability repeat on ibm_kingston: written case

Status: approved by the owner on 2026-10-26 ("ok ping me when it's collected"), in reply to the plan of running
this repeat once Kingston's reported T1 and T2 refresh, with the dry run and this case as the conditions. The
approval covers the rule and bounds below; the binding record is the dry run made right after the refresh.

**Amendment of 2026-10-27.** Kingston's calibrations from 2026-10-27T01:05-07:00 on read qubit 155's readout
error at 0.219 against the 0.08 exclusion limit (`QUALITY["max_readout_error"]` in
`gororoba_quantum/live_run.py`), so `pinned_replicas` refused the path (155,154) at every calibration through
07:53. The owner chose on 2026-10-27 to drop that pair from the repeat and both focal jobs rather than wait on
the qubit. The repeat runs 30 ordered pairs (60 qubits): path 0 is still (150,149), so replica 0 and the campaign
digest are unchanged; the 60 qubits clear the comparator's 50-qubit floor; and `compare()` reads the second
run's cohort, so the dropped pair leaves the comparison. A validation dry run of the 30-pair pin under the
2026-10-27T07:53:14-07:00 calibration (not retained) admitted all 30 paths against a live export, passed
`--self-check` and carried campaign digest `bf6be296...`. Every count below refers to the amended cohort.

**Amendment of 2026-10-27: a two-point series.** Kingston's reported T1 and T2 still carried the
2026-10-26T07:32-07:00 stamp at the 2026-10-27T07:53:14-07:00 calibration, past the hour at which the daily
refreshes of 2026-10-10 to 2026-10-25 landed. The owner approved on 2026-10-27 running the repeat at once as the
first of two points:

- Point 1 runs under the current calibration with the first run's reported T1 and T2. It is admitted by the
  exposure gate, one execution calibration whose stamp differs from the first run's, and the `--compare`
  identity checks; decision 1's T1/T2 count reads "not admitted" by construction and is recorded, not applied.
  Both runs normalize against the same reported values, so each kappa ratio between them equals the ratio of
  the fitted physical rates: decision 2 reads as device drift over about 19 hours, and the two normalization
  outcomes under "What the outcomes mean" do not apply to this point.
- Point 2 runs after the refresh under decision 1 as written, compared against the first run, on the primary
  account when its remaining seconds less 60 cover the 25 s ceiling, else on the backup account.

Decisions 2 to 5 apply to both points, and the focal jobs run in point 1's calibration window.

Both points ran: point 1 on 2026-10-27 at 09:07 PDT, point 2 on 2026-10-27 at 17:07 PDT after the refresh that
Kingston's 16:36:38-07:00 calibration carried ([point 1](#results-point-1), [point 2](#results-point-2)).

## Question

The first run, Kingston job `dbfrg3fpc3tc739o4kag` ([findings](IDLE_PENALTY_PROBE_FINDINGS.md), case
[IDLE_PENALTY_PROBE_CASE.md](IDLE_PENALTY_PROBE_CASE.md)), measured per-qubit idle multipliers and a readout-time
phase rate on 31 ordered coupled pairs under the 2026-10-26T14:25:32-07:00 calibration. Its question (d) asks
whether those values hold across a calibration. This repeat runs the identical campaign on 30 of
those ordered pairs (the amendment above drops (155,154)) under a calibration whose reported T1 and T2 have been remeasured, and compares the two runs with
`scripts/idle_penalty_report.py --compare`.

A remeasured T1/T2 is required because kappa normalizes against the reported values: a calibration stamp that
carries the first run's T1 and T2 forward (the 15:18 and 16:30 stamps of 2026-10-26 changed none of the 62) tests
two-hour physical drift only, and cannot separate drift of the device from drift of its reported normalization.

## Why a simulation cannot answer it

Aer draws from the reported T1, the echo T2 and the assignment errors. It holds no free-evolution T2*, no readout
phase rate and no history across calibrations, so a stability comparison of measured multipliers exists only on
the device. The dry run's self-check (`--self-check`) confirms the analyzer reads the noise model's own values as
kappa near 1 with no readout effect, the null each measured value is read against.

## Design

The campaign, members, ladders and analyzer are those of the first run: 44 two-qubit members, one dynamic job,
4096 shots, 20 us repetition delay, twirling off, dynamical decoupling none, isolated reference off. Branch
`heron/idle-penalty-repeat` adds one runner change: `idle_penalty` is pin-capable (`PIN_CAPABLE_CAMPAIGNS` in
`gororoba_quantum/live_run.py`), and a pinned run must carry `--max-replicas` equal to its path count. The pin
fixes each pair's orientation, so qubit 150 is the target and 149 the spectator, as in the first run:

```text
ibm_kingston:150,149/21,36/141,140/105,117/16,3/94,95/57,47/1,0/44,45/14,13/82,81/33,32/90,89/74,73/49,50/77,65/144,145/71,70/109,110/132,133/61,62/59,55/19,35/27,28/97,107/6,7/11,18/101,100/130,129/96,103
```

`pinned_replicas` refuses the plan when any path has an excluded qubit or edge, or sits one CZ hop from another
path. The repeat then runs at the next calibration that admits all 30 paths. It substitutes no path, because a
replacement pair has no first-run value to compare; the one dropped pair is the owner's amendment above.

The runner change moves the full experiment digest. The comparator binds the campaign instead: `campaign_digest`
hashes replica 0's per-role ISA instruction sequences (the CZ-kick anchor excluded, since a pinned compile commutes
the partner's X through the CZ). Both pinned validation dry runs on this branch, the first run and its approved
dry run share one campaign digest.

## Backend, account, shots and seconds

- Backend: ibm_kingston (Heron r2), pinned.
- Account: primary (default saved account). It held 101 s at the last read against a 60 s reserve floor; a fresh
  usage read precedes the dry run and the submit, and the run proceeds only if the remaining seconds less 60
  cover the 25 s ceiling.
- Shots: 4096 per PUB, 44 PUBs, one job.
- Expected charge: 16 s, the first run's billed seconds for the identical job shape. Ceiling 25 s per job and in
  total.
- Expected credits: none beyond the plan's QPU seconds.
- Seeds: `--seed-transpiler` and `--seed-simulator` take two fresh values from a new ANU draw, because the repeat
  is an independent replicate. The pin fixes placement. The dry run's campaign digest must equal the first
  run's before the submit, and `--compare` refuses two reports whose digests differ.

**No automatic fallback.** A 50 us run cannot enter `--compare` with the first run, because the repetition delay
is part of the compared identity, so it cannot answer the stability question. If the 20 us job ends with a service
error and zero circuit execution time (the signature of `results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md`), the
repeat stops and the failure goes to the owner; a 50 us run needs its own case.

## Preregistered decisions

Fixed before the repeat's data:

1. **Admission.** The repeat's report passes the exposure gate and runs under one execution calibration whose
   reported T1 and reported T2 each differ from the first run's on at least 30 of the 60 qubits. Kingston
   refreshes both together: in the daily refreshes of 2026-10-10 to 2026-10-25, T1 moved on 147 to 155 qubits and
   T2 on 152 to 154 at the same stamp. `--compare` admits the pair only with
   equal campaign digest, shots, ladders, repetition delay and execution policy, distinct calibration and
   collection, all 60 qubits on their first-run role and partner, and at least 50 fitted qubits per multiplier.
2. **Multiplier stability** (the `compare()` rule, unchanged): for each of kappa_1, kappa_2* and kappa_2e,
   "stable" when the per-qubit values correlate at Pearson r of at least 0.5 and the order-statistic 95% interval
   of the median second/first ratio lies inside [0.8, 1.25]; "drifted" when that interval lies wholly outside;
   otherwise "unresolved".
3. **Single-run decisions replicate** when the repeat's report reads the first run's verdicts: optimistic_t1
   "absent or unresolved", echo_gain "present", readout_shift "present" with a negative mean in both contrasts.
4. **Visibility, repaired.** The first run's visibility "present" rested on the chi-square alone. For the repeat,
   a cohort-mean visibility loss is claimed only when both contrasts' pair-mean t statistics (`vs_after.t`,
   `vs_quiet.t` in `pooled.readout_dephasing`) fall below the one-sided alpha 1e-3 quantile of t on 29 degrees of
   freedom (-3.396) and the quiet null reads other than "present". A "present" from the chi-square alone reads
   "pairwise heterogeneity", which establishes departures that differ from pair to pair and no mean loss.
5. **Pair pattern of the readout shift.** Over the 30 pairs, the Pearson correlation of `shift_khz` between the
   two runs at 0.5 or more reads "pair pattern stable"; below 0.5 with both runs "present" reads "effect stable,
   pattern not".

`scripts/idle_penalty_repeat_decisions.py` computes decisions 1 and 3 to 5 from the two reports, and
`--compare` computes decision 2.

What the outcomes mean:

- Stable multipliers with remeasured T1/T2 establish that this cohort's idle penalties are a property of the
  qubits across one calibration, so a noise model can carry them per qubit.
- A kappa that moves while the fitted physical rate (Gamma_1, 1/T2*, 1/T2e in the reports) holds, and the
  reported T1 or T2 moves, locates the drift in IBM's reported normalization.
- A kappa that moves together with its physical rate locates the drift in the device.
- Readout endpoints that move while every multiplier holds localize the change to the readout environment.

## Binding records

Point 1 comes from the dry run made under the 07:53 calibration of 2026-10-27, point 2 from the dry run made
after the T1/T2 refresh:

| Field | Point 1 | Point 2 |
|---|---|---|
| Dry run | `results/live/2026-10-27T155934.096853Z` | `results/live/2026-10-28T000211.008810Z` |
| record.json sha256 | `eec53fb559e794b6b9853ada5940ed0568a8e4cca0dcdb2ea7d02f21c5bcba86` | `98b4371a2e13198490810328675b69653c8dd5ad88ca6cd3b0855f56544e817a` |
| Planning calibration | 2026-10-27T07:53:14-07:00, fingerprint `e983c383c927b0c4...` | 2026-10-27T16:36:38-07:00, fingerprint `c08add92e94f75d4...` |
| Submitted run | `results/live/2026-10-27T160530.294787Z`, job `dbgcnp5rd2mc73cuf5p0`, primary | `results/live/2026-10-28T000644.379196Z`, job `dbgjpg1q260s73bte67g`, backup (the primary held 68 s, and 68 less 60 falls below 25) |
| Execution calibration | 2026-10-27T09:07:55-07:00, reported T1 and T2 of 2026-10-26T07:32-07:00 | 2026-10-27T16:56:11-07:00; its reported T1 differs from the first run's on 58 and T2 on 60 of 60 qubits |
| Charge | 16 s, 101 s remaining before the submit | 16 s, 176 s remaining on the backup before the submit |
| Seeds | ANU `docs/evidence/anu_qrng/draw-2026-10-27T155928Z.json` indices 0 and 1 | the same draw, indices 8 and 9 (first seed pair; every check passed) |
| Campaign digest | `bf6be296...`, the first run's | must equal `bf6be296...` |
| Placement | all 30 pinned paths admitted, checked against a fresh live export | same check |
| Policy | 4096 shots, rep_delay 20 us, ceiling 25 s per job and in total, no isolated reference, no DD, no twirl | same |

If the calibration values move before the submit, the submit writes `approval_required` and sends nothing; the
dry run is remade with the identical flags and submitted under this approval.

## Results, point 1

Job `dbgcnp5rd2mc73cuf5p0` executed under the 2026-10-27T09:07:55-07:00 calibration, which carried the first
run's reported T1 and T2 on all 60 qubits, so each kappa ratio below is the ratio of fitted physical rates across
about 19 hours. The reports are `idle-penalty-report.json`, `idle-penalty-compare.json` and
`idle-penalty-repeat-decisions.json` in `results/live/2026-10-27T160530.294787Z/`; the exposure gate and the
`--compare` identity checks passed.

1. **Admission**: T1 moved on 0 and T2 on 0 of 60 qubits, "not admitted" by construction; recorded, not applied.
2. **Multiplier stability**: "unresolved" on all three. Every median-ratio interval lies inside [0.8, 1.25] and
   every Pearson r falls below 0.5.

   | Multiplier | Pearson r | Median second/first ratio [95%] | Verdict |
   |---|---|---|---|
   | kappa_1 | 0.195 | 0.939 [0.836, 1.052] | unresolved |
   | kappa_2* | 0.357 | 0.906 [0.801, 0.998] | unresolved |
   | kappa_2e | 0.318 | 0.961 [0.840, 1.028] | unresolved |

3. **Single-run decisions replicate**: optimistic_t1 "absent or unresolved", echo_gain "present", readout_shift
   "present" with mean -2.627 kHz (se 0.557) against the after-readout arm and -2.632 kHz (se 0.557) against the
   quiet arm.
4. **Visibility** reads "pairwise heterogeneity" in both runs: the repeat's pair-mean t statistics are -2.48 and
   -2.28 against the -3.396 threshold.
5. **Pair pattern** of the readout shift: Pearson r 0.988 over 30 pairs, "pair pattern stable".

The focal jobs ran minutes later in the same calibration window and reproduce one another's multipliers at Pearson
r 0.91 to 0.99 with median ratios from 0.97 to 1.06 ([focal decision 4](IDLE_PENALTY_FOCAL_CASE.md#results)). Against
that test-retest floor, the cross-day r of 0.20 to 0.36 measures drift of the per-qubit physical rates while the
cohort medians hold within 10 %. A post hoc check, outside the preregistered rule, rules out leverage by a few
qubits: Spearman rank correlations are 0.38, 0.52 and 0.43, and leaving out the region qubits 73, 94 and 95 gives
Pearson 0.23, 0.37 and 0.36. The first run's heavy tail regressed toward the cohort: qubit 144 read kappa_1 5.54
on the first run and 1.16 on the repeat, and qubit 47 read kappa_2* 5.43 and 2.56. Over these 19 hours a per-qubit
multiplier carries only within one calibration window. Point 2 asks whether the same holds when the reported
normalization is remeasured; it finds the cohort medians 12 to 13 % below the first run's 28 hours on, so a cohort
multiplier carries across a day only to within that margin.

## Results, point 2

Job `dbgjpg1q260s73bte67g` executed under the 2026-10-27T16:56:11-07:00 calibration. The reports are
`idle-penalty-report.json`, `idle-penalty-compare.json` and `idle-penalty-repeat-decisions.json` in
`results/live/2026-10-28T000644.379196Z/`; the exposure gate and the `--compare` identity checks passed.

1. **Admission**: reported T1 moved on 58 and T2 on 60 of 60 qubits against the first run, "admitted".
2. **Multiplier stability**: "unresolved" on all three. Every Pearson r falls below 0.5, and every median-ratio
   interval reaches below 0.8.

   | Multiplier | Pearson r | Median second/first ratio [95%] | Verdict |
   |---|---|---|---|
   | kappa_1 | -0.041 | 0.872 [0.705, 0.974] | unresolved |
   | kappa_2* | 0.339 | 0.876 [0.683, 1.061] | unresolved |
   | kappa_2e | -0.043 | 0.869 [0.719, 1.008] | unresolved |

3. **Single-run decisions replicate**: optimistic_t1 "absent or unresolved", echo_gain "present", readout_shift
   "present" with mean -2.662 kHz (se 0.566) against the after-readout arm and -2.675 kHz (se 0.560) against the
   quiet arm; its quiet null reads -0.013 kHz (se 0.022), "absent".
4. **Visibility** reads "pairwise heterogeneity" in both runs: the pair-mean t statistics are -2.39 and -1.93
   against the -3.396 threshold.
5. **Pair pattern** of the readout shift: Pearson r 0.987 over 30 pairs, "pair pattern stable".

The readout endpoints hold across both points and the refresh: the shift's cohort mean stays within 0.04 kHz of
point 1's and its pair pattern at r 0.99, so the readout Stark shift is a fixed property of each reader-probe pair
on this cohort.

The low multiplier correlations come from neither fit noise nor leverage. Within each run, the reliability of every
kappa (one minus the mean squared fit error over the between-qubit variance) is 0.93 or more, and the focal jobs
reproduce the multipliers at r 0.91 to 0.99 within one window. A post hoc check, outside the preregistered rule,
finds Spearman rank correlations of -0.01, 0.27 and -0.02 against the first run, Pearson -0.05, 0.34 and -0.05
with region qubits 73, 94 and 95 left out, and no single left-out qubit that lifts any r above 0.42.

A second post hoc comparison applies the `compare()` statistics to the fitted physical rates (Gamma_1 =
kappa_1 / T1_reported, 1/T2* = kappa_2* / T2_reported, 1/T2e = kappa_2e / T2_reported) and to the reported values
themselves, over the same 60 qubits:

| Quantity | Point 2 against the first run: r, median ratio [95%] | Point 2 against point 1: r, median ratio [95%] |
|---|---|---|
| Gamma_1 | 0.444, 0.841 [0.757, 0.951] | 0.632, 0.954 [0.843, 1.047] |
| 1/T2* | 0.697, 0.868 [0.744, 0.987] | 0.696, 0.958 [0.863, 1.014] |
| 1/T2e | 0.665, 0.853 [0.771, 0.946] | 0.806, 0.952 [0.851, 0.997] |
| reported T1 | 0.511, 0.943 [0.855, 1.003] | 0.511, 0.943 [0.855, 1.003] |
| reported T2 | 0.742, 0.996 [0.882, 1.070] | 0.742, 0.996 [0.882, 1.070] |
| kappa_1 | -0.041, 0.872 [0.705, 0.974] | -0.106, 0.924 [0.724, 1.014] |
| kappa_2* | 0.339, 0.876 [0.683, 1.061] | 0.377, 0.972 [0.804, 1.135] |
| kappa_2e | -0.043, 0.869 [0.719, 1.008] | -0.083, 0.894 [0.803, 1.037] |

Point 1 carried the first run's reported values, so its reported-T rows against point 2 equal those of the first
run. Two readings follow, both post hoc and of moderate confidence:

- The device drifted. The cohort's fitted decay rates fell by 13 to 16 % between the first run and point 2, and the
  Gamma_1 and 1/T2e intervals lie wholly below 1, so the qubits relaxed and dephased more slowly on the evening of
  2026-10-27 than on the afternoon of 2026-10-26. The kappa medians fell with them.
- The reported normalization adds per-qubit variance. Between point 1 and point 2, 8 hours apart, the fitted rates
  keep their per-qubit pattern at r 0.63 to 0.81 with intervals inside [0.8, 1.25], which the `compare()` rule
  reads "stable" on all three, while the multipliers normalized by the refreshed T1 and T2 fall to r -0.11 to 0.38.
  The reported T1 itself repeats at only r 0.51 across the refresh. "What the outcomes mean" locates drift in the
  normalization when the physical rate holds, and the case fixed no numerical rule for "holds": the point 1 to
  point 2 rows meet the `compare()` rule, and the first-run to point 2 rows do not.

A noise model therefore carries per-qubit fitted rates across a same-day calibration refresh, and a cohort
multiplier across a day only to within about 15 %; a multiplier scaled by IBM's reported T1 or T2 keeps no
per-qubit information across a refresh. A third point under a further refresh in which the fitted rates again read
"stable" against point 2 while the multipliers do not would raise the normalization reading, and fitted rates that
lose their per-qubit pattern there would lower it.

## Commands

From `gororoba_quantum/`, with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `PYTHON` exported, `PIN`
the pin string above and `D` the new ANU draw (seed values at indices 0 and 1):

```sh
"$PYTHON" live_run.py --groups idle_penalty --backends ibm_kingston --max-pending 300 --shots 4096 \
  --rep-delay 0.00002 --no-isolated-reference --max-execution-seconds 25 --max-total-execution-seconds 25 \
  --reserve-seconds 60 --pin-layout "$PIN" --max-replicas 30 \
  --seed-transpiler "qrng:$D#0" --seed-simulator "qrng:$D#1" --out ../results/live
"$PYTHON" calibration_snapshot.py --export ibm_kingston --out SNAPSHOT
"$PYTHON" ../scripts/idle_penalty_report.py RUN --self-check --check-placement --snapshot SNAPSHOT
"$PYTHON" live_run.py ... (the same flags) --submit --approved-record RUN --approved-record-sha256 SHA
"$PYTHON" live_run.py --collect RUN_SUBMITTED
"$PYTHON" ../scripts/idle_penalty_report.py RUN_SUBMITTED --out RUN_SUBMITTED/idle-penalty-report.json
"$PYTHON" ../scripts/idle_penalty_report.py --compare FIRST/idle-penalty-report.json \
  RUN_SUBMITTED/idle-penalty-report.json --out RUN_SUBMITTED/idle-penalty-compare.json
"$PYTHON" ../scripts/idle_penalty_repeat_decisions.py FIRST/idle-penalty-report.json \
  RUN_SUBMITTED/idle-penalty-report.json --out RUN_SUBMITTED/idle-penalty-repeat-decisions.json
```
