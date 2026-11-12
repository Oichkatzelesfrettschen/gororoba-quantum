# Brief: gororoba-quantum pull request 819, offline residual-structure passes over retained hardware records

Read first: the workspace AGENTS.md one directory above the primary checkout, then AGENTS.md in this worktree.
Work read-only: change no file; never commit, push, stash, submit to a provider, call a provider API, read a
credential or start a cloud resource; spawn no subagents. You may run git and the repository interpreter that
docs/PYTHON.md names; keep each computation under 5 minutes and under 8 GiB, and write scratch files under /tmp
only. Draw no random numbers.

Material: this worktree on branch hardware-residuals-offline; the change is `git diff origin/main...HEAD` (one
commit). Root: docs/evidence/hardware-residuals (H). H/ibm holds 13 scripts, their JSON results, p-value lists and
REPORT.md, reading the shot-ordered IBM Heron r2 records under results/live/. H/tuna-quandela holds 9 scripts, their
JSON and REPORT.md, reading retained Tuna-17 and Quandela records through gororoba_quantum/qi_records.py and
qd_records.py. H/README.md and one row of docs/README.md map them. No finding is a registered claim.

## Claims under review (justify or falsify each against the source and the retained JSON)

1. H/ibm/REPORT.md item 1: a 60.00 Hz line in seven ibm_kingston jobs, whose bin differs per slot period while the
   frequency in Hz does not. Falsifiers: the slot-period model (sum over the job's PUBs of rep_delay + duration)
   is wrong for those jobs; the line sits at a fixed bin or a fixed list-position period (a design artifact of the
   PUB list); the periodogram null (F law per column) is miscalibrated for binary columns with drift.
2. H/ibm/REPORT.md item 2: a 29.70 Hz line; the report itself states a list-position period of 9.97 shots is not
   excluded within one 44-PUB design. Check that the text claims no more than that.
3. H/ibm/REPORT.md items 3 to 8 and the multiplicity ledger: the counts of tests (627,453), the Bonferroni line
   and the survivors agree with aggregate.json; each "observed" number is in the JSON it cites; items 4 to 7 are
   stated as dependent.
4. Each null law matches its statistic: exact Poisson, Poisson-binomial, exponential or F periodogram law, t over
   replicates, circular shifts. Name any test whose null assumes independence that the data's construction breaks.
5. H/tuna-quandela/REPORT.md: 90 pooled tests, BH and Bonferroni survivors, agree with ledger_all.json; the
   analysis-3 survivors that re-detect the known stray-mode effect are labeled as such.
6. Code: the scripts compute what their docstrings state; CPU-bound loops over independent items run through
   gororoba_quantum/parallel.py (a serial loop over such items is a defect under the repository guide); no script
   reads a credential, an account identifier or the network; no file holds a token, CRN, email address or local
   absolute path.
7. Reproducibility statement of H/README.md (which scripts reproduce byte for byte, the se_fisher difference of
   a3_belenos_mode_efficiency.json across numerical stacks).

## Questions to answer

- Which reported findings would not survive a stricter or more appropriate null, and what is the cheapest
  decisive check for each?
- Defects in code, statistics and text, each with file:line.
- Whether any retained file must leave a public repository (identifier, path, credential).

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a named statistical
result, each marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
