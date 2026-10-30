# Quandela run audit: Ascella and Belenos, 2026-10-30

Read-only audit of the retained Quandela acquisitions on `main` at commit 66d92ca, with the live processor records
read at 2026-10-30 18:05 UTC and the account usage report of the same session. The audit joins
`results/quandela/runs/*/submission.json`, `submission-state.json` and `circuit.json` to
`docs/state/research_state.json` by run directory name. It changes no record, submits no job and reads no token.

## Inventory

The tree retains 128 runs: 61 `qpu:belenos`, 38 `qpu:ascella`, 24 `sim:belenos` and 5 `sim:ascella`. Every run has a
job id, a `results.json` and a registry acquisition. 53 runs carry an `analysis.json`; the rest are analyzed by a
family script that writes elsewhere (the drift series by `scripts/bdsc_drift_series.py`, the Ascella order and
transition pilots by their case scripts).

The account usage report (`qd_usage`) counts 133 jobs: 42 `qpu:ascella`, 6 `sim:ascella`, 61 `qpu:belenos` and 24
`sim:belenos`. The retained set matches on both Belenos platforms and falls short by 4 `qpu:ascella`
jobs and 1 `sim:ascella` job. One further `qpu:ascella` run,
`2026-10-30T165953Z-qpu_ascella-ascella_predecessor-current-schema`, exists only in the worktree of branch
`fix/ascella-predecessor-current-command-binding` and is not on `main`. Four jobs stay unlocated (three `qpu:ascella`,
one `sim:ascella`); the follow-up below names the check that locates them.

Cost rule, checked with `qd_job_billing` on one job per platform: 1 credit per job plus 1e-06 credits per QPU shot, and
simulators add no shot charge. The usage report totals 130.97 credits used. All 128 retained runs were submitted from
2026-10-17 21:35 UTC to 2026-10-30 06:36 UTC, so the October window holds at least 128 of the 133 jobs.

## Same experiment, repeated

Identical `circuit.json` digests mark one frozen experiment submitted more than once. Nineteen digests repeat.

| Digest (first 10 hex) | Jobs | Platforms | Span | Content |
|---|---|---|---|---|
| `206bcfd5e4` | 28 | 25 `qpu:belenos`, 3 `sim:belenos` | 2026-10-21 to 10-24 | the frozen dark-subspace request: qualification, diagnostic, stationarity and the seven drift-series jobs |
| `736cf0c7b4` | 20 | `qpu:ascella` | 2026-10-28 to 10-29 | the transition matched-mesh circuit and its context and port diagnostics |
| `69326bf067` | 10 | 9 `qpu:belenos`, 1 `sim:belenos` | 2026-10-17 to 10-18 | Belenos mesh and diagnostics jobs |
| `1fed0081cd` | 9 | 8 `qpu:ascella`, 1 `sim:ascella` | 2026-10-24 to 10-30 | signed-coherence meshes and the source-compatible predecessor simulation |
| `8d05c0fcf5` | 4 | 2 `qpu:ascella`, 2 `sim:ascella` | 2026-10-29 | associator character |

The `body_sha256` field never repeats across runs (128 distinct values) because the job name and process id enter the
body; the circuit digest and `cases_sha256` are the comparison keys. The drift-series schedule compares its seven jobs
on the body digest without the process id (`3d5db1e2...`), which `submission.json` does not store, so the audit
cannot recompute that comparison from retained fields.

## Simulation against hardware

Thirteen circuit digests carry both a `sim:*` job and a `qpu:*` job. Nine hold exactly one of each: eight on Belenos
(six packed box-kite blocks of 2026-10-30, a single box-kite block of 2026-10-17 and a mesh job of 2026-10-18) and one on
Ascella (the two-photon associator of 2026-10-29). The other four digests hold larger groups, among them the frozen
dark-subspace request and the Ascella associator character (two simulations and two hardware jobs). Each pair shares
its compiled circuit, so a sim-to-QPU residual is defined per pair. The packed box-kite series is the only family with
a second hardware arm on swapped chip modes.

