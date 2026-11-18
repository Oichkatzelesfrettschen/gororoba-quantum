# Reconciliation: local review of PR 944 (Tuna-17 interleaved T1, crosstalk and q12 phase case)

Head read by every reviewer: e26b4a922. Reviewers (owner's selection 2026-11-18): codex (gpt-daybreak-blue, high, read-only, exit 0) and agy (gemini-3.8-flash-high, red-team brief, exit 0); the Advisor last. git status clean after both runs. Codex SCRIPT-1 run by the orchestrator on the compute host (clone of e26b4a922): output below.

| # | Finding | Source | Check | Verdict |
|---|---|---|---|---|
| F1 | QX twin CASE.md states 101 circuits, 65 batches, 194 jobs, 198,656 shots, 612.0 s and a single-qubit arm; its cases.json and prediction.json hold interleaved_t1, crosstalk, q12_phase, 30 batches, 90 jobs, 92,160 shots, 289.8 s | codex 1, agy 4 | SCRIPT-1: "qx {'batches': 30, 'jobs': 90, 'shots': 92160, 'expected_execution_seconds': 289.8}", arms crosstalk, interleaved_t1, q12_phase | Survives |
| F2 | QX prediction.json q12_phase.target_qubit is 12 on a 10-qubit profile | codex 1 | scripts/qi_tuna17_interleaved_cases.py:831 `PHASE["tuna_17"][0]`; SCRIPT-1 "qx phase target/nqubits 12 10" | Survives |
| F3 | chain_profile ignores the barrier, so a post-X wait moved after the barrier passes timing_problems | codex 2 | chain_profile (lines ~208-219) matches only wait and X lines; no barrier branch | Survives |
| F4 | timing_problems skips the crosstalk and phase circuits ("multiplier" not in row) | agy defect 3 | line ~231 `if "multiplier" not in row: continue` | Survives in part: those circuits carry no per-qubit delay invariant, but their chains (class waits, ladder) have none checked |
| F5 | --sanity checks presence of admission.json and status-trace.json, not their fields; a test writes {} and passes | codex 3 | sanity() lines ~1600-1605 check is_file only | Survives |
| F6 | The tuna17-characterization note names a "single-qubit arm" the case no longer holds | codex 4, agy 12 | docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md:585 | Survives |
| F7 | The registered detuning (25-cycle minus zero-wait offset over 0.5 us, zero within 0.05 rad) has no aggregate in analyze_phase | codex 5; agy 5 (15.9 kHz gives 0.05 rad over 500 ns) | analyze_phase returns per-(qubit, wait) rows only | Survives |
| F8 | CASE.md admission wording "before a run directory exists" is too broad for retries after a pause refusal | codex 6 | submit_series around line 1673 | Survives (wording) |
| F9 | Fixed sigma 0.0034: at a true 0.0068 the familywise false-flag rate over 98 contrasts is 0.62 (p 0.5), 0.988 (p 0.05), 0.9997 (p 0) | codex B, agy 2 | SCRIPT-1 output lines "0.5 2.584 0.00977 0.618", "0.05 2.016 0.0438 0.988", "0.0 1.745 0.081 0.9997" | Survives (computed) |
| F10 | Design A: 3.49 is the 102-test quantile (3.486057); the 98-test quantile is 3.475341; 98 x 0.05/102 = 0.0480 | codex A, agy A | SCRIPT-1 | Justified: keep 3.49 (conservative) |
| F11 | Design C: the flag reads the raw half minus all difference; normalized fields are reporting only; readout context is confounded with drive | codex C, agy 3 | read by the orchestrator in the fix diff: z = contrast_z(half, every, ...) on raw readings, normalized values only in half_value and the reporting fields | Justified in code; agy asks the verdict words to name readout |
| F12 | --self-test does not exercise the replicate gate or the 200 threshold (pytest does) | codex 8, agy 8 | tests :615, :632, :650 | Survives as a boundary |
| F13 | Up to SANITY_WRONG_QUBITS = 3 qubits per anchor can be wrong; unusable qubits drop from tail_statistic without a stop | agy 6 | sanity(), lines ~1211-1238 | Refuted as "fails open": a dropped qubit lowers a sum of nonnegative gains, so the confirmatory verdict fails toward the null; survives as a missing record field (count of unusable qubits) |
| F14 | Conjecture: staggered excitation produces an apparent tail through neighbor-state relaxation or assignment | codex, agy | hypothesis | Open lead; cheapest test is descriptive and costs no job: all-drive 20 and 80 us crosstalk readings against the interleaved points at matching per-qubit delays |

## Orchestrator decisions (routine design, decided and reported)
- A: keep 3.49.
- B: the registered flag uses sigma 2 x 0.0034 = 0.0068 (familywise level below 0.05 for any true sigma up to 0.0068 by SCRIPT-1's arithmetic); the reading at 0.0034 is a descriptive field. The q2 pair prediction (retained 0.046 against 0.893) holds at either.
- C: keep the raw difference; verdict words become "drive-and-readout context dependence".
- D: rewrite the QX CASE.md from its generated records; target from PHASE[profile_name][0]; the twin holds the three Tuna-17 arms.
- F14: add the descriptive simultaneous-versus-staggered comparison.

## Fixes (head 1ccb6523f; commits 82988a7d4 and 1ccb6523f, by the implementing worker)
- F3: chain_profile closes at the first barrier; a wait or X after it is a timing problem (known-bad test).
- F4: the crosstalk and phase circuits get the invariant of their kind (known-bad test per kind).
- F5: --sanity validates the admission and trace fields; the earlier test that wrote {} now fails sanity.
- F1, F2: q12_phase.target_qubit from PHASE[profile_name][0] (QX reads q9); the QX CASE.md is restated from its own cases.json and prediction.json (30 batches, 90 jobs, 92,160 shots, 289.8 s, three arms).
- F7: analyze_phase emits the wrapped offset difference, its standard error, the detuning per us and the zero-within-0.05-rad verdict.
- B: FLAG_JOB_LEVEL_SIGMA 0.0068, reading at 0.0034 descriptive; family false-flag rate 0.046 at a true 0.0068. C: verdict words "drive-and-readout context dependence". F6, F8, F12, F13 (unusable-qubit count recorded), F14 (descriptive simultaneous-versus-staggered comparison).
- Worker's mutation check: 31 mutants, 30 caught; the miss is a break in operations() whose effect the post-barrier check reports on the same lines. Validation on the compute host: --self-test, 60 tests, ruff, mypy, ci/pr_checks.sh pass; --check skips (draw pending). Files touched: the PR's own seven; no retained generator. One subject is 73 characters and stays.

## Orchestrator checks after the fixes
- F13: tail_contribution returns max(0.0, single minus tail AICc), so a dropped qubit only lowers the sum; the refutation of "fails open" stands (read at scripts/qi_tuna17_interleaved_cases.py, tail_contribution).
- Decision B grounded (compute host, retained_inputs' own anchors, 3 prepared-0 and 3 prepared-1 jobs per qubit): per-qubit job-level sigma 0 on 7 of 17 qubits, pooled 0.00343, largest 0.01021 on q6, the only qubit above 0.0068; q1 0, q7 0.00466, q10 0.00316, so agy's "qubits 1, 7, 10 above 1.8 times pooled" is refuted. Three jobs per qubit leave each per-qubit estimate uncertain; the doubled sigma is a choice, not a measurement, and goes to the owner with the case approval (keep 0.0068, or q6 at its own 0.0102, or 0.0102 for all).

## Advisor verdicts (read the round's findings, the orchestrator's checks and excerpts of 1ccb6523f)

| # | Verdict |
|---|---|
| F1, F2, F3, F5, F6 | Confirmed. |
| F4 | The skip is confirmed; the invariant chosen for the crosstalk and phase circuits rests on the worker's report. |
| F7 | Consistent: the detuning verdict uses phase_verdict's abs(x) + 2 se form (read by the orchestrator). |
| F8, F12 | Stand. |
| F9 | Computed; the rates assume independent contrasts, while the contrasts of one condition batch share one all-17 job: labeled as independence figures (c409ea20c). |
| F10 / A | Justified: 3.49 exceeds 3.486057. |
| F11 / C | First draft unsourced; sourced afterwards by the orchestrator's read (row above). |
| F13 | Refuted only for false confirmation: dropped qubits push the statistic toward the registered falsifier, and the power of 0.996 was simulated with 17 qubits; the owner set a minimum (below). |
| F14 | Open lead. The first fix compared raw points at the nearest delay, which differ in delay and so measure decay; c409ea20c evaluates the interleaved fit at the crosstalk wait with its prediction error. |
| B | Owner decision (below). |
| D | Fixed; the orchestrator compared four numbers of the QX CASE.md with its JSON (30 batches, 90 jobs, 92,160 shots, 289.8 s, phase on q9). |

Orchestrator's checks on 1ccb6523f (compute host): `--write results/quantum_inspire/cases` regenerates both directories byte for byte; `--check` skips while the QRNG draw is pending; three mutations rerun by the orchestrator each fail the test file (barrier ignored by chain_profile and post_barrier_operations: 2 failed; admission record validation returning no problem: 3 failed; QX phase target set to the Tuna-17 qubit: 1 failed). The worker's count of 31 mutants (30 caught) is the worker's.

## Owner rulings (2026-11-18) and the fix commit c409ea20c
- B, flag sigma: "Measured when both run": each qubit's flag sigma is max(sqrt(job_level_variance) of its 18 interleaved anchor pairs, 0.0034) when the interleaved arm is analyzed with the crosstalk arm (the floor is the orchestrator's decision: a zero estimate would make the flag anti-conservative), and 0.0102 (the largest retained per-qubit value) for every qubit otherwise; the q1/q2 pair takes the larger of its two qubits' sigmas.
- F13: "15 of 17": a tail statistic below 200 with fewer than 15 usable qubits reads inconclusive (all qubits of a smaller chip, so all 10 of the QX twin, an orchestrator decision: the emulator is noiseless).
- The worker's mutation check on c409ea20c: sigma floor removed, inconclusive branch removed, and the staggered comparison returned to the raw nearest point each fail a test; 62 tests, --self-test, ruff, mypy, lint and types pass on the compute host.
