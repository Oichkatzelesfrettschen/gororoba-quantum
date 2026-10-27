# N=21 orbit detuning-sign test: the calibration-adaptive approval envelope

This case asks approval for a rule and its bounds, not for one calibration's values, as the window-dose sweep's
envelope did ([n21-orbit-window-dose-envelope.md](n21-orbit-window-dose-envelope.md)).
`scripts/n21_detuning_sign_run.sh --submit` plans on the calibration in force, checks the plan against this
envelope with `scripts/n21_detuning_sign.py --preflight`, and submits that plan. The layout, the replica sets and
the model values are the fresh plan's own; the bounds below are enforced by the preflight, the runner or
live_run.py, and a plan outside any of them sends nothing.

## Question

The window-dose sweep on ibm_kingston (job `dbg04idjm0ks73efj0j0`, 19 replicas, 86 s billed) left a residual in its
free-idle arm that its one-rate decay family does not describe (chi2 427 on 5). Split into its parts, the
no-feedback member's law shows the relaxation offset at the Target model's value at every dose and a coherence
that turns with the dose: per replica, the measured coherence over the modeled one is a cosine of the dose at
4 to 30 kHz with rms residual 0.02 to 0.07, and the Hahn echo holds each replica at its undosed value (correlation
0.986 across 19 replicas). Routing the controlled swaps moves the logical roles, so the compiled program, not the
logical circuit, names the qubits: a Z turn on one physical qubit during the dose moves the coherence only on each
replica's initial-layout positions 0 and 3, in all 19 replicas (exact evaluation of the retained ISA). During the
dose each replica holds one excitation shared between those two qubits; its other two qubits are in |0>, and no
superposed qubit neighbors another replica's qubit, so a ZZ term gives both branches the same phase and cannot turn
their relative phase. What remains is a frame offset of each of the two qubits, its frequency off the frame the
gates track, which turns the relative phase at the offset of the qubit holding the bit for 16 minus that of the
qubit holding the bit for 1.

The sweep read only the cosine of that phase, so it gives the rate's magnitude without its sign, and the
idle-penalty probe's Ramsey offsets come from another calibration, so they cannot be compared replica by replica.
This run measures both in one job: the orbit's relative phase in two quadratures over a dose sweep, and each work
bit's own Ramsey phase over the same idles. The frame-offset account predicts f_orbit = f_sixteen - f_one for every
replica, with its sign. A noise simulation cannot answer it: the Target carries no frame offset, so any simulation
built from it predicts zero for every term of the comparison.

## Circuit

The `n21-orbit-rca` family with `--init-herald --window-doses-dt D,D,... --detuning-sign`, built by
`diagnostic_experiments.n21_detuning_sign_group`. At every dose D:
- `window_dose` without feed-forward, the sweep's free-idle member: after the control's mid-circuit measurement
  and reset, a barrier, `delay(D)` on all four wires and a barrier, then the second round, read as the parity of
  the two phase bits (the cosine of the relative phase);
- `window_dose_y`, the same circuit with P(-pi/2) on the control where the feedback member conditions it, so the
  second round reads the sine;
- `n21_work_ramsey_{one,sixteen}_{x,y}`: H on the qubit that holds the work bit for 1 or for 16 during the dose,
  the other qubits in |0>, a barrier, `delay(D)` on all four wires, a barrier, then H (X) or Sdg H (Y) and a
  readout of that qubit.

A Ramsey arm has no two-qubit gate, so its logical qubit k stays on initial-layout position k, while routing moves
the orbit's roles. The planner therefore locates the roles in the compiled orbit arms (`qpu_planning.dose_roles`):
it turns each initial qubit by 0.4 rad during the dose, evaluates both quadratures exactly, and requires a turn of
+1 on one qubit (the bit for 16), -1 on another (the bit for 1) and 0 on the other two, identical at every nonzero
dose. It rebuilds the Ramsey arms on those logical indices, requires each to turn with its own qubit alone, and
records the indices as `dose_roles` in the family configuration, which `--submit` binds with the rest of the
approved record. On FakeFez the roles fall on positions 3 and 1 of the pinned layout and on 0 and 3 of the
planner's own, so no fixed assignment serves.

At the largest dose the echo member, `window_dose_echo` and `window_dose_echo_y`, spends the dose as
`delay(D/4) X delay(D/2) X delay(D/4)` on the work bits for 1 and 16. The members run dose by dose, the orbit and
Ramsey readings of one dose next to each other, so drift over the job enters each dose's readings alike. None of the members feeds forward, so the
service runs the replicas in parallel and the planner's timing holds (the sweep's 3.6x underrun came from the
serialized feed-forward branches). The initialization herald measures every qubit before the circuit and makes
every member dynamic, so all PUBs share one job and one calibration; the analysis keeps only shots whose herald
reads all zeros. `tests/gororoba_quantum/test_detuning_sign.py` evaluates every member exactly: each keeps its
ideal law, a Z rotation on the bit for 16 (for 1) during the dose turns the orbit's quadrature pair by plus (minus)
its angle, a rotation of a work bit turns its own Ramsey pair by plus its angle and leaves the other bit's at zero,
and the echo returns the undosed phase; `qpu_planning_contracts._verify_detuning_sign_plan` checks the role probe
on compiled FakeFez plans, and that an arm moved to another qubit fails it.

## Bounds

