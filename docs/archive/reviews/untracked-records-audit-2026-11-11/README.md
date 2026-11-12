# Audit of untracked records in docs/local (a5-failed-runs, ultrareview-worktree-local, archived-worktrees)

Read-only audit at `main` (head `dd4e84b09`), 2026-11-11, retained with four edits: this paragraph, a path pattern in
the method, a duplicated clause in the class definitions and a note on the raw-byte comparison under RM-2. The audit
produced no per-file listing that is retained: the manifest of the 22,648 + 456 + 505 audited paths with their hashes
is not kept, so every count below is the audit's own and a reader cannot recompute it from this directory; the files
that matter carry their own retention (sections 3A to 3C name each group and its home). The audit changed no file
other than this report, and made no provider call, network access or random draw. Host names, account identifiers and
absolute home paths are left out; "the laptop" and "the build host" name host classes. Repository paths are relative
to the checkout; `A5/` abbreviates `docs/evidence/a5-exceptional-fibers/`, and `docs/local/` names the ignored local
tree that held the audited files.

## 1. Method

1. Hashed every file under the three trees with `git hash-object` (22,648 files in `a5-failed-runs`, 456 in
   `ultrareview-worktree-local`, 505 in `archived-worktrees`; `find -type f`, so the symlink
   `ultrareview-worktree-local/a5-failed-runs` is not double counted) and compared against (a) all blobs of `HEAD`
   and (b) all objects of `git rev-list --objects --all` (88,479 objects, every branch, `pr/*`, `refs/codex`).
2. A tracked copy can differ from the local one for mechanical reasons, so two further normalizations were applied
   before a file was called untracked: (i) the scrub of `A5/retain_working.sh` (home path to `~`, scratch path to
   `SCRATCH`, UUIDs, build-host name, login name), re-implemented line for line; (ii) worktree-path normalization
   (`<worktree>/docs/local/...` to `docs/local/...`), which re-matched 37 files of
   `archived-worktrees` (the `w8-engine-map/logs` timing files). Files above 50 MB are tracked as `.partNN`
   pieces (`A5/split.txt`); 14 local files were matched to their piece sets by exact total byte count.
3. Compared rank records by value: every `r_N` record with per-block ranks (key `d`, `N`, `r_N`, block tuple) in
   the untracked files was matched to the same tuple in any tracked JSON/JSONL/out/txt/log blob.
   Result: 160 files carry only tuples that are tracked; 14 carry at least one untracked tuple, and 10 of those 14
   are test fixtures or review probes (section 4.3); 4 are genuine ladder rungs (RM-4).
4. Read the head and tail of representative files of every group, the tracked README or ledger row that should
   carry the result, and the existing audit `docs/archive/reviews/kaggle-audit-2026-11-09/README.md`, whose
   classifications were re-verified against the current `HEAD` (it predates several landings: A5-286 to A5-290,
   `vb-d7/`, `w8-d5-probe/`, `distribute/out/a5-chart-w8nm-long`, `a5-v7-batch-reduce-e8nm-n12`).

5. Searched the open remote branches for the content of each candidate-missing result. Path search over every
   `refs/remotes/origin/*` tree for `smith_torus`, `germ-checks`, `twist_compare`, `npm_map`, `sign_search`,
   `std-ladder`, `split_test`, `arc-derivative`, `germ-xvb`, `sweep_p32009`, `e8nm_d4_v7`, `w8_d4.jsonl`, `xm_d5_v6`: no
   hit. Added-line search of the diff against `origin/main` of `a5-audit-certificates-20261111` (150 files),
   `a5-char0-quadrics-iso-w8` (34), `a5-monomial-ladder` (181; adds `monomial-ladder/`, `quadric-census/`) and
   `codex/a5-memory-bounded` (15; adds `memory-bounded/`) for the distinguishing values (13369, 6976, 4,195 s, 1,584 s,
   524.8, 407.6, the four block-split tuples, the tool names): no hit. The branch `a5/exact-quantum-contracts-20261111`
   did not resolve as a ref at audit time. Hence no group below is tracked on an open branch, apart from the 10 blobs of
   section 2.1 and the 9 older-revision blobs of section 2.3.

