# engine

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Fiber-rank engine versions v4 to v13 with their ladder and cell launchers and the outputs of v9, v9m, v11 and v13 (E8-bar -> N- degree 4 at N = 15 to 18 and E8-bar -> VB degree 5 to 7).

Generator and command: launchers `launch.sh`, `ladder-*.sh`, `queue*.sh`, `v11/run-*.sh`, `v13/run-cells-v13.sh`, `v9m/run-repro.sh` (included) call `fiber_rank_vN.py`..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-10-31 to 2026-11-09.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.done` | 1 | 21 | `queue4.done` |
| `*.log` | 1 | 5298 | `v7_regressions_quick_laptop.log` |
| `*.py` | 3 | 76872 | `fiber_rank_regressions.py`, `fiber_rank_v4.py` |
| `*.sh` | 10 | 8031 | `ladder-engine.sh`, `ladder-v6.sh` |
| `v10/*.sh` | 1 | 1380 | `run-d5.sh` |
| `v11/*.sh` | 5 | 5794 | `guard-vb.sh`, `run-d5.sh` |
| `v11/out/*.json` | 2 | 5218 | `e8nm_d5_n16_p32029.json`, `e8nm_export_n17_p32029.json` |
| `v11/out/*.txt` | 1 | 6809 | `n18-singular-version.txt` |
| `v13/*.sh` | 1 | 1509 | `run-cells-v13.sh` |
| `v9/*.log` | 1 | 2498 | `e8nm_d4_n15.tables.log` |
| `v9m/*.sh` | 1 | 904 | `run-repro.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
