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

## Question

The first run, Kingston job `dbfrg3fpc3tc739o4kag` ([findings](IDLE_PENALTY_PROBE_FINDINGS.md), case
[IDLE_PENALTY_PROBE_CASE.md](IDLE_PENALTY_PROBE_CASE.md)), measured per-qubit idle multipliers and a readout-time
phase rate on 31 ordered coupled pairs under the 2026-10-26T14:25:32-07:00 calibration. Its question (d) asks
whether those values hold across a calibration. This repeat runs the identical campaign on the identical 31
ordered pairs under a calibration whose reported T1 and T2 have been remeasured, and compares the two runs with
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

Filled from the dry run made after the T1/T2 refresh:

| Field | Value |
|---|---|
| Run directory | pending |
| record.json sha256 | pending |
| Calibration | pending |
| Campaign digest | must equal `bf6be296...`, the first run's |
| Placement | all 30 pinned paths admitted, checked against a fresh live export |
| Policy | 4096 shots, rep_delay 20 us, ceiling 25 s per job and in total, no isolated reference, no DD, no twirl |

If the calibration values move before the submit, the submit writes `approval_required` and sends nothing; the
dry run is remade with the identical flags and submitted under this approval.

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
