# Case: Ramsey delay sweep of ibm_fez qubit 143 with the control grounded

Status: written case awaiting the user's approval. Nothing in this file
authorizes a submission.

## What it measures

The ground-control split ([N21_ORBIT_RCA.md](N21_ORBIT_RCA.md), "Spectator
dephasing with the control grounded") found qubit 143 losing 0.367 of its
Ramsey visibility across one 836 dt (3.344 us) idle with the control 142
held in |0>, and bounded the control-state-dependent ZZ share at about 11
percent of the window loss. One exposure cannot separate a decay law or a
coherent detuning. This sweep reads 143 in X and Y at seven exposures, 0 and
1 to 6 windows (0, 3.344, 6.688, 10.032, 13.376, 16.72, 20.064 us). A
window is a length, 836 dt, equal to 142's calibrated measure plus reset
durations; during it 142 idles in |0> and is neither measured nor reset.
Every shot is conditioned on its initialization herald, and the sweep fits

    <X>(t) = b + A exp(-(t/T2*)^beta) cos(2 pi delta t + phi0)
    <Y>(t) = b + A exp(-(t/T2*)^beta) sin(2 pi delta t + phi0)

jointly by binomial maximum likelihood (scripts/n21_spectator_ramsey.py).
An oscillating phase (delta resolved) names a coherent detuning that a frame
correction or the delay-X-delay-X echo cancels; beta near 2 names
quasi-static Gaussian frequency noise and beta near 1 a Markovian dephasing
rate; both bear on whether the work-qubit echo of the Mitigation section
recovers the window loss.

## Why simulation cannot answer it

The quantity is a property of the physical qubit 143. The noise model that
live_run.py builds from the calibration carries the reported T2 (110.9 us
for 143 at the 2026-10-19T18:56:47-07:00 calibration), an echo time. The
dry run's Aer prediction reads visibility 0.993 at every exposure out to
20 us, while the retained hardware read 0.622 at 3.344 us: the decay this
case measures is absent from every model the repository can build without
hardware data. The sweep is a device question on a named qubit, the
AGENTS.md criterion for IBM hardware below 16 qubits.

## Design

- Backend and layout: ibm_fez, `--pin-layout ibm_fez:142,136,143,144`
  (control 142, spectator 143 as logical qubit 2), the layout of the
  retained ground split, so the 1-window point repeats its idle_ground arm.
- Circuits: 14 members, one PUB each, one dynamic job:
  `n21_spectator_immediate_{x,y}` and `n21_spectator_idle_ground_w{m}_{x,y}`
  for m = 1..6. Each heralds all four qubits, prepares 143 with H behind a
  barrier, idles the control `m * (window_delay_dt + reset_dt)` = m x 836 dt
  in |0> between barriers, reads 143 in X (h) or Y (sdg, h), then resets the
  control behind a barrier. The delays are integers in dt from the Target's
  measure and reset durations of 142 (dt 4 ns, granularity 1, min_length 2).
- Immediate point: the control is prepared in |+> (the split's immediate
  arm, kept byte for byte) and the spectator's exposure is 0, so the
  control's state cannot act on it; this point pins A and phi0.
- Grid: a uniform lattice of one window. The largest exposure is 2.8 times
  the 7.2 us exponential T2* (4.1 times the 4.9 us Gaussian T) the retained
  point implies; the uniform spacing makes delta identifiable modulo
  1/3.344 us = 299 kHz, so |delta| < 149.5 kHz reads unaliased. Log spacing
  would open a wider final gap and shrink that band. The band is 1 / (2
  spacing) for the lattice spacing, dt times the gcd of every exposure in
  dt, here one window; delta folds into it because every exposure is an
  integer multiple of that spacing. The retained point's
  phase turn, atan2 of idle_ground (0.615, 0.089) minus immediate
  (0.989, -0.008), is 0.151 rad, about 7 kHz modulo 299 kHz.
- Shots: 12288 per PUB, 172,032 in all, `--rep-delay 5e-05`.
- Repetition delay: 50 us, the value of the retained ground split, which
  billed the 5 s its plan charged, and of the Kingston control jobs that ran
  in 11 to 14 s ([REP_DELAY_ZERO_CONTROL_FINDINGS.md](REP_DELAY_ZERO_CONTROL_FINDINGS.md));
  the 1305 failures there were 0 us jobs below the documented 20 us floor
  and 20 us jobs whose shots overran a 6 s ceiling. The initialization
  herald reads every qubit before each shot, so the shorter delay's
  residual excitation is measured and conditioned on rather than assumed.
  At the 250 us default the same 15 s buys about 56k shots, half the
  precision.
- Cost: the planner's estimate is 2.3 s job overhead + 11.20 s of shots x
  (rep_delay + schedule) = 13.50 s. It omits the per-shot INIT/FINI
  sequence of about 8.85 us, which adds 172,032 x 8.85 us = 1.52 s, so the
  expected bill is about 15.0 s, and about 17 s if the service splits the
  job once (about 2 s per sub-job). The planner is left unchanged.
- Ceiling: `--max-execution-seconds 30` and `--max-total-execution-seconds
  30`, `--reserve-seconds 0`, `--min-remaining-seconds 60`. The retained
  ground-split job dbba739gv2cc73e81dg0 (raw/.../job_metrics.json) reports
  circuits_execution_time 3.153 s against 2.815 s of planned shot time, a
  ratio of 1.12 (0.97 once its 49,152 x 8.85 us INIT/FINI is added), and a
  charge of 5 s against 5.12 s planned; its 190 s from running to finished
  under a 15 s ceiling shows the ceiling binds QPU time, not wall time.
  Scaled to this job: 11.20 s x 1.12 = 12.57 s + 2.3 s overhead + 2 s for
  one sub-job split = 16.9 s; 1.5 x 16.9 = 25.3 s stays below 30, so the
  ceiling stays at 30 s, 1.78 times the scaled lock time.
- Twirling off, dynamical decoupling none (policy `twirl` false, `dd` null):
  every member is dynamic (the final control reset), IBM's Sampler rejects
  DD on dynamic circuits, and a DD pulse on 143 would turn the Ramsey into
  an echo. The compiled ISA plays only measure, sx, rz on 143 (herald,
  preparation, basis change, readout) and no delay instruction, gate core-602
  holds that shape on FakeFez, and the analyzer refuses a returned schedule
  with any third pulse on the spectator before its readout.
- Dynamic-circuit limits: no `if_else`, loop, switch or classical store
  (`control_flow` empty in the record), 6 classical bits per circuit, no
  broadcast; the reset is the only dynamic operation.

## Approval record and envelope

The binding approved record is the submit-free dry run made from main
after this change merges, immediately before `--submit`, with the command
below minus `--submit` and its approval flags. Its record.json path and
sha256 replace RECORD_DIR and RECORD_SHA256 in the submit command. That
record, approval-consumed.json, the collection, ramsey.json and the
regenerated retention audit land together in the post-run results change.

This case approves the envelope: 14 members of the structure above
(immediate and idle_ground at 1 to 6 windows, X and Y, all-qubit herald,
pinned layout), 12288 shots per PUB, the policy above (rep_delay 50 us,
twirl off, dd none, 30 s ceilings) and an expected bill of at most about
17 s. A dry run whose window moves from 836 dt, whose circuits differ in
structure, or whose estimated charge exceeds 13.5 s needs a fresh user
approval. The policy design carries `ramsey_analyzer_sha256`, the sha256
of scripts/n21_spectator_ramsey.py, so an analyzer changed after the
approved dry run makes the approved record's policy differ and the
submission refuse with approval_required (gate core-602).

The development dry run (from this branch, 2026-10-19T18:56:47-07:00
calibration) planned one dynamic job of 14 PUBs, estimated charge 13.50 s
(0.677 s for an immediate PUB to 0.923 s at 6 windows), 166 s remaining,
policy twirl false, dd null, `control_flow` empty; it is not retained.

## Preregistered analysis

`"$PYTHON" scripts/n21_spectator_ramsey.py RUN_DIR --out RUN_DIR/ramsey.json
--expected-analyzer-sha256 0f54ade5b8d4351dcaabbb26749ea742588a616198a7dc93901ac4f20f2df09b` after `--collect`, and
`--check` regenerates it from the archived raw files.

1. Admissibility (returned scheduler timing): every member reads one
   spectator other than the control; immediate exposes it 0 dt, idle_ground
   at m exposes it exactly m x window dt across a control delay of the same
   length with no pulse on the control before the readout; every member
   plays exactly two spectator pulses before its readout. A failure leaves
   every test not_admissible.
2. Shots (primary): only those whose initialization herald reads all four
   pinned qubits 0. On the Fez coupling map
   (docs/evidence/heron_platform/targets.json, cz qargs) 143 couples to
   136, 142 and 144, every other pinned qubit, so an excited neighbor of
   any role shifts 143's frequency by its ZZ; 136 and 142 are not coupled
   to each other. The control-only selection (herald reads 142 0) is fitted
   too and reported as secondary, descriptive.
3. Family alpha: the record's policy.design alpha (0.05 here; a record
   without one is refused), Bonferroni over four events, 0.0125 each:
   herald admission, the detuning test, the decay-shape test and the
   ringdown consistency test. The admission reads each pinned bit's
   excited fraction per member among the shots whose other herald bits
   read 0, through that qubit's asymmetric assignment channel
   (prob_meas1_prep0, prob_meas0_prep1) in each member's execution
   calibration, and refuses when any bit's member spread exceeds
   herald_bound; n21_orbit_rca.herald_evaluation splits the 0.0125 over
   every bit and ordered member pair. A refusal leaves the other tests
   not_admissible. The per-bit spread over the control-zero shots is
   reported descriptively.
