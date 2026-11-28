# Native Qiskit and runtime features as opt-in local comparisons

Four local tools compare a native IBM feature against the unchanged submission path. Each runs offline, sends no
job, and changes no default of live_run.py: approval binding, digests and records stay in repository code, and a
native feature enters a submission only as an opt-in that the record captures.

Evidence class: build and local-simulation measurements on qiskit 2.6.2, qiskit-ibm-runtime 0.51.0 and qiskit-aer
0.18.2. Every number below is a one-run exploratory value with the stated shots; none is a hardware result.

## Stretch exists in Qiskit 2.6.2

A gap report claimed that the installed Qiskit has no stretch. The installed package holds it:
`QuantumCircuit.add_stretch`, a `Delay` whose duration is a `Stretch` or an `expr` Duration expression
(`expr.mul`, `expr.add`, `Duration.dt`), and a transpile of a stretch delay against the Heron Target that keeps
the delay symbolic. `tests/test_qiskit_stretch_support.py` checks each. The open work of
[QPU_EXECUTION_ROADMAP.md](../../../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) item 3 is the echo design and its
evidence, never client support.

## Dynamical decoupling: `scripts/ibm_dd_compare.py`

The tool compiles a named experiment group once, schedules it as late as possible, and builds two arms from the same
idle windows: delay padding only (what the service plays) and the runtime's own DD pass manager
(`qiskit_ibm_runtime.executor.dynamical_decoupling.generate_dd_pass_manager`; XX, XpXm, XY4). Both arms simulate on
the density-matrix noise model of `live_run.noise_simulator`. Control flow is refused, as the runtime refuses DD there.

Mechanism result. The Target's noise model relaxes qubits by memoryless T1 and T2 channels. A refocusing pulse cannot
undo a memoryless channel, so the model charges DD its pulse error and credits it nothing. The `--detuning-hz`
option adds the mechanism DD exists for, a quasi-static Z detuning (an rz of 2 pi f t after every delay, conjugated
by the circuit's own X pulses), labeled in the report as a model input.

| Row (fake_fez Target, 4000 shots) | baseline | XX | XpXm | XY4 |
|---|---|---|---|---|
| `design_a_1_2` total variation to ideal, memoryless noise | 0.0707 | 0.0800 | 0.0813 | 0.0720 |
| same row, modeled detuning 78.125 kHz | 0.2760 | 0.0825 | 0.0845 | 0.0873 |

Standard error of each entry is about 0.003. The reading: on a 1233 dt (4.9 us) static group, DD costs up to 0.01 under
the memoryless model and recovers a modeled quasi-static detuning completely. Whether the device carries such a
detuning on the placed qubits is a hardware question that this tool cannot answer; the retained idle-schedule runs
([evidence/local_idle_padding](../../evidence/local_idle_padding/README.md)) are the matching data. The shipped
tests pin the structural facts (the baseline plays no pulse, DD keeps the duration, DD refocuses the modeled detuning,
memoryless noise gives DD no credit).

Open items. `--backend live:NAME` reads a free live calibration through `take_snapshot`; it is written but not run
in this change. The measurements above are unseeded; a retained run takes its seeds from a QRNG draw through the CLI flags.

## Fractional gates: `scripts/ibm_fractional_compare.py`

The tool builds the standard and the fractional Target from `docs/evidence/heron_platform/targets.json` (calibration
2026-10-14 for ibm_fez) and compiles five Heron multiprogramming circuits for both.

| Circuit | CZ-basis 2q gates | fractional 2q gates | duration ratio | gate-error budget ratio |
|---|---|---|---|---|
| k5 LCU zero-product witness | 68 | 56 | 0.787 | 0.729 |
| k10 Steane Z syndrome patch (control flow) | 36 | 36 | n/a | 0.962 |
| k2 Bell delay probe | 2 | 2 | 1.000 | 1.000 |
| k7 sedenion associator witness | 721 | 651 (451 cz, 200 rzz) | 0.827 | 0.938 |
| Ising rzz and rx chain (6 qubits, 3 steps) | 30 | 15 rzz | 0.724 | 0.446 |

The budget is the sum of -log(1 - e) over the gates with a Target error, so it ranks compiles and is no fidelity
estimate. No compile produced an rzz outside (0, pi/2]. The Ising chain is the workload fractional gates were built
for; the algebra circuits gain through rx only (k5, k7) or not at all (k2).

Incompatibilities, from [fractional-gates.md](fractional-gates.md): Pauli twirling, probabilistic error
cancellation and probabilistic error amplification are unsupported on fractional circuits, TREX is supported, the
transpiler optimizes rzz only partly, and an rzz outside (0, pi/2] fails at the service. A fractional compile is
therefore an intervention with its own controls, never a silent substitution into an approved case.

## EstimatorV2 resilience: design note and `scripts/ibm_resilience_local_check.py`

Where expectation values arise. The repository submits Sampler jobs and forms expectation values from counts:
`experiments.z_expectation` and `odr_p1` (gororoba_quantum/experiments.py, lines 243 to 255) read <Z> of a measured
bit, `design_a` and `zero_divisor_fringe` fit fringes of those values, and the signed-kernel and Ramsey-contrast rows
reduce counts the same way. Our own readout correction is `live_run.readout_corrected` (the measure-mitigation
construction without twirling) and the mirror-twin ratio of `odr_p1` (an attenuation correction the native
options lack).

What the native options would change. Runtime 0.50 and later move resilience to the client Estimator
(`executor_estimator`, options `ResilienceOptions`: `measure_mitigation`, `zne_mitigation` with
`ZneOptions.noise_factors` default (1, 3, 5) and extrapolators exponential and linear, `pec_mitigation`); the
server-side `EstimatorV2` is deprecated. A move to an Estimator PUB needs observables in place of counts, drops our
shot-level records (raw counts stay only in the Sampler path), and multiplies quantum time by the noise-factor sum.

Local check on `design_a_1_2` (ideal <Z> = -1, 20000 shots per factor, fake_fez Target noise, unseeded):

| noise factor | raw <Z> | readout-corrected <Z> | circuit duration (dt) |
|---|---|---|---|
| 1 | -0.8482 | -0.8563 | 1227 |
| 3 | -0.6065 | -0.6134 | 2901 |
| 5 | -0.4386 | -0.4447 | 4575 |

Extrapolated to zero noise: raw linear -0.9383, raw exponential -0.9984; readout-corrected linear -0.9468,
exponential -1.0067. The quantum-time ratio against one unmitigated circuit is 7.09. Reading: readout inversion
moves <Z> by 0.008; folding plus an exponential fit removes the 15 percent gate and idle attenuation, and costs seven
times the quantum time on the 600 s rolling window. The local noise is memoryless by construction, which is the
assumption ZNE extrapolation needs; a device with non-Markovian or drifting noise can break the fit, and only a
paired hardware case with a mirror control decides that. The construction is an equivalent of the technique on a
simulated channel, never the service implementation.

Recommendation: keep resilience out of the approved paths. A static row that reads <Z> and has quota to spare is the
first candidate for a written case that pairs a mitigated and an unmitigated arm at equal total charge.