Classes (mapped to the four classes of the request: RM, AR, FR, SC): AR already represented, including AR-gap, a
result whose numbers a tracked claim states while the record it cites is untracked; SC scratch (scripts,
intermediates, model-review prose, test logs, regenerable tables, duplicates, producing scripts and
`REPORT.md`/`VALIDATION.md` prose that ship with a record), with RMD a sub-label for working-record prose and
provenance that `retain_working.sh` would retain; RM result missing (a completed computation whose numbers are stated in no tracked file); FR failed or aborted run.
Counts are per file.

File universe: every regular file found by `find -type f` under the three trees (symlinks not followed). The figures in
the request (493 of 706, 44 of 78, 19 of 87, 2 of 2) come from a universe I could not reconstruct, and they differ
from the recomputed fractions (70 percent against 94 percent for `a5-failed-runs`; 56 percent against 66 percent for
`ultrareview-worktree-local`; 22 percent against about 58 percent for `docs-a5-32d-findings`). The counts below replace
them.

## 2. Counts

### 2.1 a5-failed-runs (22,648 files)

Tracked by raw hash 1,364; tracked after the scrub 60 more; on another ref only 10 (nine PDFs and `purpose.md` on
`pr/661`, plus one compiled `.pyc` on four quandela and least-squares branches). Untracked everywhere: **21,224**.

| group (top-level directories) | files | untracked | AR (of which AR-gap) | SC | RMD (SC, prose) | RM | FR |
|---|---:|---:|---:|---:|---:|---:|---:|
| `arcs-p2` | 18,904 | 18,836 | 18,700 | 130 | 0 | 6 | 0 |
| `reviews` | 1,050 | 956 | 2 (2) | 947 | 5 | 2 | 0 |
| engine validation (`v9-e2e`, `v10-compare`, `v11-build`, `export-split-test`, `v9-n15-laptop`, `v9-review`) | 815 | 760 | 108 | 649 | 1 | 2 | 0 |
| `falsify` | 220 | 183 | 60 (7) | 118 | 0 | 5 | 0 |
| compute outputs (`distribute`, `kaggle-v7`, `kaggle-tpu`, `azure-*`, `runs`, `trunc`, `d5-p2`, `receipt-d3-probe`, `std-ladder-desktop`, `e8nm-d4-p2-n13`) | 930 | 270 | 111 | 100 | 5 | 9 | 45 |
| everything else (`build`, `b9-vb-test`, `arcs-x*`, `asymmetry`, `second-opinion*`, `e8nm-d4-*`, `opt-review`, `n15-result-review`, `probes`, 10 loose prose files, ...) | 722 | 219 | 71 | 132 | 16 | 0 | 0 |
| **total** | 22,648 | **21,224** | **19,052 (9)** | **2,076** | **27** | **24** | **45** |

In the four-class view SC is 2,076 + 27 = 2,103. The RMD files are working-record prose that `retain_working.sh` would
copy and that carry no number absent elsewhere (listed in section 3C). RM counts files (24) that hold six distinct
results (3A).

### 2.2 ultrareview-worktree-local (456 files)

Untracked everywhere 302 (4 more are on `quandela/ascella-cz-tomography-reference-runs` or equal an older revision of a
tracked path); 81 of the 302 are byte-identical to files in `a5-failed-runs` (`distribute/out`, `kaggle-v7/out`),
duplicates under another path. AR 175 (`kaggle-pull` 73, `kaggle-collect` 84, `candidates-review` 16, `twisted-tower`
1, `plucker-x.log` 1), SC 58, FR 69 (`kaggle-pull`), **RM 0**.

### 2.3 archived-worktrees (505 files)

