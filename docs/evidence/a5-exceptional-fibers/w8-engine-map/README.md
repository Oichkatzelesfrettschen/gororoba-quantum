# Rank engine fiber_rank_v11.py: call graph, memory model, block-at-a-time feasibility (W8 -> N-, p = 32009)

The scripts and logs here are the agent's run files with local paths scrubbed (home and scratch directories replaced);
a path inside a script that points at `docs/local/` or a scratch directory names where the run wrote, which a clean
clone does not hold. The memoized products pickle and the exports are not retained. After the runs the Python probes
were formatted (`ruff format`, AST-equal to the bytes that ran) and given type annotations, an import order, a loader
check, `zip(strict=True)` and, in `microbench.py`, a registered QRNG seed in place of the literal 12345 its retained
timings used (residue values do not change the timed operations), to pass the repository's ruff, mypy and seed ledger; `wrap.py` reproduces r_7 = 156 at W8 degree 2
afterwards. `run.sh` returns the engine's exit status and falls back to `prlimit --as` (per-process address space,
not resident memory of the tree) where no user bus answers.

Engine sha256 `7849cbc7...`, header `w8-nm.sing` `585a946d...`, receipt `6e464db6...`, Singular 4.4.1 (passagemath wheel,
python3.13 venv), python-flint 0.9.0, numpy 2.5.4, scipy 1.18.1, Python 3.14. E is unedited. Tags: [M] measured, [C]
computed from a measured term, [H] hypothesis. Host load ran 1 to 30 (other sessions), so [M] wall times carry a factor
of three; memory numbers do not. Scripts, logs and the products memo: `docs/evidence/a5-exceptional-fibers/w8-engine-map/` (`cell.sh` runs a cell,
`wrap.py` is the wrapper; the logs `d4n13-spy2` and `d4n13-closure` are plain repeats, no py-spy ran: ptrace is denied).

## Call graph (`callgraph.txt`: 61 functions, AST, callers and callees)

| Stage | Functions (line) | Dominant data |
|---|---|---|
| 0 setup | `main` 1226, `sign_group` 185, `independent_generators` 211, `representatives` 1018 (`load_receipt` 923, `standard_monomials` 943) | small dicts |
| 1 Singular std and export | `quotient_data` 561 -> `_quotient_data_locked` 600 -> `run_step` 519 -> `_run_singular_locked` 491 (pool via `parallel.ordered_map`, 720); STD 382, TABLE 402, GENERATOR 417; parse `read_list` 446 at 734-735 | parent dicts of all 7 tables |
| 2 multiplication tables | Singular `reduce(var(k)*B, s)` (402-408), `block_tables` 779 | CSR per variable and block, 12 B per nonzero |
| 3 products | `order_walk` 816, `generator_blocks` 845, `block_products` 861 (call 1143), stacking 1146-1155 | dense L, 8 sum_b c_b c_{b^chi} B; rows 8 R c_max |
| 4 closure | inline 1166-1189; `Echelon.insert` 317, `reduce` 312, `table_mul` 1163, `sparse_mod_matmul` 758 | W[b].B, `new` (1173), chunk temporaries |
| 5 rank and output | inline 1190-1223 (final Q insert 1194, receipt checks 1201-1207) | W[b] |

`main` calls `quotient_rank` 1057; the raw path (`Space` 226, `extend_products` 365) is unused here. `estimate` 1074 and
`preflight` 1091 run on the basis alone (678, 1139).

## Memory model (D quotient dimension, c_b block columns, G = 24 generators, n = 7 variables)

Terms [C], each checked on the runs: L = 8 sum_b c_b c_{b^chi} = 128,256,128 B (d = 3) and 1,914,565,632 B (d = 4), byte-equal
to the measured `generator_blocks` result; walk temporaries 0.11 L (d = 3) and 0.10 L (d = 4) [M] against 0.5 L in the
preflight (1085); built rows 8 R c_max (R = 858 at d = 3, 2,933 at d = 4); W bytes 8 rho sum c_b^2 with rho = rank_W/cols =
0.62 (d = 3), 0.645 (d = 4), 0.657 (d = 5, README) [M]; the update (336-337) rebinds B and holds the old B, the matmul
result, the difference and the reduction at once, 3 B_b above the resident B; the seed pass leaves 58 % of the final W at
d = 4 (11,662 of 20,007 rows) and line 1173 copies it into `new`; Python marshaling (327, 331) costs about 121 B per entry
of rows x free columns (`microbench.py`, 2,000 x 20,000: 4.8 GB; in-engine 94 B at d = 4).

