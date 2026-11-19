# Analysis of the A_5 scratch runs and the quotient exports

What the retained scratch runs of [README.md](README.md) and the 36 Singular quotient exports behind them establish over the dimensions family, prime, truncation order N, engine version and fiber kind, where they agree and disagree with the [findings ledger](../ledger.tsv), and what they change for the A_5 exceptional-fiber program. Every figure below names its table in [analysis/](analysis/README.md) (`exports-audit.tsv`, `scratch-ranks.tsv` and the others, produced by the scripts beside them on the compute workstation) or the retained file it was read from; a ledger row is cited by its id and read from `../ledger.tsv`. Evidence class: every rank and length is diagnostic working data over F_32009 or F_32029 from a modular or floating-point engine, and a truncated rank r_N is a lower bound of the Hilbert function h_d of F(I) that certifies h_d only when it equals the ledger value, which the `relation` column of `scratch-ranks.tsv` records (equal, below, above). Statements marked hypothesis carry their falsifier.

## What the exports are and what was kept

The export tree held 36 directories (`FAMILY-pPRIME-nN-vENGINE`) and four loose files, 23.7 GB in 2,189 files. Each directory is the Singular quotient of one slice ideal J: `s.txt` is the reduced standard basis of J + m^N in the degree-reverse-lexicographic order, `qB.txt` its k-base (the standard monomials, whose count is the quotient length l(N) = dim k[t]/(J + m^N)), `qG.txt` the fiber-map generators and `qM1.txt` to `qM9.txt` the multiplication tables of the variables on that basis. By bytes the tables are the multiplication tables (22.0 GB, single tables up to 149 MB) and by cost the standard basis `s.txt` (1.56 GB in total), as [Regeneration cost of the exports](#regeneration-cost-of-the-exports) states. The retained part is [exports/](exports/README.md): `export.json`, sidecars, the Singular scripts and `qG.txt` of every directory, 5 MB; every table is bound by its sha256 in `analysis/exports-file-digests.tsv`.

| Family | Directories | Primes | N held | Engines | Quotient length l(N) |
|---|---|---|---|---|---|
| E8-bar -> N- (`e8nm`) | 11 | 32009, 32029 | 15 to 18 | v9, v9m, v11 | 31,599 / 42,380 / 55,913 / 72,693 |
| E8-bar -> VB (`e8-vb`) | 17 | 32009 (N = 15 to 22), 32029 (N = 12 to 15, 18 to 22) | 12 to 22 | v11, v13 | 2,718 (N = 12) to 25,278 (N = 22) |
| Iso -> N- (`isonm`) | 3 | 32009 (N = 18, 19), 32029 (N = 19) | 18, 19 | v11 | 46,683 / 59,983 |
| W8 -> N- (`w8nm`) | 1 | 32009 | 19 | v11 | 235,543 |
| same-sign X (`xmnm`) | 6 | both | 20 to 22 | v11 | 17,690 / 21,231 / 25,278 |

Source: `analysis/exports-audit.tsv`. The eleven `e8nm` directories include one empty reboot remnant (`e8nm-p32009-n17-v11.dead-reboot`, no table) and one directory without `export.json` (`e8nm-p32009-n15`, three tables whose digests equal those of `e8nm-p32009-n15-v9`).

## Integrity and agreement of the exports

1. **Every digest the exports record is true.** Of 382 table digests listed in the `export.json` files, 382 equal the sha256 of the file; 372 sidecars match their tables and none fails. Two directories list nothing and hold tables: `w8nm-p32009-n19-v11` (`export.json` has `files` empty; `qB.txt` and `s.txt` carry two matching sidecars) and `e8nm-p32009-n15`. Source: `exports-audit.tsv` columns `listed_match`, `listed_mismatch`, `sidecars_ok`, `sidecars_bad`.
2. **Engines v11 and v13 write the same export.** `e8-vb-p32009-n15-v11` and `e8-vb-p32009-n15-v13` are byte-identical in every file (`s.txt`, `qB.txt`, `qG.txt`, `qM1` to `qM8`; `exports-digest-groups.tsv`); likewise `e8nm-p32009-n15-v9` and `-v9m` agree in `s.txt` and `qM1` to `qM9`, which extends the byte equality of the split export of engine v9 with the serial export of v8 (A5-322, N = 9 and 11) to N = 15 with the memory-scheduled variant.
3. **A fresh recomputation reproduces the N = 15 tables byte for byte.** `kbcheck-n15.txt` has the sha256 of `qB.txt` and `qM1-recomputed.txt` (131,600,293 bytes) that of `qM1.txt` of `e8nm-p32009-n15-v9m` (`exports-digest-groups.tsv`, rows with `kbcheck-n15.txt` and `qM1-recomputed.txt`).
4. **The standard monomials do not depend on the prime.** At each family and N the two primes have the same `qB.txt` (E8-bar -> N- N = 15 to 18, E8-bar -> VB N = 15, 18 to 22, Iso N = 19, X N = 20 to 22; same sha256), and for Iso at N = 19 also the same `s.txt` and all of `qM1` to `qM6`: the reduced standard basis of Iso has the same text modulo 32009 and 32029, so its coefficients are small integers. The `s.txt` of E8-bar -> N- differs between the primes, so its coefficients are residues.
5. **The Singular option does not change the result.** The k-bases of the standard-basis option comparison (std, slimgb, groebner; `probes/vb-levers/ladder`, `codex-final`) equal the `qB.txt` of the exports of E8-bar -> VB at N = 12 to 16 and 18 to 20 (26 manifest rows whose sha256 equals an export file; `large-files-manifest.tsv` against `exports-file-digests.tsv`), and the standard bases `ladder-n15-{std,slimgb}.s` and `ladder-n16-{std,slimgb}.s` equal `s.txt` of `e8-vb-p32009-n15-v13` and `-n16-v11`. The generator counts of `s.txt` equal the `sb_size` of the logs (1,244 at N = 13 and 1,797 at N = 15; `singular-timings.tsv`).
6. **Lengths agree with the tracked records.** The `qB.txt` count equals `dim_quotient` of engine records at E8-bar -> VB N = 16 (7,736; `replay/out/E8-VB-32009-d5-N16-quotient/replay.jsonl`), E8-bar -> N- N = 17 (55,913; `engine/v11/out/e8nm_export_n17_p32029.json`) and A5-183 (72,693 at N = 18).

## Quotient lengths: dimension, multiplicity and a test of A5-325

`hilbert_samuel.py` takes finite differences of l(N) over consecutive N (`hilbert-samuel.tsv`). Since l(N) - l(N - 1) is the Hilbert function of the tangent cone at degree N - 1, the first non-constant difference order shows the dimension and the constant difference the multiplicity once the polynomial range starts.

- **E8-bar -> N-**, lengths 11,595, 16,575, 23,128 (A5-321, N = 12 to 14) and 31,599, 42,380, 55,913, 72,693 (N = 15 to 18): the fifth differences are 3 and 3 (differences 4,980 ... 16,780; 1,573 ... 3,247; 345 ... 495; 47, 50, 53; 3, 3). The local ring has dimension 5 and multiplicity 3 on this evidence (two equal fifth differences; hypothesis that the polynomial range has begun). It agrees with `germ_dimension 5` and `germ_component_count 1` of `clo/e8-nm-stdq.log` and with the multiplicity 1 + 2 = 3 of A5-002; falsifier: a length l(19) other than 93,271, the value that a fifth difference 3 continues from the differences above.
- **E8-bar -> VB**, p = 32029 N = 12 to 15 and both primes N = 18 to 22: lengths 11,952, 14,611, 17,690, 21,231, 25,278 have differences 2,659 ... 4,047; 420, 462, 506; 42, 44; 2. The third difference of the tangent-cone Hilbert function is 2: dimension 4, multiplicity 2, the values that A5-325 states for the tangent cone of the presolved germ.
- **Same-sign X**: l(20), l(21), l(22) = 17,690, 21,231, 25,278 at both primes, the second difference of the Hilbert function 506.
- **New: the quotient lengths of E8-bar -> VB and of same-sign X are equal at N = 20, 21 and 22 at both primes** (`hilbert-samuel-relations.tsv`: 17,690/17,690, 21,231/21,231, 25,278/25,278 at 32009 and at 32029), although the ideals differ (8 against 7 variables, `J_sha256` differs) and the standard monomial sets differ (`qB.txt` digests differ; degree counts 1, 8, 34, 94 against 1, 7, 27, 67). A5-325 (open) names a quotient length q_N that differs between the two germs as its falsifier; six matched pairs at N between 20 and 22 hold, and the claim that the two germs are isomorphic is not falsified there. Lengths at N <= 19 for X (not exported) are the decisive next cells.
- **Two degree-wise identities of the leading monomials** (hypothesis, from `hilbert-samuel-relations.tsv`; they describe the standard monomials in the degree-reverse-lexicographic order of the truncated ideal, not the tangent cone): the number of standard monomials of degree d is VB(d) = X(d) + X(d - 1) and VB(d) = E8(d) - E8(d - 1) for d = 1 to 7 at both primes (1, 8, 34, 94, 199, 360, 589, 898 for VB). For d >= 8 the VB counts depend on N (1,268 at N = 20, 1,297 at N = 22 at d = 8), so only d <= 7 is stable. Falsifier: a stable count at d = 8 with N >= 26.

## Rank ladders against the ledger

`scratch_ranks.py` reads 79 rank records (47 engine records of fiber_rank v6 to v11 and 32 fast-ladder rows; `scratch-ranks.tsv`) and compares each with the certified h_d of the ledger for its fiber class, prime and degree. **71 records equal the ledger value, 8 lie below it and none lies above** (`scratch-ranks-summary.tsv`: E8-bar -> N- 19 equal and 5 below, E8-bar -> VB 5 equal, Iso 9 and 1, W8 8 and 1, X 30 and 1). The six below are the cells the ledger classes as truncations short of the closing N: E8-bar -> N- d = 3 at N = 10 (191 against 225), d = 4 at N = 12, 13, 14 (357, 440, 440 against 495), d = 5 at N = 16 and p = 32029 (742 against 952), Iso d = 5 at N = 15 (1,195 against 1,316), W8 d = 4 at N = 12 (1,644 against 1,725) and X d = 8 at order 32 (1,133 against 1,422). No retained record contradicts a ledger Hilbert value.

| Fiber class | Degree, closing N seen here | Below that N |
|---|---|---|
| E8-bar -> N- (p = 32009) | d = 3 at N = 11; d = 4 at N = 15 (`replay/out/e8n15-p1/out.json`, 11,021 s) | d = 3: 191 at N = 10; d = 4: 357, 440, 440 at N = 12, 13, 14 |
| E8-bar -> VB | d = 5 at N = 16, both primes | not run here |
| Iso | d = 5 at N = 16 (both primes; v6 and v8) | 1,195 at N = 15 |
| W8 -> N- | d = 4 at N = 13 (both primes; v6 and v8) | 1,644 at N = 12 (p = 32029) |
| X (same sign) | d = 1 to 7 at the ladder orders 11, 14, 17, 20, 23, 26, 29 (`fast/xm-nm-p32009-d8-n32.json`) | d = 8: 1,133 at order 32 (1,422 at order 34, A5-299) |

Cross-checks: Iso and W8 close at N = 3d + 1 (16 and 13), as A5-244 states; the plateau of E8-bar -> N- d = 4 (440 at N = 13 and 14, 495 at N = 15) is an instance of A5-051 (a plateau below the K2 count refutes nothing). **Engine agreement:** the cells that two engines or two runs computed give equal ranks: v6 against v8 at E8-bar -> N- d = 3 N = 11 (p = 32009 both signs, p = 32029 N-), Iso d = 5 N = 16 and W8 d = 4 N = 13 (both primes), and v7 against v8 at E8-bar -> VB d = 5 N = 16 (p = 32009). **Replay:** of the 32 cells of `replay/replay-ids.txt`, 31 reproduce (exit 0, equal record) and one stops at its 2,280 s limit (E8-bar -> N-, p = 32009, d = 4, N = 15, exit status 124); the same cell completes in 11,021 s in `replay/out/e8n15-p1` (r = 495), so the failure is the limit and no disagreement.

## Kernel limits, Plucker maps and monomial probes

- **Kernel limits** (`kernel-limits.tsv`): the opposite-sign X arcs (xp-nm and xm-np) at order 12 (36 arcs, nine groups, nine distinct planes, pivot valuation sum 8, limit dimension 8 inside the base kernel of nullity 16) hold over F_32009, F_32029 and Q for both slices (verdict `survives`); the W8 cap-30 arcs at order 32 (24 arcs, six distinct planes, valuation sum 16) carry the verdict `refuted` over all three fields, so that verdict does not depend on the prime.
- **Plucker maps** (`plucker-map.tsv`): every one of the 19 cases fits the degree-2 map exactly (delta 2, solution dimension 1) and every held-out sample is proportional (40 of 40, 80 of 80, 10 of 10); ranks are Iso 85 (both primes), W8 120, 84 and 156 (both primes), E8-bar -> N- 22, 53 and 69, X 6, same-sign X 45. **Disagreement between batches:** the `fpm-line` batch gives Plucker rank 23 for same-sign X (Veronese ranks 11, 23, 35) where the `fpm` batch gives 45 (12, 45, 112), with the same order 40, 360 arcs and 320 samples, and the degree-3 Veronese rank of X is 9 there against 10; the batches sample different arc sets (the purpose of `fpm-line` is not recorded), so each rank is a lower bound of the span and the two do not conflict. Falsifier of "lower bound only": a larger sample whose rank exceeds 45.
- **Monomial probes** (`monomial-probes.tsv`): for same-sign X the spans of I and of m_R I are monomial subspaces at order 12 (ranks 973 and 958, both primes, both signs) and order 14 (1,788 and 1,773), each equal to its number of single-monomial rows. These equal the tracked probe records.

## Singular standard-basis cost (A5-321)

`singular-timings.tsv` extends the cost curve of A5-321 to E8-bar -> VB: std takes 200 s at N = 13, 1,313 s at N = 15, 2,796 s at N = 16 and 4,963 s at N = 17 against slimgb 77 s, 339 s, 973 s and 1,741 s: slimgb is faster by 2.6 to 3.9 times for N = 13 to 17, at 3.2 to 4.9 times the memory (351,620 against 87,228 KiB at N = 15), and the ratios of consecutive std times are 2.7, 2.5, 2.1 and 1.8 (N = 14 to 17). At N = 13 groebner (173 s), slimgb with a degree bound (48 s), without the reduced tail (56 s) and reversed (99 s) return the same standard basis size 1,244 and k-base size 3,627.

## Ascella band replay

`../../ascella-cz-tomography-band/mesh-model-mapped-refits/` holds the serial and the mapped run of `mesh_model.py` (not an A_5 run): the two outputs are byte-identical (160 s serial, 125 s mapped), and 108 of 117 numeric leaves equal the retained `mesh-model.json` bit for bit while 9 differ by at most 8.6e-16 relative, so the held-out result of that component model reproduces to floating-point summation order.

## Where the runs agree, disagree and add

- **Agree:** all 71 records equal to the ledger, all replays, all export digests, the cross-prime and cross-engine byte equalities above, the dimension 5 of E8-bar -> N-, the dimension 4 and multiplicity 2 of E8-bar -> VB.
- **Disagree:** nothing contradicts a certified row. The ledger's own hypothesis clause on the closing N of X- (A5-244: floor(7d/2) + 1, that is 25 at d = 7 and 29 at d = 8) is contradicted by the ledger rows A5-298 and A5-299 and by the record here: r_25 = 300 and r_27 = 582 at d = 7 and r_32 = 1,133 at d = 8 lie below h_d, so the closing N is above 27 at d = 7 and above 32 at d = 8. The clause on the last jump, (2d + 1)^2, holds at d = 8 on the retained ladder (1,422 - 1,133 = 289 = 17^2) over a two-step ladder; at d = 7 it needs r_28 = 771 and the retained cells do not decide it.
- **New:** (a) the l(N) equality of E8-bar -> VB and X at N = 20 to 22 at both primes (A5-325); (b) the dimension and multiplicity of the E8-bar -> N- local ring read from l(N); (c) byte equality of v11 with v13 and of v9 with v9m exports, of std with slimgb results at VB N = 15, 16 and of a recomputation at E8-bar -> N- N = 15; (d) the Plucker-rank difference between the `fpm` and `fpm-line` batches; (e) the std against slimgb cost ratios for E8-bar -> VB at N = 13 to 17; (f) the two identities of leading-monomial counts.

## Impact on the A_5 project

| Row | Effect |
|---|---|
| A5-325 (open) | six matched q_N at N = 20 to 22, both primes, do not falsify it; propose a row that records them and keeps A5-325 open until X is run at N <= 19 |
| A5-244 (survives) | propose retiring the floor(7d/2) + 1 clause for X- (contradicted by A5-298, A5-299); keep the (2d + 1)^2 clause, with d = 8 as an additional matched value |
| A5-031 (survives) | 71 of 79 retained records equal h_d, none above: a further tally of the 48-cell statement; no change of status |
| A5-321, A5-322 (survive) | A5-321 extends to VB std against slimgb (cost curve) and A5-322 to N = 15 (v9 against v9m, recomputation); both stay survives |
| A5-002, A5-406 | independent reading of dimension 5 and multiplicity 3 (E8-bar -> N-) and of dimension 4 and multiplicity 2 (E8-bar -> VB) from l(N); consistent, no status change |
| A5-051 (rejected) | a further instance of the plateau (440, 440, 495) |
| A5-576 to A5-578 (open) | not touched: no scratch run here is a modular Rees fiber at the second prime |

No ledger row is edited by this change. The rows above are proposals; the registry (`build_registry.py` scan roots) is unchanged.

## Follow-ups

| Follow-up | Decisive run or proof | Cost |
|---|---|---|
| Close A5-325 on the computed side | std(J + m^N) of same-sign X at N = 18 and 19, p = 32009, compared with the VB lengths 11,952 and 14,611 (`exports-audit.tsv`); slimgb with the exports layout | about an hour each if X behaves like VB at N = 17 (1,741 s slimgb; estimate, X has one variable fewer) |
| Close A5-325 by proof | an isomorphism of the presolved germs of X- and E8-bar -> VB, or a Hilbert-Samuel function in closed form for both: Rocq (a finite certificate) or Lean (the statement for the family); the first step is the equality of their Hilbert series after removing the linear form (A5-325) | days, no compute |
| Decide the X- closing N | r_28 at d = 7 (needs 771 for the last-jump law) and r_33 at d = 8 (needs 1,133), engine `fast_ladder` with 24 threads | 2,097 s at order 29 and 3,217 s at order 32 are the retained times |
| Confirm the multiplicity 3 of E8-bar -> N- | l(19) = 93,271 predicted by the quintic through N = 12 to 18; std at N = 19 with slimgb | 43,597 s of std at N = 17 (engine v11) extrapolates to more than 100,000 s per step; this is a hypothesis check that is cheaper by proof (A5-002 gives the multiplicity 3) |
| Settle the Plucker rank of same-sign X | the `fpm` sampler at 720 arcs and 640 samples with the same slice, compared with 45 and 23 | minutes (logs of the batches) |
| Raise the replay limit | the E8-bar -> N- d = 4 N = 15 replay cell with a limit above 12,000 s | 3.1 hours |
| Keep a way to restart rank runs | decide whether to keep the standard bases `s.txt` of E8-bar -> N- N = 17 and 18 (892 MB for both primes) off the repository | the decision below |

## Regeneration cost of the exports

The expensive file of an export is `s.txt`: 43,597 s (12.1 h) at E8-bar -> N-, p = 32029, N = 17 with engine v11 (`engine/v11/out/e8nm_export_n17_p32029.json`, which also records 4,581 s for all 45 `qM` chunks and 38.6 s for `qG.txt`; `s.txt` is 98.7 percent of the 44,188 s total). The standard basis cost grows by 2.5 to 2.7 per step of N (A5-321; 2.1 to 2.7 for VB std), so the N = 18 standard basis costs about 31 hours (estimate from the ratio 2.6; not measured). Engine regeneration commands are the launchers of `engine/v11/run-*.sh` and `engine/v13/run-cells-v13.sh`; the multiplication tables (`qM`) follow from `s.txt` in minutes per chunk.

| Entry | Bytes | Regenerable by | Cost |
|---|---|---|---|
| `e8nm` N = 15 (v9, v9m, n15) | 0.92, 0.92 and 0.24 GB at p = 32009 (the three directories share their table digests), 0.92 GB at p = 32029 | `replay/engine/fiber_rank_v9m.py` (`engine/v9m/run-repro.sh`) | hours (N = 15) |
| `e8nm` N = 16, 17, 18 | 1.6, 2.6, 4.1 GB per prime | engine v11 | N = 17: 12.1 h of `s.txt` plus 1.3 h of `qM`; N = 18 about 31 h (estimate) |
| `e8-vb` (17) | 1.8 GB | engine v11 and v13 | N = 22: below 1 day (VB std N = 17 is 4,963 s, slimgb 1,741 s; N = 22 not measured) |
| `isonm` (3), `xmnm` (6), `w8nm` n19 | 0.02, 1.2, 0.11 GB | engine v11 | hours or less (not measured) |

## Reproduction

`analysis/scratch_ranks.py`, `scratch_tables.py` and `hilbert_samuel.py` run from this tree (`python3 scratch_ranks.py ../.. .` from `analysis/`); `exports_audit.py` needs the export tree and was run once on the compute workstation (hashing 23.7 GB took under one minute from the page cache). The python lanes of the repository check the four scripts; the mypy sweep excludes `scratch-runs/`.
