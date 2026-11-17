# Brief: gororoba-quantum pull request 931, scripts/qi_tuna17_characterization_cases.py (Tuna-17 characterization case)

Read first: the workspace AGENTS.md, then AGENTS.md and scripts/AGENTS.md.
Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no
subagents. Send no request to any network host. You may run git and read files; you may run python3 only on pure
functions of the script (no qxelarator run, no --local), each computation under 2 minutes, in a scratch directory
outside every repository.

Material: worktree the worktree, branch tuna17-characterization-case at 5f4a0e26e; the change is
`git diff origin/main...tuna17-characterization-case`.
Files: scripts/qi_tuna17_characterization_cases.py, tests/scripts/test_qi_tuna17_characterization_cases.py,
results/quantum_inspire/cases/characterization_tuna_17/ and characterization_qx/ (CASE.md, cases.json, prediction.json,
batch files), docs/notes/quantum_inspire/tuna17-characterization-case-draft.md.
Context: scripts/qi_platform.py (pause and batch limits, submission path; sha256-pinned, must not change),
docs/evidence/qi-status-context/retained-context.json (retained per-qubit rows of 2026-10-16/17),
docs/notes/quantum_inspire/experiments.md, the "Hardware services" and "Seeds" sections of AGENTS.md.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The generator submits nothing and reads no account: no code path of the script reaches a provider request.
   Status: by inspection. Falsifier: an import or call that sends one, in any mode.
2. The series respects the provider limits CASE.md states: at most 3 circuits per batch, each job under 131,072
   shots, at most 16,384 measurements per qubit per job against 500,000, total 14 jobs and 147,456 shots.
   Status: tested (test_series_respects_batch_and_measurement_limits). Falsifier: a number in CASE.md, cases.json
   or the batch files that disagrees with circuits()/batches(), or a limit in qi_platform.py or the retained
   backend-type limits the series exceeds.
3. expected_seconds() gives 115.8 s for the Tuna-17 profile under the stated model (2.6 s per job, 0.53 ms per
   shot, plus the circuit's wait per shot). Status: computed. Falsifier: a recomputation that differs, or a
   retained job timing in retained-context.json that the model contradicts by a factor that matters for approval.
4. The circuits measure what CASE.md says: readout-0/1 prepare 0 and 1; t1-N waits N cycles of 20 ns after an X;
   x90-K applies 4K X90 pulses (whole turns) so the noiseless outcome is all 0. Status: by inspection. Falsifier: a
   circuit text whose noiseless outcome or wait differs (cycle count, gate name, qubit range, measurement order).
5. analyze() corrects populations by the readout pair, fits one exponential per qubit and reports verdicts by the
   thresholds of prediction.json. Status: tested on synthetic shots (test_analysis_recovers_a_given_t1_and_readout_pair).
   Falsifier: an estimator error (bit order in bit()/p1(), readout inversion, weights, chi-square degrees of
   freedom, chi_square_probability accuracy, behavior at the population floor or with a zero-variance point).
6. sanity() between batches stops a series whose result contradicts the noiseless prediction beyond what the
   retained error rates explain, and does not stop a healthy one. Status: by inspection. Falsifier: a healthy
   retained-rate result it rejects, or a broken one (all-zero shots, swapped bit order) it accepts.
7. --check reproduces every generated file byte for byte and names a changed file. Status: tested. Falsifier: a
   tracked generated file --check does not cover, or nondeterminism in files().
8. The thresholds (readout tolerance 0.03, chi-square probability 0.01, ladder minimum 0.5 at 256 pulses,
   population floor 0.05) were fixed before any run and make each verdict falsifiable. Status: design claim.
   Falsifier: a threshold no plausible device state can fail, or one the retained rows already fail for most qubits.
9. No random seed is used, so the QRNG seed rule does not apply. Status: by inspection. Falsifier: a seeded call.

## Questions to answer

- Defects in code, tests, CASE.md and prediction.json, each with file:line.
- Does the written case state everything "Hardware services" requires (what it measures, why a simulation cannot
  answer it, backend, shots, expected seconds, expected credits)?
- Conjecture: which further per-qubit quantity do these 14 circuits already determine that analyze() drops?

Report ranked by consequence, every finding tied to a file:line or a command with its output, each marked proved,
computed, measured or hypothesis. Print it as your answer, under 150 lines.
