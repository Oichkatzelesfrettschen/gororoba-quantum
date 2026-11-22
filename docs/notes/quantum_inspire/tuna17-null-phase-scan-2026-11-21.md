# Tuna-17 null phase scan of 2026-11-21: retained series, decision and QX control

Status: retained acquisition and its preregistered analysis; no claim row cites it yet. The case is
[pathion_null_phase_scan_tuna_17/CASE.md](../../../results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/CASE.md)
(ledger row A5-186; predecessor: [the rotation scan phase refit](tuna17-null-rotation-scan-phase-refit.md)). Every number
below is a field of a retained record, named in brackets, or a sum over the `results.json` of the runs.

## Provenance

- Approval: `submission.json` of every batch holds `"approval": "owner AskUserQuestion 2026-11-21T16:43Z: Finish, then
  scan (Recommended)"`. CASE.md itself carries the status line "written case awaiting its review and the owner's
  approval" and no approval line.
- Runs: `results/quantum_inspire/runs/2026-11-21T1650Z-pathion_null_phase_scan_tuna_17-batch-00` to `-28` (29 batches)
  and `2026-11-21T1650Z-pathion_null_phase_scan_qx-batch-00` to `-03` (4 batches). The QX twin was submitted first
  (`created_utc` 2026-11-21T17:38:46Z, last collection 17:40:21Z); the Tuna-17 series ran from 17:46:26Z to its last
  collection at 19:37:18Z.
- Analysis: `scripts/qi_pathion_null_phase_scan_cases.py --analyze RUN_DIRS --out RECORD` with `GOROROBA_WORKERS=8`
  and `GOROROBA_SCAN_TABLES` set, on the compute host at commit b35a867c0 (origin/main of the time), started
  2026-11-21T19:41:56Z and ended 23:29:19Z (3.8 hours). `--sanity` over the 29 Tuna-17 runs passed first and is
  reproduced byte for byte at the retention head. Records:
  [Tuna-17](../../../results/quantum_inspire/pathion_null_phase_scan_tuna_17_analysis.json) and
  [QX](../../../results/quantum_inspire/pathion_null_phase_scan_qx_analysis.json), schema
  `qi-pathion-null-phase-scan-analysis-v1`.
- Verification at retention: every copied file matches its source sha256 (303 files); `--sanity` passes on the QX runs
  and the 29 Tuna-17 runs; `--analyze` over the four QX runs rewrites the QX record byte for byte. The Tuna-17
  analysis is not rerun (hours); its provenance is the log and commit above.

## Jobs, shots and execution time

Summed over the `jobs[].results[]` rows (`shots_done`, `execution_time_in_seconds`) of each run's `results.json`:

| series | batches | jobs | shots | execution seconds |
|---|---|---|---|---|
| Tuna-17 | 29 | 72 | 6,488,064 | 3,412.209 |
| QX | 4 | 12 | 24,576 | 9.344 |

The Tuna-17 totals equal the case's stated 72 jobs and 6,488,064 shots; the execution total lies below the case's
expectation of 3,626 to 4,019 s.

## Preregistered decision

Record `decision` (rules 1 to 4 of CASE.md, "Preregistered decision rules"):

- `decision.label` is `none_adequate`; `decision.a5_186` reads "unchanged; the numbers are reported".
- Under rule 4, `none_adequate` means no world is adequate: no world's chi-square sum reaches its adequacy limit at any
  noise model and readout flip of the fit. The case's outcome table gives the effect on A5-186 as "unchanged".
- Admitted batches (`numbers.admitted_batches`): 14 of 14 data batches (batch-01, 03, 05, 07, 09, 11, 13, 15, 17, 19,
  21, 23, 25, 27); `split_admitted` lists the 8 whose d2 splits enter the fit. The inverse-variance center contrast is
  0.014623 +- 0.000739 (`numbers.center_contrast`), so rule 2 is passed.
- Chi-square of each world against its limit (`numbers.chi2`, `numbers.adequacy_limit`):

| world | chi-square | adequacy limit | fitted readout flip | noise model |
|---|---|---|---|---|
| exact gates | 1685.093 | 70.703 | 0.0275 | contraction share 0 |
| q12 phase | 232.103 | 59.703 | 0.005 | contraction share 0 |
| coupler 8-12 phase | 156.286 | 59.703 | 0.0025 | contraction share 0.0833 |
| q8 phase at coupler | 276.700 | 59.703 | 0.0075 | contraction share 0.25 |

- Per deciding kind (`numbers.kind_chi2` against `numbers.kind_limit` 26.124, 26.124, 39.252 for z12-10, z12-30,
  z8c-10): coupler phase 9.45, 72.563, 74.273; q12 phase 42.106, 145.807, 44.19; q8 phase 23.809, 154.697,
  98.194. `flip_at_grid_end` is empty. `separation_needed` is 208.382.

The coupler-phase world has the least sum and misses its limit by 96.6 (156.286 less 59.703); it fits the z12-10 kind
within its limit and misses the other two.

## QX control

`qx_control.pass` is true and `complete` is true: each of the 12 circuits reads `ok` true, with its total-variation distance (`tvd`)
against its sampling `floor` at `factor` 2.0; the largest tvd/floor ratio is 1.36 (`batch-00/b0-rxz.cq`) and the least 0.73
(`batch-01/b0-rxz-q4-p5.cq`). The case's command sequence runs the Tuna-17 lines only after this analysis exits 0.

## Reported block (descriptive)

Outside the label (`reported`, rules 5 to 7 of CASE.md); descriptive fits that decide nothing:

- Bridge: padded less plain contrast -0.000126 +- 0.002393, `within_resolve` true, so the padding changes the center by
  less than 3 standard errors.
- z12 parabola of contrast against injected phase: least point at -7.62 +- 0.25 degrees, least contrast 0.009608, chi-square
  11.03 on 9. z8c parabola: least point at -10.91 +- 2.16 degrees, least contrast 0.002017, chi-square 18.10 on 9.
- q4 line: slope 0.000459 +- 0.000175 per degree, chi-square 7.18 on 7, zero at -31.9 degrees;
  `q4_slope_against_retained.within_resolve` is false (difference 0.002699 +- 0.000277).
- Pooled d2 splits and visibility ratios per arm are in `reported.d2_split` and `reported.visibility_ratio`.

## Open hypotheses

- hypothesis: the coupler-phase world is the nearest of the three error worlds but misses a second mechanism, since its
  z12-30 and z8c-10 kinds exceed their limits by 46 and 35. Test: the shot-order fold of rule 8 on the retained jobs, and a
  refit with a q12 phase and a coupler phase together on the same 14 batches.
- hypothesis: the excess of every world over its limit includes drift between batches, since CASE.md reports a drift of the
  predecessor's center offset of 0.001 to 0.020 between batches. Test: the per-batch center contrast of the
  14 `batch_rows` against batch order.
