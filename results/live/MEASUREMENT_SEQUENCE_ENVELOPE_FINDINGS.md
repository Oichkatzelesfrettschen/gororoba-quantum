# Measurement-sequence envelope run on ibm_kingston: device verdict withheld by the reset screen

Run `2026-10-27T014422.881898Z`, job `dbg08t9j4t8s73abaghg`, ibm_kingston (Heron r2), backup IBM Cloud instance.
The approved dry run is `2026-10-27T012214.435220Z` (record sha256 `ac412781...91c8b4`); the design is
[measurement-sequence-adaptive-envelope.md](../../docs/design/measurement-sequence-adaptive-envelope.md).

## Execution

The submission re-planned on the live calibration and reproduced the approved plan digest (`a7c7d40d...`) and the
32-qubit layout (1 5 10 13 17 19 20 23 29 33 42 46 50 59 62 66 71 79 82 86 89 95 98 100 109 117 128 134 136 141 149 154);
the approved-record comparison reported no mismatch. One dynamic Sampler job of 88 fused PUBs at 8192 shots
(720,896 shots) ran at a 20 us repetition delay: queued 2026-10-27T01:55:01Z, running 02:54:36Z, finished 02:57:52Z.
`circuits_execution_time_ns` is 35.36 s and `qpu_charge_time_seconds` is 38 against the case's expected 37.7 s
(planner 31.2 s plus 9 us per shot) and its 57 s ceiling, so the 50 us fallback did not run. The planner plus the
per-shot residual priced this circuit class (single-qubit rotations, mid-circuit measurement, terminal reset, no CZ)
within 1 %.

## Preregistered outcome

`msq_envelope_analysis.collected` keeps no qubit, so the pinching analysis reports
`withheld: 0 kept qubits, fewer than 8` and the run has no device verdict. Every qubit passes execution-time
eligibility. Every qubit fails the reset screen; six also fail the crosstalk screen.

Reset screen. The readout-corrected difference between the reset residuals from `|1>` and from `|0>` is positive on
all 32 qubits: median 0.0123, range 0.0049 (q89) to 0.0366 (q98). The screen requires the upper end of the
Bonferroni interval (z = 3.163, standard errors 0.0013 to 0.0024) below 0.0094, which admits a point estimate below
about 0.0045; the smallest upper bound is 0.0096 (q149). The difference runs about 1.7 times the qubit's calibrated
`prob_meas0_prep1` (median 0.0071) with correlation r = 0.34 across qubits, so a measure-based reset inherits its
readout error and something else adds to it.

Crosstalk screen. At 0.05/64 per (qubit, own state) test, qubits 1, 17, 59, 62, 100 and 154 show excess dispersion
of their `|0>` readout error across the other qubits' configurations (p from 6e-4 down to below 1e-6); every `|1>`
test passes.

## Why the reset screen could not pass

The defect was checkable before the run. The control `x; measure; reset; measure` reads the residual of one
measure-and-flip reset, and that residual carries at least the reset measurement's P(0|1); the calibration the case
used put the layout's median P(0|1) at 0.0071, above the 0.0045 point estimate the screen admits at 8192 shots. The
margin was set at half the 0.0188 bound floor, not from the bias a reset residual puts on the N = 16 endpoint, and no
review checked it against Heron r2 reset error. The control also measures a single in-shot reset, while the quantity
that biases the next shot is the state after the terminal reset and the service's `init_qubits` initialization; the
20 us Kingston controls of 2026-10-18 measured that history effect directly (mean -0.0003, median +0.0006, five of 148
qubits above 0.01; [design](../../docs/design/measurement-sequence-adaptive-envelope.md#repetition-delay-shot-history-and-reset-controls)).
The screen therefore withheld qubits on a residual the endpoint does not inherit at that size. A successor case sets
its margin before the run from the endpoint bias of a reset residual, and measures the cross-shot history it bounds.

## Exploratory reading (not preregistered)

`scripts/msq_envelope_exploratory.py` runs the pinching analysis over all 32 qubits with the screens ignored, after
recomputing the screens from the same counts and matching collect.json exactly; its output is
[envelope-run-exploratory.json](../../docs/evidence/measurement_sequence/envelope-run-exploratory.json). Nothing below
is a result of the case.

- Mutation test: the N = 16 measure-minus-unitary contrast is 0.771 to 0.871 (median 0.850, ideal 0.861), z at least
  94.6 on every qubit.
- Departure: all 32 qubits read `consistent`; the measure arm's N = 16 P0 lies above its projective prediction on every
  qubit (median +0.0185, each within about one standard error of 0.017 to 0.068), pooled z 1.07, count rule none.
  No measurement-induced deficit appears at the scale of the 0.0188 floor.
- Settle arm: 16 qubits (15 informative, pooled z 18.7) read `reduced_by_gap`. The measure arm shows no deficit for a
  gap to reduce, so this is the settle arm's P0 standing above the model's prediction for its sixteen 2 us gaps, the
  same direction as the delay arm's idle-model shortfall (measured minus modeled N = 16 dephasing, median +0.11, positive
  on 31 qubits). It is an unexplained excess over the idle model, not a readout-tail attribution.
- Qubits 149 and 154 are uninformative: departure standard errors 0.068 and 0.046 exceed twice their planning values.

## Retained files

`collect.json` is 42.4 MB, `record.json` 17.9 MB and the run directory with `raw/` 361 MB, under the design's 45 MB
and 400 MB limits; the dry-run charge table's 15.3 MB and 20 MB entries described the submit-free record.
