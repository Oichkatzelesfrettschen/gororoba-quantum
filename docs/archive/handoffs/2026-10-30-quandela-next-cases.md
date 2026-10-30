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

## Belenos teleportation job-01 (blocked on the case identity gate)

**What it measures.** The six Pauli-eigenstate teleportation circuits on one `qpu:belenos` chip, twelve compilations in
two blocks (block B mirrored), under the descriptive rule: pooled accepted-event correctness with an anytime-valid
lower bound, a block homogeneity test and two labeled comparisons, as
[the design](../../design/ascella-belenos-entanglement-teleportation.md#recovered-chip-rehearsal-job-01) fixes. Job-00
returned no three-click sample on the degraded record, so it says nothing about the circuits.

**Cost and time (corrected).** The registered `JOBS["job-01"]` row sets 1200 samples per iteration, 3,200,000
`max_shots` per iteration, a credit ceiling of 4.2 (1 credit per job plus 3,200,000 times 1e-06) and 240 expected
seconds. The figure of about 2.2 credits quoted earlier in the session was job-00's ceiling and applies to no job-01
case. Both fit the roughly 68 credits that remain before the 2026-11-01 00:00 UTC reset.

**Blocker.** The retained case was prepared at the platform read of 2026-10-30 01:20 UTC (perfs sha256 `f421bed7...`,
HOM 83.9 %, g2 1.3 %, transmittance 5.19 %, pooled model fidelity 0.8204). The live record at 19:14 UTC reads perfs
sha256 `b27e0546...` (HOM 87.1 %, g2 1.3 %, transmittance 4.99 %, pooled fidelity 0.8407), and the processor record read
at 18:05 UTC (HOM 87 %, transmittance 5.43 %) differed from both. The `binding` gate in
`scripts/qd_teleportation_rehearsal.py` sets `inside_justified_range` by exact equality of the live and prepared
perfs digests, so it refuses any submission after the record moves. Two reads 69 minutes apart disagreed, so a
case prepared at one read and submitted after an approval round-trip is likely to be refused. The `--plan` at 19:14 UTC
refused for that figure change and additionally because the Explorer row read `running` for a moment
(`plan-refused-20261030T191429091793Z.json`).

**Tolerance (implemented, not yet merged).** Branch `fix/teleportation-job-gate-tolerance` replaces the digest equality
in `model_at` with the two conditions the frozen budget depends on: no mode of the case's layout reads a dark rate above
`DARK_LIMIT`, and `expected_seconds` at the live clock and per-input sample probabilities stays within `MAX_DURATION`. The
descriptive rule's lower bound holds at any accepted count, so the pooled fidelity no longer gates admission. Read-only
`--plan job-01` at 19:58 UTC under the live record (perfs sha256 `b27e0546...`) returns `inside_justified_range` true,
no layout mode above the dark limit and 240 s expected, equal to the frozen case. The plan still refused because the
Explorer row read `running`: registry claim `qd-belenos-running-status-holds-jobs` records one job that sat queued
for 26 minutes with no start under that status, so the case waits for `available`.

**Submission needs two things.** The owner's approval at the corrected ceiling of 4.2 credits (the approval given
earlier named the figure of about 2.2), and `qpu:belenos` reading `available` with no running or queued token job.

**Options (as drafted before the tolerance).**
1. Re-prepare at the live read and submit within minutes: snapshot the platform, derive the case under a new job name
   (`--prepare` refuses a registered name; the seed rule of the repository guide lets a replacement for the same question
   reuse the unspent job-01 seeds, which no run has used; not checked against `ci/seed_provenance.py`), register its rows, then
   `--submit` in the same sitting. The gate passes only if the record holds still for that window.
2. Relax the gate's justified range from digest equality to a tolerance on the model inputs (HOM, g2 and the window's
   per-mode transmissions) at which the justified sample budget and the seconds model still hold. This changes the
   preregistration rule, so it needs the owner's choice and a Codex review.
3. Wait for a stable record: the record watch posts changes to issue 556; submit at the first read that stays put for
   an hour.

The Belenos weekly maintenance runs 2026-11-05 08:30 to 12:00 UTC, after the reset window.