Untracked everywhere 317 after normalization (354 before it); 9 other blobs equal an older revision of a tracked path
(`w8-engine-map/*.py`, `findings-32d` brief). AR 20 (the `*-report.md` files of `docs-a5-32d-findings`, the two
`.tsv` tables, `w8-engine-map.md`, `engine-v12-report.md`, 8 `ibm-pathion-parallel-coset-drain` logs), SC 297
(`w8-engine-map` exports 177, review and brief prose 130, dry-run exploration records), RM 0, FR 0.

## 3. RESULT-MISSING, AR-gap and retention-lag groups (a5-failed-runs only)

"Home" names the tracked location and ledger row kind. All results hold over F_32009 or F_32029 as stated in each
record; none touches characteristic 0. Producing scripts and `REPORT.md`/`VALIDATION.md` prose are SC and ship with
the record they produced.

### 3A. RESULT-MISSING: numbers absent from every tracked file and every open branch

**RM-1. Cost of std(J + m^N), E8-bar -> N-, p = 32009 (`std-ladder-desktop/`: `summary.txt`, `n12|13|14.log`, `.time`,
`singular-version.txt`; the three `.sing` scripts are SC).** Singular 4.4.1 on the desktop class, option redSB, dp
ordering: N = 12: vdim 11,595, standard basis size 5,125, 627 s, 134 MiB; N = 13: vdim 16,575, size 6,739, 1,584 s,
225 MiB; N = 14: vdim 23,128, size 8,687, 4,195 s, 352 MiB. 11,595 appears in A5-288 as a quotient length only; the sizes
and times appear nowhere. Already flagged as NEW-RESULT by the 2026-11-09 audit; still open.
- Home: `A5/std-ladder/`; ledger kind `method`, beside A5-031 and A5-246 (the quotient lengths equal the tabulated D(N)).

**RM-2. Engine v9 split export, validation (`export-split-test/n9.log`, `n11.log`).** One Singular process computes
std(J + m^N), one process per variable writes its multiplication table: the 11 export files equal the serial export
byte for byte at N = 9 (the logged comparison removed line breaks; a raw-byte comparison made afterwards found all 22
files identical, see `A5/split-export-test/byte-comparison.tsv`) (serial 37.3 s, split std 29.1 s, total 31.3 s) and at N = 11 (serial 524.8 s, split std 407.6 s,
total 425.3 s). The engine `replay/engine/fiber_rank_v9.py` is tracked; the equality and the timings are not.
- Home: `A5/vb-export-levers/` sibling; ledger kind `method`, the shape of A5-280 and A5-288. The 100 other files of the
  directory (exported tables, `split_test.py`) are SC.

**RM-3. VB dominance witness and normalization dimension (`reviews/codex-reaudit/arc-derivative.jsonl`,
`normalization-dimension.json`).** Exact dual-number Hensel derivative of the E8-bar -> VB normalization at
(u1, u2, k) = (5, 7, 4): the two dependent 16 x 16 Jacobian determinants are 13369 and 6976 mod 32009, the actual
projective derivative has rank 3 on both branches, `normalization_dim 4` (3.09 s). `reaudit-adjudication.md` says the
witness was "retained beside the arc report"; no tracked file holds 13369 or 6976.
- Home: `A5/arcs-vb/`; evidence column of A5-015 (ledger kind `structure`).

**RM-4. Four ladder-rung records with per-block ranks.** `falsify/laptop/v7/e8nm_d4_v7.jsonl` (E8-bar -> N-, d = 4,
N = 12: r 357, blocks 117/98/71/71; N = 13: r 440, blocks 140/122/89/89), `falsify/laptop/w8_d4.jsonl` (W8 -> N-, d = 4,
N = 12: r 1644, blocks 425/415/402/402), `falsify/xm_d5_v6.jsonl` (X-, d = 5, N = 16: r 201, blocks 43/46/56/56; N = 17: r
296, blocks 68/66/81/81), `e8nm-d4-p2-n13/record.json` (E8-bar -> N-, p = 32029, d = 4, N = 13: r 440, blocks 140/122/89/89,
6,832 s, preflight 14.36 GB). The r_N totals are tracked (`A5/forecasts/trends-2026-11-06.md` lines 54, 75, 121); the block
splits, wall times and preflight sizes are not (no hit for the tuples in any tracked file or branch).
- Home: the tracked scan root `A5/a5-failed-runs/` at the original relative paths, then `build_registry.py` (they enter
  `unbound.jsonl` as below-target lower bounds); no ledger row.

