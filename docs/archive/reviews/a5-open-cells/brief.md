# Brief: A5 E8-bar Rees fiber open cells, full-run replay, modulo colon (gororoba-quantum branch a5-rees-open-cells, commit 13d5ad48c)

Read first: the workspace AGENTS.md, then the repository AGENTS.md. Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git, grep, sha256sum and python3 -B on the two Python files below (each under 2 minutes; no Singular run, no test suite). Print your report as your answer, under 150 lines.

Material: the working directory is the worktree at commit 13d5ad48c. Read the change with `git diff origin/main...HEAD --stat` and the files under `docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v3-open-cells/` (README.md, render_cells.py, check_open_cells.py, the .sing scripts, .log and .time files, bases.sha256, sha256.txt, replay-v2-full/, modulo-colon/) and `docs/evidence/a5-exceptional-fibers/ledger.tsv` rows A5-576, A5-578, A5-587 to A5-590. The retained earlier runs sit in sibling directories of `docs/evidence/a5-exceptional-fibers/working/runs/`.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Each of the six open-cell logs (*.v3-u-full.log) certifies, at its prime and root, 148 minimal generators of degree 2, dimension 5, multiplicity 11, and equality of the fiber ideal with the quadric ideal. Status: computed (Singular 4.4.1, modular). Support: the logs and check_open_cells.py. Falsifier: a log line that contradicts these values, a script whose certificate lines can print without the computation they name, or a script that differs from the retained v2 script beyond prime, root, sign and file names.
2. The two replay logs under replay-v2-full/ reproduce the retained full-run logs beyond timer lines, and their four basis digests equal the retained digests. Status: computed. Falsifier: a non-timer line that differs, or a digest compared against itself.
3. Replacing `quotient(HS,ideal(u))` by `modulo(ideal(u),HS)` (the generators of the module of g with g*u in HS, read back as an ideal) computes the same colon ideal HS:u. Status: computed for four cells by equal sha256 of the saved basis files across two CPU architectures; the general identity is asserted from the definition of modulo. Falsifier: a case where the entries of modulo(ideal(u),HS) generate an ideal other than HS:u, a digest comparison that does not involve the colon's output, or a v4m script that differs from its v3 script by more than the colon call and file names.
4. Ledger row A5-590: the relation lines of N- at root -r equal those of N+ at root r for four sign pairs. Status: computed observation; the explanation by a conjugation is marked hypothesis. Falsifier: a pair of logs whose relation lines differ, or a row text that states more than the logs show.
5. check_open_cells.py fails closed: missing, truncated or altered logs give a failing verdict, and its --self-test rejects eight known-bad variants. Status: computed. Falsifier: an input alteration that changes a certified value or drops a log and still reads PASS.
6. Rows A5-587 and A5-588 supersede A5-576 and A5-578 with scope no wider than the evidence: modular certificates at primes 32009 and 32029 only. Falsifier: a row, README or pull-request sentence that claims characteristic zero, all primes, or a proof.

## Questions to answer

- Does equality at four (prime, root) points per sign support the statement the ledger makes, and where does the text overreach?
- Which unstated structure do the logs suggest (for example the dependence on the product of sign and root)? Give each conjecture with its falsifier and cheapest test.
- Defects in code, claims and records, with file:line.

Report ranked by consequence, every finding tied to a file:line or a command with its output, each marked proved, computed, measured or hypothesis.

The red-team reviewer received this brief under one added paragraph: its task is to break each claim, by an input, a reading of a script or a counterexample, and to report a claim it cannot break as not broken with what it tried.
