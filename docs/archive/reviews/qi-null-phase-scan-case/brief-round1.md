# Brief: pull request 914 of gororoba-quantum, the Tuna-17 phase scan case of the null block (q12 Rz scan, q4 angle scan)

Read first: the workspace AGENTS.md, then AGENTS.md and scripts/AGENTS.md of the repository. Work read-only:
change no file (your report is your printed answer); never commit, push, stash, submit to a provider or start a
cloud resource; spawn no subagents. You may run git and the pinned interpreter that docs/PYTHON.md names (`"$PYTHON" -B -W error ...` from the repository root). Keep each computation under 10 minutes. No random draw is
needed; if you sample, say so and use fixed deterministic offsets.

Material: branch
`qi-null-phase-scan-case`, one commit on top of `origin/qi-null-scan-line-phase-interpretation` (pull request 912).
Read the change with `git diff origin/qi-null-scan-line-phase-interpretation...HEAD --stat` and the files:
`scripts/qi_pathion_null_phase_scan_cases.py`, `tests/scripts/test_qi_pathion_null_phase_scan.py`,
`results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/CASE.md` and `prediction.json`, one `batch-NN`
directory of each series. Predecessor module: `scripts/qi_pathion_null_rotation_scan_cases.py`. The draft this case
builds: `docs/notes/quantum_inspire/tuna17-null-phase-scan-case-draft.md`. Retained predecessor analysis:
`results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json`. The case is a request for hardware time
that the owner has not approved; nothing is submitted.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The emitted circuits are the predecessor's center arm with one rewrite: a z12 arm adds exactly five
   `Rz(phi) q[12]` lines, each directly before a q12 pulse, and a q4 arm changes exactly q4's eight pulse angles.
   Status: computed. Support: `arm_lines`, tests `test_an_arm_rewrites_one_qubit`,
   `test_the_center_arm_is_the_predecessors_center_arm`. Falsifier: a batch file whose diff against
   `pathion_null_rotation_scan_tuna_17/batch-01/b0-rx.cq` shows another change.
2. `forward_laws` is a correct state-vector model of the three worlds, with the operator order of the emitted text
   (the injected Rz and the world's z rotation act before the pulse). Status: computed. Support: `--self-test`
   (cancellation to 1e-12; equality with the predecessor's laws). Falsifier: an independent simulation of one arm's
   .cq text that differs from `forward_law`, or a sign convention under which Rz(phi) and the world's theta do not
   add.
3. At expected values each truth of `TRUTHS` reads its own label, the other error world lies 56.4 to 181.7 above,
   and a constant 0.014 beside exact gates reads `none_adequate`. Status: computed. Support: `--self-test`,
   `prediction.json`. Falsifier: a rerun that reads otherwise; or a plausible truth (a q12 phase of other size, a
   phase plus a static offset, contraction share 1, a phase after the pulse instead of before) that reads a wrong
   deciding label (`q12_phase` for a coupler truth or the reverse, or a deciding label for exact gates).
4. The adequacy bound (0.001 point of chi-square with 6 or 5 degrees of freedom per z12 batch less one) and the
   separation of 25 are applied as `preregistered()` and CASE.md state them, and the statement of the rules in
   `preregistered()`, in CASE.md and in `decide()` agree. Status: computed. Falsifier: a rule stated one way and
   coded another.
5. Treating a circuit's contrast and d2 split as independent in the chi-square is a stated limit and does not by
   itself produce a wrong deciding label. Status: hypothesis. Falsifier: a computation of their covariance on one
   expected law that changes a label at expected values or makes the bound badly anticonservative.
6. The admission guards all five region qubits and `evaluate` refuses a z12 kind whose brackets jump. Status:
   computed. Support: `test_evaluate_refuses_a_z12_kind_whose_d2_readout_jumps`.
7. The series respects the provider's queue rule: every batch holds at most 3 circuits and the submit route is
   `scripts/qi_pathion_one_cz_null_submit.sh`, one batch queued at a time. Status: computed. Support:
   `test_no_batch_exceeds_the_hardware_batch_size`, CASE.md "Commands".
8. CASE.md's numbers (42 jobs, 17 batches, 3,735,552 shots, seconds, the prediction table, the d2 splits) equal
   `prediction.json` and the build. Status: computed. Falsifier: any number that differs.
9. The premise that Tuna-17 applies Rz as a zero-duration frame update is marked as a hypothesis everywhere it is
   used. Status: hypothesis. Falsifier: a sentence that states it as fact, or provider documentation in
   `docs/notes/quantum_inspire/` that contradicts it.

## Questions to answer

- Does the design answer its question? Name any mechanism that would read `q12_phase` or `coupler_phase` while
  being neither (the most damaging failure, since those two labels change ledger row A5-186), with a computation.
- Is the choice of arms (z12 at +-10 and +-20 degrees, q4 at -5, +5, +10, +15) adequate given a fitted q12 phase
  near -0.15 to -0.18 rad (9 to 10 degrees)? Would other angles separate the worlds better at the same shots?
- Defects: code, claims and records, with file:line. Include comment and docstring statements that the code does
  not support, and anything in CASE.md a reader arriving cold could not follow.
- Conjecture where nothing is posited: structural statements about the three worlds' response curves that the code
  suggests and no record states, each with its falsifier and cheapest test.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 250 lines.
