# IQM Emerald idle schedule and per-qubit decay

Status: written case awaiting the owner's approval; nothing submitted.

Backend `iqm:emerald` (Crystal 54, chip M216 variant H03, pay-as-you-go 0.75 credits per second). Calibration copy
retained for planning: set `3a1a9ad0-0c98-49db-8cf5-7623d13729f4`, read 2026-10-22
([dynamic architecture](../../../../docs/evidence/iqm/qc/emerald/calibration/dynamic-quantum-architecture.json),
[metrics](../../../../docs/evidence/iqm/qc/emerald/calibration/metrics.json)). A submission rereads the live default set,
because IQM refuses a job pinned to a retired set and calibration is a property of the run.

## Question

The Garnet idle-schedule job ([design](../../../../docs/design/iqm-garnet-idle-schedule-train-readout.md#result), job
`01a1707f`) resolved ASAP scheduling on all 68 pulsed-qubit arms and left one item open: the observed decay exceeds the
ASAP model's, with a contrast 0.86 to 2.39 times the prediction (median 1.63) and an apparent T1 at 1000 pulses of a
median 0.53 of the calibrated value. The design records that the modeled 16 ns per prx, the calibrated T1, or both
understate the wait. Emerald answers it with two properties Garnet lacks: a 24 ns prx (`drag_crf_sx`, same implementation
name) and calibrated T1 values from 18.9 us (QB37) to 80 us (QB24) on the qubits chosen below. The case asks:

1. Does Emerald's station compiler also schedule ASAP? (H1)
2. Is the excess decay a per-pulse timing gap common to the control stack, or a per-qubit T1 error in the calibration
   copy? (H2)

## Chosen over the runners-up

- QET compensated ladder on Emerald ([design](../../../../docs/design/iqm-garnet-qet-compensated-ladder.md#result)):
  lost because its Garnet H1 is unresolved on pair spread (0.150) and is a statistics question that 54 qubits do not
  change, and its window-phase split depends on the schedule that this case measures first.
- Packed Pauli response on Emerald ([proposal](../packed-pauli-response-emerald/proposal.json),
  [current-balance design](../../../../docs/design/packed-pauli-response-current-balance.md)): lost because it would
  commit 24 credits to 52 qubits with its cost bound pending, and the design prefers the Rigetti route for the density
  test; it also measures no Emerald timing, which sets its shot budget. The 24 credits are measured against the historical
  30.00-credit snapshot (see "Retained measurements").

## Circuits

Twelve circuits at 4000 shots, one active-reset cycle, heralding `none`, each read with one joint `measure` over the
twelve qubits QB5, QB10, QB14, QB18, QB20, QB24, QB26, QB30, QB34, QB37, QB42 and QB44 (names from the dynamic
architecture; couplers from the
[static architecture](../../../../docs/evidence/iqm/qc/emerald/artifacts/static-architecture.json)).

- **Idle layouts, 6 circuits.** The train qubit runs 0, 500 or 1000 `prx(pi)` pulses while every measured qubit that
  shares no coupler with it gets one `prx(pi)`. Layout A trains QB20 (couplers to QB12, QB19, QB21, QB28), so all
  eleven others are pulsed. Layout B trains QB26 (couplers to QB18, QB25, QB27, QB34), so nine are pulsed, and QB20 is
  pulsed there. Every qubit is pulsed at least once (20 pulsed-qubit arms). Under ASAP a pulsed qubit waits 12 us (500
  pulses, 24 ns each) or 24 us (1000) in |1>; under ALAP it does not wait.
- **Parallel trains, 6 circuits.** ro0 and ro1 on all twelve qubits, and trains of 1, 5, 9 and 13 `prx(pi/2)` pulses
  on all twelve, fitted per qubit with its readout pair. The result is descriptive; it sets the readout offset and
  scale used by H2.

## Pre-flight

1. Hypothesis. H1: Emerald schedules ASAP. H2: the job identifies two things only: the schedule, and whether the ratio
   r = apparent T1 / calibrated T1 is common across qubits or varies by qubit. By the definition below,
   r_i = d / (d + g_i) x T1_true_i / T1_cal_i, so a common r fits both a common additive timing gap g and a common
   multiplicative T1 calibration bias, and scatter fits per-qubit gaps or per-qubit T1 errors; 500 against 1000 pulses
   does not separate them, because both stationary mechanisms predict the same r at both counts. Separating a timing gap
   from a T1 calibration bias needs an independent T1 measurement (delay-based decay) or a second pulse duration on the
   same qubits. That measurement is out of scope here; adding it is a separate case with its own cost and approval. H2 is gated on
   H1: r is defined only when the pulsed qubits wait, which holds under ASAP. Under ALAP, a mixed schedule or an
   unresolved schedule the pulsed qubits do not wait on every arm, the contrast carries no T1 information, and H2 is
   unidentifiable; no common-r statistic is computed.
2. Quantity. P(1) of each pulsed qubit at 0, 500 and 1000 train pulses on the train qubit. Contrast c = P(1) at 0 minus
   P(1) at N, corrected by the parallel ro0 and ro1 pair as in `iqm_cancellation_probe.fit_train`. Apparent T1 =
   -(N d) / ln(1 - c) with d = 24 ns, and r = apparent T1 / calibrated T1 (`characterization.model.QBn.t1_time`).
   Definitions follow the Garnet design's analysis, `results/iqm/idle_schedule_probe_analysis.json`.
3. Falsifier and uncertainty model. The common-r test runs only when every pulsed arm resolves to ASAP. H1 fails if any pulsed arm sits closer to the ALAP prediction than the midpoint, or
   the 20 arms split between schedules. For the common-r test, each qubit contributes one r_i from its 1000-pulse arm (a
   qubit pulsed in both layouts pools its arms by inverse variance of the shot noise; the calibrated T1 error is shared by
   its arms and is not reduced by pooling). The variance is sigma_i^2 = r_i^2 [ (sigma_Tapp/Tapp)^2 + (sigma_T1/T1)^2 ],
   with sigma_T1 the retained T1 uncertainty of `metrics.json` (3.6 to 21.7 percent; QB44 21.7, QB26 13.2, QB34 12.8)
   and sigma_Tapp the binomial propagation through the readout correction. The statistic is chi2 = sum_i (r_i - rbar)^2 /
   sigma_i^2 about the weighted mean rbar, with 11 degrees of freedom (12 qubits, one fitted mean). It rejects a common r at
   p < 0.01 (chi2 above 24.7). The variances are propagated from independent per-qubit T1 errors; any correlation among
   qubits is unmodeled.
4. Predicted outcome with budget. ASAP, at about 12.7 standard errors from the midpoint of the ASAP and ALAP predictions
   (hand estimate from the retained T1: QB24 at 500 pulses, exp(-12/80) = 0.861, contrast 0.139 below the ALAP value,
   binomial standard error 0.0055 at 4000 shots, so contrast over standard error is 25.4 and the midpoint over standard
   error is 12.7; zero-pulse arm uncertainty only lowers it; QB37 at 1000 pulses, exp(-24/18.9) = 0.28). Gap model carried
   from Garnet: r = 0.53 there gives g = 16 ns x (1/0.53 - 1) = 14 ns, hence r = 24 / (24 + 14) = 0.63 on Emerald
   (inference; it assumes one common g and a calibrated T1 that is unbiased). Budget: 3.00 credits expected, 4.50 ceiling
   (below).
5. What each result changes.
   - ASAP on all arms: fixes the schedule used by the `iqm_sim` predictions for every later Emerald case. ALAP on all arms:
     retires the Garnet excess as a Garnet-station property and sets the ALAP schedule for `iqm_sim`.
   - Arms split between schedules, or any arm statistically unresolved from the midpoint: the schedule is mixed or
     undetermined; no schedule is assumed for `iqm_sim`, the pulsed arms are tabulated per qubit and layout, and the later
     Emerald cases wait for a successor case with more shots on the unresolved arms.
   - Common-r outcomes below apply only after ASAP on all arms; ALAP, mixed or unresolved schedules leave H2
     unidentifiable and the common-r bullets do not apply.
   - Common r (chi2 not rejected) near 0.63 (within two standard errors of rbar): consistent with one common gap or one
     common T1 bias; it sets the effective per-pulse wait and the pulse-count budget of the pinching and QET cases as an
     effective value, without a mechanism claim.
   - Common r that differs from 0.63 (rbar more than two standard errors away): the Garnet gap does not transfer; the
     pulse-count budgets use the measured rbar, and the Garnet-derived 14 ns is dropped.
   - r varying with qubit (chi2 rejected): per-qubit gaps or per-qubit T1 errors; the later cases stay unpriced until T1 is
     remeasured per qubit.
   - r varying with pulse count (500 against 1000 differing beyond uncertainty): the stationary model fails; the case is
     recorded as a finding and the decay model is reopened before any dependent case is priced.
   - Both variation by qubit and by pulse count: treated as the pulse-count case first; the per-qubit reading waits for a
     model that holds at one qubit.

## Why a simulation cannot answer it

The question is which schedule and which timing the IQM station compiler applies to a circuit job, and how long a
pulse train really occupies a qubit. `iqm_sim` applies the schedule and the calibrated T1 as inputs, so it cannot test
either; the free `emerald:mock` twin has a different chip (M160), different cz and prx implementations, and returns
random bits. Only the Emerald chip answers.

## Cost

Source: `docs/evidence/iqm/qc/emerald/details.json` (payg 0.75 credits per second) and `ceiling_credits` in
`scripts/iqm_jobs.py`: credits = ceil(JOB_SECONDS + expected seconds) x price, with JOB_SECONDS = 1.6 (measured on
Garnet; an Emerald fixed cost is not retained). The Emerald calibration set gives `reset_wait` 400 us, end delay 5 us
and readout 360 ns.

| reset | shots | seconds of shots | plus train idle and 1.6 s | billed | credits |
|---|---|---|---|---|---|
| active, 1 cycle | 48000 | 1.80 (37.5 us each, Garnet value) | 3.69 | 4 s | 3.00 |
| passive fallback | 48000 | 19.46 (405.4 us each) | 21.35 | 22 s | 16.50 |

The train idle adds 0.29 s (4000 shots x 36 us over the two layouts). The active-reset shot time of Emerald is not
measured; the `emerald:mock` estimate (0.00 credits) returns the runtime before any charge. Requested approval:
backend `iqm:emerald`, 12 circuits x 4000 shots, active reset, expected 3.7 s, 3.00 credits, ceiling 4.50 credits (6
billed seconds at 0.75 credits per second). `scripts/iqm_idle_schedule_probe.py` requires 2 s of plan headroom under the
ceiling, so the active path proceeds only if the mock estimate is at most 4.0 s. If the mock refuses active reset or
estimates above 4.0 s, the passive fallback (21.35 s plus 2 s headroom fits 24 s) needs its own approval at a ceiling of
18.00 credits (24 s); against the historical 30.00-credit snapshot that would leave 12.00, but the live balance decides.
Against the retained limits (20000 shots per circuit, 100 circuits per job), the job fits.

## Retained measurements of the same shape

- Garnet idle-schedule job `01a1707f`: 24 circuits x 4500 shots, 1.92 s run, 2 s billed, 1.00 credit at 0.50
  credits per second; all 68 Garnet pulsed arms read ASAP. It differs from this case: its train qubits are QB1 and QB20
  (this case trains QB20 and QB26), its layouts cover a different qubit cohort, and it adds twelve isolated-train/readout
  circuits that this case omits. The pulse counts (0, 500, 1000) and the idle-layout pattern are shared.
- No retained Emerald job of this shape exists: no directory of `results/iqm/runs` and no run record there names
  Emerald.
- The balance on record is 30.00 credits at the 2026-10-22 snapshot, with an expiry of 2026-11-01 in
  `docs/evidence/iqm/account/credit.json`. That snapshot expired before this case was written, so every credit comparison
  above (24 of 30, 12.00 of 30.00) is historical arithmetic; the live balance is unread and is read at submission.

## Open items before a build

- `scripts/iqm_idle_schedule_probe.py` builds for Garnet only; an Emerald build needs a `--qc` option and the qubit
  lists above, then the byte-for-byte case check.
- Predictions above are hand estimates from the retained calibration; the build writes `prediction.json`.
