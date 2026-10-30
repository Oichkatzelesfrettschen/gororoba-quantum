# Findings: primorial coherence case, stage 1 on ibm_kingston path 0-1-2

The approved case [PRIMORIAL_COHERENCE_CASE.md](PRIMORIAL_COHERENCE_CASE.md) ran its first stage, the coherence
probes, as job `dbfdotnpc3tc739n8nm0` on ibm_kingston physical qubits 0, 1 and 2 (backup instance, 800 shots on
each of 98 circuits, approved record `2026-10-26T044954.431433Z`, run record `2026-10-26T045124.175747Z`). The
job billed 23 s against the case's 27.5 s estimate. Every circuit executed under the 2026-10-25T21:37:46-07:00
calibration, the calibration of both approval dry runs and of the snapshot the decision would read, and none
changed during its shots.

## Stage 1 voids on qubit 0; stage 2 is not sent

The case's preregistered voiding rule (a wire whose in-job readout calibration gives 1 - e10 - e01 below 0.8
voids its estimates, and a void estimate stops the case) fires on physical qubit 0. Its in-job readout
calibration read |0> as 1 in 629 of 800 shots (e10 = 0.786) and |1> as 0 in 86 (e01 = 0.108), so
1 - e10 - e01 = 0.106. The same calibration reported e10 = 0.006 and e01 = 0.009 for qubit 0, and qubits 1 and
2 read normally in the same job (e10 = 0.000 and 0.004, e01 = 0.024 and 0.013). The summary's own one-shot flip
variance for wire 0, 0.168 = e10 (1 - e10), agrees with the raw counts.

The void reaches beyond qubit 0's own estimates. Every middle-qubit Ramsey arm keeps only shots whose outer
qubits read as prepared, and the coupler-(0, 1) pair probe keeps shots on qubit 0's readout, so detuning_q0,
detuning_q1, both ZZ rates, cz_raw_c0 and both ZZ-corrected CZ phases rest on the voided readout. Following the
preregistration, stage 2 (the gap-88 tomography) is not sent, and no decision record is written.

## Estimates that stand on qubits 1 and 2

These estimates are descriptive and outside the preregistered decision, which the void stopped. The tilt cells
of the middle qubit and of the outer pair read each wire through its own readout, the coupler-(1, 2) pair probe
postselects on qubit 2 only, and the outer Ramsey arm keeps every shot; the summary's derivatives of these
estimates with respect to qubit 0's assignment flips are zero. They rest on qubits whose readout passed:

| estimate | value (rad) | standard error at 800 shots | gate-error bound | fraction of bound | share of the gate infidelity |
| --- | ---: | ---: | ---: | ---: | ---: |
| sx tilt, qubit 1 | -0.00087 | 0.00018 | 0.0223 | 0.039 | 0.0015 |
| x tilt, qubit 1 | -0.00124 | 0.00017 | 0.0158 | 0.079 | 0.0062 |
| sx tilt, qubit 2 | +0.00158 | 0.00016 | 0.0196 | 0.080 | 0.0064 |
| x tilt, qubit 2 | -0.00040 | 0.00018 | 0.0139 | 0.029 | 0.0008 |
| raw CZ conditional phase, coupler (1, 2) | +0.0192 | 0.0009 | 0.0780 | 0.246 | 0.061 |
| static detuning, qubit 2 (kHz) | -2.40 | 0.49 | none | | |

The raw CZ phase omits the partner-in-0 ZZ share, at most 2 pi x 68 ns x zeta, 0.0026 rad for a 6 kHz ZZ.
Coherent tilt carries under 1 percent of the sx and x infidelity on these qubits and the conditional phase about
6 percent of the CZ infidelity, and qubit 2's static detuning is 2.4 kHz, inside the 5 to 30 kHz range the
repository's Fez fits found. The joint-bound record's coherent-fraction scan
([primorial-cover-joint-coherent-bounds.md](../../docs/design/primorial-cover-joint-coherent-bounds.md)) puts
that region (f near 0.1, g near 0.25) near max_z 0.1, but the scan was computed on other paths under an older
snapshot, scales all three qubits together and holds no detuning; qubit 0, coupler (0, 1), the detuning of
qubits 0 and 1 and both ZZ rates are unmeasured here.

## Deviation from the preregistration

The preregistration names `groups[0].summary` of the collected record as the decision's input; in the collected
layout that summary sits at `collect.json[1].measured_statistics.summary`. It is the same raw summary with the
in-job readout inversion only, which `probe-summary.json` holds; the analysis choice is unchanged. The stage-2
approval dry run `2026-10-26T045028.853944Z` was never consumed, and its approval does not carry to another path.

## Consequences

- Qubit 0's readout fault is a device finding in its own right: the calibration the job ran under reported a
  0.6 percent assignment error on a qubit that read |0> as 1 in 79 percent of shots. The in-job readout
  calibration of the probe design caught it before any gap-88 time was spent.
- The probe design works on hardware: the tilt cells, the pair probe and the readout inversion gave estimates
  with the standard errors the probe-case record predicted (0.00016 to 0.00018 rad of tilt, 0.0009 rad of CZ
  phase at 800 shots).
- A decision on the gap-88 tomography needs a path whose three qubits pass the readout rule. A re-run on another
  path is a new case and needs a fresh approval; the case allowed no path change.

A re-retrieval of job `dbfdotnpc3tc739n8nm0` through `live_run.py --preserve-raw` on 2026-10-27 returned the 101
retained raw files byte for byte. The backup-instance inventory observed on 2026-10-27 covers the job, and
`docs/state/research_state.json` registers it as acquisition `kingston-primorial-coherence-case1` under claim
`kingston-primorial-case1-q0-readout-void`. The submitted-circuit comparison reads the primary instance's audit
only, so the backup observation leaves it unchanged.
