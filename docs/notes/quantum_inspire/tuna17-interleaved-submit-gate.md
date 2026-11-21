# Tuna-17 interleaved characterization: the submit gate after 2026-11-21

The interleaved Tuna-17 case (`results/quantum_inspire/cases/characterization_interleaved_tuna_17`, approved
2026-11-19) keeps its approved CASE.md. This note records the owner's change of its submit gate on 2026-11-21 and the
evidence for it; `scripts/qi_tuna17_interleaved_cases.py` carries the rule.

## The rule before and after

The series admitted a batch only while Tuna-17 read `idle`, and `--sanity` required `backend_status_at_submit` of
`submission.json` to read `idle`. That rule stood for two conditions: this series never stacks a batch behind its own
previous one, and nothing is submitted while the device calibrates or is offline. It also refused a batch that would
only wait behind another user's job.

Since 2026-11-21 admission, the admission record and `--sanity` require a device status in `SUBMIT_STATUSES`
(`idle` or `executing`) and the account's own queue empty at submit (`queue_user_only` true,
`number_of_jobs_in_queue` 0). `submit_series` collects each batch before it submits the next, and that is what keeps
the series' batches apart: a running batch of the account leaves the own-queue count (batch 01's trace read 1 at
17:36:24Z while it waited and 0 at 17:36:43Z while it executed), so the own-queue read refuses only a submission behind
a batch still waiting. `status_label` names a reading outside `SUBMIT_STATUSES` first, so an executing type with a
calibrating instance reads `calibrating`; this tightens the execution-start check (`START_STATUSES`) as well.

## The batch that prompted it

Batch 01 of arm `q12_phase` (stamp `2026-11-19T1735Z-t17`) passed its admission read at 17:36:11Z (`idle`, own queue
0). The lab runner's poll at 17:36:07Z read the device `idle` with an own queue of 0 and an account-wide queue of 2, so
other users held jobs (inference from the queue counts; the jobs themselves are not visible to this account). The
device read `executing` at the submit 8 s later, all three jobs completed, and the old `--sanity` stopped the series.

## Records under the new rule

All 30 Tuna-17 receipts of stamp `2026-11-19T1735Z-t17` (lab host, retained by the retention change) record
`queue_user_only` true with an own queue of 0; 29 read `idle` at submit and batch 01 reads `executing`. The 30 QX twin
run directories that main tracks (`results/quantum_inspire/runs/2026-11-19T1700Z-qx-characterization_interleaved_qx-*`)
pass `--sanity` under the old and the new rule. Batches 02 and 03 of `q12_phase` were submitted on 2026-11-21 by the
script at commit facfcf748 (this change), 18.5 hours after batch 00; the analysis compares the two `w0` batches (00
and 02) before pooling them.
