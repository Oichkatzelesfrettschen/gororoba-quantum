# Brief: gororoba-quantum pull request 822, degree-2 relations over Q(i) and the modular standard-basis engine

Read first: the workspace AGENTS.md one directory above the primary checkout, then AGENTS.md in this worktree.
Work read-only: change no file; never commit, push, stash, submit to a provider, call a provider API, read a
credential or start a cloud resource; spawn no subagents. You may run git, Singular and the repository interpreter
that docs/PYTHON.md names; keep each computation under 5 minutes and under 8 GiB, and write scratch files under
/tmp only. Draw no random numbers.

Material: this worktree on branch a5-char0-quadrics-iso-w8; the change is `git diff origin/main...HEAD`. Root:
docs/evidence/a5-char0-transfer (T). T/quadric_lift.py computes over Q(i) the degree-2 relations
{q : q(G) in J + m I^2} of a fiber-track pair and compares their echelon form with the retained K2 at the split
primes 32009 and 32029; `--cores N` takes its two standard bases from nfmodStd (Singular nfmodstd.lib). T/kaggle
holds the kernel generator (make_kernels.py), the shared runner (runner.py) and the generated kernels with retained
output. docs/evidence/a5-kernel-attachments/fiber_inputs.py gains the E8-bar -> VB route. T/README.md states the
results; docs/evidence/a5-exceptional-fibers/ledger.tsv gains rows.

## Claims under review (justify or falsify each against the source and the retained records)

1. T/quadrics-iso-nm.json (direct std) and T/quadrics-iso-nm-modular.json (nfmodStd) hold the same relation space,
   equal to K2 at both primes, with a mutation detected. Check the comparison code: reduction of Q(i) coefficients
   at a prime (i -> root), denominators divisible by the prime, the echelon comparison, and what the mutation proves.
2. The modular route is as rigorous as the README says. State exactly what nfmodStd certifies (its final test, its
   behavior for inhomogeneous ideals in a global ordering, bad primes) from the library source on this machine, and
   whether the README claims more than that.
3. T/quadrics-e8-vb.json: E8-bar -> VB over Q(i) equals K2 at both primes; the producer route added to
   fiber_inputs.py matches the route the modular header of that pair uses.
4. E8-bar -> N- and W8 -> N- are reported as no verdict, with the stopping step and memory named, and no sentence
   reads as a result for them. The retained Kaggle output (summary.json, driver.log, singular.log) supports the
   stated stop: Singular killed for memory 27,718 s in, inside the standard basis of the relation ideal.
5. T/kaggle/runner.py: the driver timeout, the outer `timeout` and the push limit are ordered so the kernel writes
   its records before Kaggle ends the session; output is streamed to files; summary.json is rewritten on a
   heartbeat; a killed child is reported with its return code. tests/test_a5_kaggle_kernels.py holds the ordering.
   Find any path on which a stop still loses the log.
6. Every generated kernel under T/kaggle equals what make_kernels.py writes; the pinned commit of the E8 kernel is
   intended and documented.
7. Ledger rows and README sentences agree with the JSON records, status words included; the README's "check 3"
   (good reduction of J + m^N as a transfer criterion) is known to be refuted on another branch: report where this
   branch's text still relies on it.
8. Code: CPU-bound loops over independent items go through gororoba_quantum/parallel.py; no file holds a token, an
   account identifier, an email address or a local absolute path (a public Kaggle owner/slug is allowed).

## Questions to answer

- Which stated result does not follow from its record, and what is the cheapest decisive check?
- Defects in code, mathematics and text, each with file:line.
- Whether any retained file must leave a public repository.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a named theorem,
each marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
