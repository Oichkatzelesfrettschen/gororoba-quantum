# IQM Emerald third train length: result of 2026-11-22

Case: [idle-schedule-third-length-emerald](../../../results/iqm/proposals/idle-schedule-third-length-emerald/CASE.md)
(cases.json sha256 2c118f7b1ebfaa6782ded87aa650512b4c0fbda7a256ad68356ef66ee0591e4c, approval "owner AskUserQuestion
2026-11-22T22:49Z: Approve procedure"). The case was rebuilt from a live calibration read immediately before submission
on the compute host and reproduced that digest (set 7d7ebe74). Runs:
`results/iqm/runs/2026-11-22T231402Z-emerald_mock-idle-schedule-third-length-emerald-probe` (emerald:mock, completed)
and `results/iqm/runs/2026-11-22T231417Z-emerald-idle-schedule-third-length-emerald-probe` (job
`01a2058a-01a3-7210-b6b9-cd1b02d2d710`). Analysis: `results/iqm/idle_schedule_third_length_emerald_analysis.json`
(`scripts/iqm_idle_schedule_probe.py analyze`, compute host).

## Preregistered verdict

- h3_line: `on-line` for the cohort and for QB24. The cohort is ten qubits usable at both lengths (QB5, QB10, QB14,
  QB18, QB20, QB24, QB26, QB34, QB37, QB42; QB30 and QB44 fail a gate). The within-job deviation of the gap from the
  line through the same job's 500 and 1000 pulse gaps, after the quadratic delay correction, reads -0.05 +- 1.47 ns at
  250 pulses (z -0.04) and +0.86 +- 0.63 ns at 2000 (z 1.36); QB24 reads +4.8 +- 4.2 ns (z 1.14) and +0.07 +- 1.87 ns
  (z 0.04). The four lengths are consistent with g(N) = a + b / N within these errors; the run does not attribute b to a
  mechanism (CASE.md, "What on-line tests").
- H1, schedule: `asap`.

## Descriptive readings

These come from the same record and decide nothing.

- The line moved between the two days. Through this job's own anchors (29.68 ns at 500 pulses, 26.31 ns at 1000) the
  line is a = 22.9 ns per pulse beyond the nominal 24 ns and b = 3.37 us per train, against a = 21.4 ns and b = 5.84 us
  on 2026-11-21. Against the retained line the cohort reads 34.51 ns at 250 pulses where it predicts 42.86 (z -5.16)
  and 29.68 ns at 500 where the retained anchor reads 32.11 (z -2.95, inside the 3-standard-error anchors-moved gate);
  the 1000 and 2000 pulse readings agree with it (z -0.63 and -0.54).
- The delay-curvature correction carries the 2000 pulse reading: without it the cohort deviation reads z -1.75, with it
  z +1.36, the direction the retained curvature predicts.
- Per layout the deviations agree: at 250 pulses +1.23 ns (z 0.63) beside QB20 and -1.70 ns (z -0.77) beside QB26; at
  2000 pulses +0.74 (z 0.93) and +1.03 (z 1.14).
- Cost: compilation 0.327 s and execution 9.505 s, billed 10 s at 0.75 credits per second, 7.50 credits, against an
  expected 3.9 to 4.4 s and 3.00 to 3.75 credits; the emerald:mock estimate of the same job was 1.53 s of execution.

## Open hypotheses

- hypothesis: the execution time of this job is set by the longest circuits' duration per shot (the 96 us delay arm and
  the 2000 pulse trains, about 97 us), which neither the case's per-circuit-shot estimate nor the mock's runtime
  estimate carries. Falsifier: a job of the same circuits without the two longest arms whose execution scales by the
  remaining circuits' mean duration rather than their count. Cheapest test: refit the billing model of
  `docs/evidence/iqm-garnet-billing-v3/` on Emerald jobs with a per-shot-duration term, from the retained runs alone.
  Done in [billing-v4](../../evidence/iqm-billing-v4/README.md): the per-shot duration sum, the per-shot longest duration
  and the padded longest duration each leave a 5.0 to 5.8 s residual on this job, so the hypothesis fails as stated.
- hypothesis: b changes between calibrations while the form holds. Falsifier: two jobs on one calibration set whose
  within-job b differ by more than three standard errors.
