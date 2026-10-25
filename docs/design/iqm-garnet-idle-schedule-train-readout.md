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

The job runs 18 circuits at 10000 shots, with all-zeros heralding and one active-reset cycle:

- **Idle arms, 6 circuits.** On QB1 (T1 23.7 us) and QB7 (T1 49.1 us), each arm is one pi pulse on the probe
  qubit, then 0, 500 or 1000 pi pulses on an uncoupled partner (QB3 and QB2), then one joint measure of both.
  Under ASAP the probe qubit idles 8 or 16 us in |1>. The predicted ASAP contrasts z(n) - z(0) are 0.559 and
  0.958 on QB1 and 0.287 and 0.531 on QB7; ALAP predicts 0. At the design's 50 % kept-shot floor, the two
  schedules separate by 36 to 176 standard errors.
- **Train readout, 12 circuits.** For QB6 and QB11: ro0, ro1, and the amplitude trains of 1, 5, 9 and 13
  pi/2 pulses. Each train is fitted jointly with its own readout pair (`iqm_cancellation_probe.fit_train`).

## Why a simulation cannot answer it

Both questions concern the device itself. H1 asks which schedule Garnet's station compiler applies, which no
local model or mock contains: the mock twin's cz and prx implementations differ from Garnet's, and it returns
random bits. H2 asks how much the physical pulses on QB6 and QB11 over-rotate. The self-test shows that the
analysis recovers either schedule, and injected over-rotations, from model devices whose readouts differ from the
calibration's.

## Cost

- **Expected time:** 6.06 s, which is 18 circuits x 10000 shots x 31 us plus the idle trains.
- **Ceiling:** 8 billed seconds, 4.00 credits at Garnet's 0.50 credits/s. `cases.json` records it as
  `max_credits`, and `iqm_jobs.py collect` cancels a job that would exceed it (#376).
- **Mock run:** the free `garnet:mock` twin, at 0.00 credits/s, first returns the runtime estimate. Its outcomes
  never enter the analysis.
- **Balance:** the account holds 17.00 credits that expire at 2026-11-01 00:00 UTC.

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
case bytes.
