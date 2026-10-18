# Written case: bracketed n21-orbit-rca windows on ibm_fez

Status: UNAPPROVED and parked while IBM QPU time stays reserved. This file
authorizes nothing and submits nothing.

## Binding

- Dry run: this directory, `record.json` SHA-256
  `bee44f51e6eff892294bf9da2e0fafac3a2776fe0b58d923482cf626fa7d8a9e`,
  source commit `656e944`, `sources_modified=false`.
- Plan: one dynamic job of 8 PUBs on ibm_fez, 8192 shots per PUB, template
  layout `[25, 23, 24, 22]`, executed qubits `[101, 121, 116, 120]`,
  transpiler seed 20261014, 48 routed CZ per member.
- Seconds: the cost model predicts 20.0 s with 2.3 s of job overhead; the
  service ceiling (`--max-execution-seconds`) is 30 s and the invocation cap
  30 s, against 266 s the account reported remaining.
- `UNAPPROVED_CASE.md` beside this file carries the generated endpoints, the
  ideal laws and the exact `--submit` command with `--approved-record` and
  `--approved-record-sha256`.

## What the run measures

Every arm brackets the control's measurement and reset with barriers over
all qubits, so each multiplier round compiles on one side of the window
(`qpe_diagnostics.window_bracket_violations`, gate core-446). The run tests
whether that bracket gives every member one physical window structure on
hardware: `scripts/n21_orbit_rca.py --between-arm RUN` reports the members'
probed couplings, and the family is admissible when all eight equal the
nominal feed-forward member's (no-feedback members up to their global
sign). On an admissible run the three preregistered contracts decide:

1. window_delay's work phase lies on the nominal pair's phase-per-exposure
   slope, inside its profile-likelihood set at alpha 0.05/3;
2. extra_readout's contrast magnitude hypot(fb1 - fb3, nf3 - nf1) reaches the
   nominal magnitude times exp(-sum t_q / T2_q) over the added idle;
3. window_echo's magnitude reaches the nominal one.

## Why noise simulation cannot answer it

- `window_roles` keys each qubit's window on the schedule IBM returns in
  `metadata.compilation.scheduler_timing`; a local schedule places
  work-only pulses by its own ALAP rule, so it cannot stand in for the
  returned one.
- The contracts measure a coherent work phase. Backend properties carry no
  qubit frequency, so a calibration noise model holds no detuning and
  predicts phase zero in every arm.
- The retained unbracketed run (2026-10-13T083417.634585Z) is
  `not_admissible`: five members differ from the nominal feed-forward
  coupling, which is the structure the bracket removes.

## Falsifiers

- The issue's own: with bracketed arms, `--between-arm` still reports
  `not_admissible`. That would mean the returned schedule moves work
  qubits' roles across the window despite the barriers.
- Routed CZ: the plan's 48 per member is 11.6 percent above the retained
  plan's 43. On one fresh ibm_fez snapshot the bracket costs one CZ per arm
  at both layouts (43 to 44 at the retained `[2, 4, 3, 16]`, 47 to 48 at
  `[25, 23, 24, 22]`), so 4 of the 5 added CZ come from the layout scorer
  choosing a different region under the newer calibration, not from the
  barriers. The 5 percent bound on the barrier's own cost holds; the
  plan-to-plan comparison exceeds it and is stated here rather than hidden.
