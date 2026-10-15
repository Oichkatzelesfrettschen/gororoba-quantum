# QPU program held for review: ripple, rank sectors and the coherence window

The program is three fixed live_run.py commands with 146 s of service
ceilings: ripple under `--max-total-execution-seconds 74` (2 x 37 s jobs),
rank sectors under 54 (2 x 27 s) and the coherence window under 18
(2 x 9 s). No command names a backend or a qubit: each omits `--backends`
and `--patch-qubits`, so the planner scores every accessible backend and,
for the coherence window, every calibrated patch embedding, and chooses by
calibration. The program is held and no job has been sent. Every `--submit`
waits for the owner's approval and names a fresh submit-free dry run by its
record.json digest (AGENTS.md, QPU time and calibration). The account's
28-day window reported 210 of 600 s used and 390 s remaining at
2026-10-15T01:37Z, so the program plus the 60 s reserve fits.

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

## Submitting after approval

Each case runs as its own invocation under its own total ceiling. The
procedure for each is a fresh dry run of the unchanged command, a check
that its record is `planned` with every observable admitted and its
ceilings unchanged, and the case file's approval-only command run at once
against that record. The runner compares calibration at the refresh and
at each batch, writes `approval_required` and sends nothing on any
difference, and writes `approval-consumed.json` at the first batch so an
approval runs once.
