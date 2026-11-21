# Reconciliation: local review of PR 959 (iqm: Emerald idle-schedule written case)

Head read: 1ec3682569e9cfa4284698b21f831bf623a075b0 against origin/main f31df799da9e8b6d19ac000888cff727b1d967cd. Reviewer: the local codex round (gpt-daybreak-blue, read-only, exit 0), chosen by the owner on 2026-11-19; the Advisor last. Every finding below carries its disposition; a fixing commit is named by its full hash after its diff was read.

| # | Finding | Source | Check | Verdict |
|---|---|---|---|---|
| 1 | High: H2 cannot separate a timing gap from a T1 calibration error | codex | r_i = d/(d+g_i) x T1_true/T1_cal; 500 against 1000 pulses predicts the same r for both | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: H2 claims schedule and r heterogeneity only; the separating measurement is a separate case |
| 2 | High: chi-square has 10 degrees of freedom and no uncertainty model | codex | 12 unique qubits, 20 arms; T1 relative uncertainty 3.6 to 21.7 % | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: 11 degrees of freedom, a stated variance model, threshold chi2 24.7 at p < 0.01 |
| 3 | Medium: pre-flight lacks decisions for several outcomes | codex | CASE.md lines 58 to 70 | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: every outcome carries a decision |
| 4 | Medium: 25 standard errors is the contrast, the midpoint is 12.7 | codex | p1 0.8607, contrast 0.1393, se 0.00547 | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0 |
| 5 | Medium: the Garnet job is not the same layouts and trains | codex | retained cases.json (24 circuits, QB1 and QB20, isolated block) | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: the differences are listed |
| 6 | Medium: 4.5 s mock cutoff violates the 2 s headroom rule | codex | scripts/iqm_idle_schedule_probe.py lines 73 and 226; 6 s cap | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: cutoff 4.0 s |
| 7 | Medium: the run-name search claim is false | codex | 0 Emerald run directories | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0 |
| 8 | Medium: credit comparisons rest on an expired snapshot | codex | credit.json expiry 2026-11-01 | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: stated as historical arithmetic |
| 9 | Low: the packed-Pauli link omits the design that holds the Rigetti preference | codex | docs/design/packed-pauli-response-current-balance.md lines 44 and 49 | Fixed in 5eb930fa7d999ca885184198d6b846ac6215b6d0: the design is cited |
| C | Claims that hold: architecture, topology, calibration, cost table, Garnet comparison, expiry | codex | architecture JSON, topology and cost commands | Pass |
| 10 | Hosted Codex thread: the common-r analysis needs a resolved ASAP schedule; H2 is unidentifiable under ALAP, mixed or unresolved schedules | hosted codex | CASE.md pre-flight items 1, 3 and 5: under ALAP the pulsed qubits do not wait, so the contrast carries no T1 information | Fixed in 88dc5f522daa5eda91a346e9d61278f062ea5f28: H2 is gated on H1 and the common-r outcomes apply only after ASAP on all arms |
| 11 | Live account read replaces the expired-snapshot wording | coordinator | read-only credit query of scripts/iqm_jobs.py at 2026-11-19T23:17Z: currentBalance 30.00, expiresAt 2026-12-01 | Fixed in the commit that carries this row: the case cites the live reading and keeps the read at submission |
| A1 | Advisor (parent) | Advisor | read after the fixes | Passes |

## Successor round: delay-measured T1 (head 11c316a6b, fixes in c22070077 and 2d540f8db)

