# Belenos recovery watch and the job-01 rehearsal

This handoff carries the single-chip teleportation rehearsal on Quandela's `qpu:belenos` from its first run (job-00,
retained) to its second (job-01, not yet written). It stands alone for a reader with no access to the session that
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

**Record `changed`, pooled fidelity below 0.86.** Job-01 stays held; the workflow has disabled itself. Re-arm it for
the new state through one pull request:

1. `"$PYTHON" scripts/qd_platform.py snapshot --out DIR` (needs `QUANDELA_TOKEN_FILE`) writes `DIR/catalogue.json`;
   retain it under `docs/evidence/quandela/` or a run directory.
2. `"$PYTHON" scripts/qd_record_watch.py held CATALOGUE qpu:belenos --out results/quandela/watch/qpu-belenos-held.json`.
3. Update `READS` and the held figures in `tests/scripts/test_qd_record_watch.py`
   (`test_held_digest_names_every_retained_read_of_the_held_state`), which bind the held file to its retained reads.
4. Replace or drop `qpu-belenos-booking.json` (and the workflow's `--booking` arguments) when no window is pending.
5. After the merge, `gh api -X PUT repos/Oichkatzelesfrettschen/gororoba-quantum/actions/workflows/quandela-record-watch.yml/enable`.

**Record `changed`, pooled fidelity at or above 0.86.** Build job-01 as plan step `recovered-chip-rehearsal`
describes, and submit nothing before the owner approves its written case. The job-00 approval covered one
submission and does not carry over.

**Run failed.** Read the run log, fix the cause in a pull request, and confirm the next run. The failure marker keys
on the commit, so the fixed commit posts again if it fails.

## Building job-01

`scripts/qd_teleportation_rehearsal.py` serves job-00 only, and each of these places needs a job parameter:

- `COMPILATION_SEEDS` is one tuple of six seeds, and `check_setting` and `validate_body` require exactly those values. Job-01 takes six new values from a fresh ANU draw
  (`"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng`), registered as rows of
  `docs/evidence/qrng_seeds/allocations.json` with the draw file and index of each value, in index order
  (root AGENTS.md "Seeds"; `ci/seed_provenance.py` enforces it).
- `JOBS` holds one `Job("job-00", 900, 1_200_000, 2.2, 120.0)`; job-01 needs its row, with `max_shots` re-derived from
  `estimate_required_shots` under the fresh record.
- `CASES / "job-00"` is fixed in `variants` (the platform read), `retained_derivation` (noise-model.json),
  `shot_estimate`, `write_estimate`, `write_justification` and `simulate`; each takes the job's directory,
  `results/quandela/cases/teleportation_rehearsal/job-01/`.

The job-01 case then follows the job-00 sequence: retain the fresh platform read, `--justify` and `--estimate` under
it, write the case, run `--check`, plan it with `--plan job-01` and `--body job-01` (no `--anchor`: the live gate
applies), and write the case paragraph in the design. The written case states what the run measures, why a noise
simulation cannot answer it (only the chip shows whether its Bell pair and analyzer beat B), the backend
`qpu:belenos`, the shots, the expected seconds (job-00 took 292 s) and the credits (an iterated job bills
1 + largest `max_shots` * 1e-6, 2.2 for 1,200,000). After the owner's approval, `--submit RUN APPROVAL` sends it
once; `binding` refuses a body that differs from the retained `job-body.json` or a live model below F*. Retention
mirrors PR #538: the run directory with both analyses, `--check` replays, a replay gate modeled on
`core-teleportation-rehearsal-job-00-replay` with its `ci/runner_image_records.json` exempt entries, a registry
acquisition and claim inserted as text into the hand-formatted `docs/state/research_state.json`, and the plan step's
receipt. These code changes and the seed draw depend on no record and can land before the chip recovers.

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
| issue #556 | the live thread the watch posts to |
| [Perceval #798](https://github.com/Quandela/Perceval/issues/798) | remote result contract (computed_circuit, count provenance, mitigations); no reply on 2026-10-26 |
| [Perceval #799](https://github.com/Quandela/Perceval/issues/799) | Ascella per-job calibration; one cross-reference comment from the owner |

The owner still has to submit the Quandela contact-form request for a joint Ascella-Belenos configuration; its text
is in the owner's checkout only (ignored `docs/local/`), and the plan record's `pause` names the answer that resumes
the network work.
