# Reconciliation: local review of PR 948 (research_state self-test pool bounded by memory)

Head read: 6f9e6703d. Reviewer: codex (model gpt-daybreak-blue, reasoning effort high, read-only; exit 0); the owner chose codex and the Advisor.

| # | Finding | Check | Verdict |
|---|---|---|---|
| C1 to C5 | Claims 1 to 5 pass by inspection: cgroup v2 walk, the cap only lowers the count, the case specs keep order and copy boundaries, CaseVerdict pickles without a Context, records are restored in a finally block. | The diff was read by the orchestrator before the PR opened; the full self-test at the default worker count rejects 74 of 74 mutations. | Confirmed. |
| C6 | The 2 GiB per-worker figure is measurement-scoped: at 16 GiB it admits seven workers, 15.25 GiB projected, and the read is a snapshot with no reserve. | Arithmetic by hand: (16 - 1.25) // 2 = 7; measured peak 13.10 GB. | Confirmed; the PR body states the bound as measured. |
| D1 | The pool-cap test observes which processes ran, not the requested executor size. | tests/gororoba_quantum/test_parallel_memory.py:53-60 (reviewer's citation). | Survives; fixed by brief Z84. |
| D2 | The pickle test starts from an unloaded CaseVerdict, so a __getstate__ that kept _loaded would pass. | :77-79. | Survives; Z84. |
| D3 | The two-worker test passes for a serial implementation. | :65-74. | Survives; Z84. |
| D4 | No fail-closed guarantee against sibling allocations after the snapshot. | Same as C6. | Scoped: residual risk in the PR body. |
| D5 | The available-memory test lacks the malformed, absent, root-limit and over-limit cases. | :37. | Survives; Z84. |

## Fixes

Commits 477d54d1b, 46bc9c5dd and be614010f strengthen the tests; be614010f does not parse (a type-ignore comment swallowed the closing parentheses of a call) and stays in history; e926a6bb3 repairs it; 22eb8b5e7 sets the process budget directly in the pool tests and moves the malformed and absent cgroup files to the leaf. On 22eb8b5e7, compute host, pinned Python: the file passes unmutated (5 passed); 20 of 20 runs pass under `taskset -c 0,1`; the slowest test takes 0.94 s; ruff format, ruff check and mypy clean.

| Mutation | Failing test |
|---|---|
| M1 memory_workers returns 1 | test_worker_count_fits_the_reported_memory; test_ordered_map_requests_no_more_workers_than_fit; test_two_workers_return_the_serial_verdicts |
| M2 available_memory returns None | test_available_memory_is_the_tightest_headroom |
| M3 _run_chunk reverses | test_ordered_map_requests_no_more_workers_than_fit; test_two_workers_return_the_serial_verdicts |
| M4 ordered_map always serial | test_ordered_map_requests_no_more_workers_than_fit; test_two_workers_return_the_serial_verdicts |
| M5 _executor builds one worker | test_ordered_map_requests_no_more_workers_than_fit (got [(2, 1), (4, 1)]); test_two_workers_return_the_serial_verdicts |
| M6 worker_bytes ignored | test_ordered_map_requests_no_more_workers_than_fit (got [(4, 4), (4, 4)]) |
| M7 __getstate__ keeps state | test_case_verdict_pickles_without_loaded_state_and_cases_are_unique |
| M8 the cgroup walk stops at the first unreadable node (`break` for `continue`) | test_available_memory_is_the_tightest_headroom |

D1, D2, D3, D5: fixed by these commits. D4: residual risk in the PR body.

## Advisor verdicts (read e926a6bb3)

| # | Verdict |
|---|---|
| C1 to C6 | Stand. |
| D1, D2, D3 | Fixed: M5 and M6, M7, and M4 each fail the intended test. |
| D4 | Scoped to residual risk. |
| D5 | Partly fixed at e926a6bb3: the malformed and absent files sat where a walk that stops early still passed. Fixed in 22eb8b5e7 and shown by M8. |
| Host dependence | The pool tests read the host's CPU count through `workers()` and raced two workers; 22eb8b5e7 sets the budget directly, and the 20-run check on two CPUs measures the race. |

## Successor module

The hosted `arm (ubuntu-26.04-arm)` check on 8b8943a61 failed: `gororoba_quantum/parallel.py` is bound by sha256 in more than twenty retained records (`tests/scripts/test_ascella_predecessor_simulator.py`, `scripts/qi_matched_zero_divisor.py` producer dependency sources), so the edited file broke their binding. 147d9a3d7 and e3576c2e7 restore `parallel.py` to main's bytes and move the bound into `gororoba_quantum/parallel_memory.py`: `available_memory`, `memory_workers` and `bounded_ordered_map`, which caps the process budget through `GOROROBA_WORKERS` for the one call and restores the variable afterwards. `scripts/research_state.py`, whose digest no tracked file binds, calls it. The subject of 147d9a3d7 carries stray single quotes and stays in history.

On e3576c2e7 (compute host): the memory tests and the two predecessor tests, 29 passed; every mutation M1 to M8 above, and M9 (the cap left set after the call), fails at least one test; `ci/pr_checks.sh lint` and `types` clean; `research_state.py --self-test` at the default worker count in a 16 GiB scope: 74 mutations rejected, 79 s, memory.peak 13.2 GB.

## Advisor verdicts on the successor module (read c63521654)

| # | Verdict |
|---|---|
| Mechanism | Sound: the cap only lowers the budget, the variable returns in a finally block, an unknown figure leaves the call unchanged. Codex read 6f9e6703d only, before the redesign. |
| C2 | Superseded: the positive-size test moved out with the code, so a zero worker size divided by zero. 14bb4f54a rejects a size below one byte (M10). |
| Mutation table | Re-run by the orchestrator on 14bb4f54a: M1 to M10 each fail at least one test (M6 as a bounded map with no cap context, M9 as a cap that is not restored, M10 as a removed size guard); 20 of 20 runs pass under `taskset -c 0,1`; slowest test 0.83 s; `ci/pr_checks.sh lint` and `types` clean. |
