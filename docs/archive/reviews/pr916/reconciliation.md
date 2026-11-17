# PR 916 local review reconciliation

## agy gemini-3.8-flash-high (red team, head 43feb6fac)

1. gen_family.py reduction loops bounded by size(): confirmed (Singular size counts nonzero generators). A size-bounded
   loop can only leave generators unreduced, so a reported count can only exceed the true count and a reported 0 is
   sound. All 24 retained arcs scripts give identical counts under ncols. Fixed in 14f827202 (ncols loops; the 16
   relation-ideal-orders scripts regenerated, record and logs byte-identical).
2. Chart certificate never exercised on a nonreduced ring: confirmed for the calibration (all five cells give a
   squarefree chart; only the Cohen-Macaulay gate lets the chart decide, as the module docstring argues). Fixed in
   2510f9840: known-bad sixth cell K = (y1^2) in three variables, Cohen-Macaulay and nonreduced; the chart finds no
   squarefree base and the ring stays undecided.
3. Gate replay writes scripts and logs into the retained tree: confirmed. Fixed in 14f827202 (beside the output
   record); the replay at 2510f9840 left git status clean.
4. Iso and W8 not probed for nilpotents: refuted. Both are Cohen-Macaulay with a squarefree chart, which proves them
   reduced (quadric_rings.py docstring), so no nilpotent exists to probe; radical() on W8 was OOM-killed at 12G.
5. Missing scroll P2NONVAN mutation: confirmed, fixed in 2510f9840. Pytest not reading the committed records:
   refuted as a defect; the workspace rule puts record replays in on-demand gates (ci/gates.json), not admission tests.

Ledger audit: every changed row judged earned. Conjectures 1-3 noted; conjecture 3 is the dimension count behind the
chart argument, not new structure.

## codex gpt-daybreak-blue (high, head 43feb6fac)

1. Peak memory understated: confirmed against receipt-d2.json (singular_products_std.peak_bytes 5,261,334,937 and
   7,301,444,403; the stated 1.4 and 2.0 GB were linear_algebra.peak_bytes). Fixed in a1113655d (README, A5-560).
2. Expectation-directed nilpotent switch and unconditional exit 0 in quadric_rings.py: confirmed. Fixed in f1d980e73:
   the probe runs on every ring the Cohen-Macaulay test rejects (computed, not expected), main exits 1 on a falsified,
   undecided or defective record (exit_status, with four unit tests). The calibration record is byte-identical; the
   32057 record loses only the 0-form probe of the Cohen-Macaulay E8-bar -> VB ring. Computing the radical of every
   ring is not adopted: a Cohen-Macaulay ring is decided by its chart.
3. npm_map_qi.py exits 0 on a false identity: confirmed. Fixed in f1d980e73.
4. Replay writes into the tracked tree: same as agy 3, fixed in 14f827202; the retained logs left uncompared are
   digested into the record rows in 0728e4fc5.
5. Missing scroll P2NONVAN mutation: same as agy 5, fixed in 2510f9840.

Claim audit: every changed row earned; the N+ 32009 premise judged sound. The serialized 32029 sweep and Q(i) builder
timed out at the reviewer's 850 s cap under host contention, an uncompleted replay rather than contrary evidence.

## Advisor (head f1d980e73)

Confirmed every disposition above; codex 4 was half fixed (0728e4fc5 completes it). Further fixes: radical equality
decides a probed ring reduced, so a falsification can surface (6b67debbe); peaks to systemd's one decimal and sizes in
MiB (7d7de082a); final-head validation and the four-part PR body.
