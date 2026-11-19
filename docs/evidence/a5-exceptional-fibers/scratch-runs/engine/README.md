# engine

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Fiber-rank engine versions v4 to v13 with their ladder and cell launchers and the outputs of v9, v9m, v11 and v13 (E8-bar -> N- degree 4 at N = 15 to 18 and E8-bar -> VB degree 5 to 7).

Generator and command: launchers `launch.sh`, `ladder-*.sh`, `queue*.sh`, `v11/run-*.sh`, `v13/run-cells-v13.sh`, `v9m/run-repro.sh` (included) call `fiber_rank_vN.py`..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-10-31 to 2026-11-12.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 0 | `xm_d5_skip` |
| `*.done` | 1 | 21 | `queue4.done` |
| `*.err` | 11 | 998 | `e8nm_d3_p2_raw_v6.jsonl.err`, `e8nm_d3_raw_v6.jsonl.err` |
| `*.jsonl` | 11 | 9878 | `e8nm_d3_p2_raw_v6.jsonl`, `e8nm_d3_raw_v6.jsonl` |
| `*.lock` | 2 | 0 | `.mem.lock`, `.vb.lock` |
| `*.log` | 1 | 5298 | `v7_regressions_quick_laptop.log` |
| `*.py` | 3 | 76872 | `fiber_rank_regressions.py`, `fiber_rank_v4.py` |
| `*.resources` | 9 | 478 | `e8nm_d3_p2_raw_v6.jsonl.resources`, `e8nm_d3_raw_v6.jsonl.resources` |
| `*.sh` | 10 | 8031 | `ladder-engine.sh`, `ladder-v6.sh` |
| `*.time` | 2 | 79 | `iso_d5.jsonl.time`, `w8_d4.jsonl.time` |
| `v10/*.sh` | 1 | 1380 | `run-d5.sh` |
| `v11/*.sh` | 5 | 5794 | `guard-vb.sh`, `run-d5.sh` |
| `v11/out/*.err` | 36 | 171 | `e8nm_d4_n15_p32009.err`, `e8nm_d4_n16_p32009.err` |
| `v11/out/*.events` | 13 | 4192 | `cells-p2.events`, `cells.events` |
| `v11/out/*.json` | 2 | 5218 | `e8nm_d5_n16_p32029.json`, `e8nm_export_n17_p32029.json` |
| `v11/out/*.time` | 35 | 1229 | `e8nm_d4_n15_p32009.time`, `e8nm_d4_n16_p32009.time` |
| `v11/out/*.txt` | 1 | 6809 | `n18-singular-version.txt` |
| `v13/*.sh` | 1 | 1509 | `run-cells-v13.sh` |
| `v13/out/*.err` | 5 | 224 | `e8vb_d5_n15_p32009.err`, `e8vb_d7_n21_p32009.err` |
| `v13/out/*.events` | 1 | 465 | `cells.events` |
| `v13/out/*.time` | 5 | 172 | `e8vb_d5_n15_p32009.time`, `e8vb_d7_n21_p32009.time` |
| `v9/*.err` | 1 | 0 | `e8nm_d4_n15.err` |
| `v9/*.events` | 1 | 152 | `e8nm_d4_n15.events` |
| `v9/*.log` | 1 | 2498 | `e8nm_d4_n15.tables.log` |
| `v9/*.time` | 1 | 36 | `e8nm_d4_n15.time` |
| `v9m/*.sh` | 1 | 904 | `run-repro.sh` |
| `v9m/out/*.err` | 2 | 0 | `e8nm_d4_n15_p32009.err`, `e8nm_d4_n15_p32029.err` |
| `v9m/out/*.events` | 1 | 142 | `repro.events` |
| `v9m/out/*.time` | 2 | 72 | `e8nm_d4_n15_p32009.time`, `e8nm_d4_n15_p32029.time` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
