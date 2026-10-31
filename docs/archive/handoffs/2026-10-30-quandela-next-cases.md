# Quandela cases drafted 2026-10-30: Ascella matched-mesh third acquisition and Belenos teleportation job-01

This handoff stands alone for a reader with no access to the session that wrote it. Both cases follow the audit in
[2026-10-30-quandela-run-audit.md](../reviews/2026-10-30-quandela-run-audit.md). Each Quandela job needs the owner's
approval of its written case; nothing below has been submitted. The plans below were read live at 2026-10-30 19:14 UTC
through `qd_platform.py plan` and `qd_teleportation_rehearsal.py --plan`, which send no job.

## Ascella matched-mesh third acquisition (ran)

**Run.** The frozen five-mesh matched request of `results/quandela/cases/ascella_transition_day_repeat/matched` ran a
third time on `qpu:ascella` under the owner's approval at the 1.131072-credit ceiling: job
`cb8717bc-6bb3-4cbd-b508-a8f4d73c20c7`, completed, 327,680 samples, retained as
`results/quandela/runs/2026-10-30T195355Z-qpu_ascella-transition-matched-mesh-third-acquisition/`. The baseline
(`ascella-context-packed-forward`) started 2026-10-28 00:38:05 UTC, the first day repeat 2026-10-29 09:39 UTC, and the third acquisition's provider start fell 67.3 hours after the baseline start.

**Comparison.** `scripts/ascella_matched_port_comparison.py` compares the single-click port distributions of the three
acquisitions, setting by setting (`port-comparison.json` in the run directory). Settings, circuit parameters and
compilation seeds are identical across the three runs; only cohort labels differ. Homogeneity chi-square over the three
acquisitions reads 5,149, 1,935, 5,595 and 2,707 on 22 degrees of freedom for settings 0, 1, 2 and 4 and 29.2 on 22
for setting 3. The changes follow no linear trend: setting 2 rose by total variation 0.062 from the baseline to the first
repeat and returned to within 0.013 of the baseline at the third acquisition, and setting 0 held at 0.005 between the
baseline and the first repeat before moving 0.045 by the third. This is exploratory (claim
`ascella-transition-matched-mesh-third-acquisition`): independent accepted events are assumed, and no calibration read
separates drift from a calibration change.

**Matched-mesh check.** `scripts/ascella_transition_ci_check.py --matched-check` fails with "the frozen next-day case
differs" on the retained campaign file for every run in the tree, including the first repeat it admitted on 2026-10-29,
under the pinned 3.14.7 interpreter and the system 3.14.8. The run's mesh identity therefore rests on equal
settings and seeds. Repairing the check is a follow-up of the audit.

## Belenos teleportation job-01 (ran partially)

**Run.** The owner approved the 4.2-credit ceiling. Job `708bb40d-78d1-4903-9d61-e38705b85465` was submitted
2026-10-30 20:23:48 UTC on branch `fix/teleportation-job-gate-tolerance`, which carries two changes to
`scripts/qd_teleportation_rehearsal.py`: the gate admits a descriptive case on its budget (no layout mode above
`DARK_LIMIT`, `expected_seconds` within `MAX_DURATION` at the live record) instead of perfs digest equality, and the
plan and submission admit the Explorer status `running` beside `available`. The branch has had no Codex review.

**Why `running` is admitted.** At 20:13 UTC the token held no running or queued job while the row read `running`, so the
status reports other jobs. Jobs planned under it queue: of 17 retained Belenos jobs, 12 completed (median wait 74 s,
with three waits of 36 to 235 minutes) and 5 never started and were canceled. This job started 12.6 s after creation.

**Outcome.** The service canceled the job at its 300 s maximum duration (reported duration 318 s, progress 0.917) after
11 of 12 iterations. It returned 13,200 of 14,400 samples, billed the full 4.2-credit ceiling, and left the +Z iteration
of block B without counts. Pooled accepted-event correctness reads 0.802 over 1262 accepted events with an anytime-valid
lower bound of 0.759; the partial-job rule makes the verdict descriptive and inconclusive, both classical comparisons
are not evaluated, and the block homogeneity test flags +X, +Y, -X and -Y. The expected-seconds model gave 240 s and
underestimates this chip.

**Next case.** A repeat needs a corrected seconds model before it spends another ceiling. Six iterations per job fits the
observed pace of about 27 s per iteration plus compilation; its ceiling is 1 plus the per-iteration shot budget times
1e-06.
