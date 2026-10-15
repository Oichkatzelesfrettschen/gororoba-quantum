# QPU program: ripple, rank sectors and the coherence window on ibm_kingston

The program is three fixed live_run.py commands with 146 s of service
ceilings: ripple under `--max-total-execution-seconds 74` (2 x 37 s jobs),
rank sectors under 54 (2 x 27 s) and the coherence window under 18
(2 x 9 s). No command names a backend or a qubit: each omits `--backends`
and `--patch-qubits`, so the planner scores every accessible backend and,
for the coherence window, every calibrated patch embedding, and chooses by
calibration. The owner approved the program on 2026-10-15; each case ran as
a fresh dry run at source `e4389c1` (experiment digest `aa49bbd65c82`)
followed at once by its approval-only command, and all six jobs ran on
ibm_kingston for 110 s of settled charge.

## Acquisition

| Case | Approved dry run (SHA-256 of record.json) | Submitted run | Jobs (settled s) | Charge / nominal (s) |
|---|---|---|---|---:|
| coherence window | [2026-10-15T030638.929111Z](2026-10-15T030638.929111Z/UNAPPROVED_CASE.md) `135dcac7e2c98c04f5a699926f506567a90ee0535ce35c280f880672384d7781` | [2026-10-15T030748.903241Z](2026-10-15T030748.903241Z/collect.json) | db847nur6oqs7388nen0 (5), db847oiraffc73fbmfk0 (8) | 13 / 12.51 |
| rank sectors | [2026-10-15T030638.132007Z](2026-10-15T030638.132007Z/UNAPPROVED_CASE.md) `fbc8826e6dfcd3924ab57f076912b7cc7edbf3675916e5dea7d2e9c18415f6e9` | [2026-10-15T030903.235380Z](2026-10-15T030903.235380Z/collect.json) | db848h6r6oqs7388nfm0 (6), db848hmil99s73fp99tg (25) | 31 / 30.45 |
| ripple | [2026-10-15T030638.321696Z](2026-10-15T030638.321696Z/UNAPPROVED_CASE.md) `9f0d50a404b7596b35cb495a72b0b5d4a48173434179437696e7093e24cb1e7f` | [2026-10-15T031229.371738Z](2026-10-15T031229.371738Z/collect.json) | db84dt6il99s73fp9gjg (35), db84dv2raffc73fbmnag (31) | 66 / 64.28 |

Every case planned on ibm_kingston calibration 2026-10-14 19:47:44 PDT
(ibm_fez in maintenance), passed the approved-record comparison, and wrote
`approval-consumed.json` into its dry-run directory. Five jobs executed under
that calibration. Ripple's second job (26 PUBs at 4096 shots) waited in the
queue through Kingston's 20:25:34 PDT recalibration and executed under it.
The account reported 320 of 600 s used and 280 s remaining after
collection; `qpu-job-inventory.json` and `qpu-job-retention-audit.json` bind
all 21 jobs, with 110 s reported as `later_program_charge_seconds`.

## Results

- **Rank sectors transfer.** The preregistered analysis (196 contracts,
  collect.json) rejects 20 nulls on ibm_kingston, the same 20 as on ibm_fez
  (8 sector bright-minus-dark and 12 pulse differences), every one with the
  same sign. Sector 4 is weaker on Kingston: bright minus dark 0.507 against
  0.868, and its `pulse_zero_two` `t3d2 - t2d1` difference 0.137 has a
  two-sided interval reaching -0.001 while the directional test at the
  one-sided radius still rejects.
