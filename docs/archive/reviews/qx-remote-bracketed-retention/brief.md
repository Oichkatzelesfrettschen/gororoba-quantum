# Brief: review of gororoba-quantum PR 927, the retained hosted QX run of the bracketed one-CZ-null series

Read first: the workspace guide (gororoba-infrastructure `workspace/AGENTS.md`) (workspace guide), then
AGENTS.md and its scripts/AGENTS.md and ci/AGENTS.md. Work read-only: change no file (the launcher captures your final answer); never
commit, push, stash, submit to any provider or emulator, or start a cloud resource; spawn no subagents.
Binding host rule: this host runs no computation. Read files with cat, sed, head or git show on a named path, and git diff --stat or git diff on named paths. Run no
python, no tests, no repository-wide grep. A computation you would have run goes into your report as a fenced block `SCRIPT-n` (python3, reading only
paths you name) with the output you expect; the orchestrator runs it on a compute host.

Material: a checkout of, branch qx-remote-bracketed-retention, head d79a5cd2b (frozen for this round); the pull request is
`git diff origin/main...HEAD` (64 files, about 44,750 inserted lines, nearly all retained run data). The head is one merge commit of origin/main (fc9a8daa2) on top of c43857992.

## Claims under review (each is a claim; justify or falsify it)
1. The four run directories results/quantum_inspire/runs/2026-11-15T184810Z-pathion_one_cz_null_bracketed_qx-batch-00 to -03 are complete retained records of one hosted QX series: 4 batches of 5 circuits, 2,048 shots, 20 jobs, 0 credits; each holds submission.json, submission-state.json, results.json and raw/ with one file per circuit. Status: measured (provider receipts). Falsifier: a batch with a missing or duplicated job id, a circuit digest in submission.json that differs from the case manifest's, a shot count other than 2,048, or a job id shared between batches.
2. No batch was submitted twice: the driver stopped after batch 0 on a sanity check that refused a bracketed run directory, and the same stamp resumed with SANITY_COMMAND. Status: measured (receipts). Falsifier: two submission records for one batch, or job ids of batch 0 that differ between submission.json and submission-state.json.
3. results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json has qx_control.pass and qx_brackets.pass true, is bound in ci/runner_image_records.json, and is replayed by the gate core-pathion-one-cz-null-bracketed-qx-analysis-replay of ci/gates.json through ci/replay_check.py. Status: computed. Falsifier: a digest in runner_image_records.json that differs from the file's (give the SCRIPT), a gate entry that names another path, or a pass flag derived from fewer than the 20 jobs.
4. Two of the four batches executed out of the requested order by queued_at (batches 02 and 03). Status: measured. Falsifier: the queued_at values of the receipts.
5. docs/evidence/quantum_inspire/usage.json holds the 20 jobs of this series, and its "unretained" list is empty at this head. The merge commit resolved a conflict in this file by taking main's later snapshot and recomputing "unretained" with qi_platform.retained_job_ids(). Status: computed by a worker, not by the documented generator (the generator needs a provider call). Falsifier: a job id of the four batches absent from usage.json; a job id in usage.json with no retained run directory at this head while "unretained" is empty; a field of main's snapshot other than "unretained" changed by the merge (read git show d79a5cd2b -- docs/evidence/quantum_inspire/usage.json against git show origin/main:docs/evidence/quantum_inspire/usage.json).
6. docs/state/research_state.json holds main's acquisitions and the branch's four hosted QX batch acquisitions after the merge, and no claim cites them. Status: computed (research_state.py --check passes at this head on a compute host). Falsifier: a dropped or duplicated acquisition id against origin/main and c43857992.
7. Nothing in the pull request states a property of the Tuna-17 device. Status: by inspection. Falsifier: a sentence in a changed tracked file that does.
8. The approval record in each submission.json carries the owner's sentence and the session's parenthetical. Status: by inspection. Falsifier: a submission.json without it.

## Questions to answer
- For each claim: justified, falsified, or undecided with the missing evidence.
- Defects in the changed code and documents (ci/, docs/design, docs/notes, the CASE.md of pathion_one_cz_null_bracketed_tuna_17) with file:line.
- Whether the merge commit's resolution of usage.json and research_state.json is a faithful union, and what check would catch a wrong one.
- Anything retained that should not be public: a token, a host name, an account identifier, an absolute local path.

## Report (print as your final answer, under 150 lines, ranked by consequence)
A verdict table for claims 1 to 8 with the decisive file:line; then findings, each tied to a file:line or a SCRIPT-n with its expected output, each marked measured, computed or hypothesis.
