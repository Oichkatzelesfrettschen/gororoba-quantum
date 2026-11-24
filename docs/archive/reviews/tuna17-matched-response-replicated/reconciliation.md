# Reconciliation: replicated Tuna-17 matched-response proposal (pull request 998)

One local red-teamer read head 7a4ff6de1: opencode 2.1.2 on `opencode-go/glm-5.3` ([report](review-opencode.md), from
[this brief](redteam-brief.md)). Each finding was checked against the tree. Its verdict was "submit stage 1 after named
changes"; the changes are on head b694566e4.

| Finding | Verdict | Check | Change |
|---|---|---|---|
| F1: job ids and batch-job ids are compared within one run only, so shots of one replicate spliced into another replicate's manifest pass | confirmed | the two new faults ran against the unchanged module and did not raise | `analyze_replicated_series` takes the batch-job ids and refuses a repeated job id or batch-job id across replicates; two faults in `test_analysis_refuses_each_fault` |
| F2: "the level is exact for every sigma" holds for normal exchangeable residuals; the simulation drew normal residuals only | confirmed | Student t residuals with 3 degrees of freedom at SD 0.038: level 0.0112 (standard error 0.00016) against 0.0100 | the note and the module docstring scope the statement; the simulation holds the heavy-tailed row |
| F3: the simulation script wrote over its retained result by default | confirmed | script defaults | `--check` compares without writing; a write to an existing file needs `--overwrite` |
| F4: the approval case restates the refreshed queue and availability | accepted | provider read at 2026-11-24T03:10Z: Tuna-17 enabled and idle, at most 5 jobs per batch job, at most 5 batch jobs per queue | stated in the approval request |
| F5: the lag-1 mark needs abs(rho) above 0.566 at N = 12 | no defect | the conjunction of 0.3 and 1.96/sqrt(N) | none |

Claims the reviewer could not break, each with its own recomputation: the Stein constants (bit-exact against scipy) and an
independent 200,000-trial simulation of the level and power table; the cancellation of batch offsets in the one-batch
residual; the balance of the schedule over blocks of four; all 60 schedule rows against the digests on disk; the reuse of
the q11 circuit bytes; the costs; the carry-over of the predicted residual, whose estimand (g_2 - g_1)/2 does not depend on
the batch structure.

Two limits stay with the owner's decision and are stated in the design note: at the retained scatter estimate 0.038 the
cap of 60 replicates rejects a true residual of -0.024 in 70 percent of runs and stops undecided in 12 percent; the
scatter estimate rests on 3 degrees of freedom of a design with two batches per replicate, so the one-batch scatter is
unmeasured until stage 1.

The predecessor round (the nine-job proposals and the reason they do not run) is recorded in the
[analysis note](../../../design/tuna17-matched-response-analysis.md).