4. Fits: free beta, beta = 1 and beta = 2, each over all 28 binomial reads,
   starts spread over the alias band, the estimate of delta folded into it;
   Wald intervals from the expected Fisher information at the estimate.
   The search parameterizes A = u (1 - |b|) with u in [0, 1], so every
   candidate's means lie inside (-1, 1) and neither the likelihood nor the
   information clips one. An information eigenvalue below 1e-10 of the
   largest marks an unidentified direction; a decision whose parameter
   (delta, or beta and T2*) has weight on it, or whose interval is wider
   than the alias band or the beta search range, reads not_evaluable.
5. Detuning: "detuned" when the two-sided 0.0125 interval of delta (free
   beta) excludes 0, else "unresolved"; the sign convention is that rz(+theta)
   on qubit 2 advances phi by +theta (self-check plant through the built
   circuits).
6. Shape: the two-sided 0.0125 interval of beta; "exponential" if it holds
   1 and not 2, "gaussian" if 2 and not 1, "unresolved" if both, "neither"
   if neither. T2* is reported from all three fits; the verdict names
   which one describes the decay. The shape test's power assumes the
   retained 7.2 us decay; a much shorter or longer T2* puts beta near a
   bound or makes it weakly identified, and the Wald interval then reads
   unresolved rather than a shape.
