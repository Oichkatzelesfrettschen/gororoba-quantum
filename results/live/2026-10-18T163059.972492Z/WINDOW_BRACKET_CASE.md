# Written case: bracketed n21-orbit-rca windows on ibm_fez

Status: UNAPPROVED. This file authorizes nothing and submits nothing. It
supersedes the case of `results/live/2026-10-18T062500.711287Z`, whose
calibration and quota figures are stale.

## Binding

- Dry run: this directory, `record.json` SHA-256
  `d43ee2ec981d0bbe6276a6cf2a205ab1cfc6510cb231640688ed70e72f583171`,
  source commit `04f707d`, `sources_modified=false`.
- Plan: one dynamic job of 8 PUBs on ibm_fez (calibration
  2026-10-18T08:40:01-07:00), 7040 shots per PUB, template layout
  `[2, 4, 3, 16]`, executed qubits `[136, 142, 143, 144]`, 44 routed CZ per
  member.
- Seconds: the cost model predicts 17.52 s, 2.3 s of it job overhead. The
  service ceiling (`--max-execution-seconds`) and the invocation cap are
  both 22 s, and the account reported 218 s remaining.
- `UNAPPROVED_CASE.md` beside this file carries the generated endpoints, the
  ideal laws and the exact `--submit` command with `--approved-record` and
  `--approved-record-sha256`.

## What the run measures

Every arm brackets the control's measurement and reset with barriers over
all qubits, so each multiplier round compiles on one side of the window. On
this record's ISA `qpe_diagnostics.window_bracket_violations` finds none in
all eight members (window_echo with its echo X pulses inside the window, as
gate core-446 checks). The run tests whether the bracket gives every member
one physical window structure on hardware:
`scripts/n21_orbit_rca.py --between-arm RUN` reports the members' probed
couplings, and the family is admissible when all eight equal the nominal
feedback member's (no-feedback members up to their global sign). On an
admissible run the three preregistered contracts decide, at alpha 0.05/3:

1. window_delay's work phase lies on the nominal pair's phase-per-exposure
   slope, inside its profile-likelihood set;
2. extra_readout's contrast magnitude hypot(fb1 - fb3, nf3 - nf1) reaches the
   nominal magnitude times exp(-sum t_q / T2_q) over the added idle;
3. window_echo's magnitude reaches the nominal one.

## Why noise simulation cannot answer it

- `window_roles` keys each qubit's window on the schedule IBM returns in
  `metadata.compilation.scheduler_timing`; a local schedule places
  work-only pulses by its own ALAP rule, so it cannot stand in for the
  returned one. IBM's server-side `dry_run=True` returns no schedule on this
  account (`results/live/2026-10-12T054229.702537Z/native-validation.json`,
  `QiskitBackendNotFoundError`).
- The contracts measure a coherent work phase. Backend properties carry no
  qubit frequency, so a calibration noise model holds no detuning and
  predicts phase zero in every arm.
- The retained unbracketed run (2026-10-13T083417.634585Z) is
  `not_admissible`: five members differ from the nominal feedback coupling,
  which is the structure the bracket removes.
- Tuna-17 cannot answer it: its compiler runs gates in the written order, so
  the bracket holds trivially, and it has no binary-controlled gate, so the
  feedback arms become post-processing.

## Run-time choices

`docs/local/reports/n21-window-bracket-runtime-study.md` decomposes the
charge: the 250 us repetition delay is 82 percent, the job overhead 11
percent and the circuits 3.4 percent.
- Shots: 7040 per PUB replaces 8192. The planner's Hoeffding power rule on
  the four per-arm feedback contrasts admits 7040 at 131072 model shots
  (`--shot-tiers 7040 --model-shots 131072`). The between-arm contracts'
  minimum detectable deficit at power 0.8 rises from 0.032 to 0.035, and the
  extra_readout per-arm endpoint's detection probability on the retained
  hardware contrasts falls from 0.995 to 0.97. Levels, statistics and rules
  are unchanged.
- The fitted billing rule predicts 17 s billed, against 20 s at 8192.
- Kept: the 250 us repetition delay (no initialization control exists for
  these Fez qubits, and PR #258 measured a shot-history effect on Kingston
  at the scale of the 0.035 deficit), init_qubits on, standard measure and
  reset (measure_2 changes the window under test), one job in job mode.
  Dynamical decoupling and twirling are refused on circuits with if_else.

## Falsifiers

- The issue's own: with bracketed arms, `--between-arm` still reports
  `not_admissible`. That would mean the returned schedule moves work
  qubits' roles across the window despite the barriers.
- Routed CZ: 44 per member equals the retained unbracketed plan's
  layout-[2, 4, 3, 16] count plus the bracket's one CZ, and the topology
  minimum on heavy-hex at optimization level 3.
