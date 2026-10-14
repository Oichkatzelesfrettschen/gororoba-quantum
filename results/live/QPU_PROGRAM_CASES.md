# QPU program for review: ripple, rank sectors and the coherence window

Three UNAPPROVED cases make up the program, with 146 s of service ceilings
in all. Each case is a submit-free dry run whose record digest an approval
names; nothing here submits a job, and each `--submit` waits for the owner's
approval of that case and its digest (AGENTS.md, QPU time and calibration).
The account's 28-day window reported 210 of 600 s used and 390 s remaining
at 2026-10-14T21:42Z, so the program plus the 60 s reserve fits.

| Case | Backend, calibration (PDT) | Record SHA-256 | Jobs and shots | Nominal / stress (s) | Ceilings (s) |
|---|---|---|---|---:|---:|
| [ripple](2026-10-14T214325.818563Z/UNAPPROVED_CASE.md) | ibm_kingston, 2026-10-14 14:25:47 | `abbbb2d3b39953e35914b6b33cfd81fb14bd674b3e889e5f6f87a59fd00d32fe` | 120 x 1024 and 26 x 4096, two static jobs | 64.28 / 68.88 | 2 x 37 |
| [rank sectors](2026-10-14T214325.271357Z/UNAPPROVED_CASE.md) | ibm_kingston, 2026-10-14 14:25:47 | `2dde22ad03ae0342756b6ec99f5792d7cc50448fc206393d32199b06a5cd6e18` | 15 x 1024 and 21 x 4096, two static jobs | 30.45 / 35.05 | 2 x 27 |
| [coherence window](2026-10-14T055711.938217Z/UNAPPROVED_CASE.md) | ibm_fez, 2026-10-13 22:42:00 | `9ca39ad47c1833903111c344b29ff1467e12c3728c7cd93d5f1fc35af7255138` | 10 static and 5 dynamic PUBs at 2048 shots, two jobs | 12.47 / 12.47 | 2 x 9 |
| **Program** | | | 6 jobs | **107.20 / 116.40** | **146** |

Both Kingston records come from the recorded commands of their earlier
cases, run unchanged on source `a2392dc` with `sources_modified=false`;
every one of ripple's 1138 and rank's 196 observables admits. Their
`SHA256SUMS` bind record.json, isa.qpy and the case file.

## What each case measures

- **Ripple and rank sectors** are Kingston replications of the 2026-10-13
  ibm_fez acquisitions (CAMPAIGN_FINDINGS.md sections 5 and 6). The
  incremental question is transfer: whether the 84 box-kite, 8 sector and
  12 pulse-difference contrasts that rejected their nulls on Fez reproduce
  on a second Heron r2 processor under different placements and
  calibration. They do not target the Fez union-template walk discrepancy.
  [KINGSTON_ALGEBRA_CASES.md](KINGSTON_ALGEBRA_CASES.md) carries the design
  search and the runtime levers.
- **Rank sectors at 4096 shots.** The 131072-sample noise model admits every
  contrast without an 8192-shot tier. On the 14:25 calibration the sector
  4 to 7 `t1d2 - t1d1` contrasts predict 0.1253, 0.1226, 0.1252 and 0.1215,
  with lower modeled values 0.1125, 0.1098, 0.1124 and 0.1087 against the
  0.0997 the directional contracts need; sector 7 has the thinnest margin,
  0.0090.
- **Ripple's ceiling.** The 120-PUB job's latency-stress charge is 36.27 s
  against its 37 s ceiling.
- **Coherence window** measures, on the pinned ibm_fez patch (control 142,
  work 136 and 144, spectator 143), the branch-signed work coherence the
  first N=21 orbit round leaves, in three contexts: immediate readout, a
  matched 836 dt idle, and a mid-circuit measure and reset of the control.
  Five precision contracts at half-width 0.33 on 4 C admit it. The
  analyzer reports a phase only where the joint (Re C, Im C) region
  excludes the origin, attributes a measurement-induced phase only after
  the signed per-qubit exposure, setting-specific and winding corrections,
  and also reports both selected coherences with branch and spectator
  strata (scripts/coherence_window_analysis.py).

## Holds before approval

- **ibm_fez is in maintenance** (58 pending jobs at 14:42 PDT), so the
  coherence case cannot be re-planned; its record predates two Fez
  calibrations and source changes after `5f46c38`. Approval needs a fresh
  dry run of its recorded command once ibm_fez reports `active`, and the
  new record digest replaces the one above.
- **Kingston recalibrates** roughly hourly and on triggers. The runner
  compares calibration at the refresh and at each batch with the approved
  record and refuses submission on a change, so a Kingston case approved
  after a recalibration needs another dry run of the same command.
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
