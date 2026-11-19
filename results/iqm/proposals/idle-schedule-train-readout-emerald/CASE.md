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
- Packed Pauli response on Emerald ([proposal](../packed-pauli-response-emerald/proposal.json)): lost because it would
  commit 24 of the 30 credits to 52 qubits with its cost bound pending and its own design preferring the Rigetti route
  for the density test; it also measures no Emerald timing, which sets its shot budget.

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

1. Hypothesis. H1: Emerald schedules ASAP. H2: the Garnet excess decay is a fixed per-pulse gap g of the control stack,
   so apparent T1 over calibrated T1 is r = d / (d + g) with the same r on every qubit; the alternative is a per-qubit
   calibration error, with r scattered by qubit and independent of d.
2. Quantity. P(1) of each pulsed qubit at 0, 500 and 1000 train pulses on the train qubit. Contrast c = P(1) at 0 minus
   P(1) at N, corrected by the parallel ro0 and ro1 pair as in `iqm_cancellation_probe.fit_train`. Apparent T1 =
   -(N d) / ln(1 - c) with d = 24 ns, and r = apparent T1 / calibrated T1 (`characterization.model.QBn.t1_time`).
   Definitions follow the Garnet design's analysis, `results/iqm/idle_schedule_probe_analysis.json`.
3. Falsifier. H1 fails if any pulsed arm sits closer to the ALAP prediction than the midpoint, or the 20 arms split
   between schedules. H2 (gap) fails if the per-qubit r values from the 1000-pulse arm reject a common value
   (chi-square over 10 degrees of freedom at p < 0.01); it is supported by agreement, and the per-qubit alternative
   wins when r varies with qubit but not with N (500 against 1000).
4. Predicted outcome with budget. ASAP, at about 25 or more standard errors from the midpoint (hand estimate from the
   retained T1: QB24 at 500 pulses, exp(-12/80) = 0.861, 14 percent below the ALAP value, 0.55 percent standard error at
   4000 shots; QB37 at 1000 pulses, exp(-24/18.9) = 0.28). Gap model carried from Garnet: r = 0.53 there gives
   g = 16 ns x (1/0.53 - 1) = 14 ns, hence r = 24 / (24 + 14) = 0.63 on Emerald (inference; it assumes one common g).
   Budget: 3.00 credits expected, 4.50 ceiling (below).
5. What each result changes. ASAP on Emerald fixes the schedule used by the `iqm_sim` predictions for every later
   Emerald case. A common r near 0.63 sets the per-pulse gap and the pulse-count budget of the pinching and QET cases; a
   scattered r sends the correction to per-qubit calibration and leaves those cases unpriced until T1 is remeasured.
   ALAP, or r near 1, retires the Garnet excess as a Garnet-station property.

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
billed seconds). If the mock refuses active reset or estimates above 4.5 s, the passive fallback needs its own approval
at a ceiling of 18.00 credits (24 s), leaving 12.00 of the 30.00. Against the retained limits (20000 shots per circuit,
100 circuits per job), the job fits.

## Retained measurements of the same shape

- Garnet idle-schedule job `01a1707f`: 24 circuits x 4500 shots, 1.92 s run, 2 s billed, 1.00 credit at 0.50
  credits per second. Same layouts and trains; all 68 Garnet pulsed arms read ASAP.
- No retained Emerald job of this shape exists: a name search of `results/iqm/runs` finds one run record, the Garnet
  QET ladder.
- The balance on record is 30.00 credits at the 2026-10-22 snapshot, with an expiry of 2026-11-01 in
  `docs/evidence/iqm/account/credit.json`; the live balance and expiry are read at submission.

## Open items before a build

- `scripts/iqm_idle_schedule_probe.py` builds for Garnet only; an Emerald build needs a `--qc` option and the qubit
  lists above, then the byte-for-byte case check.
- Predictions above are hand estimates from the retained calibration; the build writes `prediction.json`.