Cross-platform pairing is thin: Ascella and Belenos share no circuit digest. The only Ascella run built as a control for
a Belenos family is `bdsc_ascella_control` (one job, 2026-10-21). The two chips answer different questions: Belenos
carries the dark-subspace, sum-rule, box-kite and teleportation work, and Ascella carries signed coherence, associator
character and the transition diagnostics.

## Mode-swap replay

`scripts/qd_packed_mode_swap_analysis.py qpu_belenos/box_kite_photonic_packed qpu_belenos/box_kite_photonic_packed_swapped`
replays the retained series and returns verdict `mixed`. 26 of 32 blocks change their algebra-mode share by more than
4.5 standard errors when the block moves three of six slots, with the largest change 0.146 (z 36). The block predictor
reads r = -0.337 (interval -0.714 to +0.190), so the residual does not follow the block. The slot predictor reads
r = -0.585 (interval -0.838 to -0.126), so the residual follows the chip modes with a reversed sign. The replay
reproduces the figures of registry claim `qd-belenos-packed-mode-swap`. The sign reversal of the slot predictor is a lead for
the output-swap plan `belenos-sum-rule-output-swap`: a deficit that tracks the detector slot supports terminal
imbalance, and the packed series is the retained evidence that modes matter. The claim's boundary applies: one chip in one
calibration state, the two layouts about an hour apart, so placement is not separated from drift.

## Across time

Three families repeat one request at different times.

