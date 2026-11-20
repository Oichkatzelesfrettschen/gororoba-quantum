# Review of the sim:belenos timing requests P1 and P2 (PR 965)

Subject: `scripts/bdsc_diagnostic_timing_case.py`, its tree `results/quandela/cases/bdsc_diagnostic_timing_sim_belenos/`, its
tests and the implementation section of
[`bdsc_diagnostic_billing_rule_sim_belenos/CASE.md`](../../../../results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos/CASE.md).
Every reviewer read head 9b22694a6 on one brief per role, read-only, with computation on the build host forbidden; hosted CI
had passed all six checks there. This record is the case's review packet (`qd_platform.py review` writes Ascella packets
only).

| Role | Reviewer | Outcome |
|---|---|---|
| reviewer | grok (grok-4.7, headless) | report |
| reviewer | codex gpt-daybreak-blue-latest, high, read-only | the first attempt ended without a report; the retry reported |
| reviewer | agy gemini-4-hydrogen-high | report |
| red team | agy gemini-3.8-flash-high | report |
| red team | agy gemini-4-neon-high | report |
| red team | opencode, OpenCode Go account, glm-5.3 | report |
| last | the Advisor | read every finding with its verdict; its items are rows below |
| red team | vibe mistral-medium-3.5 | `not run`: the CLI could not authenticate |

The briefs and raw reports stay in the ignored `docs/local/pr965-review/` of the primary checkout, since they carry local
paths.

## Findings and resolutions

Fixes landed in 432de1c4c, 737f778dd and the commit after it. Verdicts are checked against the source at those commits.

