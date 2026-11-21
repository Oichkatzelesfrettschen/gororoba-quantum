# Brief: gororoba-quantum PR 966, IQM Garnet Grover search with a seven-CZ line-native CCZ (head 5417bc0df)

Read first: the workspace AGENTS.md, then AGENTS.md (sections "Hardware services", "Reviews and merges", QRNG seeds, records). Work read-only: change no file except none (print your report as your answer); never commit, push, stash, submit to any provider (no iqm_jobs.py submit, not even --dry against the network), or start a cloud resource; spawn no subagents. You may run git, and python3 for small local checks (each under 10 minutes, scratch under a scratch directory only). Do not run the full test suite or "check" (it takes 16 workers); the self-test (`python3 -B scripts/iqm_grover_line.py --self-test`, 1.5 s) is allowed if qiskit is importable.

Material: worktree the pull-request worktree, branch iqm-garnet-grover-line-ccz; diff with `git diff origin/main...HEAD`. Key files: scripts/iqm_grover_line.py, tests/test_iqm_grover_line.py, docs/design/iqm-garnet-grover-line-ccz.md, results/iqm/cases/grover-line-ccz/{cases.json,prediction.json,circuits/,calibration copy}, scripts/iqm_jobs.py (submission governance, unchanged here), ci/gates.json (core-772, core-773), ci/runner_image_records.json, docs/evidence/qrng_seeds/allocations.json.

This case is about to spend about 1 to 2.5 IQM credits on Garnet (18 circuits x 4000 shots, active reset, zeros heralding, pinned calibration set 03975719-b1c2-4805-a212-877a026e1724). A defect that wastes the run or invalidates its decisions is the most important finding.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. CCZ on a three-qubit line needs 8 CNOTs when every wire returns to its input and 7 when the middle wire may exchange with one end, within CNOT-plus-phase circuits. Status: computed (BFS in line_networks()). Falsifier: a shorter network carrying all seven parities, or a BFS state-space bug.
2. Every compiled circuit equals its logical Grover circuit times the tracked permutation up to a final diagonal (self-test residual 4e-11). Status: computed. Falsifier: a marked string, k, or network where the native unitary disagrees, or where the measurement locus maps logical bits to the wrong physical qubits (bit-order reversal).
3. Z-frame tracking into prx phases is correct for IQM's prx(theta, phi) convention and CZ; dropping the final frame before measurement is harmless. Falsifier: a sign/convention mismatch with IQM's native gate definitions (check scripts/iqm_jobs.py or the IQM circuit JSON schema used).
4. The circuit JSON files match the format iqm_jobs.py submits and the case schema iqm-circuit-case-v1 (qubit names, gate names, measurement keys, locus order), and cases.json digests match the files. Falsifier: a field the server would reject or misread.
5. Path choice QB3-QB4-QB1 is the best of 136 oriented paths by mean predicted marked probability, and the prediction model (iqm_sim depolarizing + ALAP T1/T2 + analytic readout) is implemented correctly. Falsifier: a calibration field read from the wrong qubit/coupler, units error (us vs s), or path orientation mixup.
6. Credits: 72000 shots priced at 37.5 us/shot + 1.6 s fixed gives 2.70 s and ceiling 2.50 credits at 0.50/s. Falsifier: arithmetic or the ceiling rule in iqm_jobs.py disagreeing.
7. Preregistered decisions (docs/design, "Preregistered decisions"): z > 3 with binomial standard errors on heralded counts, copies pooled; P(resolve) 0.98 / 0.90 under a 0.75 shortfall. Falsifier: a wrong variance formula, unequal copy pooling, or a decision the job cannot answer.
8. Governance: seed provenance (TRANSPILER_SEED 53987 from QRNG allocation), gates registration, runner-image ledger exemptions, and no host names or local paths in committed text.

## Questions to answer

- Any defect that would make the hardware run wasted or its decisions invalid (highest priority).
- Code, claims and records defects with file:line.
- Conjecture: a six-CZ line construction with general single-qubit gates between CZs, or a cheaper Grover diffuser on a line; each with falsifier and cheapest test.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
