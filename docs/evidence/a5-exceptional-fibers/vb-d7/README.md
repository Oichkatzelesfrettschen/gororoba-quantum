# E8-bar -> VB degree 7 at both primes

[`run-cells-v13.sh`](run-cells-v13.sh) ran engine v13 (`../replay/engine/fiber_rank_v13.py`, sha256 8e6b8d100b07a687...,
whose export builds the basis with `slimgb`) in quotient mode, raw, on the Windows workstation from 2026-11-09T18:05Z.
Five cells ran at once, four workers each, with `--max-gb 12`. The headers were `../working/build/inputs/p32009-r10754/e8-vb.sing` (sha256
4dbcb4676ca0821a...) and `../working/build/inputs/p32029-r9115/e8-vb.sing` (6b3cea4923b4e0e2...). Every cell exited 0
([`out/cells.events`](out/cells.events)).

| p | N | r_N | blocks 0 / 1 / 2 / 3 | Singular export | products | closure | wall, peak RSS |
|---|---|---|---|---|---|---|---|
| 32009 | 22 | 624 | 180 / 136 / 154 / 154 | 16,145.6 s | 63.6 s | 255.6 s | 16,538 s, 3.38 GiB |
| 32029 | 22 | 624 | 180 / 136 / 154 / 154 | 16,029.1 s | 57.7 s | 259.2 s | 16,419 s, 3.36 GiB |
| 32009 | 21 | 609 | 173 / 128 / 154 / 154 | 11,846.8 s | 53.3 s | 195.6 s | 12,155 s, 2.76 GiB |
| 32029 | 21 | 609 | 173 / 128 / 154 / 154 | 11,826.3 s | 47.4 s | 193.0 s | 12,127 s, 2.73 GiB |
| 32009 | 15 (d = 5) | 255 | 75 / 50 / 65 / 65 | 356.9 s | 23.7 s | 21.1 s | 416 s, 0.34 GiB |

The degree-5 cell reproduces the engine-v11 record (r_15 = 255, the same blocks; `../vb-d6-laptop/`), validating the
`slimgb` export. r_22 = 624 = HF(k[y]/K2, 7) (`../k2-hilbert.jsonl`) certifies h_7 = 624 at both primes (ledger A5-286,
A5-287). r_21 = 609 below it fixes the closing order at exactly 22 = 3 * 7 + 1 (A5-260). The last jump is 15 = 2 * 7 + 1,
split 7/8/0/0 (A5-269), so blocks 2 and 3 already sit at their K2 counts at N = 21. All four predictions were committed
in `docs/design/a5-vb-degree7-and-w8-char0-plan.md` before the cells started.

`exports/` holds each export's `export.json` and the sha256 of its reduced basis `s.txt` and kbase `qB.txt`. The Kaggle
cross-check kernels (`../vb-export-levers/kaggle/`) compare their own `slimgb` bases against these digests.
