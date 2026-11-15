# Review of PR 907 (residual nullity-4 strata of the orbit normal forms)

The launcher ran one local reviewer on this pull request: `codex` on gpt-daybreak-blue-latest at high effort. It read
[brief.md](brief.md) at head ac3255d55 and wrote [review-codex.md](review-codex.md); every computation ran on a
remote checkout of that head. It confirms the arguments of A5-537, A5-539 and A5-540, the exact witnesses of A5-552,
and the dispositions of A5-441, A5-442 and A5-538. The launcher checked each finding against the source, and all four
hold. Local paths, host names and the remote command in both files are replaced by placeholders.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | The Singular runner of `nullity4_quartic_discriminant.py` and the audit of `tests/test_a5_nullity4_polar_line_stack.py` accept a process that exits nonzero or writes a fatal error, read no init-file flag and check no version | holds | `run_checked` requires exit status 0, an empty stderr, `--no-rc`, no `?` error line and the terminal marker; `_singular` requires the version 4.4.1 from `--version`; both gates use them. Planted executables (status 7 with a fatal stderr and the expected stdout, status 7 alone, a fatal stderr alone, release 4.3.2) are refused, and a clean one is accepted. |
| 2 | A5-550 and A5-552 are proved rows that state real nullities through the identification of A5-554, which only survives | holds | The real-nullity parentheticals leave both claims; A5-554 keeps the real statement and cites A5-550. |
| 3 | A5-541's basis says its nullity-12 clause holds by A5-552, which covers only `P = P_x` with `u.u` nonzero and `s^2` other than 1; its primes column reads 32029 | holds | The clause is open in A5-553 with the missing lemma (every real nullity-4 point with `dim C(P) = 5` lies in that family); A5-541 reads `char0`, since exact witnesses over Q(i) decide it. |
| 4 | ci-runtime.md classifies a call-budget failure on a loaded host as no regression | holds | The runbook classifies only after a rerun unloaded or with the budget lifted, comparing the result and the unloaded time with the unit's earlier unloaded time. |

The reviewer's four next certificates (an interval Newton step for A5-551; a compact-frame elimination at `s = +-1`;
the second chart of the conic; the rank 10 of the totally isotropic pairs) are recorded as hypotheses with their
falsifiers in the bases of A5-551 and A5-553.

## Advisor verdict