- **Ripple transfers under a calibration-scoped secondary analysis.** The
  collector withheld the family analysis because the PUBs spanned two
  calibrations. `scripts/calibration_scoped_family_analysis.py` (gate
  core-266) evaluates each preregistered contract with the PUBs of a single
  execution calibration at its preregistered alpha: 1137 of 1138 contracts
  qualify and one cross-job packing difference
  (`ripple_design_c_16_1_8_isolated_packed_difference`) stays withheld. The
  84 box-kite bright-minus-dark contrasts reject their nulls, the same set
  as on ibm_fez with the same signs (median 0.695 against 0.605). The
  depth-4 class return contrast is -0.019 [-0.093, +0.056] against a
  detection radius of 0.072, null retained as on Fez. This analysis is
  secondary; collect.json keeps the collector's withheld verdict.
- **Coherence window.** The five preregistered precision contracts measure
  4 Re C = 1.653 [1.500, 1.806] at immediate readout; the matched idle moves
  4 C by -1.034 [-1.357, -0.711] in Re and -1.341 [-1.664, -1.018] in Im;
  the mid-circuit measure and reset adds 0.090 [-0.233, 0.413] and 0.001
  [-0.322, 0.324] relative to the matched idle, so no preregistered
  measurement-induced change is resolved. Descriptively
  (`coherence-analysis.json`), |C| is 0.413 immediate and 0.375 after the
  idle (ratio 0.907), the idle rotates C by -1.130 rad over 4.4 us of added
  exposure, and the measure-and-reset context rotates it by a further
  +0.054 rad [0.002, 0.105] with identical exposure. The branch-unsigned
  negative control, zero on an ideal device, reaches a modulus of 0.043 to
  0.065 across the contexts; against |C| = 0.375 that bias can rotate C by up
  to about 0.17 rad, so the +0.054 rad is not a resolved measurement-induced
  phase.

## Planning at source 71decdf

All four records below were planned at source `71decdf` with
`sources_modified=false` and experiment digest `8d7979af7d27`. ibm_fez
reported maintenance (67 pending jobs) throughout, and ibm_marrakesh had 3
pending jobs.

| Record | Case | Outcome | Record SHA-256 |
|---|---|---|---|
| [2026-10-15T013255.787315Z](2026-10-15T013255.787315Z/record.json) | rank sectors | `design_infeasible` on ibm_marrakesh; ibm_kingston skipped at 109 pending, above `--max-pending 60` | `94226058c08db80bffb66bde56e766673b533fdb2a317554eef2d1a0b82dea68` |
| [2026-10-15T013256.246642Z](2026-10-15T013256.246642Z/UNAPPROVED_CASE.md) | coherence window | planned on ibm_marrakesh, patch 92, 98, 91, 90, 111, 89, joint score 0.660, nominal 12.56 s; ibm_kingston skipped at 109 pending, above `--max-pending 100` | `e0f9a714718630091fca5d6353df1497c6733e332d78a09de68aae945cd562be` |
| [2026-10-15T013528.988943Z](2026-10-15T013528.988943Z/record.json) | coherence window, submit against 013256 | `approval_required`; nothing sent | `0bd6b15dc32492e90734c302ab2739d1caf267392f70cf2bfa14b5cdd4652309` |
| [2026-10-15T013647.977610Z](2026-10-15T013647.977610Z/UNAPPROVED_CASE.md) | coherence window | planned on ibm_kingston (calibration 2026-10-14 18:27:34 PDT, 85 pending), patch 57, 68, 67, 66, 69, 65, joint score 0.746 dynamic and 0.784 static, nominal 12.51 s | `b57fb093b3a88d60d9b2f06711d16c6379c2b13cd591b520aa0483d376d1a546` |

Ripple wrote no record directory: with ibm_kingston above `--max-pending 25`
the only eligible backend was ibm_marrakesh, where the runner stopped with
"the experiment family has no admitted routed candidate". Rank sectors on
ibm_marrakesh fail one preregistered contrast: at 4096 shots the sector 4
`pulse_one_two` `t1d2 - t1d1` difference cannot detect its reported
alternative at the declared alpha and power. `SHA256SUMS` in each case
directory binds record.json, isa.qpy and UNAPPROVED_CASE.md.

## Queue-dependent placement

