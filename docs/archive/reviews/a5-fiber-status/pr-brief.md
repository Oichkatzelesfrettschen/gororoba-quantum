# Review brief: gororoba-quantum pull request 990, head acdcda581

Read first: the workspace AGENTS.md, then gororoba-quantum/AGENTS.md. You are read-only: change no file, create no file,
run no git write and no network or provider job. Run no computation above 60 seconds or 2 GB (no Singular, no test
suite); reading, grep and small Python one-liners are fine. Print the report as your final answer.

The review tree is the session worktree (branch a5-fiber-status-and-identities). The diff is
`git diff 78c5e5c3a..acdcda581` (six commits).

## What the change claims

1. A5-583 certified: docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/ (slice_bridge.py,
   bridge_verify.py, records, Singular logs, README). An invertible 21 x 21 map over F_32009 carries the weight-slice
   quadric ideal of E8-bar onto the header-slice ideal at N- and N+.
2. A5-593 proved, A5-594 certified: .../runs/e8-pfaffian-schur-identity/. Pf_4(W) = Pf(B)^3 Pf_10(T) on 126
   quadruples over Q(i); generators 10 and 16 carry an extra factor through Pf_10.
3. A5-597 proved: docs/evidence/a5-char0-transfer/arcs_vb_qi.py, arcs-vb-qi.sing, arcs-vb-qi.log and the last README
   section. E8-bar -> VB over Q(i): L = K2.
4. A5-577 certified: docs/evidence/a5-kernel-attachments/weight_slice_modular_cells.py and its record and log.
5. A5-595 proved, A5-596 survives: docs/evidence/a5-exceptional-fibers/coefficient-structure/.
6. docs/notes/topics/a5-exceptional-fiber-status.md rewritten; ledger rows in
   docs/evidence/a5-exceptional-fibers/ledger.tsv (A5-577, A5-583, A5-278, A5-418, A5-425 amended; A5-593 to A5-597
   new); review record docs/archive/reviews/a5-fiber-status/.

## Check

- Soundness of each verdict: does the retained log support the row's status and wording? Is "proved" earned for
  A5-593, A5-595 and A5-597, or is "certified" or "survives" the right status? Name hidden premises.
- slice_bridge.py: is the argument "a linear equivalence can be composed with a symmetry into permutation times
  diagonal in torus eigen-coordinates" stated with its conditions (conjugacy of maximal tori over F_p, split tori)?
  The script only needs to find and verify one map; does the README overstate uniqueness or scope? Any bug in
  stabilizer(), solve_scalars() (discrete logs, Hermite normal form) or transport() that the Singular check would
  not catch?
- arcs_vb_qi.py: does rank 4 at two rational points plus vanishing of one prime's generators give dominance onto a
  component of dimension 4? Is K2 inside L established by the quadric stage? Does the mutated control test what it
  should?
- Controls: does each known-bad control reject for the right reason?
- The status note: every cell of its tables against the ledger rows it cites; count of incidences (33) and the
  breakdown; any statement stronger than its row.
- Ledger hygiene: statuses, primes fields, falsifiers, evidence paths.
- Text rules: no local absolute path, host name or address in tracked files; emoji-free American English; durable
  names.

Report findings worst first with file path and line, a severity (FATAL, SERIOUS, SLOPPY, COSMETIC), the governing
principle and the remedy. State SOUND plainly where a part holds. Mark each finding confirmed (source read),
likely or unproven. At most 1,800 words.