| Finding | Raised by | Verdict | Resolution |
|---|---|---|---|
| The 1800 s and 6.48-credit caps refuse `next` and `analyze` after six completed jobs (six 300 s jobs sum to 1800 s), so the reading is lost after the spend | grok, agy Hydrogen, opencode, agy Neon | confirmed | Fixed: the caps gate a further submission only (`next_request`); `analyze` reads six admitted runs whatever the caps hold |
| The caps check spent credits, not the next job's authorization | agy Neon | confirmed | Fixed: `next` requires spent + 1.08 <= 6.48 |
| A completed job at the 300 s limit does not stop the case (CASE.md "any job reaching the limit") | agy Hydrogen, agy Neon, codex | confirmed | Fixed: `admitted` requires 0 < duration < 300 |
| `next` trusts the run list on its command line; a dropped, canceled or rerun slot escapes the stop rules | codex, opencode, agy Flash, agy Neon | confirmed | Fixed: `bound_runs` finds every submitted P run under results/quandela in submission order; an interrupted checkpoint stops the case |
| The runbook submits through `qd_platform.py submit` with no timing gate; `successor_sources` switches the token rule from idle to queue slot, so a job can queue behind another | codex, agy Neon, opencode, agy Hydrogen | confirmed | Fixed: the manifests name `submit_wrapper`; `SubmissionGate` runs under the submit lock and refuses another slot, a running or queued job, mitigations and every stop rule; `max_credits` 1.08 enters the manifest |
| The runbook continues after `next` refuses; `DONE` is unset on the first slot; `complete` creates a stray directory | grok, agy Hydrogen, agy Flash, agy Neon, codex | confirmed | Fixed: `set -eu` and a loop that ends on `complete` or a refusal |
| The recorder's gap is the read latency plus 10 s, and `patient` retries add silent gaps | all six | confirmed | Fixed: fixed 10 s start-to-start cadence, transient errors logged as lines; CASE.md says a read slower than the cadence delays the next |
| Timestamps compared as strings ("Z" against "+00:00", equal seconds refused) | agy Hydrogen, agy Flash, agy Neon | confirmed | Fixed: parsed instants, submission at or after the previous collection |
| A ratio equal to 5 % reads above it in binary64 (p1 = 150, 150, 151; p2 = 143 x 3) | agy Neon | confirmed | Fixed: `decide` uses exact fractions; boundary rows added to the test |
| A zero duration divides by zero | agy Flash, agy Neon | confirmed | Fixed: refused |
| `next` reads neither the body's mitigations nor the served platform | agy Neon, agy Flash, codex | confirmed | Fixed: both checked per run and in the gate |
| `build` misses runs outside results/quandela/runs and is blocked by a staged copy | agy Neon | confirmed | Fixed: any directory under results/quandela with a receipt or checkpoint binds the tree; a staged copy binds nothing |
| `record` skips the receipt digest and passes the full timeout to collect | agy Neon | confirmed | Fixed |
| CASE.md: "no command below sends a job"; plan placed after approval; "well below" undefined; "j1's first two groups"; rehearsal paragraph says "controlled repeat" | grok, agy Hydrogen, agy Neon, codex | confirmed | Fixed in CASE.md and the rehearsal record |
| `case.json` omits the plan and BSCount stop conditions | codex | confirmed | Fixed |
| `successor_sources` omits `docs/evidence/bdsc/inputs/receipt.json` and `docs/evidence/quandela/catalogue.json`, which `payload_version_basis` reads when the live record lacks `specs.commands` | agy Flash, agy Neon, opencode | Boundary | The posted body is retained in `job-body.json` and bound by `body_sha256` in the receipt, so the request sent is recorded whatever those inputs held; binding the catalogue would refuse every plan after a routine snapshot |
| A change to a bound source after the first job leaves the case unable to continue or rebuild | agy Flash, opencode, agy Neon | Boundary | CASE.md "Bound sources": the six jobs run from one commit in one session; a mid-case change stops the case and a successor tree needs its own approval |
| Usage-delta billing can misattribute a concurrent job's charge | agy Neon, opencode | Boundary | Pre-existing in `qd_platform.charged`; the idle-token gate removes the concurrent case for this run |
| A canceled job's bill is not in the credit sum | agy Flash, codex | Boundary | A canceled job stops the case before any later slot, so no further spend follows; its bill is read from its usage report when the record is written |
| Reused `family`, `acquisition_admission` and `diagnostic_case_sha256` give P runs diagnostic identity | agy Neon | Boundary | Required for `draw_claims`; `admit_run` refuses a P run by platform and by job membership (`bdsc_diagnostic.py` 850, 878) |
| Reusing the retained seeds breaks the seed rule because the question is new | agy Flash, agy Neon (hypothesis) | Refuted | gororoba-quantum `AGENTS.md` "Seeds": a seed that reproduces a retained record or known compiled mesh is an identifier; the question is the time of these exact requests, so the seeds are part of the request under test |
| `check_budgets` rejects the P manifests | agy Flash | Refuted | `iteration_form` calls it only when settings name budgets (`qd_records.py` 212-217); the P settings, like the retained ones, name none |
| `analyze` applies the rules despite a deviation | agy Flash | Refuted | CASE.md records a deviation as a finding before the rules and does not suspend them; `analyze` lists deviations beside the reading |
| `collect`'s final status read is unlogged | agy Flash | Refuted | `record` logs the terminal read before calling `collect` |
| A gate or plan refusal raises `PlatformError`, which `main` does not catch, so a refusal prints a traceback | agy Hydrogen | confirmed | Fixed: `main` prints the message and exits 1; a test drives it |
| The stock plan output omits the body, so the approval record would not show the mitigation policy | codex | confirmed | Fixed: `bdsc_diagnostic_timing_case.py plan` prints each plan summary with the body's mitigation list |
| No test shows the diagnostic analyzer refusing a P run | agy Hydrogen, agy Neon | Boundary | The refusal rests on two source lines, the served platform and job membership (`bdsc_diagnostic.py` 850, 878); a test needs a synthetic run checked against a frozen rebuild, which the acquisition tests construct through the solver |
| The wrapper takes the run path as given, where the stock CLI applies `case_path` containment | Advisor | confirmed | Fixed: `submit` and `record` resolve the run through `qd_platform.case_path` |
| The claim that P derives from the manifests the retained jobs were sent with rests on a one-off comparison | Advisor | confirmed | Fixed: a test compares `source_job.cases_sha256` with the retained receipts' `cases_sha256` |
| A boundary test row labeled 10 % has spread 14/147 | Advisor | confirmed | Fixed: the row is 133, 140, 147, spread exactly 1/10 |

## Open before approval

- `qd_platform.py plan` on `p1` and `p2` (read-only, the first block of the CASE.md runbook) has not run; its output
  enters the approval request.
- vibe stays `not run` until it authenticates again.
