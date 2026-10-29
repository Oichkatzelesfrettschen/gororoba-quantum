# Local idle padding of ISA circuits

`NoiseModel.from_backend` relaxes a qubit only during its own gates and explicit top-level `delay` instructions
(its `RelaxationNoisePass`). An ISA circuit states no delay, so a qubit that waits behind its neighbors relaxes for
free in every model prediction. `gororoba_quantum/idle_padding.py` schedules the circuit under the Target's gate
durations alone and writes each wait in as a dt delay, so the prediction charges the idle before submission. Two
placements exist: `asap` starts every instruction as early as its qubits and condition bits allow, and `alap` places
it as late as the ASAP makespan allows, honoring the same qubit and classical-bit order. The retained
`scheduler_timing` tables show that IBM's scheduler plays ALAP; a sibling analysis of those tables matched ALAP
first-instruction times within 1 dt on every qubit of the encoded N=21 run, and the comparison below confirms it on
the law.

This bundle answers issue 526's preregistered falsifier (ASAP padding) and sets the padding against competing
error sources. `idle_budget.json` of [ghost_error_scale](../ghost_error_scale/README.md) and `ghost_event_scale.py`'s
pad axis charge the idle the service schedule recorded after execution; this bundle's padding needs only the circuit
and the Target, which is what a planner holds before submission.

## Files

| File | Producer | Content |
| --- | --- | --- |
| [result.json](result.json) | `scripts/local_idle_falsifier.py --runs all` | per run and replica: unpadded and ASAP-padded exact laws, TV distances to hardware, inserted idle; the decision |
| [controls.json](controls.json) | `scripts/local_idle_controls.py --runs ...` | mean TV distance per run under every control arm, per replica beneath |
| [service_comparison.json](service_comparison.json) | `scripts/local_idle_controls.py --service-replay` | encoded N=21: unpadded, local ASAP, local ALAP and service-padded laws on matched baselines |

Every law is exact: `dynamic_density.probabilities` on the replica restricted to its active qubits, under the
member's execution calibration snapshot (`docs/evidence/calibration/history/`), after
`scheduled_idle_replay.relaxed` turns each top-level delay into relaxation channels. Exact laws carry no shot noise,
and no script draws a seed. A member whose replicas a structural check refuses, or whose control-flow body holds a
qubit the top-level circuit never touches (`restrict_circuit` refuses it), is listed under `members_refused` and
left out. Every file records its qiskit, qiskit-aer and numpy versions; the falsifier's laws are identical to 9
digits under qiskit 2.5.2 and 2.6.0.

## Preregistered falsifier

Issue 526 (criterion posted before the sweep, issue comment 6406212933): per replica,
d = TV(measured, ASAP-padded) - TV(measured, unpadded); a run passes when its mean d is negative, and the sweep
passes when a strict majority of eligible runs does. Runs with a mean d more than two standard errors above zero are
listed.

| Run | Backend | Replicas | Unpadded TV | Padded TV | Mean d | SE |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-11T152922 | kingston | 29 | 0.1009 | 0.0782 | -0.0227 | 0.0049 |
| 2026-10-12T055624 | kingston | 16 | 0.1374 | 0.0945 | -0.0429 | 0.0041 |
| 2026-10-13T020454 | kingston | 4 | 0.1874 | 0.1201 | -0.0673 | 0.0012 |
| 2026-10-13T022433 | kingston | 4 | 0.2118 | 0.1445 | -0.0673 | 0.0012 |
| 2026-10-13T080216 | fez | 2 | 0.0698 | 0.0544 | -0.0154 | 0.0080 |
| 2026-10-13T083417 | fez | 8 | 0.0695 | 0.0545 | -0.0150 | 0.0040 |
| 2026-10-13T201757 | fez | 6 | 0.0343 | 0.0292 | -0.0051 | 0.0038 |
| 2026-10-18T083403 | kingston | 149 | 0.0021 | 0.0021 | 0 | 0 |
| 2026-10-18T083404.226285 | kingston | 149 | 0.0030 | 0.0030 | 0 | 0 |
| 2026-10-18T090603 | kingston | 2 | 0.0256 | 0.0189 | -0.0067 | 0.0006 |
| 2026-10-18T214519 | kingston | 148 | 0.0061 | 0.0061 | 0 | 0 |
| 2026-10-19T151959 | fez | 14 | 0.1312 | 0.1222 | -0.0090 | 0.0023 |
| 2026-10-19T170620 | fez | 12 | 0.1471 | 0.1389 | -0.0082 | 0.0025 |
| 2026-10-19T231043 | fez | 6 | 0.0849 | 0.0800 | -0.0049 | 0.0031 |
| 2026-10-20T031212 | fez | 14 | 0.3224 | 0.3015 | -0.0209 | 0.0079 |
| 2026-10-21T043156 | marrakesh | 48 | 0.5047 | 0.5047 | 0 | 0 |
FALSIFIER_TAIL