| Cell | Stage | Measured peak (self `VmHWM`) | Model | Wall (s) |
|---|---|---|---|---|
| d=3, N=10, D=8,008 | export parse | 117 MiB (with Singular and pool 0.41 GiB) | | 4.2 reused std; 34.9 fresh (std 13.0) |
| | products | 305 MiB | 284 MiB | 22.9 (load 14) |
| | closure | 434 MiB | | 29.5; 85 at load 30 |
| | preflight | | 0.45 GiB | |
| d=4, N=13, D=30,940 | export parse | 403 MiB (tree 0.68 GiB) | | 206.9 fresh (std 150.8); 11 reused |
| | products | 2.36 GiB | 2.47 GiB | 177 to 279 (L builds 126 of 279: 24 x 5.3) |
| | closure | 3.70 GiB (3.56 in the memo run) | see below | 295 to 439 (four runs) |
| | preflight | | 6.58 GiB (1.8x the peak) | |

The d = 4 cell runs end to end under one 900 s scope with the export reused (`d4n13-full`, 521 s; fresh export adds about
207 s). The memo pickle of `block_products` serves only the one-block probes below. tracemalloc, d = 3 only: peaks 48
(export), 53 (tables), 161 (products), 256 MiB (closure); not run at d = 4 (triples the wall time, risks the 900 s cap).
Closure at the highest-RSS sample of `d4n13-full` [M]: RSS 3.49 GiB = W 1.15 GiB + 2.34 GiB other; base at closure start
0.53 GiB, 3 B_b = 0.86 GiB, residual 0.95 GiB. Splitting the residual into the `new` copy (0.7 GiB at 58 % of W) and chunk
arrays (0.25 GiB) is [H]; it fixes the model: peak = base + W + 3 B_b + new + chunk arrays.
d = 5 anchor: preflight 58.9 GiB, measured 24.9 GiB (2.4x). The model gives closure about 21 GiB, products 21 GiB [H], so
the stage of the 24.9 GiB is not identified [H].
Closure time split at d = 4 [M] (`d4n13-split`, 283 s in inserts): matmul 113.5 s at 91 GFLOP/s (200.6 s in `d4n13-full`,
53 GFLOP/s, same flops), flint `nmod_mat` 38.2, `rref` 23.4, `entries()` 39.0, tolist/int/np.array/mod/vstack 69 s. Single-
thread marshaling, `rref` and elementwise numpy hold 45 to 60 % of the closure.

## Block-at-a-time

The blocks are coupled in the closure. W[tb] receives the rows of W[b] for b = tb ^ var_char[k] (seed 1170-1172, rounds
1180-1187); for W8 var_char = t1:0, t2:1, t4:3, t5:2, t6:3, t7:2, t9:0 [M] (`logs/classify.json`), so five of seven variables
cross blocks and the four blocks form one orbit. The check at 799-800 enforces the grading b -> b ^ var_char[k]; it does not
make a block closed. `generator_blocks` 853-858 fills L[b] from parents in b ^ var_char[k], so one generator's four block
matrices are coupled (generators are independent of each other and built one at a time). Independent once W is complete:
the final per-block insert of Q[b] (1194) and the checks (1200-1207). E has no hook that restricts the block set (`blocks`
is a local, 1065); the wrapper drops every insert into the other blocks, which gives invalid ranks and a lower-bound memory.

| Kept block | d=3 rank_W alone / full | d=4 rank_W alone / full | d=4 closure peak alone |
|---|---|---|---|
| 0 | 1272 / 1272 | 5,023 / 5,036 (-13), check growth 2 | 2.23 GiB |
| 1 | 1243 / 1243 | 4,960 / 4,973 (-13), growth 1 | 2.17 GiB |
| 2 | 1251 / 1256 (-5), growth | 4,979 / 4,999 (-20), growth 3 | 2.21 GiB |
| 3 | 1251 / 1256 (-5) | 4,979 / 4,999 (-20), growth 1 | 2.25 GiB |

At d = 4 every block alone falls short of the full rank_W and trips the receipt check at 1206 [M]; the closure of one
block needs rows of the others. All four blocks together peak at 3.56 to 3.70 GiB. Expected saving from three absent
blocks is 3 B_b = 0.86 GiB; the measured saving is 1.33 to 1.5 GiB, and the 0.5 GiB gap is unexplained.
A valid one-block-resident schedule (hypothesis, not run): keep one W[tb].B in memory, stream the other blocks' new rows
from disk, update in place. It keeps B_b, an in-place update and the chunk arrays; the products stage is unchanged.

