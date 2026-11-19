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
| A1 | Advisor (parent) | Advisor | read after the fixes | Passes |