- The dark-subspace drift series: seven jobs of one frozen request at two-hour spacing on 2026-10-24 07:00 to 19:00 UTC,
  plus five stationarity jobs on 2026-10-23. The preregistered primary reads consistent (von Neumann ratio 1.674, exact
  p 0.056), the lag profile rises from 7.1e-6 at 2 h to 2.24e-5 at 12 h, and the post-hoc lag trend reads Spearman 0.65,
  p 0.006. The design records every reading in
  [bdsc-qualification.md](../../design/bdsc-qualification.md#drift-series-of-one-frozen-request).
- The Belenos order, transform and three wave repeats of 2026-10-22.
- The Ascella matched-mesh day repeat: five matched meshes on 2026-10-29, scheduler receipt `passed`, 5 of 5 matched
  (`results/quandela/schedules/ascella-transition-day-repeat/matched-repeat-admitted.receipt.json`).

**Registry binding.** Every one of the 128 retained acquisitions is cited by a registry claim, through the claim's
`acquisitions` field or an evidence path. The drift-series and stationarity runs reach the registry through derived
readouts: claims `qd-belenos-bdsc-stationarity-readout` (established, preregistered), `qd-belenos-bdsc-drift-series-readout`
(established, preregistered, reads consistent) and `qd-belenos-bdsc-drift-series-diagnostic` (exploratory) cite the
pinned JSON files, and the five Belenos repeats of 2026-10-22 enter through a claim's `acquisitions` list. The
across-time work therefore produced a registered result: run-to-run jitter without memory at p 0.056, an undecided
walk (sensitivity 0.71 for a step SD of 0.0021 per two hours) and one exploratory lead, the lag trend. An earlier
version of this audit reported 17 uncited runs; that count came from searching claim text for run directory names,
which misses citations by acquisition id.

## Live state and the gating hold

| Platform | Status at 2026-10-30 18:05 UTC | HOM | g2 | Transmittance |
|---|---|---|---|---|
| `qpu:belenos` | running | 87 % | 1.3 % | 5.43 % |
| `qpu:ascella` | calibration | 88.82 % | 1.8 % | 5.5 % |

The Belenos record sits near the 2026-10-24 anchor (HOM 88.8 %, g2 1.1 %, transmittance 5.5 %) and far from the
degraded record that held from 2026-10-25 18:47 UTC (HOM 83.8 %, g2 16.7 %, transmittance 0.05 %): g2 and transmittance
sit a factor of 13 and 108 from the degraded figures. The recovery
condition in the teleportation handoff
([belenos-recovery-watch.md](../handoffs/belenos-recovery-watch.md)) is met, and plan step `recovered-chip-rehearsal`
of `ascella-belenos-entanglement-teleportation` holds its run: twelve iterations in two blocks, block B mirrored. The
preregistered fidelity target F* = 0.86 comes from the anchor figures; the model needs rescoring at the live figures
(HOM 87 %, g2 1.3 %) before the case is written. Belenos lists weekly maintenance from 2026-11-05 08:30 UTC.

Autonomous spending is off. The `quandela-schedule.yml` workflow reads `disabled_manually` while the repository variable
`QUANDELA_SCHEDULE_ENABLED` reads `true`; both schedule files read `"enabled": true`, and every job they list (one Ascella
matched repeat, seven drift-series slots) already holds a receipt. Each job submits once, so no listed job can submit
again.

## Credit window

The monthly allowance resets 2026-11-01 00:00 UTC (2026-10-31 17:00 Pacific), per the Explorer plan facts in
[README.md](../../notes/quandela/README.md): 200 credits per calendar month, no carry-over. `qd_usage` reports no period
boundary; the 130.97 credits used leave about 69 remaining if all 133 jobs ran in October, which the dates of the 128
retained runs support. A run submitted before the reset spends expiring credit, and a run submitted after it draws on the
new allowance. Job count sets the cost (one credit per job), and a single job runs up to 300 s, so packing settings into a
job lowers the cost per setting.

## Follow-ups

1. Repair `scripts/ascella_transition_ci_check.py --matched-check`: it fails with "the frozen next-day case differs:
   docs/evidence/ascella-transition-day-repeat-ci/campaign.json" on `main`, under the pinned 3.14.7 interpreter, for
   the first repeat that it previously admitted, because `ascella_transition_day_repeat.build_files()` no longer
   rebuilds the retained campaign bytes. The cause is not yet located.
2. Locate the four unretained jobs (three `qpu:ascella`, one `sim:ascella`): list each retained job id from
   `qd_job_status` against the account's job list through the dashboard session, and compare with the
   schedule receipts and the Codex worktree `a9e6`, whose 41 runs end at 2026-10-22.
3. Merge or discard `fix/ascella-predecessor-current-command-binding`: it holds the one retained Quandela run absent from
   `main`.
4. Rescore the teleportation fidelity model at the live Belenos figures and write `teleportation_rehearsal/job-01`.
5. Compute the power of the lag-trend statistic for a random walk against a bounded mean-reverting drift at nine runs
   over 48 hours, per plan `belenos-drift-memory-successor`, and write that case only above 0.8.
6. Turn the join used here into a gated script, so the inventory regenerates from the records.

## Update after the approved Ascella run

The owner approved the Ascella matched-mesh repeat at the 1.131072-credit ceiling. Job
`cb8717bc-6bb3-4cbd-b508-a8f4d73c20c7` ran on `qpu:ascella` and returned 327,680 accepted events (65,536 per setting)
in a completed status. [The handoff](../handoffs/2026-10-30-quandela-next-cases.md) records the comparison and the
exploratory claim `ascella-transition-matched-mesh-third-acquisition`. The matched-mesh check named in follow-up 1 could
not qualify the run, so its mesh identity rests on equal settings and compilation seeds.

## Not run

- `qd_job_billing` ran on four jobs, not on all 128; the usage report supplies the total.
- The content of each family's analysis was read for the drift series, the packed mode swap and the transition repeat
  only; the Ascella order, context and port pilots were counted, not read.
- The `sim:*` against `qpu:*` residuals were paired by digest, not recomputed.
- The power calculation of follow-up 5 was not run.