d = 6, N = 19, D = 235,543, c = 58.9k per block; L, Sigma c_b^2 and R c_max from the probe preflight (`w8nm_d6_n19_p32009.err`):

| Quantity | Value |
|---|---|
| L, all four blocks (the walk couples them, so any block set builds it) | 103.3 GiB [C]; walk temporaries 10.3 GiB [H, 0.10 L] |
| rows 7.0, stacking 4, base 4 (table parse 4.6) | products peak 129 GiB [H] |
| W at rho = 0.67: B_b 17.3, sum 69.2 GiB; `new` 58 % of sum | closure peak 139 (late) to 160 GiB (end of round 1) [H] |
| W at rho = 0.96 (rank_W + 8,624 = cols), the ceiling: sum 99 GiB | closure peak 191 to 223 GiB [H] |
| marshaling, rows x free x 121 B | seed insert (2.2k rows, free c) up to 14.6 GiB; chunk 4,000 at free 19.6k 8.8 GiB [H] |
| one block alone, update as written (3 B_b + B_b) | 69 GiB (rho = 0.67) to 103 GiB; not 47 GiB, not 8 GiB, within 252 GB |
| one block alone, in-place update, `new` streamed | 17 to 25 GiB plus chunk arrays; products still need L = 103 GiB |
| closure wall | 14 h (from d = 5, 4,751 s) to 19 h (from the d = 4 split: BLAS x 441, marshaling x 58, rref x 441) [H] |
| products wall | 4 h (L builds x 6.4) to 8 h (matmul x 13.5), from the d = 5 measurement of 2,201 s [H] |

Whole run: peak 129 to 160 GiB at rho = 0.67, up to 223 GiB at the ceiling, against 252 GB (235 GiB) and the case's 225 GiB
RSS guard: the guard trips only near the ceiling. A single block fits neither 47 GiB nor 8 GiB per worker under E, because
L is independent of the block set. Per-block wall time is undefined (coupled); the run is 18 to 27 h on FX4-class cores [H];
27 h exceeds the case's 24 h timeout, and the case's 17 to 20 h on FX12 overlaps only the low end of this range.
Predicted per-block standard monomials of k[y]/K2 at degree 6 [C] (E's `standard_monomials` and the xor rule of
`block_products`): 2,198 / 2,170 / 2,128 / 2,128, sum 8,624. The same code gives d = 3: 147 / 141 / 156 / 156 and d = 5:
1,017 / 1,005 / 1,047 / 1,047, equal to the measured ranks; that r_19 follows this split is [H].

## Ranks [M]

d = 3, N = 10: r = 600 = HF(k[y]/K2, 3), blocks 147 / 141 / 156 / 156, rank_W 1,272 / 1,243 / 1,256 / 1,256, 258 nonstandard
checks without growth, 3 rounds. d = 4, N = 13: r = 1,725 = HF(k[y]/K2, 4), blocks 450 / 435 / 420 / 420, rank_W 5,036 /
4,973 / 4,999 / 4,999, 265 checks without growth, 4 rounds. Blocks 2 and 3 are equal in both.

## Defects found in E

1. 1085, 1088: `walk_temporaries` = 0.5 L against 0.10 L measured; `echelon_bases` assumes rank = cols with two copies (3.1x
   the measured W at d = 4) and omits `new`, the update temporaries and the marshaling objects. Net 1.8x over at d = 4,
   2.4x at d = 5, 2.3 to 2.7x over the forecast closure peak at d = 6.
2. 327, 331: `Z.ravel().tolist()` and `[int(x) for x in R.entries()]` make Python lists of rows x free entries, 121 B per
   entry; `--chunk` bounds it and no preflight term counts it.
3. 336-337: the update rebinds B through three B-sized temporaries and a `vstack`; 3 B_b above the resident B per insert.
4. 1173: B is rebound, never mutated, so `new = {b: W[b].B.copy()}` needs no copy; it holds 58 % of W (40 GiB at d = 6,
   rho = 0.67) through round 1.
5. 1206: a failed receipt check raises `SystemExit` after the ranks exist, so no JSON prints and the per-block ranks are lost.
Cost, not a defect: 845-858 builds each generator's dense L once (45 % of the d = 4 products stage; 103 GiB at d = 6).
