# IQM Garnet idle schedule and per-qubit train readout

This case measures two Garnet device facts that the IQM circuit-job predictions rest on, in one job. The case
directory is [results/iqm/cases/idle-schedule-train-readout](../../results/iqm/cases/idle-schedule-train-readout/cases.json),
built by `scripts/iqm_idle_schedule_probe.py build DIR --live` from Garnet's default calibration set
`a18a947f-0408-4628-81ea-1715637e434f`. The script's docstring states the preregistered decisions H1 and H2, and
`prediction.json`, bound by digest into `cases.json`, holds the predictions they are decided against.

## Questions

**Scheduling.** `iqm_sim`-based predictions (the kernel cancellation, signed and null-controlled signed probes)
apply idle T1/T2 relaxation over an ALAP schedule. The iqm-pulse TimeBox default is ASAP, and a circuit job body
names no strategy. The job API returns only `measurements`, `measurement_counts`, `runtime_estimates` and
`sweep_results`, and the compilation record of a retained `garnet_mock` job holds only the runtime estimate and the
calibration set. No retained record names the strategy, so it is measured. On the retained kernel cancellation
case, the schedule moves the model's relaxation even part from +0.038 (ALAP) to +0.066 (ASAP).

**Train readout.** The null-controlled signed probe read its prx trains on QB6 and QB11 through a readout pair on
QB7 only, so a train's over-rotation is not separable from its own qubit's readout offset and scale. Its retained
prediction attributes a 2.7 % over-rotation to QB11 (`iqm_signed_resolve.COHERENT`).

## Circuits

The job runs 24 circuits at 4500 shots, with one active-reset cycle and no heralding. All-zeros heralding over
20 measured qubits would keep about a fifth of the shots, so each readout pair's bare measure carries the reset's
initialization error in its e01 instead. One shot reads every qubit, so circuits that drive all qubits at once cost
the shots of one.

- **Idle layouts, 6 circuits.** A train qubit runs 0, 500 or 1000 pi pulses while every qubit that shares no coupler
  with it gets one pi pulse, and all 20 qubits are read in one joint measure. The train qubit is QB1 in one layout
  and QB20 in the other, so every qubit is pulsed at least once (34 pulsed-qubit arms). Under ASAP each pulsed
  qubit waits 8 or 16 us in |1> and relaxes; ALAP predicts no change. The weakest predicted separation of the two
  schedules is 25.7 standard errors (QB12 at 500 pulses), and under an ASAP verdict each pulsed qubit's decay
  also gives an apparent T1.
- **Parallel trains, 6 circuits.** ro0 and ro1 on all qubits, and trains of 1, 5, 9 and 13 pi/2 pulses on all
  qubits at once, fitted per qubit with its readout pair: an over-rotation map of the device.
- **Isolated trains, 12 circuits.** QB6 and QB11 alone, as the signed probes drove them: ro0, ro1 and the four
  trains, each fitted with its own readout pair (`iqm_cancellation_probe.fit_train`). The parallel minus isolated
  eps of each measures drive crosstalk on these two qubits.

## Why a simulation cannot answer it

Both questions concern the device itself. H1 asks which schedule Garnet's station compiler applies, which no
local model or mock contains: the mock twin's cz and prx implementations differ from Garnet's, and it returns
random bits. H2 asks how much the physical pulses on QB6 and QB11 over-rotate. The self-test shows that the
analysis recovers either schedule, and injected over-rotations, from model devices whose readouts differ from the
calibration's.

## Cost

- **Expected time:** 4.27 s of shots, 24 circuits x 4500 shots x 37.5 us (the unheralded active-reset shot of
  the reset pilot) plus the idle trains. Garnet adds about 1.6 s per job.
- **Ceiling:** the approved 4.00 credits (8 billed seconds at Garnet's 0.50 credits/s), recorded as
  `max_credits`. IQM Server takes no runtime cap with a job, so on its own `max_credits` bounds only the
  predicted bill. This job was collected by the `iqm_jobs.py collect` of #469, which cancels a priced run whose
  billed runtime comes within 1.0 s of the ceiling. The build refuses a plan that leaves less than 2 s below
  the ceiling, because runtimes ran up to 1.39 s above their estimates.
- **Mock run:** the free `garnet:mock` twin, at 0.00 credits/s, first returns the runtime estimate. Its outcomes
  never enter the analysis.
- **Balance:** the account holds 17.00 credits that expire at 2026-11-01 00:00 UTC.

## Result

The job ran on 2026-10-25 as `01a1707f-6157-75dc-aca8-6f30e5f0280b`, under calibration set `a18a947f`, after the
`garnet:mock` run `01a1707e` estimated 3.09 s. It ran 1.92 s, billed 2 s and charged 1.00 credit. The analysis is
[idle_schedule_probe_analysis.json](../../results/iqm/idle_schedule_probe_analysis.json), and the claims are
`iqm-garnet-idle-schedule` and `iqm-garnet-mock-idle-schedule`.

- **H1, schedule: ASAP.** All 68 pulsed-qubit arms resolve ASAP, at 13.3 to 58.7 standard errors from the midpoint
  of the two predictions. The decay exceeds the ASAP model's: the observed contrast runs 0.86 to 2.39 times the
  prediction (median 1.63), and the apparent T1 at 1000 pulses is a median 0.53 of the calibrated value. The
  modeled 16 ns per prx, the calibrated T1, or both understate the wait. That is unresolved here and decides
  nothing.
- **H2, train readout.** QB11's isolated train reads -0.30 +- 0.06 %, which excludes the 2.7 % attribution at 47
  standard errors. QB6's reads -0.18 +- 0.07 %. Both fits are linear (chi-square 8.1 and 1.2 on three degrees of
  freedom).
- **Parallel map, descriptive.** 13 of 20 qubits fit the linear train model when all are driven at once; QB2,
  QB5, QB7, QB11, QB15, QB16 and QB17 do not. QB6 reads -0.22 +- 0.10 % parallel minus isolated.

## Procedure

```sh
export PYTHON="${PYTHON:-python3}" IQM_TOKENS_FILE=~/.config/iqm/tokens.json
C=results/iqm/cases/idle-schedule-train-readout
D=$(sha256sum $C/cases.json | cut -d' ' -f1)
"$PYTHON" scripts/iqm_jobs.py submit $C probe --qc garnet:mock --approval QUOTE --approved-cases-sha256 $D --max-credits 0.0
"$PYTHON" scripts/iqm_jobs.py collect RUN_DIR
"$PYTHON" scripts/iqm_jobs.py submit $C probe --qc garnet --approval QUOTE --approved-cases-sha256 $D --max-credits 4.0
"$PYTHON" scripts/iqm_jobs.py collect RUN_DIR
"$PYTHON" scripts/iqm_idle_schedule_probe.py analyze RUN_DIR --out results/iqm/idle_schedule_probe_analysis.json
```

Gates `core-681` (self-test) and `core-682` (case rebuild from its retained calibration) cover the script and the
case bytes in the nightly audit; at about 60 s and 35 s they exceed the pull-request gate bound.
