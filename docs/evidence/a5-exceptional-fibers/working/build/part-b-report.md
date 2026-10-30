# Part B report: degree driver and certificate layer

Files (worktree a5-kernel-attachments, docs/evidence/a5-kernel-attachments/, uncommitted):
- fiber_cone_driver.py: `--header --degree --previous-relations --out --prime` (plus `--memory-gib`, `--timeout`, `--batch`).
- fiber_certificates.py: `candidate-ideal` and `dense-family` subcommands.
- tests/test_a5_fiber_cone_driver.py: 5 pure-Python tests (parser, kernel, admission bound, dense-family verdicts); pass.
- ruff format/check and mypy through ci/pinned_tool.py: clean.

Driver: stage 1 (Singular, one cgroup unit) builds products reduced mod J per factor, std(J + m P_d), normal forms, writes
std basis; Python parses exactly (one merged parser), computes rank and left kernel with python-flint; stage 3 (Singular)
re-forms sum c_b P_b for every relation and reduces by the stored std basis (exact membership, fails the run otherwise).
Degrees 1-2 take all monomials; d >= 3 takes kbase(std(K_{<d}), d). Outputs per degree: receipt-dD.json (status
"degree-certified", hashes, matrix shape, h_d, per-stage non-cumulative seconds and memory peaks parsed from
systemd-run's "Memory peak", versions), relations-dD.rel, cumulative relations-upto-dD.rel. Singular runs under
`systemd-run --user --wait --pipe -p MemoryMax=3G -p MemorySwapMax=0 -E MALLOC_ARENA_MAX=2`. Pool: `--batch` runs
(pair, degree) items through parallel.ordered_map in chunks of floor(budget / per-job cap) so resident caps never exceed
the budget; tested only as the admission function (budget 3, job 3 gives 1 worker).

Bug found while building: a Singular `int t1` shadows ring variable t1 and silently corrupts polynomials read afterwards;
timers are named tm0..tm2. Singular `ideal` assignment from text also reorders generators (irrelevant here: the nf file is
consumed in write order).

Validation (3G cap, logs in docs/local/a5-failed-runs/build/logs/part-b/):
- E8-bar->VB (hdr/vb.sing, first 4 lines of runs/e8vb_a2/input.sing): h = 10, 34, 80; 21 quadrics, ideal equal to
  runs/e8vb_a2/k2.rel both ways (vb/cmp output a_in_b = b_in_a = 1); degree 3: 0 new relations. Degree 2 total about
  9 s (products+std 5.6 s, membership 3.4 s, linear algebra 0.1 s); degree 3 about 6-7 min.
- X- degree 2 (hdr/xm.sing, first 4 lines of runs/s1/input.sing): h2 = 51, 69 relations, ideal equal to
  kaggle-pack-a/xm_nm/xm_nm_fiber.rel both ways (xm/). Note kaggle-pack-a/xm_nm/input.sing is a `ds` ring, so the
  header used is the dp one from runs/s1.

Certificates:
- candidate-ideal (L = H + lifts; checks H in L, L in kernel by substitution, L : g = L, fiber of L equals (K)).
  On E8-bar->VB: pivot G_3 (9 terms), 21 lifts built in 40 s (one `lift` call against J + t_k P_b), then std(L) in 18
  variables did not finish: 500 s timeout at 2.1G peak, and a second run reached the 3G cap after 14 min. Status
  candidate-not-verified, no scheme-equal claim. It is not shown cheaper than saturation: method B on VB
  (runs/e8vb_b) has printed nothing past its pivot, so neither route has a completion at these limits. The certificate
  code path past std(L) (colon, substitution, fiber comparison) is therefore untested.
- dense-family: exact containment of supplied limit points in V(K) components; support-equal only with a per-component
  certified dimension argument, otherwise "support lower bound", "refuted" for a point outside. Random arc sampler NOT
  implemented: it needs qrng_seeds draws and ledger rows, outside the files I may touch. Unit-tested only.
- bounded Hilbert function: scope cut, no relation-type bound exists in the tree.

Proposed ci/gates.json entries (not edited): fast gate, E8-bar->VB degrees 1-2 (about 9 s, needs Singular and
systemd-run on the runner; hosted CI may lack both, so check availability first); full tier, X- degree 2 (about
19 s: 16.1 s products+std, 2.0 s membership, 0.4 s linear algebra; above the 15 s fast-gate bound).

Open limits: dense matrix in flint scales rows x columns (fine to degree 3 on these inputs); the sq.txt std basis
file is large for big cases; paths outside the checkouts are recorded by file name only; Macaulay2 version recorded from
`M2 --version`.