| Bound | Value | Enforced by |
|---|---|---|
| Backends | ibm_fez, ibm_kingston, ibm_marrakesh | preflight (`DESIGN_BACKENDS`) |
| Account | the primary, whose remaining seconds exceed the 40 s ceiling; the backup only when they do not, named in the case | runner (`GOROROBA_IBM_ACCOUNT`) |
| Doses | 0 to 14,016 dt in steps of 1,752 dt (7.008 us), nine doses | preflight (`EXPECTED_DESIGN`) |
| Members | 56, one PUB each, in one dynamic job | preflight (`DESIGN_MEMBERS`, budget plan) |
| Shots | 4,096 per PUB | preflight, runner |
| Replicas | tier 24, floor 0.45, at least 8 placed | preflight, live_run.py |
| Repetition delay | 20 us, then 50 us when no 20 us plan is admitted | runner, preflight (`DESIGN_REP_DELAYS`) |
| Ceiling | 40 s per job and in total | live_run.py, preflight |
| Search | one routed candidate, 8 layout seeds | preflight |
| Seeds | `docs/evidence/outshift_qrng/draw-2026-10-27T154654Z.json` index 0 (layout), 1 (simulator), bytes bound by SHA-256 | preflight |
| Tree | the plan's commit unmodified under every directory that builds, seeds, checks or submits it | runner, preflight |

The planner prices a member's Target duration plus the repetition delay per shot. Without feed-forward the service
runs the packed replicas in parallel; the measurement-sequence envelope's 88-PUB dynamic job of mid-circuit
measurements and resets, also without feed-forward, billed within 1 percent of the same model, so the 40 s ceiling
holds the 50 us fallback with margin. The 2.3 s job overhead is the model's.

The calibration refusals of the window-dose envelope carry over unchanged: `--submit` compares the fresh plan's
calibration values with the approved record's and writes an `approval_required` record that sends nothing when
any differs, and the runner then plans again, up to four times.

## Decisions

`scripts/n21_detuning_sign.py RUN` writes the decisions; its docstring is the specification and its `--self-test`
decides synthetic sweeps of 19 replicas at 4096 shots: the frame-offset account holds, and a reversed sign, the
sum of the offsets, an unrelated rate and an echo that keeps the precession each decide against it.

Each member's herald-kept counts give a quadrature: an orbit member's control contrast given b0 = 0 minus that
given b0 = 1, which cancels the relaxation offset both branches share, and a Ramsey member's X or Y. A phase is
atan2(sine, cosine) with its delta-method error; phases unwrap along the dose order over the leading doses whose
amplitude exceeds three standard errors, and a weighted line through at least four of them gives the rate, its
error scaled by sqrt(max(1, chi2/df)). The dose spacing of about 7 us leaves rates up to 71 kHz unambiguous; each
fit reports its largest phase step between doses, and a step near pi marks a rate at that limit.

- D1, slope: the weighted line through the origin of f_orbit on f_sixteen - f_one across replicas with all three
  rates. It holds when its 95 percent interval lies inside [0.8, 1.2] and is refuted when the interval misses that
  band; at least six replicas. A line with a free intercept is reported beside it, so a rate common to every
  replica shows as an intercept rather than a moved slope.
- D2, sign: among replicas whose prediction and orbit rate both exceed three standard errors, the fraction with
  agreeing signs; at least 0.9 holds, below 0.75 refutes (random signs give 0.5); at least six resolved replicas.
- D3, echo: among replicas whose free-idle phase moved by more than three standard errors over the sweep (the
  fitted rate times the largest dose, which a whole number of turns cannot hide) and whose echo and undosed
  amplitudes both exceed three standard errors, the fraction whose echo phase at the largest dose lies within three
  standard errors of the undosed phase; at least 0.8 reads as precession during the dose, at least six such
  replicas. An unresolved amplitude leaves a phase error wide enough to accept any return, so those replicas are
  counted and left out.

A refuted D1 or D2 leaves the sweep's residual without a mechanism and reopens it: a frequency shift of a work bit
that depends on whether the other holds the excitation (an exchange term through their coupler), or one the
orbit's own gates set, would make the orbit and the Ramsey rates differ.

## Plan at the dry run

`sh scripts/n21_detuning_sign_run.sh` on the primary account at commit `d50cd17` planned dry run
`2026-10-27T171005.467816Z` on ibm_kingston at calibration 2026-10-27T09:07:55-07:00 and the preflight admitted it:
19 replicas, the 20 us repetition delay, 56 PUBs of 4,096 shots in one dynamic job under a 40 s ceiling, estimated
charge 15.35 s against 101 s remaining on the primary instance, in 292 s of planning. The planner bound `dose_roles`
one = 0, sixteen = 3. Its compiled program is byte-identical to that of the dry run at `9ae65a9`, whose Ramsey arms
compiled serially, so the pooled rebuild changes no circuit.
An exact probe of the planned ISA, a 0.4 rad turn on each physical qubit of every replica during the largest dose,
moved the orbit's quadrature pair by +1 turn on the qubit bound to the bit for 16, -1 on the qubit for 1 and 0 on
the other two, and each Ramsey arm by +1 on its own qubit alone, in 19 of 19 replicas. The record is not retained;
`--submit` plans again on the calibration in force and binds that plan.

## Result

Kingston job `dbge2jpj4t8s73ac6fk0` ran this envelope on 2026-10-27 and all three decisions hold: slope 1.010
[0.977, 1.043] over 18 replicas, 17 of 17 signs agree, 17 of 17 echoes return. The
[findings](../../results/live/2026-10-27T173602.753176Z/FINDINGS.md) carry every replica's rates and the limits.
