# QPU program for review: ripple, rank sectors and the coherence window

Three UNAPPROVED cases make up the program, with 146 s of service ceilings
in all. No command chooses a backend or a qubit: each dry run omitted
`--backends` and `--patch-qubits`, so the planner scored every accessible
backend and, for the coherence window, every calibrated patch embedding,
and chose by calibration. The case files' reproduce and approval commands
list the whole roster it chose from, `--backends
ibm_fez,ibm_kingston,ibm_marrakesh`, so a backend added to the account later
cannot change the plan silently. Each case is a submit-free dry run whose record
digest an approval names; nothing here submits a job, and each `--submit`
waits for the owner's approval of that case and its digest (AGENTS.md, QPU
time and calibration). The account's 28-day window reported 210 of 600 s
used and 390 s remaining at 2026-10-14T21:42Z, so the program plus the 60 s
reserve fits.

| Case | Chosen backend and placement | Record SHA-256 | Jobs and shots | Nominal / stress (s) | Ceilings (s) |
|---|---|---|---|---:|---:|
| [ripple](2026-10-14T220553.174983Z/UNAPPROVED_CASE.md) | ibm_kingston, optimizer layouts | `ac01ef20898820a9f99c6e1ba3b36f41f9f643c7c43f599c31dcc62ceb8fefc6` | 120 x 1024 and 26 x 4096, two static jobs | 64.28 / 68.88 | 2 x 37 |
| [rank sectors](2026-10-14T220552.787448Z/UNAPPROVED_CASE.md) | ibm_kingston, optimizer layouts | `e1a5f2702aa4123e6cffa96da8c79e3b518efc0326dedab415ad4cc21456999c` | 15 x 1024 and 21 x 4096, two static jobs | 30.45 / 35.05 | 2 x 27 |
| [coherence window](2026-10-14T220552.942969Z/UNAPPROVED_CASE.md) | ibm_kingston, patch 57, 68, 67, 66, 69, 65 | `26a7a13afe246ccd5c420a3f5f266fed12e912740ce8cac7479dcc389eb42579` | 10 static and 5 dynamic PUBs at 2048 shots, two jobs | 12.51 / 12.51 | 2 x 9 |
| **Program** | | | 6 jobs | **107.25 / 116.45** | **146** |

All three were planned on source `dac1f2e` with `sources_modified=false`
against the ibm_kingston calibration of 2026-10-14 14:25:47 PDT, and every
observable admits (ripple 1138, rank 196, coherence 5). `SHA256SUMS` in each
directory binds record.json, isa.qpy and the case file.

## How the planner chose

- **Eligibility.** ibm_fez reported maintenance (61 pending jobs). ibm_marrakesh
  (37 pending) exceeded ripple's `--max-pending 25` and stayed eligible
  for rank (`--max-pending 60`) and the coherence window
  (`--max-pending 100`), where its compiled layouts scored below Kingston's.
  Each record's `skipped_backends` and selection trace carry the reasons.
- **Coherence patch.** The planner enumerated every embedding of the patch's
  five couplers into each eligible backend's admitted CZ graph, ranked them
  by readout error, CZ error and T2 decay over a 5 us idle, compiled the best
  16 per backend and chose the highest joint score: Kingston control 57,
  work_a 68, spectator 67, work_b 66, neighbors 69 and 65 (joint score
  0.760, best of 32 compiled patches). Routing reads b0 from 57, read_a from
  66, read_b from 68 and the sector from 67. The matched idle is 1098 dt
  (control measure 545 dt plus reset 553 dt), so a static detuning above
  114 kHz aliases.
- **Binding.** The approval binds the choice. If a fresh plan at submit picks
  another backend or patch (a recalibration, or ibm_fez leaving maintenance
  and scoring higher), the runner refuses and sends nothing until a new dry
  run is approved.

## What each case measures

- **Ripple and rank sectors** replicate the 2026-10-13 ibm_fez acquisitions
  (CAMPAIGN_FINDINGS.md sections 5 and 6) on ibm_kingston. The incremental
  question is transfer: whether the 84 box-kite, 8 sector and 12
  pulse-difference contrasts that rejected their nulls on Fez reproduce on a
  second Heron r2 processor. A future plan that the planner places on ibm_fez
  would be a repeat on the same device instead, and its case would say so.
  They do not target the Fez union-template walk discrepancy.
  [KINGSTON_ALGEBRA_CASES.md](KINGSTON_ALGEBRA_CASES.md) carries the design
  search and the runtime levers.
- **Rank margins.** The 131072-sample noise model admits every contrast at
  4096 shots; the sector 4 to 7 `t1d2 - t1d1` lower modeled values clear the
  0.0997 directional threshold by 0.0124, 0.0097, 0.0123 and 0.0086.
- **Ripple's ceiling.** The 120-PUB job's latency-stress charge is 36.27 s
  against its 37 s ceiling.
- **Coherence window** measures the branch-signed work coherence the first
  N=21 orbit round leaves on the chosen patch, in three contexts: immediate
  readout, a matched 1098 dt idle, and a mid-circuit measure and reset of the
  control. It no longer continues the earlier ibm_fez patch; it measures the
  measurement-induced phase on the patch the planner chose. Five precision
  contracts at half-width 0.33 on 4 C admit it. The analyzer reports a phase
  only where the joint (Re C, Im C) region excludes the origin, attributes a
  measurement-induced phase only after the signed per-qubit exposure,
  setting-specific and winding corrections, and reports both selected
  coherences with branch and spectator strata
  (scripts/coherence_window_analysis.py).

## Holds before approval

- **Kingston recalibrates** roughly hourly and on triggers; the runner
  compares calibration at the refresh and at each batch with the approved
  record, so a case approved after a recalibration needs another dry run of
  the same command.
- **The runner applies one ceiling per invocation**, so the program runs as
  three invocations: ripple under `--max-total-execution-seconds 74`, rank
  under 54 and the coherence window under 18. Per-job ceilings and
  co-batching would bring the program to 114 s of ceilings but need a
  runner change first.

## Approval-only commands

Each case file ends with its approval-only command, which names the record
directory and digest above with `--approved-record` and
`--approved-record-sha256` and adds `--submit`. The first batch writes
`approval-consumed.json` into the record directory, so an approval runs
once.