7. Ringdown consistency: the 1 to 6 window points alone are fitted at
   beta = 1 and beta = 2, and the fit with the larger likelihood predicts
   the immediate pair as b + A (cos phi0, sin phi0), offset and phase
   included. The measured immediate (<X>, <Y>) minus that prediction is
   tested jointly, chi-square on 2 degrees of freedom over the binomial
   variances plus the prediction's delta-method covariance, at 0.0125:
   "consistent" when accepted, "transient" when refused with the measured
   pair farther from b than predicted (visibility lost before the first
   idle, the herald back-action signature), "excess" otherwise. A transient verdict makes the decay
   fit describe the stationary decay after the transient, not T2* from
   preparation.

Expected precision at the design (Fisher information at noise-free counts,
`--design`, two-sided 0.0125 half-widths):

| Truth | T2* | beta | delta | A |
|---|---|---|---|---|
| exponential, T2* 7.2 us, delta 0 | +-0.46 us | +-0.068 | +-1.7 kHz | +-0.026 |
| Gaussian, T 4.9 us, delta 0 | +-0.13 us | +-0.14 | +-1.9 kHz | +-0.009 |

So the shape rule separates beta = 1 from 2 by more than ten half-widths,
and a 7 kHz detuning, the retained point's phase reading, sits about four
half-widths from 0.