Reviewers chosen by the owner (2026-11-21): codex (gpt-daybreak-blue-latest, high), grok and agy
gemini-4-hydrogen-high on one brief; red-teamers agy gemini-3.8-flash-high and opencode (opencode-go/beam-free, first
model, report accepted). vibe (mistral-medium-3.5) is `not run`: the first attempt stopped because its `grep` tool
no longer exists and a headless run cannot approve bash, and the second ended with "Vibe budget exhausted". Every
reviewer worked read-only from source and records; none ran Python. Each finding below was checked against the source.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, agy, agy Flash, opencode, grok | H2 decides from a nonlinear readout fit, an unchecked delay-fit chi-square and an incomplete qubit set, against the preregistered twelve-qubit, 11-degree test | Fixed in c22070077: a qubit enters H2 only with a linear readout fit, a delay fit of chi-square survival at least `T1_FIT_P_MIN` (0.001) and a rate on every train; any excluded pulsed qubit makes H2 `unidentifiable` and is named; the self-test drops one qubit and requires that reading |
| 2 | codex, grok, agy | Standard errors omit the readout correction's uncertainty and shared covariances; the chi-square and stationarity tests are uncalibrated | Fixed in c22070077 and 2d540f8db by measurement: `study()` runs 400 binomial replicates per planted gap on the case's calibration (`calibration-study.json`); one-SE coverage 0.67 and 0.69, gap and T1 z-score standard deviations 0.99 to 1.04, false common-gap rejections 0.25 and 0.76 percent, no stationarity false alarm. The omitted readout uncertainty costs no coverage at 4000 shots |
| 3 | all | A delay realized as a t + b with a != 1 scales T1 and g and leaves no trace in this job | Boundary: CASE.md states T1 per requested delay second and H2 conditional on a = 1; detecting a needs a clock independent of the delay instruction, which this job lacks |
| 4 | codex | The log transform and the 3-SE truncation may bias T1 | Measured: expected-count bias of the mean gap -0.02 ns (no gap) and -0.04 ns (14 ns); mean T1 z-scores -0.02 and +0.005; the shortest T1 on this calibration is 32.8 us, so the 64 us point stays far above the cut |
| 5 | codex, grok, opencode | "At least 7 billed seconds" rests on one unfinished run | Fixed in 2d540f8db: the projection holds if the predecessor's factor repeats, and the factor is a lower bound only |
| 6 | agy, agy Flash | The 9.00-credit ceiling cancels the job if execution exceeds about 2.7 to 2.9 times the mock estimate | Fixed in c22070077: ceiling 12.00 credits (16 billed seconds, cancel at 15.0 s, about 4.2 times the mock estimate after 1.8 s of compilation); a cancelled job bills nothing |
| 7 | opencode | The 1.46 factor should use the real job's 2.5408 s compiled estimate | Refuted: the factor divides by the predecessor's mock estimate (2.5018 s, its mock run's `raw/runtime_estimates.json`), the same estimator as the successor's 3.12 s; 2.5408 s is the real job's compiled estimate, a different quantity |
| 8 | agy, agy Flash, grok, codex | The -0.52 +- 0.22 ns zero-gap figure is attributed to model alignment and retained nowhere | Fixed in 2d540f8db: it was one random draw (-2.3 SE); expected counts read -0.023 ns, which is the pulsed qubit's own 24 ns over 1000 pulses, so agy Flash's -520 ns alignment offset is refuted; the study's numbers are retained in `calibration-study.json` |
| 9 | codex, grok, agy | Station control 50.0.0 is not in the mock run record | Fixed in 2d540f8db: acceptance rests on the completed job; the version is cited to `docs/notes/iqm/os-4.7.md` and the live listing |
| 10 | grok, agy | The self-test uses calibration set 3a1a9ad0 with a 2 ns tolerance, and no gate checks the case bytes | Fixed in c22070077 and 2d540f8db: the self-test builds from the committed case calibration at expected counts with a 0.1 ns tolerance; gate `core-iqm-idle-schedule-t1-emerald-check` replays the case |
| 11 | agy | `T1_delay / T1_cal` is promised and not computed | Fixed in c22070077: `t1_delay[q].over_calibrated` |
| 12 | agy | `expected_seconds` prices Emerald shots at Garnet's 37.5 us | Fixed in 2d540f8db: CASE.md names it a planning figure; the mock estimate is the better one |
| 13 | codex, grok, agy | `--live` now fetches any profile's computer; `write()` still names Garnet | Fixed in c22070077 (docstring); the claim of unchanged builds is narrowed to the retained, non-live builds and analyses |
| 14 | opencode, agy | `marginal()` breaks the timing-qubit tie of a delay circuit alphabetically | No change: the model is per qubit without coupling, so the extra spectator changes no reading |
| 15 | agy | Replace `t1-16us` by a second `t1-64us` for 37 percent less T1 variance | Declined: the gate on the delay fit's chi-square needs distinct interior durations, and the T1 error does not limit H2 (study, row 2) |
| 16 | agy Flash | CASE.md writes g = d (k T1 - 1) | Fixed in 2d540f8db: g = d (k / k_T1 - 1) with k_T1 = 1 / T1 |

Open hypotheses the reviewers raised, each tested by this job's own data at no further cost: the two layouts read one
gap per qubit (grok, agy); the gap grows with simultaneous drive load (codex); gaps cluster by control line (agy); the
shared readout nuisance carries part of a common gap (codex); Emerald's execution-to-mock ratio is stable across jobs
(agy).
