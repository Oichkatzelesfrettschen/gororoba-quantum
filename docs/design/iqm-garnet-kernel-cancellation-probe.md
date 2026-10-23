# Kernel cancellation probe on IQM Garnet

The certified sedenion kernel vector u = (e4 - e15)/sqrt2 of L(e1 + e10)
is the eigenvector of K = L_e1^T L_e10 with eigenvalue -1; the bright vector
(e4 + e15)/sqrt2 is its +1 eigenvector. The signed kernel probe that ran on
Garnet reads an overlap that holds for every unit vector u
([audit](iqm-garnet-signed-kernel-probe.md#adversarial-audit)), so this case
replaces it with an observable that carries the zero-divisor sign at first
order. cd_core already settles the zero-divisor property exactly, so a
resolved H1 demonstrates that Garnet realizes the compiled sign table at
first order; what the run can find out is device physics: QB11's coherent
error, the even-part decomposition and the shape of the response.

## Observable

A Hadamard test whose control branch 0 applies L_e1 or L_e10 under the
selector cos(theta)|e1> + sin(theta)|e10>, and whose branch 1 applies L_e1,
reads <Z_c> = cos^2(theta) + sin^2(theta) <L_e1 u, L_e10 u>: cos(2 theta) for
the kernel vector and 1 for the bright vector
([kernel_cancellation.py](../../gororoba_quantum/kernel_cancellation.py)).
Around the balanced selector theta = pi/4 + phi the kernel reads
-sin(2 phi), odd in phi with its zero at the kernel point. Flipping one
L_e10 sign at e4 or e15 moves that zero, and negating both makes the kernel
read like the bright vector, so the sign table enters the reading.

The reachable data span is two-dimensional: u lives on e4 and e15, both
multipliers leave index bit 2 at 1 and flip bit 1 alike, so data bits 0 and
3 hold it as a Bell pair. The probe runs on five qubits (two data, two
selector, one control), and one parametrized circuit serves both vectors
(the data preparation RY(beta), beta = -pi/2 or +pi/2) and every theta, so
all arms share one compile.

## Case

`scripts/iqm_cancellation_probe.py build results/iqm/cases/kernel-cancellation-probe --live`
reads Garnet's current default calibration set into the case's calibration
copy (set `68b0f1d0`, read 2026-10-23 after `9069c4ef` retired) and compiles
the probe onto Garnet's calibrated couplers (transpiler seed 1 of 24, the
fewest CZ): 37 CZ on QB6, QB7, QB11, QB12 and QB17, control QB12, the
selector angle on QB11. `check` rebuilds the case offline from that copy
(gate `core-642`). One job of 27 circuits x 4000 shots, active reset one
cycle, all-zeros heralding, the calibration set pinned for Garnet alone:

| circuits | purpose |
|---|---|
| kernel phi = +0.1, -0.1, -0.1, +0.1 | zero-divisor sign, drift cancels in the odd part |
| kernel phi = +0.3, -0.3, -0.3, +0.3 | sine law, drift cancels likewise |
| kernel phi = 0, twice | crossing |
| bright phi = +0.1, -0.1, -0.1, +0.1 and 0 | control |
| bare measure and pi then measure, on QB12 and on QB11 | readout calibration of every measured qubit |
| 4k + 1 prx(pi/2), k = 0 to 3, on QB11 and on QB12 | relative over-rotation eps |

**Coherent response.** On this compile the first-order response of the
control's <Z> under the audit's stationary error model (one relative
over-rotation and one axis error per qubit, one residual Z per qubit after
CZ, one conditional phase per coupler; scripts/iqm_probe_audit.py) is zero
for every error except QB11's over-rotation, which scales the kernel odd
part by 1 + O(eps) and shifts its even part by -1.54 eps at phi = 0.1. A
coherent error of that model therefore never fakes the zero-divisor sign
here, unlike the signed probe, whose odd part took a first-order term from
every qubit, and the even part becomes a meter of QB11's pulse amplitude,
which the trains measure independently in the same job. An angle-dependent
amplitude error lies outside the model: a rotation error eta theta|theta| on
QB11 moves the odd part at phi = 0.1 by -0.616 eta, while the pi/2 trains
read it as eps = 1.571 eta, through which the linear model predicts
-0.308 eta, half the effect. It rescales the visibility and leaves the sign
of the odd part.

**Train length.** The signed probe's even offsets put QB11's over-rotation
near 2.7 +- 0.7 % once the device's visibility damping is counted
([audit](iqm-garnet-signed-kernel-probe.md#adversarial-audit)), under the
retired set `9069c4ef`. A 41-pulse train would wrap that error past 1.7 rad,
so the trains stop at 13 pulses (under 0.7 rad at 3 %) and the analysis fits
-sin(N pi/2 eps) itself rather than its linearization, through each train
qubit's own readout calibration, over |eps| <= 0.06, where every train
turns through less than pi/2 and so admits no alias; a minimum on that edge
counts as a train outside the model. Garnet recalibrates
its pulses with each set, so QB11's error under `68b0f1d0` is a fresh
measurement and the 2.7 % is a comparison, not a prediction the case tests.

**Decisions** (three standard errors):

- H1 zero-divisor sign: the kernel odd part at phi = 0.1 and 0.3 resolves
  the sign when it lies three standard errors below zero and falsifies the
  cancellation law three above.
- H2 bright control: a bright odd part three standard errors from the
  model's own bright odd part (idle relaxation is not unital), rescaled to
  the measured readout, marks a circuit artifact.
- H3 sine law: the contrast odd(0.3) - 2.84 odd(0.1), with
  sin(0.6)/sin(0.2) = 2.84, three standard errors from zero.
- H4 even-part decomposition: the kernel even part at phi = 0.1 against
  the measured readout offset, plus the model's idle-relaxation even part
  rescaled by the measured readout scale, plus -1.54 V eps from QB11's
  trains; its standard error carries the readout, visibility, train and
  model-sampling errors.
- H5 amplification: the trains' <Z> follows -sin(N pi/2 eps) with the
  readout applied; a residual chi-square above 15.6, the
  three-degree-of-freedom quantile of the one-sided three-sigma tail, marks
  merged pulses or a non-stationary error and suspends H4.

The analysis lists every falsified hypothesis; an odd part within three
standard errors of zero leaves H1 unresolved, never falsified. It reads
Garnet runs of this case alone, one cases.json digest at a time, each
compiled against the prediction's calibration set; mock runs never enter.

**Prediction** (scripts/iqm_sim.py noise from set `68b0f1d0` with ALAP idle
T1/T2 relaxation, 200000 shots per circuit): kernel odd part -0.094 at
phi = 0.1 (visibility 0.47, against 0.21 measured on the 199-CZ signed
probe) and -0.265 at 0.3, kernel even part +0.061 and crossing +0.062 from
relaxation, bright odd part -0.008 and bright reading +0.487. The model
carries no coherent error.

**Model device.** The self-test draws counts from the exact coherent model of
each circuit at visibility 0.6 with QB11 over-rotated by 2.7 % and QB12 by
-0.3 %, the control reading with errors (0.01, 0.03) and QB11 with
(0.05, 0.12): it resolves H1 at both angles, falsifies no hypothesis and recovers
both over-rotations from the trains; it falsifies H1 when the kernel's sign
is reversed, falsifies H4 when the kernel arms carry an even shift of -0.05
that over-rotation does not explain, leaves H1 unresolved with H3 defined
for a device with no signed response, and suspends H4 when the trains ignore
their pulse count.

**Mock runs.** garnet:mock refused the first submission ('Calibration set
not found', 0 credits), since the case then pinned Garnet's set for every
QC; the set is now pinned per QC. The second run accepted a 21-circuit
build (estimate 2.80 s) and the third a 25-circuit build (3.01 s). The
fourth ran the current 27-circuit bytes (cases.json sha256 `b3a9e166...`),
compiled against the mock's own set, estimated 3.09 s and charged 0.00
credits; mock bits are random. A dry submission to Garnet passed every
refusal.

**Cost.** Expected 3.35 s of shots at an upper 31 us per heralded shot (the
slope of the two heralded Garnet jobs), ceiling ceil(1.60 + 3.35) x 0.50 =
2.50 credits, recorded in cases.json as the approved ceiling for Garnet; the
mock's estimate puts the likely bill at ceil(3.0) x 0.50 = 1.50 to 2.00
credits.
