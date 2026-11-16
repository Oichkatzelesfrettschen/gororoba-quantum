# Brief: decision rules R2-R6 and the value-12 prediction record of the Tuna-17 null phase scan case (gororoba-quantum pull request 914, branch qi-null-phase-scan-case, local commit e5ba2a787 on top of pushed head fc9c84b12)

Read first: the workspace AGENTS.md, then AGENTS.md of the repository. Work read-only: change no file except
your report (named at the end); never commit, push, stash, submit to a provider (the QX emulator included) or start a
cloud resource; spawn no subagents. Run git, rg, sed, head and other
file readers only; run no Python, no tests, no builds and no simulation. When a claim needs a computation, write the
exact command, its expected output and its cost into your report; the session runs it on a compute host.

Material: the branch at commit e5ba2a787 (`git show e5ba2a787`, `git diff fc9c84b12 e5ba2a787`). An earlier
review read only fc9c84b12 (rule R1; "Round 2" of reconciliation.md); do not repeat findings those records already resolve unless
the new commit reopens them. Key files: scripts/qi_pathion_null_phase_scan_cases.py (decide, screen, absorb,
fit_flips, flipped, freedom, adequacy_limit, seen_contrasts, center_retention, matched, oc_worker,
operating_characteristics, upper_bound, wrong_labels, TRUTHS, preregistered, case_tables, render_case, check,
self_test), tests/scripts/test_qi_pathion_null_phase_scan.py,
results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/{CASE.md,prediction.json,batch-*/cases.json},
docs/evidence/qi-null-phase-scan-decision-probes/ (README.md, readout-flip/README.md, its scripts and logs), the
QRNG draw docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json. 

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. q8 world. A fourth error world, a rotation about z on q8 after each CZ of coupler 8-12, lets q8 phases of -0.25,
   -0.17 and +0.10 rad fit their own world instead of reading `coupler_phase`. Status: computed (prediction.json
   truths). Falsifier: a q8 truth whose expected-value label is another error world.
2. Visibility rule. A noise model whose center visibility misses the batch's by more than 0.0083 (3/sqrt(131072))
   takes an infinite chi-square for that batch; CZ damping is computed directly at 49 multiples 0 to 3. Status:
   computed. Falsifier: an admissible model the rule excludes at expected values, or an interpolation left in the
   damping grid.
3. Scaled separation. A deciding label needs the least error world ahead of every other by 40 x max(1, chi2_lead /
   freedom(lead)); the history is value 8 (unscaled 25: nulls read q12_phase in 29 and 48 of 500), value 9 (calibrated
   30), value 10 (30: one false label in 500), value 11 (40, flip fixed: none). Status: computed and recorded.
   Falsifier: a record or log that contradicts this chronology, or code that applies another scale.
4. Readout-flip nuisance (R6). Each world is fitted at every selector-flip probability f in 0..0.06 step 0.0025
   (flip when d0 reads 0) composed as `matrix_of(batch) @ selector_flip(d0, 0, f)`, one f per series and world, ties
   keeping the smaller f; the adequacy limits and the separation scale lose one degree of freedom (70.70 exact, 59.70
   error world, eight whole batches); kind bounds and the 6.63 margin are unchanged. Status: computed. Falsifier: a
   composition order that differs from the truths' simulation (truth_row), a tie rule that differs, or a degree-of-
   freedom count that differs from the text.
5. Simulation equivalence. oc_worker fits every series at one flip before the next and draws each scenario's whole
   series from rng([seed, position]) before slicing a chunk, so labels do not depend on chunking or worker count;
   with flips=(0.0,) it reproduces the value-11 counts of every value-11 scenario
   (readout-flip/r6_regression_value11.log), and decide() on the full grid reproduces nuisance.py's labels on 80
   series (r6_regression_nuisance.log). Status: computed. Falsifier: a code path where chunking, cache clearing or
   the `fitted` argument changes a label.
6. The value-12 record. No scenario reads a deciding label that misreads it: 0 in 40,000 series of exact gates (8
   scenarios of 5,000, each one-sided 95% Clopper-Pearson bound below 0.06%) and 0 in 10,000 series of phases and
   mixed scenarios; single q12 and coupler mechanisms read their own label in 491 to 499 of 500. Status: computed.
   Falsifier: a count in prediction.json that contradicts CASE.md, a wrong_labels definition that omits a misreading,
   or a bound formula error.
7. CASE.md. Every number in the prose and the generated tables agrees with prediction.json and the generator; the
   rules, labels table and limits describe R6 (including the drifting-flip limit and the fitted flip's meaning under
   `exact_parabola`). Status: claim. Falsifier: any mismatch or a rule the text states and the code does not apply.
8. Evidence. readout-flip/README.md states the exploratory findings as the logs beside it record them; the gate of
   a least-contrast parabola (finding 6) is refuted only as an estimator. Status: claim. Falsifier: a count in the
   README that a log contradicts.

## Questions to answer

- Is the case ready for the owner's approval to run the QX twin and then Tuna-17? If not, the smallest set of changes.
- Identifiability: the exact world with a fitted flip can absorb part of a phase (under q12 -0.18 rad its best flip
  is 0.03; q12 -0.15 rad with CZ damping x3 reads `exact_parabola` in 6 of 500). `exact_parabola` states that the
  phase reading is falsified. Estimate the risk that a true small phase reads `exact_parabola`, and whether a rule
  change (for example a bound on the exact world's flip, or requiring the flip to agree with the bracket readout)
  is warranted; give the computation that would decide it.
- Does the flip interact with the visibility rule (the retention is solved through the flipped matrix) in a way that
  lets a flip stand in for contraction or damping?
- Conjecture where nothing is posited, each with its falsifier and cheapest test.
- Defects: code, tests, claims and records, with file:line.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a record path, each
marked proved, computed, measured or hypothesis. Write it to the report file the session names, under 200 lines.
