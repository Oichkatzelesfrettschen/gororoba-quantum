# Review record: the interleaved Tuna-17 submit gate (PR 971)

Local reviewers: none (owner choice, 2026-11-21). The Advisor reviewed last, on facfcf748, with the session's evidence.

| # | Finding | Disposition |
|---|---|---|
| 1 | Amending the approved case's CASE.md in place breaks the rule that a submitted case keeps its bytes | Fixed: CASE.md restored to its origin/main bytes; the amendment is `docs/notes/quantum_inspire/tuna17-interleaved-submit-gate.md` with its docs/README.md row |
| 2 | The stricter sanity fields may refuse retained records main tracks | Measured: the 30 tracked QX twin run directories pass `--sanity` under the origin/main script and under this branch; no ci/gates.json entry names the script; all 30 Tuna-17 receipts carry `queue_user_only` true and an own queue of 0 |
| 3 | "The execution-start rule is unchanged" overstates: `status_label` now reads an executing type with a calibrating instance as calibrating | Fixed: the note and the PR body state that the start check tightens |
| 4 | "Another user's job" is an inference | Fixed: the note cites the runner's 17:36:07Z poll (own queue 0, account-wide queue 2) and labels the inference |
| 5 | The code comment credits the own-queue read with keeping batches apart, while a running batch leaves that count | Fixed: the comment names collect-before-submit as the mechanism |
| 6 | Batches 02 and 03 ran 18.5 h after batch 00 under this branch's script | Recorded in the note; the retention change names facfcf748 and compares the two w0 batches before pooling |