The three one-qubit state-preparation controls carry no wait, so padding inserts nothing and d is exactly 0; they
count as not lower. The four-qubit segmented spectator runs 2026-10-21T043156 and 2026-10-21T064222 are the same
case: each qubit plays its own measure, reset and single-qubit segments with no CZ, so `idle_padding.pad` inserts no
idle into any of their 48 replicas and both laws coincide. Their distance of about 0.5 reflects 1536 shots spread over 15
classical bits (32768 outcomes), a sampling floor that padding cannot move. On the 2026-10-26 and 2026-10-27 idle-penalty
runs padding inserts idle into 372 of 1364 and 390 of 1320 replicas, and on the 2026-10-27T173602 orbit-window
dose run into 988 of 1064; every other replica enters the rule at d = 0. Twelve of the first sixteen scored runs are
lower, so the strict majority holds whatever the last four show. 2026-10-13T020454 and 2026-10-13T022433 execute the same circuits under the same snapshot, and
the hardware law lies on the same side of both model laws in every outcome, so their d agree while their distances
differ. The other runs record why they are out (no dynamic member, no job returned shots, no member with an exact
law).

The pass fixes a direction, not a mechanism: any decoherence added to an optimistic model moves it toward hardware.
The controls below test the mechanism.

## Local placement against the service schedule

On the encoded N=21 run (2026-10-18T090603), both sources carry the record's declared prep excitation 0.014393, so
their unpadded laws coincide exactly (TV 0). ASAP padding's inserted idle plus the circuit's own delays equals
`scheduled_idle_replay.list_schedule_idle` on all seven qubits of both arms, and the per-qubit totals of ASAP, ALAP
and the service schedule agree within 5 percent.

| Arm | Unpadded TV | Local ASAP | Local ALAP | Service schedule | ALAP to service law |
| --- | --- | --- | --- | --- | --- |
| feedback | 0.0216 | 0.0158 | 0.0129 | 0.0129 | 4.8e-5 TV |
| omitted correction | 0.0273 | 0.0219 | 0.0158 | 0.0158 | 1.1e-5 TV |

Same totals, different placement, different law: ASAP closes 27 and 20 percent of the unpadded distance, ALAP and
the service close 40 and 42 percent. The omitted-correction arm has no feed-forward broadcast and shows the larger
gap, so measure-to-branch latency does not cause it (a 109-cycle branch latency moved neither placement in the
sibling analysis). Local ALAP reproduces the service-padded law from the circuit and Target alone, so a planner can
charge the idle the hardware will play before it submits.

## Controls

[controls.json](controls.json) holds, for the twelve multi-qubit runs above, the mean TV distance under each arm:
inserted idle scaled by kappa under ASAP (`kappa`) and ALAP (`alap`); every reported CZ error times c, unpadded
(`cz`, `ghost_error_scale.scaled`) and on the ASAP-padded replica (`cz_pad`); placement placebos that put each
qubit's ASAP total in one delay after its first played instruction (`front`) or shift the totals one qubit along
(`permuted`); and an X flip of probability m before each mid-circuit measurement and after each reset on the
ASAP-padded replica (`event`, `ghost_event_scale.with_events`).

| Run | Unpadded | ASAP k=1 | ALAP k=1 | ALAP k=2 / 3 / 5 | Best CZ factor | Front k=1 | Best event |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10-11T152922 kingston | 0.1009 | 0.0782 | 0.0792 | 0.0596 / 0.0453 / 0.0374 | 0.0329 (c 5) | 0.0748 | 0.0706 (m 0.05) |
| 10-12T055624 kingston | 0.1374 | 0.0945 | 0.0959 | 0.0603 / 0.0342 / 0.0640 | 0.0571 (c 3) | 0.0947 | 0.0609 (m 0.1) |
| 10-13T020454 kingston | 0.1874 | 0.1201 | 0.1235 | 0.0673 / 0.0188 / 0.0645 | 0.0263 (c 5) | 0.1125 | 0.0474 (m 0.1) |
| 10-13T022433 kingston | 0.2118 | 0.1445 | 0.1479 | 0.0917 / 0.0422 / 0.0408 | 0.0447 (c 5) | 0.1368 | 0.0502 (m 0.1) |
| 10-13T080216 fez | 0.0698 | 0.0544 | 0.0531 | 0.0385 / 0.0284 / 0.0381 | 0.0251 (c 5) | 0.0753 | 0.0327 (m 0.05) |
| 10-13T083417 fez | 0.0695 | 0.0545 | 0.0533 | 0.0395 / 0.0287 / 0.0217 | 0.0332 (c 5) | 0.0745 | 0.0354 (m 0.05) |
| 10-13T201757 fez | 0.0343 | 0.0292 | 0.0286 | 0.0251 / 0.0252 / 0.0316 | 0.0314 (c 2) | 0.0342 | 0.0295 (m 0.01) |
| 10-18T090603 kingston | 0.0256 | 0.0189 | 0.0142 | 0.0134 / 0.0129 / 0.0127 | 0.0104 (c 2) | 0.0330 | 0.0141 (m 0.1) |
| 10-19T151959 fez | 0.1312 | 0.1222 | 0.1225 | 0.1150 / 0.1092 / 0.1052 | 0.0845 (c 8) | 0.1312 | 0.1255 (m 0.01) |
| 10-19T170620 fez | 0.1471 | 0.1389 | 0.1391 | 0.1332 / 0.1276 / 0.1186 | 0.1124 (c 8) | 0.1471 | 0.1459 (m 0.01) |
| 10-19T231043 fez | 0.0849 | 0.0800 | 0.0800 | 0.0753 / 0.0707 / 0.0620 | 0.0849 (c 1.5) | 0.0849 | 0.0864 (m 0.01) |
| 10-20T031212 fez | 0.3224 | 0.3015 | 0.3015 | 0.2830 / 0.2669 / 0.2401 | 0.3224 (c 1.5) | 0.3224 | 0.3065 (m 0.01) |