**RM-5. Tangent-cone comparison of X- and E8-bar -> VB (`falsify/germ-xvb/tc_xm.log`, `tc_vb.log`).** dp ordering, p = 32009:
both germs have dimension 4, multiplicity 2, one minimal prime and a singular locus of dimension 4; the X- cone has nine
quadric generators and no linear form (Hilbert numerator 1,0,-9,18,-15,6,-1), the VB cone one linear form and nine quadrics
(1,-1,-9,27,-33,21,-7,1). It does not decide whether the germs are isomorphic (the re-audit's pilot question).
- Home: `A5/structure/` as an open comparison; ledger kind `structure`, status `open`.

**RM-6. Twist correspondence of the E8-bar arc families (`arcs-p2/e8np-p32009/` and `e8np-p32029/`: `twist_compare.json`,
`twist_compare.log`, `j_twist.log`; 6 records, 6 scripts SC).** The limit vectors of the two certified families of
E8-bar -> N+ equal those of E8-bar -> N- coordinate by coordinate: N+_j(E) = eps_j E^(d_j) N-_j(1/E) on all 11 nonzero
coordinates of the order-2 family and all 16 of the order-5 family, no failing coordinate; under t9 -> -t9 alone 7 of 16 J
generators map to themselves, 9 to their negatives, none of the 21 G generators does. No tracked sentence states the
arc-limit correspondence (the tracked `compare_nm.log` and `cross_control.json` compare P1, P2 and K2 instead). It is
confirmatory: the exact sign isomorphism (`structure/doubling_automorphism.py`, A5-049) implies it.
- Home: `A5/arcs/e8np-p32009/` and `e8np-p32029/`; ledger kind `structure`, confirmatory.

### 3B. AR-gap: numbers stated by tracked claims, cited or implied record untracked (provenance PR, no new result)

- **A5-032 and A5-049 (7 record files in `falsify/`).** `invariants/smith_torus.jsonl` (27 rows: Smith invariants
  1,...,1,2,2 and torus order 4 at all 27 headers; A5-032 states exactly this), `symmetry-sweep/sweep_p32009.jsonl`
  (6,225 signed-permutation rows; A5-032 "exhaustive search over all sign vectors at 32009"), `npm-iso/npm_map.jsonl`,
  `map_p32009-r10754.json`, `map_p32009-r21255.json`, `map_p32029-r9115.json` (the pair flip t8 -> -t8, t9 -> -t9 at three
  specializations) and `sign_search.log` (A5-049: "the full 2^9 sign search finds the pair flip"; t9 alone gives rank
  41 of 42). Scripts `smith_torus.py`, `signed_perm_sweep.py`, `sign_search.py`, `npm_map.py`, `k2_transport.py` ship with
  them. The pair-flip claim is also proved exactly by `A5/structure/doubling_automorphism.py`; the sweep carries the
  limits the re-audit found (profile pruning cannot certify absence), and the `tc_*` tangent-cone probes beside it (12
  files) were withdrawn and stay SC. Home: `A5/structure/sign-symmetry/`; A5-032 and A5-049 add the evidence path.
- **Findings note, line 65 (2 record files in `reviews/codex-reaudit/`).** `germ-checks.jsonl` (27 headers, dp ordering, no
  errors) is the source the note cites for its table of q_2..q_7 (8,27,66,135,246,413 for X and E8-bar -> VB;
  7,27,77,182,378,714 for Iso; 9,39,117,283,594,1127 for E8-bar -> N+-; 8,35,112,294,672,1386 for W8); the table is
  tracked, the cited file is not. `invariants.jsonl` (42 rows) verifies the pair flip at (32009,10754), (32009,21255),
  (32029,9115). Home: `A5/structure/reaudit/`.

### 3C. Retention-lag prose (RMD, 27 files)

`retain_working.sh` would copy these; none carries a number absent elsewhere. `decision-record.md` (366 lines locally; the
tracked copy has 331; the 35 missing lines are the third consult round and the 2026-11-01 correction that E8-bar -> N- is
not a separate fiber), `campaign-dossier-2026-11-01.md` (154 lines; its failure table is covered by A5-048, 050, 057,
070-072 and section 5), `e8nm-d4-plan.md` (159 lines; the refuted hypothesis H_rad), `consult-round4/` (brief and answer),
`singular-lane-brief.md` and `-report.md`, two scout reports, four Azure written cases (`azure-cases/vm1-iso-degree4.md`,
`vm2-w8-degree3.md`, `vm3-vb-chart5.md`, `vm4-e8nm-degree3.md`), `distribute/case-small-jobs-2026-10-31.md`, the
model-review adjudications (`reviews/reaudit-adjudication.md`, `synthesis-2026-11-01.md`, `v7-fixes.md`,
`engine-review-adjudication.md`, `independent-opus.md`, and one `adjudication.md` each in `e8nm-d4-review`,
`n15-result-review`, `opt-review`, `v9-review`, `second-opinion`, `second-opinion-x`), and
`build/inputs/survivors/X+-N-.json`, `X--N+.json` (the two cached Q(i) survivor selections the tracked directory
lacks). Home: `A5/working/` through `sh A5/retain_working.sh <source> --dry-run`, which drops `ip` and `known_hosts*`.

## 4. Groups judged AR or SC (with the representing record)

### 4.1 AR
- **arcs-p2 (18,700 AR files).** Pre-consolidation tree of the formal-arc campaign. `A5/arcs/` holds the consolidated
  replay for the four targets (`campaign_summary.json`, `result*.json`, `k2_primes.log`, two certified families per target);
  `A5/arcs/README.md:139-140` states that the per-family scripts and logs (4,656 files per target) stay in the replay scratch,
  and lines 169-189 tabulate the 1,296-family scans (1,281 classified, none outside V(K2)). The local
  `campaign_summary.json` differs from the tracked one only in key names and added `fiber`/`prime` fields. The two
  per-target scan JSONL files (`scan_k_pq`, `scan_k_rs`, `scan_near`) are the raw form of that table.
- **arcs-x, arcs-x-p32029** (21 files): predecessors of `A5/arcs-x/` (`xarc_*` scripts, `records/p32009|p32029`); both
  `certified_P2: true` for xp-nm and xm-np.
- **asymmetry, arcs-l0-symbolic, char-split, k2-primes-nm, probes/lf, trunc, radicals-global, e8nm-d4-structural:** the sheets
  (4,1,4) and (4,2,7) are A5-002; the order-3 symbolic family stopped at 17 GB is A5-074; per-character totals 215/197/270/270 are
  the K2 block counts of A5-183; the leading-form ranks 137 of 265 and 53 of 240 are A5-047; Iso d = 4 N = 13 rank 640 at both
  primes is A5-007/117/123 (the raw normal forms `trunc/iso_d4/jnf13.txt`, 2.5 MB, are cited by
  `A5/working/azure-results/README.md:27` as a local file); K2 primes of E8-bar -> N- equal `A5/arcs/e8nm-p*/k2_primes.log`;
  the HF values 21, 83, 225, 495, 952, 1666 and 16, 69, 195, 440, 861, 1526 of `e8nm-d4-structural` are in the arcs README
  table.
- **v10-compare, v11-build, v9-e2e** (108 AR files, the JSON rank records): equal to `A5/v10-comparison.jsonl` (11 cases) and
  `v11-comparison.jsonl` (15 rows); the exported tables (149 MB in `exp/`, `exp-n15/`) are SC.
- **azure-results** (4 AR files): `vm1-work.tgz` is tracked as nine pieces whose summed bytes and recorded SHA-256
  (`555a86ab...`) equal the local archive; `vm4` outcome (exit 124) is described at
  `A5/working/azure-results/README.md:36-40`.
- **distribute/out** (46 AR files): Kaggle outputs of `a5-k2-*`, `a5-chart-*-long`, `a5-e8nm-d3`; counterparts listed in
  `kaggle-audit-2026-11-09/README.md` section 1, which this audit re-checked against HEAD (A5-289 now lands chart-w8nm-long,
  A5-288 the batch-reduce result). Seven `sq.txt`/`nf-*.txt` files above 50 MB are stored as pieces.
- **kaggle-v7/out X- rungs** (24 AR files): `A5/certificates.jsonl:74-76`, `a5-failed-runs/kaggle-v7/bound/xm_d5_v7.jsonl`.
- **falsify** (53 AR files): `k2-depth` equals `A5/k2-cm.jsonl` (Cohen-Macaulay lengths 7, 23, 50, 15, 20), the `laptop`
  records and `receipts-v6` are the tracked bound records, `k2counts`, `probes-v6`, `w8prime`, `e8probe` are
  predecessors of the Hilbert tables.
- **ultrareview-worktree-local/kaggle-collect** (84): `A5/vb-export-levers/kaggle/a5-vb-d7-slimgb-*/output/summary.json`
  tracks timings and SHA-256 of every output (A5-280 to A5-287, `vb-d7/out`); the raw `s.txt`/`kbase.txt` files are
  regenerable. `a5-char0-xm-quadrics` and `-truncation-n22`: `docs/evidence/a5-char0-transfer/quadrics-xm-nm.json`, A5-248, A5-290.
  `kaggle-pull` ok kernels: audit sections above.
- **candidates-review/**: `docs/archive/reviews/2026-11-10-external-candidates-review/` retains its subset and README.
- **band-replay** (SC, noted): the replay of `ascella-cz-tomography-band` scripts differs from tracked `findings.json` and
  `reference-low-cell-share.json` at the 1e-16 relative level (197 of 1,788 keys, 26 of 31 keys). No new result; a
  last-digit nondeterminism between the replay environment and the one that wrote the tracked files.
- **archived-worktrees**: the `docs-a5-32d-findings/*-report.md` summaries cite commits and ledger rows that landed
  (A5-222, 226, 227, 228, 244; `structure/c30-bounded`); `v11-cells.tsv` and `v11-last-jumps.tsv` are derived from tracked
  records and cite them; the prediction `last-jump-box-prediction.md` (Iso d = 6, N = 18, r 2,253, blocks 583/568/551/551) is
  confirmed in A5-119; the `ibm-pathion-parallel-coset-drain` logs record the retained runs of results/live (two acquisitions,
  usage 588 s and 590 s of the two 600 s windows), whose raw records are tracked.

### 4.2 SC (selected)
Model-review prose and scratch (`reviews/` 915, `second-opinion*`, `n15-result-review`, `opt-review`, `v9-review`,
`e8nm-d4-review`: reconciled in the `adjudication.md` files, RMD above), `b9-vb-test` (32 files, generated Singular scripts
and logs; the base-locus result is `A5/structure/e8-base-components/` and A5-063), `v9-e2e` engine development tables,
`witness-rerun` (35 rows `identical True`, a duplicate of `A5/witnesses.jsonl`), `m-primary`, `vjg*`, `export-rescue`,
`q5-truncated-std`, the compiled caches and mypy caches, 7 literature PDFs under `reviews/data-review/codex/` (the same
blobs once tracked as `docs/pdf/*.pdf`; document bytes belong in the documents repositories), review fixtures
(`reviews/codex-v7/fixture-*`, `selection-attacks/`: the r 122 against 265 record is the deliberately corrupted fixture
of `A5/forecasts/trends-2026-11-06.md:13`), and `distribute/kernels/`, `kaggle-v7/kernels/` (kernel sources).

### 4.3 The 10 non-ladder files with untracked rank tuples
`reviews/codex-engine-review/parser-false-rank.jsonl`, `reviews/codex-v7/{fix-memory-admission,fix-probes,
frozen-independent,independent,module-path,zero-raw}.log`, `reviews/data-review/{codex,grok}/selection-attacks/*.json`,
`v10-compare/smoke_v10.json`: parser-fault probes, regression fixtures and a smoke test.

## 5. FAILED-RUN groups and ledger coverage

Ledger rows of kind `operational` today: A5-039, 042, 048, 050, 052, 053, 054, 055, 057, 070, 071, 072, 073, 074, 077,
174, 176, 181, 205, 237, 246, 263, 267, 279, 290, 291. Covered failures: Azure W8 degree-3 std OOM (A5-048), W8 jet std
OOM (A5-050), Iso chart saturations (A5-070, 071, 174, 176, 181, 205), symbolic order-3 arcs at 17 GB (A5-074),
E8-bar -> N+ msolve degree-7 OOM (A5-042), char-0 truncation at N = 22 (A5-290). The following have **no operational row**;
draft rows (fibers, prime, class of host, wall time, peak memory, stopping point):

| # | draft row text | evidence |
|---|---|---|
| FR-1 | "the full `std(J + m P_3)` of the 225 degree-3 products of E8-bar -> N- finishes on an 84 GB cloud VM within the 36 h cap" refuted: exit 124 at the 129,600 s cap, peak Singular RSS 49,760,004 KiB, no `std_ms` line; p = 32009 | `azure-results/vm4/watch.log`, `watch.out`; prose at `A5/working/azure-results/README.md:36-40`; case `azure-cases/vm4-e8nm-degree3.md` |
| FR-2 | "msolve Rees-graph elimination (-e 1 -g 2, 4 threads) fits a 32 GiB Kaggle CPU kernel" for Iso -> N-, Iso -> N+, W8 -> N+: killed (rc -9) at 9,069.4 s, 10,910.0 s and 3,839.7 s, peak child RSS 31.37, 31.37 and 31.35 million KiB of 32.87 million; last F4 step degree 10 (110,419 pairs; 110,419; 52,198); p = 32009. E8-bar -> N+ is A5-042 | `ultrareview-worktree-local/kaggle-pull/a5-{iso-nm,iso-np,w8-np}-msolve/{result.json,msolve.log}` |
| FR-3 | "the local-syzygy computation of the degree-2 (degree-3 for Iso) fiber relations finishes in a Kaggle CPU session": W8 -> N- and W8 -> N+ killed (rc -9) at 5,437.4 s and 6,207.5 s (peak about 29.9 GiB, after printing 24 generators, 7 slice variables); E8-bar -> N+ rc 124 at 41,047.0 s (peak 18.8 GiB, 21 generators, 9 slice variables); Iso -> N+ degree 3 rc 124 at 41,051.8 s (peak 17.4 GiB, stage `syz`, U size 6,784); p = 32009 | `kaggle-pull/a5-{w8-nm,w8-np,e8-np}-fiber-singular`, `a5-iso-np-h3-singular`; consistent with A5-044 (superseded by the jet-truncated route) |
| FR-4 | "engine v7 quotient export for E8-bar -> N- degree 4 at N = 14, 15, 16 fits one 41,000 s Kaggle session": N = 14 rc 1 after 40,381.7 s wall (peak RSS 4.4 GiB; export finished, then the admission check `preflight 24.59 GiB exceeds --max-gb 24.0`); N = 15 and 16 rc 124 at 41,000 s (tables qB, qM1, qM2 only; none); p = 32009. The closing order for this ladder is already N = 15 on the laptop, so the row records cost | `a5-failed-runs/kaggle-v7/out/a5-v7-e8nm-d4-n1{4,5,6}/{summary.json,stderr.log,progress.log}`, `kaggle-v7/watch_e8nm_d4.log` |
| FR-5 | "Singular `normal` on the E8-bar -> VB chart ideals finishes in a Kaggle CPU session": charts 3, 5, 7 rc 124 at 14,400 s each; chart 5 alone rc 124 at 37,800 s; the chart-7 arc step raised `ValueError: min() iterable argument is empty` after 8.5 s; p = 32009. The build host completed the chart-5 normalization (`normal_done` with one ring, 21 variables, 382 relations; the log's timer reads 359) and 14 order-1 arcs in `build/arc/n5/arcs5.jsonl`, each with `inP2` true and `inP1` false (a fifteenth line records a free-parameter choice with Jacobian rank 16 of the 17 needed), consistent with A5-016, so this row states only the Kaggle cost | `distribute/out/a5-vb-arcs/`, `a5-vb-chart5/`, `build/arc/n5/` |
| FR-6 (optional) | "minAssChar and minAssGTZ of the Iso K2 on a Kaggle CPU kernel finish in 41,000 s": both rc 124 | `distribute/out/a5-k2-iso-direct/`; `A5/structure/iso-k2/chart-colon/README.md` states "exceeded about 40,000 s" without a ledger row |

FR-1 is mentioned in A5-049 as duplicated N- work, but A5-049 is a `structure` row, so the draft operational row stands.
The four ghost-error and ghost-event kernels among the failed Kaggle pulls (`gororoba-ghost-error-scale-a2`,
`gororoba-ghost-event-scale-c1`, `-d2`, `-e2`: 58 to 112 s, no result, no `exit.json`) belong to
`docs/archive/reviews/pr-147-ghost-error-scale.md`, not to the A5 ledger.

Not a computation failure and needing no row: `receipt-d3-probe/` (10 files): six launches of the degree-3 receipt driver
ended `Failed to start transient service unit` or status 127 before Singular ran (`d3-products.log` 110 bytes); the
degree-3 membership route is covered by FR-1 and A5-092 (degree 3 by truncated rank).

## 6. Unclassified or not verified

- `arcs-p2` per-family files were not read one by one (18,700). Their correspondence to the tracked tallies rests on the
  README statement and on the matching file counts (4,650-4,654 per target) and equal `campaign_summary.json` tallies; a
  full replay (`A5/arcs/replay.sh`, about 8 minutes on the build host) would confirm it and exceeds the two-minute limit.
- The 82 per-header `.sing`/`.log` files of `reviews/codex-reaudit/` and the 12 `symmetry-sweep/tc_*` files were treated as
  regenerable or withdrawn; the re-audit's `REPORT.md` states this, I did not rerun them.
- RM-3 values (the VB dominance determinants) and the 3B records (the 42-row `invariants.jsonl`, `germ-checks.jsonl`) were
  read from the local files and compared by `git grep` against the tracked tree and the diffs of the open A5 branches; a
  tracked file holding the same numbers under a different digit grouping would escape the search.
- The remaining record files of `reviews/codex-reaudit/` (`arc-binding.jsonl`, `arc-generator-binding.jsonl`,
  `relation-checks.jsonl`, `extra-checks.jsonl`, `degree2-receipts.jsonl`, `degree2-receipt-bindings.jsonl`,
  `receipt-coverage.jsonl`, `regression.jsonl`, `e8-control.jsonl` partly tracked) are classed SC as review verification
  output (checks of tracked records and of the reviewed engine). I read their counts in `REPORT.md` and did not compare each
  row against the tracked witnesses and receipts; a missing row there would move a file to RM.
- `falsify` per-run engine gate logs (`v6`, `v7`, `v8` regressions, `v7_gates*`): classified SC (engine validation, 972 oracle
  cases and 45 fixtures with zero failures per log); tracked `v7_gates.jsonl` and `v8_gates.jsonl` are the retained
  counterparts. I did not diff the untracked gate variants against them.
- `reviews/data-review/` (276 files), `codex-engine-review/`, `grok-*`: reviewed through the adjudications; the underlying
  reviewer checks were not individually replayed.
- The RM-4 rung records may already be bound under another prime or path in `claims.json`; the tuple search covered
  `certificates.jsonl`, `unbound.jsonl` and every other tracked JSON/JSONL, not the SQLite registry.