Self-check (gate core-601) plants: an exponential and a Gaussian truth
reach their shapes with delta unresolved; a 40 kHz truth reads detuned; pure exponential and Gaussian decays pass
the ringdown test and 20 percent lost with a 0.4 us time constant on top
of the 7.2 us exponential fails it; a 15 percent subpopulation heralding work
bit 1 excited with a 0.1 MHz ZZ shift moves the control-only fit to beta
0.71 and T2* 6.45 us while the all-zero fit stays at beta 1.000, T2* 7.200; a
rz(+2 pi 0.03 MHz t) inserted into the built circuits reads +0.03 MHz; an
added 30 percent of shots that herald the control 1 with a 0.3 MHz turn
moves the unconditioned fit off the plant while the conditioned fit
recovers it; a zero-visibility truth reads both decisions not_evaluable;
counts drawn exactly from the model with offset 0.03 and phi0 0 read
ringdown-consistent at 4.2 million shots; windows 1, 3 and 4 give the
one-window band and recover a 100 kHz detuning; one herald bit rising and
another falling between members, the any-bit fraction fixed, refuses the
admission; an empty herald selection reads not_evaluable; a decoupling
pulse, a short idle or a prepared control refuses admissibility.

## Submit command

From gororoba_quantum/, after approval:

```sh
"$PYTHON" live_run.py --family n21-orbit-rca --shot-allocation uniform \
  --objective minimum_charge --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 --simulation-memory-mb 512 --optimize \
  --backends ibm_fez --shots 12288 --seeds 8 --max-pending 25 \
  --min-remaining-seconds 60.0 --max-execution-seconds 30 --rep-delay 5e-05 \
  --no-isolated-reference --cross-group-buffer --shot-tiers 12288 \
  --replica-tiers 1 --optimizer-candidates 6 --model-shots 131072 \
  --precision 0.08 --alpha 0.05 --power 0.8 --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 --classical-latency-us 20.0 \
  --reserve-seconds 0.0 --max-total-execution-seconds 30.0 \
  --init-herald --ground-control-split --ramsey-windows 1,2,3,4,5,6 \
  --pin-layout ibm_fez:142,136,143,144 --out ../results/live --submit \
  --approved-record ../results/live/RECORD_DIR/record.json \
  --approved-record-sha256 RECORD_SHA256
```

## Failure modes considered

- Herald readout back-action: every shot starts with readouts of all four
  qubits, and the readout resonator ringdown, its AC-Stark shift and
  measurement-induced dephasing after the herald act on 143 at the start
  of its Ramsey. That is a named confound of the short T2* against the
  110.9 us echo T2: a time-dependent shift during the first microseconds
  shows as beta below 1 or a "neither" shape, and a constant phase it
  imparts is absorbed into phi0. The separating follow-up arm repeats the
  sweep with a fixed idle inserted between the herald barrier and 143's
  preparation (or without the herald); a confound moves the early points
  and beta, an intrinsic decay does not.

- 1305 ceiling cancellation: 30 s ceiling against 13.5 s expected; the
  50 us delay has completed on Heron r2 jobs of this account.
- Sub-job split: 14 PUBs of 12288 shots is about 3.5 times the retained
  job's shot executions; a split adds about 2 s of overhead per sub-job.
- Calibration change between the dry run and the submission: the approval
  binds calibration values (fingerprint); a changed measure or reset
  duration on 142 changes the window, the circuits and the QPY bytes, and
  the submission refuses with approval_required. A new dry run and an
  updated case follow.
- Queue drift inside the job: PUB execution order is not guaranteed, so a
  drift of 143's frequency during the job enters the exposures in an
  unknown order; `--collect` records each PUB's execution calibration.
- Herald refusal: the 14-member spread test is the one #315 passed with
  six members; a refusal leaves the fit not_admissible and spends the
  seconds.
- TLS or frequency jump on 143 between the retained run and this one: the
  1-window point repeats the retained idle_ground arm, so a large change
  of its visibility from 0.622 is visible before any fit is read.
- n21_orbit_rca.py on this record: its ground shape matches any
  idle_ground name, finds the sweep's members outside its six-member set
  and reads every contract not_admissible; n21_spectator_ramsey.py is the
  analyzer of record.