Readings:

- Placement carries information where the fit is sharp. ASAP padding at kappa 1 closes 15 to 36 percent of the
  unpadded distance on the runs of 10-11 to 10-18 and 6 to 7 percent on those of 10-19 and 10-20. On the 10-13 Fez
  orbit runs and encoded N=21, the front-loaded placebo (the same per-qubit totals in one early delay) moves the law
  away from hardware (-7 to -29 percent at kappa 1, -18 to -132 percent at kappa 3) while the scheduled idle closes
  15 to 26 percent. On the Kingston runs of 10-11 to 10-13, both placebos close as much as the schedule at kappa 1
  (25 to 42 percent against 22 to 36), but at kappa 3 the schedule closes 58 to 95 percent against 17 to 47 for the
  placebos, so the kappa 3 minimum belongs to the scheduled placement. On the CZ-free spectator runs and the
  reset-led orbit runs of 10-19 the front delay falls where the qubit rests in |0>, and both placebos equal the
  unpadded law.
- ALAP and ASAP differ little except where long waits sit behind a CZ chain: on encoded N=21, ALAP gives 0.0142
  against ASAP's 0.0189.
- On the Kingston QPE and correction runs on qubits 73 to 95 (10-12T055624, 10-13T020454 and its repeat
  10-13T022433), the idle scale has an interior minimum at kappa 3 under both placements, and it beats every CZ
  factor and the joint arm (CZ factor 3 on the padded replica): 0.0342 against 0.0571, 0.0188 against 0.0263, 0.0422
  against 0.0447. The repeat pair reproduces the minimum's location. On these runs the model's missing error acts
  like idle charged at three times the Target's T1 and T2. Both runs sit under one reported calibration, whose
  median T1 over those qubits (255 us) exceeds the adjacent days' 208 to 214 us, so an optimistic calibration
  supplies part of that factor (about 1.2 of it if T1 alone carried it).
- On the Fez orbit-window runs of 10-19 a CZ factor at the grid top (c 8) fits better than any idle scale, as
  ghost_error_scale part e found (c 12, grid top); on 10-13T080216 and 10-11T152922 the CZ factor wins narrowly,
  and on 10-13T083417 and 10-13T201757 the idle scale wins (0.0217 against 0.0332, 0.0251 against 0.0314). The
  missing error therefore has no single form across runs.
- On encoded N=21 the ALAP curve is flat from kappa 2 to 5 (0.0134 to 0.0127) and the CZ factor 2 fits best
  (0.0104), so this run does not resolve an idle excess. The latency-recovery acquisition on Kingston qubits 104 to
  125 (2026-10-25, `results/live/LATENCY_RECOVERY_FINDINGS.md`) measured a decay-only coherence time of 38 to 40 us
  against 65 to 67 us predicted, a factor of about 1.7, beside a coherent -13 kHz phase.
- The CZ-free spectator runs (10-19T231043, 10-20T031212) improve only along the idle axis; the y arms of the
  Ramsey sweep carry a coherent precession that no incoherent arm reaches (`hw-n21-spectator-143-beat`).
- The event flip helps less than the best idle or CZ arm on every run.

The grids are coarse (kappa 1, 2, 3, 5; c 1.5 to 8), so a best grid point bounds a minimum's location to its
neighbors, and the comparison is between one-parameter families rather than at a matched noise budget.

## Replay

`"$PYTHON" scripts/local_idle_falsifier.py --check docs/evidence/local_idle_padding/result.json --runs RUN` reruns
the named runs and requires each summary to equal the retained one exactly; `--runs all` reruns every run. Gate
CHECK_GATE_PR reruns 2026-10-13T080216 on pull requests and CHECK_GATE_FULL reruns every run in the full tier.
`tests/gororoba_quantum/test_idle_padding.py` holds the schedule contracts.

The sweep ran on the build host's CPU (exact laws of one to seven qubits, seconds per law), as ghost_error_scale
parts d, e and f did.
