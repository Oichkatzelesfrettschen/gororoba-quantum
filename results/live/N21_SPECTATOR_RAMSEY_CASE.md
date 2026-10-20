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
1 to 6 windows of the control's measure plus reset idle (0, 3.344, 6.688,
10.032, 13.376, 16.72, 20.064 us), with the control in |0> and its
initialization herald conditioning every shot, and fits

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
for 143 at the 2026-10-19T18:42:31-07:00 calibration), an echo time. The
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
- Grid: a uniform lattice of one window. The largest exposure is 2.8 times
  the 7.2 us exponential T2* (4.1 times the 4.9 us Gaussian T) the retained
  point implies; the uniform spacing makes delta identifiable modulo
  1/3.344 us = 299 kHz, so |delta| < 149.5 kHz reads unaliased. Log spacing
  would open a wider final gap and shrink that band. The retained point's
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
- Cost: planner estimate 2.3 s job overhead + 11.20 s of shots x
  (rep_delay + schedule) = 13.50 s. One unplanned sub-job split adds about
  2 s and stays under 17 s.
- Ceiling: `--max-execution-seconds 30`, 2.2 times the estimate, so an
  overrun of the per-shot model ends the job well past the expected lock
  time rather than at it; `--max-total-execution-seconds 30`,
  `--reserve-seconds 0`, `--min-remaining-seconds 60`. The dry run read 166 s
  remaining.
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

## Dry run

Record [2026-10-20T020214.648950Z](2026-10-20T020214.648950Z/record.json),
planned from commit e0d435a with sources_modified false, under the
2026-10-19T18:42:31-07:00 ibm_fez calibration (window_delay_dt 415,
reset_dt 421, so one window is 836 dt):

- record.json sha256 `4f4b231fa5141019aae72d92753b130b85eb7deae0ca433012bdb06592b37a9d`
- isa.qpy sha256 `ed6094da6a282b2d5fc64ca678f63c107c565f1acc6eeddd701ac9b251c999dc`
- one dynamic job, 14 PUBs of 12288 shots, estimated charge 13.50 s
  (11.20 s of shots, 0.677 s for an immediate PUB to 0.923 s at 6 windows)
- budget plan admitted against 166 s remaining, ceiling 30 s
- policy twirl false, dd null, rep_delay 5e-05 s; `control_flow` empty

## Preregistered analysis

`"$PYTHON" scripts/n21_spectator_ramsey.py RUN_DIR --out RUN_DIR/ramsey.json
--expected-analyzer-sha256 3744b701f3de5dfad448c9a458717733c679d1c0882c2624fbe5066d5129230b` after `--collect`, and
`--check` regenerates it from the archived raw files.

1. Admissibility (returned scheduler timing): every member reads one
   spectator other than the control; immediate exposes it 0 dt, idle_ground
   at m exposes it exactly m x window dt across a control delay of the same
   length with no pulse on the control before the readout; every member
   plays exactly two spectator pulses before its readout. A failure leaves
   every test not_admissible.
2. Shots: only those whose initialization herald reads the control 0.
3. Family alpha 0.05, Bonferroni over three events, 0.0167 each: the
   spectator herald admission (n21_orbit_rca.herald_report over the 14
   members on those shots), the detuning test and the decay-shape test. A
   refused herald leaves both tests not_admissible.
4. Fits: free beta, beta = 1 and beta = 2, each over all 28 binomial reads,
   starts spread over the alias band, the estimate of delta folded into it;
   Wald intervals from the expected Fisher information at the estimate.
5. Detuning: "detuned" when the two-sided 0.0167 interval of delta (free
   beta) excludes 0, else "unresolved"; the sign convention is that rz(+theta)
   on qubit 2 advances phi by +theta (self-check plant through the built
   circuits).
6. Shape: the two-sided 0.0167 interval of beta; "exponential" if it holds
   1 and not 2, "gaussian" if 2 and not 1, "unresolved" if both, "neither"
   if neither. T2* is reported from all three fits; the verdict names
   which one describes the decay.

Expected precision at the design (Fisher information at noise-free counts,
`--design`, two-sided 0.0167 half-widths):

| Truth | T2* | beta | delta | A |
|---|---|---|---|---|
| exponential, T2* 7.2 us, delta 0 | +-0.44 us | +-0.065 | +-1.66 kHz | +-0.025 |
| Gaussian, T 4.9 us, delta 0 | +-0.13 us | +-0.13 | +-1.80 kHz | +-0.008 |

So the shape rule separates beta = 1 from 2 by more than ten half-widths,
and a 7 kHz detuning, the retained point's phase reading, sits about four
half-widths from 0.

Self-check (gate core-601) plants: an exponential and a Gaussian truth
reach their shapes with delta unresolved; a 40 kHz truth reads detuned; a
rz(+2 pi 0.03 MHz t) inserted into the built circuits reads +0.03 MHz; an
added 30 percent of shots that herald the control 1 with a 0.3 MHz turn
moves the unconditioned fit off the plant while the conditioned fit
recovers it; an empty herald selection reads not_evaluable; a decoupling
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
  --approved-record ../results/live/2026-10-20T020214.648950Z/record.json \
  --approved-record-sha256 4f4b231fa5141019aae72d92753b130b85eb7deae0ca433012bdb06592b37a9d
```

## Failure modes considered

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
