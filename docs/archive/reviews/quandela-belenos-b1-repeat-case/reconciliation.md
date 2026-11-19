# Reconciliation: local review of PR 960 (quandela: sim:belenos b1 completion-time repeat case)

Head read: 59df6c7515852ac3cd7a8d919ff2084b4cf84d7f. Reviewer: the local codex round (gpt-daybreak-blue, read-only, exit 0), chosen by the owner on 2026-11-19; the Advisor last. Every finding below carries its disposition; a fixing commit is named by its full hash after its diff was read.

| # | Finding | Source | Check | Verdict |
|---|---|---|---|---|
| 1 | SERIOUS: the timing model reads progress as fractional iteration completion | codex | b1-j2 progress 0.9586667 against 920000 / 40000 = 23 iterations | Fixed in 3574a18755823940a8a747e56ca612bba2447d41: progress is not read as a fraction; job-level timing only |
| 2 | SERIOUS: the case specifies four jobs, the owner chose three runs per request | codex | CASE.md lines 44 to 118 | Fixed in 3574a18755823940a8a747e56ca612bba2447d41: six jobs, 6.0 credits, cap 6.48, relative range statistic |
| 3 | SERIOUS: a fixed order confounds request with order | codex | order P1 before P2 in every pair | Fixed in 3574a18755823940a8a747e56ca612bba2447d41 (counterbalanced blocks, residual assumption stated) and ab15fb06d5cf6f68d74ab3c217bf1b98d816cfcf (slot means 3.33 and 3.67 stated); the residual partial balance stays open as a stated limit |
| 4 | SERIOUS: 300 s is a cancellation threshold, not a duration ceiling | codex | b1-j2 max_duration 300, reported duration 305 | Fixed in 3574a18755823940a8a747e56ca612bba2447d41: 1800 s budget with 1830 s possible stated |
| 5 | SLOPPY: bill, ceiling and authorization cap conflated | codex | credit_ceiling 1.0 against max_credits 1.08 | Fixed in 3574a18755823940a8a747e56ca612bba2447d41: 1.0 bill, 1.08 cap |
| 6 | SLOPPY: polling presented as iteration telemetry | codex | no source contract for progress increments | Fixed in 3574a18755823940a8a747e56ca612bba2447d41: progress is logged, not analyzed |
| A1 | Advisor (parent) | Advisor | read after the fixes | Two fixes were still needed and are in ab15fb06d5cf6f68d74ab3c217bf1b98d816cfcf: the slot imbalance statement and the doubling bound in the decision table |
