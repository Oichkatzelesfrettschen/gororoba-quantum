# Primorial cover-defect probes: Grover quotient, phase-gradient tomography and the repair contrasts

The certified instances of [primorial-cover-defects.md](../notes/topics/primorial-cover-defects.md)
give circuits of two and three qubits whose ideal response is known exactly.
This document states what each circuit can test, applies the hardware-probe
rules of [algebra_circuit_rules.md](../notes/algebra_circuit_rules.md#hardware-probes)
to it, and records the noise-model prediction that decides whether any of it
goes to hardware. The prediction is the ibm_kingston snapshot of
2026-10-15T19:42:21-07:00 run by `scripts/primorial_cover_noise.py`
([evidence README](../evidence/primorial_cover/README.md), gate `core-689`).
No hardware case exists, and no submission is planned by this document.

## What a device can and cannot test here

The arithmetic is settled classically: an exhaustive search proves each defect
in about a second, so no measurement outcome bears on whether a gap exists.
A hardware run can only test whether a device implements the compiled
operation, and `Tr(rho H_D) >= delta` holds for every state, so a mitigated
energy below the certified minimum indicts the estimator.

| Family | Qubits, CZ | Ideal observable | Mutation (property removed) | Reading |
| --- | --- | --- | --- | --- |
| Gap-20 Grover quotient | 2, 2 | marked label read with probability 1 | no oracle: 1/4; complement marked: 0 | bit order, phase marking, readout; retained readout data already cover it |
| Phase gradients, gap86 or gap88 | 3, 8 | `<X_j> = cos(gamma d)`, `<Y_j> = -sin(gamma d)` per cube edge | zero-angle block: every `d = 0` | the seven nonconstant `c_S` of the compiled network |
| Gap-86 repair | 3, 8 | unchanged | the repair is the mutation | fails the mutation test: `H - I` is a global phase, and the compiled circuits are identical (test `test_gap86_repair_changes_no_circuit`) |
| Gap-88 repair | 3, 8 | `c_Z1` moves by -1/2; QAOA law moves by TV 0.132128 | the repair is the mutation | passes for the encoded arithmetic; on a device with virtual RZ both arms share every CZ and differ only in exact frame changes, so the contrast tests the program, not the device |

The gap-86 repair is therefore an analysis negative control: any measured
difference between its nominal arms measures acquisition drift. The gap-88
contrast is a check that the decoder reads the program the compiler emitted.

## Phase-gradient protocol

For each edge `(j, x)` with `x_j = 0` the arm prepares
`(|x> + |x ^ 2^j>)/sqrt2`, applies `exp(-i gamma H)` through the eight-CNOT
network at `gamma = pi/9` (every ideal edge phase lies in `(-pi, pi)`; the
largest `|d|` is 5), and reads qubit `j` in X and Y. The twelve edge phases
determine the seven nonconstant coefficients by least squares on the cube's
incidence matrix (rank 7), and the five-dimensional cycle space carries the
residual. Three corrections apply, in order:

1. **Assignment.** The eight basis preparations of the path give per-qubit
   `p(1|0)` and `p(0|1)`; `<Z>_obs = (1 - a - b) <Z> + b - a` is inverted
   before the phase is taken. Uncorrected, readout asymmetry bends `atan2`
   and biases `c_Z2` by up to 0.021, a third of the identification radius.
2. **Null subtraction.** The zero-angle block is the identity map with the
   same CZ count, schedule and duration. Each cost edge reading is rotated by
   minus the null arm's phase on the same edge, and the null arm's own shots
   add its phase variance to every subtracted edge, which roughly doubles the
   shot budget. A static detuning of one path qubit and a CZ conditional phase
   both cancel to the levels of the coherent table below; static ZZ is not
   simulated.
3. **Decision.** A coefficient is identified when its estimate lies within
   1/16 of its exact value, half the 1/8 grid; the seven coefficients of one
   cost are decided together at family-wise level 0.01 (Bonferroni, z 3.19).

## Prediction under the Kingston model

Patches: the best three-qubit path by summed CZ error plus mean assignment
error (45-46-47) and the path at the median of that cost (117-125-126). Every
arm is ALAP scheduled, so the spectator intervals of the outer qubits relax.
Shot budgets carry each mean's variance through the assignment inversion
(scaled by `1/(1 - a - b)^2`) and, after null subtraction, add the null arm's
phase variance.

| Quantity | best | median |
| --- | ---: | ---: |
| Quotient: marked label read | 0.979 to 0.984 | 0.963 to 0.973 |
| Quotient: complement-marked arm reads the label | 0.002 to 0.003 | 0.001 to 0.002 |
| Gradient visibility, gap88, raw | 0.960 to 0.985 | 0.922 to 0.975 |
| gap88 largest coefficient bias, raw / corrected / null-subtracted | 0.017 / 0.0020 / 0.0025 | 0.013 / 0.0028 / 0.0032 |
| Cycle residual RMS (corrected) | 0.0014 | 0.0024 |
| Shots per setting to identify all seven, corrected / null-subtracted | 1,242 / 2,803 | 1,405 / 3,169 |
| gap88 repair `c_Z1` shift recovered (exact -0.5) | -0.4987 | -0.4992 |
| Shots per setting resolving that shift at z 3 | 33 | 36 |
| QAOA TV, gap88 against repaired (ideal 0.132128) | 0.126 | 0.120 |

Coherent sensitivity (noise-free, best patch): every CZ followed by a
conditional phase on its pair, every sx replaced by RX(pi/2 (1 + eta)), or one
path qubit detuned, its frame drifting by RZ(2 pi delta t) over every
scheduled interval. The per-coefficient standard deviation at the
null-subtracted budget of 2,803 shots per setting is 0.011 to 0.019.

| Error | largest bias, uncorrected | null-subtracted | cycle residual |
| --- | ---: | ---: | ---: |
| CZ phase 0.02 rad | 0.057 | 0.0005 | 0.0004 |
| CZ phase 0.05 rad | 0.143 | 0.0032 | 0.0025 |
| CZ phase 0.10 rad | 0.287 | 0.0128 | 0.0103 |
| sx amplitude 0.002 | 0.00003 | 0.00001 | 0.00003 |
| sx amplitude 0.004 | 0.0001 | 0.00006 | 0.0001 |
| sx amplitude 0.01 | 0.0007 | 0.0004 | 0.0008 |
| detuning 10 kHz, q0 / q1 / q2 | 0.078 / 0.024 / 0.015 | 0.0000 / 0.0001 / 0.0003 | 0.0000 / 0.0000 / 0.0001 |
| detuning 30 kHz, q0 / q1 / q2 | 0.233 / 0.072 / 0.046 | 0.0000 / 0.0006 / 0.0022 | 0.0000 / 0.0003 / 0.0006 |

The uncorrected CZ-phase shift falls on `c_Z0`, `c_Z0Z1` and `c_Z1` and leaves
the cycle residual near zero, so a CZ phase error reads as a different but
self-consistent Hamiltonian; only an absolute comparison or the null arm
exposes it. Detuning behaves the same way. Wire 0 is never a CNOT target, so
its drift lands on `c_Z0` alone; wire 1 carries the parities `x0 + x1` and
`x0 + x1 + x2` for part of the block, so a q1 detuning moves `c_Z0Z1` by 0.75
of its `c_Z1` shift; a q2 detuning reaches `c_Z0Z2`, `c_Z1Z2` and `c_Z0Z1Z2`
at a fifth of its `c_Z2` shift. The 5 to 30 kHz detunings fitted on Fez lanes
([atlas_detuning_map](../evidence/atlas_detuning_map/README.md)) put these
shifts beyond the identification radius, and the null arm removes them to
0.0022 or less.

## Decision on hardware

The prediction answers the design question and leaves no primorial question
for a device. Under the incoherent model every family passes with a wide
margin. Of the coherent families fitted to the Fez and Kingston fringes
([coherent-error-families-report.md](../notes/topics/coherent-error-families-report.md)),
the null arm removes a static detuning of up to 30 kHz to 0.0022 and the CZ
conditional phase to first order; the sx amplitude error, the one family that
acts only inside the network's Hadamards, biases no coefficient by more than
0.0007 at eta = 0.01, far below the shot noise. Static ZZ and axis tilt were
not simulated. RZ is virtual on Heron r2 (zero duration and error in the
snapshot). The null-subtracted coefficients are therefore predicted to
recover the integer table on any healthy path at about 2,800 to 3,200 shots
per setting. A hardware run would then report two
things: the null arm's edge phases, which measure the path's detuning and CZ
phase, a characterization the atlas performs with more edges per shot; and a
null-subtracted pass that the model already predicts. Neither depends on the
primorial instance.

A case would earn hardware time only by naming a device question the null arm
answers better than the atlas: for example, the conditional-phase error of a
specific coupler inside a dense CZ network, or a platform whose single-qubit
rotations are physical rather than virtual, so that angle-dependent errors
survive null subtraction. Such a case states the platform, the path, the
coherent family it targets and its expected seconds or credits, and follows
the approval flow of AGENTS.md (QPU time and calibration, Hardware services).
The Quantum Inspire QX and Ry emulators would add an interface check only:
both are provider jobs that need an approved case, and Ry puts qubit 0 at the
leftmost character of its result strings
([quantum_inspire/README.md](../notes/quantum_inspire/README.md)).
