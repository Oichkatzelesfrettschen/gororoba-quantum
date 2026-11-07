# Reconciliation: Ascella long-horizon seed repeat (job-08) review

Three reviewers read commit `e98d5b324` on one [brief](ascella-long-horizon-seed-repeat-review-brief.md) before any
credit was spent: `codex` on gpt-daybreak-blue at high effort
([report](ascella-long-horizon-seed-repeat-review-codex-daybreak-blue.md)), an Opus agent
([report](ascella-long-horizon-seed-repeat-review-opus.md)) and `grok`, whose session compacted its context and exited
after its progress notes without a report. Each finding was checked against the files and the retained runs.

| Finding | Reviewers | Check | Resolution |
|---|---|---|---|
| Mesh identity compares serialized `computed_circuit` bytes, so float jitter between compile stacks reads as a redrawn mesh and stops the reading | Codex (fatal), Opus | The `sim:ascella` replay of job-02 equals none of the QPU's 64 strings, while every deserialized unitary lies within 2.4e-7 of the QPU's (60 of 64 within 1e-9) | Fixed: M reads unitaries within 1e-6 (largest entry modulus) and records the byte-equal count; a fixture pins 64 within tolerance and 0 byte-equal; the design, plan and research-state question now say the simulator serves the QPU's meshes |
| Value 56 of an order draw seeds two readings, and the rehearsal reuses the value the seed-repeat reading took | Opus | `PERMUTATION_INDEX` read the repeat's own draw for every pair | Fixed: each pair takes its own value of the new draw (56 job-03 against job-08, 58 job-02 against job-08, 59 the rehearsal; 57 stays the power record); the rehearsal record is rewritten and still reads persists (upper bound 1.074) |
| Tests do not cover a partial sample of relabelings or the identity path | Codex | The only sampled test passed all m! relabelings | Fixed: a 1,000-relabeling test checks the p-value is monotone in the slope, at least 1/1000, and switches at the inverted bound; the identity fixture above covers M. Synthetic end-to-end run pairs remain unwritten; the rehearsal replay gate exercises the full path on retained runs |
| Plan steps read `doing` and `todo` for finished work | Codex, Opus | The commit held the frozen body, both sim runs and the rehearsal | Fixed with receipts |
| `except (ValueError, PlatformError)` lost its parentheses in a functional commit | Opus | The formatter ran without CI's `--target-version py313` | Reverted; every touched file passes `ruff format --check --target-version py313` |

Both reviewers found the sampled Monte Carlo p-values valid with the identity in the reference set, the bisection
monotone, the exact path unchanged, and the request, budget, seeds and power model consistent with the written case.

## Second review: the first-principles findings

`codex` on gpt-daybreak-blue reviewed commit `782b189ad`
([report](ascella-long-horizon-seed-repeat-review2-codex-daybreak-blue.md)). It reproduced the by-name r 0.924550,
position-paired r -0.199119 and the 7.71-fold variance factor, found every seed echo, digest binding and the X
statistic's construction sound, and confirmed the dense-operand mode count. Its four findings each survived a check
against the files and are fixed in the findings note:

| Finding | Resolution |
|---|---|
| "Chip" attribution exceeds the evidence: `computed_circuit` is the provider's reported model, not a readback of the implemented unitary | The note refutes a returned-model mismatch and supports an implementation-path error; firmware, heater mapping and chip stay unseparated until telemetry exists |
| The per-seed correction was defined after job-08 and called out of sample | Labeled retrospective; the estimator stays frozen and scores on the next acquisition; the last residual term reads unexplained |
| "A redrawn share would lower r, which it does not" overstates the test | Replaced by the 99 % Fisher interval 0.862 to 0.960 and "not detected at this precision" |
| The ledger closes nonlinear drift, longer-memory carryover and mesh-dependent overdispersion that no control tested | The ledger names the bounded controls that passed and keeps the rest open |
