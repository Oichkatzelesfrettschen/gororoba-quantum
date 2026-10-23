# Kernel cancellation probe on IQM Garnet

The certified sedenion kernel vector u = (e4 - e15)/sqrt2 of L(e1 + e10)
is the eigenvector of K = L_e1^T L_e10 with eigenvalue -1; the bright vector
(e4 + e15)/sqrt2 is its +1 eigenvector. The signed kernel probe that ran on
Garnet reads an overlap that holds for every unit vector u
([audit](iqm-garnet-signed-kernel-probe.md#adversarial-audit)), so this case
replaces it with an observable that carries the zero-divisor sign at first
order.

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

`scripts/iqm_cancellation_probe.py build results/iqm/cases/kernel-cancellation-probe`
compiles the probe onto Garnet's calibrated couplers (transpiler seed 1 of
24, the fewest CZ): 37 CZ on QB6, QB7, QB11, QB12 and QB17, control QB12,
the selector angle on QB11. One job of 21 circuits x 4000 shots, active
reset one cycle, all-zeros heralding, calibration set `9069c4ef` pinned for
Garnet alone:

| circuits | purpose |
|---|---|
| kernel phi = +0.1, -0.1, -0.1, +0.1 | zero-divisor sign, drift cancels in the odd part |
| kernel phi = +0.3, -0.3 | sine law |
| kernel phi = 0, twice | crossing |
| bright phi = +0.1, -0.1, -0.1, +0.1 and 0 | control: odd part zero at every visibility |
| QB12 bare measure, QB12 pi then measure | readout calibration of the control |
| 4k + 1 prx(pi/2), k = 0, 5, 10, on QB11 and on QB12 | relative over-rotation eps |

**Coherent response.** On this compile the first-order response of the
control's <Z> (scripts/iqm_probe_audit.py's model) is zero for every
coherent error except QB11's over-rotation, which scales the kernel odd
part by 1 + O(eps) and shifts its even part by -1.54 eps at phi = 0.1. A
coherent error therefore never fakes the zero-divisor sign here, unlike the
signed probe, whose odd part took a first-order term from every qubit; and
the even part becomes a meter of QB11's pulse amplitude, which the trains
measure independently in the same job.

**Decisions** (three standard errors):

- H1 zero-divisor sign: the kernel odd part at phi = 0.1 and 0.3 resolves
  the sign when it lies three standard errors below zero and falsifies the
  cancellation law three above.
- H2 bright control: a bright odd part three standard errors from zero
  marks a circuit artifact.
- H3 sine law: odd(0.3)/odd(0.1) against sin(0.6)/sin(0.2) = 2.84.
- H4 even-part decomposition: the kernel even part at phi = 0.1 against
  the measured readout offset, plus the model's idle-relaxation even part
  rescaled by the measured readout scale, plus -1.54 V eps from QB11's
  trains.
- H5 amplification: the trains' <Z> is linear in the pulse count; a
  non-linear train (pulses merged or saturated) suspends H4.

**Prediction** (scripts/iqm_sim.py noise from the calibration copy with
ALAP idle T1/T2 relaxation, 200000 shots per circuit): kernel odd part
-0.113 at phi = 0.1 (visibility 0.57, against 0.21 measured on the 199-CZ
signed probe), -0.318 at 0.3, kernel even part +0.034 from relaxation, and
bright odd part -0.007 from the same non-unital relaxation, under one
standard error at these shots. The model carries no coherent error.

**Model device.** The self-test draws counts from the exact coherent model of
each circuit at visibility 0.6 with injected over-rotations: it resolves H1,
leaves H2 and H4 standing, recovers QB11's +0.006 and QB12's -0.003 from the
trains, falsifies H1 when the kernel's sign is reversed and falsifies H4
when the kernel arms carry an even shift of -0.05 that over-rotation does not
explain.

**Mock run.** garnet:mock refused the first submission ('Calibration set not
found', 0 credits), since the case then pinned Garnet's set for every QC;
the set is now pinned per QC. The second run accepted all 21 circuits,
compiled against the mock's own set, estimated 2.80 s and charged 0.00
credits; its bits are random.

**Cost.** Expected 1.80 s of shots at an upper 21.4 us per heralded shot,
ceiling ceil(1.60 + 1.80) x 0.50 = 2.00 credits, recorded in cases.json as
the approved ceiling for Garnet.
