# Seed provenance owned-draw scan profile

The non-audit suite's `test_tree_seeds_are_accounted[0]` accounted for 47
seed literals but exceeded the 10-second per-test budget: 22.49 seconds in one
run and 12.52 seconds in a later run. An isolated repeat took 15.49 seconds;
a subsequent full run took 15.63 seconds and again accounted for all 47 literals.
The measurements do not establish the amount attributable to shared-host
contention. The other suite results and the outstanding timing obligation stay
in the Tuna readout-mapping plan.

Another two-worker non-audit run completed 2,036 tests and failed shards zero
and two solely on the 10-second budget: 26.12 and 23.15 seconds respectively.
An immediate one-worker rerun of those same two cases passed in 4.54 and 2.42
seconds. These observations show variable runtime, rather than identifying the
cause of the longer calls or proving that the full suite meets its budget.
The subsequent two-worker non-audit lane passed all 2,040 tests in 58.62
seconds. Shards zero and two took 4.84 and 2.61 seconds respectively in that
run. The passing rerun closes the current timing recheck; it does not explain
the previous slow runs or guarantee the budget under other host conditions.

A later non-audit run passed 1,891 tests with two Quantum Inspire-stack skips;
shard zero took 5.30 seconds in that run. The skipped module passed all 12 tests
when rerun with the pinned Quantum Inspire interpreter. The later pass shows
variable runtime, while the earlier failures and repeated scan remain evidence
for the open timing obligation.

On 2026-10-28 UTC, a single-worker `cProfile` run of
`seed_provenance.check_tree(0)` took 14.241 seconds including profiling
overhead. Its cumulative profile attributed 10.101 seconds to two calls of
`claimed_records`, with 16,396 calls to `file_claims` across both scans.
`check_tree` calls `claimed_records(MANIFEST_ROOT)` and then calls
`owned_records(validate=True)`, which calls `claimed_records(MANIFEST_ROOT)`
again. The tracked tree and host load can change these measurements.

Reusing the first claim set in owned-draw validation is a candidate for removing
the repeated scan. A change must preserve refusal of a draw simultaneously
owned by a case and an allocation, all reserved and runtime checks, and the
semantics of a changing tree. A targeted test must exercise the same claim set
through both ownership checks, and before/after measurements must use the same
host conditions and tree. The profile alone does not prove the change meets the
10-second budget. No optimization is implemented by this observation.
