# Run records bound or listed by the registry scan

This directory is the scan root `a5-failed-runs` of [build_registry.py](../build_registry.py): the run records and the
engines of the ignored `docs/local/a5-failed-runs/` tree that the registry binds or lists, at their original relative
paths. The [evidence README](../README.md) states the scan order. The registry scan binds only a record whose `r_N`
equals the K2 count of its fiber and prime (`k2-hilbert.jsonl`), so the four records below, all under that count,
change none of `claims.json`, `certificates.jsonl` and `unbound.jsonl` (`build_registry.py --check`: registry
matches). They state truncated ranks below the target of rungs of three ladders, with the per-block ranks, and enter
the ledger as A5-324.

## Truncated ranks below the K2 count, per character block

The truncated rank r_N of the fiber cone of degree d is a lower bound for h_d at the prime of the record. The four
character blocks are those of the sign group named in each record, and blocks 2 and 3 are equal in every row. The
target is the K2 count HF(k[y]/K2, d) of `k2-hilbert.jsonl`.

| Record | Fiber, prime, degree | N | r_N | blocks | target | engine | wall time | peak resident set |
|---|---|---:|---:|---|---:|---|---:|---:|
| `falsify/laptop/v7/e8nm_d4_v7.jsonl` | E8-bar -> N-, 32009, d = 4 | 12 | 357 | 117, 98, 71, 71 | 495 | v7 | 4,564.7 s | 6,057,128 KiB |
| | | 13 | 440 | 140, 122, 89, 89 | 495 | v7 | 12,432.8 s | 10,791,620 KiB |
| | | 14 | 440 | 140, 122, 89, 89 | 495 | v7 | 30,053.0 s | 18,781,268 KiB |
| `e8nm-d4-p2-n13/record.json` | E8-bar -> N-, 32029, d = 4 | 13 | 440 | 140, 122, 89, 89 | 495 | v8 | 6,845.0 s | 8,895,292 KiB |
| `falsify/laptop/w8_d4.jsonl` | W8 -> N-, 32029, d = 4 | 12 | 1,644 | 425, 415, 402, 402 | 1,725 | not recorded | 1,083.1 s | 26,772,088 KiB |
| `falsify/xm_d5_v6.jsonl` | X-, 32009, d = 5 | 15 | 201 | 43, 46, 56, 56 | 417 | v6 | 3,238.3 s | 2,064,156 KiB |
| | | 16 | 201 | 43, 46, 56, 56 | 417 | v6 | 5,441.5 s | 3,078,972 KiB |
| | | 17 | 296 | 68, 66, 81, 81 | 417 | v6 | 10,313.2 s | 4,458,916 KiB |

The engines are `falsify/fiber_rank_v6.py` and `falsify/fiber_rank_v7.py` of this directory and
`../replay/engine/fiber_rank_v8.py` (sha256 prefixes `130f35904d21f5b4`, `a197799d97287b78`, `ea56c9cab5baf1d9` of the
records' `engine_sha256_16`). The record of W8 -> N- carries no engine hash. Each block rank sums to its `r_N`. The
quotient lengths `dim_quotient` are 11,595, 16,575 and 23,128 at N = 12, 13 and 14 for E8-bar -> N-
(equal to `vdim` of [std-ladder/](../std-ladder/README.md)), 6,105, 7,736 and 9,673 at N = 15, 16 and 17 for X-, and
31,824 for W8 -> N- at N = 12 (`dim_V`). The wall time and peak resident set come from the companion
`.resources` and `.time` files, except those of the 32029 record of E8-bar -> N-, which are in `time.txt`.

The E8-bar -> N- ladder at degree 4 plateaus at 440 for N = 13 and 14 at p = 32009 and reaches the target 495 at N = 15
(`../n15-laptop/`: r 495, blocks 158, 137, 100, 100); the 32029 record equals the 32009 record at N = 13 in `r_N` and
in every block. The records under `falsify/laptop/` ran on the laptop; the records of `xm_d5_v6.jsonl` and
`e8nm-d4-p2-n13` name no host.

## Files

| Path | Content |
|---|---|
| `falsify/fiber_rank_v4.py` to `v7.py`, `falsify/*.jsonl`, `falsify/laptop/v6/`, `kaggle-v7/bound/`, `reviews/`, `v9-e2e/`, `v9-n15-laptop/`, `v10-compare/`, `v11-build/` | the 32 run records and four engines that existed before this table |
| `falsify/laptop/v7/e8nm_d4_v7.jsonl`, `.resources` | E8-bar -> N-, 32009, degree 4, N = 12 to 14, and the wall time and peak resident set of each |
| `falsify/laptop/w8_d4.jsonl`, `.time` | W8 -> N-, 32029, degree 4, N = 12, and its wall time and peak resident set |
| `falsify/xm_d5_v6.jsonl`, `.resources` | X-, 32009, degree 5, N = 15 to 17, and the wall time and peak resident set of each |
| `e8nm-d4-p2-n13/record.json`, `time.txt` | E8-bar -> N-, 32029, degree 4, N = 13, and its wall time and peak resident set |
