# Review of pull request 1008: runner-relative test budget, shards, bytecode and per-job checkout

Head under review: 3d0ec25c9 (all eight jobs green in run 45534428488). Reviewers chosen by the owner on 2026-11-25:
`codex` (gpt-daybreak-blue, high effort, read-only) and `opencode` as red team on `opencode-go/hy4-flash-free`
(free OpenCode Go model, first and only attempt, verdict ok). Both read one brief with the six claims of the pull
request; neither changed a file (`git status` clean). The Advisor reviews last.

## Findings and dispositions

| # | Reviewer | Finding | Class | Disposition |
|---|---|---|---|---|
| 1 | codex | `runner_profile.py` capped BLAS threads with `setdefault` and left out `BLIS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS` and `NUMEXPR_NUM_THREADS`; on macOS the profile runs before `ci/pr_checks.sh` exports them, so Accelerate could calibrate several cores and under-scale a slow runner | computed | Fixed: `THREAD_CAPS` matches the pr_checks.sh set and is assigned unconditionally in the command-line process and in each pool worker (`initializer=cap_threads`); `test_thread_caps_match_the_suite_environment` binds the two sets |
| 2 | codex | `steal_fraction` read 0.0 where `/proc/stat` is absent | computed | Fixed: `None` (unmeasured) where no tick counters exist |
| 3 | codex, opencode | "Checkout was the largest step of every job" is false for the arm jobs (pytest 223 s and 342 s against checkout 193 s and 284 s) | measured | Fixed in docs/runbooks/ci-runtime.md and the pull-request body: the x64 jobs only |
| 4 | codex | The runbook said the four speed samples landed on three CPU models; they landed on EPYC 9V45 (three) and 9V74 (one), and the 7763 reading came from the slim-checkout job | measured | Fixed in the runbook |
| 5 | codex, opencode | The sparse patterns match one digit (`nf-d[0-9].txt`) and carry `.part*` for some families only, while ci/AGENTS.md named `nf-d*.txt` and `.part*` for each; a two-digit bulk file would return silently | computed (scratch sparse index) | Fixed by documenting the exact patterns and the fetch-until-named behavior; the patterns stay narrow, since a wider glob risks the failure class of heads 563951b and ed04cae (a small file the tests read left out) |
| 6 | codex | The macOS comment said a call fails past 45 s; the speed factor now multiplies the 30 s macOS target | computed | Fixed in pr.yml; the factor only loosens that bound |
| 7 | opencode | `GOROROBA_TEST_CALL_SECONDS` is now multiplied by the factor, and a malformed calibration stops collection | computed | Kept by design and documented in ci/AGENTS.md: the factor multiplies whichever target applies; a malformed value fails closed; local runs leave the variable unset |
| 8 | opencode | The core shard holds about 61 percent of test time, not "about half" | measured | Fixed in pr.yml comments and the body: about 60 and 40 percent; the core shard's slowest step was 256 s against the 8-minute limit |
| 9 | codex, opencode | The checkout table's columns come from two runs (45528880900 at e2e4fa954, 45533290585 at 4b9557d, macOS leg cancelled by the next push), not one | measured | Fixed: the runbook and body name each run, and the final head's green run |
| 10 | codex, opencode | No run exercised a cancelled shard leg; the aggregate check rejects every result but `success` by construction | computed | Residual risk, stated in the body; a shard failure did fail the aggregate (run 45531923806, `tests` failed after `tests (core)` failed) |
| 11 | opencode | Hypothesis: a runner whose 4-copy contention departs from the observed 1.78 to 1.96 concurrent-to-single ratio gets a mis-scaled budget | measured on 9a0de64 | Present on the arm runners, which do not slow under load (ubuntu-26.04-arm 1.10 s single, 1.13 s four copies, factor 2.0; macos-26 0.94 s and 0.92 s, factor 1.7), so the factor loosened their bound unearned; the arm jobs no longer run the profile and keep their fixed targets. On x64 the two calibrations track each other |
| 12 | codex | Remaining per-job cost: `pins-venv` 9 to 48 s, the profile 5 to 10 s, `Fetch main` under 1 s (the scripts shard may not need it) | hypothesis and measured | Recorded as follow-up candidates; none changes this pull request |

## Advisor verdict

The Advisor reviewed last, on 9a0de64 with every finding above: items 1 to 9 accepted, item 1 pending the macOS leg
(it passed: run 45537604848); items 10 and 12 accepted as stated; item 11 open until the arm profiles were read, which
made it a present case (fixed as recorded). It also asked that the measurements live in the repository
(`docs/evidence/ci_runtime/runner_speed_2026-11.json`) and that the pull request reference issue 1006 without closing
it, since QPU-49 closes on twenty consecutive runs inside the limit with 25 percent margin.

## Claims as the reviewers left them

Claim 1 (budget floor) holds under the stated environment precondition. Claim 2 (calibration predicts suite time)
survives its falsifiers: equal-calibration EPYC 9V45 runners differ by 11 to 12 percent of summed time, and on the core
shard the 7763-to-9V45 ratios agree (single 2.14, concurrent 2.12, summed test time 2.13). Claim 3 (shard partition) is
proved by node ids: 3,918 and 3,887, overlap 0, union the single-job run plus the six new tests. Claim 4 holds by
construction (item 10). Claim 5 (bytecode) is one measurement, A/A2 agreeing within 0.03 s. Claim 6 (checkout
coverage) holds on the final head; both reviewers found all 191 files that ruff and mypy name present under the lint
and types patterns.
