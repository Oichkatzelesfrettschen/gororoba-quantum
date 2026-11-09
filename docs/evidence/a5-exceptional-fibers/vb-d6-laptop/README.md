# E8-bar -> VB degree 6 at both primes

[`run-cells.sh`](run-cells.sh) and [`run-cells-p2.sh`](run-cells-p2.sh) ran engine v11
(`../replay/engine/fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode, raw, on the Windows compute
workstation on 2026-11-09, one process per prime at once, with sparse closure tables (`--dense-tables-gb 0`), five
export chunks and the engine's own `--max-gb 30` preflight limit; the runner comment's 36 GiB is the figure in force
when it ran, and the workstation budget is now 52.5 GB RAM plus 13.4 GiB GPU memory (owner, 2026-11-09). Headers:
`../working/build/inputs/p32009-r10754/e8-vb.sing` (sha256 4dbcb4676ca0821a...) and
`../working/build/inputs/p32029-r9115/e8-vb.sing` (6b3cea4923b4e0e2...). Both cells exited 0
([`cells.events`](cells.events)) with empty error streams.

| p | N | r_N | blocks 0 / 1 / 2 / 3 | Singular export | products | closure | wall, peak RSS |
|---|---|---|---|---|---|---|---|
| 32009 | 20 | 420 | 138 / 98 / 92 / 92 | 10,646.7 s | 31.6 s | 112.8 s | 10,795.8 s, 1.71 GiB |
| 32029 | 20 | 420 | 138 / 98 / 92 / 92 | 10,523.5 s | 42.0 s | 125.1 s | 10,696.1 s, 1.65 GiB |
| 32009 | 19 | 420 | 138 / 98 / 92 / 92 | 7,330.5 s | 19.3 s | 60.4 s | 7,413.8 s, 1.24 GiB |
| 32029 | 19 | 420 | 138 / 98 / 92 / 92 | 7,113.4 s | 21.1 s | 64.3 s | 7,202.3 s, 1.24 GiB |
| 32009 | 18 | 407 | 131 / 92 / 92 / 92 | 2,540.8 s | 18.0 s | 43.5 s | 2,605.4 s, 0.97 GiB |

r_20 = 420 = HF(k[y]/K2, 6) certifies h_6 = 420 at p = 32009 (ledger A5-107) and at p = 32029 (A5-113). The export
takes 98.6 percent of the wall time, so engine v12 and the GPU path leave these cells unchanged. r_19 = 420 at both primes
(the N = 19 rows, one queue per prime, events in [`cells.events`](cells.events) and [`cells-p2.events`](cells-p2.events)),
so the closing order is at most 19 = 3d + 1. At p = 32009, r_18 = 407 < 420: the closing order is exactly 19 and the
last jump is 13, split 7 / 6 / 0 / 0 (ledger A5-260, A5-269); N = 18 at p = 32029 is running.

Degree 5, run to test the preregistered jump law A5-269 (`vbp1`/`vbp2` headers as above): r_15 = 255 with blocks
75 / 50 / 65 / 65 at both primes (444 s and 452 s wall, 0.33 GiB peak), against the retained r_16 = 266 (80 / 56 / 65 / 65,
`../d5-p2/vb_d5_n16.json`): a last jump of 11 = 2d + 1 split 5 / 6 / 0 / 0, the predicted split. N = 16 at
p = 32009 is running.

Known runner defect: `run-cells.sh` and `run-cells-p2.sh` write the engine record straight to `out/<tag>.json` and
skip a cell whose record is nonempty, so an interrupted write would read as finished on retry ([issue 802](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/802)).
Every retained record here parsed and passed the registry's engine and header digest checks.
