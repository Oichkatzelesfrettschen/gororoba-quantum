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
  analysis is not rerun (hours). Its provenance, the QX replay and every digest are retained in
  [analysis-provenance.json](../../evidence/qi-null-phase-scan/analysis-provenance.json): commit, command, environment,
  exit status, start and end times, the 29 run directories and the sha256 of the sanity output and of both records.
- Budget: the analysis ran 3.8 hours with 8 workers; the case quotes 3,009 s on a 12-thread host for building the 192
  damped law tables alone (CASE.md, "Commands"), and the longest batch turnaround on the device was 1,964.69 s
  (`retained-context.json`, `max_turnaround_seconds` of tuna_17 on 2026-11-21).

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
- Under rule 4, `none_adequate` means no world is adequate: every world's minimum chi-square, over the noise models and
  readout flips of the fit, exceeds its adequacy limit. The case's outcome table gives the effect on A5-186 as "unchanged".
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

Every world is rejected under rule 4. Among them the coupler-phase world has the least chi-square, 96.6 above its limit
(156.286 less 59.703); it fits the z12-10 kind within its limit and misses the other two. The ordering of rejected worlds
carries no physical attribution to coupler 8-12. Single batches already exceed a kind limit: the coupler world's
batch-09 reads 44.00 against the two-batch z12-30 limit of 26.124, while batch-03 reads 5.08 and batch-25 4.37
(`numbers.batch_chi2`).

## QX control

`qx_control.pass` is true and `complete` is true: each of the 12 circuits reads `ok` true, with its total-variation distance (`tvd`)
against its sampling `floor` at `factor` 2.0; the largest tvd/floor ratio is 1.36 (`batch-00/b0-rxz.cq`) and the least 0.73
(`batch-01/b0-rxz-q4-p5.cq`). The case's command sequence runs the Tuna-17 lines only after this analysis exits 0.

## Reported block (descriptive)

Outside the label (`reported`, rules 5 to 7 of CASE.md); descriptive fits that decide nothing:

- Bridge: padded less plain contrast -0.000126 +- 0.002393, `within_resolve` true, so the padding changes the center by
  less than 3 standard errors.
- z12 parabola of contrast against injected phase: least point at -7.62 +- 0.25 degrees, least contrast 0.009608, chi-square
  11.03 on 9. z8c parabola: least point at -10.91 +- 2.16 degrees, least contrast 0.002017, chi-square 18.10 on 9. The
  z8c points sample -10, 0 and +10 degrees only, so its least point lies just outside the sampled range; both errors
  come from the binomial covariance of pooled contrasts, unscaled by chi-square over dof (2.01 for z8c) and without the
  center offsets the points of one batch share.
- q4 line: slope 0.000459 +- 0.000175 per degree, chi-square 7.18 on 7, zero at -31.9 degrees (the slope's error is 38
  percent of the slope, so that angle is poorly located); `q4_slope_against_retained.within_resolve` is false: this
  series' q4 slope differs from the retained series' by 0.002699 +- 0.000277, 9.8 standard errors, so the bridge's
  agreement at the center does not extend to the q4 arm (under rule 7 the q4 points are not pooled with the retained
  series).
- Pooled d2 splits and visibility ratios per arm are in `reported.d2_split` and `reported.visibility_ratio`.

## Open hypotheses

Each data batch carries its own fitted phase and center, so drift between batches enters none of the worlds' sums
except the exact world's; the excess sits inside batches.

- hypothesis: the excess follows the circuit family rather than the time of the batch. Test: the replicate batches of
  each kind (batch-09 and 19 for z12-30, 03 and 25 for z12-10, the four z8c batches) and their arm-level residuals from
  `batch_rows` and `decision.numbers.predicted`: a large chi-square in both replicates of a kind puts the excess on
  the arm; one large and one small puts it on the time of the batch.
- hypothesis: one q12 phase added to the coupler world brings both failing kinds (z12-30 and z8c-10) under their
  limits. Test: a descriptive joint fit with one q12 phase and one coupler phase per batch on the same 14 batches and
  the same flip and noise grid; a remaining miss leaves the missing piece outside an added q12 phase.
- hypothesis: nonstationarity within a job carries the largest single-batch chi-squares. Test: the eight time-bin
  contrasts of batch-09 and batch-19 from their retained shot lists; homogeneous bins put drift within a job out.
