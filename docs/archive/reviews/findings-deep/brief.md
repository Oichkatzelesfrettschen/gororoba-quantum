# Brief: axiom-deep adversarial review of PR #798 (A_5 exceptional fibers, CD folding, N_hat audit) and its run plan

Read first: <workspace>/AGENTS.md, then AGENTS.md at the root of this worktree
(~/worktrees/gororoba-quantum/docs/a5-32d-findings, branch docs/a5-32d-findings, head 3d928b1a6, PR #798),
then docs/runbooks/computer-algebra.md and docs/runbooks/compute-flags.md.

Rules. Change no file except your report (named at the end); never commit, push, stash, submit to a provider, start
a cloud resource or open a notebook session; spawn no subagents. The build host is a WSL guest on an active Windows
desktop: keep every computation under 5 minutes and 4 GiB, at `nice -n 19`, under `prlimit --as=4294967296`, in a
scratch directory under /tmp outside every repository; never touch the laptop or any remote host. Tools: git,
`/usr/bin/Singular` (4.4.1), `/usr/bin/M2`, msolve, the Rocq toolchain named by the replay scripts (use
`ROCQ=$HOME/.opam/rocq-9.3/bin/rocq`), and `$XDG_CACHE_HOME/gororoba-quantum/ci-py3.14.7/bin/python3` with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. A random sample takes its values from
docs/evidence/anu_qrng/draw-2026-11-08T234838Z.json: codex from index 0 upward, grok from index 500 upward; name every
index you use.

Sources you may read and must use: the whole PR (`git diff origin/main...HEAD`, 409 files; `git log --first-parent
origin/main..HEAD`); every retained result under docs/evidence/ (not only the PR's files: earlier runs under
docs/evidence/a5-exceptional-fibers/, results/, docs/notes/); gororoba-open at
<workspace>/gororoba-open (Rocq proofs under proofs/ or theories/, the SQLite claim
registry); the documents repositories <workspace>/gororoba-documents-public (TAXONOMY.md,
manifest.tsv; mathematics/cayley-dickson, nonassociative-algebra, algebra-and-representation, ...),
gororoba-documents-private and gororoba-documents-technical (read their manifest.tsv and the transcriptions beside each
PDF). You may fetch a paper or book that the question needs (arXiv, a publisher's open copy, zbMATH or OpenAlex
metadata) into your /tmp scratch directory; cite it by URL, title, section and page, and list each fetched item at the
end of your report so the orchestrator can admit it into the documents repositories. Cite no source you have not
opened.

## What "no shortcuts, recursively down to the lowest axiom layer" means for this review

For each claim: follow its chain of support to the bottom (definition, theorem with its hypotheses, retained raw
record, or measured value) and check every link, not the summary that cites it. A ledger row is a pointer, not a
proof; a README sentence is a pointer to a log; a log is checked against the script and input bytes that produced it
(digests); a theorem is checked for its exact statement and its `Print Assumptions`. Re-derive an integer when the
derivation is short, recompute a rank or Hilbert function when it fits the limits above, and name every hypothesis a
proof uses that the record does not establish (field characteristic, saturation, radicality, reducedness, genericity
of a sampled point, primality of a specialization). State the assumption that would have to fail for each result to
fail, and whether anything retained tests it.

## Claims under review (each a claim, not a fact; justify or falsify it, then give its resolution)

Central record: docs/evidence/a5-exceptional-fibers/ledger.tsv (`ledger.py --check`); registry claims.json, checked by
`build_registry.py --check d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2 ../../local/a5-failed-runs
iso-d6-n19-laptop` run from docs/evidence/a5-exceptional-fibers (never without `--check`: it rewrites the registry).

1. C30 lies in the W8 -> N- fiber, so F(I) = k[y]/K2 in every degree at p = 32009 and 32029 (A5-066 and rows citing
   it; structure/c30-bounded/README.md steps 1 to 8, l0/, hf/; K2 radical by A5-061). Status: proved (argument plus
   computations at two primes). Falsifier: a gap in the Cartier twist (step 2), the formal-IFT uniqueness and chart
   identity (step 4) or the Nullstellensatz step (step 8); a G_j nonvanishing on the chart curve.
2. E8-bar -> N+ h_5 = 952 by transport from N- (A5-082, A5-088): witnesses.jsonl sign-isomorphism rows (witnesses.py
   `sign_iso`); build_registry.py `transport`. Status: certified. Falsifier: the witness compares generators that are
   not the ones defining F(I) (header identity, G span vs G list, the producer specialization), or the map fails to
   fix the origin or to preserve the grading.
3. X degree 4 at 32029 (A5-171, A5-159; d4-p2/). Status: certified. Falsifier: a header, engine or prime mismatch.
4. Iso h_6 = 2,422 at both primes (A5-119, A5-125; iso-d6-n19-laptop/). Status: certified.
5. Last-jump law A5-244 and the closing orders: Iso and W8 close at N = 3d + 1; X- and E8-bar at floor(7d/2) + 1 with
   a one-step plateau at even d (xm-lown/README.md, forecasts/trends-2026-11-06.md d-rows, roadmap item 7 of
   docs/notes/topics/a5-exceptional-fiber-findings.md). X- degree 6 is preregistered (xm-lown/README.md, last
   section: r_22 = 665 with blocks 181/178/153/153, r_21 = r_20 = 496 with 132/136/114/114) and running elsewhere.
   Status: survives (law), hypothesis (closing orders). Falsifier: a jump, split or closing N that differs.
6. Folding: proofs/CdHalfFold.v (`RealHalfFoldDimension`), proofs/CdTwistedProduct.v (`W8_ideal_exchange`); A5-222 to
   A5-227, A5-235. Status: proved (Rocq) / computed at F_p. Falsifier: an axiom beyond the printed ones, a statement
   weaker than the notes cite.
7. N_hat audit (docs/evidence/pathion-kernel-map/nhat-bias/, A5-228 to A5-243), including the paired character
   contrasts `minus_zero_t` now in result_spectral.json. Status: as each row states.
8. Engine map (w8-engine-map/README.md): blocks are coupled in the closure of fiber_rank_v11.py; memory model; W8
   degree 6 forecast 129 GiB products, 139 to 223 GiB closure, 18 to 27 h. Status: measured at d = 3, 4, extrapolated.

## Questions to answer, each with a resolution (a concrete patch described in text, a computation with its command,
## or a ledger status change) that the orchestrator can apply

- Which claims survive from first principles, which fall, and why, at the axiom layer described above.
- Prior art: for each structural result (C30 argument, sign transport, last-jump law, closing orders, half fold,
  twisted product, N_hat Walsh form), search the documents repositories and the literature (fiber cones and special
  fibers of blowups, Rees algebras, Hilbert functions of fiber cones, Cayley-Dickson zero divisors: Moreno, Cawagas,
  Biss-Dugger-Isaksen, de Marrais, and whatever the manifests hold) and say what is known, what is new, and what an
  existing theorem gives for free.
- Engine design for degree 6 (E8-bar h_6 <= 1666 at about N = 21 to 22; W8 N = 19 as an engine test): judge these
  levers against fiber_rank_v11.py source and the map, with expected memory and time: (a) skip product rows that
  vanish because deg g + deg m >= N; (b) 2-byte storage with per-panel float64 BLAS (p < 2^15); (c) store only the
  free columns of each reduced echelon basis; (d) in-place block update and chunked `new`; (e) stream the products
  matrix L by degree level; (f) a GPU path for exact F_p elimination and modular GEMM (Kaggle T4 x2 16 GB each, laptop
  RTX 4090 Laptop 16 GiB, build-host RTX 4070 Ti 12 GiB as last fallback), with the prototype described in
  docs/design/gpu-exact-modular-linear-algebra.md; (g) any better algorithm (e.g. computing the fiber-cone Hilbert
  function from a Groebner basis of the Rees ideal, msolve/F4, M2's `specialFiber`, or a local-route proof like C30
  for E8-bar and Iso that removes the rank run). Name the acceptance test (W8 degree-4 rerun with byte-equal ranks).
- Quantum hardware for nullities: propose algorithms by which a QPU (Quandela Ascella/Belenos photonic, Quantum
  Inspire Tuna-17, IQM Garnet, IBM Heron when its quota returns) measures or certifies a nullity, rank or kernel
  property that then seeds or prunes a fast exact CPU/GPU computation. Ground each in the repository's rules
  (AGENTS.md "Grounding and algebra": L_a is a linear encoding, mutation tests, arms + - - +, null arm) and in the
  retained hardware records (docs/evidence/pathion-kernel-map/, results/quandela/, results/live/); say what a
  classical computation cannot already answer, or say plainly that it can.
- Conjecture where nothing is posited: the ring behind the parity box of A5-244 (P^1 x P^1 under O(2, 2)); why X- and
  E8-bar close at 7d/2 + 1; whether the C30 local route decides Iso (V(K2) prime of degree 23) and E8-bar; each with
  its falsifier and cheapest test.
- Connections across the A_5 fibers, the Rocq folding results and the N_hat hardware audit: mark each proved,
  computed or hypothesis.
- Run plan: for each open row (`ledger.py --open`), the computation, cost and peak memory with the evidence for the
  estimate, and the host: laptop (Ryzen 9 7945HX 16c/32t, 54 GiB in WSL, use at most 36 GiB, RTX 4090 Laptop 16 GiB),
  OCI A1 (2 ARM cores, 11 GiB, Singular only, no numpy), Kaggle CPU (about 30 GB, 12 h) and GPU (T4 x2), paid cloud
  (Azure, Google Cloud, AWS, used sparingly), and which items can run in parallel. Name what no host can finish.
- Defects: code, claims and records, with file:line.

Report ranked by consequence; every claim tied to a file:line, a command with its output, a theorem name or a cited
source, marked proved, computed, measured or hypothesis; every finding followed by its resolution. Write it to
<worktree>/docs/local/reviews/deep-<your-reviewer-name>.md, under
300 lines, with the fetched-sources list at the end.
