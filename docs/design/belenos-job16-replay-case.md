# Belenos job-16 byte replay case

Written case, awaiting owner approval, for one qpu:belenos job that replays belenos_mesh/job-16's circuit byte for byte
and separates a chip or server change after the 2026-11-27 outage from a property of the off-cone mechanisms case
([script](../../scripts/belenos_job16_replay.py), cases in `results/quandela/cases/belenos_job16_replay/job-00`). No job
was submitted, planned against the live service or created in writing this case.

## What the job measures

belenos_offcone_mechanisms job-00 to job-02 (2026-11-28) read mesh 29dc6ef8 at source 20 with in_block_cone medians of
0.158 to 0.170 and tvd_cone_from_ideal medians of 0.868 to 0.889, against 0.9917 and 0.0915 over the 13 29dc6ef8 entries of
belenos_mesh/job-16 (2026-10-18); the routing gate of the analyzer withholds every mechanism verdict
([findings](belenos-offcone-mechanisms-case.md#findings)). Two explanations remain: the chip or server changed across the
outage, or the case's own choices (a per-iteration input_mode, sources 20 and 22, 715,000 samples per job) moved the
routing. A noise simulation cannot answer it, since the question concerns the device's present state.

The job sends job-16's `circuit.json` unchanged (sha256 `69326bf0674a45e8c0005b10e2ac72cee36c122691ec0a5b542dbabb6e1fffb9`),
single source mode 20, no per-iteration input_mode and the server's default mitigations: ten entries of 10,000 samples,
alternating compilation seeds 20 (mesh 29dc6ef8, entries 0, 2, 4, 6, 8) and 46667 (mesh 14a96ca6, entries 1, 3, 5, 7, 9).
`cases.json` has sha256 `e280f39f59c45579caa174d76667a39b888a0c8554a17222392062a3b331e725`.

## Seeds

Both seeds reproduce retained compiled meshes of job-16, so they are identifiers that keep their values (AGENTS.md,
"Seeds": a job that reproduces an earlier result imports the earlier seed constant by name). The builder imports
`qd_belenos_mesh.DWELL_Q1_SEED` (20) and `qd_belenos_mesh.anu_seed(DWELL_ANU)` (46667, index 0 of the ANU draw
`draw-2026-10-18T083548Z.json`, also the `seed_source` of job-16); the case draws no new value and the ANU draw of
2026-11-27 stays unconsumed.

## Prediction, falsifiers and readings

The routing statistics are those of `scripts/qd_belenos_cone.py` `run_cells`; the envelope is the analyzer's routing gate,
the minimum in_block_cone (0.450353) and the maximum tvd_cone_from_ideal (0.819035) of job-16's 29dc6ef8 entries. The
first two job-16 entries failed (in_block_cone 0.450 and 0.457), the other 11 read 0.982 to 0.994. Entry 0 of this job
opens it as those did, so it is reported and decides nothing; the decision rests on the four seed-20 entries that follow
a seed-46667 load (entries 2, 4, 6, 8), the position of job-16's 11 healthy entries.

| Observable | chip or server changed | case property |
|---|---|---|
| post-load seed-20 entries inside the envelope | at most 1 of 4 (the new runs: 1 of 45 entries) | at least 3 of 4 at in_block_cone 0.98 or more (job-16: 11 of 11) |
| entries of 10 with a mode among 0, 1, 5 at 32 or more clicks | 0 (the new runs: 0 of 90) | at least 8 (job-16: 23 of 24) |
| mode-6 clicks per seed-20 entry | about 7 (mean 7.07, range 0 to 13, over the 15 10,000-sample entries) | 0 (job-16: 13 of 13) |

Falsifiers: three or more post-load seed-20 entries at in_block_cone 0.98 or more falsify "chip or server changed"; at most
one such entry, or no entry with a mode among 0, 1, 5 at 32 or more clicks, falsifies "case property". A served mesh prefix other than the seed's retained one on any entry reads "compiler changed", decided first, since the routing comparison then has no fixed mesh; a seed-20 entry after a void seed-46667 entry is excluded from the post-load count. Any other pattern attributes nothing. The figures come from the retained runs by `run_cells` (job-16) and
`docs/evidence/quandela/belenos_offcone_mechanisms_analysis.json` (the new runs), recomputed for this case. The red-team
figure of 0, 1, 5 packets at 23 of 24 in job-16 holds for the entries of both seeds (13 of 13 at seed 20, 10 of 11 at seed
46667); the post-load seed-46667 entries are a second control that a chip-wide change would also move.

## Seconds, credits, shots

- Shot cap: twice the samples per entry (the builder rule, `SHOT_HEADROOM` 2): 20,000 per entry, `max_shots` 200,000,
  `max_samples` 100,000.
- Seconds: the fixed overhead 8.16 s plus 6.00 s per entry from the ten-run fit of
  `docs/evidence/quandela/belenos_offcone_packets.json` (retained jobs: job-16, 24 entries, 149 s against 152.2 s fitted;
  job-00 to job-02, 30 entries, 191, 203 and 192 s against 188.2 s) gives 68.2 s, at most 74 s at the largest residual
  (+8 percent). The plan figure is the runbook's 7.3 s per entry, 8.16 + 73 = 81.16 s, and the slow bound of 9.6 s per
  entry gives 104.16 s, inside `max_duration` 300 s and its 0.9 margin of 270 s.
- Credits: 1 + 1e-6 x the largest iteration's cap (20,000) = 1.02.

## Plans

`"$PYTHON" scripts/belenos_job16_replay.py --offline-plan` runs `qd_platform.plan` with every provider read replaced by the
retained catalogue of 2026-10-20 (explorer row, processor record, availability) and a stand-in token, with both
statuses set to "available" because the retained records read "calibration". It gives `expected_seconds` 81.16,
`estimated_shots` 100,000 (cap 200,000), `credit_ceiling` 1.02, `body_sha256_without_process_id` `b42f917126c39858e7ffaccc4be381e5e7ae58117c5c3ea90aa78bcdb86b63f5`. The raw `body_sha256` includes the per-process `process_id` (a uuid4 that Perceval draws at module load), so it differs between two invocations; the stripped digest is the one that agrees across processes (`tests/scripts/test_belenos_job16_replay.py`).
That plan rehearses the arithmetic and the payload only. The live plan (`qd_platform.py plan` with `QUANDELA_TOKEN_FILE`,
`--max-credits 1.02 --expected-seconds 81.16 --per-job-credits 1`) was not run: it reads the job token, which this
session leaves alone, and the binding `approved_run.sh` check follows owner approval.

## Conditions that stop the replay

- The live plan refuses unless qpu:belenos reads "available" on both records; the retained catalogue reads "calibration".
  The case admits no other status.
- A live plan whose `body_sha256` with `process_id` removed differs from the offline plan's `body_sha256_without_process_id` signals a changed payload format or command set
  (`payload_version_basis` names the frozen record that supplies `specs.commands`).
- The live architecture comparison refuses a live `specs.architecture` that differs from the catalogue's; a carried
  architecture (`architecture_source` "carried") leaves the live couplers unread, and `compiled_couplers_checked` at
  collect then reads the compiled couplers.
- Entry 0 carries the first-entry confound of job-16; a failing entry 0 beside three healthy post-load entries reads
  "case property".
