# Reconciliation: local review of PR 927 (retained hosted QX run of the bracketed one-CZ-null series)

Head read by both reviewers: d79a5cd2b. Reviewers: codex (log header: model gpt-daybreak-blue, reasoning effort high, sandbox read-only; exit 0) and agy gemini-4-hydrogen-high (exit 0). git status clean after both. Scripts ran in a clone at d79a5cd2b with the pinned interpreter.

| # | Finding | From | Check | Verdict |
|---|---|---|---|---|
| F1 | The written case the owner approved is not retained; CASE.md calls it "not tracked", so nothing durable states what was approved (4 batches, 20 jobs, 40,960 shots, under 120 s, 0 credits). | codex (high) | The file exists in the ignored local directory of the primary checkout, 1,999 bytes, sha256 24f001fe...6e67, written 2026-11-15 before the run; two retained runs already carry a `written-case-at-approval.md`. | Survives. Fix: retain it in the batch-00 run directory under that name and cite it from CASE.md. |
| F2 | The stop-and-resume account conflicts with the source: the driver selects the bracketed sanity check by default, and the documented command sets `SANITY_COMMAND="true"`. | codex (high), agy 1 | scripts/qi_pathion_one_cz_null_submit.sh:54-58 selects the bracketed check since commit d96c12ca6, which postdates the run; the run of 2026-11-15 met the earlier default. CASE.md:458 does carry `SANITY_COMMAND="true"`, which disables the check. | Survives in part: the history is consistent once the commit is named; the command line is a defect. Fix: name the driver version in the sentence, drop the override. No transcript of the refused run is retained; the receipts show one submission per batch (codex SCRIPT-1). |
| F3 | Claim 7 of the brief ("nothing states a property of the Tuna-17 device") is false: the design document says reordering "is not particular to the Tuna-17 device". | codex (medium) | docs/design/bracketed-executed-order-analysis.md:17-19 read. The sentence compares platforms from the QX measurement. | Survives as a wording matter of the brief and the PR body: the PR reports no new Tuna-17 measurement. The PR body is corrected by the orchestrator. |
| F4 | The merge resolution of usage.json and research_state.json is a faithful union but rested on a worker's computation. | both | agy SCRIPT-2: "681 ledger jobs, unretained=[], matches origin/main snapshot". agy SCRIPT-3: "532 acquisitions (exact union), 4 new uncited, research_state --check passed". codex SCRIPT-3 fails at `usage_jobs <= retained`: its glob `runs/*/submission.json` finds 651 of 681 jobs, while the repository's `qi_platform.retained_job_ids()` (which walks `run_directories`) finds all 681; the 30 others are older receipts outside that glob. | Confirmed faithful; the codex script's failure is refuted by the repository's own enumeration. |
| F5 | research_state.py --check does not catch a stale "unretained" list. | agy 2 | research_state.py:424-430, 488-490 (reviewer's citation, not re-read). | Scoped: a gap of the checker, outside this PR; candidate issue. |
| F6 | docs/notes/quantum_inspire/README.md:99 says all ten "qi" gates run qxelarator; core-368 runs qi_toolchain_check.py. | agy 3 | ci/gates.json:2693-2699 (reviewer's citation). | Survives; fixed with the others. |
| F7 | "after PR 927 lands" in the design document; "authorization field" for the JSON key "approval". | agy 4 | CASE.md:400 read. | Survives; wording. |
| F8 | No token, account identifier, host name or absolute local path in the changed files. | both | agy SCRIPT-1 scan: 0 hits across 64 files. | Confirmed. |

Claims 1, 3 (computed-pending in both reports): codex SCRIPT-1 "4 batches; 5 jobs each; 20 unique jobs; shots/raw/digests/state/approval OK"; codex SCRIPT-2 "digest/gate/pass flags OK; analysis inputs cover all 20 jobs"; agy SCRIPT-1 "replayed exactly ... 20 jobs, 2.847960 s, analysis sha256 & replay exact". One edit to the agy scripts, statistics unchanged: the subprocess interpreter is the pinned one instead of `python3`. Claims 2, 4, 8: justified by both.

Claims 5 and 6 of the brief (the merged usage.json and research_state.json): undecided in both reports pending their scripts; settled as F4.

Fixes: bd574081e (F1, F2, F7) and 096c8417a (F6, F7); the Advisor round adds the commit that files this record, which also corrects the F6 sentence and one leftover pull-request number.

## Advisor verdicts (read 096c8417a)

| # | Verdict | Check that settles it |
|---|---|---|
| F1 | Confirmed fixed. | The retained file reads 1,999 bytes, sha256 24f001feb8082f6d84e63534df093a68fbf33785622d7ce5c8eec1f79e6e6e67, from the branch head. |
| F2 | Confirmed fixed. | scripts/qi_pathion_one_cz_null_submit.sh selects the bracketed check for every series named `pathion_one_cz_null_bracketed_*`, so the documented command runs without an override; d96c12ca6 is on main and was committed at 2026-11-15T19:36Z, after the run of 18:48Z. The stop-and-resume account rests on the receipts; no transcript of the refused batch is retained. |
| F3 | Confirmed as wording; the pull-request body states that it adds no Tuna-17 measurement. | Design document lines 17-19. |
| F4 | Confirmed. | `qi_platform.retained_job_ids()` finds all 681 ledger jobs; the union holds 532 acquisitions. |
| F5 | Refuted as a defect. | scripts/research_state.py removes a declared job that has since been retained from the unretained set by design ("a declared job whose run landed after the snapshot is retained"); orphans and absent declarations fail the check. |
| F6 | Fixed sentence was too specific: `scripts/qi_toolchain_check.py` reaches `qi_stack.live`, whose probe imports qxelarator. Corrected in the record commit to state that all ten run under the stack and none imports the SDK. | ci/gates.json lists ten gates requiring qi; gororoba_quantum/qi_stack.py PROBE. |
| F7 | Confirmed fixed; one further "PR 927" in the design document's table is corrected in the record commit. | git grep of the four changed files. |
| F8 | Confirmed for the new lines. | The fix diff carries no host, path or token. |

Validation on 096c8417a (compute host, pinned Python 3.14.7): the cases `--check`, `research_state.py --check`, `ci/seed_provenance.py --check` and `ci/runner_image_records.py check` exit 0; `pytest tests/scripts/test_results_index.py tests/scripts/test_qi_pathion_one_cz_null_bracketed.py`: 124 passed; ruff check and format clean.
