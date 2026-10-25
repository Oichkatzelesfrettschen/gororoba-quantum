# Primorial phase-gradient tomography under joint coherent gate-error bounds

[primorial-cover-defect-probes.md](primorial-cover-defect-probes.md) closed the
device question for the gap-88 phase-gradient circuits by testing one coherent
error family at a time. This document records the joint test that reopens it,
the quantity that now decides it, and the research that answers it before any
hardware case. The record is `docs/evidence/primorial_cover/bound_residuals.json`
([evidence README](../evidence/primorial_cover/README.md#joint-coherent-bounds),
gate `core-primorial-bound-residuals-replay`), computed by
`scripts/primorial_bound_residuals.py` on the compiled gap-88 and zero-angle null
arms of the best (45-46-47) and median (117-125-126) paths of the ibm_kingston
snapshot of 2026-10-15T19:42:21-07:00.

## What changed in the test

- **Per-coefficient criterion.** The seven coefficients carry per-shot
  variances from 0.32 (`c_012`) to 1.10 (`c_1`) in `noise.json`, so their
  standard deviations at the retained budget run from 0.0103 to 0.0188. A
  scenario's `max_z` divides each coefficient's null-subtracted bias by its own
  standard deviation. The single-family tilt and CZ-phase residuals land on
  `c_2`, whose SD is the largest, so this reading leaves the earlier single-family
  margins in place (tilt 0.79 and 0.89, CZ phase alone 0.72 and 0.77).
- **Joint bounds.** The sx error bounds a coherent sx and x error and the CZ
  error bounds a conditional phase; the two draw on different gates, so both
  can sit at their bounds together. The sx-and-x budget also requires the x
  pulse, whose tilt infidelity is (2/3) sin^2(beta), twice the sx value, to
  stay within the snapshot's x error.
- **Identification endpoint.** The retained budget was set by
  `primorial_cover_noise.phase_fit`: Z^2 times the worst coefficient variance
  over (1/16 minus the largest bias)^2. Each scenario reports the shots that
  rule needs with the scenario's bias in place.

An exploratory build-host run of the single-family and joint scenarios came
first and showed the joint result; the per-coefficient reading, the sx-and-x
budget, the twirled rows, the fraction scan, the refinement and the
identification endpoint were added after it, and the retained run followed.

## Result

| | best (45-46-47) | median (117-125-126) |
| --- | ---: | ---: |
| retained budget, shots per setting | 2,803 | 3,169 |
| tilt alone at the sx bound, max_z | 0.79 | 0.89 |
| CZ phase alone at its bound (0.097 to 0.104 rad), max_z | 0.72 | 0.77 |
| tilt and CZ phase jointly at the bounds, max_z / bias | 2.61 / 0.049 | 2.84 / 0.050 |
| interior refinement of the joint box, max_z | 2.62 | 2.85 |
| shots to identify all seven coefficients at that bias | 53,363 | 76,596 |
| joint, sx-and-x budget, max_z / shots | 1.90 / 13,896 | 2.06 / 16,537 |
| CZ phase twirled, alone / with tilt at the sx bound, max_z | 0.27 / 1.07 | 0.29 / 1.20 |
| sx/x amplitude alone at the sx bound, max_z | 0.16 | 0.27 |

The joint residual exceeds the sum of the single-family residuals (0.049
against 0.0147 + 0.0135 on the best path). Each family alone enters the
null-subtracted fit at second order, because the null arm shares its
first-order term; the product of tilt and CZ phase depends on the arm's rz
angles, so the null arm does not share it. The worst vertex sets the two
couplers' phases opposite, and the interior refinement finds the maximum
with q0 untilted. At the sx-budget worst point the amplitude error is zero. Both simulators agree: the numpy statevector
replays every retained single-family scenario to 1.6e-15, and an independent
qiskit circuit of the worst joint point matches it to 1e-12.

Every one of the 226 working three-qubit paths of the snapshot reaches max_z
1 at its own bounds (median 2.96, against the best path's standard
deviations), and on 82 paths the bias exceeds 1/16, so the coefficients
become unidentifiable at any shot count. Eight paths through qubits 113, 121
and 146, whose sx and x errors read 1.0, are dropped.

## What decides the question

The gate-error bounds charge the whole reported error of each gate to one
coherent family, while the reported errors also carry relaxation and
dephasing during the gate, so the bounds are upper limits on the coherent
part. Infidelity grows as the square of the error angle, so a tilt at
fraction f of its bound is a coherent share f^2 of the sx error, and a CZ
phase at fraction g of its bound a share g^2 of the CZ error. The scan
scales all three tilts by f and both CZ phases by g and takes the worst of
the 32 sign patterns at every cell; the refined worst point leaves q0
untilted, so each cell is a lower bound on its box:

| tilt fraction f (sx share f^2) | max_z at g = 0.5, share 0.25 (best / median) | max_z at g = 1, share 1 (best / median) |
| ---: | ---: | ---: |
| 0.1 (0.01) | 0.25 / 0.26 | 0.84 / 0.90 |
| 0.2 (0.04) | 0.33 / 0.35 | 0.98 / 1.04 |
| 0.3 (0.09) | 0.42 / 0.46 | 1.13 / 1.21 |
| 0.5 (0.25) | 0.66 / 0.72 | 1.48 / 1.59 |
| 1.0 (1) | 1.53 / 1.70 | 2.61 / 2.84 |

Tilt and CZ phase alone reach max_z 1 only when the CZ error is almost
wholly a coherent conditional phase (g near 1) and at least 4 percent of
the sx error is coherent tilt (f = 0.2), or when about a quarter of the sx
error and half of the CZ error are coherent (f = 0.5, g = 0.7). At f = 0.1
the worst scanned pattern gives 0.84 and 0.90 even with g = 1.

Static detuning and ZZ, which the gate errors do not bound, enter the same
way: each cancels to first order in the null arm, and its product with
another family survives. The record pairs them with the bounded families:

| pair, every sign pattern | max_z best / median |
| --- | --- |
| detuning 30 kHz on all three qubits, alone | 0.13 / 0.14 |
| detuning 30 kHz with the atlas-fitted CZ phase 0.04 rad | 0.43 / 0.45 |
| detuning 30 kHz with the CZ-phase bound | 1.32 / 1.40 |
| detuning 30 kHz with the tilt bound | 1.59 / 1.75 |
| detuning 5 kHz with the CZ-phase bound / with the tilt bound | 0.81 / 0.85; 0.90 / 1.02 |
| partner-in-0 ZZ 20 kHz with the tilt bound / with the CZ-phase bound | 1.03 / 1.15; 0.98 / 1.04 |
| symmetric-frame ZZ 20 kHz with the tilt bound / with the CZ-phase bound | 0.81 / 0.92; 0.81 / 0.86 |
| ZZ 2 kHz, either frame, with either bound | at most 0.81 / 0.91 |

So the question rests on three coherent quantities of the chosen path, not
two: the tilt and CZ-phase fractions and the static detuning of each qubit.
At the magnitudes the repository has measured, the atlas's 5 to 30 kHz
detunings and its 0.04 rad CZ phase, the pair stays at 0.43 and 0.45.
Detuning of 30 kHz crosses 1 with a CZ phase or a tilt at its bound, 5 kHz
crosses it with the tilt bound on the median path, and partner-in-0 ZZ of
20 kHz crosses it with either bound on the median path and with the tilt
bound on the best.

Two estimates place f and g, neither measured on these paths. A drive-axis
tilt from a detuning Delta during a pulse of mean Rabi rate Omega is about
Delta / Omega; the 32 ns sx pulse has Omega near 2 pi times 7.8 MHz, so
f = 0.2 corresponds to an in-pulse detuning near 47 kHz, against the 5 to
30 kHz static detunings the Fez atlas fits
([atlas_detuning_map](../evidence/atlas_detuning_map/README.md)). That
estimate gives f of about 0.02 to 0.13; a DRAG-shaped pulse and AC Stark
shift make it an order-of-magnitude estimate. The only
calibration-consistent CZ-phase fit in the atlas is -0.04 rad on two Fez
couplers, g near 0.3 to 0.4
([coherent-error-families-report.md](../notes/topics/coherent-error-families-report.md)),
and Kingston identified no CZ phase. Confidence that a real Kingston path
sits below max_z 1 is moderate: a measured tilt above 0.006 rad, a CZ phase
above 0.07 rad or a static detuning above 30 kHz on the chosen path lowers
it, and measured values a factor of three below those raise it to high.

## Arm mismatch

Null subtraction cancels an error only where the signal and null arms see
the same one. Applied to the signal arm alone, each family reaches max_z 1
at a mismatch of:

| family | best | median |
| --- | --- | --- |
| tilt, per qubit (rad) | 0.0064 / 0.0022 / 0.0032 | 0.0061 / 0.0022 / 0.0031 |
| CZ phase, per coupler (rad) | 0.0064 / 0.0092 | 0.0061 / 0.0089 |
| static detuning, per qubit (kHz) | 2.4 / 7.3 / 12.4 | 2.2 / 7.1 / 11.8 |
| static ZZ, per coupler (kHz) | 4.7 / 14.6 | 4.5 / 14.2 |
| sx/x amplitude, per qubit (fraction) | 0.065 / 0.072 / 0.065 | 0.063 / 0.070 / 0.063 |

A hardware run therefore interleaves the signal and null arms within one job
and one calibration window; a q0 frequency difference of 2.2 to 2.4 kHz
between them already reaches one standard deviation.

## Research before any hardware case

Each item names its falsifier. None sends a provider job; a step that would
gets its own approved case under AGENTS.md.

1. **Direct coherent-fraction probes, designed in simulation.** The deciding
   quantities are the coherent tilt and static detuning of each path qubit
   and the conditional phase of each coupler; a Ramsey on each qubit reads
   its detuning. A CZ-phase probe repeats CZ pairs between a
   control prepared in 0 and 1 and a Ramsey target, so the error phase grows
   as 2 n phi; a tilt probe repeats an sx train whose ideal product is the
   identity between Ramsey analysis pulses. The design step simulates each
   probe on the snapshot and states the shots that resolve f = 0.2 and
   g = 0.7 at three standard deviations. Falsifier: a probe whose simulated
   response is not first order in its family is rejected before any case.
2. **Twirling as mitigation.** The idealized model, the Pauli twirl of each
   CZ's error with ideal frames, lowers CZ phase alone to 0.27 and 0.29 but
   leaves 1.07 and 1.20 jointly with tilt at its sx bound. IBM's runtime
   merges the twirl frames into the single-qubit layers, which changes the
   sx and x stream each tilt acts on; the next model samples twirled
   instances, compiles them to sx and rz, and applies tilt to the actual
   pulses. Falsifier: if the sampled-instance model leaves joint max_z above
   1 at f = 0.3, twirling is not a sufficient mitigation.
3. **Interleaving schedule.** The mismatch table bounds the drift a run
   tolerates; the run design states the interleave period against the
   atlas's measured drift rates. Falsifier: a measured drift above 2 kHz
   per interleave period on q0.
4. **Path choice.** The sweep ranks paths by their worst joint max_z at the
   bounds, which favors qubits with small sx and CZ errors over the
   readout-weighted cost of `primorial_cover_noise.path_costs`. A case names
   its path from a fresh calibration through this ranking.

A primorial hardware run measures the product of coherent tilt and CZ phase
on its path through a seven-coefficient fit, an indirect instrument for a
device property that items 1 and 3 measure directly. The run earns a case
only when those probes place the path inside the region where max_z stays
below 1, so that the primorial identification becomes the question the run
answers.
