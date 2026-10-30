# Belenos recovery watch and the job-01 rehearsal

This handoff carries the single-chip teleportation rehearsal on Quandela's `qpu:belenos` from its first run (job-00,
retained) to its second (job-01, machinery and seeds in the tree, case files pending the recovered record). It stands alone for a reader with no access to the session that
wrote it. Issue [#556](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/556) is the live thread:
the scheduled watch posts every event there, and the owner reads it. The plan record
[ascella-belenos-entanglement-teleportation.json](../../state/plans/ascella-belenos-entanglement-teleportation.json),
step `recovered-chip-rehearsal`, owns the work status; the design
[ascella-belenos-entanglement-teleportation.md](../../design/ascella-belenos-entanglement-teleportation.md),
section "Single-chip rehearsal (job-00)", owns the request, the decision rule and the budget.

## State on 2026-10-26

- The rehearsal teleports the six Pauli eigenstates of one dual-rail qubit through a Bell pair that a postselected
  Ralph CNOT builds on the same chip, three photons on eight logical modes. A preregistered decision compares the
  pooled conditional fidelity with F* = 0.86 (the model's lowest pooled fidelity at the 2026-10-24 15:35 UTC anchor
  read, HOM 88.8 %, g2 1.1 %, Transmittance 5.5 %) and with the classical bound B = 0.6937; 314 accepted outcomes
  decide at alpha 0.01, beta 0.10.
- Job-00 (Quandela job `55479252-d907-45ac-b1e1-84f19d21a131`, 2026-10-26 02:54:50 UTC, 292 s, 2.2 credits) ran
  under the owner's single-use anchor-gate approval and returned no three-click sample in six iterations of
  1,200,000 shots. Verdict `inconclusive`, record-state class `degraded-as-recorded`: the chip matched the degraded
  record. Run directory
  [results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00](../../../results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/),
  registry acquisition `qd-qpu-belenos-teleportation-rehearsal-job-00`, claim
  `qd-belenos-teleportation-rehearsal-job-00`, replay gate `core-teleportation-rehearsal-job-00-replay`.
- The performance record held one state from 2026-10-25 18:47 UTC (perfs sha256 `ae1cc9f8f9999bd76ecf8857fc6cd9a591c4ee9656880194a5cb9ca775e20446`,
  HOM 83.8 %, g2 16.7 %, Transmittance 0.05 %; the rehearsal model scores it 0.635). It left that state between the
  watch reads of 07:13 and 08:58 UTC on 2026-10-26, inside a maintenance window the public explorer lists from
  2026-10-26 08:30 UTC to 2026-10-29 11:30 UTC. The record reads status `maintenance`, HOM 83.8 %, g2 66.7 %,
  Transmittance 0.06 % (retained read
  [live-processor-qpu-belenos-2026-10-26T12-58-09Z.json](../../evidence/quandela/live-processor-qpu-belenos-2026-10-26T12-58-09Z.json),
  interpretation in [calibration.md](../../notes/quandela/calibration.md#belenos-read-of-2026-10-25-1904-utc)).
  Perceval's source model rejects emission_probability * g2 above 0.5, so the rehearsal model scores no fidelity at
  these figures.
- No local watcher runs. The scheduled workflow below is the only watch.

## The watch

[.github/workflows/quandela-record-watch.yml](../../../.github/workflows/quandela-record-watch.yml) runs on main in
the `quandela` environment at minute 41 of every even UTC hour; GitHub starts scheduled runs late (7 to 31 minutes
on 2026-10-26), so the first read after the booked end of 11:30 UTC lands at about 12:41 UTC or later. Each run calls
`scripts/qd_record_watch.py check` ([runbook](../../runbooks/quandela-scheduled-runs.md#record-watch)), which reads
the processor record and classifies it against
[qpu-belenos-held.json](../../../results/quandela/watch/qpu-belenos-held.json):

| class | meaning | workflow action |
|---|---|---|
| `held` | perfs digest equals the held one | none |
| `missing` | a figure the model reads is absent | none |
| `unscorable` | changed, and the model raises ValueError on the figures | none; the watch stays armed |
| `changed` | changed, and the model scores it | comment with both sets of figures and the pooled fidelity against F* = 0.86, then disable the workflow |

The same run reads the platform's explorer row against the window named by
[qpu-belenos-booking.json](../../../results/quandela/watch/qpu-belenos-booking.json) and posts at most one comment per
booking event: `ended` (the row lists no window or another window, sets `maintenance_ended`, or reports a status other
than `maintenance`), `overran` (the window still runs at or after its listed end) and `moved` (the listed end differs
from the booked one). Each booking comment states the record class at the same read. A failed run comments once per
commit with the run URL. Every comment goes to the open issue titled "qpu:belenos performance record changed"
(#556; the workflow opens a new one when none is open), starts with an HTML marker the workflow deduplicates on, and
ends with a mention of the repository owner, so GitHub notifies the owner of each one. The watch submits, stages,
books and plans nothing.

Check that the watch is armed with
`gh api repos/Oichkatzelesfrettschen/gororoba-quantum/actions/workflows/quandela-record-watch.yml --jq .state`
(`active`) and list its runs with `.../quandela-record-watch.yml/runs?per_page=5`.

## Instructions for an assistant watching #556

Watch issue #556 for new comments from `github-actions`. On each one, notify the owner through the channel the owner
gave you, quote the comment's first two paragraphs, and name its kind (booking ended, overran or moved; record
changed; run failed). Take no other action: submit, stage, book, cancel and plan nothing on any provider, read no
token or key file, and post nothing to #556 or to Quandela. Every job on any provider waits for the owner's approval
of a written case.

## Procedure for each comment

**Booking ended, overran or moved, record `unscorable` or `held`.** Job-01 stays held. Report the comment to the owner.
A window that overran or moved leaves the watch armed for the next event. If the window ended and the record stays
`unscorable` for more than a day, the owner decides whether to ask Quandela about the published figures; the draft
contact text lives only in the owner's checkout under the ignored `docs/local/`.

**Record `changed`.** The workflow has disabled itself. Its comment gives job-00's model pooled fidelity at the new
figures, a guide to the chip's state and no admission threshold. Job-01 is a descriptive acquisition preregistered
at its own read (design section "Recovered-chip rehearsal (job-01)"). `--prepare` refuses only a read whose modeled
seconds exceed the 300 s `max_duration`, or for which Perceval estimates no shots. At job-00's modeled
probabilities the preregistered 1200 samples per iteration in twelve iterations take 240 s.

- Prepare job-01 by the procedure of [Building job-01](#building-job-01). Its written case carries the forecast
  correctness, the forecast lower bound against each comparison, and the derived credits and seconds, so the owner
  weighs the expected result and the cost before approving.
- When `--prepare` refuses, report the refusal and re-arm the watch for the new state.
- Re-arm the watch in either case when the owner wants later reads reported. Nothing is submitted before the owner
  approves the written case; the job-00 approval covered one submission and does not carry over.

Re-arm the watch for a new state through one pull request:

1. `"$PYTHON" scripts/qd_platform.py snapshot --out DIR` (needs `QUANDELA_TOKEN_FILE`) writes `DIR/catalogue.json`;
   retain it under `docs/evidence/quandela/` or a run directory.
2. `"$PYTHON" scripts/qd_record_watch.py held CATALOGUE qpu:belenos --out results/quandela/watch/qpu-belenos-held.json`.
3. Update `READS` and the held figures in `tests/scripts/test_qd_record_watch.py`
   (`test_held_digest_names_every_retained_read_of_the_held_state`), which bind the held file to its retained reads.
4. Replace or drop `qpu-belenos-booking.json` (and the workflow's `--booking` arguments) when no window is pending.
5. After the merge, `gh api -X PUT repos/Oichkatzelesfrettschen/gororoba-quantum/actions/workflows/quandela-record-watch.yml/enable`.

**Run failed.** Read the run log, fix the cause in a pull request, and confirm the next run. The failure marker keys
on the commit, so the fixed commit posts again if it fails.

## Building job-01

The job-01 machinery and seeds are in the tree; the case files wait for the recovered record. The design section
[Recovered-chip rehearsal (job-01)](../../design/ascella-belenos-entanglement-teleportation.md#recovered-chip-rehearsal-job-01)
holds the question, the preregistration rule and the six-step procedure. The facts it rests on:

- The owner chose on 2026-10-26 to preregister job-01 at its own platform read, and then to redesign it. The
  record admits no applicable classical bound: each input compiles into its own circuit, multiphoton inputs under
  free postselection raise the bound to 3/4 or more, and the service reports no optical attempts. Job-01 is
  therefore descriptive: an anytime-valid lower confidence bound on the accepted events' correctness, a block
  homogeneity veto, and two comparisons, against 3/4 and against the attempt-box bound at ratio 1.1, each valid
  only under its named assumptions. The record behind this is the
  [consult](../reviews/2026-10-26-belenos-job-01-redesign-consult.md) and its
  [disposition](../reviews/2026-10-26-belenos-job-01-redesign-disposition.md).
- Twelve iterations, two blocks: block A in design order and block B mirrored. `JOB_01_COMPILATION_SEEDS` holds the
  twelve seeds, from the Outshift draw `draw-2026-10-26T204106Z.json` (block A) and the ANU draw
  `draw-2026-10-26T230602Z.json` (block B), indices 0 to 5 of each, registered in
  `docs/evidence/qrng_seeds/allocations.json`.
- `scripts/qd_teleportation_rehearsal.py` carries both rules: each `Request` names its rule and block count
  (`CASE_DESIGNS`).
  - The descriptive rule's analysis writes schema `qd-teleportation-analysis-v2`, and binds result iterations by
    circuit parameters and compilation seed.
  - Its `binding` gate admits a live performance record that keeps the layout's dark-rate rule and the expected seconds, floored at 27.3 s per iteration, within `max_duration`.
  - `scripts/qd_rehearsal_secondary.py` binds the same way.
- `--prepare job-01` derives the layout, `noise-model.json` and `shot-estimate.json` from
  `results/quandela/cases/teleportation_rehearsal/job-01/platform-read/catalogue.json`, prints the forecast, then
  prints the `REQUESTS` and `JOBS` rows.

When the watch posts a scorable change, take step 1 of the design's procedure (the snapshot), then step 2, and open
one pull request with:
- the read, the derivation and the estimate;
- the two rows and the case files;
- the frozen body and the plan record;
- the written-case paragraph.

The written case then goes to the owner. If the live record changes between preparation and submission, `binding`
refuses, and the case is prepared again from the new read. A split into several jobs is a different experiment and
needs its own reviewed case. The twelve seeds stay reserved for job-01.

Two details matter when job-01 is retained:
- **Break-even replay.** `break_even_ratio` bisects on strict comparisons against certified solver values, so a
  last-digit difference between runners can move it by one bisection step, 0.005. Exempt that field from the replay
  gate's byte comparison, or compare it on the 0.005 grid.
- **Shot estimate.** `shot-estimate.json` keys its `inputs` by label, so block B's estimates replace block A's in
  the record. Both blocks run identical parameters, so the shot ceiling is unaffected.

## References

| item | content |
|---|---|
| PR #493 | ideal dual-rail teleportation instrument and the Ascella-Belenos design gates |
| PR #509 | classical teleportation benchmarks over the PPT Choi cone (the bound B) |
| PR #515 | the single-chip rehearsal case for `qpu:belenos` (job-00) |
| PR #521 | guarded submit path (`--submit RUN APPROVAL`, `binding`) |
| PR #527 | the held performance record |
| PR #535 | anchor-gated submission and preregistered secondary analyses |
| PR #538 | job-00 retained: run, analyses, replay gate, registry claim |
| PR #541 | the scheduled record watch |
| PR #555 | the `unscorable` class |
| the pull request adding this file | booking events, comment deduplication, failure comments, this handoff |
| the pull request adding job-01 | per-case `Request` (layout, seeds, anchor read), `--prepare`, job-01 seeds, the design's job-01 section |
| issue #556 | the live thread the watch posts to |
| [Perceval #798](https://github.com/Quandela/Perceval/issues/798) | remote result contract (computed_circuit, count provenance, mitigations); no reply on 2026-10-26 |
| [Perceval #799](https://github.com/Quandela/Perceval/issues/799) | Ascella per-job calibration; one cross-reference comment from the owner |

The owner still has to submit the Quandela contact-form request for a joint Ascella-Belenos configuration; its text
is in the owner's checkout only (ignored `docs/local/`), and the plan record's `pause` names the answer that resumes
the network work.
