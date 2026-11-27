# Brief: pull request 1026 of gororoba-quantum, induced slice map of same-sign X and the comparison of its module maps

Read first: the workspace AGENTS.md, then the repository AGENTS.md. Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. This host takes no computation: run git and file reads only, no Singular, no Python, no test suite. Every finding cites file:line or a git command with its output.

Material: the session worktree of the branch (written WORKTREE below) at head c96ea49f1 of branch a5-x-induced-slice-map (two commits over origin/main; read them with `git -C WORKTREE diff origin/main...HEAD` and `git -C WORKTREE show HEAD~1`).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. main holds two ledger rows with id A5-642 and commit HEAD~1 moves the slice-comparison row and every reference to it to A5-643 while the covariance row keeps A5-642. Status: computed. Support: docs/evidence/a5-exceptional-fibers/ledger.tsv; `git grep -n A5-642`, `git grep -n A5-643`. Falsifier: a reference that still names the wrong row under either id.
2. docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/x_induced_slice_map.py performs the construction of ../e8-induced-slice-map/induced_slice_map.py with the X source in every place that names the source, and nothing E8-specific leaks in through the imported stages (HEADER_TAIL, FRAME_LINES, HIGH_TEST, POSITIVE, header_frame, _read, _reduce). Status: computed. Falsifier: an imported stage or constant that assumes 21 generators, 148 relations, the E8-bar equations or the E8bar incidence.
3. The retained logs support the README table and ledger row A5-644: map-*.log, high-*.log, check-*.log and control-*.log in that directory. Status: computed. Falsifier: a number in the README or in row A5-644 that a log does not show.
4. The controls can fail for the right reason. In check_script: identity, one entry raised (img2[1]+y(1)), header generators 1 and 2 swapped; in run_x_induced.sh: refute() at the other root of -1. Status: computed. Falsifier: a control that would report failure whatever the map is, or that would pass a wrong map.
5. docs/evidence/a5-kernel-attachments/slice_module_map_comparison.py with --family x runs the test of the E8-bar family with the sizes of X, and the default family behaves as before (its retained record is unchanged in the diff). Status: computed. Falsifier: a place in TAIL, script(), expected() or problems() where an E8 size or the E8 scalar still applies to an X cell, or where the parametrization changed the E8 text in meaning.
6. Row A5-645 and docs/evidence/a5-kernel-attachments/README.md state the scalar 1/2 (X- -> N-) and -1/2 (X+ -> N+) and docs/evidence/a5-kernel-attachments/x-slice-module-map-comparison-result.json shows it: residues 16005, 16015, 16029 and 16004, 16014, 16028 modulo 32009, 32029, 32057 (the record prints symmetric residues). Status: computed. Falsifier: a residue in the record that is not +-1/2 modulo its prime, or a cell whose controls report a scalar.
7. The statement that the comparison is forced by A5-644 and the one-dimensional solution spaces, and so is no independent evidence, is correctly scoped in the README, the docstring and row A5-645. Status: argument. Falsifier: a sentence that claims more.
8. tests/test_a5_slice_module_map_comparison.py and tests/test_a5_x_induced_slice_map.py reject the changed records they name, and each mutation can fail only for the reason its name states. Status: computed (51 passed on the compute host). Falsifier: a mutation that problems() rejects for another reason than the named one, or a test that passes on a wrong record.
9. ci/gates.json entry core-a5-x-slice-module-map-comparison replays the X record. Status: computed. Falsifier: a command that replays another record or skips silently.

## Questions to answer

- Defects in code, claims and records, with file:line.
- Any repository rule of the two AGENTS.md files the change breaks (parallel.py rule, pinned bytes, text rules, commit rules).
- A structural statement the evidence suggests and no record states, with its falsifier and cheapest test.

Report ranked by consequence, under 150 lines, printed as your answer.
