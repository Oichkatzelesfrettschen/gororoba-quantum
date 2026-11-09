# Brief: adversarial audit of every row of the A_5 exceptional-fiber claim ledger

Read first: AGENTS.md at the workspace root, then AGENTS.md at the root of the review worktree (a detached checkout of branch
`a5/fiber-ladders-and-run-plan` at commit 4635cc5a4, the head of draft PR 800). Work read-only: change no file except
your report (named at the end); never commit, push, stash, submit to a provider or start a cloud resource; spawn no
subagents. You may run git, Python as `$PYTHON` (set `PYTHON=python3` and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`;
numpy, python-flint and sympy are installed), Singular as `Singular -q --no-rc < script` (Singular 4.4.1; always close
stdin), Sage as `sage`, and the repository's checkers; keep each computation under 15 minutes and 8 GiB, in a scratch
directory under /tmp, never inside a checkout. This host is an interactive desktop: run at most two computations at
once. A random sample takes its seed from
docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json values at indices 1100-1199 (codex-medium), 1200-1299
(codex-terra), 1300-1399 (grok); name the indices you use.

Material, all inside the review worktree:
- The ledger: docs/evidence/a5-exceptional-fibers/ledger.tsv (242 rows; columns id, kind, fibers, primes, claim,
  status, basis, evidence, falsifier, supersedes, updated) and its checker `ledger.py --check` beside it.
- The registry: claims.json, certificates.jsonl, unbound.jsonl and receipts, rebuilt by `build_registry.py --check`
  with the scan roots listed in that directory's README.md (`d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2
  xm-lown ../../local/a5-failed-runs iso-d6-n19-laptop vb-d6-laptop`, run from docs/evidence/a5-exceptional-fibers;
  never run it without `--check`, since a write mode rewrites the registry); witnesses.jsonl (sign isomorphisms).
- The rank engine: replay/engine/fiber_rank_v11.py (sha256 prefix 7849cbc71ccf1787) and earlier versions beside it;
  the retained rank records (*.json with .err and .time) in the scan roots.
- The narrative: docs/notes/topics/a5-exceptional-fiber-findings.md (methods, hypotheses, roadmap, run plan) and
  docs/notes/topics/a5-exceptional-fiber-status.md (goal and status by layer, with its ledger counts).
- Structure and arc evidence: docs/evidence/a5-exceptional-fibers/structure/ (including c30-bounded, the W8 proof),
  working/build/arc/ (arc certificate of E8-bar -> VB, arc-report.md, the t7 = 1 chart normalization and the order-1
  arc test t7arcs.sage with its logs), arcs*/ directories, forecasts/trends-2026-11-06.md.
- Neighbors: docs/evidence/a5-strata-regularity/, docs/evidence/a5-zero-divisor-strata/,
  docs/evidence/pathion-kernel-map/, docs/design/a5-kernel-bundles-nullity8-program.md, gororoba_quantum/cd_core.py
  (the Cayley-Dickson specification), proofs/ (Rocq), docs/archive/reviews/findings-deep/ (the previous deep review
  and its reconciliation) and docs/archive/reviews/cd-tower/report.md (an unreviewed agent analysis).
- Documents: the workspace documents repositories (gororoba-documents-public,
  -private, -technical; `manifest.tsv` in each) where your session can read them; otherwise the web. Say which
  sources you could not open.

## Claims under review (each is a claim, not a fact; justify or falsify it)

Every row of ledger.tsv is a claim with a status. Treat each status as the thing under test:

1. `certified` rows (90): the cited record exists, its rank equals the claimed lower bound, the engine and header
   digests in the record match the canonical files, the upper bound HF(k[y]/K2, d) is the stated number, and the
   sign-isomorphism transport (where cited) is a valid witness. Falsifier: a record that does not replay its digest,
   a rank or HF mismatch, a transport whose witness does not map the generators.
2. `proved` rows (32): the cited proof covers the statement as written, with no unstated hypothesis (radicality,
   reducedness, equidimensionality, characteristic). Falsifier: a gap or a counterexample in the cited argument.
3. `survives` rows (53): the basis supports the claim at the stated scope, and the falsifier is decisive and has not
   fired in any retained record. Falsifier: a retained record that contradicts the row, or a falsifier that cannot
   decide the claim.
4. `refuted`, `rejected` and `superseded` rows (59): the refutation is sound (the claim really failed, not a stalled
   run read as a failure), and the superseding row exists and covers the old one.
5. `open` rows (8): the falsifier is stated and reachable; name the cheapest computation that decides each.
6. The status page's counts: 92 of 96 per-degree cells certified or proved for degrees 1 to 6 over sixteen
   fiber-and-prime rows; one of five all-degree claims proved; no characteristic-0 or kernel-plane-limit result.
   Status: computed from ledger.tsv. Falsifier: a recount that differs, or a cell whose row says otherwise.
7. Cross-row consistency: the fibers and primes columns name the pair the basis is about (A5-006 was corrected on
   2026-11-09 from the 3-generator pair to X+ -> N+, X- -> N-), superseded rows point at live rows, every evidence
   path resolves, and claims.json agrees with the ledger statuses.

## Questions to answer

- Rank every defect found by consequence for the program's goal: the kernel-plane attaching data of
  `dimension32-global-topology` (status page, "The goal").
- Multidimensional analysis: across fibers, primes, degrees, closing orders, last jumps, block splits and engine
  versions, which patterns does the ledger state, which does the data show that no row states, and which stated
  pattern is weaker than its row says? Mark each proved, computed or hypothesis.
- Conjecture where nothing is posited, each with its falsifier and the cheapest test: closing orders at degree 7,
  the last-jump law beyond Iso, W8 and X-, the VB degree-3 component (A5-016), E8-bar degree 6 (1526 <= h_6 <= 1666),
  characteristic 0.
- Remaining work: for each open item, the computation, its cost and peak memory with the evidence for the estimate,
  and the host it fits: the laptop workstation (32 threads, 52.5 GB RAM plus 13.4 GiB of an RTX 4090 Laptop), the build
  host (12 threads, 38.6 GiB, interactive, small jobs only), OCI A1 (2 ARM cores, 9.5 GiB, Singular only), a Kaggle
  session (by approved case), or a paid VM (by approved case).
- Defects in code, records and text, with file:line.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Give a per-row verdict table (id, status under test, verdict:
holds / defect / cannot check, one-line reason) covering all 242 rows, then the ranked findings. Write it to
docs/local/reviews/ledger-audit-<your reviewer name>.md,
under 900 lines.