`live_run.Snapshot.ineligible_reason` excludes a backend whose pending-job
count exceeds `--max-pending`, and that count is read again at every plan.
The coherence submit against record 013256 re-planned two and a half
minutes after it: ibm_kingston's queue had fallen from 109 to 85, below the
limit of 100, so the fresh plan moved to Kingston's higher-scoring patch.
The comparison with the approved record listed 13 mismatches (backend,
layout, replica qubits, calibration, fused PUB manifests and QPY bytes),
and the runner wrote `approval_required` and sent nothing. Record 013647
is the dry run of the same command one minute later, by which time
Kingston had also recalibrated. The refusal was correct, but a queue that
crosses a `--max-pending` limit between a dry run and its submit could move
the plan. `live_run.approved_backend_scope` now plans a submission over the
approved record's eligible backends only: a backend outside that set is
recorded as `outside_approved_scope` without a probe, while an approved
backend that changes or turns ineligible still refuses through the record
comparison. That source change moves the experiment digest, so the four
records above need fresh dry runs before any approval.

ibm_kingston admitted ripple and rank sectors in the 2026-10-14T22:05Z dry
runs at source `dac1f2e` (ripple 64.28 s nominal and 68.88 s stress, rank
30.45 s and 35.05 s, every observable admitted). Those records are retained
in the repository history at commit `ff59e2a` and no longer match the
experiment digest. Under the unchanged commands, ripple needs Kingston at
25 or fewer pending jobs, or ibm_fez out of maintenance; rank sectors need
Kingston at 60 or fewer.

## What each case measures

- **Ripple and rank sectors** replicate the 2026-10-13 ibm_fez acquisitions
  (CAMPAIGN_FINDINGS.md sections 5 and 6) on a second Heron r2 processor.
  The incremental question is transfer: whether the 84 box-kite, 8 sector
  and 12 pulse-difference contrasts that rejected their nulls on Fez
  reproduce on other hardware. A plan placed on ibm_fez is a repeat on the
  same device instead, and its case says so. They do not target the Fez
  union-template walk discrepancy.
  [KINGSTON_ALGEBRA_CASES.md](KINGSTON_ALGEBRA_CASES.md) carries the design
  search and the runtime levers.
- **Coherence window** measures the branch-signed work coherence the first
  N=21 orbit round leaves on the chosen patch, in three contexts: immediate
  readout, a matched idle, and a mid-circuit measure and reset of the
  control. Five precision contracts at half-width 0.33 on 4 C admit it on
  both backends. The analyzer reports a phase only where the joint
  (Re C, Im C) region excludes the origin, attributes a
  measurement-induced phase only after the signed per-qubit exposure,
  setting-specific and winding corrections, and reports both selected
  coherences with branch and spectator strata
  (scripts/coherence_window_analysis.py).
- **Earlier coherence cases.** Records
  [2026-10-14T060826.976518Z](2026-10-14T060826.976518Z/UNAPPROVED_CASE.md)
  and [2026-10-14T103147.847414Z](2026-10-14T103147.847414Z/UNAPPROVED_CASE.md)
  are the ibm_fez coherence-window dry runs at sources `10bb9ee` and
  `c84c490`, superseded by calibration-chosen placement;
  `plans/reviews/coherence-case-science-review.md` and
  `plans/reviews/coherence-case-submission-review.md` are the independent
  reviews of the first.

## Submission procedure

Each case runs as its own invocation under its own total ceiling: a fresh
dry run of the unchanged command, a check that its record is `planned` with
every observable admitted and its ceilings unchanged, and the case file's
approval-only command run at once against that record. The runner plans
only over the record's eligible backends, compares calibration at the
refresh and at each batch, writes `approval_required` and sends nothing on
any difference, and writes `approval-consumed.json` at the first batch so an
approval runs once. A job that waits in the queue can still execute under a
later calibration; the collector binds each PUB to its execution
calibration and withholds comparisons that span two.
