# Encoded N=21 feedback on ibm_kingston: the scheduled-idle replay

[N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md](../N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md) records the preregistered
endpoint of job `dba8r7k24mrc738527d0`. The feedback contrast difference is +0.0027 with 95 % interval [-0.0129,
+0.0184], while the calibration model's exact value is +0.0310. That note names no mechanism. This document replays
the same executed circuits with the idle time the IBM service scheduler inserted written in as explicit delays.
The replay is an exploratory reanalysis of retained bytes; it runs no new hardware job.

## Mechanism the model omitted

`live_run.noise_simulator` builds `NoiseModel.from_backend`. Its gate errors carry relaxation over each gate's own
duration, and its one custom pass (`RelaxationNoisePass`) acts on explicit `delay` instructions only. The ISA
circuits carry no delays, so a qubit that waits while its neighbors play gates decoheres for free in the model.

The service's compiled schedule is retained in every PUB result
(`raw/dba8r7k24mrc738527d0/pub_01.json` and `pub_02.json`, `metadata.compilation.scheduler_timing`). It places the
circuit's instructions over 17,500 dt (70 us at 4 ns per dt) between the opening and closing resets. The three hub
qubits 105, 117 and 125 carry 737 to 813 scheduled instructions each. The four leaf qubits 104, 106, 124 and 126
carry 90 to 192 each and wait between them behind their hub's CZ chain, with 13 to 21 waits of 300 to 2,611 dt
each among many shorter ones. Summed per qubit, the waits the ISA never states are:

| Arm | 104 | 105 | 106 | 117 | 124 | 125 | 126 |
|---|---|---|---|---|---|---|---|
| feedback, dt | 14,323 | 6,651 | 14,486 | 7,535 | 14,757 | 7,769 | 15,351 |
| omitted correction, dt | 14,569 | 6,980 | 14,739 | 7,635 | 15,099 | 7,771 | 15,481 |

Each leaf qubit idles for 57 to 62 us of the 70 us circuit. The idle comes from routing serialization, not from
the feed-forward path: the omitted-correction arm has no broadcast and carries the same idle within 5 percent.

A list schedule under the execution Target's gate durations alone, with no service input, predicts the same idle
(`--local-schedule`, [local-idle-schedule.json](local-idle-schedule.json)). It falls within 5 percent of the
service on every leaf qubit and within 1 to 11 percent on the hubs, where the unmodeled measure and broadcast
latency sits. The idle is therefore a property of the routed circuit, predictable before submission.

## Replay

`scripts/scheduled_idle_replay.py` rebuilds each replica on its physical qubits and inserts, before every
scheduled instruction, the delay separating it from that qubit's previous instruction. It replays the result under
the noise model of the Target and properties at the PUB's execution start (`backend.target_history`), with the
record's declared initial excitation 0.014393 on every active qubit. The exact law comes from
`dynamic_density.probabilities` after Aer's relaxation pass writes each delay's channel in. The output is
[idle-replay.json](idle-replay.json). No parameter is fitted: the delays are the service's, and the relaxation rates
are the Target's.

| Quantity | Value |
|---|---|
| unpadded exact contrast (control) | +0.031039262580354 |
| record's exact contrast (`record.json` `exact_model`) | +0.031039262580353 |
| idle-padded exact contrast | -0.0007 |
| measured contrast difference | +0.0027, 95 % interval [-0.0129, +0.0184] |
| idle-padded sampled contrast (100,000 shots, `SEED_SIMULATOR`) | +0.0032 |
| sampled against exact, max per-outcome gap | 0.0020 against Hoeffding radius 0.0061 (tail 0.01) |

The control reproduces the record's exact model to 1e-15, so the padded value differs from it only by the inserted
delays. The falsifier, stated before the exact computation, was a padded exact contrast outside the measured
interval. The value -0.0007 lies inside it.

| Arm | measured law (b0 + 2 b1) | padded exact | unpadded exact | TVD to padded | TVD to unpadded |
|---|---|---|---|---|---|
| feedback | 0.2692, 0.2448, 0.2371, 0.2490 | 0.2721, 0.2541, 0.2242, 0.2496 | 0.2789, 0.2553, 0.2155, 0.2503 | 0.0129 | 0.0216 |
| omitted correction | 0.2654, 0.2452, 0.2373, 0.2521 | 0.2719, 0.2545, 0.2244, 0.2492 | 0.2790, 0.2398, 0.2154, 0.2658 | 0.0158 | 0.0273 |

## What the replay settles and what it leaves

- [O] The leaf-qubit idle that the scheduler inserts is enough, under the Target's own T1 and T2, to remove the
  feedback-dependent structure: the padded model predicts a contrast of zero to within 0.001.
- [O] Padding moves both arms' laws toward the measurement, and the distance to the measured law falls by 40
  percent on each arm.
- [O] A residual of 0.013 and 0.016 TVD remains, mostly outcome 2 (0.224 padded against 0.237 measured). At
  100,000 shots it lies well above the sampling floor. The idle-padded model adds incoherent idle only, so
  coherent idle error (detuning and ZZ during the waits) is not excluded and is the leading candidate for the
  residual. The Kingston QET runs of 2026-10-25 measured such a phase directly on other qubits
  ([frame diagnostic](../2026-10-25T225332.266272Z/FINDINGS.md)).
- [I] The three candidates the findings note listed are not needed to reach the null. Feed-forward latency and
  branch dephasing act on the feedback arm alone, and the idle that cancels the contrast acts on both arms. A
  mid-circuit measurement error above the reported assignment acts on both arms too; it is not excluded and not
  required.
- [I] Contrast near zero is a weak signature on its own, since any extra decoherence pushes it there. The replay's
  specificity is that it has no free parameter and that it also closes 40 percent of the law distance.

## Falsifier on hardware

The padded model makes a prediction no calibration-only model makes: the contrast depends on the leaf-qubit idle,
not on the feed-forward path. A placement or routing of the same encoded circuit that halves the leaf idle
should restore a contrast near the padded model's value for its schedule, and a null there refutes idle as the
mechanism. The service schedule exists only after compilation, so the plan needs an idle-aware prediction
before submission: a local schedule under the Target's durations, checked against this run's retained service
schedule. Such a run needs its own written case and approval.
